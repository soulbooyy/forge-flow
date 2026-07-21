from dataclasses import dataclass
import re

SCHEMA_VERSION = "forgeflow.approval-trace-durable-summary.v1"
_DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")
_REVISION = re.compile(r"^[0-9a-f]{40}$")
_SAFE_IDENTIFIER = re.compile(r"^[a-z][a-z0-9-]{2,63}$")
_REASONS = frozenset(("sensitive_path", "stale_revision", "policy_change"))
_EVENTS = frozenset(("artifact_published", "approval_recorded", "summary_appended"))
_DETAILS = frozenset(("ok", "blocked", "approval_required"))
_STOPS = frozenset(("complete", "policy_blocked", "approval_required", "publication_failed"))


def _digest(value: object) -> None:
    if not isinstance(value, str) or not _DIGEST.fullmatch(value):
        raise ValueError("digest required")


def _schema(value: object) -> None:
    if value != SCHEMA_VERSION:
        raise ValueError("unsupported schema version")


def _safe_identifier(value: object) -> None:
    if not isinstance(value, str) or not _SAFE_IDENTIFIER.fullmatch(value):
        raise ValueError("bounded safe identifier required")


def _ordered_digests(value: object) -> None:
    if not isinstance(value, tuple) or not value:
        raise ValueError("non-empty digest tuple required")
    for item in value:
        _digest(item)
    if value != tuple(sorted(set(value))):
        raise ValueError("digest tuple must be unique and sorted")


@dataclass(frozen=True, slots=True)
class ApprovalRequest:
    schema_version: str; request_id: str; subject_contract_id: str; candidate_id: str; repository_identity: str; base_revision: str; policy_profile_id: str; policy_profile_version: int; lineage_digest: str; reason_codes: tuple[str, ...]; expires_at: int
    def __post_init__(self) -> None:
        _schema(self.schema_version)
        for value in (self.request_id, self.subject_contract_id, self.candidate_id, self.lineage_digest): _digest(value)
        _safe_identifier(self.repository_identity); _safe_identifier(self.policy_profile_id)
        if (not _REVISION.fullmatch(self.base_revision) or type(self.policy_profile_version) is not int or self.policy_profile_version <= 0 or type(self.expires_at) is not int or self.expires_at <= 0 or not isinstance(self.reason_codes, tuple) or not self.reason_codes or self.reason_codes != tuple(sorted(set(self.reason_codes))) or any(value not in _REASONS for value in self.reason_codes)):
            raise ValueError("invalid approval request")


@dataclass(frozen=True, slots=True)
class ApprovalDecision:
    schema_version: str; decision_id: str; request_id: str; lineage_digest: str; outcome: str; expires_at: int
    def __post_init__(self) -> None:
        _schema(self.schema_version)
        for value in (self.decision_id, self.request_id, self.lineage_digest): _digest(value)
        if self.outcome not in ("approved", "denied") or type(self.expires_at) is not int or self.expires_at <= 0:
            raise ValueError("invalid decision")


@dataclass(frozen=True, slots=True)
class MetadataArtifactReference:
    schema_version: str; artifact_reference_id: str; run_id: str; candidate_id: str; artifact_metadata_id: str; content_digest: str; candidate_content_digest: str; profile_id: str; profile_version: int; lineage_digest: str
    def __post_init__(self) -> None:
        _schema(self.schema_version)
        for value in (self.artifact_reference_id, self.candidate_id, self.artifact_metadata_id, self.content_digest, self.candidate_content_digest, self.lineage_digest): _digest(value)
        _safe_identifier(self.run_id); _safe_identifier(self.profile_id)
        if type(self.profile_version) is not int or self.profile_version <= 0:
            raise ValueError("invalid metadata artifact reference")


@dataclass(frozen=True, slots=True)
class TraceEvent:
    schema_version: str; event_id: str; run_id: str; event_kind: str; contract_ids: tuple[str, ...]; detail_code: str
    def __post_init__(self) -> None:
        _schema(self.schema_version); _digest(self.event_id); _safe_identifier(self.run_id); _ordered_digests(self.contract_ids)
        if self.event_kind not in _EVENTS or self.detail_code not in _DETAILS:
            raise ValueError("invalid trace event")


@dataclass(frozen=True, slots=True)
class DurableRunSummary:
    schema_version: str; summary_id: str; run_id: str; event_ids: tuple[str, ...]; artifact_reference_ids: tuple[str, ...]; policy_decision_ids: tuple[str, ...]; approval_decision_ids: tuple[str, ...]; final_stop_reason: str
    def __post_init__(self) -> None:
        _schema(self.schema_version); _digest(self.summary_id); _safe_identifier(self.run_id)
        for value in (self.event_ids, self.artifact_reference_ids, self.policy_decision_ids, self.approval_decision_ids): _ordered_digests(value)
        if self.final_stop_reason not in _STOPS:
            raise ValueError("invalid final stop")
