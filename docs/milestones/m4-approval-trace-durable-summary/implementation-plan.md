# M4 Feature 3: Approval, Trace, and Durable Summary Canonical Plan

## Authority

This plan follows the accepted Feature 3 OpenSpec and RFC-002/004/005. It is
the sole implementation authority after explicit Phase 1 authorization.

## Reconciliation

The AI-assisted draft is retained as non-canonical evidence. This plan accepts
its four-phase ordering, but resolves all ambiguity in favor of the accepted
OpenSpec: publication is metadata-only; approval is non-authorizing; the store
root is harness-injected; and no phase introduces source access, patch payload,
execution, GitHub, remote storage, or retry.

## Phases

1. **Immutable approval and trace contracts** — models, canonical IDs, exact
   expiry/lineage, and payload-exclusion tests. No store I/O.
2. **Metadata-only publication and summary assembly** — eligible-candidate
   validation, immutable references, append-only summary facts, fail-closed
   terminals. No patch content.
3. **Controlled local store adapter** — injected root, temporary write, atomic
   publish, content verification, and no partial-reference behavior.
4. **Acceptance and boundary hardening** — end-to-end fixture tests and
   prohibited capability checks.

Every phase uses RED → GREEN → scoped refactor → targeted/cumulative tests,
focused commit, completion record, progress update, and required independent
review for contract/security/store changes.

## Global Acceptance

Only immutable metadata artifacts may be published. Any candidate, approval,
profile, redaction, write, verification, or append failure is fail-closed with
no eligible durable reference or partial summary linkage. A fresh PDR remains
the only authorization for any later action.
