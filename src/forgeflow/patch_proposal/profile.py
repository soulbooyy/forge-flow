"""Versioned conservative defaults for the Milestone 2 PatchProposal contract."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PatchProposalProfile:
    policy_profile_id: str
    policy_version: int
    evaluator_id: str
    proposal_source_id: str
    max_task_ref_chars: int
    max_task_summary_chars: int
    max_root_cause_hypotheses: int
    max_hypothesis_chars: int
    max_fix_strategy_chars: int
    max_candidate_changes: int
    max_candidate_rationale_chars: int
    allowed_change_kinds: tuple[str, ...]
    required_fix_strategy_constraint_codes: tuple[str, ...]
    allowed_risk_flags: tuple[str, ...]
    allowed_limitation_codes: tuple[str, ...]
    blocked_path_segments: tuple[str, ...]
    blocked_file_suffixes: tuple[str, ...]
    blocked_file_names: tuple[str, ...]
    approval_environment_file_names: tuple[str, ...]
    approval_environment_file_prefixes: tuple[str, ...]
    approval_ci_directory_prefixes: tuple[str, ...]
    approval_ci_file_names: tuple[str, ...]
    approval_infrastructure_path_segments: tuple[str, ...]
    approval_infrastructure_file_suffixes: tuple[str, ...]
    approval_auth_path_segments: tuple[str, ...]
    approval_migration_directory_prefixes: tuple[str, ...]
    approval_lockfile_names: tuple[str, ...]
    approval_required_for_remove_file: bool


M2_CONSERVATIVE_V1 = PatchProposalProfile(
    policy_profile_id="patch-proposal/m2-conservative-v1",
    policy_version=1,
    evaluator_id="m2/deterministic-boundary-evaluator-v1",
    proposal_source_id="m2/deterministic-fixture-v1",
    max_task_ref_chars=128,
    max_task_summary_chars=1_000,
    max_root_cause_hypotheses=3,
    max_hypothesis_chars=500,
    max_fix_strategy_chars=1_000,
    max_candidate_changes=3,
    max_candidate_rationale_chars=500,
    allowed_change_kinds=(
        "modify_existing_file",
        "add_test_file",
        "add_non_sensitive_file",
        "remove_file",
    ),
    required_fix_strategy_constraint_codes=(
        "evidence_backed",
        "minimal_change",
        "no_execution",
        "policy_bounded",
    ),
    allowed_risk_flags=(
        "policy_requires_human_approval",
        "environment_path",
        "high_risk_path",
        "deletion_intent",
        "policy_profile_revalidation_required",
    ),
    allowed_limitation_codes=(
        "fixture_only_source",
        "no_source_payload",
        "no_diff_generated",
        "no_validation_executed",
    ),
    blocked_path_segments=("secrets", "secret", "credentials", "credential"),
    blocked_file_suffixes=(".pem", ".key", ".p12", ".pfx", ".jks"),
    blocked_file_names=("id_rsa", "id_dsa", "id_ecdsa", "id_ed25519"),
    approval_environment_file_names=(".env",),
    approval_environment_file_prefixes=(".env.",),
    approval_ci_directory_prefixes=(".github/workflows", ".circleci"),
    approval_ci_file_names=(
        ".gitlab-ci.yml",
        "Jenkinsfile",
        "azure-pipelines.yml",
        "azure-pipelines.yaml",
    ),
    approval_infrastructure_path_segments=(
        "deploy",
        "deployment",
        "infra",
        "infrastructure",
        "k8s",
        "helm",
        "terraform",
    ),
    approval_infrastructure_file_suffixes=(".tf",),
    approval_auth_path_segments=(
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
    approval_migration_directory_prefixes=(
        "migrations",
        "migration",
        "db/migrate",
        "database/migrations",
    ),
    approval_lockfile_names=(
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
    approval_required_for_remove_file=True,
)
