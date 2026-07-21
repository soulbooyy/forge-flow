# Phase 3: Controlled Local Metadata Store

## 1. Goal

Atomically persist verified canonical metadata bytes under harness-injected root.

## 2. Scope

### Included

- Temporary write, no-clobber publication, verification, cleanup, and fsync.

### Excluded

- Raw payloads, remote stores, encryption, retention, and execution.

## 3. Changed Files

| File | Change | Purpose |
| --- | --- | --- |
| `store.py` | Added | Controlled metadata-only store adapter. |
| `models.py`, `service.py` | Modified | Separate published and candidate lineage digests. |
| `test_store.py` | Added | Atomic-store failure and immutability tests. |

## 4. Implementation

Published bytes exclude derived identity/digest fields. The public path accepts
only a canonical Feature 2 candidate and derives the reference internally.

## 5. Design Decisions

`content_digest` identifies published bytes; `candidate_content_digest` retains
Feature 2 redacted metadata lineage.

## 6. TDD and Tests

Store RED import test preceded implementation; targeted regression tests passed
5/5 after independent-review corrections.

## 7. Important Fixes and Edge Cases

No-clobber hard links, canonical ID checks, post-link cleanup, byte readback,
and directory fsync close publication failure windows.

## 8. Commit

`da98e65` — `feat(approval-trace): publish controlled metadata artifacts`

## 9. Acceptance

Independent review verified immutable, provenance-bound, metadata-only publish.

## 10. Scope Boundary Confirmation

Root paths are runtime-only and never stored in contracts or summaries.

## 11. Follow-up

Phase 4 performs end-to-end boundary hardening.
