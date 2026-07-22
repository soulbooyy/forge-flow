"""Tests for terminal-first transient metadata security facts."""

from __future__ import annotations

from dataclasses import replace
import unittest

from forgeflow.governed_changes.artifact_security.canonical import (
    pre_scan_metadata_id_for,
    redaction_id_for,
    scan_id_for,
    sha256_hex,
)
from forgeflow.governed_changes.artifact_security.models import (
    PreScanPatchMetadataIdentity,
)
from forgeflow.governed_changes.artifact_security.policy import (
    redact_metadata,
    scan_metadata,
)
from forgeflow.governed_changes.artifact_security.profile import (
    M4_PATCH_METADATA_SECURITY_V1,
)


_VERSION = "m4-patch-artifact-security/v1"
_BASE_REVISION = "97c8220cd713ebf61124ac2de2f3eadc6e4dc222"
_DIGEST = "sha256:" + "a" * 64


def _identity() -> PreScanPatchMetadataIdentity:
    provisional = PreScanPatchMetadataIdentity(
        contract_version=_VERSION,
        pre_scan_metadata_id="sha256:" + "0" * 64,
        repository_identity="fixture-repository-1300511729",
        base_revision=_BASE_REVISION,
        target_scope=("src/calculator.py",),
        lineage_digest=_DIGEST,
    )
    return replace(
        provisional,
        pre_scan_metadata_id=pre_scan_metadata_id_for(provisional),
    )


def _projection(
    description: str = "Correct the addition result.",
) -> tuple[tuple[str, str], ...]:
    return (
        ("PreScanMetadataProjection.change_description", description),
        ("PreScanMetadataProjection.target_scope", "src/calculator.py"),
    )


class MetadataSecurityPolicyTests(unittest.TestCase):
    def test_clean_projection_has_passed_scan_and_not_needed_redaction(self) -> None:
        identity = _identity()
        projection = _projection()

        scan = scan_metadata(identity, projection, M4_PATCH_METADATA_SECURITY_V1)
        redaction = redact_metadata(
            identity, projection, scan, M4_PATCH_METADATA_SECURITY_V1
        )

        self.assertEqual(scan.result, "passed")
        self.assertEqual(redaction.status, "not_needed")
        self.assertEqual(redaction.output_metadata_digest, "sha256:" + sha256_hex(projection))
        self.assertFalse(hasattr(scan, "artifact_id"))
        self.assertFalse(hasattr(redaction, "input_artifact_id"))

    def test_each_registered_rule_blocks_without_retaining_matched_value(self) -> None:
        cases = (
            ("private-key-marker", "-----BEGIN PRIVATE KEY-----"),
            ("github-token-prefix", "ghp_abcdefghijklmnopqrstuvwx"),
            ("credential-assignment", "token=abcdefgh"),
            ("jwt-like-token", "eyJabcdefgh.abcdefgh.abcdefgh"),
        )
        for rule_id, description in cases:
            with self.subTest(rule_id=rule_id):
                identity = _identity()
                scan = scan_metadata(
                    identity, _projection(description), M4_PATCH_METADATA_SECURITY_V1
                )
                redaction = redact_metadata(
                    identity, _projection(description), scan, M4_PATCH_METADATA_SECURITY_V1
                )

                self.assertEqual(scan.result, "blocked")
                self.assertEqual(scan.findings_summary[0].rule_id, rule_id)
                self.assertEqual(redaction.status, "redacted")
                self.assertNotIn(description, repr(scan))
                self.assertNotIn(description, repr(redaction))

    def test_profile_mismatch_fails_closed_as_indeterminate(self) -> None:
        mismatched = replace(M4_PATCH_METADATA_SECURITY_V1, profile_version=2)
        identity = _identity()
        projection = _projection()

        scan = scan_metadata(identity, projection, mismatched)
        redaction = redact_metadata(identity, projection, scan, mismatched)

        self.assertEqual(scan.result, "indeterminate")
        self.assertEqual(scan.failure_reason, "security_profile_mismatch")
        self.assertEqual(redaction.status, "indeterminate")

    def test_invalid_projection_is_indeterminate_and_exposes_no_output_digest(self) -> None:
        identity = _identity()
        invalid_projection = (
            ("PreScanMetadataProjection.change_description", "Correct the addition result."),
            ("PreScanMetadataProjection.target_scope", "other/file.py"),
        )

        scan = scan_metadata(
            identity, invalid_projection, M4_PATCH_METADATA_SECURITY_V1
        )
        redaction = redact_metadata(
            identity, invalid_projection, scan, M4_PATCH_METADATA_SECURITY_V1
        )

        self.assertEqual(scan.result, "indeterminate")
        self.assertEqual(scan.failure_reason, "metadata_projection_invalid")
        self.assertEqual(redaction.status, "indeterminate")
        self.assertIsNone(redaction.output_metadata_digest)

    def test_tampered_scan_becomes_indeterminate_redaction(self) -> None:
        identity = _identity()
        projection = _projection()
        scan = scan_metadata(identity, projection, M4_PATCH_METADATA_SECURITY_V1)
        tampered = replace(scan, scan_id="sha256:" + "b" * 64)

        redaction = redact_metadata(
            identity, projection, tampered, M4_PATCH_METADATA_SECURITY_V1
        )

        self.assertEqual(redaction.status, "indeterminate")

    def test_tampered_failed_scan_cannot_produce_a_failed_redaction_fact(self) -> None:
        identity = _identity()
        projection = _projection()
        scan = scan_metadata(identity, projection, M4_PATCH_METADATA_SECURITY_V1)
        tampered = replace(
            scan,
            result="failed",
            findings_summary=(),
            failure_reason="scanner_operation_failed",
        )
        tampered = replace(tampered, scan_id=scan_id_for(tampered))

        redaction = redact_metadata(
            identity, projection, tampered, M4_PATCH_METADATA_SECURITY_V1
        )

        self.assertEqual(redaction.status, "indeterminate")

    def test_redaction_identity_is_self_excluding_and_projection_digest_only(self) -> None:
        identity = _identity()
        projection = _projection("token=abcdefgh")
        scan = scan_metadata(identity, projection, M4_PATCH_METADATA_SECURITY_V1)
        redaction = redact_metadata(
            identity, projection, scan, M4_PATCH_METADATA_SECURITY_V1
        )

        self.assertEqual(redaction.redaction_id, redaction_id_for(redaction))
        self.assertEqual(scan.scan_id, scan_id_for(scan))
        self.assertNotIn("token=abcdefgh", repr(redaction))


if __name__ == "__main__":
    unittest.main()
