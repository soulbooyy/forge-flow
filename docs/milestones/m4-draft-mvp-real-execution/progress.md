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
