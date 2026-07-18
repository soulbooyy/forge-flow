"""Accepted M4 metadata-security profile represented as immutable data."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class MetadataSecurityRule:
    """One accepted, deterministic metadata detection rule."""

    rule_id: str
    pattern: str


@dataclass(frozen=True, slots=True)
class MetadataSecurityProfile:
    profile_id: str
    profile_version: int
    secret_scan_rule_set_id: str
    scanner_version: str
    redaction_rule_set_id: str
    allowed_field_names: tuple[str, ...]
    rule_definitions: tuple[MetadataSecurityRule, ...]

    @property
    def ordered_rule_ids(self) -> tuple[str, ...]:
        return tuple(rule.rule_id for rule in self.rule_definitions)


M4_PATCH_METADATA_SECURITY_V1 = MetadataSecurityProfile(
    profile_id="forgeflow-m4-patch-metadata-security",
    profile_version=1,
    secret_scan_rule_set_id="m4-patch-metadata-secret-scan-v1",
    scanner_version="deterministic-metadata-scanner-v1",
    redaction_rule_set_id="m4-patch-metadata-redaction-v1",
    allowed_field_names=(
        "PatchArtifact.target_scope",
        "PatchIntent.change_description",
        "PatchIntent.target_scope",
    ),
    rule_definitions=(
        MetadataSecurityRule(
            rule_id="private-key-marker",
            pattern=r"-----BEGIN [A-Z0-9 ]+ PRIVATE KEY-----",
        ),
        MetadataSecurityRule(
            rule_id="github-token-prefix",
            pattern=r"gh[pousr]_[A-Za-z0-9]{20,}",
        ),
        MetadataSecurityRule(
            rule_id="credential-assignment",
            pattern=(
                r"(?i)\b(?:api_key|apikey|access_token|secret|password|token)\b"
                r"\s*[:=]\s*\S{8,}"
            ),
        ),
        MetadataSecurityRule(
            rule_id="jwt-like-token",
            pattern=(
                r"eyJ[A-Za-z0-9_-]{5,}\.[A-Za-z0-9_-]{8,}\."
                r"[A-Za-z0-9_-]{8,}"
            ),
        ),
    ),
)
