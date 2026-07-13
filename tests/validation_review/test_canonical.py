from __future__ import annotations

from dataclasses import asdict, replace
import json
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
    canonical_bytes,
    policy_decision_id_for,
    review_result_id_for,
    validation_result_id_for,
    validation_review_error_id_for,
    validation_terminal_id_for,
)


class ValidationReviewCanonicalTests(unittest.TestCase):
    def test_phase_1_expected_fixtures_match_reconstructed_contracts_and_ids(self) -> None:
        fixture_directory = (
            Path(__file__).resolve().parents[2]
            / "openspec/changes/validation-review-slice/fixtures/expected/phase-1-contract"
        )

        result_data = json.loads((fixture_directory / "validation-result.json").read_text())
        result = ValidationResult(
            **{
                **result_data,
                "policy_decision_refs": tuple(
                    self._policy_ref_from_json(item) for item in result_data["policy_decision_refs"]
                ),
                "evidence_ref_ids": tuple(result_data["evidence_ref_ids"]),
                "artifact_ids": tuple(result_data["artifact_ids"]),
                "finding_codes": tuple(result_data["finding_codes"]),
            }
        )
        self.assertEqual(self._json_value(asdict(result)), result_data)
        self.assertEqual(validation_result_id_for(result), result.contract_id)

        terminal_data = json.loads((fixture_directory / "validation-terminal.json").read_text())
        terminal = ValidationTerminal(
            **{
                **terminal_data,
                "policy_decision_refs": tuple(
                    self._policy_ref_from_json(item) for item in terminal_data["policy_decision_refs"]
                ),
                "evidence_ref_ids": tuple(terminal_data["evidence_ref_ids"]),
                "artifact_ids": tuple(terminal_data["artifact_ids"]),
            }
        )
        self.assertEqual(self._json_value(asdict(terminal)), terminal_data)
        self.assertEqual(validation_terminal_id_for(terminal), terminal.terminal_id)

        review_data = json.loads((fixture_directory / "review-result.json").read_text())
        review = ReviewResult(
            **{
                **review_data,
                "findings": tuple(
                    ReviewFinding(
                        **{**item, "evidence_ref_ids": tuple(item["evidence_ref_ids"])}
                    )
                    for item in review_data["findings"]
                ),
                "policy_decision_refs": tuple(
                    self._policy_ref_from_json(item) for item in review_data["policy_decision_refs"]
                ),
                "evidence_ref_ids": tuple(review_data["evidence_ref_ids"]),
                "artifact_ids": tuple(review_data["artifact_ids"]),
            }
        )
        self.assertEqual(self._json_value(asdict(review)), review_data)
        self.assertEqual(review_result_id_for(review), review.contract_id)

        error_data = json.loads((fixture_directory / "validation-review-error.json").read_text())
        error = ValidationReviewError(
            **{
                **error_data,
                "summary": ValidationReviewErrorSummary(**error_data["summary"]),
            }
        )
        self.assertEqual(self._json_value(asdict(error)), error_data)
        self.assertEqual(validation_review_error_id_for(error), error.error_id)

    @staticmethod
    def _policy_ref_from_json(value: dict[str, object]) -> PolicyDecisionRecordRef:
        return PolicyDecisionRecordRef(
            **{**value, "risk_flags": tuple(value["risk_flags"])}  # type: ignore[arg-type]
        )

    @staticmethod
    def _json_value(value: object) -> object:
        return json.loads(json.dumps(value))

    def test_validation_result_identity_omits_only_its_contract_id(self) -> None:
        policy = PolicyDecisionRecordRef(
            decision_id="pdr_sha256:" + "1" * 64,
            decision="allowed",
            policy_profile_id="validation-review/m3-fixture-v1",
            policy_version=1,
            evaluator_id="m3/deterministic-policy-fixture-v1",
            subject_contract_id="pp_sha256:" + "2" * 64,
            risk_flags=(),
        )
        result = ValidationResult(
            contract_id="vr_sha256:" + "3" * 64,
            patch_proposal_contract_id="pp_sha256:" + "2" * 64,
            attempt_id="m3a_sha256:" + "4" * 64,
            fixture_case_id="failed-default",
            outcome="failed",
            finding_codes=("fixture_assertion_failed",),
            policy_decision_refs=(policy,),
            evidence_ref_ids=("ev_sha256:" + "5" * 64,),
            artifact_ids=(),
        )

        self.assertEqual(validation_result_id_for(result), validation_result_id_for(result))
        self.assertNotEqual(
            validation_result_id_for(result),
            validation_result_id_for(replace(result, outcome="passed", finding_codes=())),
        )
        self.assertTrue(validation_result_id_for(result).startswith("vr_sha256:"))

    def test_policy_identity_changes_with_decision_and_canonical_bytes_are_stable(self) -> None:
        allowed = PolicyDecisionRecordRef(
            decision_id="pdr_sha256:" + "6" * 64,
            decision="allowed",
            policy_profile_id="validation-review/m3-fixture-v1",
            policy_version=1,
            evaluator_id="m3/deterministic-policy-fixture-v1",
            subject_contract_id="pp_sha256:" + "7" * 64,
            risk_flags=(),
        )
        blocked = replace(allowed, decision="blocked", risk_flags=("blocked_by_policy",))

        self.assertTrue(policy_decision_id_for(allowed).startswith("pdr_sha256:"))
        self.assertNotEqual(policy_decision_id_for(allowed), policy_decision_id_for(blocked))
        self.assertEqual(
            canonical_bytes({"b": ["x"], "a": 1}),
            b'{"a":1,"b":["x"]}',
        )
