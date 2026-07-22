from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest


sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from forgeflow.governed_changes.action_execution import (  # noqa: E402
    M4_FIXTURE_V1,
    OciCapabilityProof,
    OciRunFacts,
    ResourceObservations,
    validate_governed_lineage,
    build_action_intent,
    build_command_intent,
    evaluate_command_intent,
    execution_attempt_id_for,
    execute_governed_attempt,
)


ROOT = Path(__file__).resolve().parents[2]
EXPECTED = ROOT / "openspec" / "changes" / "governed-action-sandbox" / "fixtures" / "expected" / "phase-4-acceptance"
RUN_ID = "run_sha256:" + "8" * 64
TASK_ID = "ti_sha256:" + "9" * 64


class NeverRunBackend:
    def __init__(self) -> None:
        self.run_calls = 0
        self.prove_calls = 0

    def prove(self, command):  # type: ignore[no-untyped-def]
        self.prove_calls += 1
        return OciCapabilityProof(True, True, True, True, True, True, True)

    def run(self, command):  # type: ignore[no-untyped-def]
        self.run_calls += 1
        return OciRunFacts(True, True, True, True, True, True, True, True, True, "succeeded", None, 0, "2026-07-16T08:00:03Z", "2026-07-16T08:00:04Z", ResourceObservations(tool_call_count=1))


class UnavailableBackend(NeverRunBackend):
    def prove(self, command):  # type: ignore[no-untyped-def]
        return OciCapabilityProof(True, False, True, True, True, True, True)


class FactsBackend(NeverRunBackend):
    def __init__(self, facts: OciRunFacts) -> None:
        super().__init__()
        self.facts = facts

    def run(self, command):  # type: ignore[no-untyped-def]
        self.run_calls += 1
        return self.facts


class RawPayloadBackend(NeverRunBackend):
    def run(self, command):  # type: ignore[no-untyped-def]
        self.run_calls += 1
        return type("RawFacts", (), {"started": True, "raw_output": "secret"})()


