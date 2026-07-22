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

Not accepted. A read-only preflight on 2026-07-22 confirmed the registered
private fixture repository and open Issue #1, but the locally configured
GitHub CLI credential is a general OAuth credential rather than the registered
fixture-only fine-grained token or GitHub App installation. The gate therefore
fails closed before branch, commit, or Draft-PR creation. No GitHub mutation
was attempted.
