# Phase 4: Zero-Effect Acceptance and Boundary Hardening

## Goal

Prove the selected no-mutation adapter boundary: every allowed, denied,
approval, invalid-body, replay, and reconciliation path retains zero external
effects while preserving bounded governance facts.

## Delivered

- Acceptance coverage proves the fresh-allowed metadata-only path ends as
  `materialization_unavailable` with zero branch, commit, and Draft-PR effects.
- Denied-policy, denied-approval, and invalid-body paths each prove a bounded
  `no_effect` result and zero external effects.
- Idempotency replay returns the original result without a new effect.
- The registered manual reset/audit procedure is checked as redacted and
  payload-free; it is not invoked by the adapter.

## Verification and Review

- Phase 4 acceptance tests passed: 5/5.
- Full local verification passed: 167/167 tests.
- Static package scan found no GitHub, network, filesystem, credential, or
  external-mutation API surface.
- `openspec validate fixture-github-draft-pr-adapter --strict` passed.
- Independent review passed after explicit invalid-body zero-effect and
  `no_effect` assertions were added.

## Boundary Confirmation

Feature 4's implemented adapter slice is a safe, fail-closed no-mutation
boundary. It is **not** a successful Draft PR MVP or an external end-to-end
path. It performs no GitHub call, creates no branch, commit, or Draft PR, and
does not retain source, patch, diff, raw Issue, command output, credential,
path, or provider payload.

Real mutation remains deferred to an independent capability that first defines
source access, patch materialization, mutation authority, commit-payload
identity, a fresh PDR input, and binding to Feature 3 metadata lineage.

Status: **Accepted**.
