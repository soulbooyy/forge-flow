from __future__ import annotations

import re
from dataclasses import fields
import json
from pathlib import Path
import sys
import unittest


sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from forgeflow.governed_action_sandbox import canonical_bytes, sha256_hex  # noqa: E402
from forgeflow.governed_action_sandbox.canonical import (  # noqa: E402
    action_intent_id_for,
    command_intent_id_for,
    execution_attempt_id_for,
    policy_decision_id_for,
)
from tests.governed_action_sandbox.test_contracts import action, attempt, command, decision, sha  # noqa: E402


ROOT = Path(__file__).resolve().parents[2]
EXPECTED = ROOT / "openspec" / "changes" / "governed-action-sandbox" / "fixtures" / "expected" / "phase-1-contract"


class GovernedActionSandboxCanonicalTests(unittest.TestCase):
    def test_canonical_json_is_compact_sorted_utf8_and_rejects_floats(self) -> None:
        self.assertEqual(canonical_bytes({"z": "café", "a": "汉字"}), b'{"a":"\xe6\xb1\x89\xe5\xad\x97","z":"caf\xc3\xa9"}')
        with self.assertRaises(TypeError):
            canonical_bytes({"value": 1.5})

    def test_identity_excludes_contract_ids_and_audit_timestamps(self) -> None:
        first = action()
        same = type(first)(**{field.name: getattr(first, field.name) for field in fields(first)} | {"created_at": "2026-07-15T09:00:00Z"})
        self.assertEqual(action_intent_id_for(first), action_intent_id_for(same))
        self.assertRegex(action_intent_id_for(first), r"^ai_sha256:[0-9a-f]{64}$")
        self.assertEqual(command_intent_id_for(command()), command_intent_id_for(command()))

    def test_pdr_identity_excludes_both_identity_fields_and_requires_equality(self) -> None:
        record = decision()
        self.assertEqual(policy_decision_id_for(record), record.contract_id)
        self.assertEqual(policy_decision_id_for(record), record.decision_id)
        with self.assertRaises(ValueError):
            type(record)(**{field.name: getattr(record, field.name) for field in fields(record)} | {"decision_id": sha("pdr_sha256", "d")})

    def test_execution_attempt_identity_has_required_prefix(self) -> None:
        result = attempt()
        self.assertTrue(re.fullmatch(r"ea_sha256:[0-9a-f]{64}", execution_attempt_id_for(result)))

    def test_safe_computed_fixture_fragments_lock_registered_contract_identity(self) -> None:
        fixture = json.loads((EXPECTED / "canonical-identities.json").read_text(encoding="utf-8"))
        self.assertEqual(fixture["action_intent_id"], action_intent_id_for(action()))
        self.assertEqual(fixture["command_intent_id"], command_intent_id_for(command()))
        self.assertEqual(fixture["policy_decision_id"], policy_decision_id_for(decision()))
