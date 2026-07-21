"""Pure Phase 2 assembly for metadata-only durable publication facts."""

from dataclasses import asdict, replace
import hashlib
import json

from forgeflow.deterministic_patch_artifact_security.canonical import (
    is_canonical_candidate,
)
from forgeflow.deterministic_patch_artifact_security.models import (
    RedactedArtifactReferenceCandidate,
)

from .canonical import artifact_reference_id_for, event_id_for, summary_id_for
from .models import DurableRunSummary, MetadataArtifactReference, SCHEMA_VERSION, TraceEvent


def metadata_bytes_for(reference: MetadataArtifactReference) -> bytes:
    """Canonical published metadata, excluding its derived identity and digest."""
    payload = asdict(reference)
    payload.pop("artifact_reference_id")
    payload.pop("content_digest")
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()


def publishable_metadata(
    candidate: object, run_id: object
) -> MetadataArtifactReference | None:
    """Return a durable metadata reference only for an authentic F2 candidate."""
    if not isinstance(candidate, RedactedArtifactReferenceCandidate):
        return None
    if not is_canonical_candidate(candidate):
        return None
    try:
        provisional = MetadataArtifactReference(
            schema_version=SCHEMA_VERSION,
            artifact_reference_id="sha256:" + "0" * 64,
            run_id=run_id,  # type: ignore[arg-type]
            candidate_id=candidate.candidate_id,
            artifact_metadata_id=candidate.patch_artifact_id,
            content_digest="sha256:" + "0" * 64,
            candidate_content_digest=candidate.redacted_metadata_digest,
            profile_id=candidate.profile_id,
            profile_version=candidate.profile_version,
            lineage_digest=candidate.lineage_digest,
        )
    except ValueError:
        return None
    content_digest = "sha256:" + hashlib.sha256(metadata_bytes_for(provisional)).hexdigest()
    with_digest = replace(provisional, content_digest=content_digest)
    return replace(with_digest, artifact_reference_id=artifact_reference_id_for(with_digest))


def append_summary(summary: object, event: object) -> DurableRunSummary | None:
    """Append one canonical trace reference without changing other summary facts."""
    if not isinstance(summary, DurableRunSummary) or not isinstance(event, TraceEvent):
        return None
    if (summary.summary_id != summary_id_for(summary) or event.event_id != event_id_for(event)
            or summary.run_id != event.run_id or event.event_id in summary.event_ids):
        return None
    try:
        provisional = replace(
            summary,
            summary_id="sha256:" + "0" * 64,
            event_ids=tuple(sorted((*summary.event_ids, event.event_id))),
        )
    except ValueError:
        return None
    return replace(provisional, summary_id=summary_id_for(provisional))
