from __future__ import annotations

import json
from pathlib import Path
import re
import sys
import unittest


sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from forgeflow.patch_proposal import (  # noqa: E402
    CandidateChange,
    FixStrategy,
    PatchProposal,
    PatchProposalValidationError,
    PolicyDecisionRef,
    RootCauseHypothesis,
    TaskInput,
    ValidationErrorSummary,
    candidate_digest_for,
    canonical_bytes,
    policy_decision_id_for,
    proposal_error_id_for,
    proposal_id_for,
    sha256_hex,
)


ROOT = Path(__file__).resolve().parents[2]
EXPECTED = (
    ROOT
    / "openspec"
    / "changes"
    / "structured-patch-proposal"
    / "fixtures"
    / "expected"
    / "phase-1-contract"
)


def make_candidate(*, rationale: str = "Add a focused guard for the nullable state.") -> CandidateChange:
    return CandidateChange(
        path="src/payment_handler.py",
        change_kind="modify_existing_file",
        rationale=rationale,
        supporting_evidence_ref_ids=("ev_sha256:" + "a" * 64,),
    )


def make_policy_decision(*, decision_id: str = "pdr_sha256:" + "c" * 64, rationale: str = "Add a focused guard for the nullable state.") -> PolicyDecisionRef:
    candidate = make_candidate(rationale=rationale)
    return PolicyDecisionRef(
        decision_id=decision_id,
        decision="allowed",
        policy_profile_id="patch-proposal/m2-conservative-v1",
        policy_version=1,
        evaluator_id="m2/deterministic-boundary-evaluator-v1",
        evaluated_candidate_digest=candidate_digest_for((candidate,)),
        risk_flags=(),
        revalidation_required=True,
    )


def make_proposal(*, contract_id: str = "pp_sha256:" + "d" * 64, rationale: str = "Add a focused guard for the nullable state.") -> PatchProposal:
    candidate = make_candidate(rationale=rationale)
    policy = make_policy_decision(rationale=rationale)
    policy = PolicyDecisionRef(
        decision_id=policy_decision_id_for(policy),
        decision=policy.decision,
        policy_profile_id=policy.policy_profile_id,
        policy_version=policy.policy_version,
        evaluator_id=policy.evaluator_id,
        evaluated_candidate_digest=policy.evaluated_candidate_digest,
        risk_flags=policy.risk_flags,
        revalidation_required=policy.revalidation_required,
    )
    return PatchProposal(
        contract_id=contract_id,
        proposal_source_id="m2/deterministic-fixture-v1",
        repository_context_contract_id="rcr_sha256:" + "b" * 64,
        task_input=TaskInput(task_ref="M2-001", summary="Guard nullable payment state"),
        root_cause_hypotheses=(
            RootCauseHypothesis(
                statement="Payment state can be absent at the handler boundary.",
                uncertainty="medium",
                supporting_evidence_ref_ids=("ev_sha256:" + "a" * 64,),
            ),
        ),
        fix_strategy=FixStrategy(
            summary="Add the smallest evidence-backed guard and focused test.",
            constraint_codes=(
                "evidence_backed",
                "minimal_change",
                "no_execution",
                "policy_bounded",
            ),
        ),
        candidate_changes=(candidate,),
        risk_flags=(),
        limitation_codes=(
            "fixture_only_source",
            "no_diff_generated",
            "no_source_payload",
            "no_validation_executed",
        ),
        policy_decision=policy,
    )


def make_error(*, error_id: str = "ppe_sha256:" + "e" * 64, message: str = "Task input is invalid.") -> PatchProposalValidationError:
    return PatchProposalValidationError(
        error_id=error_id,
        error_code="invalid_task_input",
        input_category="task_input",
        message=message,
        summary=ValidationErrorSummary(
            repository_context_contract_id="rcr_sha256:" + "b" * 64,
            task_ref="M2-001",
            policy_profile_id="patch-proposal/m2-conservative-v1",
        ),
    )


