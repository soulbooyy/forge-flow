"""Independent future real-mutation contracts; no v1 authority imports."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json
import re

_DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")
_SHA = re.compile(r"^[0-9a-f]{40}$")
_REPOSITORY = "1300511729"
_BASE = "97c8220cd713ebf61124ac2de2f3eadc6e4dc222"
_ATTEMPT = re.compile(r"^[a-z0-9][a-z0-9_-]{0,127}$")


def _digest(value: str) -> None:
    if not isinstance(value, str) or not _DIGEST.fullmatch(value):
        raise ValueError("identity must be a sha256 digest")


def _id(value: object, omit: str) -> str:
    data = {field.name: getattr(value, field.name) for field in fields(value) if field.name != omit}
    return "sha256:" + hashlib.sha256(json.dumps(data, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


@dataclass(frozen=True, slots=True)
class RealMutationPDR:
    pdr_id: str
    authority_kind: str
    attempt_id: str
    issued_at: int
    expires_at: int
    repository_id: str
    base_sha: str
    payload_id: str
    payload_digest: str
    idempotency_key: str

    @classmethod
    def create(cls, **values: object) -> "RealMutationPDR":
        draft = object.__new__(cls)
        for name, value in {**values, "pdr_id": "sha256:" + "0" * 64, "authority_kind": "real_mutation"}.items():
            object.__setattr__(draft, name, value)
        return cls(**{**values, "pdr_id": _id(draft, "pdr_id"), "authority_kind": "real_mutation"})  # type: ignore[arg-type]

    def is_fresh_at(self, now: int) -> bool:
        return self.issued_at <= now < self.expires_at

    def __post_init__(self) -> None:
        _digest(self.pdr_id)
        if self.authority_kind != "real_mutation" or not isinstance(self.attempt_id, str) or not _ATTEMPT.fullmatch(self.attempt_id):
            raise ValueError("PDR must be a real-mutation authority")
        if type(self.issued_at) is not int or type(self.expires_at) is not int or self.expires_at <= self.issued_at:
            raise ValueError("PDR lifetime is invalid")
        if (self.repository_id, self.base_sha) != (_REPOSITORY, _BASE):
            raise ValueError("PDR must use registered fixture lineage")
        for value in (self.payload_id, self.payload_digest, self.idempotency_key): _digest(value)
        if self.pdr_id != _id(self, "pdr_id"): raise ValueError("PDR identity mismatch")


_REQUEST_CAPABILITY = object()


@dataclass(frozen=True, slots=True, init=False)
class RealMutationRequest:
    repository_id: str
    base_sha: str
    payload_id: str
    payload_digest: str
    idempotency_key: str
    real_mutation_pdr_id: str

    def __init__(self, capability: object, pdr: RealMutationPDR) -> None:
        if capability is not _REQUEST_CAPABILITY or not isinstance(pdr, RealMutationPDR):
            raise ValueError("request may only be built by validated authority")
        for name in ("repository_id", "base_sha", "payload_id", "payload_digest", "idempotency_key"):
            object.__setattr__(self, name, getattr(pdr, name))
        object.__setattr__(self, "real_mutation_pdr_id", pdr.pdr_id)
        self.__post_init__()

    @classmethod
    def create(cls, pdr: object, *, now: int) -> "RealMutationRequest":
        if not isinstance(pdr, RealMutationPDR) or not pdr.is_fresh_at(now):
            raise ValueError("only independent real-mutation PDR is accepted")
        return cls(_REQUEST_CAPABILITY, pdr)

    def __post_init__(self) -> None:
        if (self.repository_id, self.base_sha) != (_REPOSITORY, _BASE): raise ValueError("request lineage is invalid")
        for value in (self.payload_id, self.payload_digest, self.idempotency_key, self.real_mutation_pdr_id): _digest(value)
        if self.payload_id.startswith("forgeflow-sim-"): raise ValueError("simulation identity is not a real mutation input")

    @classmethod
    def from_fields(cls, repository_id: str, base_sha: str, payload_id: str, payload_digest: str, idempotency_key: str) -> "RealMutationRequest":
        if isinstance(payload_id, str) and payload_id.startswith("forgeflow-sim-"):
            raise ValueError("simulation identity is not a real mutation input")
        raise ValueError("real mutation request requires a RealMutationPDR")


@dataclass(frozen=True, slots=True)
class RealMutationTerminal:
    terminal_id: str
    reason: str
    attempt_id: str
    rejected_identity_class: str
    automatic_retries: int = 0

    @classmethod
    def create(cls, reason: str, attempt_id: str, rejected_identity_class: str) -> "RealMutationTerminal":
        draft = object.__new__(cls)
        for name, value in {"terminal_id": "sha256:" + "0" * 64, "reason": reason, "attempt_id": attempt_id, "rejected_identity_class": rejected_identity_class, "automatic_retries": 0}.items(): object.__setattr__(draft, name, value)
        return cls(_id(draft, "terminal_id"), reason, attempt_id, rejected_identity_class)

    def __post_init__(self) -> None:
        if not _DIGEST.fullmatch(self.terminal_id) or not isinstance(self.attempt_id, str) or not _ATTEMPT.fullmatch(self.attempt_id) or self.reason != "real_mutation_rejected" or self.rejected_identity_class not in ("simulation_identity", "materialization_pdr", "payload_eligibility_pdr", "foreign_pdr") or self.automatic_retries != 0 or self.terminal_id != _id(self, "terminal_id"):
            raise ValueError("terminal must be bounded and non-authorizing")
