from __future__ import annotations

import unittest

from forgeflow.controlled_materialization_payload_simulation.models import TransformationManifest
from forgeflow.controlled_materialization_payload_simulation.policy import issue_materialization_pdr
from forgeflow.controlled_materialization_payload_simulation.registry import (
    REGISTERED_SNAPSHOT,
    revalidate_snapshot,
    resolve_target_file,
    resolve_transformer,
)


class RegistryServiceTest(unittest.TestCase):
    def manifest(self) -> TransformationManifest:
        return TransformationManifest(
            "fixture-transform-v1", "1", "fixture-test-file-v1", REGISTERED_SNAPSHOT.target_digest
        )

    def test_only_registered_snapshot_target_and_transformer_are_resolved(self) -> None:
        self.assertEqual(resolve_target_file("fixture-test-file-v1"), "tests/fixture_test.py")
        transformer = resolve_transformer(self.manifest())
        self.assertEqual(transformer(REGISTERED_SNAPSHOT.target_bytes), b"assert True\n")
        with self.assertRaises(ValueError):
            resolve_target_file("../../etc/passwd")
        with self.assertRaises(ValueError):
            resolve_transformer(TransformationManifest("other-transform", "1", "fixture-test-file-v1", REGISTERED_SNAPSHOT.target_digest))

    def test_snapshot_mismatch_and_caller_source_selector_fail_closed(self) -> None:
        result = revalidate_snapshot(REGISTERED_SNAPSHOT, {"tests/fixture_test.py": b"wrong"})
        self.assertEqual(result.terminal.reason, "source_revalidation_failed")
        self.assertIsNone(result.snapshot)
        verified = revalidate_snapshot(REGISTERED_SNAPSHOT, {"tests/fixture_test.py": REGISTERED_SNAPSHOT.target_bytes})
        self.assertIs(verified.snapshot.snapshot, REGISTERED_SNAPSHOT)

    def test_issuance_requires_revalidated_registered_snapshot_and_is_fresh(self) -> None:
        verified = revalidate_snapshot(REGISTERED_SNAPSHOT, {"tests/fixture_test.py": REGISTERED_SNAPSHOT.target_bytes}).snapshot
        self.assertIsNotNone(verified)
        first = issue_materialization_pdr(self.manifest(), verified, now=100)
        second = issue_materialization_pdr(self.manifest(), verified, now=100)
        self.assertNotEqual(first.attempt_id, second.attempt_id)
        self.assertNotEqual(first.pdr_id, second.pdr_id)
        self.assertTrue(first.is_fresh_at(100))
        with self.assertRaises(ValueError):
            issue_materialization_pdr(TransformationManifest("fixture-transform-v1", "1", "fixture-test-file-v1", "sha256:" + "0" * 64), verified, now=100)


if __name__ == "__main__":
    unittest.main()
