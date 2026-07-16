"""Canonical identity tests for Feature 2 contracts."""

from __future__ import annotations

from dataclasses import replace
import unittest

from forgeflow.deterministic_patch_artifact_security.canonical import (
    canonical_bytes,
    intent_id_for,
    sha256_hex,
)
from forgeflow.deterministic_patch_artifact_security.models import PatchIntent


_DIGEST = "sha256:" + "0" * 64


class CanonicalTests(unittest.TestCase):
    def test_canonical_bytes_sort_mapping_keys_and_reject_float(self) -> None:
        self.assertEqual(canonical_bytes({"z": 1, "a": 2}), b'{"a":2,"z":1}')
        with self.assertRaises(TypeError):
            canonical_bytes({"value": 1.5})

    def test_intent_identity_omits_only_its_identity_field(self) -> None:
        provisional = PatchIntent(
            contract_version="m4-patch-artifact-security/v1",
            repository_identity="fixture-repository-1300511729",
            base_revision="97c8220cd713ebf61124ac2de2f3eadc6e4dc222",
            intent_id=_DIGEST,
            target_scope=("src/calculator.py",),
            change_description="Correct the addition result.",
            lineage_digest="sha256:" + "a" * 64,
        )

        identity = intent_id_for(provisional)
        self.assertEqual(identity, intent_id_for(replace(provisional, intent_id=identity)))
        self.assertEqual(len(sha256_hex(provisional)), 64)


if __name__ == "__main__":
    unittest.main()
