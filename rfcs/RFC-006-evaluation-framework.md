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

## Open Questions

- Which concrete fixture-profile values and pass thresholds define M4
  acceptance?
- How will a real GitHub fixture repository be reset and audited between runs?
- Which fault-injection mechanisms can prove adapter, sandbox, and persistence
  failure semantics without widening authority?

## M4 Readiness Preconditions

Each later M4 OpenSpec must name its evaluation fixtures, terminal cases,
redaction assertions, and evidence outputs. The canonical M4 plan may begin
only after the complete matrix and acceptance thresholds are reconciled.

## Decision Summary

M4 evaluates governed behavior through deterministic, fixture-repository
scenarios and durable redacted lineage, not through model quality or broad
repository access.
