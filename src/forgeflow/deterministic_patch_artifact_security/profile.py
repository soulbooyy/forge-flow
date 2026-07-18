"""Accepted M4 metadata-security profile represented as immutable data."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class MetadataSecurityProfile:
    profile_id: str
    profile_version: int
    secret_scan_rule_set_id: str
    scanner_version: str
    redaction_rule_set_id: str
    allowed_field_names: tuple[str, ...]
    ordered_rule_ids: tuple[str, ...]


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
    ordered_rule_ids=(
        "private-key-marker",
        "github-token-prefix",
        "credential-assignment",
        "jwt-like-token",
    ),
)
