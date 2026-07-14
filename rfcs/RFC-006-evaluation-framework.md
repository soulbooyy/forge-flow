# RFC-006: Evaluation Framework

## Status

Draft

## Context

M4 must demonstrate a governed Issue-to-Draft-PR path without equating a
successful external side effect with safe or correct behavior. Its first
evaluation environment is one allowlisted fixture/test repository, deterministic
patch artifacts, controlled command fixtures, and a versioned policy profile.

## Current Draft Decisions

- M4 evaluation is fixture/test-repository based, deterministic where possible,
  and provider-free.
- Evaluation must include allowed, blocked, approval-required, redaction,
  validation-failure, sandbox-failure, idempotency, and Draft-PR outcomes.
- A Draft PR is a result to evaluate, not proof that policy or security checks
  were correct.
- Evaluation evidence uses redacted references and DurableRunSummary lineage;
  it does not retain raw credentials, source, logs, or GitHub payloads.
- The fixture environment registration package supplies actual repository/Issue
  identity, base revision, credential mode, reset/audit procedure, budget
  values, and acceptance thresholds; M4 architecture and implementation must
  not invent them.
- The fixture-registration sub-gate is `Registered` for profile
  `forgeflow-m4-fixture-only` version `1.0.0`, as recorded in the M4 Fixture
  Environment Registration. This is not an `Approved` complete evaluation gate.
- M4 acceptance requires a 100 percent mandatory-matrix pass rate, zero
  external mutations on every non-allowed path, bounded one-branch/one-commit/
  one-Draft-PR creation for the single allowed path, zero new side effects on
  idempotency-key replay, exact governance/lineage/budget observations, zero
  prohibited publication, and reset plus redacted audit evidence after each
  external side-effect scenario.

## Goals

- Define minimum evidence for M4 safety, contract, policy, and side-effect
  behavior.
- Make policy terminals, approval expiry, and idempotency reproducible.
- Feed controlled findings back into RFCs, ADRs, and later OpenSpec changes.

## Non-goals

- Require SWE-bench, arbitrary repositories, production benchmarks, or a model
  quality evaluation.
- Define enterprise analytics, online experimentation, or provider evaluation.

## Minimum M4 Evaluation Matrix

The M4 readiness suite must prove at least:

- only the allowlisted fixture repository can reach the GitHub adapter;
- unapproved paths, commands, revisions, artifacts, and stale approvals stop
  before execution or external mutation;
- sandbox network and dynamic dependency installation remain unavailable;
- a deterministic patch artifact preserves base revision, diff, scan, policy,
  execution, review, and PR lineage;
- secret matches, scanner failures, and redaction failures use fail-closed
  policy outcomes;
- validation and execution terminals produce no implicit retry;
- only the versioned fixture policy profile can supply resource budgets;
  repository, Issue, user, and agent inputs cannot override them;
- every configured M4 resource limit is recorded with its observed value, and
  every triggered limit produces `resource_limit_exceeded` before any later
  mutation;
- idempotency prevents duplicate branch, commit, or Draft PR creation;
- summaries and PR bodies exclude prohibited raw payloads.

### Reconciled M4 Evaluation Matrix

The registered fixture profile requires these minimum deterministic scenarios.
Each scenario produces the stated immutable lineage and must meet the registered
acceptance thresholds.

