"""Immutable, payload-free M4 materialization contracts."""

from __future__ import annotations

from dataclasses import MISSING, dataclass
import re
from typing import Literal, TypeAlias


_DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")
_BASE_SHA = re.compile(r"^[0-9a-f]{40}$")
_IDENTIFIER = re.compile(r"^[a-z0-9][a-z0-9_-]{0,127}$")
_PROFILE = ("forgeflow-m4-fixture-only", "1.0.0")
_TERMINALS = frozenset((
    "source_revalidation_failed", "materialization_not_authorized", "materialization_failed",
    "validation_failed", "validation_infrastructure_failed", "payload_not_eligible",
    "simulation_binding_failed", "real_mutation_rejected",
))
AuthorityKind: TypeAlias = Literal["materialization", "payload_eligibility", "real_mutation"]
MaterializationTerminalReason: TypeAlias = Literal[
    "source_revalidation_failed", "materialization_not_authorized", "materialization_failed",
    "validation_failed", "validation_infrastructure_failed", "payload_not_eligible",
    "simulation_binding_failed", "real_mutation_rejected",
]
_TERMINAL_CLASSIFICATIONS = {
    "source_revalidation_failed": frozenset(("snapshot_mismatch", "target_digest_mismatch", "input_digest_mismatch")),
    "materialization_not_authorized": frozenset(("pdr_missing", "pdr_expired", "pdr_scope_mismatch")),
    "materialization_failed": frozenset(("transformer_failed", "sandbox_output_invalid", "output_digest_mismatch", "security_blocked")),
    "validation_failed": frozenset(("assertion_failed",)),
    "validation_infrastructure_failed": frozenset(("runner_unavailable", "image_unavailable", "profile_proof_missing")),
    "payload_not_eligible": frozenset(("pdr_missing", "pdr_expired", "pdr_scope_mismatch")),
    "simulation_binding_failed": frozenset(("handle_expired", "payload_mismatch", "pdr_scope_mismatch")),
    "real_mutation_rejected": frozenset(("simulation_identity", "v1_authority")),
}


def _digest(name: str, value: str) -> None:
    if not isinstance(value, str) or not _DIGEST.fullmatch(value):
        raise ValueError(f"{name} must be sha256:<lowercase-hex>")


def _identifier(name: str, value: str) -> None:
    if not isinstance(value, str) or not _IDENTIFIER.fullmatch(value):
        raise ValueError(f"{name} must be a controlled identifier")


def _ordered_digests(name: str, values: tuple[str, ...]) -> None:
    if not isinstance(values, tuple) or values != tuple(sorted(set(values))):
        raise ValueError(f"{name} must be a sorted unique tuple")
    for value in values:
        _digest(name, value)


def _unvalidated(cls: type[object], values: dict[str, object]) -> object:
    """Build a temporary self-identification value without accepting it publicly."""
    value = object.__new__(cls)
    for name, field in cls.__dataclass_fields__.items():  # type: ignore[attr-defined]
        if name in values:
            item = values[name]
        elif field.default is not MISSING:
            item = field.default
        else:
            raise TypeError(f"missing required field: {name}")
        object.__setattr__(value, name, item)
    return value


@dataclass(frozen=True, slots=True)
class TransformationManifest:
    transformation_id: str
    transformation_version: str
    target_file_id: str
    expected_input_digest: str

    def __post_init__(self) -> None:
        _identifier("transformation_id", self.transformation_id)
        _identifier("transformation_version", self.transformation_version)
        _identifier("target_file_id", self.target_file_id)
        _digest("expected_input_digest", self.expected_input_digest)


