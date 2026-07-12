"""Deterministic direct matching, ranking, and evidence projection."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePosixPath

from .evidence import file_evidence, text_evidence
from .models import EvidenceRef, RankingInputs, RelevantFile, SearchResult, TextLocator
from .normalization import NormalizedQuery, normalized_matching_view
from .profile import RepositoryContextProfile
from .scanner import ScannedFile


@dataclass(frozen=True, slots=True)
class MatchOutput:
    relevant_files: tuple[RelevantFile, ...]
    evidence_refs: tuple[EvidenceRef, ...]
    search_results: tuple[SearchResult, ...]


@dataclass(frozen=True, slots=True)
class _MatchedFile:
    relevant_file: RelevantFile
    evidence_refs: tuple[EvidenceRef, ...]
    search_results: tuple[SearchResult, ...]


def match_scanned_files(
    scanned_files: tuple[ScannedFile, ...],
    query: NormalizedQuery,
    profile: RepositoryContextProfile,
) -> MatchOutput:
    """Return direct-signal matches in deterministic relevance order."""
    matches = tuple(
        matched
        for scanned_file in scanned_files
        if (matched := _match_file(scanned_file, query, profile)) is not None
    )
    ordered_matches = tuple(
        sorted(
            matches,
            key=lambda matched: (-matched.relevant_file.match_score, matched.relevant_file.path),
        )
    )
    evidence_refs = tuple(
        reference for matched in ordered_matches for reference in matched.evidence_refs
    )
    search_results = tuple(
        sorted(
            (
                result
                for matched in ordered_matches
                for result in matched.search_results
            ),
            key=lambda result: (
                result.path,
                result.locator.start_line,
                result.locator.end_line,
            ),
        )
    )
    return MatchOutput(
        relevant_files=tuple(matched.relevant_file for matched in ordered_matches),
        evidence_refs=evidence_refs,
        search_results=search_results,
    )


def _match_file(
    scanned_file: ScannedFile,
    query: NormalizedQuery,
    profile: RepositoryContextProfile,
) -> _MatchedFile | None:
    filename_match = query.matching_view in normalized_matching_view(
        PurePosixPath(scanned_file.path).name
    )
    path_match = query.matching_view in normalized_matching_view(scanned_file.path)
    locators = _text_locators(scanned_file, query, profile)
    ranking_inputs = RankingInputs(
        filename_match=filename_match,
        path_match=path_match,
        text_match_count=len(locators),
    )
    if not (filename_match or path_match or locators):
        return None

    evidence_refs: list[EvidenceRef] = []
    if filename_match:
        evidence_refs.append(file_evidence(scanned_file, "filename_match"))
    if path_match:
        evidence_refs.append(file_evidence(scanned_file, "path_match"))
    for locator in locators:
        evidence_refs.append(text_evidence(scanned_file, locator))

    relevant_file = RelevantFile(
        path=scanned_file.path,
        file_kind=scanned_file.file_kind,
        ranking_inputs=ranking_inputs,
        match_score=_score(ranking_inputs),
        match_reasons=_match_reasons(ranking_inputs),
        evidence_ref_ids=tuple(reference.id for reference in evidence_refs),
    )
    text_evidence_refs = evidence_refs[-len(locators) :] if locators else ()
    search_results = tuple(
        SearchResult(
            path=scanned_file.path,
            locator=locator,
            evidence_ref_id=reference.id,
        )
        for locator, reference in zip(locators, text_evidence_refs)
    )
    return _MatchedFile(
        relevant_file=relevant_file,
        evidence_refs=tuple(evidence_refs),
        search_results=search_results,
    )


def _text_locators(
    scanned_file: ScannedFile,
    query: NormalizedQuery,
    profile: RepositoryContextProfile,
) -> tuple[TextLocator, ...]:
    if scanned_file.text is None:
        return ()

    locators: list[TextLocator] = []
    for line_number, line in enumerate(scanned_file.text.splitlines(), start=1):
        if query.matching_view in normalized_matching_view(line):
            locators.append(TextLocator(start_line=line_number, end_line=line_number))
            if len(locators) == profile.max_text_locators_per_file:
                break
    return tuple(locators)


def _score(inputs: RankingInputs) -> int:
    return (
        (100 if inputs.filename_match else 0)
        + (50 if inputs.path_match else 0)
        + 25 * inputs.text_match_count
    )


def _match_reasons(inputs: RankingInputs) -> tuple[str, ...]:
    reasons: list[str] = []
    if inputs.filename_match:
        reasons.append("filename_match")
    if inputs.path_match:
        reasons.append("path_match")
    if inputs.text_match_count:
        reasons.append("text_match")
    return tuple(reasons)
