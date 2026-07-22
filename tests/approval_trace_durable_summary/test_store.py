import tempfile
import unittest
from pathlib import Path
from dataclasses import replace
import hashlib

from forgeflow.governed_changes.approval_trace.canonical import artifact_reference_id_for
from forgeflow.governed_changes.approval_trace.models import MetadataArtifactReference
from forgeflow.governed_changes.approval_trace.service import metadata_bytes_for
from forgeflow.governed_changes.approval_trace.store import _write_metadata, publish_metadata

D = "sha256:" + "a" * 64


def reference():
    provisional = MetadataArtifactReference("forgeflow.approval-trace-durable-summary.v1", D, "run-0001", D, D, "sha256:" + "0" * 64, D, "profile-001", 1, D)
    with_digest = replace(provisional, content_digest="sha256:" + hashlib.sha256(metadata_bytes_for(provisional)).hexdigest())
    return replace(with_digest, artifact_reference_id=artifact_reference_id_for(with_digest))


class StoreTests(unittest.TestCase):
    def test_rejects_non_reference_without_writing(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.assertIsNone(publish_metadata(root, object(), "run-0001"))
            self.assertEqual(list(root.iterdir()), [])

    def test_public_path_rejects_a_manually_constructed_reference(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.assertIsNone(publish_metadata(root, reference(), "run-0001"))
            self.assertEqual(list(root.iterdir()), [])

    def test_publishes_verified_bytes_at_a_durable_id(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            artifact = reference()
            self.assertEqual(_write_metadata(root, artifact), artifact)
            self.assertEqual((root / f"{artifact.artifact_reference_id[7:]}.json").read_bytes(), metadata_bytes_for(artifact))

    def test_rejects_digest_mismatch_without_a_final_artifact(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.assertIsNone(_write_metadata(root, replace(reference(), content_digest=D)))
            self.assertEqual(list(root.iterdir()), [])

    def test_never_overwrites_an_existing_immutable_artifact(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            artifact = reference()
            target = root / f"{artifact.artifact_reference_id[7:]}.json"
            target.write_bytes(b"existing")
            self.assertIsNone(_write_metadata(root, artifact))
            self.assertEqual(target.read_bytes(), b"existing")

    def test_rejects_a_noncanonical_reference_id_without_writing(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.assertIsNone(_write_metadata(root, replace(reference(), artifact_reference_id=D)))
            self.assertEqual(list(root.iterdir()), [])
