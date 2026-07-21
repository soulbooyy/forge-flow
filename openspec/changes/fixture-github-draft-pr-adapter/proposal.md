# Change: Fixture-Repository GitHub Draft PR Adapter

## Why

M4 Feature 4 closes the governed fixture path from approved immutable lineage
to one auditable Draft PR without granting general repository automation.

## Scope

- define immutable, redacted Draft PR request/result and idempotency facts;
- allow the ForgeFlow-owned adapter to act only on the registered fixture
  repository, Issue, and fixed base revision;
- require a fresh allowed PDR, exact lineage, opaque runtime credential, and
  deterministic redacted body before branch, commit, or Draft PR mutation; and
- define fail-closed and ambiguous-result terminals with zero unintended retry.

## Non-goals

- arbitrary repository/Issue selection, source or patch materialization,
  shell execution, credential persistence, non-draft PRs, merge, general
  GitHub ingestion, automatic retry, DeerFlow, remote artifact stores,
  encryption, or retention.

## Impact

This change consumes Feature 1–3 immutable governance and durable metadata
references. It introduces no implementation authorization, branch/worktree,
or GitHub mutation until its OpenSpec, canonical plan, readiness gate, and
explicit implementation authorization are accepted.
