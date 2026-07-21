# ADR-012: Use Registered Transformers and Ephemeral Payloads for M4

## Status

Proposed

## Context

Metadata lineage cannot be treated as commit content or mutation authority.
M4 needs a narrowly controlled way to materialize one deterministic fixture
change for local/fake validation without creating a general patch language or
real GitHub capability.

## Proposed Decision

Use harness-injected registered snapshots, registered versioned transformers,
ephemeral payload bytes, and local fake Git-data simulation.

- A manifest selects a registered transformer and exact target/input digest;
  it never carries source, diff, replacement text, template, or executable
  payload.
- Docker receives only a verified read-only snapshot, fixed image, empty
  environment, fixed Feature 1 command/profile, and no network or credentials.
- The harness owns transient output and an unforgeable, non-serializable,
  single-lifecycle payload handle.
- Durable contracts retain identities, digests, references, and scoped PDRs
  only. They retain neither payload bytes nor the handle.
- Fake IDs use `forgeflow-sim-*` and cannot appear in a real mutation request,
  provider-facing contract, or real adapter import surface.
- Materialization PDR, payload-eligibility PDR, and future mutation PDR are
  separate scopes with no elevation path.

## Consequences

This supports deterministic local materialization and fake simulation while
keeping Feature 4 fail-closed. Real mutation remains a future capability with
its own OpenSpec, readiness review, credential authority, and fresh PDR.
