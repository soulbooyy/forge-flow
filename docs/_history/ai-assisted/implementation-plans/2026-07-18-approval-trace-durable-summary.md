# Approval, Trace, and Durable Summary Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish only eligible immutable metadata artifacts, bind independent expiring approval facts, and append redacted durable trace/summary lineage.

**Architecture:** Feature 3 accepts Feature 2 metadata candidates, never source/diff/patch payloads. Pure contracts and summary assembly precede an injected local store adapter; publication is temporary-write, atomic publish, digest verification, then reference creation.

**Tech Stack:** Python 3.12 standard library, frozen dataclasses, `unittest`, canonical JSON/SHA-256.

## Global Constraints

- Never persist raw source, diff, patch payload, command output, credential, environment value, or temporary path.
- Do not implement GitHub, Draft PR, execution, validation/review, retry, DeerFlow, remote storage, encryption, or retention.
- Only a fresh PDR authorizes a later action; approval and artifact facts are non-authorizing.
- The harness injects the only artifact-store root; paths are never contract identities.

---

### Task 1: Immutable Approval and Trace Contracts

**Files:**
- Create: `src/forgeflow/approval_trace_durable_summary/models.py`
- Create: `src/forgeflow/approval_trace_durable_summary/canonical.py`
- Test: `tests/approval_trace_durable_summary/test_contracts.py`
- Test: `tests/approval_trace_durable_summary/test_canonical.py`

**Interfaces:** Produces `ApprovalRequest`, `ApprovalDecision`,
`MetadataArtifactReference`, `TraceEvent`, `DurableRunSummary`, and digest
helpers. All fields use IDs/enums/digests only.

- [ ] Write failing tests for frozen contracts, exact approval lineage/expiry,
  ordered append-only event IDs, and absence of forbidden fields.
- [ ] Run `PYTHONPATH=src uv run --no-sync python -m unittest tests.approval_trace_durable_summary.test_contracts tests.approval_trace_durable_summary.test_canonical -v`; expect import failure.
- [ ] Implement frozen slotted dataclasses and canonical self-excluding IDs.
- [ ] Re-run the command; expect all tests pass.
- [ ] Commit `feat(approval-trace): add immutable contracts`.

### Task 2: Metadata-only Publication and Summary Assembly

**Files:**
- Create: `src/forgeflow/approval_trace_durable_summary/service.py`
- Test: `tests/approval_trace_durable_summary/test_service.py`

**Interfaces:** `publishable_metadata(candidate, approval, policy) -> MetadataArtifactReference | Terminal`; `append_summary(summary, event) -> DurableRunSummary`.

- [ ] Write failing tests for eligible candidate, expired/mismatched approval,
  blocked candidate, and append ordering.
- [ ] Run `PYTHONPATH=src uv run --no-sync python -m unittest tests.approval_trace_durable_summary.test_service -v`; expect failure.
- [ ] Implement pure fail-closed eligibility and append-only assembly with no filesystem access.
- [ ] Re-run the command; expect all tests pass.
- [ ] Commit `feat(approval-trace): assemble metadata publication facts`.

### Task 3: Controlled Local Metadata Store

**Files:**
- Create: `src/forgeflow/approval_trace_durable_summary/store.py`
- Test: `tests/approval_trace_durable_summary/test_store.py`

**Interfaces:** `publish_metadata(root, artifact) -> MetadataArtifactReference | Terminal`; root is harness-supplied and artifacts are canonical metadata bytes only.

- [ ] Write failing tests for atomic publish, content-digest verification, root rejection, and no reference after write/verification failure.
- [ ] Run `PYTHONPATH=src uv run --no-sync python -m unittest tests.approval_trace_durable_summary.test_store -v`; expect failure.
- [ ] Implement temporary-write, atomic replace, verification, and no partial eligible reference.
- [ ] Re-run the command; expect all tests pass.
- [ ] Commit `feat(approval-trace): publish controlled metadata artifacts`.

### Task 4: Acceptance and Boundary Hardening

**Files:**
- Create: `tests/approval_trace_durable_summary/test_acceptance.py`
- Modify: phase-scoped package/docs only when an acceptance failure requires it.

**Interfaces:** Uses only Tasks 1–3 public APIs.

- [ ] Write failing end-to-end tests proving no patch payload, source, diff,
  GitHub, execution, retry, or raw summary persistence; cover approval expiry
  and publication failure.
- [ ] Run `PYTHONPATH=src uv run --no-sync python -m unittest tests.approval_trace_durable_summary.test_acceptance -v`; expect failure.
- [ ] Make only minimum scoped corrections.
- [ ] Run `PYTHONPATH=src uv run --no-sync python -m unittest discover -s tests -v`, `openspec validate approval-trace-durable-summary --strict`, and `git diff --check`; expect pass.
- [ ] Commit `test(approval-trace): harden durable summary acceptance`.

## Self-Review

Coverage maps Task 1 to approval/trace contracts, Task 2 to fail-closed
lineage, Task 3 to RFC-005 atomic metadata publication, and Task 4 to every
OpenSpec exclusion. The plan defines no patch material, source access, GitHub,
or execution interface. No placeholders remain.
