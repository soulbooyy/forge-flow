"""Contract tests for metadata-only Feature 2 facts."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
import unittest

from forgeflow.deterministic_patch_artifact_security.models import (
    PatchArtifact,
    PatchIntent,
    RedactedArtifactReferenceCandidate,
    RedactionFact,
    ScanFinding,
    SecretScanResult,
)


_DIGEST = "sha256:" + "a" * 64


class ContractTests(unittest.TestCase):
    def test_patch_intent_is_immutable_and_non_authorizing(self) -> None:
        intent = PatchIntent(
            contract_version="m4-patch-artifact-security/v1",
            repository_identity="fixture-repository-1300511729",
            base_revision="97c8220cd713ebf61124ac2de2f3eadc6e4dc222",
            intent_id=_DIGEST,
            target_scope=("src/calculator.py",),
            change_description="Correct the addition result.",
            lineage_digest=_DIGEST,
        )

        self.assertEqual(intent.target_scope, ("src/calculator.py",))
        with self.assertRaises(FrozenInstanceError):
            intent.change_description = "change"  # type: ignore[misc]

    def test_patch_artifact_rejects_diff_and_application_fields(self) -> None:
        artifact = PatchArtifact(
            contract_version="m4-patch-artifact-security/v1",
            artifact_id=_DIGEST,
            repository_identity="fixture-repository-1300511729",
            base_revision="97c8220cd713ebf61124ac2de2f3eadc6e4dc222",
            patch_intent_id=_DIGEST,
            target_scope=("src/calculator.py",),
            metadata_digest=_DIGEST,
            lineage_digest=_DIGEST,
        )

        self.assertFalse(hasattr(artifact, "raw_patch_content"))
        self.assertFalse(hasattr(artifact, "diff_metadata"))
        self.assertFalse(hasattr(artifact, "execution_status"))

    def test_metadata_text_and_scope_reject_payload_or_escape_forms(self) -> None:
        with self.assertRaises(ValueError):
            PatchIntent(
                contract_version="m4-patch-artifact-security/v1",
                repository_identity="fixture-repository-1300511729",
                base_revision="97c8220cd713ebf61124ac2de2f3eadc6e4dc222",
                intent_id=_DIGEST,
                target_scope=("src\\..\\private.txt",),
                change_description="Correct the addition result.",
                lineage_digest=_DIGEST,
            )
        with self.assertRaises(ValueError):
            PatchIntent(
                contract_version="m4-patch-artifact-security/v1",
                repository_identity="fixture-repository-1300511729",
                base_revision="97c8220cd713ebf61124ac2de2f3eadc6e4dc222",
                intent_id=_DIGEST,
                target_scope=("src/calculator.py",),
                change_description="x" * 1_001,
                lineage_digest=_DIGEST,
            )
        with self.assertRaises(ValueError):
            PatchIntent(
                contract_version="m4-patch-artifact-security/v1",
                repository_identity="fixture-repository-1300511729",
                base_revision="97c8220cd713ebf61124ac2de2f3eadc6e4dc222",
                intent_id=_DIGEST,
                target_scope=("C:private.txt",),
                change_description="metadata must remain single-line\nnot payload text",
                lineage_digest=_DIGEST,
            )

    def test_scan_and_redaction_facts_enforce_controlled_values(self) -> None:
        scan = SecretScanResult(
            contract_version="m4-patch-artifact-security/v1",
            scan_id=_DIGEST,
            artifact_id=_DIGEST,
            rule_set_id="m4-patch-metadata-secret-scan-v1",
            scanner_version="deterministic-metadata-scanner-v1",
            result="passed",
            findings_summary=(),
            failure_reason=None,
        )
        redaction = RedactionFact(
            contract_version="m4-patch-artifact-security/v1",
            redaction_id=_DIGEST,
            input_artifact_id=_DIGEST,
            output_artifact_digest=_DIGEST,
            rule_set_id="m4-patch-metadata-redaction-v1",
            status="not_needed",
        )

        self.assertEqual(scan.result, "passed")
        self.assertEqual(redaction.status, "not_needed")
        with self.assertRaises(ValueError):
            SecretScanResult(
                contract_version="m4-patch-artifact-security/v1",
                scan_id=_DIGEST,
                artifact_id=_DIGEST,
                rule_set_id="m4-patch-metadata-secret-scan-v1",
                scanner_version="deterministic-metadata-scanner-v1",
                result="approval_required",
                findings_summary=(),
                failure_reason=None,
            )
        with self.assertRaises(ValueError):
            SecretScanResult(
                contract_version="m4-patch-artifact-security/v1",
                scan_id=_DIGEST,
                artifact_id=_DIGEST,
                rule_set_id="m4-patch-metadata-secret-scan-v1",
                scanner_version="deterministic-metadata-scanner-v1",
                result="passed",
                findings_summary=(
                    ScanFinding(
                        rule_id="github-token-prefix",
                        field_name="PatchIntent.change_description",
                    ),
                ),
                failure_reason=None,
            )
        with self.assertRaises(ValueError):
            ScanFinding(
                rule_id="matched-text",
                field_name="PatchIntent.change_description",
            )

    def test_safe_path_and_error_fields_reject_uncontrolled_payload_text(self) -> None:
        with self.assertRaises(ValueError):
            PatchIntent(
                contract_version="m4-patch-artifact-security/v1",
                repository_identity="fixture-repository-1300511729",
                base_revision="97c8220cd713ebf61124ac2de2f3eadc6e4dc222",
                intent_id=_DIGEST,
                target_scope=("src/line\nbreak.py",),
                change_description="Correct the addition result.",
                lineage_digest=_DIGEST,
            )
        with self.assertRaises(ValueError):
            SecretScanResult(
                contract_version="m4-patch-artifact-security/v1",
                scan_id=_DIGEST,
                artifact_id=_DIGEST,
                rule_set_id="m4-patch-metadata-secret-scan-v1",
                scanner_version="deterministic-metadata-scanner-v1",
                result="failed",
                findings_summary=(),
                failure_reason="uncontrolled rejected value",
            )

    def test_blocked_findings_follow_registered_rule_table_order(self) -> None:
        scan = SecretScanResult(
            contract_version="m4-patch-artifact-security/v1",
            scan_id=_DIGEST,
            artifact_id=_DIGEST,
            rule_set_id="m4-patch-metadata-secret-scan-v1",
            scanner_version="deterministic-metadata-scanner-v1",
            result="blocked",
            findings_summary=(
                ScanFinding(
                    rule_id="private-key-marker",
                    field_name="PatchIntent.change_description",
                ),
                ScanFinding(
                    rule_id="credential-assignment",
                    field_name="PatchIntent.change_description",
                ),
            ),
            failure_reason=None,
        )

        self.assertEqual(scan.findings_summary[0].rule_id, "private-key-marker")

    def test_candidate_is_identity_bound_to_scan_and_redaction_lineage(self) -> None:
        candidate = RedactedArtifactReferenceCandidate(
            contract_version="m4-patch-artifact-security/v1",
            candidate_id=_DIGEST,
            patch_artifact_id=_DIGEST,
            secret_scan_id=_DIGEST,
            redaction_id=_DIGEST,
            redacted_metadata_digest=_DIGEST,
            lineage_digest=_DIGEST,
            profile_id="forgeflow-m4-patch-metadata-security",
            profile_version=1,
            secret_scan_rule_set_id="m4-patch-metadata-secret-scan-v1",
            redaction_rule_set_id="m4-patch-metadata-redaction-v1",
        )

        self.assertEqual(candidate.secret_scan_id, _DIGEST)
        with self.assertRaises(ValueError):
            RedactedArtifactReferenceCandidate(
                contract_version="m4-patch-artifact-security/v1",
                candidate_id="candidate-1",
                patch_artifact_id=_DIGEST,
                secret_scan_id=_DIGEST,
                redaction_id=_DIGEST,
                redacted_metadata_digest=_DIGEST,
                lineage_digest=_DIGEST,
                profile_id="forgeflow-m4-patch-metadata-security",
                profile_version=1,
                secret_scan_rule_set_id="m4-patch-metadata-secret-scan-v1",
                redaction_rule_set_id="m4-patch-metadata-redaction-v1",
            )


if __name__ == "__main__":
    unittest.main()
