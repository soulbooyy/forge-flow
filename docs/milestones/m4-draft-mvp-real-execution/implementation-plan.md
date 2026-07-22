# M4 Draft-MVP Real Execution Canonical Plan

## Authority

User authorization on 2026-07-22 permits Phase 1 zero-effect preparation only.
It does not authorize Docker invocation, credential access, GitHub API calls,
or mutation.

## Execution sequence

1. **Phase 1:** RED/GREEN pure real-mutation PDR, request/idempotency, and
   terminal contracts. Keep the v1 types and simulation namespace out of the
   real adapter import surface.
2. **Docker gate:** accept a matrix proving the exact local image, verified
   base snapshot, read-only/empty/no-network/no-credential settings, limits,
   cleanup, and redacted evidence procedure. Only then implement and run one
   local Docker scenario.
3. **GitHub gate:** accept exact fixture repository/Issue/base, credential
   governance, idempotency/reconciliation, one-branch/one-commit/one-Draft-PR
   cap, reset owner, and audit procedure. Only then implement and run one
   fixture Draft PR scenario.
4. **Closure:** prove denied and fault paths create zero external effects;
   reset the fixture and retain redacted audit evidence.

Every phase follows RED → GREEN → targeted verification → independent review
→ repair → closure record → focused commit. External gates are mandatory
pause points because they authorize new side effects.
