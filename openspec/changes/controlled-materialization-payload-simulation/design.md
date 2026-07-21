# Controlled Materialization and Payload Simulation Design

The harness injects a registered snapshot and resolves target-file IDs from a
controlled registry. It revalidates repository/base/snapshot/target digests,
then permits one registered transformer only when a fresh allowed
`MaterializationPDR` binds every input and the Feature 1 profile/image.

Docker is network-disabled, credential-free, empty-environment, and consumes a
read-only snapshot. Materialized bytes exist only in harness-owned temporary
storage. Security scanning and Feature 1 validation create facts, not
authority. A `MaterializedCommitPayload` carries only identities, digests,
lineage, security/validation/review references, and PDR IDs.

A new fresh `PayloadEligibilityPDR` may authorize deterministic local fake
Git-data simulation for that one payload. The fake adapter verifies the
ephemeral handle, payload identity/digests, repository/base, and both scoped
PDRs. Simulation IDs use `forgeflow-sim-*`; real mutation surfaces reject
them. Every mismatch or expired handle fails closed with a controlled terminal.
