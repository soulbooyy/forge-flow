from __future__ import annotations

from dataclasses import FrozenInstanceError, fields
from pathlib import Path
import sys
import unittest


sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from forgeflow.validation_review import (  # noqa: E402
    PolicyDecisionRecordRef,
    ReviewFinding,
    ReviewResult,
    ValidationResult,
    ValidationReviewError,
    ValidationReviewErrorSummary,
    ValidationTerminal,
)


PATCH_PROPOSAL_ID = "pp_sha256:" + "1" * 64
ATTEMPT_ID = "m3a_sha256:" + "2" * 64
POLICY_DECISION_ID = "pdr_sha256:" + "3" * 64
EVIDENCE_ID = "ev_sha256:" + "4" * 64
ARTIFACT_ID = "artifact_sha256:" + "5" * 64


def allowed_policy_record(subject_contract_id: str = PATCH_PROPOSAL_ID) -> PolicyDecisionRecordRef:
    return PolicyDecisionRecordRef(
        decision_id=POLICY_DECISION_ID,
        decision="allowed",
        policy_profile_id="validation-review/m3-fixture-v1",
        policy_version=1,
        evaluator_id="m3/deterministic-policy-fixture-v1",
        subject_contract_id=subject_contract_id,
        risk_flags=(),
    )


class ValidationReviewContractTests(unittest.TestCase):
    def test_validation_result_is_frozen_slotted_and_contains_completed_attempt_facts(self) -> None:
        result = ValidationResult(
            contract_id="vr_sha256:" + "6" * 64,
            patch_proposal_contract_id=PATCH_PROPOSAL_ID,
            attempt_id=ATTEMPT_ID,
            fixture_case_id="passed-default",
            outcome="passed",
            finding_codes=(),
            policy_decision_refs=(allowed_policy_record(),),
            evidence_ref_ids=(EVIDENCE_ID,),
            artifact_ids=(ARTIFACT_ID,),
        )

        self.assertEqual(result.schema_version, "validation-result/v1")
        self.assertEqual(result.result_type, "validation_result")
        self.assertFalse(hasattr(result, "__dict__"))
        with self.assertRaises(FrozenInstanceError):
            result.outcome = "failed"  # type: ignore[misc]
        self.assertFalse(
            {"command", "exit_code", "stdout", "stderr", "output", "retry_count"}
            & {item.name for item in fields(result)}
        )

    def test_validation_terminal_has_no_attempt_or_execution_fact(self) -> None:
        terminal = ValidationTerminal(
            terminal_id="vt_sha256:" + "7" * 64,
            patch_proposal_contract_id=PATCH_PROPOSAL_ID,
            terminal_reason="policy_blocked",
            policy_decision_refs=(
                PolicyDecisionRecordRef(
                    decision_id=POLICY_DECISION_ID,
                    decision="blocked",
                    policy_profile_id="validation-review/m3-fixture-v1",
                    policy_version=1,
                    evaluator_id="m3/deterministic-policy-fixture-v1",
                    subject_contract_id=PATCH_PROPOSAL_ID,
                    risk_flags=("blocked_by_policy",),
                ),
            ),
            evidence_ref_ids=(EVIDENCE_ID,),
            artifact_ids=(),
        )

        self.assertEqual(terminal.schema_version, "validation-terminal/v1")
        self.assertEqual(terminal.result_type, "validation_terminal")
        terminal_fields = {item.name for item in fields(terminal)}
        self.assertFalse(
            {"attempt_id", "fixture_case_id", "outcome", "command", "exit_code", "output"}
            & terminal_fields
        )

    def test_review_result_records_findings_without_governance_outcome(self) -> None:
        result = ReviewResult(
            contract_id="rr_sha256:" + "8" * 64,
            patch_proposal_contract_id=PATCH_PROPOSAL_ID,
            validation_result_contract_id="vr_sha256:" + "6" * 64,
            findings=(
                ReviewFinding(
                    finding_code="validation_failure_requires_review",
                    severity="blocking",
                    evidence_ref_ids=(EVIDENCE_ID,),
                ),
            ),
            policy_decision_refs=(allowed_policy_record("vr_sha256:" + "6" * 64),),
            evidence_ref_ids=(EVIDENCE_ID,),
            artifact_ids=(),
        )

        self.assertEqual(result.schema_version, "review-result/v1")
        self.assertEqual(result.result_type, "review_result")
        self.assertFalse(
            {
                "decision",
                "blocked",
                "requires_human_approval",
                "approved_for_pr",
                "retry_count",
            }
            & {item.name for item in fields(result)}
        )

    def test_error_is_separate_from_terminal_result_and_review(self) -> None:
        error = ValidationReviewError(
            error_id="vre_sha256:" + "9" * 64,
            error_code="forbidden_payload",
            message="Fixture payload field is forbidden.",
            summary=ValidationReviewErrorSummary(
                patch_proposal_contract_id=PATCH_PROPOSAL_ID,
                fixture_case_id="passed-default",
                policy_profile_id="validation-review/m3-fixture-v1",
            ),
        )

        self.assertEqual(error.schema_version, "validation-review-error/v1")
        self.assertEqual(error.result_type, "validation_review_error")
        self.assertEqual(error.completion_status, "validation_error")
        self.assertFalse(
            {
                "attempt_id",
                "terminal_reason",
                "findings",
                "policy_decision_refs",
            }
            & {item.name for item in fields(error)}
        )

    def test_contracts_reject_incompatible_terminal_and_policy_lineage(self) -> None:
        with self.assertRaises(ValueError):
            ValidationTerminal(
                terminal_id="vt_sha256:" + "7" * 64,
                patch_proposal_contract_id=PATCH_PROPOSAL_ID,
                terminal_reason="human_approval_required",
                policy_decision_refs=(
                    PolicyDecisionRecordRef(
                        decision_id=POLICY_DECISION_ID,
                        decision="blocked",
                        policy_profile_id="validation-review/m3-fixture-v1",
                        policy_version=1,
                        evaluator_id="m3/deterministic-policy-fixture-v1",
                        subject_contract_id=PATCH_PROPOSAL_ID,
                        risk_flags=(),
                    ),
                ),
                evidence_ref_ids=(EVIDENCE_ID,),
                artifact_ids=(),
            )
