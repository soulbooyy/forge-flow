"""Immutable contracts for metadata-only M4 patch security facts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, TypeAlias
import re
import unicodedata

from .profile import M4_PATCH_METADATA_SECURITY_V1


ScanResult: TypeAlias = Literal["passed", "blocked", "failed", "indeterminate"]
RedactionStatus: TypeAlias = Literal["not_needed", "redacted", "failed", "indeterminate"]

_DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")
_COMMIT_SHA = re.compile(r"^[0-9a-f]{40}$")
_FORBIDDEN_SCOPE_SEGMENTS = frozenset(("", ".", ".."))
_MAX_TARGET_SCOPE_ENTRIES = 10
_MAX_TARGET_SCOPE_PATH_CHARS = 512
_MAX_CHANGE_DESCRIPTION_CHARS = 1_000
_SAFE_FAILURE_REASONS = {
    "failed": ("scanner_operation_failed",),
    "indeterminate": ("metadata_projection_invalid", "security_profile_mismatch"),
}
_SAFE_ERROR_SUMMARIES = (
    "metadata security input is invalid",
    "metadata security profile is invalid",
)
_SAFE_ERROR_CODES = frozenset(("invalid_patch_security_input", "metadata_construction_invalid"))
_CONTRACT_VERSION = "m4-patch-artifact-security/v1"
_REPOSITORY_IDENTITY = "fixture-repository-1300511729"
_BASE_REVISION = "97c8220cd713ebf61124ac2de2f3eadc6e4dc222"


@dataclass(frozen=True, slots=True)
class ScanFinding:
    """A controlled rule/field fact that never carries matched text."""

    rule_id: str
    field_name: str

    def __post_init__(self) -> None:
        if self.rule_id not in M4_PATCH_METADATA_SECURITY_V1.ordered_rule_ids:
            raise ValueError("rule_id must be registered")
        if self.field_name not in M4_PATCH_METADATA_SECURITY_V1.allowed_field_names:
            raise ValueError("field_name must be allowlisted")


@dataclass(frozen=True, slots=True)
class PreScanPatchMetadataIdentity:
    """Non-persistent, payload-free identity for transient security processing."""

    contract_version: str
    pre_scan_metadata_id: str
    repository_identity: str
    base_revision: str
    target_scope: tuple[str, ...]
    lineage_digest: str

    def __post_init__(self) -> None:
        _require_known("contract_version", self.contract_version, _CONTRACT_VERSION)
        _require_digest("pre_scan_metadata_id", self.pre_scan_metadata_id)
        _require_known("repository_identity", self.repository_identity, _REPOSITORY_IDENTITY)
        _require_known("base_revision", self.base_revision, _BASE_REVISION)
        _require_target_scope(self.target_scope)
        _require_digest("lineage_digest", self.lineage_digest)


@dataclass(frozen=True, slots=True)
class PatchIntent:
    contract_version: str
    repository_identity: str
    base_revision: str
    intent_id: str
    pre_scan_metadata_id: str
    target_scope: tuple[str, ...]
    scanned_metadata_digest: str
    lineage_digest: str

    def __post_init__(self) -> None:
        _require_known("contract_version", self.contract_version, _CONTRACT_VERSION)
        _require_known("repository_identity", self.repository_identity, _REPOSITORY_IDENTITY)
        _require_known("base_revision", self.base_revision, _BASE_REVISION)
        _require_digest("intent_id", self.intent_id)
        _require_digest("pre_scan_metadata_id", self.pre_scan_metadata_id)
        _require_target_scope(self.target_scope)
        _require_digest("scanned_metadata_digest", self.scanned_metadata_digest)
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
        _require_known("contract_version", self.contract_version, _CONTRACT_VERSION)
        _require_digest("artifact_id", self.artifact_id)
        _require_known("repository_identity", self.repository_identity, _REPOSITORY_IDENTITY)
        _require_known("base_revision", self.base_revision, _BASE_REVISION)
        _require_digest("patch_intent_id", self.patch_intent_id)
        _require_target_scope(self.target_scope)
        _require_digest("metadata_digest", self.metadata_digest)
        _require_digest("lineage_digest", self.lineage_digest)


@dataclass(frozen=True, slots=True)
class SecretScanResult:
    contract_version: str
    scan_id: str
    pre_scan_metadata_id: str
    rule_set_id: str
    scanner_version: str
    result: ScanResult
    findings_summary: tuple[ScanFinding, ...]
    failure_reason: str | None

    def __post_init__(self) -> None:
        _require_known("contract_version", self.contract_version, _CONTRACT_VERSION)
        _require_digest("scan_id", self.scan_id)
        _require_digest("pre_scan_metadata_id", self.pre_scan_metadata_id)
        _require_known("rule_set_id", self.rule_set_id, M4_PATCH_METADATA_SECURITY_V1.secret_scan_rule_set_id)
        _require_known("scanner_version", self.scanner_version, M4_PATCH_METADATA_SECURITY_V1.scanner_version)
        if self.result not in ("passed", "blocked", "failed", "indeterminate"):
            raise ValueError("result must be a controlled scan result")
        _require_sorted_unique_findings(self.findings_summary)
        if self.result == "passed" and self.findings_summary:
            raise ValueError("passed scans must not contain findings")
        if self.result == "blocked" and not self.findings_summary:
            raise ValueError("blocked scans must contain findings")
        if self.result in ("failed", "indeterminate") and self.findings_summary:
            raise ValueError("failed or indeterminate scans must not contain findings")
        if self.result in ("passed", "blocked") and self.failure_reason is not None:
            raise ValueError("successful or blocked scans must not have a failure reason")
        if self.result in ("failed", "indeterminate"):
            if self.failure_reason not in _SAFE_FAILURE_REASONS[self.result]:
                raise ValueError("failure_reason must be a controlled safe code")


@dataclass(frozen=True, slots=True)
class RedactionFact:
    contract_version: str
    redaction_id: str
    input_pre_scan_metadata_id: str
    secret_scan_id: str
    output_metadata_digest: str | None
    rule_set_id: str
    status: RedactionStatus

    def __post_init__(self) -> None:
        _require_known("contract_version", self.contract_version, _CONTRACT_VERSION)
        _require_digest("redaction_id", self.redaction_id)
        _require_digest("input_pre_scan_metadata_id", self.input_pre_scan_metadata_id)
        _require_digest("secret_scan_id", self.secret_scan_id)
        _require_known("rule_set_id", self.rule_set_id, M4_PATCH_METADATA_SECURITY_V1.redaction_rule_set_id)
        if self.status not in ("not_needed", "redacted", "failed", "indeterminate"):
            raise ValueError("status must be a controlled redaction status")
        if self.status in ("not_needed", "redacted"):
            _require_digest("output_metadata_digest", self.output_metadata_digest)
        elif self.output_metadata_digest is not None:
            raise ValueError("failed or indeterminate redaction must not expose an output digest")


TerminalStatus: TypeAlias = Literal["blocked", "failed", "indeterminate"]
TerminalReason: TypeAlias = Literal[
    "security_rule_blocked",
    "scanner_operation_failed",
    "redaction_operation_failed",
    "metadata_projection_invalid",
    "security_profile_mismatch",
]
_TERMINAL_REASONS = {
    "blocked": ("security_rule_blocked",),
    "failed": ("scanner_operation_failed", "redaction_operation_failed"),
    "indeterminate": ("metadata_projection_invalid", "security_profile_mismatch"),
}


@dataclass(frozen=True, slots=True)
class PatchSecurityTerminal:
    """Payload-free unsafe terminal; it grants no authority of any kind."""

    contract_version: str
    terminal_id: str
    pre_scan_metadata_id: str
    lineage_digest: str
    secret_scan_result: SecretScanResult
    redaction_fact: RedactionFact
    terminal_status: TerminalStatus
    terminal_reason: TerminalReason

    def __post_init__(self) -> None:
        _require_known("contract_version", self.contract_version, _CONTRACT_VERSION)
        _require_digest("terminal_id", self.terminal_id)
        _require_digest("pre_scan_metadata_id", self.pre_scan_metadata_id)
        _require_digest("lineage_digest", self.lineage_digest)
        if not isinstance(self.secret_scan_result, SecretScanResult):
            raise ValueError("secret_scan_result must be a scoped security fact")
        if not isinstance(self.redaction_fact, RedactionFact):
            raise ValueError("redaction_fact must be a scoped security fact")
        if self.secret_scan_result.pre_scan_metadata_id != self.pre_scan_metadata_id:
            raise ValueError("secret_scan_result must bind the terminal pre-scan identity")
        if self.redaction_fact.input_pre_scan_metadata_id != self.pre_scan_metadata_id:
            raise ValueError("redaction_fact must bind the terminal pre-scan identity")
        if self.redaction_fact.secret_scan_id != self.secret_scan_result.scan_id:
            raise ValueError("redaction_fact must bind the terminal scan")
        if (
            self.redaction_fact.status == "not_needed"
            and self.secret_scan_result.result != "passed"
        ):
            raise ValueError("not-needed redaction requires a passed scan")
        if self.terminal_status not in _TERMINAL_REASONS:
            raise ValueError("terminal_status must be an unsafe security status")
        if self.terminal_reason not in _TERMINAL_REASONS[self.terminal_status]:
            raise ValueError("terminal_reason must match terminal_status")
        if (
            self.terminal_status == "blocked"
            and self.secret_scan_result.result != "blocked"
        ):
            raise ValueError("blocked terminal must bind a blocked scan")
        if (
            self.terminal_reason == "scanner_operation_failed"
            and (
                self.secret_scan_result.result != "failed"
                or self.secret_scan_result.failure_reason != "scanner_operation_failed"
            )
        ):
            raise ValueError("scanner failure terminal must bind a failed scan")
        if (
            self.terminal_reason == "redaction_operation_failed"
            and self.redaction_fact.status != "failed"
        ):
            raise ValueError("redaction failure terminal must bind failed redaction")
        if self.terminal_status == "indeterminate":
            scan_proves_reason = (
                self.secret_scan_result.result == "indeterminate"
                and self.secret_scan_result.failure_reason == self.terminal_reason
            )
            if not scan_proves_reason and self.redaction_fact.status != "indeterminate":
                raise ValueError("indeterminate terminal must bind an indeterminate security fact")


@dataclass(frozen=True, slots=True)
class RedactedArtifactReferenceCandidate:
    contract_version: str
    candidate_id: str
    patch_artifact_id: str
    pre_scan_metadata_id: str
    secret_scan_id: str
    redaction_id: str
    redacted_metadata_digest: str
    lineage_digest: str
    profile_id: str
    profile_version: int
    secret_scan_rule_set_id: str
    redaction_rule_set_id: str

    def __post_init__(self) -> None:
        _require_known("contract_version", self.contract_version, _CONTRACT_VERSION)
        _require_digest("candidate_id", self.candidate_id)
        _require_digest("patch_artifact_id", self.patch_artifact_id)
        _require_digest("pre_scan_metadata_id", self.pre_scan_metadata_id)
        _require_digest("secret_scan_id", self.secret_scan_id)
        _require_digest("redaction_id", self.redaction_id)
        _require_digest("redacted_metadata_digest", self.redacted_metadata_digest)
        _require_digest("lineage_digest", self.lineage_digest)
        _require_known("profile_id", self.profile_id, M4_PATCH_METADATA_SECURITY_V1.profile_id)
        if (not isinstance(self.profile_version, int) or isinstance(self.profile_version, bool) or self.profile_version != M4_PATCH_METADATA_SECURITY_V1.profile_version):
            raise ValueError("profile_version must be the registered profile version")
        _require_known("secret_scan_rule_set_id", self.secret_scan_rule_set_id, M4_PATCH_METADATA_SECURITY_V1.secret_scan_rule_set_id)
        _require_known("redaction_rule_set_id", self.redaction_rule_set_id, M4_PATCH_METADATA_SECURITY_V1.redaction_rule_set_id)


@dataclass(frozen=True, slots=True)
class DeterministicPatchArtifactSecurityValidationError:
    schema_version: str
    error_id: str
    error_code: str
    summary: str

    def __post_init__(self) -> None:
        _require_known("schema_version", self.schema_version, _CONTRACT_VERSION)
        _require_digest("error_id", self.error_id)
        if self.error_code not in _SAFE_ERROR_CODES:
            raise ValueError("error_code must be a controlled safe code")
        if self.summary not in _SAFE_ERROR_SUMMARIES:
            raise ValueError("summary must be a controlled safe template")


def _require_digest(name: str, value: object) -> None:
    if not isinstance(value, str) or not _DIGEST.fullmatch(value):
        raise ValueError(f"{name} must be a lowercase sha256 digest")


def _require_commit_sha(name: str, value: object) -> None:
    if not isinstance(value, str) or not _COMMIT_SHA.fullmatch(value):
        raise ValueError(f"{name} must be a lowercase 40-character commit SHA")


def _require_text(name: str, value: object) -> None:
    if not isinstance(value, str) or not value or value != value.strip() or "\x00" in value:
        raise ValueError(f"{name} must be non-empty safe text")


def _require_known(name: str, value: object, expected: str) -> None:
    if value != expected:
        raise ValueError(f"{name} must be the registered value")


def _require_metadata_text(name: str, value: object, maximum: int) -> None:
    _require_text(name, value)
    if (
        not isinstance(value, str)
        or "\n" in value
        or "\r" in value
        or len(value) > maximum
        or any(unicodedata.category(character).startswith("C") for character in value)
    ):
        raise ValueError(f"{name} must be bounded single-line metadata text")


def _require_target_scope(value: object) -> None:
    if not isinstance(value, tuple) or not value:
        raise ValueError("target_scope must be a non-empty tuple")
    if len(value) > _MAX_TARGET_SCOPE_ENTRIES:
        raise ValueError("target_scope exceeds the registered changed-file limit")
    if any(
        not isinstance(path, str)
        or not path
        or path.startswith("/")
        or "\\" in path
        or bool(re.match(r"^[A-Za-z]:", path))
        or len(path) > _MAX_TARGET_SCOPE_PATH_CHARS
        or any(unicodedata.category(character).startswith("C") for character in path)
        for path in value
    ):
        raise ValueError("target_scope must contain workspace-relative paths")
    if any(_FORBIDDEN_SCOPE_SEGMENTS & set(path.split("/")) for path in value):
        raise ValueError("target_scope must not escape its logical scope")
    if value != tuple(sorted(set(value))):
        raise ValueError("target_scope must be sorted and unique")


def _require_sorted_unique_findings(value: object) -> None:
    if not isinstance(value, tuple) or any(not isinstance(item, ScanFinding) for item in value):
        raise ValueError("findings_summary must be a tuple of controlled findings")
    rule_rank = {
        rule_id: index
        for index, rule_id in enumerate(M4_PATCH_METADATA_SECURITY_V1.ordered_rule_ids)
    }
    if value != tuple(
        sorted(set(value), key=lambda item: (rule_rank[item.rule_id], item.field_name))
    ):
        raise ValueError("findings_summary must be sorted and unique")
