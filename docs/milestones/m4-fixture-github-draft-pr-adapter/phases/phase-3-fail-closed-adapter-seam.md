# Phase 3: Fail-Closed Adapter Seam

## Goal

Implement the sole future fixture GitHub adapter seam while preserving the
accepted metadata-only boundary: no materialization authority, branch, commit,
Draft PR, credential persistence, network call, or external mutation exists.

## Delivered

- `ControlledFixtureAdapter` performs pure preflight and idempotency
  reconciliation using Phase 2's canonical lineage validation.
- Replayed keys return the original immutable terminal result; a reused key for
  a different request returns an `idempotency_conflict` terminal.
- A fresh allowed PDR, approved lineage, and publishable body still terminate
  as `materialization_unavailable`, accurately distinguishing the absent patch
  materialization capability from a policy denial.
- Credential input remains opaque: the adapter only checks presence and never
  dereferences, serializes, stores, or exposes it.

## Review and Verification

- Targeted Feature 4 suite passed: 16/16.
- Full local verification passed: 167/167 tests.
- Static boundary scan found no GitHub, network, filesystem, credential, or
  external-mutation API surface in the Feature 4 package.
- `openspec validate fixture-github-draft-pr-adapter --strict` passed.
- Independent review passed after separating `materialization_unavailable` from
  `policy_blocked` terminal semantics.

## Scope Boundary

This is not a successful Draft PR MVP or external end-to-end path. It creates
zero branches, commits, and Draft PRs. A real mutation path remains deferred to
a separate capability that explicitly defines source access, patch
materialization, mutation authority, commit-payload identity, fresh PDR input,
and Feature 3 metadata-lineage binding.

## Follow-up

Phase 4 may harden the zero-effect acceptance matrix and document the deferred
real-mutation readiness requirements. It remains separately unauthorized.

Status: **Accepted**.
