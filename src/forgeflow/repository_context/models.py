"""Immutable data contracts for Repository Context results."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal, TypeAlias


@dataclass(frozen=True, slots=True)
class ResultSetTruncatedDetail:
    affected_arrays: tuple[str, ...]


LimitationDetail: TypeAlias = str | ResultSetTruncatedDetail


@dataclass(frozen=True, slots=True)
class WorkspaceRef:
    root_id: str
    source_ref: str | None = None


@dataclass(frozen=True, slots=True)
class NormalizedInput:
    normalized: str
    raw_ref: str | None = None


@dataclass(frozen=True, slots=True)
class BoundedOptionalInput:
    present: bool
    normalized: str
    truncated: bool
    raw_ref: str | None = None


@dataclass(frozen=True, slots=True)
class RankingInputs:
    filename_match: bool
    path_match: bool
    text_match_count: int


@dataclass(frozen=True, slots=True)
class TextLocator:
    start_line: int
    end_line: int


@dataclass(frozen=True, slots=True)
class ContentHash:
    algorithm: Literal["sha256"]
    value: str


@dataclass(frozen=True, slots=True)
class EvidenceRef:
    id: str
    evidence_kind: str
    retrieval_signal: str
    locator: TextLocator | None
    path: str | None = None
    content_hash: ContentHash | None = None
    hash_scope: Literal["full_inspected_text", "truncated_inspected_range"] | None = None


@dataclass(frozen=True, slots=True)
class RelevantFile:
    path: str
    file_kind: str
    ranking_inputs: RankingInputs
    match_score: int
    match_reasons: tuple[str, ...] = field(default_factory=tuple)
    evidence_ref_ids: tuple[str, ...] = field(default_factory=tuple)
    limitation_codes: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class SearchResult:
    path: str
    locator: TextLocator
    evidence_ref_id: str


@dataclass(frozen=True, slots=True)
class TestCommandHint:
    command: str
    source: str
    evidence_ref_ids: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class Limitation:
    code: str
    scope: Literal["input", "workspace", "directory", "file", "result"]
    detail: LimitationDetail
    path: str | None = None
    count: int | None = None
    related_evidence_ref_ids: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class InputSummary:
    workspace_root_id: str
    configuration_profile_id: Literal["repository-context/m1-defaults-v1"]
    query_normalized: str
    issue_text_present: bool
    issue_text_truncated: bool
    normalization_id: str
    limit_profile_id: str
    ignore_policy_id: str


@dataclass(frozen=True, slots=True)
class CandidateCounts:
    relevant_files: int
    search_results: int
    evidence_refs: int
    test_command_hints: int


@dataclass(frozen=True, slots=True)
class ReturnedCounts:
    relevant_files: int
    search_results: int
    evidence_refs: int
    test_command_hints: int
    limitations: int


@dataclass(frozen=True, slots=True)
class RunCounts:
    discovered_files: int
    discovered_directories: int
    scanned_text_files: int
    skipped_files: int
    skipped_directories: int
    candidates: CandidateCounts
    returned: ReturnedCounts


@dataclass(frozen=True, slots=True)
class RunSummary:
    operation_type: Literal["repository_context"]
    completion_status: Literal["completed", "completed_with_limitations"]
    input_summary: InputSummary
    counts: RunCounts
    limitation_codes: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class ValidationErrorSummary:
    workspace_root_id: str | None
    configuration_profile_id: str | None
    query_present: bool


@dataclass(frozen=True, slots=True)
class RepositoryContextRequest:
    workspace_root: Path
    workspace_ref: WorkspaceRef
    configuration_profile_id: str
    query: str
    issue_text: str | None = None


@dataclass(frozen=True, slots=True)
class RepositoryContextResult:
    contract_id: str
    workspace_ref: WorkspaceRef
    query: NormalizedInput
    issue_text: BoundedOptionalInput
    run_summary: RunSummary
    relevant_files: tuple[RelevantFile, ...] = field(default_factory=tuple)
    search_results: tuple[SearchResult, ...] = field(default_factory=tuple)
    test_command_hints: tuple[TestCommandHint, ...] = field(default_factory=tuple)
    evidence_refs: tuple[EvidenceRef, ...] = field(default_factory=tuple)
    limitations: tuple[Limitation, ...] = field(default_factory=tuple)
    schema_version: Literal["repository-context-result/v1"] = "repository-context-result/v1"
    result_type: Literal["repository_context_result"] = "repository_context_result"


@dataclass(frozen=True, slots=True)
class RepositoryContextValidationError:
    error_id: str
    error_code: str
    input_category: str
    message: str
    summary: ValidationErrorSummary
    input_ref: str | None = None
    schema_version: Literal["repository-context-validation-error/v1"] = (
        "repository-context-validation-error/v1"
    )
    result_type: Literal["repository_context_validation_error"] = (
        "repository_context_validation_error"
    )
    completion_status: Literal["validation_error"] = "validation_error"


RepositoryContextEnvelope: TypeAlias = (
    RepositoryContextResult | RepositoryContextValidationError
)
