# Milestone 4: Deterministic Patch Artifact and Security Scanning Progress

## Purpose

This is execution state only. It does not replace the OpenSpec, accepted
RFCs/ADRs, or the canonical implementation plan.

## Authoritative References

- [OpenSpec change](../../../openspec/changes/deterministic-patch-artifact-security/proposal.md)
- [Canonical implementation plan](implementation-plan.md)
- [RFC-002](../../../rfcs/RFC-002-contracts-and-state-model.md), [RFC-004](../../../rfcs/RFC-004-sandbox-and-security-governance.md), and [RFC-005](../../../rfcs/RFC-005-observability-and-trace-model.md)
- [Implementation execution](../../process/implementation-execution.md)

## Execution Environment

| Field | Value |
| --- | --- |
| Branch | `feature/m4-deterministic-patch-artifact-security` |
| Worktree | `.worktrees/m4-deterministic-patch-artifact-security` |
| Execution mode | Lightweight Implementation Execution |

## Current Status

| Field | Value |
| --- | --- |
| Milestone | M4 Feature 2: Deterministic Patch Artifact and Security Scanning |
| State | Re-baselined Phase 2 accepted after independent review. |
| Completed through | Re-baselined Phase 2: Transient metadata security facts. |
| Next phase | Re-baselined Phase 3: Passed-path assembly |
| Implementation authorization | Phase 3 is not authorized. |

## Phase Index

| Phase | Name | Status | Commit | Completion Record |
| --- | --- | --- | --- | --- |
| 1 | Immutable Contract and Canonical Identity | Historical; superseded by terminal-first amendment | `6ccb064`, `f9f5061` | [Phase 1 record](phases/phase-1-immutable-contract-and-canonical-identity.md) |
| 2 | Registered Metadata Security Facts | Historical; superseded by terminal-first amendment | `27a2685`, `6281867`, `fe476fb`, `0d1ac55`, `6f7bbab`, `2f54dd2` | [Phase 2 record](phases/phase-2-registered-metadata-security-facts.md) |
| 3 | Metadata-only Assembly Service | Historical; superseded by terminal-first amendment | `0fbb308`, `0cf469b` | [Phase 3 record](phases/phase-3-metadata-only-assembly-service.md) |
| 4 | Acceptance and Boundary Hardening | Stopped pending amendment | None | None |
| 1R | Pre-scan contracts and terminal identity | Accepted after independent review | This phase commit | [Phase 1R record](phases/phase-1-pre-scan-contracts-and-terminal-identity.md) |
| 2R | Transient metadata security facts | Accepted after independent review | This phase commit | [Phase 2R record](phases/phase-2-transient-metadata-security-facts.md) |

## Change Log

- 2026-07-16: Accepted OpenSpec, metadata security profile, and canonical plan; Phase 1 authorized in the assigned isolated environment.
- 2026-07-16: Accepted Phase 1 in `6ccb064`; targeted tests passed 5/5, the cumulative suite passed 128 tests, strict OpenSpec validation and static no-I/O verification passed. Phase 2 is not authorized.
- 2026-07-16: Corrected Phase 1 state to pending independent review. The change
  modifies contracts, security boundary, and canonical identity, so process
  section 1.7 requires an approved independent review before acceptance.
- 2026-07-16: Accepted Phase 1 after approved independent review. Three review
  rounds found and verified contract-security corrections; targeted tests passed
  10/10, the cumulative suite passed 133 tests, strict OpenSpec validation and
  static no-I/O verification passed. Phase 2 remains unauthorized.
- 2026-07-18: Phase 2 authorized in the assigned isolated environment.
- 2026-07-18: Accepted Phase 2 after independent review. Targeted policy tests
  passed 11/11; the cumulative suite passed 144 tests; strict OpenSpec
  validation, diff hygiene, and static no-I/O verification passed. Phase 3 is
  not authorized.
- 2026-07-18: Phase 3 authorized in the assigned isolated environment; the
  independent-subagent review permission also applies to this phase.
- 2026-07-18: Accepted Phase 3 after independent review. Targeted service tests
  passed 8/8; the cumulative suite passed 152 tests; strict OpenSpec
  validation, diff hygiene, and static no-I/O verification passed. Phase 4 is
  not authorized.
- 2026-07-18: Phase 4 authorized in the assigned isolated environment; the
  independent-subagent review permission also applies to this phase.
- 2026-07-18: Phase 4 RED acceptance test exposed that blocked matched metadata
  remained in PatchIntent. User selected the terminal-first architecture:
  pre-scan identity and security facts precede all PatchIntent/PatchArtifact
  construction. OpenSpec/RFC/profile/plan amendment is pending acceptance; no
  implementation phase is authorized.
- 2026-07-18: User accepted the terminal-first RFC/OpenSpec/profile/canonical
  plan amendment and authorized re-baselined Phase 1. Phase 1 replaces the
  pre-scan contract lineage with `PreScanPatchMetadataIdentity` and introduces
  `PatchSecurityTerminal`; no Phase 2 policy or Phase 3 service behavior is
  resumed during this phase.
- 2026-07-18: Accepted re-baselined Phase 1 after independent review. The
  targeted contract/canonical suite passed 9/9; strict OpenSpec validation,
  diff hygiene, and static no-I/O verification passed. The historical
  artifact-first policy/service failures remain owned by the unauthorized
  re-baselined Phase 2/3 work.
- 2026-07-18: Accepted re-baselined Phase 2 after independent review. The
  policy suite passed 7/7, including profile mismatch, invalid projection,
  blocked-rule, and tampered-scan fail-closed cases. Phase 2 returns only
  scan/redaction facts and creates no candidate; Phase 3 remains unauthorized.
