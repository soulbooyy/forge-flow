# Phase 4: Acceptance and Hardening

## 1. Goal

Lock M3 public-service acceptance behavior with deterministic expected fragments
and verify the complete fixture-only boundary.

## 2. Scope

### Included

- Public-service acceptance tests for results, terminals, review, and safe errors.
- Four canonical expected Phase 4 fragments for validation, terminal, review,
  and error envelopes.
- Full M3 verification and approved independent review.

### Excluded

- Production API changes, command execution, sandboxing, workspace I/O,
  network, retry, providers, runtime adapters, Git, or PR behavior.

## 3. Changed Files

| File | Change | Purpose |
| --- | --- | --- |
| `tests/validation_review/test_acceptance.py` | Added | Lock public-service acceptance and safety boundaries. |
| `openspec/changes/validation-review-slice/fixtures/expected/phase-4-acceptance/validation-fragment.json` | Added | Lock completed validation facts and lineage. |
| `openspec/changes/validation-review-slice/fixtures/expected/phase-4-acceptance/terminal-fragment.json` | Added | Lock policy-blocked terminal facts. |
| `openspec/changes/validation-review-slice/fixtures/expected/phase-4-acceptance/review-fragment.json` | Added | Lock review finding and policy lineage. |
| `openspec/changes/validation-review-slice/fixtures/expected/phase-4-acceptance/error-fragment.json` | Added | Lock safe forbidden-payload error behavior. |

## 4. Implementation

Acceptance calls only the Phase 3 public service API and compares its
dataclass envelopes to JSON fragments. It covers repeated deterministic results,
passed and failed facts, blocked and approval-required terminals, blocking
review lineage, malformed fixtures, review-after-terminal rejection, payload
redaction, and the absence of execution/retry fields.

## 5. Design Decisions

- ADR-008 remains controlling: fixtures prove contracts and do not grant
  execution authority.
- The four Phase 4 fragments are the canonical acceptance locks required by the
  M3 implementation plan; they contain only payload-free contract data.

## 6. TDD and Tests

- RED: No separate RED result was recorded: Phase 4 adds acceptance coverage
  against the already-accepted Phase 3 public service and introduces no
  production behavior. This is a recorded deviation from the plan's explicit
  RED-capture instruction.
- GREEN: targeted acceptance tests passed 3/3 after the expected fragments and
  coverage matrix were complete.
- Refactor/correction: the first approved independent review found missing
  Phase 4 fragments and incomplete acceptance coverage; the corrective update
  added the four fragments plus passed, malformed-input, terminal-review, and
  forbidden-field checks. Follow-up independent review found no remaining
  blocking issue.
- Cumulative verification: `uv run --no-sync python -m unittest discover -s
  tests -v` passed 123/123; `openspec validate validation-review-slice --strict`,
  the prohibited-import search, and `git diff --check` passed.

## 7. Important Fixes and Edge Cases

- Terminals remain attempt-free, including approval-required terminals.
- Safe errors do not disclose raw payload values and cannot become results or
  reviews.
- Acceptance explicitly rejects command, output, retry, and next-attempt
  fields on every success, terminal, and review envelope.

## 8. Commit

`336c417f9a4364b7bd466b6b383209c74fc6c247` — `test(validation-review): add acceptance coverage`

## 9. Acceptance

All M3 OpenSpec scenarios are covered by the cumulative deterministic fixture
suite; Phase 4 public outputs are fixture-locked. Approved independent review
passed after the documented correction. Status: **Accepted**.

## 10. Scope Boundary Confirmation

No production code or side-effecting surface was introduced. M3 remains
contract-first and fixture-based; command execution, sandboxing, and retry are
deferred.

## 11. Follow-up

M3 implementation is complete. Stop and await explicit user confirmation
before milestone closure, integration, or any new work.
