from __future__ import annotations

import json
from dataclasses import fields
from pathlib import Path
import sys
import unittest


sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from forgeflow.governed_changes.action_execution import (  # noqa: E402
    OciRunFacts,
    OciCapabilityProof,
    build_action_intent,
    build_command_intent,
    evaluate_command_intent,
    execute_governed_attempt,
)
from forgeflow.governed_changes.action_execution.models import ResourceObservations  # noqa: E402
from forgeflow.governed_changes.action_execution.models import PolicyDecisionRecord  # noqa: E402
from forgeflow.governed_changes.action_execution import sha256_hex  # noqa: E402


RUN_ID = "run_sha256:" + "5" * 64
TASK_ID = "ti_sha256:" + "6" * 64
ACTION_AT = "2026-07-15T11:00:00Z"
COMMAND_AT = "2026-07-15T11:00:01Z"
EVALUATED_AT = "2026-07-15T11:00:02Z"
EXPECTED = Path(__file__).resolve().parents[2] / "openspec" / "changes" / "governed-action-sandbox" / "fixtures" / "expected" / "phase-3-service"


class CountingBackend:
    def __init__(self, facts: OciRunFacts) -> None:
        self.facts = facts
        self.calls = 0

    def prove(self, command):  # type: ignore[no-untyped-def]
        return OciCapabilityProof(True, True, True, True, True, True, True)

    def run(self, command):  # type: ignore[no-untyped-def]
        self.calls += 1
        return self.facts


def action_and_command():  # type: ignore[no-untyped-def]
    action = build_action_intent(run_id=RUN_ID, task_input_contract_id=TASK_ID, created_at=ACTION_AT)
    return action, build_command_intent(action, created_at=COMMAND_AT)


def started_facts(**changes: object) -> OciRunFacts:
    values: dict[str, object] = {
        "image_digest_proven": True,
        "network_disabled": True,
        "credentials_absent": True,
        "dynamic_installation_disabled": True,
        "fixed_revision_workspace": True,
        "workspace_writes_confined": True,
        "artifact_store_unmounted": True,
        "workspace_destroyed": True,
        "started": True,
        "status": "succeeded",
        "failure_reason": None,
        "exit_code": 0,
        "started_at": "2026-07-15T11:00:03Z",
        "finished_at": "2026-07-15T11:00:04Z",
        "resource_observations": ResourceObservations(tool_call_count=1),
    }
    values.update(changes)
    return OciRunFacts(**values)


