# M4 Controlled Materialization and Payload Simulation Progress

## Phase 1 — contracts, canonical identity, and terminals

Completed 2026-07-21.

- Added immutable manifest, materialization and eligibility PDRs, payload, and
  controlled terminal contracts with self-excluding canonical SHA-256 IDs.
- Kept durable shapes free of bytes, diffs, paths, and ephemeral handles; the
  handle is non-serializable and private to the harness seam.
- Recorded all RFC-008 terminal names, closed classifications, zero automatic
  retries, and future-only `real_mutation` authority vocabulary without a v1
  concrete real-mutation PDR.
- Targeted contracts tests and boundary grep passed. Independent review found
  handle forgery and terminal-enum gaps; both were fixed and retested.

## Phase 2

Pending.

## Phase 3

Pending.

## Phase 4

Pending.
