"""Tests for metadata-only M2-to-Feature-2 service assembly."""

from __future__ import annotations

from dataclasses import replace
from unittest.mock import patch
import unittest

from forgeflow.deterministic_patch_artifact_security.canonical import scan_id_for
from forgeflow.deterministic_patch_artifact_security.models import (
    DeterministicPatchArtifactSecurityValidationError,
    SecretScanResult,
)
from forgeflow.deterministic_patch_artifact_security.service import (
    build_patch_security_facts,
)
from forgeflow.patch_proposal.canonical import (
    candidate_digest_for,
    policy_decision_id_for,
    proposal_id_for,
)
from forgeflow.patch_proposal.models import (
    CandidateChange,
    FixStrategy,
    PatchProposal,
    PolicyDecisionRef,
    RootCauseHypothesis,
    TaskInput,
)


_REPOSITORY_ID = "fixture-repository-1300511729"
_BASE_REVISION = "97c8220cd713ebf61124ac2de2f3eadc6e4dc222"


def _proposal(*, rationale: str = "Correct the nullable state boundary.") -> PatchProposal:
    change = CandidateChange(
        path="src/payment_handler.py",
        change_kind="modify_existing_file",
        rationale=rationale,
        supporting_evidence_ref_ids=("ev_sha256:" + "a" * 64,),
    )
    provisional_decision = PolicyDecisionRef(
        decision_id="pdr_sha256:" + "0" * 64,
        decision="allowed",
        policy_profile_id="patch-proposal/m2-conservative-v1",
        policy_version=1,
        evaluator_id="m2/deterministic-boundary-evaluator-v1",
        evaluated_candidate_digest=candidate_digest_for((change,)),
        risk_flags=(),
        revalidation_required=True,
    )
    decision = replace(
        provisional_decision,
        decision_id=policy_decision_id_for(provisional_decision),
    )
    provisional = PatchProposal(
        contract_id="pp_sha256:" + "0" * 64,
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
            summary="Correct nullable payment state behavior.",
            constraint_codes=(
                "evidence_backed",
                "minimal_change",
                "no_execution",
                "policy_bounded",
            ),
        ),
        candidate_changes=(change,),
        policy_decision=decision,
        risk_flags=(),
        limitation_codes=(
            "fixture_only_source",
            "no_diff_generated",
            "no_source_payload",
            "no_validation_executed",
        ),
    )
    return replace(provisional, contract_id=proposal_id_for(provisional))


