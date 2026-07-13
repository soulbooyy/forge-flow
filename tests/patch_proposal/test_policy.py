from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch


sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from forgeflow.patch_proposal import (  # noqa: E402
    CandidateChange,
    M2_CONSERVATIVE_V1,
    assess_boundary,
    canonical_bytes,
)
from forgeflow.patch_proposal.policy import PolicyBlockedError  # noqa: E402


ROOT = Path(__file__).resolve().parents[2]
EXPECTED = (
    ROOT
    / "openspec"
    / "changes"
    / "structured-patch-proposal"
    / "fixtures"
    / "expected"
    / "phase-2-policy"
)
EVIDENCE_ID = "ev_sha256:" + "1" * 64


def candidate(
    path: str,
    *,
    change_kind: str = "modify_existing_file",
    rationale: str = "Apply the smallest evidence-backed change.",
) -> CandidateChange:
    return CandidateChange(
        path=path,
        change_kind=change_kind,  # type: ignore[arg-type]
        rationale=rationale,
        supporting_evidence_ref_ids=(EVIDENCE_ID,),
    )


class PatchBoundaryAssessmentTests(unittest.TestCase):
    def test_allowed_result_pins_profile_identity_and_has_no_risk_flags(self) -> None:
        decision = assess_boundary((candidate("src/payment_handler.py"),), M2_CONSERVATIVE_V1)

        self.assertEqual(decision.decision, "allowed")
        self.assertEqual(decision.policy_profile_id, "patch-proposal/m2-conservative-v1")
        self.assertEqual(decision.policy_version, 1)
        self.assertEqual(decision.evaluator_id, "m2/deterministic-boundary-evaluator-v1")
        self.assertEqual(decision.risk_flags, ())
        self.assertTrue(decision.revalidation_required)
        self.assertRegex(decision.decision_id, r"^pdr_sha256:[0-9a-f]{64}$")

    def test_blocked_path_returns_no_successful_policy_reference(self) -> None:
        with self.assertRaises(PolicyBlockedError) as raised:
            assess_boundary((candidate("secrets/runtime-config.json"),), M2_CONSERVATIVE_V1)

        error = raised.exception
        self.assertEqual(error.error_code, "policy_blocked")
        self.assertEqual(error.policy_profile_id, M2_CONSERVATIVE_V1.policy_profile_id)
        self.assertEqual(error.policy_version, M2_CONSERVATIVE_V1.policy_version)
        self.assertEqual(error.evaluator_id, M2_CONSERVATIVE_V1.evaluator_id)
        self.assertRegex(error.evaluated_candidate_digest, r"^sha256:[0-9a-f]{64}$")
        self.assertNotIn("secrets", error.args[0])

    def test_blocked_rules_take_precedence_over_approval_rules(self) -> None:
        with self.assertRaises(PolicyBlockedError):
            assess_boundary(
                (candidate("infra/credentials/id_rsa", change_kind="remove_file"),),
                M2_CONSERVATIVE_V1,
            )

    def test_environment_and_deletion_require_human_approval_with_sorted_flags(self) -> None:
        decision = assess_boundary(
            (candidate("config/.env.production", change_kind="remove_file"),),
            M2_CONSERVATIVE_V1,
        )

        self.assertEqual(decision.decision, "requires_human_approval")
        self.assertEqual(
            decision.risk_flags,
            (
                "deletion_intent",
                "environment_path",
                "policy_requires_human_approval",
            ),
        )

    def test_deletion_escalation_uses_the_profile_rule(self) -> None:
        profile_without_deletion_escalation = replace(
            M2_CONSERVATIVE_V1,
            approval_required_for_remove_file=False,
        )

        with patch(
            "forgeflow.patch_proposal.policy.M2_CONSERVATIVE_V1",
            profile_without_deletion_escalation,
        ):
            decision = assess_boundary(
                (candidate("src/obsolete.py", change_kind="remove_file"),),
                profile_without_deletion_escalation,
            )

        self.assertEqual(decision.decision, "allowed")
        self.assertEqual(decision.risk_flags, ())

    def test_auth_matching_is_case_insensitive_and_segment_exact(self) -> None:
        approval = assess_boundary((candidate("src/Auth/token.py"),), M2_CONSERVATIVE_V1)
        allowed = assess_boundary((candidate("src/authorizer.py"),), M2_CONSERVATIVE_V1)

        self.assertEqual(approval.decision, "requires_human_approval")
        self.assertEqual(
            approval.risk_flags,
            ("high_risk_path", "policy_requires_human_approval"),
        )
        self.assertEqual(allowed.decision, "allowed")

    def test_all_profile_approval_categories_escalate(self) -> None:
        paths = (
            ".github/workflows/check.yml",
            "infra/main.tf",
            "database/migrations/001_init.sql",
            "package-lock.json",
        )

        for path in paths:
            with self.subTest(path=path):
                decision = assess_boundary((candidate(path),), M2_CONSERVATIVE_V1)
                self.assertEqual(decision.decision, "requires_human_approval")
                self.assertEqual(
                    decision.risk_flags,
                    ("high_risk_path", "policy_requires_human_approval"),
                )

    def test_rejects_missing_or_changed_profile_and_candidate_bounds(self) -> None:
        with self.assertRaises(ValueError):
            assess_boundary((), M2_CONSERVATIVE_V1)
        with self.assertRaises(ValueError):
            assess_boundary(
                tuple(candidate(f"src/file_{number}.py") for number in range(4)),
                M2_CONSERVATIVE_V1,
            )
        with self.assertRaises(ValueError):
            assess_boundary(
                (candidate("src/payment_handler.py"),),
                replace(M2_CONSERVATIVE_V1, policy_version=2),
            )

    def test_policy_identity_changes_when_candidate_intent_changes(self) -> None:
        first = assess_boundary((candidate("src/payment_handler.py"),), M2_CONSERVATIVE_V1)
        changed = assess_boundary(
            (
                candidate(
                    "src/payment_handler.py",
                    rationale="Apply a different bounded evidence-backed change.",
                ),
            ),
            M2_CONSERVATIVE_V1,
        )

        self.assertRegex(first.evaluated_candidate_digest, r"^sha256:[0-9a-f]{64}$")
        self.assertNotEqual(first.evaluated_candidate_digest, changed.evaluated_candidate_digest)
        self.assertNotEqual(first.decision_id, changed.decision_id)

    def test_expected_policy_fragments_lock_allowed_blocked_and_approval_outcomes(self) -> None:
        allowed = assess_boundary((candidate("src/payment_handler.py"),), M2_CONSERVATIVE_V1)
        approval = assess_boundary((candidate("config/.env.production"),), M2_CONSERVATIVE_V1)
        with self.assertRaises(PolicyBlockedError) as raised:
            assess_boundary((candidate("secrets/runtime-config.json"),), M2_CONSERVATIVE_V1)

        self.assertEqual(
            json.loads(canonical_bytes(allowed)),
            json.loads((EXPECTED / "allowed.json").read_text(encoding="utf-8")),
        )
        self.assertEqual(
            json.loads(canonical_bytes(approval)),
            json.loads((EXPECTED / "requires-human-approval.json").read_text(encoding="utf-8")),
        )
        self.assertEqual(
            {
                "error_code": raised.exception.error_code,
                "policy_profile_id": raised.exception.policy_profile_id,
                "policy_version": raised.exception.policy_version,
                "evaluator_id": raised.exception.evaluator_id,
                "evaluated_candidate_digest": raised.exception.evaluated_candidate_digest,
            },
            json.loads((EXPECTED / "blocked.json").read_text(encoding="utf-8")),
        )


if __name__ == "__main__":
    unittest.main()