class GovernedActionSandboxAcceptanceTests(unittest.TestCase):
    def test_deterministic_non_allowed_matrix_has_zero_backend_effects(self) -> None:
        action = build_action_intent(run_id=RUN_ID, task_input_contract_id=TASK_ID, created_at="2026-07-16T08:00:00Z")
        command = build_command_intent(action, created_at="2026-07-16T08:00:01Z")
        cases = {
            "blocked.json": evaluate_command_intent(command, evaluated_at="2026-07-16T08:00:02Z", command_args=("-m", "unittest", "-v"))[0],
            "approval.json": evaluate_command_intent(command, evaluated_at="2026-07-16T08:00:02Z", requires_human_approval=True)[0],
            "stale.json": evaluate_command_intent(command, evaluated_at="2026-07-16T08:00:02Z", current_base_commit_sha="0" * 40)[0],
        }
        for filename, decision in cases.items():
            backend = NeverRunBackend()
            attempt = execute_governed_attempt(action, command, decision, backend)
            self.assertEqual(backend.run_calls, 0)
            self.assertEqual(backend.prove_calls, 0)
            self.assertEqual(attempt.contract_id, execution_attempt_id_for(attempt))
            self.assertEqual(attempt.attempt_id, attempt.contract_id.replace("ea_sha256:", "attempt_sha256:"))
            self.assertEqual(decision.contract_id, decision.decision_id)
            self.assertTrue(decision.contract_id.startswith("pdr_sha256:"))
            self.assertEqual(decision.outcome, "blocked" if filename == "blocked.json" else "requires_human_approval")
            self.assertEqual(attempt.resource_observations, ResourceObservations())
            self.assertEqual({"status": attempt.status, "failure_reason": attempt.failure_reason}, json.loads((EXPECTED / filename).read_text(encoding="utf-8")))

    def test_oci_capability_failure_and_contract_surfaces_are_fail_closed(self) -> None:
        action = build_action_intent(run_id=RUN_ID, task_input_contract_id=TASK_ID, created_at="2026-07-16T08:00:00Z")
        command = build_command_intent(action, created_at="2026-07-16T08:00:01Z")
        decision = evaluate_command_intent(command, evaluated_at="2026-07-16T08:00:02Z")[0]
        backend = UnavailableBackend()
        attempt = execute_governed_attempt(action, command, decision, backend)

        self.assertEqual((attempt.status, attempt.failure_reason), ("not_started", "sandbox_unavailable"))
        self.assertEqual(backend.run_calls, 0)
        self.assertEqual(attempt.artifact_ref_ids, ())
        for path in (ROOT / "src" / "forgeflow" / "governed_changes" / "action_execution").glob("*.py"):
            source = path.read_text(encoding="utf-8")
            for forbidden in ("subprocess", "socket", "requests", "urllib", "httpx", "os.system", "pathlib.Path"):
                self.assertNotIn(forbidden, source)

    def test_allowed_and_started_terminal_matrix_preserves_canonical_facts(self) -> None:
        action = build_action_intent(run_id=RUN_ID, task_input_contract_id=TASK_ID, created_at="2026-07-16T08:00:00Z")
        command = build_command_intent(action, created_at="2026-07-16T08:00:01Z")
        decision = evaluate_command_intent(command, evaluated_at="2026-07-16T08:00:02Z")[0]
        validate_governed_lineage(action, command, decision)
        self.assertTrue(action.contract_id.startswith("ai_sha256:"))
        self.assertTrue(command.contract_id.startswith("ci_sha256:"))
        self.assertEqual(M4_FIXTURE_V1.max_automatic_retries, 0)
        common = (True, True, True, True, True, True, True, True, True)
        cases = (
            ("succeeded", None, 0, ResourceObservations(tool_call_count=1), "2026-07-16T08:00:04Z"),
            ("failed", "command_failed", 1, ResourceObservations(tool_call_count=1), "2026-07-16T08:00:04Z"),
            ("cancelled", "cancelled_by_request", None, ResourceObservations(tool_call_count=1), "2026-07-16T08:00:04Z"),
            ("timed_out", "resource_limit_exceeded", None, ResourceObservations(tool_call_count=1, limits_reached=("command_timeout_ms",)), "2026-07-16T08:02:03Z"),
            ("failed", "resource_limit_exceeded", None, ResourceObservations(command_output_bytes=65536, tool_call_count=1, limits_reached=("max_command_output_bytes",)), "2026-07-16T08:00:04Z"),
        )
        for status, reason, exit_code, observations, finished_at in cases:
            with self.subTest(status=status, reason=reason):
                facts = OciRunFacts(*common, status, reason, exit_code, "2026-07-16T08:00:03Z", finished_at, observations)
                attempt = execute_governed_attempt(action, command, decision, FactsBackend(facts))
                self.assertEqual((attempt.status, attempt.failure_reason), (status, reason))
                self.assertEqual(attempt.contract_id, execution_attempt_id_for(attempt))
                self.assertEqual(attempt.attempt_id, attempt.contract_id.replace("ea_sha256:", "attempt_sha256:"))
                self.assertEqual(attempt.artifact_ref_ids, ())

    def test_raw_runtime_payload_is_rejected_as_a_safe_validation_envelope(self) -> None:
        action = build_action_intent(run_id=RUN_ID, task_input_contract_id=TASK_ID, created_at="2026-07-16T08:00:00Z")
        command = build_command_intent(action, created_at="2026-07-16T08:00:01Z")
        decision = evaluate_command_intent(command, evaluated_at="2026-07-16T08:00:02Z")[0]
        result = execute_governed_attempt(action, command, decision, RawPayloadBackend())
        self.assertEqual(result.error_code, "invalid_fact_combination")
        self.assertNotIn("secret", result.summary)


if __name__ == "__main__":
    unittest.main()
