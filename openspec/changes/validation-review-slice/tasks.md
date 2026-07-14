# Validation and Review Slice Tasks

## Readiness Gate

- [x] Confirm the contract-first, deterministic-fixture architecture in
  ADR-008 and the relevant RFCs.
- [x] Complete Grill-Me review and record its accepted constraints in ADR-008.
- [x] Define the OpenSpec scope and contract boundary without authorizing a
  command runner, sandbox, runtime integration, or retry implementation.

## Specification and Planning

- [x] Define the `ValidationResult`, `ValidationTerminal`, and `ReviewResult`
  envelopes, lineage, identity, fixture, policy-reference, and failure rules.
- [x] Define acceptance scenarios for completed facts, governance terminals,
  review findings, redaction, and absence of side effects.
- [x] After review of this OpenSpec and relevant RFC/ADR authority, create the
  non-authoritative AI-assisted M3 draft implementation plan only when the
  user explicitly requests `writing-plans`.
- [x] Reconcile that draft into the sole canonical M3 implementation plan.
- [x] Create M3 milestone index and `progress.md` only with the canonical plan.

## Implementation

Implementation completed through all four accepted canonical phases. The
accepted fixture-only boundary remains closed to additional execution scope.

- [x] Begin implementation only after the canonical M3 plan, explicit Phase 1
  authorization, and assigned milestone execution environment were recorded.
- [x] Keep every later M3 phase fixture-only; do not add command execution,
  sandbox behavior, workspace access, network, dynamic installation, retries,
  or provider/runtime integration.
