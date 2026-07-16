# Milestone 4: Governed Action and Sandbox Boundary Progress

## Purpose

This is execution state only. It does not replace the OpenSpec, accepted
RFCs/ADRs, or the canonical implementation plan.

## Authoritative References

- [Governed Action and Sandbox OpenSpec](../../../openspec/changes/governed-action-sandbox/)
- [Canonical implementation plan](implementation-plan.md)
- [RFC-002](../../../rfcs/RFC-002-contracts-and-state-model.md), [RFC-004](../../../rfcs/RFC-004-sandbox-and-security-governance.md), [RFC-005](../../../rfcs/RFC-005-observability-and-trace-model.md), and [RFC-006](../../../rfcs/RFC-006-evaluation-framework.md)
- [Implementation execution](../../process/implementation-execution.md)

## Execution Environment

| Field | Value |
| --- | --- |
| Branch | `feature/m4-governed-action-sandbox` |
| Worktree | `.worktrees/m4-governed-action-sandbox` |
| Execution mode | Lightweight Implementation Execution |

## Current Status

| Field | Value |
| --- | --- |
| Milestone | Governed Action and Sandbox Boundary |
| State | Canonical implementation complete; external OCI evaluation not closed |
| Completed through | Phase 4: Acceptance Matrix and Boundary Hardening |
| Next phase | None |
| Implementation authorization | Canonical M4 plan complete; no further work authorized by this plan |

## Phase Index

| Phase | Name | Status | Commit | Completion Record |
| --- | --- | --- | --- | --- |
| 1 | Contract Foundation and Canonical Fixtures | Complete | `88bbbae` | [Phase 1 record](phases/phase-1-contract-foundation-and-canonical-fixtures.md) |
| 2 | Exact Policy and Terminal Assembly | Complete | `6a1fe04` | [Phase 2 record](phases/phase-2-exact-policy-and-terminal-assembly.md) |
| 3 | Fail-Closed OCI Adapter and Attempt Service | Complete | `746a0f9` | [Phase 3 record](phases/phase-3-fail-closed-oci-adapter-and-attempt-service.md) |
| 4 | Acceptance Matrix and Boundary Hardening | Complete | `b162f7b` | [Phase 4 record](phases/phase-4-acceptance-matrix-and-boundary-hardening.md) |

## Change Log

- 2026-07-16: Ran the single explicitly authorized real OCI fixture probe using
  the registered image digest. It exited non-zero under the required isolation
  controls; no retry or external mutation was performed. See [redacted run
  evidence](evidence/real-oci-fixture-run-2026-07-16.md).
- 2026-07-16: Completed Phase 4 in `b162f7b`; canonical M4 implementation is complete.
- 2026-07-16: Began explicitly authorized Phase 4 under the assigned M4
  worktree; no work beyond the canonical plan is authorized.
- 2026-07-16: Completed Phase 3 in `746a0f9`; final independent closure review
  found no P1/P2. Phase 4 remains unstarted pending explicit authorization.
- 2026-07-15: Began explicitly authorized Phase 3 under the assigned M4
  worktree; Phase 4 remains out of scope.
- 2026-07-15: Completed Phase 2 in `6a1fe04`; final independent closure review
  found no P1/P2 after stale-base and null-preserving PDR-lineage corrections.
  Phase 3 remains unstarted pending explicit authorization.
- 2026-07-15: Began explicitly authorized Phase 2 under the assigned M4
  worktree; Phase 3 remains out of scope.
- 2026-07-15: Completed Phase 1 in `88bbbae`; independent closure review
  passed after contract, terminal-fact, resource, timeout, and lineage
  corrections. Phase 2 remains unstarted pending explicit authorization.
- 2026-07-15: Assigned the milestone isolation environment: branch
  `feature/m4-governed-action-sandbox`, worktree
  `.worktrees/m4-governed-action-sandbox`; began explicitly authorized Phase 1
  under Lightweight Implementation Execution.
- 2026-07-15: Canonical plan accepted after independent review; awaiting
  explicit Phase 1 authorization. No branch, worktree, implementation, sandbox
  execution, or GitHub mutation is authorized.
