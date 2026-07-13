from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path
import sys
import unittest


sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from forgeflow.patch_proposal import (  # noqa: E402
    FixtureCandidateChangeDraft,
    FixtureProposalDraft,
    FixtureRootCauseDraft,
    PatchProposal,
    PatchProposalValidationError,
    TaskInput,
    build_patch_proposal,
    canonical_bytes,
    load_fixture_draft,
)
from forgeflow.repository_context.models import (  # noqa: E402
    BoundedOptionalInput,
    CandidateCounts,
    EvidenceRef,
    InputSummary,
    NormalizedInput,
    RepositoryContextResult,
    ReturnedCounts,
    RunCounts,
    RunSummary,
    WorkspaceRef,
)


ROOT = Path(__file__).resolve().parents[2]
EXPECTED = (
    ROOT
    / "openspec"
    / "changes"
    / "structured-patch-proposal"
    / "fixtures"
    / "expected"
    / "phase-4-acceptance"
)
EVIDENCE_ID = "ev_sha256:" + "a" * 64


def context(*, evidence_ids: tuple[str, ...] = (EVIDENCE_ID,)) -> RepositoryContextResult:
    evidence_refs = tuple(
        EvidenceRef(
            id=evidence_id,
            evidence_kind="filename_match",
            retrieval_signal="filename_match",
            locator=None,
            path="src/payment_handler.py",
        )
        for evidence_id in evidence_ids
    )
    return RepositoryContextResult(
        contract_id="rcr_sha256:" + "b" * 64,
        workspace_ref=WorkspaceRef(root_id="m2-fixture-workspace"),
        query=NormalizedInput(normalized="payment"),
        issue_text=BoundedOptionalInput(False, "", False),
        run_summary=RunSummary(
            operation_type="repository_context",
            completion_status="completed",
            input_summary=InputSummary(
                workspace_root_id="m2-fixture-workspace",
                configuration_profile_id="repository-context/m1-defaults-v1",
                query_normalized="payment",
                issue_text_present=False,
                issue_text_truncated=False,
                normalization_id="m1/nfc-whitespace-casefold-v1",
                limit_profile_id="repository-context/m1-defaults-v1",
                ignore_policy_id="repository-context/m1-defaults-v1",
            ),
            counts=RunCounts(
                discovered_files=1,
                discovered_directories=1,
                scanned_text_files=1,
                skipped_files=0,
                skipped_directories=0,
                candidates=CandidateCounts(0, 0, len(evidence_refs), 0),
                returned=ReturnedCounts(0, 0, len(evidence_refs), 0, 0),
            ),
        ),
        evidence_refs=evidence_refs,
    )


def task_input() -> TaskInput:
    return TaskInput(task_ref="M2-004", summary="Guard missing payment state")


def draft(*, path: str = "src/payment_handler.py", evidence_id: str = EVIDENCE_ID) -> FixtureProposalDraft:
    return FixtureProposalDraft(
        root_cause_hypotheses=(
            FixtureRootCauseDraft(
                statement="Payment state can be absent at the handler boundary.",
                uncertainty="medium",
                supporting_evidence_ref_ids=(evidence_id,),
            ),
        ),
        fix_strategy_summary="Add the smallest evidence-backed guard and focused test.",
        candidate_changes=(
            FixtureCandidateChangeDraft(
                path=path,
                change_kind="modify_existing_file",
                rationale="Guard the missing payment state before dereferencing it.",
                supporting_evidence_ref_ids=(evidence_id,),
            ),
        ),
    )


