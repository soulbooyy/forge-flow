"""Contract tests for terminal-first metadata-only Feature 2 facts."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
import unittest

from forgeflow.governed_changes.artifact_security.models import (
    PatchArtifact,
    PatchIntent,
    PatchSecurityTerminal,
    PreScanPatchMetadataIdentity,
    RedactedArtifactReferenceCandidate,
    DeterministicPatchArtifactSecurityValidationError,
    RedactionFact,
    ScanFinding,
    SecretScanResult,
)


_DIGEST = "sha256:" + "a" * 64
_BASE_REVISION = "97c8220cd713ebf61124ac2de2f3eadc6e4dc222"
_VERSION = "m4-patch-artifact-security/v1"


def _pre_scan() -> PreScanPatchMetadataIdentity:
    return PreScanPatchMetadataIdentity(
        contract_version=_VERSION,
        pre_scan_metadata_id=_DIGEST,
        repository_identity="fixture-repository-1300511729",
        base_revision=_BASE_REVISION,
        target_scope=("src/calculator.py",),
        lineage_digest=_DIGEST,
    )


def _passed_scan() -> SecretScanResult:
    return SecretScanResult(
        contract_version=_VERSION,
        scan_id=_DIGEST,
        pre_scan_metadata_id=_DIGEST,
        rule_set_id="m4-patch-metadata-secret-scan-v1",
        scanner_version="deterministic-metadata-scanner-v1",
        result="passed",
        findings_summary=(),
        failure_reason=None,
    )


def _not_needed_redaction() -> RedactionFact:
    return RedactionFact(
        contract_version=_VERSION,
        redaction_id=_DIGEST,
        input_pre_scan_metadata_id=_DIGEST,
        secret_scan_id=_DIGEST,
        output_metadata_digest=_DIGEST,
        rule_set_id="m4-patch-metadata-redaction-v1",
        status="not_needed",
    )


def _redacted_redaction() -> RedactionFact:
    return RedactionFact(
        contract_version=_VERSION,
        redaction_id=_DIGEST,
        input_pre_scan_metadata_id=_DIGEST,
        secret_scan_id=_DIGEST,
        output_metadata_digest=_DIGEST,
        rule_set_id="m4-patch-metadata-redaction-v1",
        status="redacted",
    )


class ContractTests(unittest.TestCase):
    def test_pre_scan_identity_is_immutable_and_excludes_raw_metadata(self) -> None:
        identity = _pre_scan()

        self.assertEqual(identity.target_scope, ("src/calculator.py",))
        self.assertFalse(hasattr(identity, "change_description"))
        self.assertFalse(hasattr(identity, "rationale"))
        with self.assertRaises(FrozenInstanceError):
            identity.target_scope = ()  # type: ignore[misc]

    def test_intent_and_artifact_are_payload_free_and_bound_to_pre_scan_identity(self) -> None:
        intent = PatchIntent(
            contract_version=_VERSION,
            repository_identity="fixture-repository-1300511729",
            base_revision=_BASE_REVISION,
            intent_id=_DIGEST,
            pre_scan_metadata_id=_DIGEST,
            target_scope=("src/calculator.py",),
            scanned_metadata_digest=_DIGEST,
            lineage_digest=_DIGEST,
        )
        artifact = PatchArtifact(
            contract_version=_VERSION,
            artifact_id=_DIGEST,
            repository_identity="fixture-repository-1300511729",
            base_revision=_BASE_REVISION,
            patch_intent_id=_DIGEST,
            target_scope=("src/calculator.py",),
            metadata_digest=_DIGEST,
            lineage_digest=_DIGEST,
        )

        self.assertEqual(intent.pre_scan_metadata_id, _DIGEST)
        self.assertFalse(hasattr(intent, "change_description"))
        self.assertFalse(hasattr(artifact, "raw_patch_content"))
        self.assertFalse(hasattr(artifact, "execution_status"))

    def test_pre_scan_contracts_reject_scope_escape_or_non_digest_lineage(self) -> None:
        with self.assertRaises(ValueError):
            PreScanPatchMetadataIdentity(
                contract_version=_VERSION,
                pre_scan_metadata_id=_DIGEST,
                repository_identity="fixture-repository-1300511729",
                base_revision=_BASE_REVISION,
                target_scope=("src/../private.txt",),
                lineage_digest=_DIGEST,
            )
        with self.assertRaises(ValueError):
            PreScanPatchMetadataIdentity(
                contract_version=_VERSION,
                pre_scan_metadata_id="not-a-digest",
                repository_identity="fixture-repository-1300511729",
                base_revision=_BASE_REVISION,
                target_scope=("src/calculator.py",),
                lineage_digest=_DIGEST,
            )

    def test_security_facts_anchor_to_pre_scan_identity_without_artifact_reference(self) -> None:
        scan = _passed_scan()
        redaction = _not_needed_redaction()

        self.assertEqual(scan.pre_scan_metadata_id, _DIGEST)
        self.assertEqual(redaction.input_pre_scan_metadata_id, _DIGEST)
        self.assertFalse(hasattr(scan, "artifact_id"))
        self.assertFalse(hasattr(redaction, "input_artifact_id"))

    def test_terminal_is_the_only_unsafe_contract_and_has_controlled_reason(self) -> None:
        scan = SecretScanResult(
            contract_version=_VERSION,
            scan_id=_DIGEST,
            pre_scan_metadata_id=_DIGEST,
            rule_set_id="m4-patch-metadata-secret-scan-v1",
            scanner_version="deterministic-metadata-scanner-v1",
            result="blocked",
            findings_summary=(
                ScanFinding(
                    rule_id="github-token-prefix",
                    field_name="PreScanMetadataProjection.change_description",
                ),
            ),
            failure_reason=None,
        )
        terminal = PatchSecurityTerminal(
            contract_version=_VERSION,
            terminal_id=_DIGEST,
            pre_scan_metadata_id=_DIGEST,
            lineage_digest=_DIGEST,
            secret_scan_result=scan,
            redaction_fact=_redacted_redaction(),
            terminal_status="blocked",
            terminal_reason="security_rule_blocked",
        )

        self.assertFalse(hasattr(terminal, "patch_intent"))
        self.assertFalse(hasattr(terminal, "patch_artifact"))
        self.assertFalse(hasattr(terminal, "candidate"))
        with self.assertRaises(ValueError):
            PatchSecurityTerminal(
                contract_version=_VERSION,
                terminal_id=_DIGEST,
                pre_scan_metadata_id=_DIGEST,
                lineage_digest=_DIGEST,
                secret_scan_result=scan,
                redaction_fact=_not_needed_redaction(),
                terminal_status="blocked",
                terminal_reason="security_rule_blocked",
            )
        with self.assertRaises(ValueError):
            PatchSecurityTerminal(
                contract_version=_VERSION,
                terminal_id=_DIGEST,
                pre_scan_metadata_id=_DIGEST,
                lineage_digest=_DIGEST,
                secret_scan_result=scan,
                redaction_fact=_not_needed_redaction(),
                terminal_status="blocked",
                terminal_reason="scanner_operation_failed",
            )
        with self.assertRaises(ValueError):
            PatchSecurityTerminal(
                contract_version=_VERSION,
                terminal_id=_DIGEST,
                pre_scan_metadata_id=_DIGEST,
                lineage_digest=_DIGEST,
                secret_scan_result=_passed_scan(),
                redaction_fact=_not_needed_redaction(),
                terminal_status="blocked",
                terminal_reason="security_rule_blocked",
            )
        failed_scan = SecretScanResult(
            contract_version=_VERSION,
            scan_id=_DIGEST,
            pre_scan_metadata_id=_DIGEST,
            rule_set_id="m4-patch-metadata-secret-scan-v1",
            scanner_version="deterministic-metadata-scanner-v1",
            result="failed",
            findings_summary=(),
            failure_reason="scanner_operation_failed",
        )
        with self.assertRaises(ValueError):
            PatchSecurityTerminal(
                contract_version=_VERSION,
                terminal_id=_DIGEST,
                pre_scan_metadata_id=_DIGEST,
                lineage_digest=_DIGEST,
                secret_scan_result=failed_scan,
                redaction_fact=_not_needed_redaction(),
                terminal_status="failed",
                terminal_reason="redaction_operation_failed",
            )

    def test_candidate_carries_pre_scan_lineage(self) -> None:
        candidate = RedactedArtifactReferenceCandidate(
            contract_version=_VERSION,
            candidate_id=_DIGEST,
            patch_artifact_id=_DIGEST,
            pre_scan_metadata_id=_DIGEST,
            secret_scan_id=_DIGEST,
            redaction_id=_DIGEST,
            redacted_metadata_digest=_DIGEST,
            lineage_digest=_DIGEST,
            profile_id="forgeflow-m4-patch-metadata-security",
            profile_version=1,
            secret_scan_rule_set_id="m4-patch-metadata-secret-scan-v1",
            redaction_rule_set_id="m4-patch-metadata-redaction-v1",
        )

        self.assertEqual(candidate.pre_scan_metadata_id, _DIGEST)

    def test_security_lineage_uses_only_the_registered_profile_identities(self) -> None:
        with self.assertRaises(ValueError):
            SecretScanResult(
                contract_version=_VERSION, scan_id=_DIGEST,
                pre_scan_metadata_id=_DIGEST, rule_set_id="unknown-rule-set",
                scanner_version="deterministic-metadata-scanner-v1", result="passed",
                findings_summary=(), failure_reason=None,
            )
        with self.assertRaises(ValueError):
            RedactionFact(
                contract_version=_VERSION, redaction_id=_DIGEST,
                input_pre_scan_metadata_id=_DIGEST, secret_scan_id=_DIGEST,
                output_metadata_digest=_DIGEST, rule_set_id="unknown-rule-set",
                status="not_needed",
            )
        with self.assertRaises(ValueError):
            RedactedArtifactReferenceCandidate(
                contract_version=_VERSION, candidate_id=_DIGEST,
                patch_artifact_id=_DIGEST, pre_scan_metadata_id=_DIGEST,
                secret_scan_id=_DIGEST, redaction_id=_DIGEST,
                redacted_metadata_digest=_DIGEST, lineage_digest=_DIGEST,
                profile_id="unknown-profile", profile_version=0,
                secret_scan_rule_set_id="unknown-rule-set",
                redaction_rule_set_id="unknown-rule-set",
            )

    def test_identity_fields_reject_raw_or_unregistered_text(self) -> None:
        with self.assertRaises(ValueError):
            PreScanPatchMetadataIdentity(
                contract_version=_VERSION,
                pre_scan_metadata_id=_DIGEST,
                repository_identity="raw source contents " * 100,
                base_revision=_BASE_REVISION,
                target_scope=("src/calculator.py",),
                lineage_digest=_DIGEST,
            )

    def test_profile_version_and_validation_error_code_are_controlled(self) -> None:
        with self.assertRaises(ValueError):
            RedactedArtifactReferenceCandidate(
                contract_version=_VERSION, candidate_id=_DIGEST,
                patch_artifact_id=_DIGEST, pre_scan_metadata_id=_DIGEST,
                secret_scan_id=_DIGEST, redaction_id=_DIGEST,
                redacted_metadata_digest=_DIGEST, lineage_digest=_DIGEST,
                profile_id="forgeflow-m4-patch-metadata-security", profile_version=True,
                secret_scan_rule_set_id="m4-patch-metadata-secret-scan-v1",
                redaction_rule_set_id="m4-patch-metadata-redaction-v1",
            )
        with self.assertRaises(ValueError):
            DeterministicPatchArtifactSecurityValidationError(
                schema_version=_VERSION, error_id=_DIGEST,
                error_code="raw source contents " * 100,
                summary="metadata security input is invalid",
            )
        with self.assertRaises(ValueError):
            PreScanPatchMetadataIdentity(
                contract_version="unregistered-contract-version",
                pre_scan_metadata_id=_DIGEST,
                repository_identity="fixture-repository-1300511729",
                base_revision=_BASE_REVISION,
                target_scope=("src/calculator.py",),
                lineage_digest=_DIGEST,
            )


if __name__ == "__main__":
    unittest.main()
