# Phase 2: Metadata-Only Publication and Summary Assembly

## 1. Goal

Derive durable metadata references only from canonical Feature 2 candidates and
append canonical same-run trace facts without I/O.

## 2. Scope

### Included

- Canonical candidate verification, reference assembly, and summary append.

### Excluded

- Store I/O, source/diff/patch content, execution, and external effects.

## 3. Changed Files

| File | Change | Purpose |
| --- | --- | --- |
| `service.py` | Added | Pure fail-closed reference and summary assembly. |
| `test_service.py` | Added | Candidate, lineage, and append-boundary tests. |

## 4. Implementation

Only Feature 2 canonical candidates can produce a reference; forged inputs
return no reference. Summary append validates both identities and run binding.

## 5. Design Decisions

Approval remains non-authorizing; no payload or store location enters a fact.

## 6. TDD and Tests

RED import failure preceded the minimal service. Targeted tests passed 4/4.

## 7. Important Fixes and Edge Cases

Tampered candidates, unsafe run IDs, duplicate events, and cross-run events
fail closed.

## 8. Commit

`0cf6f62` — `feat(approval-trace): assemble metadata publication facts`

## 9. Acceptance

Independent review passed after adding required append-only summary assembly.

## 10. Scope Boundary Confirmation

No filesystem, source, diff, patch, execution, GitHub, retry, or remote store.

## 11. Follow-up

Phase 3 adds the controlled local store.
