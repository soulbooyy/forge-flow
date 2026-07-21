"""Closed fixture registrations; callers never resolve source locations."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from typing import Callable

from .models import MaterializationTerminal, TransformationManifest


def _digest_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


@dataclass(frozen=True, slots=True)
class RegisteredSourceSnapshot:
    """Harness-private registration, never a durable payload contract."""

    repository_id: str
    base_sha: str
    snapshot_digest: str
    target_file_id: str
    target_digest: str
    target_bytes: bytes


_TARGET_FILE_ID = "fixture-test-file-v1"
_TARGET_LOCATION = "tests/fixture_test.py"
_TARGET_BYTES = b"assert False\n"
REGISTERED_SNAPSHOT = RegisteredSourceSnapshot(
    repository_id="1300511729",
    base_sha="97c8220cd713ebf61124ac2de2f3eadc6e4dc222",
    snapshot_digest=_digest_bytes(_TARGET_BYTES),
    target_file_id=_TARGET_FILE_ID,
    target_digest=_digest_bytes(_TARGET_BYTES),
    target_bytes=_TARGET_BYTES,
)


@dataclass(frozen=True, slots=True)
class SnapshotRevalidation:
    snapshot: "VerifiedSnapshot" | None
    terminal: MaterializationTerminal | None


_VERIFICATION_CAPABILITY = object()


class VerifiedSnapshot:
    """Private proof that this exact registration was just revalidated."""

    __slots__ = ("_snapshot", "_capability")

    def __init__(self, snapshot: RegisteredSourceSnapshot, capability: object) -> None:
        if capability is not _VERIFICATION_CAPABILITY:
            raise TypeError("VerifiedSnapshot is harness-private")
        self._snapshot = snapshot
        self._capability = capability

    @property
    def snapshot(self) -> RegisteredSourceSnapshot:
        return self._snapshot


def resolve_target_file(target_file_id: str) -> str:
    if target_file_id != _TARGET_FILE_ID:
        raise ValueError("target file ID is not registered")
    return _TARGET_LOCATION


def _fixture_transformer(value: bytes) -> bytes:
    if value != _TARGET_BYTES:
        raise ValueError("registered transformer input mismatch")
    return b"assert True\n"


def resolve_transformer(manifest: TransformationManifest) -> Callable[[bytes], bytes]:
    if (manifest.transformation_id, manifest.transformation_version, manifest.target_file_id, manifest.expected_input_digest) != (
        "fixture-transform-v1", "1", _TARGET_FILE_ID, REGISTERED_SNAPSHOT.target_digest
    ):
        raise ValueError("manifest does not select a registered transformer")
    return _fixture_transformer


def revalidate_snapshot(snapshot: RegisteredSourceSnapshot, injected_files: dict[str, bytes]) -> SnapshotRevalidation:
    """Accept only the exact harness-injected registered fixture target bytes."""
    if snapshot != REGISTERED_SNAPSHOT or set(injected_files) != {_TARGET_LOCATION}:
        return _source_terminal(snapshot, "snapshot_mismatch")
    observed = injected_files[_TARGET_LOCATION]
    if _digest_bytes(observed) != snapshot.target_digest or _digest_bytes(observed) != snapshot.snapshot_digest:
        return _source_terminal(snapshot, "target_digest_mismatch")
    return SnapshotRevalidation(snapshot=VerifiedSnapshot(snapshot, _VERIFICATION_CAPABILITY), terminal=None)


def _source_terminal(snapshot: RegisteredSourceSnapshot, classification: str) -> SnapshotRevalidation:
    return SnapshotRevalidation(
        snapshot=None,
        terminal=MaterializationTerminal.create(
            reason="source_revalidation_failed", attempt_id="revalidation-attempt-1",
            repository_id=snapshot.repository_id, base_sha=snapshot.base_sha,
            profile_id=None, profile_version=None, classification=classification,
        ),
    )