class PatchSecurityServiceTests(unittest.TestCase):
    def test_clean_proposal_builds_only_metadata_facts_and_candidate(self) -> None:
        result = build_patch_security_facts(_proposal(), _REPOSITORY_ID, _BASE_REVISION)

        self.assertNotIsInstance(result, DeterministicPatchArtifactSecurityValidationError)
        intent, artifact, scan, redaction, candidate = result
        self.assertEqual(intent.repository_identity, _REPOSITORY_ID)
        self.assertEqual(artifact.base_revision, _BASE_REVISION)
        self.assertEqual(scan.result, "passed")
        self.assertEqual(redaction.status, "not_needed")
        self.assertIsNotNone(candidate)
        self.assertFalse(hasattr(artifact, "raw_patch_content"))

    def test_secret_like_metadata_blocks_without_candidate(self) -> None:
        result = build_patch_security_facts(
            _proposal(rationale="token=ghp_abcdefghijklmnopqrstuvwx"),
            _REPOSITORY_ID,
            _BASE_REVISION,
        )

        self.assertNotIsInstance(result, DeterministicPatchArtifactSecurityValidationError)
        _, _, scan, redaction, candidate = result
        self.assertEqual(scan.result, "blocked")
        self.assertEqual(redaction.status, "redacted")
        self.assertIsNone(candidate)

    def test_invalid_proposal_lineage_returns_safe_error_without_partial_facts(self) -> None:
        invalid = replace(_proposal(), contract_id="pp_sha256:" + "f" * 64)

        result = build_patch_security_facts(invalid, _REPOSITORY_ID, _BASE_REVISION)

        self.assertIsInstance(result, DeterministicPatchArtifactSecurityValidationError)
        self.assertEqual(result.summary, "metadata security input is invalid")
        self.assertFalse(hasattr(result, "patch_artifact"))

    def test_invalid_repository_binding_returns_safe_error(self) -> None:
        result = build_patch_security_facts(_proposal(), "", _BASE_REVISION)

        self.assertIsInstance(result, DeterministicPatchArtifactSecurityValidationError)
        self.assertEqual(result.summary, "metadata security input is invalid")

    def test_unregistered_repository_or_base_revision_returns_safe_error(self) -> None:
        for repository_identity, base_revision in (
            ("fixture-repository-other", _BASE_REVISION),
            (_REPOSITORY_ID, "0" * 40),
        ):
            with self.subTest(repository_identity=repository_identity):
                result = build_patch_security_facts(
                    _proposal(), repository_identity, base_revision
                )
                self.assertIsInstance(
                    result, DeterministicPatchArtifactSecurityValidationError
                )

    def test_unregistered_m2_policy_or_missing_provenance_is_rejected(self) -> None:
        proposal = _proposal()
        altered_policy = proposal.policy_decision
        object.__setattr__(altered_policy, "evaluator_id", "unregistered-evaluator")
        object.__setattr__(
            altered_policy,
            "decision_id",
            policy_decision_id_for(altered_policy),
        )
        altered = replace(proposal, policy_decision=altered_policy)
        altered = replace(altered, contract_id=proposal_id_for(altered))

        result = build_patch_security_facts(altered, _REPOSITORY_ID, _BASE_REVISION)
        self.assertIsInstance(result, DeterministicPatchArtifactSecurityValidationError)

        missing_provenance = replace(_proposal(), limitation_codes=())
        missing_provenance = replace(
            missing_provenance,
            contract_id=proposal_id_for(missing_provenance),
        )
        result = build_patch_security_facts(
            missing_provenance, _REPOSITORY_ID, _BASE_REVISION
        )
        self.assertIsInstance(result, DeterministicPatchArtifactSecurityValidationError)

    def test_scanner_failed_fact_is_fail_closed(self) -> None:
        proposal = _proposal()
        result = build_patch_security_facts(proposal, _REPOSITORY_ID, _BASE_REVISION)
        self.assertNotIsInstance(result, DeterministicPatchArtifactSecurityValidationError)
        intent, artifact, _, _, _ = result
        provisional = SecretScanResult(
            contract_version=intent.contract_version,
            scan_id="sha256:" + "0" * 64,
            artifact_id=artifact.artifact_id,
            rule_set_id="m4-patch-metadata-secret-scan-v1",
            scanner_version="deterministic-metadata-scanner-v1",
            result="failed",
            findings_summary=(),
            failure_reason="scanner_operation_failed",
        )
        failed_scan = replace(provisional, scan_id=scan_id_for(provisional))

        with patch(
            "forgeflow.deterministic_patch_artifact_security.service.scan_metadata",
            return_value=failed_scan,
        ):
            result = build_patch_security_facts(proposal, _REPOSITORY_ID, _BASE_REVISION)

        self.assertNotIsInstance(result, DeterministicPatchArtifactSecurityValidationError)
        _, _, scan, redaction, candidate = result
        self.assertEqual(scan.result, "failed")
        self.assertEqual(redaction.status, "failed")
        self.assertIsNone(candidate)

    def test_indeterminate_scanner_fact_is_fail_closed(self) -> None:
        proposal = _proposal()
        result = build_patch_security_facts(proposal, _REPOSITORY_ID, _BASE_REVISION)
        self.assertNotIsInstance(result, DeterministicPatchArtifactSecurityValidationError)
        intent, artifact, _, _, _ = result
        provisional = SecretScanResult(
            contract_version=intent.contract_version,
            scan_id="sha256:" + "0" * 64,
            artifact_id=artifact.artifact_id,
            rule_set_id="m4-patch-metadata-secret-scan-v1",
            scanner_version="deterministic-metadata-scanner-v1",
            result="indeterminate",
            findings_summary=(),
            failure_reason="metadata_projection_invalid",
        )
        indeterminate_scan = replace(provisional, scan_id=scan_id_for(provisional))

        with patch(
            "forgeflow.deterministic_patch_artifact_security.service.scan_metadata",
            return_value=indeterminate_scan,
        ):
            result = build_patch_security_facts(proposal, _REPOSITORY_ID, _BASE_REVISION)

        self.assertNotIsInstance(result, DeterministicPatchArtifactSecurityValidationError)
        _, _, scan, redaction, candidate = result
        self.assertEqual(scan.result, "indeterminate")
        self.assertEqual(redaction.status, "indeterminate")
        self.assertIsNone(candidate)


if __name__ == "__main__":
    unittest.main()
