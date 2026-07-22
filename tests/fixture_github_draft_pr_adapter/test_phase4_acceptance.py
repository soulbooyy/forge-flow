from dataclasses import replace
from pathlib import Path
import unittest

from forgeflow.governed_changes.approval_trace.canonical import artifact_reference_id_for, decision_id_for, summary_id_for
from forgeflow.governed_changes.approval_trace.models import ApprovalDecision, DurableRunSummary, MetadataArtifactReference, SCHEMA_VERSION as DURABLE_SCHEMA
from forgeflow.governed_changes.draft_pr.adapter import ControlledFixtureAdapter
from forgeflow.governed_changes.draft_pr.models import DraftPRRequest, FixturePolicyDecisionRecord

class Phase4AcceptanceTests(unittest.TestCase):
    def _facts(self):
        digest_a = "sha256:" + "a" * 64
        digest_b = "sha256:" + "b" * 64
        approval = ApprovalDecision(DURABLE_SCHEMA, digest_b, digest_a, digest_a, "approved", 200)
        approval = replace(approval, decision_id=decision_id_for(approval))
        reference = MetadataArtifactReference(DURABLE_SCHEMA, digest_a, "run-0001", digest_a, digest_a, digest_a, digest_a, "profile-001", 1, digest_a)
        reference = replace(reference, artifact_reference_id=artifact_reference_id_for(reference))
        policy = FixturePolicyDecisionRecord.create(reference.artifact_reference_id, approval.decision_id, "idempotency-001", "allowed", 200)
        summary = DurableRunSummary(DURABLE_SCHEMA, digest_b, "run-0001", (digest_a,), (reference.artifact_reference_id,), (policy.policy_decision_id,), (approval.decision_id,), "complete")
        summary = replace(summary, summary_id=summary_id_for(summary))
        request = DraftPRRequest.create("run-0001", policy.policy_decision_id, approval.decision_id, reference.artifact_reference_id, summary.summary_id, "idempotency-001")
        from forgeflow.governed_changes.draft_pr.service import RedactedBodyFacts
        facts = RedactedBodyFacts("fixture-task-accepted", "governed-metadata-update", ("change-001",), "succeeded", "passed", 0, "none")
        return request, policy, approval, reference, summary, facts

    def test_allowed_metadata_only_path_has_exactly_zero_external_effect(self):
        request, policy, approval, reference, summary, facts = self._facts()
        adapter = ControlledFixtureAdapter()
        outcome = adapter.reconcile(request, policy, approval, reference, summary, facts, 100, object())
        self.assertEqual("materialization_unavailable", outcome.terminal.reason)
        self.assertEqual(0, adapter.external_mutation_count)

    def test_idempotency_replay_creates_no_new_effect(self):
        request, policy, approval, reference, summary, facts = self._facts()
        adapter = ControlledFixtureAdapter()
        first = adapter.reconcile(request, policy, approval, reference, summary, facts, 100, object())
        replay = adapter.reconcile(request, policy, approval, reference, summary, facts, 100, object())
        self.assertEqual(first, replay)
        self.assertEqual(0, adapter.external_mutation_count)

    def test_denied_policy_has_zero_external_effect(self):
        _, _, approval, reference, _, facts = self._facts()
        policy = FixturePolicyDecisionRecord.create(reference.artifact_reference_id, approval.decision_id, "idempotency-001", "blocked", 200)
        summary = DurableRunSummary(approval.schema_version, "sha256:" + "b" * 64, "run-0001", ("sha256:" + "a" * 64,), (reference.artifact_reference_id,), (policy.policy_decision_id,), (approval.decision_id,), "complete")
        summary = replace(summary, summary_id=summary_id_for(summary))
        request = DraftPRRequest.create("run-0001", policy.policy_decision_id, approval.decision_id, reference.artifact_reference_id, summary.summary_id, "idempotency-001")
        adapter = ControlledFixtureAdapter()
        outcome = adapter.reconcile(request, policy, approval, reference, summary, facts, 100, object())
        self.assertEqual("policy_blocked", outcome.terminal.reason)
        self.assertEqual(0, adapter.external_mutation_count)

    def test_denied_approval_and_invalid_body_have_zero_external_effect(self):
        request, policy, approval, reference, summary, _ = self._facts()
        denied = replace(approval, outcome="denied")
        denied = replace(denied, decision_id=decision_id_for(denied))
        denied_policy = FixturePolicyDecisionRecord.create(reference.artifact_reference_id, denied.decision_id, "idempotency-002", "allowed", 200)
        denied_summary = DurableRunSummary(approval.schema_version, "sha256:" + "b" * 64, "run-0001", ("sha256:" + "a" * 64,), (reference.artifact_reference_id,), (denied_policy.policy_decision_id,), (denied.decision_id,), "complete")
        denied_summary = replace(denied_summary, summary_id=summary_id_for(denied_summary))
        denied_request = DraftPRRequest.create("run-0001", denied_policy.policy_decision_id, denied.decision_id, reference.artifact_reference_id, denied_summary.summary_id, "idempotency-002")
        adapter = ControlledFixtureAdapter()
        approval_outcome = adapter.reconcile(denied_request, denied_policy, denied, reference, denied_summary, object(), 100, object())
        self.assertEqual("approval_required", approval_outcome.terminal.reason)
        self.assertEqual(0, adapter.external_mutation_count)
        body_adapter = ControlledFixtureAdapter()
        body_outcome = body_adapter.reconcile(request, policy, approval, reference, summary, object(), 100, object())
        self.assertEqual("policy_blocked", body_outcome.terminal.reason)
        self.assertEqual("no_effect", body_outcome.result.outcome)
        self.assertEqual(0, body_adapter.external_mutation_count)

    def test_registered_reset_and_audit_procedure_is_manual_and_payload_free(self):
        registration = Path("docs/fixtures/m4-fixture-environment-registration.md").read_text()
        self.assertIn("reset_method: After each evaluation", registration)
        self.assertIn("redacted audit summary", registration)
        self.assertIn("credentials, raw token values, and raw GitHub payloads are excluded", registration)
