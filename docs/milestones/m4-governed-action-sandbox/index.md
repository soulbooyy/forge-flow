# Milestone 4, Feature 1: Governed Action and Sandbox Boundary

## Scope

This first feature within the planned M4 Draft PR MVP establishes immutable governed-action contracts, exact
fixture-only command policy, and a fail-closed OCI sandbox execution seam. It
excludes patch generation/application, scanning/redaction, approval workflow,
artifact store, durable summary, GitHub activity, providers, DeerFlow runtime,
and retry.

## Authoritative References

- [Governed Action and Sandbox OpenSpec](../../../openspec/changes/governed-action-sandbox/)
- [RFC-002: Contracts and State Model](../../../rfcs/RFC-002-contracts-and-state-model.md)
- [RFC-004: Sandbox and Security Governance](../../../rfcs/RFC-004-sandbox-and-security-governance.md)
- [RFC-005: Observability and Trace Model](../../../rfcs/RFC-005-observability-and-trace-model.md)
- [RFC-006: Evaluation Framework](../../../rfcs/RFC-006-evaluation-framework.md)
- [ADR-011: OCI Container Adapter](../../../adr/ADR-011-use-oci-container-adapter-for-m4-controlled-execution.md)
- [Canonical implementation plan](implementation-plan.md)
- [Progress](progress.md)

## Feature Completion Records

- [Phase 1: Contract Foundation and Canonical Fixtures](phases/phase-1-contract-foundation-and-canonical-fixtures.md)
- [Phase 2: Exact Policy and Terminal Assembly](phases/phase-2-exact-policy-and-terminal-assembly.md)
- [Phase 3: Fail-Closed OCI Adapter and Attempt Service](phases/phase-3-fail-closed-oci-adapter-and-attempt-service.md)
- [Phase 4: Acceptance Matrix and Boundary Hardening](phases/phase-4-acceptance-matrix-and-boundary-hardening.md)

Feature 1 is complete. Milestone 4 remains planned until its separately gated
patch/security, approval/trace/summary, Draft PR adapter, and end-to-end
evaluation feature changes are complete.
