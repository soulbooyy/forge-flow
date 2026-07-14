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
repository_owner:
repository_name:
repository_id:
visibility:
allowlisted:
```

Leave every field as a placeholder until the real environment supplies it. Do
not create a repository or generate a repository ID. Repository identity must
come from the registered controlled environment.

## Issue Registration

```yaml
issue_number:
issue_id:
issue_title:
content_hash:
```

Leave every field as a placeholder until the registered fixture Issue exists.
Do not create a synthetic Issue. Its fixed identity is the source of
`TaskInput` lineage.

## Base Revision Registration

```yaml
base_commit_sha:
revision_pinning_reason:
```

The base revision must be an immutable commit SHA supplied by the controlled
fixture environment. It makes M4 execution reproducible and must not drift
automatically during implementation.

## Authentication Registration

```yaml
auth_type:
permission_scope:
credential_owner:
rotation_and_revocation_responsibility:
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
reset_owner:
reset_method:
branch_cleanup_strategy:
draft_pr_cleanup_strategy:
audit_responsibility:
```

M4 may use a manual reset. The completed registration must state how the
fixture repository is restored to its registered base revision, how generated
branches and Draft PRs are cleaned up, and how redacted audit evidence is
retained.

## Evaluation Policy Profile

```yaml
profile_id:
profile_version:

max_wall_clock_ms:
max_sandbox_lifetime_ms:
max_command_output_bytes:
max_workspace_write_bytes:
max_artifact_bytes:
max_diff_bytes:
max_changed_files:
max_tool_calls:
max_automatic_retries: 0
```

All budget values must come from the versioned fixture policy profile. The
repository, Issue, request, user, and agent cannot override them. Reaching any
budget produces `resource_limit_exceeded` and blocks later mutation.

## Registration Status

```yaml
status: Pending # Pending | Registered | Approved
readiness_blocker: Real controlled fixture environment values are not registered.
```

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

