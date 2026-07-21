from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest


sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from forgeflow.governed_action_sandbox import (  # noqa: E402
    M4_FIXTURE_V1,
    build_action_intent,
    build_command_intent,
    evaluate_command_intent,
    validate_governed_lineage,
)


RUN_ID = "run_sha256:" + "1" * 64
TASK_ID = "ti_sha256:" + "2" * 64
ACTION_AT = "2026-07-15T09:00:00Z"
COMMAND_AT = "2026-07-15T09:00:01Z"
EVALUATED_AT = "2026-07-15T09:00:02Z"
EXPECTED = (
    Path(__file__).resolve().parents[2]
    / "openspec"
    / "changes"
    / "governed-action-sandbox"
    / "fixtures"
    / "expected"
    / "phase-2-policy"
)


class GovernedActionSandboxPolicyTests(unittest.TestCase):
    def test_builders_pin_the_registered_fixture_lineage(self) -> None:
        action = build_action_intent(
            run_id=RUN_ID, task_input_contract_id=TASK_ID, created_at=ACTION_AT
        )
        command = build_command_intent(action, created_at=COMMAND_AT)

        self.assertEqual(command.action_intent_contract_id, action.contract_id)
        self.assertEqual(command.executable, "python3")
        self.assertEqual(command.args, ("-m", "unittest", "discover", "-s", "tests"))
        self.assertEqual(command.oci_image_digest, M4_FIXTURE_V1.oci_image_digest)

    def test_exact_current_command_is_allowed_with_fresh_pdr(self) -> None:
        action = build_action_intent(run_id=RUN_ID, task_input_contract_id=TASK_ID, created_at=ACTION_AT)
        command = build_command_intent(action, created_at=COMMAND_AT)
        record, terminal = evaluate_command_intent(command, evaluated_at=EVALUATED_AT)

        self.assertEqual(record.outcome, "allowed")
        self.assertEqual(record.subject_contract_id, command.contract_id)
        self.assertIsNone(terminal)
        validate_governed_lineage(action, command, record)

    def test_command_mismatch_is_blocked_without_execution_facts(self) -> None:
        action = build_action_intent(run_id=RUN_ID, task_input_contract_id=TASK_ID, created_at=ACTION_AT)
        command = build_command_intent(action, created_at=COMMAND_AT)
        record, terminal = evaluate_command_intent(
            command, evaluated_at=EVALUATED_AT, command_args=("-m", "unittest", "discover", "-s", "tests", "-v")
        )

        self.assertEqual(record.outcome, "blocked")
        self.assertEqual(terminal.status, "not_started")
        self.assertEqual(terminal.failure_reason, "policy_blocked")

    def test_explicit_null_command_args_is_blocked_with_a_fresh_pdr(self) -> None:
        action = build_action_intent(run_id=RUN_ID, task_input_contract_id=TASK_ID, created_at=ACTION_AT)
        command = build_command_intent(action, created_at=COMMAND_AT)
        allowed, _ = evaluate_command_intent(command, evaluated_at=EVALUATED_AT)
        record, terminal = evaluate_command_intent(
            command, evaluated_at=EVALUATED_AT, command_args=None
        )

        self.assertEqual(record.outcome, "blocked")
        self.assertEqual(terminal.status, "not_started")
        self.assertNotEqual(record.input_lineage_digest, allowed.input_lineage_digest)

    def test_stale_base_requires_human_approval_with_distinct_terminal_fact(self) -> None:
        action = build_action_intent(run_id=RUN_ID, task_input_contract_id=TASK_ID, created_at=ACTION_AT)
        command = build_command_intent(action, created_at=COMMAND_AT)
        record, terminal = evaluate_command_intent(
            command, evaluated_at=EVALUATED_AT, current_base_commit_sha="0" * 40
        )

        self.assertEqual(record.outcome, "requires_human_approval")
        self.assertEqual(terminal.status, "not_started")
        self.assertEqual(terminal.failure_reason, "base_revision_mismatch")

    def test_stale_base_from_capability_mapping_requires_human_approval(self) -> None:
        action = build_action_intent(run_id=RUN_ID, task_input_contract_id=TASK_ID, created_at=ACTION_AT)
        command = build_command_intent(action, created_at=COMMAND_AT)
        record, terminal = evaluate_command_intent(
            command,
            evaluated_at=EVALUATED_AT,
            current_capability={"base_commit_sha": "0" * 40},
        )

        self.assertEqual(record.outcome, "requires_human_approval")
        self.assertEqual(terminal.status, "not_started")
        self.assertEqual(terminal.failure_reason, "base_revision_mismatch")

    def test_explicit_policy_escalation_requires_approval_without_start(self) -> None:
        action = build_action_intent(run_id=RUN_ID, task_input_contract_id=TASK_ID, created_at=ACTION_AT)
        command = build_command_intent(action, created_at=COMMAND_AT)
        record, terminal = evaluate_command_intent(
            command, evaluated_at=EVALUATED_AT, requires_human_approval=True
        )

        self.assertEqual(record.outcome, "requires_human_approval")
        self.assertEqual(terminal.status, "not_started")
        self.assertEqual(terminal.failure_reason, "approval_required")

    def test_all_capability_variations_are_blocked_and_get_fresh_pdrs(self) -> None:
        action = build_action_intent(run_id=RUN_ID, task_input_contract_id=TASK_ID, created_at=ACTION_AT)
        command = build_command_intent(action, created_at=COMMAND_AT)
        executable_record, executable_terminal = evaluate_command_intent(
            command, evaluated_at=EVALUATED_AT, current_capability={"executable": "sh"}
        )
        directory_record, directory_terminal = evaluate_command_intent(
            command, evaluated_at=EVALUATED_AT, current_capability={"working_directory": "other"}
        )

        self.assertEqual(executable_record.outcome, "blocked")
        self.assertEqual(directory_record.outcome, "blocked")
        self.assertEqual(executable_terminal.status, "not_started")
        self.assertEqual(directory_terminal.status, "not_started")
        self.assertNotEqual(executable_record.contract_id, directory_record.contract_id)

    def test_unknown_capability_values_are_blocked_and_bound_to_fresh_pdrs(self) -> None:
        action = build_action_intent(run_id=RUN_ID, task_input_contract_id=TASK_ID, created_at=ACTION_AT)
        command = build_command_intent(action, created_at=COMMAND_AT)
        first, first_terminal = evaluate_command_intent(
            command, evaluated_at=EVALUATED_AT, current_capability={"unsupported_switch": "one"}
        )
        second, second_terminal = evaluate_command_intent(
            command, evaluated_at=EVALUATED_AT, current_capability={"unsupported_switch": "two"}
        )

        self.assertEqual(first.outcome, "blocked")
        self.assertEqual(second.outcome, "blocked")
        self.assertEqual(first_terminal.failure_reason, "policy_blocked")
        self.assertEqual(second_terminal.failure_reason, "policy_blocked")
        self.assertNotEqual(first.contract_id, second.contract_id)

    def test_nested_null_capability_values_do_not_collide_in_pdr_lineage(self) -> None:
        action = build_action_intent(run_id=RUN_ID, task_input_contract_id=TASK_ID, created_at=ACTION_AT)
        command = build_command_intent(action, created_at=COMMAND_AT)
        empty, _ = evaluate_command_intent(
            command, evaluated_at=EVALUATED_AT, current_capability={"unsupported_switch": {}}
        )
        nested_null, _ = evaluate_command_intent(
            command,
            evaluated_at=EVALUATED_AT,
            current_capability={"unsupported_switch": {"a": None}},
        )

        self.assertEqual(empty.outcome, "blocked")
        self.assertEqual(nested_null.outcome, "blocked")
        self.assertNotEqual(empty.input_lineage_digest, nested_null.input_lineage_digest)

    def test_null_current_values_are_bound_without_digest_omission(self) -> None:
        action = build_action_intent(run_id=RUN_ID, task_input_contract_id=TASK_ID, created_at=ACTION_AT)
        command = build_command_intent(action, created_at=COMMAND_AT)
        executable, _ = evaluate_command_intent(
            command, evaluated_at=EVALUATED_AT, current_capability={"executable": None}
        )
        directory, _ = evaluate_command_intent(
            command, evaluated_at=EVALUATED_AT, current_capability={"working_directory": None}
        )
        args, _ = evaluate_command_intent(
            command, evaluated_at=EVALUATED_AT, current_capability={"args": None}
        )
        unknown, _ = evaluate_command_intent(
            command, evaluated_at=EVALUATED_AT, current_capability={"unsupported_switch": None}
        )
        allowed, _ = evaluate_command_intent(command, evaluated_at=EVALUATED_AT)

        self.assertEqual(executable.outcome, "blocked")
        self.assertEqual(directory.outcome, "blocked")
        self.assertEqual(args.outcome, "blocked")
        self.assertEqual(unknown.outcome, "blocked")
        self.assertNotEqual(args.input_lineage_digest, allowed.input_lineage_digest)
        self.assertEqual(
            len({executable.contract_id, directory.contract_id, args.contract_id, unknown.contract_id}), 4
        )

    def test_expected_fragments_lock_all_policy_terminal_outcomes(self) -> None:
        action = build_action_intent(run_id=RUN_ID, task_input_contract_id=TASK_ID, created_at=ACTION_AT)
        command = build_command_intent(action, created_at=COMMAND_AT)
        cases = {
            "allowed.json": evaluate_command_intent(command, evaluated_at=EVALUATED_AT),
            "blocked.json": evaluate_command_intent(
                command, evaluated_at=EVALUATED_AT, command_args=("-m", "unittest", "-v")
            ),
            "approval-required.json": evaluate_command_intent(
                command, evaluated_at=EVALUATED_AT, requires_human_approval=True
            ),
            "stale-revision.json": evaluate_command_intent(
                command, evaluated_at=EVALUATED_AT, current_base_commit_sha="0" * 40
            ),
        }

        for filename, (record, terminal) in cases.items():
            expected = json.loads((EXPECTED / filename).read_text(encoding="utf-8"))
            actual = {"outcome": record.outcome}
            if terminal is None:
                actual["terminal"] = None
            else:
                actual |= {"status": terminal.status, "failure_reason": terminal.failure_reason}
            self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
