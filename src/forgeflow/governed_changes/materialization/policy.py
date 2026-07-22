"""Exact-scope PDR issuance for verified registry inputs only."""

from __future__ import annotations

from itertools import count

from .models import MaterializationPDR, TransformationManifest
from .registry import REGISTERED_SNAPSHOT, VerifiedSnapshot, resolve_transformer
from forgeflow.governed_changes.action_execution.profile import M4_FIXTURE_V1

_ATTEMPT_SEQUENCE = count(1)


def issue_materialization_pdr(manifest: TransformationManifest, verified: VerifiedSnapshot | None, now: int) -> MaterializationPDR:
    if not isinstance(verified, VerifiedSnapshot) or verified.snapshot is not REGISTERED_SNAPSHOT:
        raise ValueError("only the revalidated registered snapshot may receive a PDR")
    snapshot = verified.snapshot
    resolve_transformer(manifest)
    if type(now) is not int:
        raise ValueError("now must be an integer attempt clock")
    attempt_sequence = next(_ATTEMPT_SEQUENCE)
    return MaterializationPDR.create(
        attempt_id=f"materialization-{snapshot.snapshot_digest[7:19]}-{now}-{attempt_sequence}", issued_at=now, expires_at=now + 1,
        repository_id=snapshot.repository_id, base_sha=snapshot.base_sha, snapshot_digest=snapshot.snapshot_digest,
        transformation_id=manifest.transformation_id, transformation_version=manifest.transformation_version,
        target_file_id=manifest.target_file_id, expected_input_digest=manifest.expected_input_digest,
        profile_id=M4_FIXTURE_V1.policy_profile_id, profile_version=M4_FIXTURE_V1.policy_profile_version,
    )
