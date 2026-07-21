# Controlled Materialization and Payload Simulation Design

## Proposed Direction

v1 uses a controlled, short-lived materialization pipeline:

```text
source registry -> snapshot revalidation -> materialization PDR
-> network-disabled Docker -> digest/security checks
-> MaterializedCommitPayload -> payload-eligibility PDR
-> fake mutation simulation
```

The harness injects the only source snapshot and privately owns transient
payload bytes/handle. Contracts carry only registered identities, digests,
lineage, and fact references. Real GitHub mutation is excluded.

## Key Boundaries

- Registered transformer IDs replace free-form diffs, templates, scripts, and
  LLM-generated patch input.
- A controlled target-file registry resolves file IDs; callers and fake
  adapters cannot select or reinterpret paths.
- Each authority has its own fresh PDR scope; no materialization or payload
  eligibility authority can become real mutation authority.
- Feature 1's exact sandbox validation profile is reused by reference only.
- Fake Git-data simulation IDs are ForgeFlow-only `forgeflow-sim-*` values.

## Delivery Shape

1. Contract and terminal vocabulary.
2. Snapshot registry/revalidation and transformer execution.
3. Docker/security/validation integration with transient cleanup.
4. Fake mutation simulation and zero-effect acceptance matrix.

The design creates no source-access implementation, Docker invocation,
credential use, GitHub call, or remote write by itself.