class PatchProposalCanonicalTests(unittest.TestCase):
    def test_canonical_json_is_sorted_compact_utf8_and_rejects_floats(self) -> None:
        self.assertEqual(canonical_bytes({"z": "café", "a": "汉字"}), b'{"a":"\xe6\xb1\x89\xe5\xad\x97","z":"caf\xc3\xa9"}')
        self.assertEqual(canonical_bytes(("third", "second")), b'["third","second"]')
        with self.assertRaises(TypeError):
            canonical_bytes({"value": 1.5})
        with self.assertRaises(TypeError):
            canonical_bytes(object())

    def test_proposal_and_error_ids_are_self_excluding_and_content_bound(self) -> None:
        first = make_proposal(contract_id="pp_sha256:" + "1" * 64)
        same = make_proposal(contract_id="pp_sha256:" + "2" * 64)
        changed = make_proposal(rationale="Use a different evidence-backed guard.")
        first_error = make_error(error_id="ppe_sha256:" + "3" * 64)
        same_error = make_error(error_id="ppe_sha256:" + "4" * 64)
        changed_error = make_error(message="Task input summary exceeds the allowed bound.")

        self.assertEqual(proposal_id_for(first), proposal_id_for(same))
        self.assertNotEqual(proposal_id_for(first), proposal_id_for(changed))
        self.assertEqual(proposal_error_id_for(first_error), proposal_error_id_for(same_error))
        self.assertNotEqual(proposal_error_id_for(first_error), proposal_error_id_for(changed_error))

    def test_candidate_digest_and_policy_identity_bind_ordered_candidate_content(self) -> None:
        first_candidate = make_candidate()
        changed_candidate = make_candidate(rationale="Use a different evidence-backed guard.")
        first_policy = make_policy_decision(decision_id="pdr_sha256:" + "5" * 64)
        same_policy = make_policy_decision(decision_id="pdr_sha256:" + "6" * 64)
        changed_policy = make_policy_decision(rationale="Use a different evidence-backed guard.")

        self.assertRegex(candidate_digest_for((first_candidate,)), r"^sha256:[0-9a-f]{64}$")
        self.assertNotEqual(
            candidate_digest_for((first_candidate,)),
            candidate_digest_for((changed_candidate,)),
        )
        self.assertEqual(policy_decision_id_for(first_policy), policy_decision_id_for(same_policy))
        self.assertNotEqual(policy_decision_id_for(first_policy), policy_decision_id_for(changed_policy))

    def test_contract_fixtures_lock_complete_payload_free_envelopes(self) -> None:
        proposal = make_proposal()
        proposal = PatchProposal(
            contract_id=proposal_id_for(proposal),
            proposal_source_id=proposal.proposal_source_id,
            repository_context_contract_id=proposal.repository_context_contract_id,
            task_input=proposal.task_input,
            root_cause_hypotheses=proposal.root_cause_hypotheses,
            fix_strategy=proposal.fix_strategy,
            candidate_changes=proposal.candidate_changes,
            risk_flags=proposal.risk_flags,
            limitation_codes=proposal.limitation_codes,
            policy_decision=proposal.policy_decision,
        )
        error = make_error()
        error = PatchProposalValidationError(
            error_id=proposal_error_id_for(error),
            error_code=error.error_code,
            input_category=error.input_category,
            message=error.message,
            summary=error.summary,
        )

        self.assertEqual(
            json.loads(canonical_bytes(proposal)),
            json.loads((EXPECTED / "success-envelope.json").read_text(encoding="utf-8")),
        )
        self.assertEqual(
            json.loads(canonical_bytes(error)),
            json.loads((EXPECTED / "validation-error.json").read_text(encoding="utf-8")),
        )
        self.assertEqual(sha256_hex(proposal), sha256_hex(proposal))


if __name__ == "__main__":
    unittest.main()
