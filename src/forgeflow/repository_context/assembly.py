"""Deterministic Repository Context result assembly."""

from __future__ import annotations

from dataclasses import replace

from .canonical import contract_id_for
from .hints import HintDiscovery
from .matching import MatchOutput
from .models import (
    BoundedOptionalInput,
    CandidateCounts,
    EvidenceRef,
    InputSummary,
    Limitation,
    NormalizedInput,
    RepositoryContextResult,
    ResultSetTruncatedDetail,
    ReturnedCounts,
    RunCounts,
    RunSummary,
    TestCommandHint,
    WorkspaceRef,
)
from .profile import RepositoryContextProfile
from .scanner import ScanReport


_SCOPE_ORDER = {"input": 0, "workspace": 1, "directory": 2, "file": 3, "result": 4}


def assemble_result(
    *,
    workspace_ref: WorkspaceRef,
    query: NormalizedInput,
    issue_text: BoundedOptionalInput,
    scan_report: ScanReport,
    matches: MatchOutput,
    hints: tuple[TestCommandHint, ...],
    hint_evidence_refs: tuple[EvidenceRef, ...],
    profile: RepositoryContextProfile,
    limitations: tuple[Limitation, ...] = (),
) -> RepositoryContextResult:
    """Apply result caps and derive a graph-consistent immutable envelope."""
    candidate_counts = CandidateCounts(
        relevant_files=len(matches.relevant_files),
        search_results=len(matches.search_results),
        evidence_refs=len(matches.evidence_refs) + len(hint_evidence_refs),
        test_command_hints=len(hints),
    )
    relevant_files = matches.relevant_files[: profile.max_relevant_files]
    retained_paths = {file.path for file in relevant_files}
    search_results = tuple(
        result for result in matches.search_results if result.path in retained_paths
    )[: profile.max_search_results]
    returned_hints = tuple(
        sorted(hints, key=lambda hint: (hint.command, hint.source))
    )[: profile.max_test_command_hints]

    required_evidence_ids = {
        reference_id
        for relevant_file in relevant_files
        for reference_id in relevant_file.evidence_ref_ids
    }
    required_evidence_ids.update(
        result.evidence_ref_id for result in search_results
    )
    required_evidence_ids.update(
        reference_id
        for hint in returned_hints
        for reference_id in hint.evidence_ref_ids
    )
    evidence_by_id = {
        reference.id: reference
        for reference in (*matches.evidence_refs, *hint_evidence_refs)
    }
    evidence_refs = tuple(
        sorted(
            (
                evidence_by_id[reference_id]
                for reference_id in required_evidence_ids
            ),
            key=lambda reference: reference.id,
        )
    )

    all_limitations = list(limitations)
    if issue_text.truncated:
        all_limitations.append(
            Limitation(
                code="issue_text_truncated",
                scope="input",
                detail="issue text was bounded to the configured limit",
            )
        )
    if scan_report.discovered_files == 0:
        all_limitations.append(
            Limitation(code="empty_repository", scope="workspace", detail="no files discovered")
        )
    elif not matches.relevant_files:
        all_limitations.append(
            Limitation(code="no_matches", scope="workspace", detail="no direct matches found")
        )

    affected_arrays = _affected_arrays(
        candidate_counts, relevant_files, search_results, evidence_refs, returned_hints
    )
    if affected_arrays:
        all_limitations.append(
            Limitation(
                code="result_set_truncated",
                scope="result",
                detail=ResultSetTruncatedDetail(affected_arrays=affected_arrays),
                count=len(affected_arrays),
            )
        )
    ordered_limitations = tuple(
        sorted(
            (
                replace(
                    limitation,
                    related_evidence_ref_ids=tuple(
                        sorted(limitation.related_evidence_ref_ids)
                    ),
                )
                for limitation in all_limitations
            ),
            key=_limitation_key,
        )
    )
    limitation_codes_by_path: dict[str, list[str]] = {}
    for limitation in ordered_limitations:
        if limitation.scope == "file" and limitation.path is not None:
            limitation_codes_by_path.setdefault(limitation.path, []).append(limitation.code)
    relevant_files = tuple(
        replace(
            relevant_file,
            limitation_codes=tuple(sorted(limitation_codes_by_path.get(relevant_file.path, ()))),
        )
        for relevant_file in relevant_files
    )
    returned_counts = ReturnedCounts(
        relevant_files=len(relevant_files),
        search_results=len(search_results),
        evidence_refs=len(evidence_refs),
        test_command_hints=len(returned_hints),
        limitations=len(ordered_limitations),
    )
    run_summary = RunSummary(
        operation_type="repository_context",
        completion_status=(
            "completed_with_limitations" if ordered_limitations else "completed"
        ),
        input_summary=InputSummary(
            workspace_root_id=workspace_ref.root_id,
            configuration_profile_id=profile.configuration_profile_id,
            query_normalized=query.normalized,
            issue_text_present=issue_text.present,
            issue_text_truncated=issue_text.truncated,
            normalization_id=profile.normalization_id,
            limit_profile_id=profile.limit_profile_id,
            ignore_policy_id=profile.ignore_policy_id,
        ),
        counts=RunCounts(
            discovered_files=scan_report.discovered_files,
            discovered_directories=scan_report.discovered_directories,
            scanned_text_files=sum(
                scanned_file.file_kind == "text" for scanned_file in scan_report.files
            ),
            skipped_files=scan_report.skipped_files,
            skipped_directories=scan_report.skipped_directories,
            candidates=candidate_counts,
            returned=returned_counts,
        ),
        limitation_codes=tuple(
            sorted({limitation.code for limitation in ordered_limitations})
        ),
    )
    result = RepositoryContextResult(
        contract_id="",
        workspace_ref=workspace_ref,
        query=query,
        issue_text=issue_text,
        run_summary=run_summary,
        relevant_files=relevant_files,
        search_results=search_results,
        test_command_hints=returned_hints,
        evidence_refs=evidence_refs,
        limitations=ordered_limitations,
    )
    return replace(result, contract_id=contract_id_for(result))


