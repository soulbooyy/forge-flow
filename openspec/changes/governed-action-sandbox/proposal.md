# Change: Governed Action and Sandbox Boundary

## Why

M1–M3 establish repository facts, declarative `PatchProposal`, and
fixture-based validation/review contracts, but none grants or performs real
execution. M4 needs a first, bounded controlled-execution feature that proves
the separation of intent, authorization, execution facts, and sandbox
capability without introducing patch generation, approval workflow, durable
storage, GitHub mutation, or provider/runtime coupling.

## Scope

- define immutable `ActionIntent`, `CommandIntent`, `PolicyDecisionRecord`, and
  `ExecutionAttempt` contracts and their canonical identity/lineage rules;
- evaluate the sole registered fixture command against the versioned fixture
  policy profile and a fresh Policy Decision Record;
- define the ForgeFlow-owned OCI adapter seam, including a temporary
  fixed-revision workspace, exact image-digest binding, and fail-closed
  capability checks;
- record bounded non-payload execution facts and terminal behavior for allowed,
  blocked, approval-required, unavailable, failed, cancelled, timed-out, and
  resource-limited cases; and
- define deterministic fixture and controlled-adapter acceptance cases for the
  governed-action and sandbox boundary.

## Non-goals

- `PatchIntent`, `PatchArtifact`, source or diff generation/application,
  secret scanning, redaction implementation, review evaluation, approval
  request/decision implementation, artifact-store implementation, or
  `DurableRunSummary` implementation;
- arbitrary commands, shell wrappers, environment injection, network access,
  dependency installation, credentials in the sandbox, host-process fallback,
  DeerFlow runtime attachment, or a general command allowlist;
- GitHub Issue retrieval, branch/commit/Draft PR creation, any other GitHub
  mutation, merge, deployment, or production/organization repository support;
- automatic retry, repair loops, provider/LLM patch generation, or runtime
  recovery behavior.

## Architecture Readiness Gate

The gate is closed for feature-level OpenSpec preparation only:

1. [ADR-011](../../../adr/ADR-011-use-oci-container-adapter-for-m4-controlled-execution.md)
   accepts ForgeFlow-owned OCI adapter ownership and its fail-closed sandbox
   boundary.
2. RFC-002 and RFC-004 define the required M4 contract separation, sole
   fixture command, immutable image binding, and terminal semantics; RFC-005
   and RFC-006 define the durable/evaluation boundaries that this feature must
   not preempt.
3. The fixture repository/Issue/policy profile and the independent
   [approved sandbox image registration](../../../docs/fixtures/m4-sandbox-image-registration.md)
   are controlled external inputs. The registration authorizes no image
   substitution, branch/worktree, GitHub mutation, or implementation by itself.
4. Grill-Me design challenge concluded that image registration is not execution
   authorization, a shell present in an image is not a command capability,
   missing sandbox proof stops before side effects, and an attempt may record
   only facts that occurred.

This change still requires accepted OpenSpec review, planning, an explicitly
authorized implementation environment, and per-phase authorization before any
implementation or execution activity.

## Impact

This change adds the first M4 feature contract and OCI-adapter boundary. It
creates no GitHub side effect and does not make a `PatchProposal`, fixture
registration, image registration, or an `allowed` decision an independent
execution permit.
