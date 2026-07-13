"""Immutable data contracts for Milestone 2 PatchProposal envelopes."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, TypeAlias
import re
import unicodedata

from .profile import M2_CONSERVATIVE_V1


HypothesisUncertainty: TypeAlias = Literal["low", "medium", "high"]
ChangeKind: TypeAlias = Literal[
    "modify_existing_file",
    "add_test_file",
    "add_non_sensitive_file",
    "remove_file",
]
RiskFlag: TypeAlias = Literal[
    "policy_requires_human_approval",
    "environment_path",
    "high_risk_path",
    "deletion_intent",
    "policy_profile_revalidation_required",
]
LimitationCode: TypeAlias = Literal[
    "fixture_only_source",
    "no_source_payload",
    "no_diff_generated",
    "no_validation_executed",
]
PolicyDecision: TypeAlias = Literal["allowed", "requires_human_approval"]
ValidationErrorCode: TypeAlias = Literal[
    "unsupported_repository_context",
    "dangling_evidence_ref",
    "empty_hypotheses",
    "invalid_task_input",
    "invalid_candidate_change",
    "invalid_change_kind",
    "bounds_exceeded",
    "invalid_policy_profile",
    "policy_blocked",
    "fixture_draft_malformed",
    "raw_payload_forbidden",
]
ValidationInputCategory: TypeAlias = Literal[
    "repository_context",
    "task_input",
    "proposal_draft",
    "policy_profile",
    "candidate_change",
]


@dataclass(frozen=True, slots=True)
class TaskInput:
    task_ref: str
    summary: str

    def __post_init__(self) -> None:
        _require_bounded_text("task_ref", self.task_ref, maximum=128)
        if self.task_ref != self.task_ref.strip() or any(
            unicodedata.category(character).startswith("C") for character in self.task_ref
        ):
            raise ValueError("task_ref must be a safe logical reference")
        _require_bounded_text("summary", self.summary, maximum=1_000)
        normalized_summary = " ".join(unicodedata.normalize("NFC", self.summary).split())
        if self.summary != normalized_summary:
            raise ValueError("summary must be NFC-normalized, trimmed, and whitespace-collapsed")


@dataclass(frozen=True, slots=True)
class RootCauseHypothesis:
    statement: str
    uncertainty: HypothesisUncertainty
    supporting_evidence_ref_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        _require_bounded_text("statement", self.statement, maximum=500)
        _require_controlled_value("uncertainty", self.uncertainty, ("low", "medium", "high"))
        _require_evidence_ids(self.supporting_evidence_ref_ids)


@dataclass(frozen=True, slots=True)
class FixStrategy:
    summary: str
    constraint_codes: tuple[
        Literal["evidence_backed", "minimal_change", "no_execution", "policy_bounded"],
        ...,
    ]

    def __post_init__(self) -> None:
        _require_bounded_text("summary", self.summary, maximum=1_000)
        if self.constraint_codes != M2_CONSERVATIVE_V1.required_fix_strategy_constraint_codes:
            raise ValueError("constraint_codes must be the fixed ordered M2 constraint set")


@dataclass(frozen=True, slots=True)
class CandidateChange:
    path: str
    change_kind: ChangeKind
    rationale: str
    supporting_evidence_ref_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        _require_workspace_relative_path(self.path)
        _require_controlled_value(
            "change_kind", self.change_kind, M2_CONSERVATIVE_V1.allowed_change_kinds
        )
        _require_bounded_text("rationale", self.rationale, maximum=500)
        _require_evidence_ids(self.supporting_evidence_ref_ids)


@dataclass(frozen=True, slots=True)
class PolicyDecisionRef:
    decision_id: str
    decision: PolicyDecision
    policy_profile_id: Literal["patch-proposal/m2-conservative-v1"]
    policy_version: int
    evaluator_id: Literal["m2/deterministic-boundary-evaluator-v1"]
    evaluated_candidate_digest: str
    risk_flags: tuple[RiskFlag, ...] = field(default_factory=tuple)
    revalidation_required: Literal[True] = True

    def __post_init__(self) -> None:
        _require_hash_id("decision_id", self.decision_id, "pdr_sha256:")
        _require_controlled_value(
            "decision", self.decision, ("allowed", "requires_human_approval")
        )
        if self.policy_profile_id != M2_CONSERVATIVE_V1.policy_profile_id:
            raise ValueError("policy_profile_id must identify the M2 conservative profile")
        if self.policy_version != M2_CONSERVATIVE_V1.policy_version:
            raise ValueError("policy_version must be 1")
        if self.evaluator_id != M2_CONSERVATIVE_V1.evaluator_id:
            raise ValueError("evaluator_id must identify the M2 boundary evaluator")
        _require_hash_id(
            "evaluated_candidate_digest", self.evaluated_candidate_digest, "sha256:"
        )
        _require_sorted_unique_controlled_values(
            "risk_flags", self.risk_flags, M2_CONSERVATIVE_V1.allowed_risk_flags
        )
        if self.revalidation_required is not True:
            raise ValueError("revalidation_required must be true")


@dataclass(frozen=True, slots=True)
class PatchProposal:
    contract_id: str
    proposal_source_id: Literal["m2/deterministic-fixture-v1"]
    repository_context_contract_id: str
    task_input: TaskInput
    root_cause_hypotheses: tuple[RootCauseHypothesis, ...]
    fix_strategy: FixStrategy
    candidate_changes: tuple[CandidateChange, ...]
    policy_decision: PolicyDecisionRef
    risk_flags: tuple[RiskFlag, ...] = field(default_factory=tuple)
    limitation_codes: tuple[LimitationCode, ...] = field(default_factory=tuple)
    schema_version: Literal["patch-proposal/v1"] = "patch-proposal/v1"
    result_type: Literal["patch_proposal"] = "patch_proposal"

    def __post_init__(self) -> None:
        _require_hash_id("contract_id", self.contract_id, "pp_sha256:")
        if self.proposal_source_id != M2_CONSERVATIVE_V1.proposal_source_id:
            raise ValueError("proposal_source_id must identify the M2 deterministic fixture")
        _require_hash_id(
            "repository_context_contract_id", self.repository_context_contract_id, "rcr_sha256:"
        )
        _require_tuple_of("root_cause_hypotheses", self.root_cause_hypotheses, RootCauseHypothesis)
        if not self.root_cause_hypotheses or len(self.root_cause_hypotheses) > 3:
            raise ValueError("root_cause_hypotheses must contain between one and three entries")
        if self.root_cause_hypotheses != tuple(
            sorted(
                self.root_cause_hypotheses,
                key=lambda item: (
                    item.statement,
                    item.uncertainty,
                    item.supporting_evidence_ref_ids,
                ),
            )
        ):
            raise ValueError("root_cause_hypotheses must use canonical ordering")
        _require_tuple_of("candidate_changes", self.candidate_changes, CandidateChange)
        if not self.candidate_changes or len(self.candidate_changes) > 3:
            raise ValueError("candidate_changes must contain between one and three entries")
        if self.candidate_changes != tuple(
            sorted(
                self.candidate_changes,
                key=lambda item: (item.path, item.change_kind, item.rationale),
            )
        ):
            raise ValueError("candidate_changes must use canonical ordering")
        _require_sorted_unique_controlled_values(
            "risk_flags", self.risk_flags, M2_CONSERVATIVE_V1.allowed_risk_flags
        )
        _require_sorted_unique_controlled_values(
            "limitation_codes", self.limitation_codes, M2_CONSERVATIVE_V1.allowed_limitation_codes
        )
        if self.schema_version != "patch-proposal/v1" or self.result_type != "patch_proposal":
            raise ValueError("PatchProposal must use the patch-proposal/v1 success envelope")


@dataclass(frozen=True, slots=True)
class ValidationErrorSummary:
    repository_context_contract_id: str | None = None
    task_ref: str | None = None
    policy_profile_id: str | None = None

    def __post_init__(self) -> None:
        if self.repository_context_contract_id is not None:
            _require_hash_id(
                "repository_context_contract_id",
                self.repository_context_contract_id,
                "rcr_sha256:",
            )
        if self.task_ref is not None:
            _require_bounded_text("task_ref", self.task_ref, maximum=128)
        if (
            self.policy_profile_id is not None
            and self.policy_profile_id != M2_CONSERVATIVE_V1.policy_profile_id
        ):
            raise ValueError("policy_profile_id must identify the M2 conservative profile")


@dataclass(frozen=True, slots=True)
class PatchProposalValidationError:
    error_id: str
    error_code: ValidationErrorCode
    input_category: ValidationInputCategory
    message: str
    summary: ValidationErrorSummary
    schema_version: Literal["patch-proposal-validation-error/v1"] = (
        "patch-proposal-validation-error/v1"
    )
    result_type: Literal["patch_proposal_validation_error"] = (
        "patch_proposal_validation_error"
    )
    completion_status: Literal["validation_error"] = "validation_error"

    def __post_init__(self) -> None:
        _require_hash_id("error_id", self.error_id, "ppe_sha256:")
        _require_controlled_value(
            "error_code",
            self.error_code,
            (
                "unsupported_repository_context",
                "dangling_evidence_ref",
                "empty_hypotheses",
                "invalid_task_input",
                "invalid_candidate_change",
                "invalid_change_kind",
                "bounds_exceeded",
                "invalid_policy_profile",
                "policy_blocked",
                "fixture_draft_malformed",
                "raw_payload_forbidden",
            ),
        )
        _require_controlled_value(
            "input_category",
            self.input_category,
            ("repository_context", "task_input", "proposal_draft", "policy_profile", "candidate_change"),
        )
        _require_bounded_text("message", self.message, maximum=500)
        if (
            self.schema_version != "patch-proposal-validation-error/v1"
            or self.result_type != "patch_proposal_validation_error"
            or self.completion_status != "validation_error"
        ):
            raise ValueError("PatchProposalValidationError must use the validation-error envelope")


PatchProposalEnvelope: TypeAlias = PatchProposal | PatchProposalValidationError


_LOWERCASE_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def _require_bounded_text(name: str, value: object, *, maximum: int) -> None:
    if not isinstance(value, str) or not 1 <= len(value) <= maximum:
        raise ValueError(f"{name} must contain between one and {maximum} Unicode code points")


def _require_controlled_value(name: str, value: object, allowed: tuple[str, ...]) -> None:
    if value not in allowed:
        raise ValueError(f"{name} is not a controlled M2 value")


def _require_hash_id(name: str, value: object, prefix: str) -> None:
    if not isinstance(value, str) or not value.startswith(prefix) or not _LOWERCASE_SHA256.fullmatch(value[len(prefix) :]):
        raise ValueError(f"{name} must be a lowercase SHA-256 identity")


def _require_evidence_ids(value: object) -> None:
    if not isinstance(value, tuple) or not value:
        raise ValueError("supporting_evidence_ref_ids must be a non-empty tuple")
    if value != tuple(sorted(value)) or len(value) != len(set(value)):
        raise ValueError("supporting_evidence_ref_ids must be sorted and unique")
    for evidence_id in value:
        _require_hash_id("supporting evidence ID", evidence_id, "ev_sha256:")


def _require_workspace_relative_path(value: object) -> None:
    if not isinstance(value, str) or not value or value.startswith("/") or "\\" in value:
        raise ValueError("path must be a canonical workspace-relative path")
    segments = value.split("/")
    if any(not segment or segment in {".", ".."} for segment in segments):
        raise ValueError("path must be a canonical workspace-relative path")


def _require_tuple_of(name: str, value: object, item_type: type[object]) -> None:
    if not isinstance(value, tuple) or not all(isinstance(item, item_type) for item in value):
        raise ValueError(f"{name} must be a tuple of {item_type.__name__}")


def _require_sorted_unique_controlled_values(
    name: str, value: object, allowed: tuple[str, ...]
) -> None:
    if not isinstance(value, tuple) or value != tuple(sorted(value)) or len(value) != len(set(value)):
        raise ValueError(f"{name} must be sorted and unique")
    if any(item not in allowed for item in value):
        raise ValueError(f"{name} contains an unsupported value")
