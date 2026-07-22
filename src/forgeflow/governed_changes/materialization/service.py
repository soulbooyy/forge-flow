"""Payload assembly with facts-only terminals and unconditional lease cleanup."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from collections.abc import Callable

from forgeflow.governed_changes.action_execution.profile import M4_FIXTURE_V1

from .models import EphemeralPayloadHandle, MaterializationPDR, MaterializationTerminal, MaterializedCommitPayload, TransformationManifest, _mint_ephemeral_handle
from .registry import VerifiedSnapshot, resolve_transformer
from .sandbox import LocalDockerBackend


class EphemeralPayloadLease:
    __slots__ = ("_bytes", "handle", "destroyed")

    def __init__(self, value: bytes) -> None:
        self._bytes = value
        self.handle = _mint_ephemeral_handle()
        self.destroyed = False

    @classmethod
    def for_test(cls, value: bytes) -> "EphemeralPayloadLease":
        return cls(value)

    @property
    def bytes_for_harness(self) -> bytes:
        if self.destroyed or not self.handle.is_live:
            raise ValueError("ephemeral lease is no longer live")
        return self._bytes

    def destroy(self) -> None:
        self._bytes = b""
        self.handle.destroy()
        self.destroyed = True


@dataclass(frozen=True, slots=True)
class MaterializationResult:
    payload: MaterializedCommitPayload | None
    terminal: MaterializationTerminal | None


def materialize(pdr: MaterializationPDR, verified: VerifiedSnapshot | None, manifest: TransformationManifest, backend: LocalDockerBackend, *, now: int, _harness_consumer: Callable[[MaterializedCommitPayload, EphemeralPayloadLease], None] | None = None) -> MaterializationResult:
    lease: EphemeralPayloadLease | None = None
    snapshot = verified.snapshot if isinstance(verified, VerifiedSnapshot) else None
    try:
        if snapshot is None or not pdr.is_fresh_at(now) or not _exact_pdr(pdr, snapshot, manifest):
            return _terminal(pdr, "materialization_not_authorized", "pdr_expired" if not pdr.is_fresh_at(now) else "pdr_scope_mismatch")
        try:
            proof = backend.prove(M4_FIXTURE_V1)
        except Exception:
            return _terminal(pdr, "validation_infrastructure_failed", "runner_unavailable")
        if not proof.allowed:
            return _terminal(pdr, "validation_infrastructure_failed", "profile_proof_missing")
        try:
            facts = backend.materialize(snapshot, manifest)
        except Exception:
            return _terminal(pdr, "materialization_failed", "sandbox_output_invalid")
        if not isinstance(facts.lease, EphemeralPayloadLease):
            return _terminal(pdr, "materialization_failed", "sandbox_output_invalid")
        lease = facts.lease
        expected = resolve_transformer(manifest)(snapshot.target_bytes)
        if facts.security_status != "passed":
            return _terminal(pdr, "materialization_failed", "security_blocked", facts.security_fact_id)
        if facts.extra_files or lease.bytes_for_harness != expected:
            return _terminal(pdr, "materialization_failed", "sandbox_output_invalid")
        try:
            validation = backend.validate(lease, M4_FIXTURE_V1)
        except Exception:
            return _terminal(pdr, "validation_infrastructure_failed", "runner_unavailable")
        if validation.status == "assertion_failed":
            return _terminal(pdr, "validation_failed", "assertion_failed")
        if validation.status != "passed" or validation.execution_fact_id is None:
            return _terminal(pdr, "validation_infrastructure_failed", "runner_unavailable")
        output_digest = "sha256:" + hashlib.sha256(lease.bytes_for_harness).hexdigest()
        payload = MaterializedCommitPayload.create(
            repository_id=snapshot.repository_id, base_sha=snapshot.base_sha, snapshot_digest=snapshot.snapshot_digest,
            transformation_id=manifest.transformation_id, transformation_version=manifest.transformation_version,
            target_file_id=manifest.target_file_id, input_digest=manifest.expected_input_digest, output_digest=output_digest,
            materialization_pdr_id=pdr.pdr_id, security_fact_ids=(facts.security_fact_id,),
            validation_fact_id=validation.execution_fact_id, review_fact_ids=(),
        )
        if _harness_consumer is not None:
            _harness_consumer(payload, lease)
        return MaterializationResult(payload, None)
    except (TypeError, ValueError):
        return _terminal(pdr, "materialization_failed", "sandbox_output_invalid")
    finally:
        if lease is not None:
            try:
                lease.destroy()
            except Exception:
                pass


def _exact_pdr(pdr: MaterializationPDR, snapshot: object, manifest: TransformationManifest) -> bool:
    return (pdr.repository_id, pdr.base_sha, pdr.snapshot_digest, pdr.transformation_id, pdr.transformation_version, pdr.target_file_id, pdr.expected_input_digest, pdr.profile_id, pdr.profile_version) == (snapshot.repository_id, snapshot.base_sha, snapshot.snapshot_digest, manifest.transformation_id, manifest.transformation_version, manifest.target_file_id, manifest.expected_input_digest, M4_FIXTURE_V1.policy_profile_id, M4_FIXTURE_V1.policy_profile_version)


def _terminal(pdr: MaterializationPDR, reason: str, classification: str, *related_ids: str) -> MaterializationResult:
    return MaterializationResult(None, MaterializationTerminal.create(reason=reason, attempt_id=pdr.attempt_id, repository_id=pdr.repository_id, base_sha=pdr.base_sha, profile_id=pdr.profile_id, profile_version=pdr.profile_version, classification=classification, related_ids=tuple(sorted((pdr.pdr_id, *related_ids)))))
