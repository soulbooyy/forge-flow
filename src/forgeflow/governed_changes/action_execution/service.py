"""PDR-first governed attempt assembly using an injected OCI backend."""

from __future__ import annotations

from .canonical import sha256_hex
from .models import ActionIntent, CommandIntent, ExecutionAttempt, GovernedActionSandboxValidationError, PolicyDecisionRecord, ResourceObservations, validate_governed_lineage
from .oci_adapter import OciBackend, OciCapabilityProof, OciRunFacts


def execute_governed_attempt(action: ActionIntent, command: CommandIntent, decision: PolicyDecisionRecord, backend: OciBackend) -> ExecutionAttempt | GovernedActionSandboxValidationError:
    if not _valid_inputs(action, command, decision):
        return _error("invalid_lineage", "The evaluated input lineage is invalid.")
    if decision.outcome != "allowed":
        failure = "policy_blocked" if decision.outcome == "blocked" else ("base_revision_mismatch" if "base_revision_mismatch" in decision.reason_codes else "approval_required")
        return _attempt(command, decision, status="not_started", failure_reason=failure, created_at=decision.evaluated_at)
    try:
        validate_governed_lineage(action, command, decision)
    except ValueError:
        return _error("invalid_lineage", "The allowed decision lineage is invalid.")
    try:
        proof = backend.prove(command)
        proven = type(proof) is OciCapabilityProof and proof.proven
    except Exception:
        return _attempt(command, decision, status="not_started", failure_reason="sandbox_unavailable", created_at=decision.evaluated_at)
    if not proven:
        return _attempt(command, decision, status="not_started", failure_reason="sandbox_unavailable", created_at=decision.evaluated_at)
    try:
        facts = backend.run(command)
    except Exception:
        return _error("invalid_fact_combination", "The backend did not return bounded execution facts.")
    try:
        if type(facts) is not OciRunFacts or not facts.started or not facts.security_facts_valid:
            return _error("invalid_fact_combination", "The backend returned invalid bounded execution facts.")
        return _attempt(command, decision, status=facts.status, failure_reason=facts.failure_reason, created_at=facts.finished_at or facts.started_at or decision.evaluated_at, observations=facts.resource_observations, exit_code=facts.exit_code, started_at=facts.started_at, finished_at=facts.finished_at)
    except (AttributeError, TypeError, ValueError):
        return _error("invalid_fact_combination", "The backend returned invalid bounded execution facts.")


def _valid_inputs(action: ActionIntent, command: CommandIntent, decision: PolicyDecisionRecord) -> bool:
    return (command.action_intent_contract_id == action.contract_id and decision.subject_contract_id == command.contract_id and action.run_id == command.run_id == decision.run_id and action.repository_id == command.repository_id and action.base_commit_sha == command.base_commit_sha and action.policy_profile_id == command.policy_profile_id == decision.policy_profile_id and action.policy_profile_version == command.policy_profile_version == decision.policy_profile_version)


def _attempt(command: CommandIntent, decision: PolicyDecisionRecord, *, status: str, failure_reason: str | None, created_at: str, observations: ResourceObservations = ResourceObservations(), exit_code: int | None = None, started_at: str | None = None, finished_at: str | None = None) -> ExecutionAttempt:
    payload = {"run_id": command.run_id, "command_intent_contract_id": command.contract_id, "policy_decision_contract_id": decision.contract_id, "status": status, "failure_reason": failure_reason, "resource_observations": observations, "artifact_ref_ids": (), "oci_image_digest": command.oci_image_digest if status != "not_started" else None, "exit_code": exit_code, "started_at": started_at, "finished_at": finished_at, "schema_version": "m4-governed-action-sandbox/v1"}
    identity = "ea_sha256:" + sha256_hex(payload)
    return ExecutionAttempt(contract_id=identity, attempt_id=identity.replace("ea_sha256:", "attempt_sha256:"), created_at=created_at, **payload)


def _error(error_code: str, summary: str) -> GovernedActionSandboxValidationError:
    payload = {"error_code": error_code, "summary": summary, "schema_version": "m4-governed-action-sandbox/v1"}
    return GovernedActionSandboxValidationError(error_id="gase_sha256:" + sha256_hex(payload), **payload)
