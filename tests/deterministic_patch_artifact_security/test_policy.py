"""Tests for registered metadata security facts."""

from __future__ import annotations

from dataclasses import replace
import unittest

from forgeflow.deterministic_patch_artifact_security.canonical import (
    redaction_id_for,
    scan_id_for,
)
from forgeflow.deterministic_patch_artifact_security.models import (
    PatchArtifact,
    PatchIntent,
    RedactionFact,
    SecretScanResult,
)
from forgeflow.deterministic_patch_artifact_security.policy import (
    candidate_for,
    redact_metadata,
    scan_metadata,
)
from forgeflow.deterministic_patch_artifact_security.profile import (
    M4_PATCH_METADATA_SECURITY_V1,
    MetadataSecurityProfile,
)


_DIGEST = "sha256:" + "a" * 64


def _intent(description: str = "Correct the addition result.") -> PatchIntent:
    return PatchIntent(
        contract_version="m4-patch-artifact-security/v1",
        repository_identity="fixture-repository-1300511729",
        base_revision="97c8220cd713ebf61124ac2de2f3eadc6e4dc222",
        intent_id=_DIGEST,
        target_scope=("src/calculator.py",),
        change_description=description,
        lineage_digest=_DIGEST,
    )


def _artifact() -> PatchArtifact:
    return PatchArtifact(
        contract_version="m4-patch-artifact-security/v1",
        artifact_id=_DIGEST,
        repository_identity="fixture-repository-1300511729",
        base_revision="97c8220cd713ebf61124ac2de2f3eadc6e4dc222",
        patch_intent_id=_DIGEST,
        target_scope=("src/calculator.py",),
        metadata_digest=_DIGEST,
        lineage_digest=_DIGEST,
    )


