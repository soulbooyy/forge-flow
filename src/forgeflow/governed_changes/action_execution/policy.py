"""Pure Phase 2 policy assembly for the sole registered M4 command."""

from __future__ import annotations

from collections.abc import Mapping

from .canonical import sha256_hex
from .models import (
    ActionIntent,
    CommandIntent,
    ExecutionAttempt,
    PolicyDecisionRecord,
    ResourceObservations,
)
from .profile import M4_FIXTURE_V1


_SCHEMA = "m4-governed-action-sandbox/v1"
_OMITTED = object()


def build_action_intent(*, run_id: str, task_input_contract_id: str, created_at: str) -> ActionIntent:
    """Build the sole declarative action from registered fixture lineage."""
    payload: dict[str, object] = {
        "run_id": run_id,
        "task_input_contract_id": task_input_contract_id,
        "repository_id": M4_FIXTURE_V1.repository_id,
        "base_commit_sha": M4_FIXTURE_V1.base_commit_sha,
        "requested_command_id": M4_FIXTURE_V1.command_id,
        "policy_profile_id": M4_FIXTURE_V1.policy_profile_id,
        "policy_profile_version": M4_FIXTURE_V1.policy_profile_version,
        "schema_version": _SCHEMA,
        "kind": "execute_fixture_test",
    }
    contract_id = f"ai_sha256:{sha256_hex(payload)}"
    return ActionIntent(
        contract_id=contract_id,
        action_id=contract_id.replace("ai_sha256:", "action_sha256:"),
        created_at=created_at,
        **payload,
    )


def build_command_intent(action: ActionIntent, *, created_at: str) -> CommandIntent:
    """Render the exact registered command without granting execution authority."""
    payload: dict[str, object] = {
        "run_id": action.run_id,
        "action_intent_contract_id": action.contract_id,
        "repository_id": action.repository_id,
        "base_commit_sha": action.base_commit_sha,
        "command_id": M4_FIXTURE_V1.command_id,
        "executable": M4_FIXTURE_V1.executable,
        "args": M4_FIXTURE_V1.args,
        "working_directory": M4_FIXTURE_V1.working_directory,
        "allowed_environment": M4_FIXTURE_V1.allowed_environment,
        "oci_image_digest": M4_FIXTURE_V1.oci_image_digest,
        "timeout_ms": M4_FIXTURE_V1.timeout_ms,
        "max_output_bytes": M4_FIXTURE_V1.max_output_bytes,
        "policy_profile_id": action.policy_profile_id,
        "policy_profile_version": action.policy_profile_version,
        "schema_version": _SCHEMA,
    }
    return CommandIntent(
        contract_id=f"ci_sha256:{sha256_hex(payload)}", created_at=created_at, **payload
    )


def evaluate_command_intent(
    command: CommandIntent,
    *,
    evaluated_at: str,
    current_base_commit_sha: str | None = None,
    command_args: object = _OMITTED,
    current_capability: Mapping[str, object] | None = None,
    requires_human_approval: bool = False,
) -> tuple[PolicyDecisionRecord, ExecutionAttempt | None]:
    """Evaluate current registered inputs and assemble only a PDR or no-start terminal."""
    current_base = M4_FIXTURE_V1.base_commit_sha if current_base_commit_sha is None else current_base_commit_sha
    current = {
        "repository_id": command.repository_id,
        "base_commit_sha": current_base,
        "command_id": command.command_id,
        "executable": command.executable,
        "args": command.args if command_args is _OMITTED else command_args,
        "working_directory": command.working_directory,
        "allowed_environment": command.allowed_environment,
        "oci_image_digest": command.oci_image_digest,
        "timeout_ms": command.timeout_ms,
        "max_output_bytes": command.max_output_bytes,
        "policy_profile_id": command.policy_profile_id,
        "policy_profile_version": command.policy_profile_version,
    }
    unknown_capability: dict[str, object] = {}
    if current_capability is not None:
        allowed = frozenset(current)
        unknown_capability = {
            key: value for key, value in current_capability.items() if key not in allowed
        }
        current.update({key: value for key, value in current_capability.items() if key in allowed})
    expected = {
        "repository_id": M4_FIXTURE_V1.repository_id,
        "base_commit_sha": M4_FIXTURE_V1.base_commit_sha,
        "command_id": M4_FIXTURE_V1.command_id,
        "executable": M4_FIXTURE_V1.executable,
        "args": M4_FIXTURE_V1.args,
        "working_directory": M4_FIXTURE_V1.working_directory,
        "allowed_environment": M4_FIXTURE_V1.allowed_environment,
        "oci_image_digest": M4_FIXTURE_V1.oci_image_digest,
        "timeout_ms": M4_FIXTURE_V1.timeout_ms,
        "max_output_bytes": M4_FIXTURE_V1.max_output_bytes,
        "policy_profile_id": M4_FIXTURE_V1.policy_profile_id,
        "policy_profile_version": M4_FIXTURE_V1.policy_profile_version,
    }
    if command.base_commit_sha != current["base_commit_sha"]:
        outcome, reason, failure = (
            "requires_human_approval",
            "base_revision_mismatch",
            "base_revision_mismatch",
        )
    elif requires_human_approval:
        outcome, reason, failure = (
            "requires_human_approval",
            "approval_required",
            "approval_required",
        )
    elif unknown_capability or current != expected:
        outcome, reason, failure = "blocked", "command_mismatch", "policy_blocked"
    else:
        outcome, reason, failure = "allowed", "registered_command", None

    record = _decision(
        command, evaluated_at=evaluated_at, outcome=outcome, reason=reason,
        current=current,
        unknown_capability=unknown_capability,
        requires_human_approval=requires_human_approval,
    )
    if failure is None:
        return record, None
    return record, _not_started_attempt(command, record, failure=failure, created_at=evaluated_at)


