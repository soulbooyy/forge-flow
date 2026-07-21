from dataclasses import replace
import unittest

from forgeflow.approval_trace_durable_summary.canonical import (
    artifact_reference_id_for,
    decision_id_for,
    summary_id_for,
)
from forgeflow.approval_trace_durable_summary.models import (
    ApprovalDecision,
    DurableRunSummary,
    MetadataArtifactReference,
    SCHEMA_VERSION as DURABLE_SCHEMA,
)
from forgeflow.fixture_github_draft_pr_adapter.adapter import ControlledFixtureAdapter
from forgeflow.fixture_github_draft_pr_adapter.models import (
    DraftPRRequest,
    FixturePolicyDecisionRecord,
)
from forgeflow.fixture_github_draft_pr_adapter.service import RedactedBodyFacts

D = "sha256:" + "a" * 64
D2 = "sha256:" + "b" * 64


class Phase3AdapterTests(unittest.TestCase):
    def _facts(self):
        approval = ApprovalDecision(DURABLE_SCHEMA, D2, D, D, "approved", 200)
        approval = replace(approval, decision_id=decision_id_for(approval))
        reference = MetadataArtifactReference(DURABLE_SCHEMA, D, "run-0001", D, D, D, D, "profile-001", 1, D)
        reference = replace(reference, artifact_reference_id=artifact_reference_id_for(reference))
        policy = FixturePolicyDecisionRecord.create(reference.artifact_reference_id, approval.decision_id, "idempotency-001", "allowed", 200)
        summary = DurableRunSummary(DURABLE_SCHEMA, D2, "run-0001", (D,), (reference.artifact_reference_id,), (policy.policy_decision_id,), (approval.decision_id,), "complete")
        summary = replace(summary, summary_id=summary_id_for(summary))
        request = DraftPRRequest.create("run-0001", policy.policy_decision_id, approval.decision_id, reference.artifact_reference_id, summary.summary_id, "idempotency-001")
        facts = RedactedBodyFacts("fixture-task-accepted", "governed-metadata-update", ("change-001",), "succeeded", "passed", 0, "none")
        return request, policy, approval, reference, summary, facts

    def test_authorized_metadata_only_request_ends_without_external_mutation(self):
        request, policy, approval, reference, summary, facts = self._facts()
        adapter = ControlledFixtureAdapter()
        outcome = adapter.reconcile(request, policy, approval, reference, summary, facts, 100, object())
        self.assertEqual("materialization_unavailable", outcome.terminal.reason)
        self.assertEqual("terminal", outcome.idempotency_record.state)
        self.assertEqual("no_effect", outcome.result.outcome)
        self.assertEqual(0, adapter.external_mutation_count)

    def test_replay_returns_the_original_terminal_without_new_effect(self):
        request, policy, approval, reference, summary, facts = self._facts()
        adapter = ControlledFixtureAdapter()
        first = adapter.reconcile(request, policy, approval, reference, summary, facts, 100, object())
        replay = adapter.reconcile(request, policy, approval, reference, summary, facts, 100, object())
        self.assertEqual(first, replay)
        self.assertEqual(0, adapter.external_mutation_count)

    def test_same_key_for_different_request_is_an_idempotency_conflict(self):
        request, policy, approval, reference, summary, facts = self._facts()
        conflicting = DraftPRRequest.create("run-0002", policy.policy_decision_id, approval.decision_id, reference.artifact_reference_id, summary.summary_id, "idempotency-001")
        adapter = ControlledFixtureAdapter()
        adapter.reconcile(request, policy, approval, reference, summary, facts, 100, object())
        outcome = adapter.reconcile(conflicting, policy, approval, reference, summary, facts, 100, object())
        self.assertEqual("idempotency_conflict", outcome.terminal.reason)
        self.assertEqual(0, adapter.external_mutation_count)

    def test_opaque_credential_is_not_read_or_retained(self):
        class OpaqueCredential:
            def __getattribute__(self, name):
                raise AssertionError("credential must remain opaque")

        request, policy, approval, reference, summary, facts = self._facts()
        outcome = ControlledFixtureAdapter().reconcile(request, policy, approval, reference, summary, facts, 100, OpaqueCredential())
        self.assertFalse(hasattr(outcome, "credential"))
        self.assertEqual("materialization_unavailable", outcome.terminal.reason)
