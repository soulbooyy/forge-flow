from __future__ import annotations

from dataclasses import FrozenInstanceError, fields
from pathlib import Path
import sys
import unittest


sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from forgeflow.patch_proposal import (  # noqa: E402
    CandidateChange,
    FixStrategy,
    M2_CONSERVATIVE_V1,
    PatchProposal,
    PatchProposalValidationError,
    PolicyDecisionRef,
    RootCauseHypothesis,
    TaskInput,
    ValidationErrorSummary,
)


class PatchProposalContractTests(unittest.TestCase):
    def test_success_contract_is_frozen_slotted_and_uses_required_literals(self) -> None:
        candidate = CandidateChange(
            path="src/payment_handler.py",
            change_kind="modify_existing_file",
            rationale="Guard the missing payment state before dereferencing it.",
            supporting_evidence_ref_ids=("ev_sha256:" + "1" * 64,),
        )
        proposal = PatchProposal(
            contract_id="pp_sha256:" + "2" * 64,
            proposal_source_id="m2/deterministic-fixture-v1",
            repository_context_contract_id="rcr_sha256:" + "3" * 64,
            task_input=TaskInput(task_ref="M2-001", summary="Guard missing payment state"),
            root_cause_hypotheses=(
                RootCauseHypothesis(
                    statement="A nullable payment state is dereferenced.",
                    uncertainty="medium",
                    supporting_evidence_ref_ids=("ev_sha256:" + "1" * 64,),
                ),
            ),
            fix_strategy=FixStrategy(
                summary="Add the smallest evidence-backed guard and a focused test.",
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
            policy_decision=PolicyDecisionRef(
                decision_id="pdr_sha256:" + "4" * 64,
                decision="allowed",
                policy_profile_id="patch-proposal/m2-conservative-v1",
                policy_version=1,
                evaluator_id="m2/deterministic-boundary-evaluator-v1",
                evaluated_candidate_digest="sha256:" + "5" * 64,
                risk_flags=(),
                revalidation_required=True,
            ),
        )

        self.assertEqual(proposal.schema_version, "patch-proposal/v1")
        self.assertEqual(proposal.result_type, "patch_proposal")
        self.assertIsInstance(proposal.root_cause_hypotheses, tuple)
        self.assertIsInstance(proposal.candidate_changes, tuple)
        self.assertFalse(hasattr(proposal, "__dict__"))
        with self.assertRaises(FrozenInstanceError):
            proposal.contract_id = "changed"

    def test_validation_error_is_separate_from_success_fields(self) -> None:
        error = PatchProposalValidationError(
            error_id="ppe_sha256:" + "6" * 64,
            error_code="invalid_task_input",
            input_category="task_input",
            message="Task input summary is empty after normalization.",
            summary=ValidationErrorSummary(
                repository_context_contract_id="rcr_sha256:" + "7" * 64,
                task_ref="M2-001",
                policy_profile_id="patch-proposal/m2-conservative-v1",
            ),
        )

        self.assertEqual(error.schema_version, "patch-proposal-validation-error/v1")
        self.assertEqual(error.result_type, "patch_proposal_validation_error")
        self.assertEqual(error.completion_status, "validation_error")
        error_fields = {field.name for field in fields(error)}
        self.assertNotIn("contract_id", error_fields)
        self.assertFalse(
            {
                "candidate_changes",
                "risk_flags",
                "policy_decision",
                "proposal_source_id",
            }
            & error_fields
        )

    def test_profile_is_exact_immutable_and_provider_neutral(self) -> None:
        self.assertEqual(
            M2_CONSERVATIVE_V1.policy_profile_id,
            "patch-proposal/m2-conservative-v1",
        )
        self.assertEqual(M2_CONSERVATIVE_V1.policy_version, 1)
        self.assertEqual(
            M2_CONSERVATIVE_V1.evaluator_id,
            "m2/deterministic-boundary-evaluator-v1",
        )
        self.assertEqual(M2_CONSERVATIVE_V1.proposal_source_id, "m2/deterministic-fixture-v1")
        self.assertEqual(M2_CONSERVATIVE_V1.max_root_cause_hypotheses, 3)
        self.assertEqual(M2_CONSERVATIVE_V1.max_candidate_changes, 3)
        self.assertEqual(M2_CONSERVATIVE_V1.max_hypothesis_chars, 500)
        self.assertEqual(M2_CONSERVATIVE_V1.max_fix_strategy_chars, 1_000)
        self.assertEqual(M2_CONSERVATIVE_V1.max_candidate_rationale_chars, 500)
        with self.assertRaises(FrozenInstanceError):
            M2_CONSERVATIVE_V1.policy_version = 2

    def test_profile_contains_the_versioned_path_rule_data(self) -> None:
        self.assertEqual(
            M2_CONSERVATIVE_V1.blocked_path_segments,
            ("secrets", "secret", "credentials", "credential"),
        )
        self.assertEqual(
            M2_CONSERVATIVE_V1.blocked_file_suffixes,
            (".pem", ".key", ".p12", ".pfx", ".jks"),
        )
        self.assertEqual(
            M2_CONSERVATIVE_V1.blocked_file_names,
            ("id_rsa", "id_dsa", "id_ecdsa", "id_ed25519"),
        )
        self.assertEqual(M2_CONSERVATIVE_V1.approval_environment_file_names, (".env",))
        self.assertEqual(M2_CONSERVATIVE_V1.approval_environment_file_prefixes, (".env.",))
        self.assertEqual(
            M2_CONSERVATIVE_V1.approval_ci_directory_prefixes,
            (".github/workflows", ".circleci"),
        )
        self.assertEqual(
            M2_CONSERVATIVE_V1.approval_ci_file_names,
            (".gitlab-ci.yml", "Jenkinsfile", "azure-pipelines.yml", "azure-pipelines.yaml"),
        )
        self.assertEqual(
            M2_CONSERVATIVE_V1.approval_infrastructure_path_segments,
            ("deploy", "deployment", "infra", "infrastructure", "k8s", "helm", "terraform"),
        )
        self.assertEqual(M2_CONSERVATIVE_V1.approval_infrastructure_file_suffixes, (".tf",))
        self.assertEqual(
            M2_CONSERVATIVE_V1.approval_auth_path_segments,
            (
                "auth",
                "authentication",
                "authorization",
                "permission",
                "permissions",
                "access-control",
                "access_control",
                "crypto",
                "cryptography",
            ),
        )
        self.assertEqual(
            M2_CONSERVATIVE_V1.approval_migration_directory_prefixes,
            ("migrations", "migration", "db/migrate", "database/migrations"),
        )
        self.assertEqual(
            M2_CONSERVATIVE_V1.approval_lockfile_names,
            (
                "package-lock.json",
                "npm-shrinkwrap.json",
                "yarn.lock",
                "pnpm-lock.yaml",
                "poetry.lock",
                "Pipfile.lock",
                "Cargo.lock",
                "go.sum",
                "Gemfile.lock",
                "composer.lock",
            ),
        )
        self.assertTrue(M2_CONSERVATIVE_V1.approval_required_for_remove_file)

    def test_models_reject_invalid_bounded_literals_and_ordering(self) -> None:
        evidence_id = "ev_sha256:" + "1" * 64

        with self.assertRaises(ValueError):
            TaskInput(task_ref="", summary="Valid summary")
        with self.assertRaises(ValueError):
            TaskInput(task_ref="M2-001", summary="  Not normalized  summary ")
        with self.assertRaises(ValueError):
            RootCauseHypothesis(
                statement="A cause",
                uncertainty="certain",  # type: ignore[arg-type]
                supporting_evidence_ref_ids=(evidence_id,),
            )
        with self.assertRaises(ValueError):
            RootCauseHypothesis(
                statement="A cause",
                uncertainty="low",
                supporting_evidence_ref_ids=(evidence_id, evidence_id),
            )
        with self.assertRaises(ValueError):
            FixStrategy(
                summary="A strategy",
                constraint_codes=("minimal_change", "evidence_backed"),
            )
        with self.assertRaises(ValueError):
            CandidateChange(
                path="../outside.py",
                change_kind="modify_existing_file",
                rationale="A bounded rationale",
                supporting_evidence_ref_ids=(evidence_id,),
            )
        with self.assertRaises(ValueError):
            CandidateChange(
                path="src/example.py",
                change_kind="execute_command",  # type: ignore[arg-type]
                rationale="A bounded rationale",
                supporting_evidence_ref_ids=(evidence_id,),
            )

    def test_envelopes_reject_invalid_identity_literals_and_collection_bounds(self) -> None:
        evidence_id = "ev_sha256:" + "1" * 64
        hypothesis = RootCauseHypothesis(
            statement="A cause",
            uncertainty="low",
            supporting_evidence_ref_ids=(evidence_id,),
        )
        candidate = CandidateChange(
            path="src/example.py",
            change_kind="modify_existing_file",
            rationale="A bounded rationale",
            supporting_evidence_ref_ids=(evidence_id,),
        )
        strategy = FixStrategy(
            summary="A strategy",
            constraint_codes=(
                "evidence_backed",
                "minimal_change",
                "no_execution",
                "policy_bounded",
            ),
        )
        policy = PolicyDecisionRef(
            decision_id="pdr_sha256:" + "2" * 64,
            decision="allowed",
            policy_profile_id="patch-proposal/m2-conservative-v1",
            policy_version=1,
            evaluator_id="m2/deterministic-boundary-evaluator-v1",
            evaluated_candidate_digest="sha256:" + "3" * 64,
        )

        with self.assertRaises(ValueError):
            PolicyDecisionRef(
                decision_id="pdr_sha256:" + "2" * 64,
                decision="blocked",  # type: ignore[arg-type]
                policy_profile_id="patch-proposal/m2-conservative-v1",
                policy_version=1,
                evaluator_id="m2/deterministic-boundary-evaluator-v1",
                evaluated_candidate_digest="sha256:" + "3" * 64,
            )
        with self.assertRaises(ValueError):
            PatchProposal(
                contract_id="not-a-contract-id",
                proposal_source_id="m2/deterministic-fixture-v1",
                repository_context_contract_id="rcr_sha256:" + "4" * 64,
                task_input=TaskInput(task_ref="M2-001", summary="A valid summary"),
                root_cause_hypotheses=(hypothesis,),
                fix_strategy=strategy,
                candidate_changes=(candidate,),
                policy_decision=policy,
            )
        with self.assertRaises(ValueError):
            PatchProposal(
                contract_id="pp_sha256:" + "5" * 64,
                proposal_source_id="m2/deterministic-fixture-v1",
                repository_context_contract_id="rcr_sha256:" + "4" * 64,
                task_input=TaskInput(task_ref="M2-001", summary="A valid summary"),
                root_cause_hypotheses=(hypothesis,) * 4,
                fix_strategy=strategy,
                candidate_changes=(candidate,),
                policy_decision=policy,
            )
        earlier_candidate = CandidateChange(
            path="src/a.py",
            change_kind="modify_existing_file",
            rationale="A bounded rationale",
            supporting_evidence_ref_ids=(evidence_id,),
        )
        with self.assertRaises(ValueError):
            PatchProposal(
                contract_id="pp_sha256:" + "5" * 64,
                proposal_source_id="m2/deterministic-fixture-v1",
                repository_context_contract_id="rcr_sha256:" + "4" * 64,
                task_input=TaskInput(task_ref="M2-001", summary="A valid summary"),
                root_cause_hypotheses=(hypothesis,),
                fix_strategy=strategy,
                candidate_changes=(candidate, earlier_candidate),
                policy_decision=policy,
            )
        with self.assertRaises(ValueError):
            PatchProposal(
                contract_id="pp_sha256:" + "5" * 64,
                proposal_source_id="m2/deterministic-fixture-v1",
                repository_context_contract_id="rcr_sha256:" + "4" * 64,
                task_input=TaskInput(task_ref="M2-001", summary="A valid summary"),
                root_cause_hypotheses=(hypothesis,),
                fix_strategy=strategy,
                candidate_changes=(candidate,),
                policy_decision=policy,
                risk_flags=("high_risk_path", "deletion_intent"),
            )
        with self.assertRaises(ValueError):
            PatchProposalValidationError(
                error_id="ppe_sha256:" + "6" * 64,
                error_code="unknown",  # type: ignore[arg-type]
                input_category="task_input",
                message="A safe message",
                summary=ValidationErrorSummary(),
            )

    def test_contract_models_exclude_payload_runtime_and_execution_fields(self) -> None:
        forbidden_names = {
            "raw_source",
            "raw_payload",
            "source_content",
            "diff",
            "patch",
            "command",
            "command_output",
            "provider_payload",
            "prompt",
            "absolute_path",
            "environment_value",
            "timestamp",
            "run_id",
            "network",
            "branch",
            "commit",
            "pr",
            "memory",
            "workflow",
        }
        model_types = (
            TaskInput,
            RootCauseHypothesis,
            FixStrategy,
            CandidateChange,
            PolicyDecisionRef,
            PatchProposal,
            ValidationErrorSummary,
            PatchProposalValidationError,
        )

        for model_type in model_types:
            with self.subTest(model_type=model_type.__name__):
                self.assertFalse(forbidden_names & {field.name for field in fields(model_type)})


if __name__ == "__main__":
    unittest.main()
