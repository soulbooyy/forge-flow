"""Pure Phase 2 eligibility and redacted Draft-PR body assembly."""

from dataclasses import dataclass
import re

from forgeflow.governed_changes.approval_trace.models import (
    ApprovalDecision,
    DurableRunSummary,
    MetadataArtifactReference,
)
from forgeflow.governed_changes.approval_trace.canonical import (
    artifact_reference_id_for,
    decision_id_for,
    summary_id_for,
)

from .models import DraftPRRequest, FixturePolicyDecisionRecord, PRTerminal

_CHANGE_CODE = re.compile(r"^change-[0-9]{3}$")
_VALIDATION_STATUSES = frozenset(("succeeded", "not_started"))
_SEVERITIES = frozenset(("none", "low", "medium", "high"))
_TASK_SUMMARIES = {"fixture-task-accepted": "Fixture task accepted"}
_CHANGE_SUMMARIES = {"governed-metadata-update": "Governed metadata update"}


@dataclass(frozen=True, slots=True)
class RedactedBodyFacts:
    """Transient publication-whitelist facts; no source or provider payload."""

    task_summary_code: str
    change_summary_code: str
    changed_file_codes: tuple[str, ...]
    validation_status: str
    secret_scan_status: str
    review_finding_count: int
    review_severity: str

    def __post_init__(self) -> None:
        if self.task_summary_code not in _TASK_SUMMARIES or self.change_summary_code not in _CHANGE_SUMMARIES:
            raise ValueError("registered redacted summary codes required")
        if (
            not isinstance(self.changed_file_codes, tuple)
            or not self.changed_file_codes
            or self.changed_file_codes != tuple(sorted(set(self.changed_file_codes)))
            or any(not isinstance(value, str) or not _CHANGE_CODE.fullmatch(value) for value in self.changed_file_codes)
        ):
            raise ValueError("ordered change codes required")
        if self.validation_status not in _VALIDATION_STATUSES or self.secret_scan_status != "passed":
            raise ValueError("only publishable validation and scan statuses are allowed")
        if type(self.review_finding_count) is not int or not 0 <= self.review_finding_count <= 99:
            raise ValueError("bounded review finding count required")
        if self.review_severity not in _SEVERITIES:
            raise ValueError("controlled review severity required")


def evaluate_eligibility(
    request: object,
    policy: object,
    approval: object,
    reference: object,
    summary: object,
    now: object,
) -> PRTerminal | None:
    """Return a bounded terminal for any ineligible mutation lineage."""
    if not isinstance(request, DraftPRRequest) or type(now) is not int:
        raise ValueError("canonical request and clock required")
    if not isinstance(policy, FixturePolicyDecisionRecord):
        return PRTerminal.create(request.request_id, "policy_blocked")
    if policy.outcome != "allowed" or policy.expires_at <= now:
        return PRTerminal.create(request.request_id, "policy_blocked")
    if not isinstance(approval, ApprovalDecision) or approval.outcome != "approved" or approval.expires_at <= now:
        return PRTerminal.create(request.request_id, "approval_required")
    if not isinstance(reference, MetadataArtifactReference) or not isinstance(summary, DurableRunSummary):
        return PRTerminal.create(request.request_id, "policy_blocked")
    if (
        approval.decision_id != decision_id_for(approval)
        or reference.artifact_reference_id != artifact_reference_id_for(reference)
        or summary.summary_id != summary_id_for(summary)
        or approval.decision_id != request.approval_decision_id
        or approval.lineage_digest != reference.lineage_digest
        or policy.policy_decision_id != request.policy_decision_id
        or policy.artifact_reference_id != request.artifact_reference_id
        or policy.approval_decision_id != request.approval_decision_id
        or policy.idempotency_key != request.idempotency_key
        or reference.artifact_reference_id != request.artifact_reference_id
        or reference.run_id != request.run_id
        or summary.summary_id != request.durable_summary_id
        or summary.run_id != request.run_id
        or reference.artifact_reference_id not in summary.artifact_reference_ids
        or request.policy_decision_id not in summary.policy_decision_ids
        or approval.decision_id not in summary.approval_decision_ids
    ):
        return PRTerminal.create(request.request_id, "policy_blocked")
    return None


def render_redacted_body(
    request: object,
    reference: object,
    summary: object,
    facts: object,
) -> str:
    """Render a deterministic body from the RFC-005 publication whitelist."""
    if not isinstance(request, DraftPRRequest) or not isinstance(reference, MetadataArtifactReference) or not isinstance(summary, DurableRunSummary) or not isinstance(facts, RedactedBodyFacts):
        raise ValueError("canonical publication facts required")
    if (
        reference.artifact_reference_id != artifact_reference_id_for(reference)
        or summary.summary_id != summary_id_for(summary)
        or reference.artifact_reference_id != request.artifact_reference_id
        or reference.run_id != request.run_id
        or summary.summary_id != request.durable_summary_id
        or summary.run_id != request.run_id
        or reference.artifact_reference_id not in summary.artifact_reference_ids
    ):
        raise ValueError("body lineage is not closed")
    return "\n".join((
        "## ForgeFlow governed Draft PR",
        f"Issue: #{request.issue_number}",
        f"Base revision: {request.base_revision}",
        f"Task summary: {_TASK_SUMMARIES[facts.task_summary_code]}",
        f"Artifact metadata: {reference.artifact_metadata_id}",
        f"Change summary: {_CHANGE_SUMMARIES[facts.change_summary_code]}",
        f"Change references: {', '.join(facts.changed_file_codes)}",
        f"Validation: {facts.validation_status}",
        f"Secret scan: {facts.secret_scan_status}",
        f"Review: {facts.review_finding_count} ({facts.review_severity})",
        f"Policy profile: {request.profile_id}@{request.profile_version}",
        f"Policy decision: {request.policy_decision_id}",
        f"Approval decision: {request.approval_decision_id}",
        f"Durable summary: {summary.summary_id}",
    ))
