import unittest
from dataclasses import replace

from forgeflow.approval_trace_durable_summary.service import append_summary, publishable_metadata
from forgeflow.approval_trace_durable_summary.canonical import event_id_for, summary_id_for
from forgeflow.approval_trace_durable_summary.models import DurableRunSummary, TraceEvent
from forgeflow.deterministic_patch_artifact_security.canonical import candidate_id_for
from forgeflow.deterministic_patch_artifact_security.models import RedactedArtifactReferenceCandidate


D = "sha256:" + "a" * 64


def candidate() -> RedactedArtifactReferenceCandidate:
    provisional = RedactedArtifactReferenceCandidate(
        "m4-patch-artifact-security/v1", "sha256:" + "0" * 64,
        D, D, D, D, D, D, "forgeflow-m4-patch-metadata-security", 1,
        "m4-patch-metadata-secret-scan-v1", "m4-patch-metadata-redaction-v1",
    )
    return replace(provisional, candidate_id=candidate_id_for(provisional))


class ServiceTests(unittest.TestCase):
    def test_rejects_non_candidate_input_fail_closed(self):
        self.assertIsNone(publishable_metadata(object(), "run-0001"))

    def test_publishes_only_a_canonical_metadata_reference(self):
        reference = publishable_metadata(candidate(), "run-0001")
        self.assertIsNotNone(reference)
        assert reference is not None
        self.assertEqual(reference.candidate_id, candidate().candidate_id)
        self.assertEqual(reference.content_digest, D)

    def test_rejects_tampered_candidate_or_unsafe_run_id(self):
        self.assertIsNone(publishable_metadata(replace(candidate(), candidate_id=D), "run-0001"))
        self.assertIsNone(publishable_metadata(candidate(), "run/source"))

    def test_appends_only_a_canonical_same_run_event(self):
        event = TraceEvent("forgeflow.approval-trace-durable-summary.v1", D, "run-0001", "artifact_published", (D,), "ok")
        event = replace(event, event_id=event_id_for(event))
        summary = DurableRunSummary("forgeflow.approval-trace-durable-summary.v1", D, "run-0001", (D,), (D,), (D,), (D,), "complete")
        summary = replace(summary, summary_id=summary_id_for(summary))
        result = append_summary(summary, event)
        self.assertIsNotNone(result)
        self.assertIn(event.event_id, result.event_ids)
        self.assertIsNone(append_summary(result, event))
