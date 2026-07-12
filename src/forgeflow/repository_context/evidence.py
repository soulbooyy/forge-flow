"""Evidence construction for direct repository-context matches."""

from __future__ import annotations

from dataclasses import replace
import hashlib

from .canonical import evidence_id_for
from .models import ContentHash, EvidenceRef, TextLocator
from .scanner import ScannedFile


def file_evidence(scanned_file: ScannedFile, retrieval_signal: str) -> EvidenceRef:
    """Build file-level evidence for a filename or path match."""
    return _with_id(
        EvidenceRef(
            id="",
            evidence_kind=f"file_{retrieval_signal}",
            retrieval_signal=retrieval_signal,
            locator=None,
            path=scanned_file.path,
        )
    )


def text_evidence(scanned_file: ScannedFile, locator: TextLocator) -> EvidenceRef:
    """Build text-match evidence with an inspected-text verification hash."""
    if scanned_file.text is None:
        raise ValueError("text evidence requires inspected text")

    content_hash = ContentHash(
        algorithm="sha256",
        value=hashlib.sha256(scanned_file.text.encode("utf-8")).hexdigest(),
    )
    hash_scope = (
        "truncated_inspected_range"
        if scanned_file.text_truncated
        else "full_inspected_text"
    )
    return _with_id(
        EvidenceRef(
            id="",
            evidence_kind="file_text_match",
            retrieval_signal="text_match",
            locator=locator,
            path=scanned_file.path,
            content_hash=content_hash,
            hash_scope=hash_scope,
        )
    )


def _with_id(reference: EvidenceRef) -> EvidenceRef:
    return replace(reference, id=evidence_id_for(reference))