@dataclass(frozen=True, slots=True)
class MaterializationPDR:
    pdr_id: str
    authority_kind: Literal["materialization"]
    attempt_id: str
    issued_at: int
    expires_at: int
    repository_id: str
    base_sha: str
    snapshot_digest: str
    transformation_id: str
    transformation_version: str
    target_file_id: str
    expected_input_digest: str
    profile_id: str
    profile_version: str

    @classmethod
    def create(cls, **values: object) -> "MaterializationPDR":
        draft = _unvalidated(cls, {**values, "pdr_id": "sha256:" + "0" * 64, "authority_kind": "materialization"})
        from .canonical import materialization_pdr_id_for
        return cls(**{**values, "pdr_id": materialization_pdr_id_for(draft), "authority_kind": "materialization"})  # type: ignore[arg-type]

    def is_fresh_at(self, now: int) -> bool:
        return self.issued_at <= now < self.expires_at

    def __post_init__(self) -> None:
        _digest("pdr_id", self.pdr_id)
        if self.authority_kind != "materialization":
            raise ValueError("MaterializationPDR authority_kind must be materialization")
        _identifier("attempt_id", self.attempt_id)
        if type(self.issued_at) is not int or type(self.expires_at) is not int or self.expires_at <= self.issued_at:
            raise ValueError("PDR lifetime must be a positive integer interval")
        _identifier("repository_id", self.repository_id)
        if not _BASE_SHA.fullmatch(self.base_sha):
            raise ValueError("base_sha must be a locked lowercase SHA")
        _digest("snapshot_digest", self.snapshot_digest)
        _identifier("transformation_id", self.transformation_id)
        _identifier("transformation_version", self.transformation_version)
        _identifier("target_file_id", self.target_file_id)
        _digest("expected_input_digest", self.expected_input_digest)
        if (self.profile_id, self.profile_version) != _PROFILE:
            raise ValueError("PDR must reuse the exact M4 fixture profile reference")
        from .canonical import materialization_pdr_id_for
        if self.pdr_id != materialization_pdr_id_for(self):
            raise ValueError("MaterializationPDR ID must match canonical payload")


@dataclass(frozen=True, slots=True)
class MaterializedCommitPayload:
    payload_id: str
    repository_id: str
    base_sha: str
    snapshot_digest: str
    transformation_id: str
    transformation_version: str
    target_file_id: str
    input_digest: str
    output_digest: str
    materialization_pdr_id: str
    security_fact_ids: tuple[str, ...]
    validation_fact_id: str
    review_fact_ids: tuple[str, ...]

    @classmethod
    def create(cls, **values: object) -> "MaterializedCommitPayload":
        draft = _unvalidated(cls, {**values, "payload_id": "sha256:" + "0" * 64})
        from .canonical import materialized_payload_id_for
        return cls(**{**values, "payload_id": materialized_payload_id_for(draft)})  # type: ignore[arg-type]

    def __post_init__(self) -> None:
        for name in ("payload_id", "snapshot_digest", "input_digest", "output_digest", "materialization_pdr_id", "validation_fact_id"):
            _digest(name, getattr(self, name))
        _identifier("repository_id", self.repository_id)
        if not _BASE_SHA.fullmatch(self.base_sha):
            raise ValueError("base_sha must be a locked lowercase SHA")
        _identifier("transformation_id", self.transformation_id)
        _identifier("transformation_version", self.transformation_version)
        _identifier("target_file_id", self.target_file_id)
        _ordered_digests("security_fact_ids", self.security_fact_ids)
        _ordered_digests("review_fact_ids", self.review_fact_ids)
        from .canonical import materialized_payload_id_for
        if self.payload_id != materialized_payload_id_for(self):
            raise ValueError("MaterializedCommitPayload ID must match canonical payload")


@dataclass(frozen=True, slots=True)
class PayloadEligibilityPDR:
    pdr_id: str
    authority_kind: Literal["payload_eligibility"]
    attempt_id: str
    issued_at: int
    expires_at: int
    repository_id: str
    base_sha: str
    payload_id: str
    output_digest: str
    security_fact_ids: tuple[str, ...]
    validation_fact_id: str
    review_fact_ids: tuple[str, ...]
    materialization_pdr_id: str

    @classmethod
    def create(cls, **values: object) -> "PayloadEligibilityPDR":
        draft = _unvalidated(cls, {**values, "pdr_id": "sha256:" + "0" * 64, "authority_kind": "payload_eligibility"})
        from .canonical import payload_eligibility_pdr_id_for
        return cls(**{**values, "pdr_id": payload_eligibility_pdr_id_for(draft), "authority_kind": "payload_eligibility"})  # type: ignore[arg-type]

    def is_fresh_at(self, now: int) -> bool:
        return self.issued_at <= now < self.expires_at

    def __post_init__(self) -> None:
        _digest("pdr_id", self.pdr_id)
        if self.authority_kind != "payload_eligibility":
            raise ValueError("PayloadEligibilityPDR authority_kind must be payload_eligibility")
        _identifier("attempt_id", self.attempt_id)
        if type(self.issued_at) is not int or type(self.expires_at) is not int or self.expires_at <= self.issued_at:
            raise ValueError("PDR lifetime must be a positive integer interval")
        _identifier("repository_id", self.repository_id)
        if not _BASE_SHA.fullmatch(self.base_sha):
            raise ValueError("base_sha must be a locked lowercase SHA")
        for name in ("payload_id", "output_digest", "validation_fact_id", "materialization_pdr_id"):
            _digest(name, getattr(self, name))
        _ordered_digests("security_fact_ids", self.security_fact_ids)
        _ordered_digests("review_fact_ids", self.review_fact_ids)
        from .canonical import payload_eligibility_pdr_id_for
        if self.pdr_id != payload_eligibility_pdr_id_for(self):
            raise ValueError("PayloadEligibilityPDR ID must match canonical payload")


