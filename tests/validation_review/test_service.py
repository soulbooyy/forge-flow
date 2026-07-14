from __future__ import annotations

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from forgeflow.patch_proposal import CandidateChange, FixStrategy, PatchProposal, PolicyDecisionRef, RootCauseHypothesis, TaskInput  # noqa: E402
from forgeflow.validation_review import ValidationResult, ValidationReviewError, ValidationTerminal  # noqa: E402
from forgeflow.validation_review.service import build_review_result, build_validation_envelope  # noqa: E402


EVIDENCE_ID = "ev_sha256:" + "a" * 64


def proposal() -> PatchProposal:
    return PatchProposal(
        contract_id="pp_sha256:" + "1" * 64,
        proposal_source_id="m2/deterministic-fixture-v1",
        repository_context_contract_id="rcr_sha256:" + "2" * 64,
        task_input=TaskInput(task_ref="M3-001", summary="Validate deterministic fixture lineage"),
        root_cause_hypotheses=(RootCauseHypothesis("Fixture supports this contract.", "low", (EVIDENCE_ID,)),),
        fix_strategy=FixStrategy("Preserve fixture-only boundaries.", ("evidence_backed", "minimal_change", "no_execution", "policy_bounded")),
        candidate_changes=(CandidateChange("src/example.py", "modify_existing_file", "Use fixture evidence.", (EVIDENCE_ID,)),),
        policy_decision=PolicyDecisionRef("pdr_sha256:" + "3" * 64, "allowed", "patch-proposal/m2-conservative-v1", 1, "m2/deterministic-boundary-evaluator-v1", "sha256:" + "4" * 64),
        risk_flags=(),
        limitation_codes=("fixture_only_source", "no_diff_generated", "no_source_payload", "no_validation_executed"),
    )


class ValidationReviewServiceTests(unittest.TestCase):
    def test_policy_outcomes_produce_result_or_terminal_without_execution_claims(self) -> None:
        value = proposal()
        passed = build_validation_envelope(value, "allowed-default", "passed-default")
        blocked = build_validation_envelope(value, "blocked-default", "passed-default")
        approval = build_validation_envelope(value, "requires-human-approval-default", "passed-default")
        self.assertIsInstance(passed, ValidationResult)
        self.assertEqual(passed.outcome, "passed")
        self.assertIsInstance(blocked, ValidationTerminal)
        self.assertEqual(blocked.terminal_reason, "policy_blocked")
        self.assertFalse(hasattr(blocked, "attempt_id"))
        self.assertIsInstance(approval, ValidationTerminal)
        self.assertEqual(approval.terminal_reason, "human_approval_required")

    def test_review_rejects_terminal_and_preserves_policy_lineage(self) -> None:
        value = proposal()
        result = build_validation_envelope(value, "allowed-default", "failed-default")
        assert isinstance(result, ValidationResult)
        review = build_review_result(value, result, "blocked-default", "blocking-default")
        self.assertNotIsInstance(review, ValidationReviewError)
        self.assertEqual(review.policy_decision_refs[0].decision, "blocked")
        terminal = build_validation_envelope(value, "blocked-default", "passed-default")
        error = build_review_result(value, terminal, "blocked-default", "blocking-default")
        self.assertIsInstance(error, ValidationReviewError)
        self.assertEqual(error.error_code, "invalid_review_input")

    def test_unknown_cases_and_non_proposal_input_return_safe_errors(self) -> None:
        self.assertEqual(build_validation_envelope(object(), "allowed-default", "passed-default").error_code, "unsupported_patch_proposal")
        self.assertEqual(build_validation_envelope(proposal(), "unknown", "passed-default").error_code, "invalid_policy_reference")
        self.assertEqual(build_validation_envelope(proposal(), "allowed-default", "unknown").error_code, "invalid_fixture_case")

    def test_forbidden_fixture_payload_fields_return_safe_error_without_echo(self) -> None:
        value = proposal()
        validation_error = build_validation_envelope(value, "allowed-default", {"raw_output": "secret"})
        valid_result = build_validation_envelope(value, "allowed-default", "passed-default")
        assert isinstance(valid_result, ValidationResult)
        review_error = build_review_result(value, valid_result, "allowed-default", {"command": "secret"})
        self.assertEqual(validation_error.error_code, "forbidden_payload")
        self.assertEqual(review_error.error_code, "forbidden_payload")
        self.assertNotIn("secret", validation_error.message)
        self.assertNotIn("secret", review_error.message)
