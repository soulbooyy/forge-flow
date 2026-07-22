"""Deterministic in-memory simulation; never a provider or Git surface."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

from .models import EphemeralPayloadHandle, MaterializationPDR, MaterializationTerminal, MaterializedCommitPayload, PayloadEligibilityPDR, _bind_ephemeral_handle


@dataclass(frozen=True, slots=True)
class FakeMutationResult:
    blob_id: str
    tree_id: str
    commit_id: str
    ref_id: str

    @classmethod
    def from_payload(cls, payload: MaterializedCommitPayload) -> "FakeMutationResult":
        seed = hashlib.sha256((payload.payload_id + payload.base_sha).encode()).hexdigest()
        return cls(*(f"forgeflow-sim-{kind}-{hashlib.sha256((seed + kind).encode()).hexdigest()}" for kind in ("blob", "tree", "commit", "ref")))


class FakeGitDataAdapter:
    def _bind_for_harness(self, handle: EphemeralPayloadHandle, payload: MaterializedCommitPayload, pdr: PayloadEligibilityPDR) -> None:
        _bind_ephemeral_handle(handle, (payload.payload_id, payload.repository_id, payload.base_sha, payload.output_digest, pdr.pdr_id))

    def simulate(self, handle: EphemeralPayloadHandle, payload: MaterializedCommitPayload, pdr: PayloadEligibilityPDR, *, now: int) -> FakeMutationResult | MaterializationTerminal:
        try:
            if not isinstance(pdr, PayloadEligibilityPDR):
                return _binding_terminal(payload, None, "pdr_scope_mismatch")
            if not isinstance(handle, EphemeralPayloadHandle) or not handle.is_live or handle._binding != (payload.payload_id, payload.repository_id, payload.base_sha, payload.output_digest, pdr.pdr_id):
                return _binding_terminal(payload, pdr, "handle_expired")
            if not isinstance(pdr, PayloadEligibilityPDR) or not pdr.is_fresh_at(now):
                return _binding_terminal(payload, pdr, "pdr_scope_mismatch")
            if (pdr.repository_id, pdr.base_sha, pdr.payload_id, pdr.output_digest, pdr.security_fact_ids, pdr.validation_fact_id, pdr.review_fact_ids, pdr.materialization_pdr_id) != (payload.repository_id, payload.base_sha, payload.payload_id, payload.output_digest, payload.security_fact_ids, payload.validation_fact_id, payload.review_fact_ids, payload.materialization_pdr_id):
                return _binding_terminal(payload, pdr, "payload_mismatch")
            return FakeMutationResult.from_payload(payload)
        finally:
            if isinstance(handle, EphemeralPayloadHandle):
                handle.destroy()


def reject_real_mutation_input(value: object) -> None:
    if isinstance(value, (MaterializationPDR, PayloadEligibilityPDR)) or (isinstance(value, str) and value.startswith("forgeflow-sim-")):
        raise ValueError("v1 authority or simulation identity is not real-mutation input")


def _binding_terminal(payload: MaterializedCommitPayload, pdr: PayloadEligibilityPDR | None, classification: str) -> MaterializationTerminal:
    related = (payload.payload_id,) if pdr is None else tuple(sorted((payload.payload_id, pdr.pdr_id)))
    return MaterializationTerminal.create(reason="simulation_binding_failed", attempt_id="simulation-binding-1" if pdr is None else pdr.attempt_id, repository_id=payload.repository_id, base_sha=payload.base_sha, profile_id=None, profile_version=None, classification=classification, related_ids=related)
