"""Canonical identity tests for terminal-first Feature 2 contracts."""

from __future__ import annotations

from dataclasses import replace
import unittest

from forgeflow.deterministic_patch_artifact_security.canonical import (
    candidate_id_for,
    canonical_bytes,
    is_canonical_candidate,
    pre_scan_metadata_id_for,
    sha256_hex,
    terminal_id_for,
)
from forgeflow.deterministic_patch_artifact_security.models import (
    PatchSecurityTerminal,
    PreScanPatchMetadataIdentity,
    RedactionFact,
    RedactedArtifactReferenceCandidate,
    SecretScanResult,
)


_DIGEST = "sha256:" + "0" * 64
_BASE_REVISION = "97c8220cd713ebf61124ac2de2f3eadc6e4dc222"
_VERSION = "m4-patch-artifact-security/v1"


def _pre_scan() -> PreScanPatchMetadataIdentity:
    return PreScanPatchMetadataIdentity(
        contract_version=_VERSION,
        pre_scan_metadata_id=_DIGEST,
        repository_identity="fixture-repository-1300511729",
        base_revision=_BASE_REVISION,
        target_scope=("src/calculator.py",),
        lineage_digest="sha256:" + "a" * 64,
    )


class CanonicalTests(unittest.TestCase):
    def test_canonical_bytes_sort_mapping_keys_and_reject_float(self) -> None:
        self.assertEqual(canonical_bytes({"z": 1, "a": 2}), b'{"a":2,"z":1}')
        with self.assertRaises(TypeError):
            canonical_bytes({"value": 1.5})

    def test_pre_scan_identity_omits_only_its_identity_field(self) -> None:
        provisional = _pre_scan()

        identity = pre_scan_metadata_id_for(provisional)
        self.assertEqual(
            identity,
            pre_scan_metadata_id_for(
                replace(provisional, pre_scan_metadata_id=identity)
            ),
        )
        self.assertEqual(len(sha256_hex(provisional)), 64)

    def test_terminal_identity_binds_security_facts_and_reason(self) -> None:
        scan = SecretScanResult(
            contract_version=_VERSION,
            scan_id="sha256:" + "b" * 64,
            pre_scan_metadata_id=_DIGEST,
            rule_set_id="m4-patch-metadata-secret-scan-v1",
            scanner_version="deterministic-metadata-scanner-v1",
            result="failed",
            findings_summary=(),
            failure_reason="scanner_operation_failed",
        )
        redaction = RedactionFact(
            contract_version=_VERSION,
            redaction_id="sha256:" + "c" * 64,
            input_pre_scan_metadata_id=_DIGEST,
            secret_scan_id=scan.scan_id,
            output_metadata_digest=None,
            rule_set_id="m4-patch-metadata-redaction-v1",
            status="failed",
        )
        provisional = PatchSecurityTerminal(
            contract_version=_VERSION,
            terminal_id=_DIGEST,
            pre_scan_metadata_id=_DIGEST,
            lineage_digest="sha256:" + "d" * 64,
            secret_scan_result=scan,
            redaction_fact=redaction,
            terminal_status="failed",
            terminal_reason="scanner_operation_failed",
        )

        identity = terminal_id_for(provisional)
        self.assertEqual(
            identity,
            terminal_id_for(replace(provisional, terminal_id=identity)),
        )

    def test_candidate_identity_must_be_canonical_before_cross_feature_use(self) -> None:
        provisional = RedactedArtifactReferenceCandidate(
            contract_version=_VERSION, candidate_id=_DIGEST,
            patch_artifact_id=_DIGEST, pre_scan_metadata_id=_DIGEST,
            secret_scan_id=_DIGEST, redaction_id=_DIGEST,
            redacted_metadata_digest=_DIGEST, lineage_digest="sha256:" + "a" * 64,
            profile_id="forgeflow-m4-patch-metadata-security", profile_version=1,
            secret_scan_rule_set_id="m4-patch-metadata-secret-scan-v1",
            redaction_rule_set_id="m4-patch-metadata-redaction-v1",
        )
        self.assertFalse(is_canonical_candidate(provisional))
        candidate = replace(provisional, candidate_id=candidate_id_for(provisional))
        self.assertTrue(is_canonical_candidate(candidate))


if __name__ == "__main__":
    unittest.main()
