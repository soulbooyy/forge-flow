from __future__ import annotations

import unittest

from forgeflow.governed_changes.materialization.models import TransformationManifest
from forgeflow.governed_changes.materialization.policy import issue_materialization_pdr
from forgeflow.governed_changes.materialization.registry import (
    REGISTERED_SNAPSHOT,
    revalidate_snapshot,
    resolve_target_file,
    resolve_transformer,
)
from forgeflow.governed_changes.materialization.sandbox import DockerCapabilityProof, DockerMaterializationFacts, ValidationFacts
from forgeflow.governed_changes.materialization.service import EphemeralPayloadLease, materialize


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

    def test_unproven_sandbox_or_extra_file_fails_closed_and_clears_bytes(self) -> None:
        verified = revalidate_snapshot(REGISTERED_SNAPSHOT, {"tests/fixture_test.py": REGISTERED_SNAPSHOT.target_bytes}).snapshot
        pdr = issue_materialization_pdr(self.manifest(), verified, now=200)
        lease = EphemeralPayloadLease.for_test(b"assert True\n")
        result = materialize(pdr, verified, self.manifest(), FakeDocker(lease, extra_files=("other.py",)), now=200)
        self.assertEqual(result.terminal.reason, "materialization_failed")
        self.assertTrue(lease.destroyed)
        self.assertFalse(lease.handle.is_live)

    def test_validation_assertion_and_infrastructure_failures_are_distinct_and_cleanup(self) -> None:
        verified = revalidate_snapshot(REGISTERED_SNAPSHOT, {"tests/fixture_test.py": REGISTERED_SNAPSHOT.target_bytes}).snapshot
        for validation, reason in ((ValidationFacts("assertion_failed", "sha256:" + "1" * 64), "validation_failed"), (ValidationFacts("runner_unavailable", None), "validation_infrastructure_failed")):
            pdr = issue_materialization_pdr(self.manifest(), verified, now=300)
            lease = EphemeralPayloadLease.for_test(b"assert True\n")
            result = materialize(pdr, verified, self.manifest(), FakeDocker(lease, validation=validation), now=300)
            self.assertEqual(result.terminal.reason, reason)
            self.assertTrue(lease.destroyed)

    def test_all_sandbox_proof_gaps_expiry_security_and_exceptions_fail_closed(self) -> None:
        verified = revalidate_snapshot(REGISTERED_SNAPSHOT, {"tests/fixture_test.py": REGISTERED_SNAPSHOT.target_bytes}).snapshot
        for proof in (
            DockerCapabilityProof(False, True, True, True, True, True), DockerCapabilityProof(True, False, True, True, True, True),
            DockerCapabilityProof(True, True, False, True, True, True), DockerCapabilityProof(True, True, True, False, True, True),
            DockerCapabilityProof(True, True, True, True, False, True), DockerCapabilityProof(True, True, True, True, True, False),
            DockerCapabilityProof(True, True, True, True, True, True, False),
        ):
            pdr = issue_materialization_pdr(self.manifest(), verified, now=400)
            lease = EphemeralPayloadLease.for_test(b"assert True\n")
            result = materialize(pdr, verified, self.manifest(), FakeDocker(lease, proof=proof), now=400)
            self.assertEqual(result.terminal.reason, "validation_infrastructure_failed")
        expired = issue_materialization_pdr(self.manifest(), verified, now=500)
        self.assertEqual(materialize(expired, verified, self.manifest(), FakeDocker(EphemeralPayloadLease.for_test(b"assert True\n")), now=501).terminal.reason, "materialization_not_authorized")
        blocked = FakeDocker(EphemeralPayloadLease.for_test(b"assert True\n"), security_status="blocked")
        self.assertEqual(materialize(issue_materialization_pdr(self.manifest(), verified, now=600), verified, self.manifest(), blocked, now=600).terminal.reason, "materialization_failed")

    def test_private_harness_consumer_can_use_live_lease_once_then_cleanup(self) -> None:
        verified = revalidate_snapshot(REGISTERED_SNAPSHOT, {"tests/fixture_test.py": REGISTERED_SNAPSHOT.target_bytes}).snapshot
        lease = EphemeralPayloadLease.for_test(b"assert True\n")
        observed = []
        result = materialize(issue_materialization_pdr(self.manifest(), verified, now=700), verified, self.manifest(), FakeDocker(lease), now=700, _harness_consumer=lambda payload, live: observed.append((payload.payload_id, live.handle.is_live, live.bytes_for_harness)))
        self.assertIsNone(result.terminal)
        self.assertEqual(observed[0][1:], (True, b"assert True\n"))
        self.assertTrue(lease.destroyed)


class FakeDocker:
    def __init__(self, lease, *, extra_files=(), validation=ValidationFacts("passed", "sha256:" + "2" * 64), proof=DockerCapabilityProof(True, True, True, True, True, True), security_status="passed"):
        self.lease, self.extra_files, self.validation, self.proof, self.security_status = lease, extra_files, validation, proof, security_status

    def prove(self, profile):
        return self.proof

    def materialize(self, snapshot, manifest):
        return DockerMaterializationFacts(self.lease, self.extra_files, "sha256:" + "3" * 64, self.security_status)

    def validate(self, lease, profile):
        return self.validation


if __name__ == "__main__":
    unittest.main()
