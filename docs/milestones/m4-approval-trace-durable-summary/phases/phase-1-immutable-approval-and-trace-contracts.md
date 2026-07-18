# Phase 1: Immutable Approval and Trace Contracts

## 1. Goal

Establish immutable, digest-identified approval, metadata-reference, trace, and
durable-summary facts before publication, store I/O, or service assembly.

## 2. Scope

### Included

- Frozen, slotted approval, decision, metadata-reference, trace-event, and
  durable-summary contracts.
- Strict schema, digest, bounded-identifier, profile-version, and ordered
  reference validation.
- Canonical self-excluding SHA-256 identity helpers and focused contract tests.

### Excluded

- Metadata publication, summary assembly, artifact-store I/O, source access,
  raw source/diff/patch payloads, command output, credentials, execution,
  validation/review, retry, GitHub, PR, remote storage, encryption, and
  retention.

## 3. Changed Files

| File | Change | Purpose |
| --- | --- | --- |
| `src/forgeflow/approval_trace_durable_summary/models.py` | Added | Define immutable, payload-free Phase 1 facts and validation. |
| `src/forgeflow/approval_trace_durable_summary/canonical.py` | Added | Derive canonical self-excluding contract identities. |
| `tests/approval_trace_durable_summary/test_contracts.py` | Added | Verify validation, immutability, payload exclusion, and identity behavior. |
| `docs/milestones/m4-approval-trace-durable-summary/index.md` | Modified | Link the accepted Phase 1 record. |
| `docs/milestones/m4-approval-trace-durable-summary/progress.md` | Modified | Record Phase 1 acceptance and Phase 2 authorization. |

## 4. Implementation

All contracts use frozen slotted dataclasses. Constructors accept only the
controlled Feature 3 schema, SHA-256 identifiers, positive profile versions,
fixed enums, and bounded identifier formats. Trace and summary references are
non-empty tuples of unique, lexicographically sorted digests. Canonical helpers
serialize every field except their own identity field using compact sorted JSON.

## 5. Design Decisions

- Approval remains an independent expiring lineage fact; it is not execution or
  publication authority.
- Durable identifiers carry only governed metadata references and never store
  local paths, source, diff, patch, credential, or command-output content.
- The controlled schema and identifier formats fail closed rather than allowing
  arbitrary contract text into durable facts.

## 6. TDD and Tests

- RED: added contract cases for mutable, empty, duplicate, unordered, and
  raw-payload-like inputs; the pre-correction suite failed because lists and an
  uncontrolled schema were accepted.
- GREEN: added strict constructor validation and bounded identity helpers; the
  targeted suite passed.
- Review correction: added fixed-point replacement checks and independently
  computed canonical-digest assertions proving each helper excludes only its
  own identity field; also added unordered-summary and explicit path rejection.
- Targeted verification: `PYTHONPATH=src uv run --no-sync python -m unittest
  tests.approval_trace_durable_summary.test_contracts -v` passed 7/7; `git diff
  --check` passed.

## 7. Important Fixes and Edge Cases

- Collection fields reject lists and empty, duplicate, or non-canonical tuples.
- Boolean values do not satisfy positive-integer profile version checks.
- Summary and reference constructors reject path-like identifiers; frozen
  objects cannot be modified after construction.

## 8. Commit

`feat(approval-trace): add immutable contracts`

## 9. Acceptance

An independent reviewer approved the Phase 1 implementation after verifying
the contract constraints, payload exclusions, canonical fixed points, and
complete self-exclusion coverage. The focused suite passed 7/7 and the diff
whitespace check was clean.

Status: **Accepted**.

## 10. Scope Boundary Confirmation

This phase introduced no source access, raw source/diff/patch payload,
filesystem store, execution, validation/review, retry, GitHub/PR, remote
artifact store, encryption, or retention capability.

## 11. Follow-up

Next Phase: Metadata-only publication and summary assembly, under the standing
Feature 3 authorization.
