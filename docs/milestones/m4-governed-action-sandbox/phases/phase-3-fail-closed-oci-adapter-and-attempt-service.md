# Phase 3: Fail-Closed OCI Adapter and Attempt Service

## 1. Goal

Deliver a fake-backend-tested, fail-closed OCI attempt seam.

## 2. Scope

### Included

- Explicit ActionIntent, CommandIntent, and PDR execution inputs.
- Pre-start OCI proof, bounded run facts, and truthful terminal assembly.

### Excluded

- Real OCI execution, network, workspace access, GitHub mutation, artifacts,
  retries, and Phase 4.

## 3. Changed Files

| File | Change | Purpose |
| --- | --- | --- |
| `src/forgeflow/governed_action_sandbox/oci_adapter.py` | Create | Typed injected OCI proof/run seam. |
| `src/forgeflow/governed_action_sandbox/service.py` | Create | PDR-first fail-closed attempt service. |
| `tests/governed_action_sandbox/test_oci_adapter.py` | Create | OCI proof boundary tests. |
| `tests/governed_action_sandbox/test_service.py` | Create | PDR, terminal, fault, and lineage tests. |
| `openspec/changes/governed-action-sandbox/fixtures/expected/phase-3-service/` | Create | Controlled terminal fragments. |

## 4. Implementation

The service permits `run` only for a canonically valid allowed PDR after a
strict pre-start OCI proof. Non-allowed PDRs create no-start facts with zero
backend run calls. Backend faults, malformed facts, and post-run security
inconsistency return payload-free validation envelopes.

## 5. Design Decisions

- Proof and run are separate operations; no host fallback exists.
- OCI proof and run facts require exact types and literal booleans.
- Raw output, credentials, paths, runtime objects, and artifacts are absent.

## 6. TDD and Tests

- RED: Phase 3 API imports initially failed.
- GREEN: Controlled fakes cover proof failure, non-allowed zero run, stale,
  cancellation, budgets, tampered PDRs, faults, and malformed facts.
- Verification: targeted 11 tests and complete suite of 164 tests passed;
  strict OpenSpec, prohibited-I/O, and diff checks passed.

## 7. Important Fixes and Edge Cases

- Untrusted/duck-typed proof or run facts fail closed.
- A post-run inconsistency is never rewritten as `not_started`.

## 8. Commit

`746a0f9` — `feat(governed-action-sandbox): add fail-closed oci attempt service`

## 9. Acceptance

Final independent closure review found no P1/P2. All automated execution uses
only fakes; no real OCI image was run.

## 10. Scope Boundary Confirmation

No real OCI, process, network, GitHub mutation, artifact persistence, retry,
or Phase 4 work was performed.

## 11. Follow-up

Phase 4 requires explicit user authorization.
