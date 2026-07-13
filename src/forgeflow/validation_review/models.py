"""Immutable M3 validation, terminal, review, and error contracts."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, TypeAlias
import re

from .profile import M3_FIXTURE_V1


PolicyDecision: TypeAlias = Literal["allowed", "blocked", "requires_human_approval"]
ValidationOutcome: TypeAlias = Literal["passed", "failed"]
ValidationTerminalReason: TypeAlias = Literal[
    "policy_blocked", "human_approval_required"
]
ReviewSeverity: TypeAlias = Literal["advisory", "blocking"]
ValidationReviewErrorCode: TypeAlias = Literal[
    "unsupported_patch_proposal",
    "invalid_fixture_case",
    "invalid_policy_reference",
    "policy_lineage_mismatch",
    "dangling_evidence_ref",
    "dangling_artifact_ref",
    "forbidden_payload",
    "invalid_review_input",
    "bounds_exceeded",
]

_HASH_PATTERN = re.compile(r"^[0-9a-f]{64}$")


def _require_hash_id(name: str, value: str, prefix: str) -> None:
    if not isinstance(value, str) or not value.startswith(prefix) or not _HASH_PATTERN.fullmatch(
        value[len(prefix) :]
    ):
        raise ValueError(f"{name} must use the {prefix}<lowercase-hex> format")


def _require_sorted_unique_ids(
    name: str, values: tuple[str, ...], prefix: str, maximum: int
) -> None:
    if not isinstance(values, tuple) or len(values) > maximum:
        raise ValueError(f"{name} must be a tuple with at most {maximum} entries")
    for value in values:
        _require_hash_id(name, value, prefix)
    if values != tuple(sorted(set(values))):
        raise ValueError(f"{name} must be sorted and unique")


def _require_sorted_unique_controlled(
    name: str, values: tuple[str, ...], allowed: tuple[str, ...], maximum: int
) -> None:
    if not isinstance(values, tuple) or len(values) > maximum:
        raise ValueError(f"{name} must be a tuple with at most {maximum} entries")
    if any(value not in allowed for value in values):
        raise ValueError(f"{name} contains an unsupported value")
    if values != tuple(sorted(set(values))):
        raise ValueError(f"{name} must be sorted and unique")


@dataclass(frozen=True, slots=True)
class PolicyDecisionRecordRef:
    decision_id: str
    decision: PolicyDecision
    policy_profile_id: Literal["validation-review/m3-fixture-v1"]
    policy_version: int
    evaluator_id: Literal["m3/deterministic-policy-fixture-v1"]
    subject_contract_id: str
    risk_flags: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        _require_hash_id("decision_id", self.decision_id, "pdr_sha256:")
        if self.decision not in ("allowed", "blocked", "requires_human_approval"):
            raise ValueError("decision must be controlled")
        if self.policy_profile_id != M3_FIXTURE_V1.policy_profile_id:
            raise ValueError("policy_profile_id must identify the M3 fixture profile")
        if self.policy_version != M3_FIXTURE_V1.policy_version:
            raise ValueError("policy_version must be 1")
        if self.evaluator_id != M3_FIXTURE_V1.evaluator_id:
            raise ValueError("evaluator_id must identify the M3 policy fixture")
        if not self.subject_contract_id.startswith(("pp_sha256:", "vr_sha256:", "rr_sha256:")):
            raise ValueError("subject_contract_id must identify an M3 lineage subject")
        prefix = self.subject_contract_id.split(":", maxsplit=1)[0] + ":"
        _require_hash_id("subject_contract_id", self.subject_contract_id, prefix)
        _require_sorted_unique_controlled(
            "risk_flags",
            self.risk_flags,
            M3_FIXTURE_V1.allowed_risk_flags,
            len(M3_FIXTURE_V1.allowed_risk_flags),
        )


@dataclass(frozen=True, slots=True)
class ReviewFinding:
    finding_code: str
    severity: ReviewSeverity
    evidence_ref_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.finding_code not in M3_FIXTURE_V1.allowed_review_finding_codes:
            raise ValueError("finding_code must be controlled")
        if self.severity not in ("advisory", "blocking"):
            raise ValueError("severity must be controlled")
        _require_sorted_unique_ids(
            "evidence_ref_ids", self.evidence_ref_ids, "ev_sha256:", M3_FIXTURE_V1.max_evidence_refs
        )
        if not self.evidence_ref_ids:
            raise ValueError("evidence_ref_ids must not be empty")


@dataclass(frozen=True, slots=True)
class ValidationResult:
    contract_id: str
    patch_proposal_contract_id: str
    attempt_id: str
    fixture_case_id: str
    outcome: ValidationOutcome
    finding_codes: tuple[str, ...]
    policy_decision_refs: tuple[PolicyDecisionRecordRef, ...]
    evidence_ref_ids: tuple[str, ...]
    artifact_ids: tuple[str, ...]
    schema_version: Literal["validation-result/v1"] = "validation-result/v1"
    result_type: Literal["validation_result"] = "validation_result"

    def __post_init__(self) -> None:
        _require_hash_id("contract_id", self.contract_id, "vr_sha256:")
        _require_hash_id("patch_proposal_contract_id", self.patch_proposal_contract_id, "pp_sha256:")
        _require_hash_id("attempt_id", self.attempt_id, "m3a_sha256:")
        if self.fixture_case_id not in ("passed-default", "failed-default"):
            raise ValueError("fixture_case_id must be a controlled completed-attempt case")
        if self.outcome not in ("passed", "failed"):
            raise ValueError("outcome must be passed or failed")
        _require_sorted_unique_controlled(
            "finding_codes",
            self.finding_codes,
            M3_FIXTURE_V1.allowed_validation_finding_codes,
            M3_FIXTURE_V1.max_finding_codes,
        )
        if self.outcome == "passed" and self.finding_codes:
            raise ValueError("passed result cannot contain finding codes")
        if self.outcome == "failed" and not self.finding_codes:
            raise ValueError("failed result requires a finding code")
        _require_policy_refs(self.policy_decision_refs, self.patch_proposal_contract_id, "allowed")
        _require_sorted_unique_ids(
            "evidence_ref_ids", self.evidence_ref_ids, "ev_sha256:", M3_FIXTURE_V1.max_evidence_refs
        )
        _require_sorted_unique_ids(
            "artifact_ids", self.artifact_ids, "artifact_sha256:", M3_FIXTURE_V1.max_artifact_ids
        )
        if self.schema_version != "validation-result/v1" or self.result_type != "validation_result":
            raise ValueError("ValidationResult must use the validation-result/v1 envelope")


@dataclass(frozen=True, slots=True)
class ValidationTerminal:
    terminal_id: str
    patch_proposal_contract_id: str
    terminal_reason: ValidationTerminalReason
    policy_decision_refs: tuple[PolicyDecisionRecordRef, ...]
    evidence_ref_ids: tuple[str, ...]
    artifact_ids: tuple[str, ...]
    schema_version: Literal["validation-terminal/v1"] = "validation-terminal/v1"
    result_type: Literal["validation_terminal"] = "validation_terminal"

    def __post_init__(self) -> None:
        _require_hash_id("terminal_id", self.terminal_id, "vt_sha256:")
        _require_hash_id("patch_proposal_contract_id", self.patch_proposal_contract_id, "pp_sha256:")
        expected_decision = {
            "policy_blocked": "blocked",
            "human_approval_required": "requires_human_approval",
        }.get(self.terminal_reason)
        if expected_decision is None:
            raise ValueError("terminal_reason must be controlled")
        _require_policy_refs(self.policy_decision_refs, self.patch_proposal_contract_id, expected_decision)
        _require_sorted_unique_ids(
            "evidence_ref_ids", self.evidence_ref_ids, "ev_sha256:", M3_FIXTURE_V1.max_evidence_refs
        )
        _require_sorted_unique_ids(
            "artifact_ids", self.artifact_ids, "artifact_sha256:", M3_FIXTURE_V1.max_artifact_ids
        )
        if self.schema_version != "validation-terminal/v1" or self.result_type != "validation_terminal":
            raise ValueError("ValidationTerminal must use the validation-terminal/v1 envelope")


@dataclass(frozen=True, slots=True)
class ReviewResult:
    contract_id: str
    patch_proposal_contract_id: str
    validation_result_contract_id: str
    findings: tuple[ReviewFinding, ...]
    policy_decision_refs: tuple[PolicyDecisionRecordRef, ...]
    evidence_ref_ids: tuple[str, ...]
    artifact_ids: tuple[str, ...]
    schema_version: Literal["review-result/v1"] = "review-result/v1"
    result_type: Literal["review_result"] = "review_result"

    def __post_init__(self) -> None:
        _require_hash_id("contract_id", self.contract_id, "rr_sha256:")
        _require_hash_id("patch_proposal_contract_id", self.patch_proposal_contract_id, "pp_sha256:")
        _require_hash_id("validation_result_contract_id", self.validation_result_contract_id, "vr_sha256:")
        if not isinstance(self.findings, tuple) or not self.findings:
            raise ValueError("findings must be a non-empty tuple")
        if len(self.findings) > M3_FIXTURE_V1.max_review_findings:
            raise ValueError("findings exceeds the M3 fixture limit")
        if not all(isinstance(finding, ReviewFinding) for finding in self.findings):
            raise ValueError("findings must contain ReviewFinding values")
        if self.findings != tuple(
            sorted(self.findings, key=lambda item: (item.finding_code, item.severity, item.evidence_ref_ids))
        ):
            raise ValueError("findings must use canonical ordering")
        _require_policy_refs(self.policy_decision_refs, self.validation_result_contract_id, "allowed")
        _require_sorted_unique_ids(
            "evidence_ref_ids", self.evidence_ref_ids, "ev_sha256:", M3_FIXTURE_V1.max_evidence_refs
        )
        _require_sorted_unique_ids(
            "artifact_ids", self.artifact_ids, "artifact_sha256:", M3_FIXTURE_V1.max_artifact_ids
        )
        if self.schema_version != "review-result/v1" or self.result_type != "review_result":
            raise ValueError("ReviewResult must use the review-result/v1 envelope")


@dataclass(frozen=True, slots=True)
class ValidationReviewErrorSummary:
    patch_proposal_contract_id: str | None = None
    fixture_case_id: str | None = None
    policy_profile_id: str | None = None

    def __post_init__(self) -> None:
        if self.patch_proposal_contract_id is not None:
            _require_hash_id("patch_proposal_contract_id", self.patch_proposal_contract_id, "pp_sha256:")
        if self.fixture_case_id is not None and self.fixture_case_id not in (
            "passed-default",
            "failed-default",
        ):
            raise ValueError("fixture_case_id must be controlled")
        if self.policy_profile_id is not None and self.policy_profile_id != M3_FIXTURE_V1.policy_profile_id:
            raise ValueError("policy_profile_id must identify the M3 fixture profile")


@dataclass(frozen=True, slots=True)
class ValidationReviewError:
    error_id: str
    error_code: ValidationReviewErrorCode
    message: str
    summary: ValidationReviewErrorSummary
    completion_status: Literal["validation_error"] = "validation_error"
    schema_version: Literal["validation-review-error/v1"] = "validation-review-error/v1"
    result_type: Literal["validation_review_error"] = "validation_review_error"

    def __post_init__(self) -> None:
        _require_hash_id("error_id", self.error_id, "vre_sha256:")
        if self.error_code not in (
            "unsupported_patch_proposal",
            "invalid_fixture_case",
            "invalid_policy_reference",
            "policy_lineage_mismatch",
            "dangling_evidence_ref",
            "dangling_artifact_ref",
            "forbidden_payload",
            "invalid_review_input",
            "bounds_exceeded",
        ):
            raise ValueError("error_code must be controlled")
        if not isinstance(self.message, str) or not self.message or len(self.message) > 500:
            raise ValueError("message must be bounded safe text")
        if not isinstance(self.summary, ValidationReviewErrorSummary):
            raise ValueError("summary must be ValidationReviewErrorSummary")
        if (
            self.completion_status != "validation_error"
            or self.schema_version != "validation-review-error/v1"
            or self.result_type != "validation_review_error"
        ):
            raise ValueError("ValidationReviewError must use the validation-review-error/v1 envelope")


ValidationEnvelope: TypeAlias = ValidationResult | ValidationTerminal


def _require_policy_refs(
    values: tuple[PolicyDecisionRecordRef, ...], subject_contract_id: str, required_decision: str
) -> None:
    if not isinstance(values, tuple) or not values:
        raise ValueError("policy_decision_refs must be a non-empty tuple")
    if not all(isinstance(value, PolicyDecisionRecordRef) for value in values):
        raise ValueError("policy_decision_refs must contain PolicyDecisionRecordRef values")
    if values != tuple(sorted(values, key=lambda value: value.decision_id)):
        raise ValueError("policy_decision_refs must use canonical decision-ID ordering")
    if len({value.decision_id for value in values}) != len(values):
        raise ValueError("policy_decision_refs must be unique")
    if not any(
        value.subject_contract_id == subject_contract_id and value.decision == required_decision
        for value in values
    ):
        raise ValueError("policy_decision_refs must contain the required subject and decision")
