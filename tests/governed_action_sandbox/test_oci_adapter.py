from __future__ import annotations

from pathlib import Path
import sys
import unittest


sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from forgeflow.governed_changes.action_execution import (  # noqa: E402
    M4_FIXTURE_V1,
    OciCapabilityProof,
    OciRunFacts,
    build_action_intent,
    build_command_intent,
    evaluate_command_intent,
    execute_governed_attempt,
)
from forgeflow.governed_changes.action_execution.models import ResourceObservations  # noqa: E402


RUN_ID = "run_sha256:" + "3" * 64
TASK_ID = "ti_sha256:" + "4" * 64
ACTION_AT = "2026-07-15T10:00:00Z"
COMMAND_AT = "2026-07-15T10:00:01Z"
EVALUATED_AT = "2026-07-15T10:00:02Z"


class ControlledBackend:
    def __init__(self, facts: OciRunFacts, proof: OciCapabilityProof | None = None) -> None:
        self.facts = facts
        self.proof = proof or capability_proof()
        self.proof_calls = 0
        self.command_launches = 0
        self.command_seen = None

    def prove(self, command):  # type: ignore[no-untyped-def]
        self.proof_calls += 1
        return self.proof

    def run(self, command):  # type: ignore[no-untyped-def]
        self.command_seen = command
        if self.facts.started:
            self.command_launches += 1
        return self.facts


def action_and_command():  # type: ignore[no-untyped-def]
    action = build_action_intent(run_id=RUN_ID, task_input_contract_id=TASK_ID, created_at=ACTION_AT)
    return action, build_command_intent(action, created_at=COMMAND_AT)


def allowed_pdr(command):  # type: ignore[no-untyped-def]
    return evaluate_command_intent(command, evaluated_at=EVALUATED_AT)[0]


def capability_proof(**changes: object) -> OciCapabilityProof:
    values = {"image_digest_proven": True, "network_disabled": True, "credentials_absent": True, "dynamic_installation_disabled": True, "fixed_revision_workspace": True, "workspace_writes_confined": True, "artifact_store_unmounted": True}
    values.update(changes)
    return OciCapabilityProof(**values)


def facts(**changes: object) -> OciRunFacts:
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
        "started_at": "2026-07-15T10:00:03Z",
        "finished_at": "2026-07-15T10:00:04Z",
        "resource_observations": ResourceObservations(tool_call_count=1),
    }
    values.update(changes)
    return OciRunFacts(**values)


class OciAdapterTests(unittest.TestCase):
    def test_unproven_network_fails_closed_before_command_launch(self) -> None:
        action, command = action_and_command()
        backend = ControlledBackend(facts(), capability_proof(network_disabled=False))

        attempt = execute_governed_attempt(action, command, allowed_pdr(command), backend)

        self.assertEqual((attempt.status, attempt.failure_reason), ("not_started", "sandbox_unavailable"))
        self.assertEqual(backend.command_launches, 0)
        self.assertEqual(attempt.resource_observations, ResourceObservations())

    def test_every_required_oci_proof_fails_closed_before_command_launch(self) -> None:
        action, command = action_and_command()
        for proof in (
            "image_digest_proven", "credentials_absent", "dynamic_installation_disabled",
            "fixed_revision_workspace", "workspace_writes_confined",
            "artifact_store_unmounted",
        ):
            with self.subTest(proof=proof):
                backend = ControlledBackend(facts(), capability_proof(**{proof: False}))
                attempt = execute_governed_attempt(action, command, allowed_pdr(command), backend)
                self.assertEqual((attempt.status, attempt.failure_reason), ("not_started", "sandbox_unavailable"))
                self.assertEqual(backend.command_launches, 0)

    def test_exact_command_is_passed_as_structured_capability_without_shell(self) -> None:
        action, command = action_and_command()
        backend = ControlledBackend(facts())

        attempt = execute_governed_attempt(action, command, allowed_pdr(command), backend)

        self.assertEqual(attempt.status, "succeeded")
        self.assertIs(backend.command_seen, command)
        self.assertEqual(backend.command_seen.executable, M4_FIXTURE_V1.executable)
        self.assertEqual(backend.command_seen.args, M4_FIXTURE_V1.args)

    def test_truthy_non_boolean_proof_is_rejected_before_run(self) -> None:
        with self.assertRaises(ValueError):
            capability_proof(network_disabled=1)


if __name__ == "__main__":
    unittest.main()