@dataclass(frozen=True, slots=True)
class MaterializationTerminal:
    terminal_id: str
    reason: MaterializationTerminalReason
    attempt_id: str
    repository_id: str | None
    base_sha: str | None
    profile_id: str | None
    profile_version: str | None
    classification: str
    automatic_retries: Literal[0] = 0
    related_ids: tuple[str, ...] = ()
    rejected_identity_class: str | None = None

    @classmethod
    def create(cls, **values: object) -> "MaterializationTerminal":
        draft = _unvalidated(cls, {**values, "terminal_id": "sha256:" + "0" * 64})
        from .canonical import terminal_id_for
        return cls(**{**values, "terminal_id": terminal_id_for(draft)})  # type: ignore[arg-type]

    def __post_init__(self) -> None:
        _digest("terminal_id", self.terminal_id)
        if self.reason not in _TERMINALS:
            raise ValueError("reason must be a controlled terminal")
        _identifier("attempt_id", self.attempt_id)
        if (self.repository_id is None) != (self.base_sha is None):
            raise ValueError("terminal repository identity must be complete or absent")
        if self.repository_id is not None:
            _identifier("repository_id", self.repository_id)
            if not _BASE_SHA.fullmatch(self.base_sha or ""):
                raise ValueError("base_sha must be a locked lowercase SHA")
        if (self.profile_id is None) != (self.profile_version is None):
            raise ValueError("terminal profile reference must be complete or absent")
        if self.profile_id is not None and (self.profile_id, self.profile_version) != _PROFILE:
            raise ValueError("terminal profile reference must use M4 fixture profile")
        if self.classification not in _TERMINAL_CLASSIFICATIONS[self.reason]:
            raise ValueError("classification must be registered for the terminal")
        if self.automatic_retries != 0:
            raise ValueError("automatic retries are always zero")
        _ordered_digests("related_ids", self.related_ids)
        if self.reason == "real_mutation_rejected":
            if self.rejected_identity_class not in ("simulation_identity", "materialization_pdr", "payload_eligibility_pdr"):
                raise ValueError("real mutation rejection requires a controlled identity class")
            if self.repository_id is not None or self.profile_id is not None:
                raise ValueError("real mutation terminal must not retain source or profile identity")
        elif self.rejected_identity_class is not None:
            raise ValueError("only real mutation rejection may retain rejected identity class")
        from .canonical import terminal_id_for
        if self.terminal_id != terminal_id_for(self):
            raise ValueError("MaterializationTerminal ID must match canonical payload")


_HANDLE_MINT_CAPABILITY = object()


class EphemeralPayloadHandle:
    """A deliberately non-serializable, harness-private liveness token."""

    __slots__ = ("_token", "_live")

    def __init__(self, capability: object, token: object) -> None:
        if capability is not _HANDLE_MINT_CAPABILITY or type(token) is not object:
            raise TypeError("EphemeralPayloadHandle can only be minted by the harness")
        self._token = token
        self._live = True

    @property
    def is_live(self) -> bool:
        return self._live

    def destroy(self) -> None:
        self._live = False
        self._token = None

    def __getstate__(self) -> object:
        raise TypeError("EphemeralPayloadHandle cannot be serialized")

    def __reduce__(self) -> object:
        raise TypeError("EphemeralPayloadHandle cannot be serialized")


def _mint_ephemeral_handle() -> EphemeralPayloadHandle:
    """Private harness seam; no durable contract exposes this capability."""
    return EphemeralPayloadHandle(_HANDLE_MINT_CAPABILITY, object())