class MetadataSecurityPolicyTests(unittest.TestCase):
    def test_clean_metadata_passes_and_yields_not_needed_candidate(self) -> None:
        scan = scan_metadata(_intent(), _artifact(), M4_PATCH_METADATA_SECURITY_V1)
        redaction = redact_metadata(
            _intent(), _artifact(), scan, M4_PATCH_METADATA_SECURITY_V1
        )
        candidate = candidate_for(
            _intent(), _artifact(), scan, redaction, M4_PATCH_METADATA_SECURITY_V1
        )

        self.assertEqual(scan.result, "passed")
        self.assertEqual(redaction.status, "not_needed")
        self.assertIsNotNone(candidate)

    def test_each_registered_secret_rule_blocks_without_candidate(self) -> None:
        cases = (
            ("private-key-marker", "-----BEGIN TEST PRIVATE KEY-----"),
            ("github-token-prefix", "ghp_abcdefghijklmnopqrstuvwx"),
            ("credential-assignment", "token=abcdefgh"),
            ("jwt-like-token", "eyJabcdefgh.abcdefgh.abcdefgh"),
        )
        for rule_id, description in cases:
            with self.subTest(rule_id=rule_id):
                scan = scan_metadata(_intent(description), _artifact(), M4_PATCH_METADATA_SECURITY_V1)
                redaction = redact_metadata(
                    _intent(description), _artifact(), scan, M4_PATCH_METADATA_SECURITY_V1
                )

                self.assertEqual(scan.result, "blocked")
                self.assertEqual(scan.findings_summary[0].rule_id, rule_id)
                self.assertEqual(redaction.status, "redacted")
                self.assertIsNone(
                    candidate_for(
                        _intent(description),
                        _artifact(),
                        scan,
                        redaction,
                        M4_PATCH_METADATA_SECURITY_V1,
                    )
                )

    def test_invalid_profile_identity_is_indeterminate_and_never_candidate_eligible(self) -> None:
        mismatched = replace(
            M4_PATCH_METADATA_SECURITY_V1,
            profile_version=2,
            scanner_version="unregistered-scanner",
        )

        scan = scan_metadata(_intent(), _artifact(), mismatched)
        redaction = redact_metadata(_intent(), _artifact(), scan, mismatched)

        self.assertEqual(scan.result, "indeterminate")
        self.assertEqual(
            scan.scanner_version, M4_PATCH_METADATA_SECURITY_V1.scanner_version
        )
        self.assertEqual(redaction.status, "indeterminate")
        self.assertEqual(
            redaction.rule_set_id, M4_PATCH_METADATA_SECURITY_V1.redaction_rule_set_id
        )
        self.assertIsNone(candidate_for(_intent(), _artifact(), scan, redaction, mismatched))

    def test_tampered_scan_lineage_becomes_indeterminate(self) -> None:
        scan = scan_metadata(_intent(), _artifact(), M4_PATCH_METADATA_SECURITY_V1)
        tampered = replace(scan, scan_id="sha256:" + "b" * 64)

        redaction = redact_metadata(
            _intent(), _artifact(), tampered, M4_PATCH_METADATA_SECURITY_V1
        )

        self.assertEqual(redaction.status, "indeterminate")
        self.assertIsNone(
            candidate_for(
                _intent(), _artifact(), tampered, redaction, M4_PATCH_METADATA_SECURITY_V1
            )
        )

    def test_failed_scanner_and_redactor_are_never_candidate_eligible(self) -> None:
        failed_scan = SecretScanResult(
            contract_version="m4-patch-artifact-security/v1",
            scan_id=_DIGEST,
            artifact_id=_artifact().artifact_id,
            rule_set_id=M4_PATCH_METADATA_SECURITY_V1.secret_scan_rule_set_id,
            scanner_version=M4_PATCH_METADATA_SECURITY_V1.scanner_version,
            result="failed",
            findings_summary=(),
            failure_reason="scanner_operation_failed",
        )
        failed_redaction = redact_metadata(
            _intent(), _artifact(), failed_scan, M4_PATCH_METADATA_SECURITY_V1
        )

        self.assertEqual(failed_redaction.status, "failed")
        self.assertIsNone(
            candidate_for(
                _intent(),
                _artifact(),
                failed_scan,
                failed_redaction,
                M4_PATCH_METADATA_SECURITY_V1,
            )
        )

        failed_redaction = RedactionFact(
            contract_version="m4-patch-artifact-security/v1",
            redaction_id=_DIGEST,
            input_artifact_id=_artifact().artifact_id,
            secret_scan_id=_DIGEST,
            output_artifact_digest=None,
            rule_set_id=M4_PATCH_METADATA_SECURITY_V1.redaction_rule_set_id,
            status="failed",
        )
        passed_scan = scan_metadata(_intent(), _artifact(), M4_PATCH_METADATA_SECURITY_V1)
        self.assertIsNone(
            candidate_for(
                _intent(),
                _artifact(),
                passed_scan,
                failed_redaction,
                M4_PATCH_METADATA_SECURITY_V1,
            )
        )

    def test_tampered_redaction_identity_is_never_candidate_eligible(self) -> None:
        scan = scan_metadata(_intent(), _artifact(), M4_PATCH_METADATA_SECURITY_V1)
        redaction = redact_metadata(
            _intent(), _artifact(), scan, M4_PATCH_METADATA_SECURITY_V1
        )
        tampered = replace(redaction, redaction_id="sha256:" + "c" * 64)

        self.assertIsNone(
            candidate_for(
                _intent(), _artifact(), scan, tampered, M4_PATCH_METADATA_SECURITY_V1
            )
        )

    def test_unaligned_intent_and_artifact_are_indeterminate(self) -> None:
        unrelated_artifact = replace(
            _artifact(), patch_intent_id="sha256:" + "b" * 64
        )

        scan = scan_metadata(
            _intent(), unrelated_artifact, M4_PATCH_METADATA_SECURITY_V1
        )

        self.assertEqual(scan.result, "indeterminate")
        self.assertEqual(scan.failure_reason, "metadata_projection_invalid")

    def test_self_consistent_forged_facts_cannot_create_candidate(self) -> None:
        intent = _intent()
        artifact = _artifact()
        expected_scan = scan_metadata(intent, artifact, M4_PATCH_METADATA_SECURITY_V1)
        forged_scan = replace(expected_scan, contract_version="forged/v1")
        forged_scan = replace(forged_scan, scan_id=scan_id_for(forged_scan))
        expected_redaction = redact_metadata(
            intent, artifact, expected_scan, M4_PATCH_METADATA_SECURITY_V1
        )
        forged_redaction = replace(
            expected_redaction, secret_scan_id=forged_scan.scan_id
        )
        forged_redaction = replace(
            forged_redaction, redaction_id=redaction_id_for(forged_redaction)
        )

        self.assertIsNone(
            candidate_for(
                intent,
                artifact,
                forged_scan,
                forged_redaction,
                M4_PATCH_METADATA_SECURITY_V1,
            )
        )

    def test_profile_is_immutable_and_metadata_only(self) -> None:
        self.assertIsInstance(M4_PATCH_METADATA_SECURITY_V1, MetadataSecurityProfile)
        self.assertEqual(
            M4_PATCH_METADATA_SECURITY_V1.allowed_field_names,
            (
                "PatchArtifact.target_scope",
                "PatchIntent.change_description",
                "PatchIntent.target_scope",
            ),
        )
        with self.assertRaises(Exception):
            M4_PATCH_METADATA_SECURITY_V1.profile_version = 2  # type: ignore[misc]


if __name__ == "__main__":
    unittest.main()
