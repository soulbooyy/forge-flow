from __future__ import annotations

from dataclasses import FrozenInstanceError, fields
from pathlib import Path
import sys
import unittest


sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from forgeflow.governed_changes.action_execution import (  # noqa: E402
    ActionIntent,
    CommandIntent,
    ExecutionAttempt,
    GovernedActionSandboxValidationError,
    M4_FIXTURE_V1,
    PolicyDecisionRecord,
    ResourceObservations,
    input_lineage_digest_for,
    sha256_hex,
    validate_governed_lineage,
    validate_execution_attempt_lineage,
)


def sha(prefix: str, char: str) -> str:
    return f"{prefix}:{char * 64}"


def canonical_id(payload: dict[str, object], prefix: str) -> str:
    return f"{prefix}{sha256_hex(payload)}"


def action() -> ActionIntent:
    payload: dict[str, object] = dict(
        run_id=sha("run_sha256", "1"),
        task_input_contract_id=sha("ti_sha256", "2"),
        repository_id="1300511729",
        base_commit_sha="97c8220cd713ebf61124ac2de2f3eadc6e4dc222",
        requested_command_id="fixture-test-runner-v1",
        policy_profile_id="forgeflow-m4-fixture-only",
        policy_profile_version="1.0.0",
        schema_version="m4-governed-action-sandbox/v1",
        kind="execute_fixture_test",
    )
    digest = canonical_id(payload, "ai_sha256:")
    return ActionIntent(contract_id=digest, action_id=digest.replace("ai_sha256:", "action_sha256:"), created_at="2026-07-15T08:00:00Z", **payload)


def command(*, run_id: str | None = None) -> CommandIntent:
    payload: dict[str, object] = dict(
        run_id=run_id or sha("run_sha256", "1"),
        action_intent_contract_id=action().contract_id,
        repository_id="1300511729",
        base_commit_sha="97c8220cd713ebf61124ac2de2f3eadc6e4dc222",
        command_id="fixture-test-runner-v1",
        executable="python3",
        args=("-m", "unittest", "discover", "-s", "tests"),
        working_directory="workspace_root",
        allowed_environment=(),
        oci_image_digest="sha256:81b691e3b5d43b2f4e717eaeef63437705addd115aee32917efd5d7387807f28",
        timeout_ms=120000,
        max_output_bytes=65536,
        policy_profile_id="forgeflow-m4-fixture-only",
        policy_profile_version="1.0.0",
        schema_version="m4-governed-action-sandbox/v1",
    )
    return CommandIntent(contract_id=canonical_id(payload, "ci_sha256:"), created_at="2026-07-15T08:00:01Z", **payload)


def decision(outcome: str = "allowed", *, subject_contract_id: str | None = None) -> PolicyDecisionRecord:
    current_action = action()
    current_command = command()
    payload: dict[str, object] = dict(
        run_id=sha("run_sha256", "1"),
        subject_contract_id=subject_contract_id or current_command.contract_id,
        input_lineage_digest=input_lineage_digest_for(current_action, current_command),
        policy_profile_id="forgeflow-m4-fixture-only",
        policy_profile_version="1.0.0",
        outcome=outcome,  # type: ignore[arg-type]
        reason_codes=(),
        evidence_ref_ids=(),
        evaluated_at="2026-07-15T08:00:02Z",
        schema_version="m4-governed-action-sandbox/v1",
    )
    identity = canonical_id(payload, "pdr_sha256:")
    return PolicyDecisionRecord(contract_id=identity, decision_id=identity, created_at="2026-07-15T08:00:02Z", **payload)


def attempt(**overrides: object) -> ExecutionAttempt:
    payload: dict[str, object] = dict(
        run_id=sha("run_sha256", "1"), command_intent_contract_id=command().contract_id,
        policy_decision_contract_id=decision().contract_id, status="not_started",
        failure_reason="approval_required", resource_observations=ResourceObservations(),
        artifact_ref_ids=(), oci_image_digest=None, exit_code=None, started_at=None,
        finished_at=None, schema_version="m4-governed-action-sandbox/v1",
    ) | overrides
    identity = canonical_id({key: value for key, value in payload.items() if value is not None}, "ea_sha256:")
    return ExecutionAttempt(contract_id=identity, attempt_id=identity.replace("ea_sha256:", "attempt_sha256:"), created_at="2026-07-15T08:00:03Z", **payload)


