from __future__ import annotations

from dataclasses import fields
from pathlib import Path
import sys
import unittest


sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from forgeflow.patch_proposal import (  # noqa: E402
    FixtureDraftNotFoundError,
    FixtureProposalDraft,
    load_fixture_draft,
)


class FixtureSourceTests(unittest.TestCase):
    def test_valid_default_is_deterministic_transient_intent_only(self) -> None:
        first = load_fixture_draft("valid-default")
        second = load_fixture_draft("valid-default")

        self.assertEqual(first, second)
        self.assertIsInstance(first, FixtureProposalDraft)
        self.assertEqual(
            {field.name for field in fields(first)},
            {"root_cause_hypotheses", "fix_strategy_summary", "candidate_changes"},
        )
        self.assertFalse(
            {
                "raw_payload",
                "source_content",
                "prompt",
                "policy_decision",
                "policy_profile_id",
                "limitation_codes",
                "diff",
                "command",
            }
            & {field.name for field in fields(first)}
        )

    def test_unknown_case_is_a_lookup_failure(self) -> None:
        with self.assertRaises(FixtureDraftNotFoundError):
            load_fixture_draft("unknown-case")


if __name__ == "__main__":
    unittest.main()
