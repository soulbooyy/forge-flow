"""Controlled local persistence for Feature 3 canonical metadata artifacts."""

import hashlib
import os
from pathlib import Path
import tempfile

from .models import MetadataArtifactReference
from .canonical import artifact_reference_id_for
from .service import metadata_bytes_for, publishable_metadata


def publish_metadata(root: object, candidate: object, run_id: object) -> MetadataArtifactReference | None:
    """Atomically publish verified canonical metadata; never persist caller paths."""
    reference = publishable_metadata(candidate, run_id)
    if not isinstance(root, Path) or not root.is_dir() or reference is None:
        return None
    return _write_metadata(root, reference)


def _write_metadata(root: Path, reference: MetadataArtifactReference) -> MetadataArtifactReference | None:
    payload = metadata_bytes_for(reference)
    if (reference.artifact_reference_id != artifact_reference_id_for(reference)
            or "sha256:" + hashlib.sha256(payload).hexdigest() != reference.content_digest):
        return None
    target = root / f"{reference.artifact_reference_id[7:]}.json"
    temporary: str | None = None
    published = False
    try:
        with tempfile.NamedTemporaryFile(dir=root, prefix=".metadata-", delete=False) as handle:
            temporary = handle.name
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.link(temporary, target)
        published = True
        os.unlink(temporary)
        temporary = None
        if target.read_bytes() != payload:
            os.unlink(target)
            published = False
            return None
        directory_fd = os.open(root, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
        return reference
    except OSError:
        if published:
            try:
                os.unlink(target)
            except OSError:
                pass
        return None
    finally:
        if temporary is not None:
            try:
                os.unlink(temporary)
            except OSError:
                pass
