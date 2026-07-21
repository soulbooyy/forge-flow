# Fixture GitHub Draft PR Adapter Design

The adapter is the only M4 component permitted to call GitHub APIs. Its public
input is a bounded request composed entirely of ForgeFlow-owned IDs, the
registered fixture identity, an idempotency key, and a fresh allowed PDR. It
does not accept source, diff, raw Issue content, command output, credential, or
caller-selected repository state.

Before mutation, the adapter verifies the registered repository/Issue/base
revision, current PDR lineage, approval when required, metadata-security
references, and deterministic redacted PR-body input. The sole allowed path
creates at most one controlled branch, one commit, and one Draft PR. Its result
records only bounded identifiers/URLs/statuses and is idempotency-bound.

The runtime injects an opaque repository-scoped credential. It cannot enter a
contract, durable artifact, log, body, or summary. Pre-mutation failure creates
no external effect. An ambiguous post-request result is recorded as a bounded
terminal and never retried automatically; reconciliation is explicit and
idempotency-bound.
