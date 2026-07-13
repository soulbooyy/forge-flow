# Phase 4: Acceptance and Hardening

## 1. Goal

Verify the complete M2 public fixture service against its accepted contract and
security boundaries, without adding a provider, execution, mutation, or
workflow capability.

## 2. Scope

### Included

- Public-service acceptance coverage for determinism, canonical identities,
  M1 evidence closure, policy outcomes, revalidation binding, terminal-error
  separation, and payload avoidance.
- Payload-free expected fragments for the accepted success and validation-error
  results.
- Strict OpenSpec validation, complete-suite verification, and static scanning
  for prohibited side-effect-related production imports.

### Excluded

- Production feature changes, real provider/LLM/MCP/DeerFlow integration,
  filesystem or workspace access, commands, network, sandbox mutation, diff,
  test execution, Git/PR, memory, or approval workflow behavior.

## 3. Changed Files

| File | Change | Purpose |
| --- | --- | --- |
| `tests/patch_proposal/test_acceptance.py` | Added | Exercise the complete public M2 proposal boundary. |
| `openspec/changes/structured-patch-proposal/fixtures/expected/phase-4-acceptance/result-fragment.json` | Added | Lock the canonical, payload-free fixture proposal. |
| `openspec/changes/structured-patch-proposal/fixtures/expected/phase-4-acceptance/validation-error-fragment.json` | Added | Lock the safe terminal validation envelope. |

## 4. Implementation

The acceptance suite invokes only public PatchProposal APIs. It verifies that
equivalent inputs produce byte-identical canonical envelopes and stable IDs;
every declared intent reference belongs to the supplied M1 evidence set; and
policy outcomes retain the allowed, approval-required, and blocked terminal
boundaries. It also verifies that changed candidate intent changes its
revalidation-bound digest, and that forbidden raw-payload input is represented
only by a safe fixed terminal envelope without leaking its value.

No production source change was required.

## 5. Design Decisions

- The acceptance tests use a separate `M2-004` task reference so their locked
  fragments are distinct from the Phase 3 service fixtures.
- Fixed error-code terminology may name the rejected field category; the
  security invariant is that no untrusted payload value reaches a success or
  terminal envelope.
- Static scanning is supplementary evidence for the no-side-effect boundary;
  the normative boundary remains the accepted OpenSpec and contract tests.

## 6. TDD and Tests

- RED: the initial public-service acceptance run exposed two test assumptions
  that did not match the accepted contract field names, plus intentionally
  absent Phase 4 expected fragments. The assertions were reconciled to
  `decision_id` and `evaluated_candidate_digest`; payload avoidance was scoped
  to payload values rather than the fixed `raw_payload_forbidden` error code.
- GREEN: generated the deterministic success and validation-error fragments;
  `uv run --no-sync python -m unittest tests.patch_proposal.test_acceptance -v`
  passed 6/6.
- Final verification: `openspec validate structured-patch-proposal --strict`
  passed; `uv run --no-sync python -m unittest discover -s tests -v` passed
  98/98; the static prohibited-import search returned no matches; and
  `git diff --check` passed.

## 7. Important Fixes and Edge Cases

- A policy block is a validation envelope, while approval-required remains a
  declarative successful proposal.
- Successful hypothesis and candidate evidence IDs must close over the exact
  supplied M1 result; a missing ID maps to `dangling_evidence_ref`.
- `revalidation_required` remains true and the evaluated candidate digest
  changes when the candidate rationale changes.
- Raw-payload values are absent from canonical terminal output and no terminal
  envelope exposes successful proposal fields.

## 8. Commit

- Full commit hash: `cb7caa6f5cb728ba94997ce405ecaa725f0bd45b`
- Commit message: `test(patch-proposal): add acceptance coverage`

## 9. Acceptance

All M2 OpenSpec scenarios are covered through the fixture-only public service.
Equivalent runs are deterministic and canonical; policy, evidence, and
terminal-envelope boundaries are verified; locked results contain no raw
payload values; and the full suite passed 98 tests.

Status: **Accepted**.

## 10. Scope Boundary Confirmation

This phase added no production capability and no provider, MCP, DeerFlow,
workspace, filesystem, command, network, sandbox, diff, mutation, validation
executor, Git/PR, memory, or approval-workflow behavior.

## 11. Follow-up

M2 implementation is complete. Milestone closure activities, including any
retrospective, require separate authorization.