class PatchProposalAcceptanceTests(unittest.TestCase):
    def test_equivalent_public_service_runs_are_canonical_and_deterministic(self) -> None:
        first = build_patch_proposal(context(), task_input(), load_fixture_draft("valid-default"))
        second = build_patch_proposal(context(), task_input(), load_fixture_draft("valid-default"))

        self.assertIsInstance(first, PatchProposal)
        self.assertEqual(canonical_bytes(first), canonical_bytes(second))
        self.assertEqual(first.contract_id, second.contract_id)
        self.assertEqual(first.policy_decision.decision_id, second.policy_decision.decision_id)
        self.assertRegex(first.contract_id, r"^pp_sha256:[0-9a-f]{64}$")
        self.assertRegex(first.policy_decision.decision_id, r"^pdr_sha256:[0-9a-f]{64}$")

    def test_every_successful_intent_reference_closes_over_m1_evidence(self) -> None:
        result = build_patch_proposal(context(), task_input(), draft())

        self.assertIsInstance(result, PatchProposal)
        available_ids = {reference.id for reference in context().evidence_refs}
        declared_ids = {
            evidence_id
            for hypothesis in result.root_cause_hypotheses
            for evidence_id in hypothesis.supporting_evidence_ref_ids
        } | {
            evidence_id
            for candidate in result.candidate_changes
            for evidence_id in candidate.supporting_evidence_ref_ids
        }
        self.assertTrue(declared_ids)
        self.assertTrue(declared_ids <= available_ids)

        dangling = build_patch_proposal(context(evidence_ids=()), task_input(), draft())
        self.assertIsInstance(dangling, PatchProposalValidationError)
        self.assertEqual(dangling.error_code, "dangling_evidence_ref")

    def test_policy_outcomes_preserve_success_and_terminal_boundaries(self) -> None:
        allowed = build_patch_proposal(context(), task_input(), draft())
        approval_required = build_patch_proposal(
            context(), task_input(), draft(path="config/.env.production")
        )
        blocked = build_patch_proposal(
            context(), task_input(), draft(path="secrets/production.json")
        )

        self.assertIsInstance(allowed, PatchProposal)
        self.assertEqual(allowed.policy_decision.decision, "allowed")
        self.assertIsInstance(approval_required, PatchProposal)
        self.assertEqual(approval_required.policy_decision.decision, "requires_human_approval")
        self.assertIn("policy_requires_human_approval", approval_required.risk_flags)
        self.assertIsInstance(blocked, PatchProposalValidationError)
        self.assertEqual(blocked.error_code, "policy_blocked")
        self.assertFalse(hasattr(blocked, "candidate_changes"))

    def test_policy_binding_requires_revalidation_for_changed_intent(self) -> None:
        original = build_patch_proposal(context(), task_input(), draft())
        changed = build_patch_proposal(
            context(),
            task_input(),
            replace(
                draft(),
                candidate_changes=(
                    FixtureCandidateChangeDraft(
                        path="src/payment_handler.py",
                        change_kind="modify_existing_file",
                        rationale="Validate state before the handler uses it.",
                        supporting_evidence_ref_ids=(EVIDENCE_ID,),
                    ),
                ),
            ),
        )

        self.assertIsInstance(original, PatchProposal)
        self.assertIsInstance(changed, PatchProposal)
        self.assertTrue(original.policy_decision.revalidation_required)
        self.assertTrue(changed.policy_decision.revalidation_required)
        self.assertNotEqual(original.contract_id, changed.contract_id)
        self.assertNotEqual(
            original.policy_decision.evaluated_candidate_digest,
            changed.policy_decision.evaluated_candidate_digest,
        )

    def test_terminal_error_excludes_raw_payload_and_success_fields(self) -> None:
        secret = "m2-fixture-secret-must-not-escape"
        result = build_patch_proposal(context(), task_input(), {"raw_payload": secret})

        self.assertIsInstance(result, PatchProposalValidationError)
        self.assertEqual(result.error_code, "raw_payload_forbidden")
        self.assertFalse(hasattr(result, "candidate_changes"))
        self.assertNotIn(secret, canonical_bytes(result).decode("utf-8"))
        self.assertNotIn("m2-fixture-secret", canonical_bytes(result).decode("utf-8"))

    def test_expected_public_service_fragments_are_payload_free(self) -> None:
        success = build_patch_proposal(context(), task_input(), load_fixture_draft("valid-default"))
        error = build_patch_proposal(
            context(), task_input(), {"raw_payload": "m2-fixture-secret-must-not-escape"}
        )

        self.assertEqual(
            json.loads(canonical_bytes(success)),
            json.loads((EXPECTED / "result-fragment.json").read_text(encoding="utf-8")),
        )
        self.assertEqual(
            json.loads(canonical_bytes(error)),
            json.loads((EXPECTED / "validation-error-fragment.json").read_text(encoding="utf-8")),
        )


if __name__ == "__main__":
    unittest.main()
