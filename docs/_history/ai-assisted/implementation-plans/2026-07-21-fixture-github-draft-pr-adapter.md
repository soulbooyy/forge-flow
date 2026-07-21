# Fixture GitHub Draft PR Adapter Implementation Draft

## Scope

Create a fixture-only, policy-gated adapter that records bounded request/result
facts and performs at most one idempotent branch, commit, and Draft PR mutation
on the registered environment. Credentials remain runtime-injected opaque data.

## Proposed Phases

1. Immutable request, terminal, idempotency, and PR-result contracts.
2. Deterministic redacted body rendering and fresh-lineage eligibility checks.
3. Controlled GitHub adapter with explicit pre/post-mutation reconciliation.
4. Acceptance matrix, fault injection, idempotency, and boundary hardening.

## Exclusions

No arbitrary repository access, raw Issue/source/diff/patch retention, shell
execution, credential storage, non-draft PR, merge, retry, DeerFlow, or remote
artifact-store capability.
