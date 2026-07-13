from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch


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
    / "phase-3-source"
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
    return TaskInput(task_ref="M2-003", summary="Guard missing payment state")


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


class PatchProposalServiceTests(unittest.TestCase):
    def test_valid_fixture_builds_a_complete_evidence_backed_proposal(self) -> None:
        result = build_patch_proposal(context(), task_input(), load_fixture_draft("valid-default"))

        self.assertIsInstance(result, PatchProposal)
        self.assertEqual(result.proposal_source_id, "m2/deterministic-fixture-v1")
        self.assertEqual(result.repository_context_contract_id, context().contract_id)
        self.assertEqual(result.policy_decision.decision, "allowed")
        self.assertEqual(
            result.limitation_codes,
            (
                "fixture_only_source",
                "no_diff_generated",
                "no_source_payload",
                "no_validation_executed",
            ),
        )
        self.assertEqual(
            result.candidate_changes[0].supporting_evidence_ref_ids,
            (EVIDENCE_ID,),
        )
        self.assertRegex(result.contract_id, r"^pp_sha256:[0-9a-f]{64}$")

    def test_approval_required_remains_a_successful_declarative_proposal(self) -> None:
        result = build_patch_proposal(context(), task_input(), draft(path="config/.env.production"))

        self.assertIsInstance(result, PatchProposal)
        self.assertEqual(result.policy_decision.decision, "requires_human_approval")
        self.assertIn("policy_requires_human_approval", result.risk_flags)

    def test_terminal_errors_are_separate_safe_validation_envelopes(self) -> None:
        cases = (
            (object(), task_input(), draft(), "unsupported_repository_context"),
            (
                replace(context(), contract_id="invalid_sha256:" + "b" * 64),
                task_input(),
                draft(),
                "unsupported_repository_context",
            ),
            (context(evidence_ids=()), task_input(), draft(), "dangling_evidence_ref"),
            (context(), task_input(), object(), "fixture_draft_malformed"),
            (context(), task_input(), {"raw_payload": "do-not-leak"}, "raw_payload_forbidden"),
            (context(), task_input(), draft(path="secrets/config.json"), "policy_blocked"),
        )

        for repository_context, task, fixture_draft, error_code in cases:
            with self.subTest(error_code=error_code):
                result = build_patch_proposal(repository_context, task, fixture_draft)
                self.assertIsInstance(result, PatchProposalValidationError)
                self.assertEqual(result.error_code, error_code)
                self.assertFalse(hasattr(result, "candidate_changes"))
                self.assertNotIn("do-not-leak", result.message)

    def test_oversized_draft_maps_to_bounds_error_without_partial_success(self) -> None:
        oversized = replace(
            draft(),
            root_cause_hypotheses=(
                FixtureRootCauseDraft(
                    statement="x" * 501,
                    uncertainty="medium",
                    supporting_evidence_ref_ids=(EVIDENCE_ID,),
                ),
            ),
        )

        result = build_patch_proposal(context(), task_input(), oversized)

        self.assertIsInstance(result, PatchProposalValidationError)
        self.assertEqual(result.error_code, "bounds_exceeded")

    def test_invalid_profile_maps_to_validation_error(self) -> None:
        with patch("forgeflow.patch_proposal.service.M2_CONSERVATIVE_V1", None):
            result = build_patch_proposal(context(), task_input(), draft())

        self.assertIsInstance(result, PatchProposalValidationError)
        self.assertEqual(result.error_code, "invalid_policy_profile")

    def test_expected_fragments_lock_valid_draft_and_malformed_error(self) -> None:
        fixture_draft = load_fixture_draft("valid-default")
        malformed = build_patch_proposal(context(), task_input(), object())

        self.assertEqual(
            json.loads(canonical_bytes(fixture_draft)),
            json.loads((EXPECTED / "valid-draft.json").read_text(encoding="utf-8")),
        )
        self.assertEqual(
            json.loads(canonical_bytes(malformed)),
            json.loads((EXPECTED / "malformed-draft-error.json").read_text(encoding="utf-8")),
        )


if __name__ == "__main__":
    unittest.main()
