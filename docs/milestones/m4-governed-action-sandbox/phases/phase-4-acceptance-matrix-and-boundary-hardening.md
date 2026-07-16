# Phase 4: Acceptance Matrix and Boundary Hardening

## 1. Goal

Lock M4 governed-action acceptance behavior with deterministic fake-backend tests.

## 2. Scope

### Included

- Acceptance coverage for canonical IDs, policy outcomes, OCI denial, lifecycle terminals, raw payload rejection, and prohibited effects.

### Excluded

- Real OCI, network, GitHub, artifacts, retries, and new public interfaces.

## 3. Changed Files

| File | Change | Purpose |
| --- | --- | --- |
| `tests/governed_action_sandbox/test_acceptance.py` | Create | Deterministic acceptance matrix. |
| `openspec/changes/governed-action-sandbox/fixtures/expected/phase-4-acceptance/` | Create | Bounded terminal fragments. |
| `docs/milestones/m4-governed-action-sandbox/progress.md` | Modify | Record Phase 4 start. |

## 4. Implementation

Acceptance tests cover allowed, blocked, approval, stale, OCI unavailable,
command failure, timeout, output limit, cancellation, canonical IDs, zero
retry/artifacts, safe raw-payload rejection, and zero backend operations on
non-allowed paths.

## 5. Design Decisions

- All execution uses fakes.
- Raw runtime payloads must become bounded validation envelopes.

## 6. TDD and Tests

- RED: missing Phase 4 expected fixtures.
- GREEN: added bounded expected fragments and acceptance matrix.
- Verification: acceptance tests passed; full suite passed 168 tests; strict
  OpenSpec and diff checks passed.

## 7. Important Fixes and Edge Cases

- Non-allowed paths assert zero proof and run calls.
- Started and not-started attempt identities are recomputed canonically.

## 8. Commit

`b162f7b` — `test(governed-action-sandbox): add acceptance coverage`

## 9. Acceptance

Final independent review corrections were incorporated; no real side effect was performed.

## 10. Scope Boundary Confirmation

No work beyond the canonical Phase 4 scope was performed.

## 11. Follow-up

The canonical Feature 1 implementation plan is complete. This does not close
the broader M4 Draft PR MVP.
