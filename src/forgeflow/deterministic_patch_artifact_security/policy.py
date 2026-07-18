"""Pure security facts over a bounded, transient pre-scan projection."""

from __future__ import annotations

from dataclasses import replace
import re
import unicodedata

from .canonical import (
    pre_scan_metadata_id_for,
    redaction_id_for,
    scan_id_for,
    sha256_hex,
)
from .models import (
    PreScanPatchMetadataIdentity,
    RedactedArtifactReferenceCandidate,
    RedactionFact,
    ScanFinding,
    SecretScanResult,
)
from .profile import M4_PATCH_METADATA_SECURITY_V1, MetadataSecurityProfile


Projection = tuple[tuple[str, str], ...]


def scan_metadata(
    identity: PreScanPatchMetadataIdentity,
    projection: object,
    profile: MetadataSecurityProfile,
) -> SecretScanResult:
    """Produce a scan fact without retaining or returning the projection."""
    if not _is_registered_profile(profile):
        return _scan_terminal(identity, "indeterminate", "security_profile_mismatch")
    if not _valid_identity(identity) or not _valid_projection(identity, projection, profile):
        return _scan_terminal(identity, "indeterminate", "metadata_projection_invalid")

    valid_projection = projection  # narrowed by _valid_projection
    findings = _findings(valid_projection, profile)
    provisional = SecretScanResult(
        contract_version=identity.contract_version,
        scan_id="sha256:" + "0" * 64,
        pre_scan_metadata_id=identity.pre_scan_metadata_id,
        rule_set_id=profile.secret_scan_rule_set_id,
        scanner_version=profile.scanner_version,
        result="blocked" if findings else "passed",
        findings_summary=findings,
        failure_reason=None,
    )
    return replace(provisional, scan_id=scan_id_for(provisional))


def redact_metadata(
    identity: PreScanPatchMetadataIdentity,
    projection: object,
    scan: SecretScanResult,
    profile: MetadataSecurityProfile,
) -> RedactionFact:
    """Produce a digest-only redaction fact for an exact scan/projection pair."""
    if not _is_registered_profile(profile):
        return _redaction_terminal(identity, scan.scan_id, "indeterminate")
    if not _valid_identity(identity) or not _valid_projection(identity, projection, profile):
        return _redaction_terminal(identity, scan.scan_id, "indeterminate")
    expected = scan_metadata(identity, projection, profile)
    if scan != expected:
        return _redaction_terminal(identity, scan.scan_id, "indeterminate")
    if scan.result == "failed":
        return _redaction_terminal(identity, scan.scan_id, "failed")
    if scan.result == "indeterminate":
        return _redaction_terminal(identity, scan.scan_id, "indeterminate")

    valid_projection = projection  # narrowed by _valid_projection
    if scan.result == "passed":
        return _redaction_success(identity, scan, profile, "not_needed", valid_projection)
    return _redaction_success(
        identity,
        scan,
        profile,
        "redacted",
        _redacted_projection(valid_projection, scan, profile),
    )


def candidate_for(*_args: object) -> RedactedArtifactReferenceCandidate | None:
    """Phase 2 deliberately cannot create a candidate; Phase 3 owns that path."""
    return None


def _is_registered_profile(profile: object) -> bool:
    return profile == M4_PATCH_METADATA_SECURITY_V1


def _valid_identity(value: object) -> bool:
    return (
        isinstance(value, PreScanPatchMetadataIdentity)
        and value.pre_scan_metadata_id == pre_scan_metadata_id_for(value)
    )


def _valid_projection(
    identity: PreScanPatchMetadataIdentity,
    projection: object,
    profile: MetadataSecurityProfile,
) -> bool:
    if not isinstance(projection, tuple) or len(projection) != len(profile.allowed_field_names):
        return False
    if any(
        not isinstance(item, tuple)
        or len(item) != 2
        or not isinstance(item[0], str)
        or not isinstance(item[1], str)
        for item in projection
    ):
        return False
    fields = tuple(name for name, _ in projection)
    if fields != profile.allowed_field_names:
        return False
    values = dict(projection)
    description = values["PreScanMetadataProjection.change_description"]
    scope = values["PreScanMetadataProjection.target_scope"]
    return (
        bool(description)
        and description == description.strip()
        and "\n" not in description
        and "\r" not in description
        and len(description) <= 1_000
        and not any(unicodedata.category(character).startswith("C") for character in description)
        and scope == "\n".join(identity.target_scope)
    )


