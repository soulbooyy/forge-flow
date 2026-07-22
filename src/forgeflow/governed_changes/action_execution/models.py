"""Immutable M4 governed-action contract models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import re
from typing import Literal, TypeAlias

from .profile import M4_FIXTURE_V1


_HEX = re.compile(r"^[0-9a-f]{64}$")
_SHA = re.compile(r"^[0-9a-f]{40}$")
_TIMESTAMP = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
Outcome: TypeAlias = Literal["allowed", "requires_human_approval", "blocked"]
AttemptStatus: TypeAlias = Literal["succeeded", "failed", "cancelled", "timed_out", "not_started"]
FailureReason: TypeAlias = Literal["policy_blocked", "approval_required", "sandbox_unavailable", "base_revision_mismatch", "command_failed", "resource_limit_exceeded", "cancelled_by_request"]


def _id(name: str, value: str, prefix: str) -> None:
    if not isinstance(value, str) or not value.startswith(prefix) or not _HEX.fullmatch(value[len(prefix):]):
        raise ValueError(f"{name} must use {prefix}<lowercase-hex>")


def _timestamp(name: str, value: str) -> None:
    if not isinstance(value, str) or not _TIMESTAMP.fullmatch(value):
        raise ValueError(f"{name} must be an RFC 3339 UTC timestamp")


def _timestamp_ms(value: str) -> int:
    return int(datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc).timestamp() * 1000)


def _ordered(name: str, values: tuple[str, ...], prefix: str | None = None) -> None:
    if not isinstance(values, tuple) or values != tuple(sorted(set(values))):
        raise ValueError(f"{name} must be a sorted unique tuple")
    if prefix:
        for value in values:
            _id(name, value, prefix)


def _base_fields(contract_id: str, run_id: str, created_at: str, prefix: str) -> None:
    _id("contract_id", contract_id, prefix)
    _id("run_id", run_id, "run_sha256:")
    _timestamp("created_at", created_at)


def _canonical_id(value: object, prefix: str, omitted: frozenset[str]) -> str:
    from .canonical import sha256_hex

    return f"{prefix}{sha256_hex(value, omit_fields=omitted)}"


@dataclass(frozen=True, slots=True)
class ActionIntent:
    contract_id: str
    action_id: str
    run_id: str
    created_at: str
    task_input_contract_id: str
    repository_id: str
    base_commit_sha: str
    requested_command_id: str
    policy_profile_id: str
    policy_profile_version: str
    schema_version: Literal["m4-governed-action-sandbox/v1"] = "m4-governed-action-sandbox/v1"
    kind: Literal["execute_fixture_test"] = "execute_fixture_test"

    def __post_init__(self) -> None:
        _base_fields(self.contract_id, self.run_id, self.created_at, "ai_sha256:")
        _id("action_id", self.action_id, "action_sha256:")
        _id("task_input_contract_id", self.task_input_contract_id, "ti_sha256:")
        if (self.repository_id, self.base_commit_sha, self.requested_command_id, self.policy_profile_id, self.policy_profile_version, self.schema_version, self.kind) != (M4_FIXTURE_V1.repository_id, M4_FIXTURE_V1.base_commit_sha, M4_FIXTURE_V1.command_id, M4_FIXTURE_V1.policy_profile_id, M4_FIXTURE_V1.policy_profile_version, "m4-governed-action-sandbox/v1", "execute_fixture_test"):
            raise ValueError("ActionIntent must use the exact registered fixture lineage")
        expected = _canonical_id(self, "ai_sha256:", frozenset({"contract_id", "action_id", "created_at"}))
        if self.contract_id != expected or self.action_id != expected.replace("ai_sha256:", "action_sha256:"):
            raise ValueError("ActionIntent IDs must match the canonical payload")


@dataclass(frozen=True, slots=True)
class CommandIntent:
    contract_id: str
    run_id: str
    created_at: str
    action_intent_contract_id: str
    repository_id: str
    base_commit_sha: str
    command_id: str
    executable: str
    args: tuple[str, ...]
    working_directory: str
    allowed_environment: tuple[str, ...]
    oci_image_digest: str
    timeout_ms: int
    max_output_bytes: int
    policy_profile_id: str
    policy_profile_version: str
    schema_version: Literal["m4-governed-action-sandbox/v1"] = "m4-governed-action-sandbox/v1"

    def __post_init__(self) -> None:
        _base_fields(self.contract_id, self.run_id, self.created_at, "ci_sha256:")
        _id("action_intent_contract_id", self.action_intent_contract_id, "ai_sha256:")
        exact = (M4_FIXTURE_V1.repository_id, M4_FIXTURE_V1.base_commit_sha, M4_FIXTURE_V1.command_id, M4_FIXTURE_V1.executable, M4_FIXTURE_V1.args, M4_FIXTURE_V1.working_directory, M4_FIXTURE_V1.allowed_environment, M4_FIXTURE_V1.oci_image_digest, M4_FIXTURE_V1.timeout_ms, M4_FIXTURE_V1.max_output_bytes, M4_FIXTURE_V1.policy_profile_id, M4_FIXTURE_V1.policy_profile_version, "m4-governed-action-sandbox/v1")
        actual = (self.repository_id, self.base_commit_sha, self.command_id, self.executable, self.args, self.working_directory, self.allowed_environment, self.oci_image_digest, self.timeout_ms, self.max_output_bytes, self.policy_profile_id, self.policy_profile_version, self.schema_version)
        if actual != exact:
            raise ValueError("CommandIntent must use the exact registered command capability")
        if self.contract_id != _canonical_id(self, "ci_sha256:", frozenset({"contract_id", "created_at"})):
            raise ValueError("CommandIntent ID must match the canonical payload")


@dataclass(frozen=True, slots=True)
class PolicyDecisionRecord:
    contract_id: str
    decision_id: str
    run_id: str
    created_at: str
    subject_contract_id: str
    input_lineage_digest: str
    policy_profile_id: str
    policy_profile_version: str
    outcome: Outcome
    reason_codes: tuple[str, ...]
    evidence_ref_ids: tuple[str, ...]
    evaluated_at: str
    schema_version: Literal["m4-governed-action-sandbox/v1"] = "m4-governed-action-sandbox/v1"

    def __post_init__(self) -> None:
        _base_fields(self.contract_id, self.run_id, self.created_at, "pdr_sha256:")
        _id("decision_id", self.decision_id, "pdr_sha256:")
        if self.contract_id != self.decision_id:
            raise ValueError("PDR contract_id and decision_id must be equal")
        _id("subject_contract_id", self.subject_contract_id, "ci_sha256:")
        _id("input_lineage_digest", self.input_lineage_digest, "sha256:")
        if (self.policy_profile_id, self.policy_profile_version, self.outcome, self.schema_version) not in ((M4_FIXTURE_V1.policy_profile_id, M4_FIXTURE_V1.policy_profile_version, "allowed", "m4-governed-action-sandbox/v1"), (M4_FIXTURE_V1.policy_profile_id, M4_FIXTURE_V1.policy_profile_version, "requires_human_approval", "m4-governed-action-sandbox/v1"), (M4_FIXTURE_V1.policy_profile_id, M4_FIXTURE_V1.policy_profile_version, "blocked", "m4-governed-action-sandbox/v1")):
            raise ValueError("PolicyDecisionRecord has unsupported controlled values")
        _ordered("reason_codes", self.reason_codes)
        _ordered("evidence_ref_ids", self.evidence_ref_ids, "ev_sha256:")
        _timestamp("evaluated_at", self.evaluated_at)
        if self.contract_id != _canonical_id(self, "pdr_sha256:", frozenset({"contract_id", "decision_id", "created_at"})):
            raise ValueError("PolicyDecisionRecord ID must match the canonical payload")


@dataclass(frozen=True, slots=True)
class ResourceObservations:
    wall_clock_ms: int = 0
    sandbox_lifetime_ms: int = 0
    command_output_bytes: int = 0
    workspace_write_bytes: int = 0
    artifact_bytes: Literal[0] = 0
    diff_bytes: Literal[0] = 0
    changed_files: Literal[0] = 0
    tool_call_count: Literal[0, 1] = 0
    limits_reached: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        bounds = (("wall_clock_ms", self.wall_clock_ms, M4_FIXTURE_V1.max_wall_clock_ms), ("sandbox_lifetime_ms", self.sandbox_lifetime_ms, M4_FIXTURE_V1.max_sandbox_lifetime_ms), ("command_output_bytes", self.command_output_bytes, M4_FIXTURE_V1.max_output_bytes), ("workspace_write_bytes", self.workspace_write_bytes, M4_FIXTURE_V1.max_workspace_write_bytes))
        if any(type(value) is not int or value < 0 or value > maximum for _, value, maximum in bounds):
            raise ValueError("resource observations must stay within registered bounds")
        if (type(self.artifact_bytes) is not int or type(self.diff_bytes) is not int or type(self.changed_files) is not int or type(self.tool_call_count) is not int or (self.artifact_bytes, self.diff_bytes, self.changed_files) != (0, 0, 0) or self.tool_call_count not in (0, 1)):
            raise ValueError("Phase 1 observations permit no artifact/diff facts and one command at most")
        _ordered("limits_reached", self.limits_reached)
        if any(limit not in M4_FIXTURE_V1.resource_limit_ids for limit in self.limits_reached):
            raise ValueError("limits_reached must name registered profile limits")
        observed_limit_reached = {
            "max_wall_clock_ms": self.wall_clock_ms >= M4_FIXTURE_V1.max_wall_clock_ms,
            "max_sandbox_lifetime_ms": self.sandbox_lifetime_ms >= M4_FIXTURE_V1.max_sandbox_lifetime_ms,
            "max_command_output_bytes": self.command_output_bytes >= M4_FIXTURE_V1.max_output_bytes,
            "max_workspace_write_bytes": self.workspace_write_bytes >= M4_FIXTURE_V1.max_workspace_write_bytes,
        }
        if any(
            limit != "command_timeout_ms" and not observed_limit_reached[limit]
            for limit in self.limits_reached
        ):
            raise ValueError("limits_reached must be supported by the observed registered bound")


@dataclass(frozen=True, slots=True)
class ExecutionAttempt:
    contract_id: str
    attempt_id: str
    run_id: str
    created_at: str
    command_intent_contract_id: str
    policy_decision_contract_id: str
    status: AttemptStatus
    failure_reason: FailureReason | None
    resource_observations: ResourceObservations
    artifact_ref_ids: tuple[str, ...]
    oci_image_digest: str | None = None
    exit_code: int | None = None
    started_at: str | None = None
    finished_at: str | None = None
    schema_version: Literal["m4-governed-action-sandbox/v1"] = "m4-governed-action-sandbox/v1"

    def __post_init__(self) -> None:
        _base_fields(self.contract_id, self.run_id, self.created_at, "ea_sha256:")
        _id("attempt_id", self.attempt_id, "attempt_sha256:")
        _id("command_intent_contract_id", self.command_intent_contract_id, "ci_sha256:")
        _id("policy_decision_contract_id", self.policy_decision_contract_id, "pdr_sha256:")
        if self.status not in ("succeeded", "failed", "cancelled", "timed_out", "not_started") or self.schema_version != "m4-governed-action-sandbox/v1":
            raise ValueError("ExecutionAttempt has unsupported controlled values")
        if self.status == "succeeded" and self.failure_reason is not None:
            raise ValueError("succeeded attempts cannot have failure reasons")
        if self.status != "succeeded" and self.failure_reason not in ("policy_blocked", "approval_required", "sandbox_unavailable", "base_revision_mismatch", "command_failed", "resource_limit_exceeded", "cancelled_by_request"):
            raise ValueError("non-success attempts require an applicable failure reason")
        if self.artifact_ref_ids:
            raise ValueError("Phase 1 ExecutionAttempt artifact_ref_ids must be empty")
        not_started = self.status == "not_started"
        if not_started:
            if any(value is not None for value in (self.oci_image_digest, self.exit_code, self.started_at, self.finished_at)) or self.resource_observations != ResourceObservations():
                raise ValueError("not_started attempts cannot contain execution facts")
        else:
            if self.oci_image_digest != M4_FIXTURE_V1.oci_image_digest or self.started_at is None or self.finished_at is None or self.resource_observations.tool_call_count != 1:
                raise ValueError("started attempts require observed OCI facts")
            _timestamp("started_at", self.started_at)
            _timestamp("finished_at", self.finished_at)
            if _timestamp_ms(self.finished_at) < _timestamp_ms(self.started_at):
                raise ValueError("started attempts cannot finish before they start")
            if self.exit_code is not None and type(self.exit_code) is not int:
                raise ValueError("exit_code must be an observed integer")
        if self.status == "cancelled" and self.failure_reason != "cancelled_by_request":
            raise ValueError("cancelled attempts require cancelled_by_request")
        if self.failure_reason == "cancelled_by_request" and self.status != "cancelled":
            raise ValueError("cancelled_by_request requires cancelled status")
        pre_start_reasons = {"policy_blocked", "approval_required", "sandbox_unavailable", "base_revision_mismatch"}
        started_reasons = {"command_failed", "resource_limit_exceeded", "cancelled_by_request"}
        if (self.status == "not_started" and self.failure_reason not in pre_start_reasons) or (self.status != "not_started" and self.failure_reason in pre_start_reasons) or (self.status == "succeeded" and self.failure_reason is not None) or (self.status == "cancelled" and self.failure_reason not in started_reasons):
            raise ValueError("ExecutionAttempt status and failure reason must describe compatible facts")
        timeout_reached = "command_timeout_ms" in self.resource_observations.limits_reached
        if timeout_reached and (
            self.status != "timed_out"
            or self.failure_reason != "resource_limit_exceeded"
            or _timestamp_ms(self.finished_at) - _timestamp_ms(self.started_at) < M4_FIXTURE_V1.timeout_ms
        ):
            raise ValueError("command timeout limit requires a proven timed_out lifecycle")
        if self.status == "timed_out" and (
            self.failure_reason != "resource_limit_exceeded"
            or not timeout_reached
            or _timestamp_ms(self.finished_at) - _timestamp_ms(self.started_at) < M4_FIXTURE_V1.timeout_ms
        ):
            raise ValueError("timed_out attempts require the observed command timeout limit")
        limit_reached = bool(self.resource_observations.limits_reached)
        if limit_reached != (self.failure_reason == "resource_limit_exceeded"):
            raise ValueError("reached resource limits require and are required by resource_limit_exceeded")
        expected = _canonical_id(self, "ea_sha256:", frozenset({"contract_id", "attempt_id", "created_at"}))
        if self.contract_id != expected or self.attempt_id != expected.replace("ea_sha256:", "attempt_sha256:"):
            raise ValueError("ExecutionAttempt IDs must match the canonical payload")


def validate_execution_attempt_lineage(
    attempt: ExecutionAttempt, decision: PolicyDecisionRecord
) -> None:
    """Validate the immutable PDR reference and its allowed terminal relationship."""
    if attempt.policy_decision_contract_id != decision.contract_id:
        raise ValueError("ExecutionAttempt must reference the supplied PolicyDecisionRecord")
    if decision.subject_contract_id != attempt.command_intent_contract_id:
        raise ValueError("PolicyDecisionRecord must govern the attempt CommandIntent")
    required_outcomes = {
        "policy_blocked": "blocked",
        "approval_required": "requires_human_approval",
        "base_revision_mismatch": "requires_human_approval",
    }
    required = required_outcomes.get(attempt.failure_reason)
    if required is not None and decision.outcome != required:
        raise ValueError("ExecutionAttempt terminal must match the referenced policy outcome")
    if attempt.failure_reason not in required_outcomes and decision.outcome != "allowed":
        raise ValueError("execution facts require an allowed PolicyDecisionRecord")


def validate_governed_lineage(
    action: ActionIntent, command: CommandIntent, decision: PolicyDecisionRecord
) -> None:
    """Validate immutable ActionIntent → CommandIntent → PDR input lineage."""
    from .canonical import input_lineage_digest_for

    if command.action_intent_contract_id != action.contract_id:
        raise ValueError("CommandIntent must reference the supplied ActionIntent")
    if not (
        action.run_id == command.run_id == decision.run_id
        and action.repository_id == command.repository_id
        and action.base_commit_sha == command.base_commit_sha
        and action.policy_profile_id == command.policy_profile_id == decision.policy_profile_id
        and action.policy_profile_version == command.policy_profile_version == decision.policy_profile_version
    ):
        raise ValueError("governed lineage inputs must match exactly")
    if decision.subject_contract_id != command.contract_id:
        raise ValueError("PolicyDecisionRecord must govern the supplied CommandIntent")
    if decision.input_lineage_digest != input_lineage_digest_for(action, command):
        raise ValueError("PolicyDecisionRecord input lineage digest must be canonical")


@dataclass(frozen=True, slots=True)
class GovernedActionSandboxValidationError:
    error_id: str
    error_code: str
    summary: str
    schema_version: Literal["m4-governed-action-sandbox/v1"] = "m4-governed-action-sandbox/v1"

    def __post_init__(self) -> None:
        _id("error_id", self.error_id, "gase_sha256:")
        if self.error_code not in {"invalid_lineage", "unsupported_schema", "unsupported_profile", "unsupported_command", "image_identity_mismatch", "forbidden_payload", "invalid_fact_combination", "dangling_reference"} or not self.summary or len(self.summary) > 500:
            raise ValueError("validation error must be bounded and controlled")
        if self.error_id != _canonical_id(self, "gase_sha256:", frozenset({"error_id"})):
            raise ValueError("validation error ID must match the canonical payload")
