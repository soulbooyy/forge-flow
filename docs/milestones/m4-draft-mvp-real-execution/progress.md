# M4 Draft-MVP Real Execution Progress

## Phase 1 — zero-effect authority and request contracts

Completed 2026-07-22.

- Added an independent, fresh `RealMutationPDR` and a closed request constructor.
- Rejected v1 PDRs and `forgeflow-sim-*` identities before any adapter surface.
- Added bounded canonical real-mutation terminals with zero automatic retries.
- Targeted tests, authority-isolation checks, and independent review passed.

## External gates

### Local Docker

Completed 2026-07-22. The registered image and verified fixture base revision
were run once with a read-only workspace, read-only root filesystem, no
network, UID/GID `100:100`, no injected credentials or environment, and
tmpfs-only output. The registered negative fixture test returned `exit=1`
within its time and output limits; its output was discarded after bounded
measurement. The temporary checkout was removed.

### Fixture GitHub mutation

Accepted 2026-07-22 after the credential was replaced. A read-only preflight
confirmed a fine-grained token, the registered private repository ID
`1300511729`, default branch `main`, and open Issue #1. The operator attests
that the token is fixture-only and has the registered minimal permissions.
GitHub does not expose a complete fine-grained permission grant to the client;
no token value is retained. The authorized scenario remains limited to one
branch, one commit, and one Draft PR for one idempotency key, with no automatic
retry and mandatory reset/audit cleanup.

## GitHub mutation orchestration seam

Completed 2026-07-22 without external mutation.

- The adapter accepts only an independently fresh real-mutation PDR and a
  non-serializable ephemeral payload whose digest and lineage match exactly.
- It reads the registered remote base before any write and uses a deterministic
  governed-change branch identity for reconciliation.
- A branch claim is made before the first provider write. Any partial,
  malformed, or uncertain remote state is `ambiguous_result`; manual replay
  creates no further external effect.
- Targeted RED/GREEN, fault/replay, authority-isolation tests, and independent
  review passed. The concrete GitHub CLI provider and the real-payload harness
remain separate, unimplemented work; no GitHub mutation was attempted.

## GitHub CLI provider seam

Completed 2026-07-22 without invoking the CLI.

- The only concrete provider uses fixed `gh` argv tuples and JSON stdin; it
  never uses a shell, token argument, environment token, or raw output log.
- Only a verified HTTP 404 can represent an absent reconciliation branch.
  Authentication, transport, rate-limit, and provider failures propagate and
  fail closed.
- Every branch, Git object, and ref response is validated before it becomes an
  input to a later write. The provider accepts only the registered fixture,
  base, target, deterministic governed-change branch format, commit message,
  Issue title, and Draft PR body.
- Targeted RED/GREEN tests and independent review passed. No GitHub request or
mutation was attempted by this batch.

## Real payload harness

Completed 2026-07-22 without external mutation.

- A single registry owns the fixture target ID/path and immutable input/output
  digests. The source is accepted only when it matches the registered snapshot.
- The only transformer changes one subtraction operator in a return expression;
  it requires exactly one match and validates the registered output digest.
- Payload bytes remain non-serializable and are passed only to the in-memory
  provider boundary. A controlled read-only revalidation of the fixed fixture
  SHA passed without retaining or displaying source content.
- Targeted tests, authority checks, and independent review passed.

## Authorization-stage diagnosis

Completed 2026-07-23 without external mutation.

- Authorization failures are partitioned into controlled payload, freshness,
  lineage, and payload-binding stage codes; no original exception data is
  retained in a result.
- RED/GREEN fault-injection tests confirm every partition fails before a
  provider write and destroys the ephemeral payload.
- Targeted adapter, provider, payload, and contract tests passed; local review
  found no further authority or result-surface expansion.

## Reconciliation lookup diagnosis

Completed 2026-07-23 after one fully reconciled fixture scenario.

- The scenario returned the controlled generic provider-unavailable result
  before any branch was retained; reconciliation, checkout removal, and fixed
  base-SHA audit completed.
- Reconciliation now separately records controlled branch-ref and PR-list
  lookup failures, while preserving credential, rate-limit, and provider
  rejection classifications.
- RED/GREEN provider tests and independent local review passed; the next fresh
  scenario will identify which reconciliation operation needs correction.

## Accepted fixture Draft PR scenario

Completed 2026-07-23.

- A fresh real-mutation PDR, idempotency key, and temporary fixture checkout
  completed the registered branch, commit, and Draft PR path.
- The Draft PR was closed, its branch was deleted, the checkout was removed,
  and the registered `main` base SHA was re-audited successfully.
- Only controlled outcome and stage evidence was retained; no token, payload,
  source, raw provider response, or temporary path was recorded.

## M4 closure audit

Completed 2026-07-23.

- The registered fixture audit found zero governed-change branch residues and
  zero open managed Draft PR residues; the fixed `main` SHA remained exact.
- The closure satisfies the canonical plan's denied/fault-path, reset, and
  redacted-evidence requirements, while preserving RFC-008 and ADR-012's
  separate-authority and ephemeral-payload boundaries.
- The completed task list, implementation evidence, fixture registration, and
  acceptance record now agree on the M4 Draft MVP lifecycle.
