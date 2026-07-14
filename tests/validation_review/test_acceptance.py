from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from forgeflow.validation_review import (  # noqa: E402
    ValidationResult,
    ValidationReviewError,
    ValidationTerminal,
    build_review_result,
    build_validation_envelope,
)
from tests.validation_review.test_service import proposal  # noqa: E402


class ValidationReviewAcceptanceTests(unittest.TestCase):
    _expected_dir = (
        Path(__file__).resolve().parents[2]
        / "openspec/changes/validation-review-slice/fixtures/expected/phase-4-acceptance"
    )

    def assert_expected_fragment(self, name: str, value: object) -> None:
        expected = json.loads((self._expected_dir / name).read_text())
        self.assertEqual(json.loads(json.dumps(asdict(value))), expected)

    def test_public_service_is_deterministic_and_preserves_terminal_boundaries(self) -> None:
        value = proposal()
        first = build_validation_envelope(value, "allowed-default", "failed-default")
        second = build_validation_envelope(value, "allowed-default", "failed-default")
        self.assertIsInstance(first, ValidationResult)
        self.assertEqual(first, second)
        self.assert_expected_fragment("validation-fragment.json", first)
        passed = build_validation_envelope(value, "allowed-default", "passed-default")
        self.assertIsInstance(passed, ValidationResult)
        self.assertEqual(passed.outcome, "passed")
        self.assertEqual(first.patch_proposal_contract_id, value.contract_id)
        blocked = build_validation_envelope(value, "blocked-default", "passed-default")
        approval = build_validation_envelope(value, "requires-human-approval-default", "passed-default")
        self.assertIsInstance(blocked, ValidationTerminal)
        self.assertIsInstance(approval, ValidationTerminal)
        self.assertFalse(hasattr(blocked, "attempt_id"))
        self.assertEqual(approval.terminal_reason, "human_approval_required")
        self.assert_expected_fragment("terminal-fragment.json", blocked)
        review = build_review_result(value, first, "blocked-default", "blocking-default")
        self.assertEqual(review.findings[0].severity, "blocking")
        self.assertEqual(review.policy_decision_refs[0].decision, "blocked")
        self.assertEqual(review.validation_result_contract_id, first.contract_id)
        self.assert_expected_fragment("review-fragment.json", review)
        for envelope in (first, passed, blocked, approval, review):
            for forbidden_field in ("command", "output", "retry", "next_attempt"):
                self.assertFalse(hasattr(envelope, forbidden_field))

    def test_public_service_rejects_payload_without_execution_surface(self) -> None:
        error = build_validation_envelope(proposal(), "allowed-default", {"raw_output": "secret"})
        self.assertEqual(error.error_code, "forbidden_payload")
        self.assertNotIn("secret", error.message)
        self.assert_expected_fragment("error-fragment.json", error)

    def test_public_service_keeps_malformed_and_terminal_review_flows_separate(self) -> None:
        value = proposal()
        malformed = build_validation_envelope(value, "allowed-default", "unknown-case")
        self.assertIsInstance(malformed, ValidationReviewError)
        self.assertEqual(malformed.error_code, "invalid_fixture_case")
        self.assertFalse(hasattr(malformed, "attempt_id"))
        terminal = build_validation_envelope(value, "blocked-default", "passed-default")
        terminal_review = build_review_result(value, terminal, "blocked-default", "blocking-default")
        self.assertIsInstance(terminal_review, ValidationReviewError)
        self.assertEqual(terminal_review.error_code, "invalid_review_input")
