import unittest

from forgeflow.approval_trace_durable_summary.models import (
    ApprovalDecision,
    DurableRunSummary,
    MetadataArtifactReference,
    SCHEMA_VERSION as DURABLE_SCHEMA,
)
from forgeflow.approval_trace_durable_summary.canonical import (
    artifact_reference_id_for,
    decision_id_for,
    summary_id_for,
)
from dataclasses import replace
from forgeflow.fixture_github_draft_pr_adapter.models import (
    DraftPRRequest,
    FixturePolicyDecisionRecord,
    PRResult,
)
from forgeflow.fixture_github_draft_pr_adapter.service import (
    RedactedBodyFacts,
    evaluate_eligibility,
    render_redacted_body,
)

D = "sha256:" + "a" * 64
D2 = "sha256:" + "b" * 64


class Phase2ServiceTests(unittest.TestCase):
    def _facts(self):
        approval = ApprovalDecision(DURABLE_SCHEMA, D2, D, D, "approved", 200)
        approval = replace(approval, decision_id=decision_id_for(approval))
        reference = MetadataArtifactReference(DURABLE_SCHEMA, D, "run-0001", D, D, D, D, "profile-001", 1, D)
        reference = replace(reference, artifact_reference_id=artifact_reference_id_for(reference))
        policy = FixturePolicyDecisionRecord.create(reference.artifact_reference_id, approval.decision_id, "idempotency-001", "allowed", 200)
        summary = DurableRunSummary(DURABLE_SCHEMA, D2, "run-0001", (D,), (reference.artifact_reference_id,), (policy.policy_decision_id,), (approval.decision_id,), "complete")
        summary = replace(summary, summary_id=summary_id_for(summary))
        request = DraftPRRequest.create("run-0001", policy.policy_decision_id, approval.decision_id, reference.artifact_reference_id, summary.summary_id, "idempotency-001")
        return request, policy, approval, reference, summary

    def test_fresh_allowed_lineage_is_eligible(self):
        request, policy, approval, reference, summary = self._facts()
        self.assertIsNone(evaluate_eligibility(request, policy, approval, reference, summary, 100))

    def test_stale_or_missing_approval_is_a_no_effect_terminal(self):
        request, _, approval, reference, summary = self._facts()
        stale_policy = FixturePolicyDecisionRecord.create(reference.artifact_reference_id, approval.decision_id, "idempotency-001", "allowed", 99)
        stale = evaluate_eligibility(request, stale_policy, approval, reference, summary, 100)
        missing = evaluate_eligibility(request, FixturePolicyDecisionRecord.create(reference.artifact_reference_id, approval.decision_id, "idempotency-001", "allowed", 200), None, reference, summary, 100)
        self.assertEqual("policy_blocked", stale.reason)
        self.assertEqual("approval_required", missing.reason)

    def test_mismatched_durable_lineage_is_policy_blocked(self):
        request, policy, approval, reference, summary = self._facts()
        bad_summary = DurableRunSummary(DURABLE_SCHEMA, D2, "run-0001", (D,), (D,), (D2,), (D2,), "complete")
        terminal = evaluate_eligibility(request, policy, approval, reference, bad_summary, 100)
        self.assertEqual("policy_blocked", terminal.reason)

    def test_forged_upstream_facts_are_policy_blocked(self):
        policy = FixturePolicyDecisionRecord.create(D, D2, "idempotency-001", "allowed", 200)
        request = DraftPRRequest.create("run-0001", policy.policy_decision_id, D2, D, D2, "idempotency-001")
        forged_approval = ApprovalDecision(DURABLE_SCHEMA, D2, D, D, "approved", 200)
        forged_reference = MetadataArtifactReference(DURABLE_SCHEMA, D, "run-0001", D, D, D, D, "profile-001", 1, D)
        forged_summary = DurableRunSummary(DURABLE_SCHEMA, D2, "run-0001", (D,), (D,), (policy.policy_decision_id,), (D2,), "complete")
        terminal = evaluate_eligibility(request, policy, forged_approval, forged_reference, forged_summary, 100)
        self.assertEqual("policy_blocked", terminal.reason)

    def test_renderer_uses_only_bounded_redacted_facts(self):
        request, _, _, reference, summary = self._facts()
        facts = RedactedBodyFacts(
            "fixture-task-accepted",
            "governed-metadata-update",
            ("change-001",),
            "succeeded",
            "passed",
            0,
            "none",
        )
        body = render_redacted_body(request, reference, summary, facts)
        self.assertIn("Fixture task accepted", body)
        self.assertIn(reference.artifact_metadata_id, body)
        self.assertNotIn("credential", body.lower())
        self.assertNotIn("raw issue", body.lower())

    def test_renderer_rejects_source_like_or_path_like_text(self):
        with self.assertRaises(ValueError):
            RedactedBodyFacts("password=secret", "governed-metadata-update", ("change-001",), "succeeded", "passed", 0, "none")
        with self.assertRaises(ValueError):
            RedactedBodyFacts("fixture-task-accepted", "governed-metadata-update", ("src-file",), "succeeded", "passed", 0, "none")

    def test_renderer_rejects_forbidden_payload_terms(self):
        with self.assertRaises(ValueError):
            RedactedBodyFacts("Raw source summary", "governed-metadata-update", ("change-001",), "succeeded", "passed", 0, "none")
        with self.assertRaises(ValueError):
            RedactedBodyFacts("fixture-task-accepted", "Patch content summary", ("change-001",), "succeeded", "passed", 0, "none")