def _findings(projection: Projection, profile: MetadataSecurityProfile) -> tuple[ScanFinding, ...]:
    values = dict(projection)
    findings: list[ScanFinding] = []
    for rule in profile.rule_definitions:
        pattern = re.compile(rule.pattern)
        for field_name in profile.allowed_field_names:
            if pattern.search(values[field_name]):
                findings.append(ScanFinding(rule_id=rule.rule_id, field_name=field_name))
    return tuple(findings)


def _redacted_projection(
    projection: Projection,
    scan: SecretScanResult,
    profile: MetadataSecurityProfile,
) -> Projection:
    rule_patterns = {rule.rule_id: re.compile(rule.pattern) for rule in profile.rule_definitions}
    finding_rules = {finding.rule_id for finding in scan.findings_summary}
    redacted: list[tuple[str, str]] = []
    for field_name, value in projection:
        replacements: list[tuple[int, int, str]] = []
        for rule in profile.rule_definitions:
            if rule.rule_id not in finding_rules:
                continue
            for match in rule_patterns[rule.rule_id].finditer(value):
                start, end = match.span()
                if any(start < prior_end and end > prior_start for prior_start, prior_end, _ in replacements):
                    continue
                replacements.append((start, end, rule.rule_id))
        replacements.sort(key=lambda item: item[0])
        redacted.append((field_name, _replace_spans(value, replacements)))
    return tuple(redacted)


def _replace_spans(value: str, replacements: list[tuple[int, int, str]]) -> str:
    parts: list[str] = []
    cursor = 0
    for start, end, rule_id in replacements:
        parts.extend((value[cursor:start], f"[REDACTED:{rule_id}]"))
        cursor = end
    parts.append(value[cursor:])
    return "".join(parts)


def _scan_terminal(
    identity: PreScanPatchMetadataIdentity,
    result: str,
    failure_reason: str,
) -> SecretScanResult:
    provisional = SecretScanResult(
        contract_version=identity.contract_version,
        scan_id="sha256:" + "0" * 64,
        pre_scan_metadata_id=identity.pre_scan_metadata_id,
        rule_set_id=M4_PATCH_METADATA_SECURITY_V1.secret_scan_rule_set_id,
        scanner_version=M4_PATCH_METADATA_SECURITY_V1.scanner_version,
        result=result,  # type: ignore[arg-type]
        findings_summary=(),
        failure_reason=failure_reason,
    )
    return replace(provisional, scan_id=scan_id_for(provisional))


def _redaction_success(
    identity: PreScanPatchMetadataIdentity,
    scan: SecretScanResult,
    profile: MetadataSecurityProfile,
    status: str,
    projection: Projection,
) -> RedactionFact:
    provisional = RedactionFact(
        contract_version=identity.contract_version,
        redaction_id="sha256:" + "0" * 64,
        input_pre_scan_metadata_id=identity.pre_scan_metadata_id,
        secret_scan_id=scan.scan_id,
        output_metadata_digest="sha256:" + sha256_hex(projection),
        rule_set_id=profile.redaction_rule_set_id,
        status=status,  # type: ignore[arg-type]
    )
    return replace(provisional, redaction_id=redaction_id_for(provisional))


def _redaction_terminal(
    identity: PreScanPatchMetadataIdentity,
    secret_scan_id: str,
    status: str,
) -> RedactionFact:
    provisional = RedactionFact(
        contract_version=identity.contract_version,
        redaction_id="sha256:" + "0" * 64,
        input_pre_scan_metadata_id=identity.pre_scan_metadata_id,
        secret_scan_id=secret_scan_id,
        output_metadata_digest=None,
        rule_set_id=M4_PATCH_METADATA_SECURITY_V1.redaction_rule_set_id,
        status=status,  # type: ignore[arg-type]
    )
    return replace(provisional, redaction_id=redaction_id_for(provisional))
