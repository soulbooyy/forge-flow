from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path
import sys
import unittest


sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from forgeflow.validation_review import (  # noqa: E402
    M3_FIXTURE_V1,
    policy_decision_id_for,
)
from forgeflow.validation_review.policy import policy_record_for  # noqa: E402


PATCH_PROPOSAL_ID = "pp_sha256:" + "1" * 64


class DeterministicPolicyFixtureTests(unittest.TestCase):
    def test_policy_cases_have_exact_outcomes_risk_flags_and_computed_ids(self) -> None:
        expected = {
            "allowed-default": ("allowed", ()),
            "blocked-default": ("blocked", ("blocked_by_policy",)),
            "requires-human-approval-default": (
                "requires_human_approval",
                ("human_approval_required",),
            ),
        }

        for case_id, (decision, risk_flags) in expected.items():
            with self.subTest(case_id=case_id):
                record = policy_record_for(PATCH_PROPOSAL_ID, case_id)
                self.assertEqual(record.decision, decision)
                self.assertEqual(record.risk_flags, risk_flags)
                self.assertEqual(record.subject_contract_id, PATCH_PROPOSAL_ID)
                self.assertEqual(record.policy_profile_id, M3_FIXTURE_V1.policy_profile_id)
                self.assertEqual(record.decision_id, policy_decision_id_for(record))

    def test_policy_fixture_is_deterministic_and_rejects_unknown_case(self) -> None:
        self.assertEqual(
            policy_record_for(PATCH_PROPOSAL_ID, "blocked-default"),
            policy_record_for(PATCH_PROPOSAL_ID, "blocked-default"),
        )
        with self.assertRaises(LookupError):
            policy_record_for(PATCH_PROPOSAL_ID, "unknown")

    def test_profile_retains_forbidden_payload_field_names(self) -> None:
        self.assertEqual(
            M3_FIXTURE_V1.forbidden_payload_field_names,
            (
                "command",
                "exit_code",
                "stdout",
                "stderr",
                "output",
                "raw_output",
                "report_payload",
                "environment",
                "source",
                "prompt",
            ),
        )

    def test_expected_policy_fragments_lock_all_three_outcomes(self) -> None:
        fixture_directory = (
            Path(__file__).resolve().parents[2]
            / "openspec/changes/validation-review-slice/fixtures/expected/phase-2-policy"
        )
        for case_id, filename in (
            ("allowed-default", "allowed.json"),
            ("blocked-default", "blocked.json"),
            ("requires-human-approval-default", "requires-human-approval.json"),
        ):
            with self.subTest(case_id=case_id):
                expected = json.loads((fixture_directory / filename).read_text())
                self.assertEqual(
                    json.loads(json.dumps(asdict(policy_record_for(PATCH_PROPOSAL_ID, case_id)))),
                    expected,
                )