| Scenario | Expected PDR outcome | Expected execution / side-effect result | External mutations |
| --- | --- | --- | --- |
| Registered allowlisted clean path | `allowed` | Successful execution; at most one branch, commit, and Draft PR | At most 1 of each |
| Non-allowlisted repository or Issue | `blocked` | `not_started` / `policy_blocked` | 0 |
| Scanner failure, redaction failure, or indeterminate security rule | `blocked` | `not_started` / `policy_blocked`; no persistable or publishable artifact | 0 |
| Confirmed secret match | `blocked` | `not_started` / `policy_blocked`; no commit or Draft PR | 0 |
| Sensitive path, pre-execution threshold review, non-allowlisted command, or stale base revision | `requires_human_approval` | Bound ApprovalRequest; `not_started` / `approval_required` or `base_revision_mismatch` | 0 before a new approved evaluation |
| Approval expired or inputs changed | `requires_human_approval` | Previous approval unusable; `not_started` / `approval_required` | 0 |
| Runtime resource budget reached after an allowed start | prior `allowed` remains a decision fact | `failed` / `resource_limit_exceeded`; current run cannot mutate externally | 0 after the limit |
| Sandbox, command, timeout, cancellation, parser, or artifact-publication fault | decision remains separately recorded | Corresponding terminal failure; controlled adapter records no effect | 0 |
| GitHub adapter pre-mutation or ambiguous-result fault | fresh action decision remains separately recorded | Fake/controlled adapter records no duplicate external effect | 0 |
| Idempotency-key replay | fresh current-input decision as required | Existing result is returned or reconciled; no new branch, commit, or Draft PR | 0 new effects |

### Registered Fixture Acceptance Thresholds

The registered fixture profile defines these M4 acceptance thresholds:

- 100 percent of mandatory evaluation-matrix scenarios pass;
- denied, approval-required, and fault paths produce zero external mutations;
- the one allowed end-to-end scenario creates at most one branch, one commit,
  and one Draft PR;
- replaying an idempotency key creates zero new GitHub side effects;
- every terminal, Policy Decision Record, lineage field, and resource-budget
  observation exactly matches its expected value;
- Draft PR bodies, summaries, and artifact references contain zero prohibited
  or unredacted content; and
- every external-side-effect scenario completes reset and retains redacted
  audit evidence.

### M4 Deterministic Fault Injection

Fault injection is a fixed acceptance requirement at ForgeFlow-owned local
controlled harness and adapter seams. It must deterministically cover sandbox
unavailable, command failure, timeout, cancellation, parser failure,
secret-scan/redaction failure, artifact temporary-write/atomic-publish failure,
policy/approval/base-revision/idempotency conflicts, and GitHub adapter
pre-mutation plus post-request ambiguous-result failures.

Every non-allowed fault path uses a fake or controlled adapter and must produce
zero external mutations. Only the single registered allowed path may invoke the
real GitHub adapter, and it must complete the registered reset/audit procedure.
Fault injection must not introduce arbitrary shell execution, network access,
credentials, or environment variables; bypass policy; fabricate authorization;
or change immutable lineage.

## M4 Readiness Preconditions

Each later M4 OpenSpec must name its evaluation fixtures, terminal cases,
redaction assertions, and evidence outputs. The canonical M4 plan may begin
only after the complete matrix and acceptance thresholds are reconciled. The
evaluation gate additionally requires a registered fixture environment profile
containing fixture repository owner/name/ID, pre-registered Issue number/ID,
fixed base commit SHA, credential mode, reset/audit ownership and recovery
procedure, concrete resource-budget values, and acceptance thresholds. These
are external controlled inputs rather than values an implementation may infer.
Until registration is complete, M4 must not create a hypothetical GitHub
mutation configuration or enter implementation.

The required registration fields and placeholder rules are maintained in the
[M4 Fixture Environment Registration](../docs/fixtures/m4-fixture-environment-registration.md)
template. That template is a readiness-gate input record, not permission to
provision or infer a fixture environment.

### M4 Fixture-Registration Gate

The fixture-registration sub-gate is `Registered`. The controlled external
environment has supplied the allowlisted repository and Issue identities, fixed
base revision, fixture-only fine-grained credential mode, reset/audit procedure,
and versioned budget values in the registration record. No credential value is
recorded in this RFC or in the registration document.

The registration, acceptance-threshold, and fault-injection prerequisites are
satisfied. The complete evaluation gate remains unapproved until its evaluation
matrix is reconciled and Phase 0 closure review approval is complete. It
therefore does not authorize an M4 OpenSpec, branch/worktree, GitHub mutation,
or implementation.

## Decision Summary

M4 evaluates governed behavior through deterministic, fixture-repository
scenarios and durable redacted lineage, not through model quality or broad
repository access.
