from __future__ import annotations

import inspect
from dataclasses import asdict
import json
from pathlib import Path
import sys
import unittest


sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from forgeflow.validation_review.fixture_source import (  # noqa: E402
    FixtureReviewFindings,
    FixtureValidationAttempt,
    load_review_fixture,
    load_validation_fixture,
)
import forgeflow.validation_review.fixture_source as fixture_source  # noqa: E402
import forgeflow.validation_review.policy as policy  # noqa: E402


class FixtureSourceTests(unittest.TestCase):
    def test_validation_fixtures_are_in_memory_completed_facts_only(self) -> None:
        passed = load_validation_fixture("passed-default")
        failed = load_validation_fixture("failed-default")

        self.assertIsInstance(passed, FixtureValidationAttempt)
        self.assertEqual(passed.outcome, "passed")
        self.assertEqual(passed.finding_codes, ())
        self.assertEqual(failed.outcome, "failed")
        self.assertEqual(failed.finding_codes, ("fixture_assertion_failed",))
        self.assertTrue(passed.attempt_id.startswith("m3a_sha256:"))
        self.assertFalse(hasattr(passed, "command"))
        self.assertFalse(hasattr(passed, "output"))

    def test_review_fixture_is_deterministic_and_contains_only_findings(self) -> None:
        fixture = load_review_fixture("blocking-default")

        self.assertIsInstance(fixture, FixtureReviewFindings)
        self.assertEqual(fixture.case_id, "blocking-default")
        self.assertEqual(fixture.findings[0].severity, "blocking")
        self.assertEqual(load_review_fixture("blocking-default"), fixture)
        self.assertFalse(hasattr(fixture, "decision"))
        self.assertFalse(hasattr(fixture, "command"))

    def test_unknown_fixture_cases_are_lookup_failures(self) -> None:
        with self.assertRaises(LookupError):
            load_validation_fixture("unknown")
        with self.assertRaises(LookupError):
            load_review_fixture("unknown")

    def test_policy_and_fixture_modules_do_not_expose_io_surfaces(self) -> None:
        source = inspect.getsource(policy) + inspect.getsource(fixture_source)
        for forbidden in ("subprocess", "socket", "urllib", "httpx", "open(", "Path("):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, source)

    def test_expected_attempt_fragments_lock_completed_fixture_facts(self) -> None:
        fixture_directory = (
            Path(__file__).resolve().parents[2]
            / "openspec/changes/validation-review-slice/fixtures/expected/phase-2-policy"
        )
        for case_id, filename in (
            ("passed-default", "passed-attempt.json"),
            ("failed-default", "failed-attempt.json"),
        ):
            with self.subTest(case_id=case_id):
                expected = json.loads((fixture_directory / filename).read_text())
                self.assertEqual(
                    json.loads(json.dumps(asdict(load_validation_fixture(case_id)))),
                    expected,
                )