def _decision(
    command: CommandIntent, *, evaluated_at: str, outcome: str, reason: str,
    current: Mapping[str, object], unknown_capability: Mapping[str, object],
    requires_human_approval: bool,
) -> PolicyDecisionRecord:
    payload: dict[str, object] = {
        "run_id": command.run_id,
        "subject_contract_id": command.contract_id,
        "input_lineage_digest": _current_lineage_digest(
            command,
            current=current,
            unknown_capability=unknown_capability,
            requires_human_approval=requires_human_approval,
        ),
        "policy_profile_id": command.policy_profile_id,
        "policy_profile_version": command.policy_profile_version,
        "outcome": outcome,
        "reason_codes": (reason,),
        "evidence_ref_ids": (),
        "evaluated_at": evaluated_at,
        "schema_version": _SCHEMA,
    }
    identity = f"pdr_sha256:{sha256_hex(payload)}"
    return PolicyDecisionRecord(
        contract_id=identity, decision_id=identity, created_at=evaluated_at, **payload
    )


def _current_lineage_digest(
    command: CommandIntent,
    *,
    current: Mapping[str, object],
    unknown_capability: Mapping[str, object],
    requires_human_approval: bool,
) -> str:
    payload: dict[str, object] = {
        "action_intent_contract_id": command.action_intent_contract_id,
        "command_intent_contract_id": command.contract_id,
        "repository_id": command.repository_id,
        "base_commit_sha": command.base_commit_sha,
        "policy_profile_id": command.policy_profile_id,
        "policy_profile_version": command.policy_profile_version,
        "oci_image_digest": command.oci_image_digest,
    }
    for name in (
        "repository_id",
        "base_commit_sha",
        "policy_profile_id",
        "policy_profile_version",
        "oci_image_digest",
        "command_id",
        "executable",
        "args",
        "working_directory",
        "allowed_environment",
        "timeout_ms",
        "max_output_bytes",
    ):
        if current[name] != getattr(command, name):
            payload[f"evaluated_{name}_digest"] = _value_digest(current[name])
    if requires_human_approval:
        payload["requires_human_approval"] = True
    if unknown_capability:
        payload["unknown_capability_digest"] = _value_digest(unknown_capability)
    return "sha256:" + sha256_hex(payload)


def _value_digest(value: object) -> str:
    return "sha256:" + sha256_hex(_presence_bound(value))


def _presence_bound(value: object) -> object:
    """Return a canonical value that preserves type and explicit null presence."""
    if value is None:
        return {"kind": "null"}
    if isinstance(value, bool):
        return {"kind": "bool", "value": value}
    if isinstance(value, int):
        return {"kind": "int", "value": value}
    if isinstance(value, str):
        return {"kind": "str", "value": value}
    if isinstance(value, float):
        return {"kind": "float", "value": value.hex()}
    if isinstance(value, Mapping):
        entries = tuple(
            {"key": _presence_bound(key), "value": _presence_bound(item)}
            for key, item in value.items()
        )
        return {"kind": "mapping", "entries": tuple(sorted(entries, key=sha256_hex))}
    if isinstance(value, (list, tuple)):
        return {"kind": "sequence", "entries": tuple(_presence_bound(item) for item in value)}
    raise TypeError(f"unsupported current capability value: {type(value).__name__}")


def _not_started_attempt(
    command: CommandIntent, record: PolicyDecisionRecord, *, failure: str, created_at: str
) -> ExecutionAttempt:
    payload: dict[str, object] = {
        "run_id": command.run_id,
        "command_intent_contract_id": command.contract_id,
        "policy_decision_contract_id": record.contract_id,
        "status": "not_started",
        "failure_reason": failure,
        "resource_observations": ResourceObservations(),
        "artifact_ref_ids": (),
        "schema_version": _SCHEMA,
    }
    identity = f"ea_sha256:{sha256_hex(payload)}"
    return ExecutionAttempt(
        contract_id=identity,
        attempt_id=identity.replace("ea_sha256:", "attempt_sha256:"),
        created_at=created_at,
        **payload,
    )
