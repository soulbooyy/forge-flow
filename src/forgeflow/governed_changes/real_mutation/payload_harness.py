"""Registered fixture payload materialization for the real-mutation boundary."""

from __future__ import annotations

import hashlib
import re

from .github_adapter import EphemeralMutationPayload, _mint_ephemeral_payload
from .fixture_registry import FIXTURE_INPUT_DIGEST, FIXTURE_OUTPUT_DIGEST, FIXTURE_TARGET_FILE_ID
from .models import RealMutationPDR


_RETURN_SUBTRACTION = re.compile(rb"(?m)^(\s*return\s+[^\r\n]*?)\s-\s")
_SOURCE_CAPABILITY = object()


class VerifiedFixtureSource:
    __slots__ = ("_content",)

    def __init__(self, capability: object, content: bytes) -> None:
        if capability is not _SOURCE_CAPABILITY:
            raise TypeError("fixture source must be verified by the harness")
        self._content = content

    @property
    def content_for_harness(self) -> bytes:
        return self._content


def _mint_verified_fixture_source(content: bytes) -> VerifiedFixtureSource:
    if not isinstance(content, bytes) or _digest(content) != FIXTURE_INPUT_DIGEST:
        raise ValueError("fixture source does not match registered snapshot")
    return VerifiedFixtureSource(_SOURCE_CAPABILITY, content)


def transform_fixture_bytes(content: bytes) -> bytes:
    transformed, count = _RETURN_SUBTRACTION.subn(lambda match: match.group(1) + b" + ", content, count=1)
    if count != 1:
        raise ValueError("registered calculator transformation did not match exactly once")
    return transformed


def materialize_fixture_payload(pdr: RealMutationPDR, source: VerifiedFixtureSource) -> EphemeralMutationPayload:
    if not isinstance(pdr, RealMutationPDR) or not isinstance(source, VerifiedFixtureSource):
        raise ValueError("real mutation authority and verified source are required")
    output = transform_fixture_bytes(source.content_for_harness)
    if _digest(output) != FIXTURE_OUTPUT_DIGEST or pdr.payload_digest != FIXTURE_OUTPUT_DIGEST:
        raise ValueError("registered transformer output does not match real-mutation lineage")
    return _mint_ephemeral_payload(pdr.payload_id, pdr.payload_digest, FIXTURE_TARGET_FILE_ID, output)


def _digest(content: bytes) -> str:
    return "sha256:" + hashlib.sha256(content).hexdigest()
