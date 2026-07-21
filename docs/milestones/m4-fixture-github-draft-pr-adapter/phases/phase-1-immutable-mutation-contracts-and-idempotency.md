# Phase 1: Immutable Mutation Contracts and Idempotency

## Goal

Define fixture-bound, immutable request, terminal, idempotency, and result
facts without GitHub access, credentials, external I/O, or mutation.

## Delivered

- `DraftPRRequest` binds the registered repository, Issue, base revision, and
  profile/version to bounded ForgeFlow lineage identifiers.
- `PRTerminal`, `IdempotencyRecord`, and `PRResult` provide separate,
  canonical, immutable facts for no-effect, reconciliation, and successful
  Draft-PR outcomes.
- Every contract ID is a self-excluding canonical SHA-256 identity, enforced
  by the model and covered by forged-ID negative tests.
- Successful results retain only bounded branch and Draft-PR identifiers plus
  a fixed Git commit SHA; no-effect results retain only a canonical terminal
  digest.

## Review and Verification

- Targeted contract and canonical tests passed: 5/5.
- Full local verification passed: 167/167 tests.
- `openspec validate fixture-github-draft-pr-adapter --strict` passed.
- `git diff --check` passed.
- Independent review passed after a correction that tightened `PRResult`
  terminal, branch, commit, and Draft-PR reference validation.

## Scope Boundary

This phase contains no GitHub client, network call, credential field, source,
diff, patch, command output, raw Issue content, retry loop, or external
mutation. It authorizes none of those capabilities.

## Follow-up

Phase 2 may add pure eligibility and deterministic redacted-body assembly
only after its implementation authority is accepted. GitHub mutation remains
separately unauthorized.

Status: **Accepted**.
