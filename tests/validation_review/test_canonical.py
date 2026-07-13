from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import sys
import unittest


sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from forgeflow.validation_review import (  # noqa: E402
    PolicyDecisionRecordRef,
    ValidationResult,
    canonical_bytes,
    policy_decision_id_for,
    validation_result_id_for,
)


class ValidationReviewCanonicalTests(unittest.TestCase):
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
