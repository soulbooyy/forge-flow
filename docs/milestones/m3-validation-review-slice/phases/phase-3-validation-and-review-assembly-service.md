# Phase 3: Validation and Review Assembly Service

## 1. Goal

Assemble fixture-only validation terminals/results and review results with safe
lineage and error envelopes.

## 2. Scope

### Included

- Deterministic service assembly from M2 proposals and M3 policy/fixture cases.
- Safe policy terminal, completed-result, review, and error mappings.

### Excluded

- Commands, sandbox, workspace I/O, network, retry, provider, runtime, Git, or PR behavior.

## 3. Changed Files

| File | Change | Purpose |
| --- | --- | --- |
| `src/forgeflow/validation_review/service.py` | Added | Assemble fixture-only envelopes. |
| `src/forgeflow/validation_review/__init__.py` | Modified | Export public service APIs. |
| `tests/validation_review/test_service.py` | Added | Verify terminals, lineage, safe errors, and forbidden payload handling. |

## 4. Implementation

The service validates proposal lineage before fixture assembly, emits terminals
before attempt lookup for non-allowed policy, and computes final IDs last.
Forbidden fixture field names map to `forbidden_payload` without reading or
echoing their values.

## 5. Design Decisions

- Service is pure and fixture-only; policy decides, review records findings.
- Terminals never contain attempt facts; review rejects terminals.

## 6. TDD and Tests

- RED: missing `service.py` caused the targeted service import failure.
- GREEN: targeted service tests passed 4/4 after assembly and safe-payload mapping.
- Cumulative verification: `unittest discover` passed 120/120; strict OpenSpec,
  static side-effect checks, and `git diff --check` passed.
- Independent review found and the follow-up review verified the forbidden-payload mapping.

## 7. Important Fixes and Edge Cases

- Unknown policy/fixture cases become safe errors.
- Raw fixture payload field names produce `forbidden_payload` without value disclosure.

## 8. Commit

- Full commit hash: `695d6ef`
- Commit message: `feat(validation-review): assemble fixture-only result flows`

## 9. Acceptance

Validation/result/terminal/review separation, M2/M3 lineage, and safe payload
failure semantics are covered. Status: **Accepted**.

## 10. Scope Boundary Confirmation

No execution or external side-effect surface was introduced.

## 11. Follow-up

Phase 4 requires explicit user authorization.