class GovernedAttemptServiceTests(unittest.TestCase):
    def test_blocked_approval_and_stale_pdrs_never_call_backend(self) -> None:
        action, command = action_and_command()
        pdrs = (
            evaluate_command_intent(command, evaluated_at=EVALUATED_AT, command_args=("-m", "unittest", "-v"))[0],
            evaluate_command_intent(command, evaluated_at=EVALUATED_AT, requires_human_approval=True)[0],
            evaluate_command_intent(command, evaluated_at=EVALUATED_AT, current_base_commit_sha="0" * 40)[0],
        )
        expected = (("not_started", "policy_blocked"), ("not_started", "approval_required"), ("not_started", "base_revision_mismatch"))

        for record, terminal in zip(pdrs, expected, strict=True):
            backend = CountingBackend(started_facts())
            attempt = execute_governed_attempt(action, command, record, backend)
            self.assertEqual((attempt.status, attempt.failure_reason), terminal)
            self.assertEqual(backend.calls, 0)
            self.assertEqual(attempt.resource_observations, ResourceObservations())

    def test_started_command_failure_and_cancellation_preserve_distinct_facts(self) -> None:
        action, command = action_and_command()
        record = evaluate_command_intent(command, evaluated_at=EVALUATED_AT)[0]
        failed = execute_governed_attempt(
            action,
            command,
            record,
            CountingBackend(started_facts(status="failed", failure_reason="command_failed", exit_code=1)),
        )
        cancelled = execute_governed_attempt(
            action,
            command,
            record,
            CountingBackend(started_facts(status="cancelled", failure_reason="cancelled_by_request", exit_code=None)),
        )

        self.assertEqual((failed.status, failed.failure_reason, failed.exit_code), ("failed", "command_failed", 1))
        self.assertEqual((cancelled.status, cancelled.failure_reason), ("cancelled", "cancelled_by_request"))

    def test_timeout_and_output_budget_are_resource_limit_terminals(self) -> None:
        action, command = action_and_command()
        record = evaluate_command_intent(command, evaluated_at=EVALUATED_AT)[0]
        timeout = execute_governed_attempt(
            action,
            command,
            record,
            CountingBackend(started_facts(status="timed_out", failure_reason="resource_limit_exceeded", exit_code=None, started_at="2026-07-15T11:00:03Z", finished_at="2026-07-15T11:02:03Z", resource_observations=ResourceObservations(tool_call_count=1, limits_reached=("command_timeout_ms",)))),
        )
        output_limited = execute_governed_attempt(
            action,
            command,
            record,
            CountingBackend(started_facts(status="failed", failure_reason="resource_limit_exceeded", exit_code=None, resource_observations=ResourceObservations(command_output_bytes=65536, tool_call_count=1, limits_reached=("max_command_output_bytes",)))),
        )

        self.assertEqual((timeout.status, timeout.failure_reason), ("timed_out", "resource_limit_exceeded"))
        self.assertEqual((output_limited.status, output_limited.failure_reason), ("failed", "resource_limit_exceeded"))

    def test_foreign_evaluated_input_returns_error_without_backend_call(self) -> None:
        action, command = action_and_command()
        other_action = build_action_intent(run_id="run_sha256:" + "7" * 64, task_input_contract_id=TASK_ID, created_at=ACTION_AT)
        other_command = build_command_intent(other_action, created_at=COMMAND_AT)
        foreign_pdr = evaluate_command_intent(other_command, evaluated_at=EVALUATED_AT)[0]
        backend = CountingBackend(started_facts())

        result = execute_governed_attempt(action, command, foreign_pdr, backend)

        self.assertEqual(result.error_code, "invalid_lineage")
        self.assertEqual(backend.calls, 0)

    def test_tampered_allowed_pdr_digest_returns_error_without_backend_call(self) -> None:
        action, command = action_and_command()
        original = evaluate_command_intent(command, evaluated_at=EVALUATED_AT)[0]
        payload = {field.name: getattr(original, field.name) for field in fields(original) if field.name not in {"contract_id", "decision_id", "created_at"}}
        payload["input_lineage_digest"] = "sha256:" + "0" * 64
        identity = "pdr_sha256:" + sha256_hex(payload)
        tampered = PolicyDecisionRecord(contract_id=identity, decision_id=identity, created_at=original.created_at, **payload)
        backend = CountingBackend(started_facts())

        result = execute_governed_attempt(action, command, tampered, backend)

        self.assertEqual(result.error_code, "invalid_lineage")
        self.assertEqual(backend.calls, 0)

    def test_backend_faults_and_malformed_started_facts_do_not_escape(self) -> None:
        action, command = action_and_command()
        record = evaluate_command_intent(command, evaluated_at=EVALUATED_AT)[0]
        proof_fault = execute_governed_attempt(action, command, record, ProofFaultBackend(started_facts()))
        run_fault = execute_governed_attempt(action, command, record, RunFaultBackend(started_facts()))
        none_facts = execute_governed_attempt(action, command, record, NoneFactsBackend(started_facts()))
        duck_proof = execute_governed_attempt(action, command, record, DuckProofBackend(started_facts()))
        malformed = execute_governed_attempt(
            action, command, record,
            CountingBackend(started_facts(status="not_started", failure_reason="sandbox_unavailable")),
        )
        unstarted_after_run = execute_governed_attempt(
            action, command, record,
            CountingBackend(started_facts(started=False, status="not_started", failure_reason="sandbox_unavailable", exit_code=None, started_at=None, finished_at=None, resource_observations=ResourceObservations())),
        )
        inconsistent_security = execute_governed_attempt(
            action, command, record, CountingBackend(started_facts(network_disabled=False)),
        )

        self.assertEqual((proof_fault.status, proof_fault.failure_reason), ("not_started", "sandbox_unavailable"))
        self.assertEqual(run_fault.error_code, "invalid_fact_combination")
        self.assertEqual(none_facts.error_code, "invalid_fact_combination")
        self.assertEqual((duck_proof.status, duck_proof.failure_reason), ("not_started", "sandbox_unavailable"))
        self.assertEqual(malformed.error_code, "invalid_fact_combination")
        self.assertEqual(unstarted_after_run.error_code, "invalid_fact_combination")
        self.assertEqual(inconsistent_security.error_code, "invalid_fact_combination")

    def test_expected_terminal_fragments_are_locked(self) -> None:
        action, command = action_and_command()
        cases = {
            "blocked.json": execute_governed_attempt(action, command, evaluate_command_intent(command, evaluated_at=EVALUATED_AT, command_args=("-m", "unittest", "-v"))[0], CountingBackend(started_facts())),
            "approval-required.json": execute_governed_attempt(action, command, evaluate_command_intent(command, evaluated_at=EVALUATED_AT, requires_human_approval=True)[0], CountingBackend(started_facts())),
            "sandbox-unavailable.json": execute_governed_attempt(action, command, evaluate_command_intent(command, evaluated_at=EVALUATED_AT)[0], UnprovenBackend()),
            "cancelled.json": execute_governed_attempt(action, command, evaluate_command_intent(command, evaluated_at=EVALUATED_AT)[0], CountingBackend(started_facts(status="cancelled", failure_reason="cancelled_by_request", exit_code=None))),
        }
        for filename, attempt in cases.items():
            self.assertEqual({"status": attempt.status, "failure_reason": attempt.failure_reason}, json.loads((EXPECTED / filename).read_text(encoding="utf-8")))


class UnprovenBackend(CountingBackend):
    def __init__(self) -> None:
        super().__init__(started_facts())

    def prove(self, command):  # type: ignore[no-untyped-def]
        return OciCapabilityProof(True, False, True, True, True, True, True)


class ProofFaultBackend(CountingBackend):
    def prove(self, command):  # type: ignore[no-untyped-def]
        raise RuntimeError("unavailable")


class RunFaultBackend(CountingBackend):
    def run(self, command):  # type: ignore[no-untyped-def]
        raise RuntimeError("backend fault")


class NoneFactsBackend(CountingBackend):
    def run(self, command):  # type: ignore[no-untyped-def]
        return None


class DuckProofBackend(CountingBackend):
    def prove(self, command):  # type: ignore[no-untyped-def]
        return type("Proof", (), {"proven": True})()


if __name__ == "__main__":
    unittest.main()
