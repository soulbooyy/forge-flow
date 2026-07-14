# M4 Fixture Environment Registration

## Purpose

This template registers the external controlled fixture environment required to
evaluate the M4 MVP vertical path:

```text
GitHub Issue
    ↓
TaskInput
    ↓
PatchArtifact
    ↓
ExecutionAttempt
    ↓
Draft PR
```

It applies only to a ForgeFlow-owned fixture/test repository and supports
reproducible evaluation. It does not support arbitrary user repositories,
production repositories, or organization-level repositories.

Fixture environment registration is an M4 readiness-gate external input. Until
it is completed and approved, M4 must not create an OpenSpec, branch/worktree,
GitHub mutation implementation, or implementation code. Real environment
values must be supplied by the controlled external environment; this template
must not be completed with AI-inferred or generated values.

## Repository Registration

```yaml
repository_owner: soulbooyy
repository_name: forgeflow-m4-fixture
repository_id: 1300511729
visibility: private
allowlisted: true
```

In an unregistered copy, leave every field as a placeholder until the real
environment supplies it. Do not create a repository or generate a repository
ID. Repository identity must come from the registered controlled environment.

## Issue Registration

```yaml
issue_number: 1
issue_id: 4883496432
issue_title: Fix calculator addition bug
content_hash: sha256:7acf3aebdad4eb3b138c975cb10ba094b7be63dc2f983f9d506adba4f799e785
```

`content_hash` is SHA-256 of the exact Issue title, followed by two newline
characters, followed by the exact Issue body as created on 2026-07-14.

In an unregistered copy, leave every field as a placeholder until the
registered fixture Issue exists. Do not create a synthetic Issue. Its fixed
identity is the source of `TaskInput` lineage.

## Base Revision Registration

```yaml
base_commit_sha: 97c8220cd713ebf61124ac2de2f3eadc6e4dc222
revision_pinning_reason: Immutable initial fixture commit; M4 evaluation must use this SHA and may not follow the main branch implicitly.
```

The base revision must be an immutable commit SHA supplied by the controlled
fixture environment. It makes M4 execution reproducible and must not drift
automatically during implementation.

## Authentication Registration

```yaml
auth_type: fixture_only_fine_grained_token
permission_scope: Repository access is restricted to soulbooyy/forgeflow-m4-fixture only; Contents, Issues, and Pull requests are Read and write; Metadata is required Read-only.
credential_owner: soulbooyy (ForgeFlow fixture environment owner)
rotation_and_revocation_responsibility: Owner stores the token only in the approved controlled secret store, rotates it before expiry or on suspected exposure, and revokes it immediately after M4 evaluation or on scope change.
```

Allowed `auth_type` values are:

- `github_app_installation` (preferred)
- `fixture_only_fine_grained_token` (only when the fixture environment cannot
  support a GitHub App installation)

Do not use a classic PAT, organization-wide credential, or unrestricted token.
Do not write credentials to the repository, artifact store, DurableRunSummary,
logs, or PR body. This document records credential governance only, never a
real token.

## Reset and Audit Strategy

```yaml
reset_owner: soulbooyy (ForgeFlow fixture environment owner)
reset_method: After each evaluation, force-restore the fixture default branch to base_commit_sha 97c8220cd713ebf61124ac2de2f3eadc6e4dc222; do not implicitly advance the baseline.
branch_cleanup_strategy: Delete every evaluation-created branch after its audit summary is retained.
draft_pr_cleanup_strategy: Close every evaluation-created Draft PR, then delete its head branch after audit retention.
audit_responsibility: Owner retains the ForgeFlow redacted audit summary and reset record; credentials, raw token values, and raw GitHub payloads are excluded.
```

M4 may use a manual reset. The completed registration must state how the
fixture repository is restored to its registered base revision, how generated
branches and Draft PRs are cleaned up, and how redacted audit evidence is
retained.

## Evaluation Policy Profile

```yaml
profile_id: forgeflow-m4-fixture-only
profile_version: 1.0.0

max_wall_clock_ms: 600000
max_sandbox_lifetime_ms: 480000
max_command_output_bytes: 65536
max_workspace_write_bytes: 10485760
max_artifact_bytes: 2097152
max_diff_bytes: 262144
max_changed_files: 10
max_tool_calls: 25
max_automatic_retries: 0

scanner_failure_outcome: blocked
redaction_failure_outcome: blocked
uncertain_security_result_outcome: blocked
```

This versioned fixture-only profile is the sole budget source. Repository,
Issue, request, user, and agent inputs cannot override it.

All budget values must come from the versioned fixture policy profile. The
repository, Issue, request, user, and agent cannot override them. Reaching any
budget produces `resource_limit_exceeded` and blocks later mutation.

