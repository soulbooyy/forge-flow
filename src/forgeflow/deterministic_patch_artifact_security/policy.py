"""Pure deterministic scan/redaction functions for bounded metadata only."""

from __future__ import annotations

from dataclasses import replace
import re

from .canonical import candidate_id_for, redaction_id_for, scan_id_for, sha256_hex
from .models import (
    PatchArtifact,
    PatchIntent,
    RedactedArtifactReferenceCandidate,
    RedactionFact,
    ScanFinding,
    SecretScanResult,
)
from .profile import M4_PATCH_METADATA_SECURITY_V1, MetadataSecurityProfile


def scan_metadata(
    intent: PatchIntent, artifact: PatchArtifact, profile: MetadataSecurityProfile
) -> SecretScanResult:
    """Return only deterministic scan facts for the registered metadata projection."""
    if not _is_registered_profile(profile):
        return _scan_terminal(
            artifact,
            M4_PATCH_METADATA_SECURITY_V1,
            "indeterminate",
            "security_profile_mismatch",
        )
    if not _intent_artifact_aligned(intent, artifact):
        return _scan_terminal(
            artifact,
            M4_PATCH_METADATA_SECURITY_V1,
            "indeterminate",
            "metadata_projection_invalid",
        )
    projection = _projection(intent, artifact)
    findings = _findings(projection, profile)
    result = "blocked" if findings else "passed"
    provisional = SecretScanResult(
        contract_version=intent.contract_version,
        scan_id="sha256:" + "0" * 64,
        artifact_id=artifact.artifact_id,
        rule_set_id=profile.secret_scan_rule_set_id,
        scanner_version=profile.scanner_version,
        result=result,
        findings_summary=findings,
        failure_reason=None,
    )
    return replace(provisional, scan_id=scan_id_for(provisional))


def redact_metadata(
    intent: PatchIntent,
    artifact: PatchArtifact,
    scan: SecretScanResult,
    profile: MetadataSecurityProfile,
) -> RedactionFact:
    """Return a digest-only redaction fact after validating current scan lineage."""
    if not _is_registered_profile(profile) or scan.result == "indeterminate":
        return _redaction_terminal(
            artifact, M4_PATCH_METADATA_SECURITY_V1, scan.scan_id, "indeterminate"
        )
    if scan.result == "failed":
        return _redaction_terminal(artifact, profile, scan.scan_id, "failed")
    expected = scan_metadata(intent, artifact, profile)
    if (
        scan.artifact_id != artifact.artifact_id
        or scan.rule_set_id != profile.secret_scan_rule_set_id
        or scan.scanner_version != profile.scanner_version
        or scan.scan_id != scan_id_for(scan)
        or scan.result != expected.result
        or scan.findings_summary != expected.findings_summary
    ):
        return _redaction_terminal(artifact, profile, scan.scan_id, "indeterminate")
    projection = _projection(intent, artifact)
    if scan.result == "passed":
        return _redaction_success(artifact, profile, scan, "not_needed", projection)
    return _redaction_success(
        artifact, profile, scan, "redacted", _redacted_projection(projection, scan, profile)
    )


def candidate_for(
    intent: PatchIntent,
    artifact: PatchArtifact,
    scan: SecretScanResult,
    redaction: RedactionFact,
    profile: MetadataSecurityProfile,
) -> RedactedArtifactReferenceCandidate | None:
    """Return an in-memory candidate only for registered passed/not-needed facts."""
    if not _is_registered_profile(profile):
        return None
    if not _intent_artifact_aligned(intent, artifact):
        return None
    expected_scan = scan_metadata(intent, artifact, profile)
    expected_redaction = redact_metadata(intent, artifact, expected_scan, profile)
    if (
        scan.artifact_id != artifact.artifact_id
        or scan.rule_set_id != profile.secret_scan_rule_set_id
        or scan.scanner_version != profile.scanner_version
        or scan.scan_id != scan_id_for(scan)
        or scan != expected_scan
        or scan.result != "passed"
        or scan.findings_summary
        or redaction.input_artifact_id != artifact.artifact_id
        or redaction.rule_set_id != profile.redaction_rule_set_id
        or redaction.redaction_id != redaction_id_for(redaction)
        or redaction != expected_redaction
        or redaction.status != "not_needed"
        or redaction.output_artifact_digest is None
    ):
        return None
    lineage_digest = "sha256:" + sha256_hex(
        {
            "artifact_id": artifact.artifact_id,
            "scan_id": scan.scan_id,
            "redaction_id": redaction.redaction_id,
            "profile_id": profile.profile_id,
            "profile_version": profile.profile_version,
        }
    )
    provisional = RedactedArtifactReferenceCandidate(
        contract_version=artifact.contract_version,
        candidate_id="sha256:" + "0" * 64,
        patch_artifact_id=artifact.artifact_id,
        secret_scan_id=scan.scan_id,
        redaction_id=redaction.redaction_id,
        redacted_metadata_digest=redaction.output_artifact_digest,
        lineage_digest=lineage_digest,
        profile_id=profile.profile_id,
        profile_version=profile.profile_version,
        secret_scan_rule_set_id=profile.secret_scan_rule_set_id,
        redaction_rule_set_id=profile.redaction_rule_set_id,
    )
    return replace(provisional, candidate_id=candidate_id_for(provisional))


