# GitHub Mutation Orchestration Closure — 2026-07-22

## Scope

This batch implements the fail-closed orchestration boundary for the sole
registered fixture mutation scenario. Its provider is injected in tests; it
does not invoke the GitHub CLI, retain a credential, or create a GitHub
resource.

## Controls proved

- Only a fresh, exact `real_mutation` PDR may enter the adapter.
- Payload bytes are held in a non-serializable ephemeral object and are
  destroyed unconditionally on every exit path.
- The adapter verifies the registered base revision before a provider write.
- The deterministic branch identity is reconciled before writes. Branch-only,
  commit-only, malformed, or otherwise uncertain state fails closed.
- A local idempotency claim is made before the branch call. A provider fault
  after a possible remote side effect cannot trigger another write in the same
  adapter lifetime; a new adapter relies on deterministic remote reconciliation
  and likewise rejects partial state.
- Automatic retries are fixed at zero.

## Verification and review

`tests.m4_draft_mvp_real_execution.test_github_adapter` covers the allowed
one-branch/one-commit/one-Draft-PR sequence through a fake provider, replay,
stale base, expired PDR, partial reconciliation, malformed branch response,
and fault-after-branch retry. The real-mutation contract tests and a static
authority-isolation check also pass.

An independent read-only review found two idempotency defects in the initial
implementation: missing partial-state protection and a late claim. Both were
fixed with RED tests, retested, and independently re-reviewed as passing.