Scanner failure, redaction failure, and any indeterminate security result are
fixed to `PolicyDecisionRecord.outcome: blocked`; they never enter human
approval. `requires_human_approval` remains available only for policy-defined,
interpretable governance escalations such as sensitive paths, pre-execution
threshold review and stale base revisions.

## Command Allowlist

```yaml
command_allowlist:
- command_id: fixture-test-runner-v1
  executable: python3
  args:
  - -m
  - unittest
  - discover
  - -s
  - tests
  working_directory: workspace_root
  allowed_environment: []
  timeout_ms: 120000
  max_output_bytes: 65536
```

This is the sole M4 fixture-specific execution capability, not a ForgeFlow
general command allowlist. The executable, argument order, working directory,
and empty environment must match exactly; extra arguments, shell wrappers,
network access, dependency installation, and dynamic values from users, Issues,
repository configuration, or agents are forbidden. `CommandIntent` records
`command_id` and the policy-profile version in its immutable lineage.

Command-specific limits may only reference or narrow the registered fixture
profile budget; they may not exceed it. This command's `max_output_bytes` equals
the registered `max_command_output_bytes: 65536`. A timeout or output limit
exhaustion is `resource_limit_exceeded`; a command mismatch is
`policy_blocked`. Any future command or larger budget requires a new versioned
policy profile and a separate OpenSpec.

No `CommandIntent` is executable until the required OCI image is registered
below. `latest`, any floating tag, and a local unregistered image are forbidden.

## Sandbox Image Registration

```yaml
sandbox_image_registration:
  image_reference:
  image_digest:
  registry:
  approval_owner:
  security_review_reference:
  registered_at:
  registration_version:
```

These values are supplied only by the controlled, security-reviewed OCI image
environment. The immutable digest must identify the manifest used by the OCI
adapter; it must not be generated, inferred, or substituted by an image tag.
Until every field is registered, the sandbox capability is unavailable and the
first M4 execution-feature OpenSpec remains blocked.

## Evaluation Acceptance Thresholds

```yaml
mandatory_matrix_pass_rate: 100_percent
non_allowed_path_external_mutations: 0
allowed_end_to_end_max_branch_creations: 1
allowed_end_to_end_max_commit_creations: 1
allowed_end_to_end_max_draft_pr_creations: 1
idempotency_key_replay_new_external_mutations: 0
terminal_pdr_lineage_and_budget_observation_match: exact
prohibited_or_unredacted_publication_count: 0
external_side_effect_scenario_reset_and_redacted_audit_evidence: required
```

Every mandatory matrix scenario must pass. Denied, approval-required, and fault
paths must produce zero external mutations. The one allowed end-to-end scenario
may create at most one branch, one commit, and one Draft PR; replaying its
idempotency key may create no new GitHub side effect. Terminals, Policy Decision
Records, lineage, and resource-budget observations must exactly match their
expected values. Draft PR bodies, summaries, and artifact references tolerate
no prohibited or unredacted content. Every scenario with an external side
effect must complete reset and retain redacted audit evidence.

## Fault-Injection Boundary

M4 fault injection is deterministic and occurs only at ForgeFlow-owned local
controlled harness and adapter seams. Required cases are sandbox unavailable,
command failed, timeout, cancellation, parser failure, secret-scan/redaction
failure, artifact temporary-write/atomic-publish failure, policy/approval/base-
revision/idempotency conflict, and GitHub adapter pre-mutation or post-request
ambiguous-result failure.

Every non-allowed path uses a fake or controlled adapter and must produce zero
external mutations. Only the single registered allowed path may call the real
GitHub adapter, followed by the registered reset/audit procedure. Fault
injection must not introduce arbitrary shell, network access, credentials, or
environment variables; bypass policy; fabricate authorization; or change
immutable lineage.

## Registration Status

```yaml
status: Approved # Pending | Registered | Approved
readiness_blocker: M4 Phase 0 closure is approved; feature-level OpenSpec gates remain required.
execution_feature_readiness: Blocked
execution_feature_readiness_blocker: Required OCI image registration is absent.
```

`Registered` means that the controlled external environment supplied and the
project reconciled the required registration values. `Approved` additionally
records the explicit M4 Phase 0 closure decision. That decision authorizes
feature-level OpenSpec preparation only; every later feature still requires its
own OpenSpec and readiness gate, and it does not authorize a branch/worktree,
GitHub mutation, or implementation.

While status is `Pending`, the following are prohibited:

- creating an M4 OpenSpec;
- creating an M4 branch or worktree;
- GitHub mutation; and
- implementation code.

## References

- [M4 execution architecture readiness](../product/roadmap/milestones.md)
- [RFC-004: Sandbox and Security Governance](../../rfcs/RFC-004-sandbox-and-security-governance.md)
- [RFC-006: Evaluation Framework](../../rfcs/RFC-006-evaluation-framework.md)
- [RFC-007: DeerFlow Extension Strategy](../../rfcs/RFC-007-deerflow-extension-strategy.md)
