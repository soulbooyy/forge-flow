"""Migration-period compatibility aliases preserve canonical type identity."""

import unittest


class GovernedChangesCompatibilityTest(unittest.TestCase):
    def test_legacy_submodules_alias_semantic_modules(self) -> None:
        from forgeflow.governed_changes.action_execution.models import PolicyDecisionRecord
        from forgeflow.governed_action_sandbox.models import PolicyDecisionRecord as LegacyDecision
        from forgeflow.governed_changes.artifact_security.models import PatchArtifact
        from forgeflow.deterministic_patch_artifact_security.models import PatchArtifact as LegacyArtifact
        from forgeflow.governed_changes.approval_trace.models import DurableRunSummary
        from forgeflow.approval_trace_durable_summary.models import DurableRunSummary as LegacySummary
        from forgeflow.governed_changes.draft_pr.models import DraftPRRequest
        from forgeflow.fixture_github_draft_pr_adapter.models import DraftPRRequest as LegacyRequest
        from forgeflow.governed_changes.materialization.models import MaterializationPDR
        from forgeflow.controlled_materialization_payload_simulation.models import MaterializationPDR as LegacyPDR
        from forgeflow.governed_changes.real_mutation.models import RealMutationPDR
        from forgeflow.m4_draft_mvp_real_execution.models import RealMutationPDR as LegacyRealPDR

        self.assertIs(PolicyDecisionRecord, LegacyDecision)
        self.assertIs(PatchArtifact, LegacyArtifact)
        self.assertIs(DurableRunSummary, LegacySummary)
        self.assertIs(DraftPRRequest, LegacyRequest)
        self.assertIs(MaterializationPDR, LegacyPDR)
        self.assertIs(RealMutationPDR, LegacyRealPDR)
