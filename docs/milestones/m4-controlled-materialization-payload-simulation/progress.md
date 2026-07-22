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

Completed 2026-07-21.

- Added closed snapshot, target-file, and transformer registrations with exact
  revalidation before PDR issuance.
- PDR issuance accepts only a private verification proof, reuses the exact
  Feature 1 profile reference, and mints a unique fresh attempt per issuance.
- Targeted contract/registry tests and source-selection boundary checks passed.
  Independent review found deterministic attempt reuse; it was fixed and
  retested.

## Phase 3

Completed 2026-07-22.

- Added the isolated local-Docker protocol/seam with exact Feature 1 profile
  rejection, local/no-network/read-only/empty-environment/credential/resource
  proofs, and no process surface outside `sandbox.py`.
- Materialization retains only facts and digests in payload contracts; security
  non-pass states, validation assertion failures, and infrastructure failures
  terminate fail-closed without payload text.
- Added explicit current-time PDR freshness, every proof-gap coverage, cleanup
  coverage, and a private one-shot harness continuation. It exposes a live
  lease only during the same lifecycle, then destroys it in `finally`.
- Independent review found and closed profile-proof, security-fact, expiry,
  public-handle, and continuation-lifecycle gaps; targeted tests passed.

## Phase 4

Completed 2026-07-22.

- Added deterministic in-memory `forgeflow-sim-*` fake identities with exact
  payload/PDR/handle binding, controlled binding terminals, and unconditional
  one-attempt handle destruction.
- Added real-surface rejection for all v1 PDRs and simulation identities.
- Full suite, OpenSpec validation, and independent review repair loop passed;
  no provider, Git, network, or credential surface was added.