class GovernedActionSandboxContractTests(unittest.TestCase):
    def test_profile_and_contract_models_are_exact_frozen_and_slotted(self) -> None:
        intent = action()
        self.assertEqual(intent.schema_version, "m4-governed-action-sandbox/v1")
        self.assertEqual(intent.kind, "execute_fixture_test")
        self.assertEqual(M4_FIXTURE_V1.repository_id, "1300511729")
        self.assertEqual(M4_FIXTURE_V1.max_automatic_retries, 0)
        self.assertFalse(hasattr(intent, "__dict__"))
        with self.assertRaises(FrozenInstanceError):
            intent.repository_id = "different"  # type: ignore[misc]

    def test_command_and_pdr_require_exact_registered_literals(self) -> None:
        self.assertEqual(command().args, ("-m", "unittest", "discover", "-s", "tests"))
        self.assertEqual(command().allowed_environment, ())
        self.assertEqual(decision().contract_id, decision().decision_id)
        with self.assertRaises(ValueError):
            CommandIntent(
                **{field.name: getattr(command(), field.name) for field in fields(command())}
                | {"args": ("-m", "unittest")}
            )

    def test_observations_enforce_registered_bounds_and_not_started_zero_facts(self) -> None:
        zero = ResourceObservations()
        self.assertEqual(zero.tool_call_count, 0)
        with self.assertRaises(ValueError):
            ResourceObservations(command_output_bytes=65537)
        actual_attempt = attempt(policy_decision_contract_id=decision("blocked").contract_id, failure_reason="policy_blocked", resource_observations=zero)
        self.assertEqual(actual_attempt.status, "not_started")
        with self.assertRaises(ValueError):
            ExecutionAttempt(**{field.name: getattr(actual_attempt, field.name) for field in fields(actual_attempt)} | {"oci_image_digest": M4_FIXTURE_V1.oci_image_digest})

    def test_stale_revision_and_cancellation_remain_factual_non_authorizing_terminals(self) -> None:
        stale = attempt(policy_decision_contract_id=decision("requires_human_approval").contract_id, failure_reason="base_revision_mismatch")
        self.assertEqual(stale.failure_reason, "base_revision_mismatch")
        cancelled = attempt(
            status="cancelled", failure_reason="cancelled_by_request", resource_observations=ResourceObservations(tool_call_count=1),
            oci_image_digest=M4_FIXTURE_V1.oci_image_digest,
            started_at="2026-07-15T08:00:04Z", finished_at="2026-07-15T08:00:05Z",
        )
        self.assertEqual(cancelled.failure_reason, "cancelled_by_request")

    def test_validation_error_is_payload_free_and_separate_from_success_contracts(self) -> None:
        error_payload = {"error_code": "forbidden_payload", "summary": "The supplied contract contains a forbidden payload field.", "schema_version": "m4-governed-action-sandbox/v1"}
        error = GovernedActionSandboxValidationError(error_id=canonical_id(error_payload, "gase_sha256:"), **error_payload)
        names = {field.name for field in fields(error)}
        self.assertNotIn("rejected_value", names)
        self.assertNotIn("execution_attempt", names)

    def test_success_contract_ids_must_match_their_canonical_payloads(self) -> None:
        with self.assertRaises(ValueError):
            ActionIntent(**{field.name: getattr(action(), field.name) for field in fields(action())} | {"contract_id": sha("ai_sha256", "a")})
        with self.assertRaises(ValueError):
            CommandIntent(**{field.name: getattr(command(), field.name) for field in fields(command())} | {"contract_id": sha("ci_sha256", "b")})
        with self.assertRaises(ValueError):
            PolicyDecisionRecord(**{field.name: getattr(decision(), field.name) for field in fields(decision())} | {"contract_id": sha("pdr_sha256", "c"), "decision_id": sha("pdr_sha256", "c")})

    def test_execution_status_and_failure_reason_combinations_are_truthful(self) -> None:
        with self.assertRaises(ValueError):
            ExecutionAttempt(
                contract_id=sha("ea_sha256", "d"), attempt_id=sha("attempt_sha256", "e"),
                run_id=sha("run_sha256", "1"), created_at="2026-07-15T08:00:03Z",
                command_intent_contract_id=command().contract_id,
                policy_decision_contract_id=decision().contract_id,
                status="failed", failure_reason="base_revision_mismatch",
                resource_observations=ResourceObservations(tool_call_count=1), artifact_ref_ids=(),
                oci_image_digest=M4_FIXTURE_V1.oci_image_digest,
                started_at="2026-07-15T08:00:03Z",
            )
        with self.assertRaises(ValueError):
            ExecutionAttempt(
                contract_id=sha("ea_sha256", "d"), attempt_id=sha("attempt_sha256", "e"),
                run_id=sha("run_sha256", "1"), created_at="2026-07-15T08:00:03Z",
                command_intent_contract_id=command().contract_id,
                policy_decision_contract_id=decision().contract_id,
                status="not_started", failure_reason="command_failed",
                resource_observations=ResourceObservations(), artifact_ref_ids=(),
            )

    def test_resource_observations_accept_only_profile_owned_integer_limits(self) -> None:
        with self.assertRaises(ValueError):
            ResourceObservations(limits_reached=("raw output or secret",))
        with self.assertRaises(ValueError):
            ResourceObservations(artifact_bytes=True)  # type: ignore[arg-type]
        with self.assertRaises(ValueError):
            ResourceObservations(tool_call_count=0.0)  # type: ignore[arg-type]

    def test_timeout_and_reached_limits_have_exact_terminal_semantics(self) -> None:
        with self.assertRaises(ValueError):
            attempt(
                status="timed_out", failure_reason="command_failed",
                resource_observations=ResourceObservations(tool_call_count=1),
                oci_image_digest=M4_FIXTURE_V1.oci_image_digest,
                started_at="2026-07-15T08:00:04Z",
            )
        with self.assertRaises(ValueError):
            attempt(
                status="succeeded", failure_reason=None,
                resource_observations=ResourceObservations(
                    tool_call_count=1, limits_reached=("max_wall_clock_ms",)
                ),
                oci_image_digest=M4_FIXTURE_V1.oci_image_digest,
                started_at="2026-07-15T08:00:04Z",
            )
        with self.assertRaises(ValueError):
            attempt(
                status="failed", failure_reason="resource_limit_exceeded",
                resource_observations=ResourceObservations(tool_call_count=1),
                oci_image_digest=M4_FIXTURE_V1.oci_image_digest,
                started_at="2026-07-15T08:00:04Z",
            )

    def test_attempt_lineage_matches_the_referenced_policy_outcome(self) -> None:
        stale = attempt(
            policy_decision_contract_id=decision("requires_human_approval").contract_id,
            failure_reason="base_revision_mismatch",
        )
        validate_execution_attempt_lineage(stale, decision("requires_human_approval"))
        with self.assertRaises(ValueError):
            validate_execution_attempt_lineage(stale, decision())
        unrelated = command(run_id=sha("run_sha256", "9"))
        unrelated_decision = decision(subject_contract_id=unrelated.contract_id)
        with self.assertRaises(ValueError):
            validate_execution_attempt_lineage(
                attempt(policy_decision_contract_id=unrelated_decision.contract_id),
                unrelated_decision,
            )

    def test_reached_limits_require_their_observed_bound_and_timeout_limit(self) -> None:
        with self.assertRaises(ValueError):
            ResourceObservations(limits_reached=("max_wall_clock_ms",))
        timed_out = attempt(
            status="timed_out", failure_reason="resource_limit_exceeded",
            resource_observations=ResourceObservations(
                wall_clock_ms=120000,
                tool_call_count=1,
                limits_reached=("command_timeout_ms",),
            ),
            oci_image_digest=M4_FIXTURE_V1.oci_image_digest,
            started_at="2026-07-15T08:00:04Z",
            finished_at="2026-07-15T08:02:04Z",
        )
        self.assertEqual(timed_out.status, "timed_out")
        with self.assertRaises(ValueError):
            attempt(
                status="timed_out", failure_reason="resource_limit_exceeded",
                resource_observations=ResourceObservations(
                    command_output_bytes=65536,
                    tool_call_count=1,
                    limits_reached=("max_command_output_bytes",),
                ),
                oci_image_digest=M4_FIXTURE_V1.oci_image_digest,
                started_at="2026-07-15T08:00:04Z",
            )

    def test_started_attempt_exit_code_is_an_integer_fact(self) -> None:
        with self.assertRaises(ValueError):
            attempt(
                status="failed", failure_reason="command_failed",
                resource_observations=ResourceObservations(tool_call_count=1),
                oci_image_digest=M4_FIXTURE_V1.oci_image_digest,
                exit_code="raw output",  # type: ignore[arg-type]
                started_at="2026-07-15T08:00:04Z",
                finished_at="2026-07-15T08:00:05Z",
            )

    def test_governed_lineage_recomputes_input_digest_and_cross_contract_bindings(self) -> None:
        current_action = action()
        current_command = command()
        current_decision = decision()
        validate_governed_lineage(current_action, current_command, current_decision)
        with self.assertRaises(ValueError):
            validate_governed_lineage(
                action(), command(run_id=sha("run_sha256", "9")), current_decision
            )
        with self.assertRaises(ValueError):
            attempt(
                status="timed_out", failure_reason="resource_limit_exceeded",
                resource_observations=ResourceObservations(
                    wall_clock_ms=120000,
                    tool_call_count=1,
                    limits_reached=("command_timeout_ms",),
                ),
                oci_image_digest=M4_FIXTURE_V1.oci_image_digest,
                started_at="2026-07-15T08:00:04Z",
                finished_at="2026-07-15T08:00:05Z",
            )
        with self.assertRaises(ValueError):
            attempt(
                status="failed", failure_reason="resource_limit_exceeded",
                resource_observations=ResourceObservations(
                    tool_call_count=1, limits_reached=("command_timeout_ms",)
                ),
                oci_image_digest=M4_FIXTURE_V1.oci_image_digest,
                started_at="2026-07-15T08:00:04Z",
                finished_at="2026-07-15T08:02:04Z",
            )
        with self.assertRaises(ValueError):
            attempt(
                status="failed", failure_reason="command_failed",
                resource_observations=ResourceObservations(tool_call_count=1),
                oci_image_digest=M4_FIXTURE_V1.oci_image_digest,
                started_at="2026-07-15T08:00:04Z",
            )
        with self.assertRaises(ValueError):
            attempt(
                status="failed", failure_reason="command_failed",
                resource_observations=ResourceObservations(tool_call_count=1),
                oci_image_digest=M4_FIXTURE_V1.oci_image_digest,
                started_at="2026-07-15T08:00:04Z",
                finished_at="2026-07-15T08:00:03Z",
            )
