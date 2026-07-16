"""Immutable contracts for metadata-only M4 patch security facts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, TypeAlias
import re


ScanResult: TypeAlias = Literal["passed", "blocked", "failed", "indeterminate"]
RedactionStatus: TypeAlias = Literal["not_needed", "redacted", "failed", "indeterminate"]

_DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")
_COMMIT_SHA = re.compile(r"^[0-9a-f]{40}$")
_FORBIDDEN_SCOPE_SEGMENTS = frozenset(("", ".", ".."))


@dataclass(frozen=True, slots=True)
class PatchIntent:
    contract_version: str
    repository_identity: str
    base_revision: str
    intent_id: str
    target_scope: tuple[str, ...]
    change_description: str
    lineage_digest: str

    def __post_init__(self) -> None:
        _require_text("contract_version", self.contract_version)
        _require_text("repository_identity", self.repository_identity)
        _require_commit_sha("base_revision", self.base_revision)
        _require_digest("intent_id", self.intent_id)
        _require_target_scope(self.target_scope)
        _require_text("change_description", self.change_description)
        _require_digest("lineage_digest", self.lineage_digest)


@dataclass(frozen=True, slots=True)
class PatchArtifact:
    contract_version: str
    artifact_id: str
    repository_identity: str
    base_revision: str
    patch_intent_id: str
    target_scope: tuple[str, ...]
    metadata_digest: str
    lineage_digest: str

    def __post_init__(self) -> None:
        _require_text("contract_version", self.contract_version)
        _require_digest("artifact_id", self.artifact_id)
        _require_text("repository_identity", self.repository_identity)
        _require_commit_sha("base_revision", self.base_revision)
        _require_digest("patch_intent_id", self.patch_intent_id)
        _require_target_scope(self.target_scope)
        _require_digest("metadata_digest", self.metadata_digest)
        _require_digest("lineage_digest", self.lineage_digest)


@dataclass(frozen=True, slots=True)
class SecretScanResult:
    contract_version: str
    scan_id: str
    artifact_id: str
    rule_set_id: str
    scanner_version: str
    result: ScanResult
    findings_summary: tuple[str, ...]
    failure_reason: str | None

    def __post_init__(self) -> None:
        _require_text("contract_version", self.contract_version)
        _require_digest("scan_id", self.scan_id)
        _require_digest("artifact_id", self.artifact_id)
        _require_text("rule_set_id", self.rule_set_id)
        _require_text("scanner_version", self.scanner_version)
        if self.result not in ("passed", "blocked", "failed", "indeterminate"):
            raise ValueError("result must be a controlled scan result")
        _require_sorted_unique_text("findings_summary", self.findings_summary)
        if self.result in ("passed", "blocked") and self.failure_reason is not None:
            raise ValueError("successful or blocked scans must not have a failure reason")
        if self.result in ("failed", "indeterminate"):
            _require_text("failure_reason", self.failure_reason)


@dataclass(frozen=True, slots=True)
class RedactionFact:
    contract_version: str
    redaction_id: str
    input_artifact_id: str
    output_artifact_digest: str | None
    rule_set_id: str
    status: RedactionStatus

    def __post_init__(self) -> None:
        _require_text("contract_version", self.contract_version)
        _require_digest("redaction_id", self.redaction_id)
        _require_digest("input_artifact_id", self.input_artifact_id)
        _require_text("rule_set_id", self.rule_set_id)
        if self.status not in ("not_needed", "redacted", "failed", "indeterminate"):
            raise ValueError("status must be a controlled redaction status")
        if self.status in ("not_needed", "redacted"):
            _require_digest("output_artifact_digest", self.output_artifact_digest)
        elif self.output_artifact_digest is not None:
            raise ValueError("failed or indeterminate redaction must not expose an output digest")


@dataclass(frozen=True, slots=True)
class RedactedArtifactReferenceCandidate:
    patch_artifact_id: str
    redacted_metadata_digest: str
    profile_id: str
    profile_version: int
    secret_scan_rule_set_id: str
    redaction_rule_set_id: str

    def __post_init__(self) -> None:
        _require_digest("patch_artifact_id", self.patch_artifact_id)
        _require_digest("redacted_metadata_digest", self.redacted_metadata_digest)
        _require_text("profile_id", self.profile_id)
        if not isinstance(self.profile_version, int) or isinstance(self.profile_version, bool):
            raise ValueError("profile_version must be an integer")
        _require_text("secret_scan_rule_set_id", self.secret_scan_rule_set_id)
        _require_text("redaction_rule_set_id", self.redaction_rule_set_id)


@dataclass(frozen=True, slots=True)
class DeterministicPatchArtifactSecurityValidationError:
    schema_version: str
    error_id: str
    error_code: str
    summary: str

    def __post_init__(self) -> None:
        _require_text("schema_version", self.schema_version)
        _require_digest("error_id", self.error_id)
        _require_text("error_code", self.error_code)
        _require_text("summary", self.summary)


def _require_digest(name: str, value: object) -> None:
    if not isinstance(value, str) or not _DIGEST.fullmatch(value):
        raise ValueError(f"{name} must be a lowercase sha256 digest")


def _require_commit_sha(name: str, value: object) -> None:
    if not isinstance(value, str) or not _COMMIT_SHA.fullmatch(value):
        raise ValueError(f"{name} must be a lowercase 40-character commit SHA")


def _require_text(name: str, value: object) -> None:
    if not isinstance(value, str) or not value or value != value.strip() or "\x00" in value:
        raise ValueError(f"{name} must be non-empty safe text")


def _require_target_scope(value: object) -> None:
    if not isinstance(value, tuple) or not value:
        raise ValueError("target_scope must be a non-empty tuple")
    if any(not isinstance(path, str) or not path or path.startswith("/") for path in value):
        raise ValueError("target_scope must contain workspace-relative paths")
    if any(_FORBIDDEN_SCOPE_SEGMENTS & set(path.split("/")) for path in value):
        raise ValueError("target_scope must not escape its logical scope")
    if value != tuple(sorted(set(value))):
        raise ValueError("target_scope must be sorted and unique")


def _require_sorted_unique_text(name: str, value: object) -> None:
    if not isinstance(value, tuple) or any(not isinstance(item, str) or not item for item in value):
        raise ValueError(f"{name} must be a tuple of non-empty text")
    if value != tuple(sorted(set(value))):
        raise ValueError(f"{name} must be sorted and unique")
