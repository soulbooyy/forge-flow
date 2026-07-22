import unittest
import tempfile
from pathlib import Path
from dataclasses import replace

from forgeflow.governed_changes.approval_trace import service
from forgeflow.governed_changes.approval_trace.store import publish_metadata
from forgeflow.governed_changes.artifact_security.canonical import candidate_id_for
from forgeflow.governed_changes.artifact_security.models import RedactedArtifactReferenceCandidate

D = "sha256:" + "a" * 64


def candidate():
    provisional = RedactedArtifactReferenceCandidate("m4-patch-artifact-security/v1", "sha256:" + "0" * 64, D, D, D, D, D, D, "forgeflow-m4-patch-metadata-security", 1, "m4-patch-metadata-secret-scan-v1", "m4-patch-metadata-redaction-v1")
    return replace(provisional, candidate_id=candidate_id_for(provisional))


class AcceptanceTests(unittest.TestCase):
    def test_public_modules_do_not_expose_patch_or_execution_capability(self):
        forbidden = ("patch", "diff", "source", "execute", "github", "retry")
        self.assertTrue(all(token not in service.__dict__ for token in forbidden))

    def test_canonical_candidate_publishes_only_metadata_bytes(self):
        reference = service.publishable_metadata(candidate(), "run-0001")
        self.assertIsNotNone(reference)
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(publish_metadata(Path(directory), candidate(), "run-0001"), reference)
            self.assertNotIn(b"raw source", next(Path(directory).iterdir()).read_bytes().lower())