def assemble_with_hints(
    *,
    workspace_ref: WorkspaceRef,
    query: NormalizedInput,
    issue_text: BoundedOptionalInput,
    scan_report: ScanReport,
    matches: MatchOutput,
    discovery: HintDiscovery,
    profile: RepositoryContextProfile,
) -> RepositoryContextResult:
    """Assemble a result from root hint discovery without exposing its internals."""
    return assemble_result(
        workspace_ref=workspace_ref,
        query=query,
        issue_text=issue_text,
        scan_report=scan_report,
        matches=matches,
        hints=discovery.hints,
        hint_evidence_refs=discovery.evidence_refs,
        profile=profile,
        limitations=(*scan_report.limitations, *discovery.limitations),
    )


def _affected_arrays(
    candidates: CandidateCounts,
    relevant_files: tuple[object, ...],
    search_results: tuple[object, ...],
    evidence_refs: tuple[EvidenceRef, ...],
    hints: tuple[TestCommandHint, ...],
) -> tuple[str, ...]:
    affected: list[str] = []
    if len(relevant_files) < candidates.relevant_files:
        affected.extend(("relevant_files", "search_results", "evidence_refs"))
    if len(search_results) < candidates.search_results:
        affected.append("search_results")
    if len(evidence_refs) < candidates.evidence_refs:
        affected.append("evidence_refs")
    if len(hints) < candidates.test_command_hints:
        affected.extend(("test_command_hints", "evidence_refs"))
    return tuple(sorted(set(affected)))


def _limitation_key(limitation: Limitation) -> tuple[object, ...]:
    return (
        limitation.code,
        _SCOPE_ORDER[limitation.scope],
        limitation.path is not None,
        limitation.path or "",
        limitation.count if limitation.count is not None else -1,
        _limitation_detail_key(limitation.detail),
    )


def _limitation_detail_key(detail: object) -> str:
    if isinstance(detail, ResultSetTruncatedDetail):
        return ",".join(detail.affected_arrays)
    return str(detail)