def _is_registered_profile(profile: object) -> bool:
    return profile == M4_PATCH_METADATA_SECURITY_V1


def _projection(intent: PatchIntent, artifact: PatchArtifact) -> tuple[tuple[str, str], ...]:
    return (
        ("PatchArtifact.target_scope", "\n".join(artifact.target_scope)),
        ("PatchIntent.change_description", intent.change_description),
        ("PatchIntent.target_scope", "\n".join(intent.target_scope)),
    )


def _findings(
    projection: tuple[tuple[str, str], ...], profile: MetadataSecurityProfile
) -> tuple[ScanFinding, ...]:
    values = dict(projection)
    findings: list[ScanFinding] = []
    for rule in profile.rule_definitions:
        pattern = re.compile(rule.pattern)
        for field_name in profile.allowed_field_names:
            if pattern.search(values[field_name]):
                findings.append(ScanFinding(rule_id=rule.rule_id, field_name=field_name))
    return tuple(findings)


def _redacted_projection(
    projection: tuple[tuple[str, str], ...],
    scan: SecretScanResult,
    profile: MetadataSecurityProfile,
) -> tuple[tuple[str, str], ...]:
    rule_patterns = {
        rule.rule_id: re.compile(rule.pattern) for rule in profile.rule_definitions
    }
    findings_by_field: dict[str, list[str]] = {}
    for finding in scan.findings_summary:
        findings_by_field.setdefault(finding.field_name, []).append(finding.rule_id)
    redacted: list[tuple[str, str]] = []
    for field_name, value in projection:
        replacement = value
        for rule_id in findings_by_field.get(field_name, []):
            replacement = rule_patterns[rule_id].sub(f"[REDACTED:{rule_id}]", replacement)
        redacted.append((field_name, replacement))
    return tuple(redacted)


def _scan_terminal(
    artifact: PatchArtifact,
    profile: MetadataSecurityProfile,
    result: str,
    failure_reason: str,
) -> SecretScanResult:
    provisional = SecretScanResult(
        contract_version=artifact.contract_version,
        scan_id="sha256:" + "0" * 64,
        artifact_id=artifact.artifact_id,
        rule_set_id=profile.secret_scan_rule_set_id,
        scanner_version=profile.scanner_version,
        result=result,  # type: ignore[arg-type]
        findings_summary=(),
        failure_reason=failure_reason,
    )
    return replace(provisional, scan_id=scan_id_for(provisional))


def _redaction_success(
    artifact: PatchArtifact,
    profile: MetadataSecurityProfile,
    scan: SecretScanResult,
    status: str,
    projection: tuple[tuple[str, str], ...],
) -> RedactionFact:
    provisional = RedactionFact(
        contract_version=artifact.contract_version,
        redaction_id="sha256:" + "0" * 64,
        input_artifact_id=artifact.artifact_id,
        secret_scan_id=scan.scan_id,
        output_artifact_digest="sha256:" + sha256_hex(projection),
        rule_set_id=profile.redaction_rule_set_id,
        status=status,  # type: ignore[arg-type]
    )
    return replace(provisional, redaction_id=redaction_id_for(provisional))


def _redaction_terminal(
    artifact: PatchArtifact,
    profile: MetadataSecurityProfile,
    secret_scan_id: str,
    status: str,
) -> RedactionFact:
    provisional = RedactionFact(
        contract_version=artifact.contract_version,
        redaction_id="sha256:" + "0" * 64,
        input_artifact_id=artifact.artifact_id,
        secret_scan_id=secret_scan_id,
        output_artifact_digest=None,
        rule_set_id=profile.redaction_rule_set_id,
        status=status,  # type: ignore[arg-type]
    )
    return replace(provisional, redaction_id=redaction_id_for(provisional))


def _intent_artifact_aligned(intent: PatchIntent, artifact: PatchArtifact) -> bool:
    return (
        intent.contract_version == artifact.contract_version
        and artifact.patch_intent_id == intent.intent_id
        and artifact.repository_identity == intent.repository_identity
        and artifact.base_revision == intent.base_revision
        and artifact.target_scope == intent.target_scope
    )
