# Phase 2: Exact Policy and Terminal Assembly

## 1. Goal

Deliver pure, exact M4 policy and terminal-contract assembly for the single
registered fixture command.

## 2. Scope

### Included

- Declarative ActionIntent and CommandIntent assembly from the registered
  fixture profile.
- Pure PDR evaluation for exact, blocked, approval-required, and stale-revision
  outcomes.
- Truthful `not_started` terminal attempts for every non-allowed outcome.
- Safe Phase 2 expected policy fragments and policy tests.

### Excluded

- OCI execution, process or workspace access, artifact persistence, GitHub
  mutations, approval workflow execution, retry, and all Phase 3+ behavior.

## 3. Changed Files

| File | Change | Purpose |
| --- | --- | --- |
| `src/forgeflow/governed_action_sandbox/policy.py` | Create | Pure intent assembly, exact policy evaluation, terminal assembly, and lineage input binding. |
| `src/forgeflow/governed_action_sandbox/__init__.py` | Modify | Export the accepted Phase 2 policy API. |
| `tests/governed_action_sandbox/test_policy.py` | Create | Exact-policy, terminal, fixture, and digest-boundary coverage. |
| `openspec/changes/governed-action-sandbox/fixtures/expected/phase-2-policy/` | Create | Allowed, blocked, approval, and stale-revision expected fragments. |
| `docs/milestones/m4-governed-action-sandbox/progress.md` | Modify | Record Phase 2 authorization and start. |

## 4. Implementation

`build_action_intent`, `build_command_intent`, and `evaluate_command_intent`
return immutable contracts only. The evaluator accepts only the exact registered
fixture capability; changed capability inputs block without a started attempt.
Stale revisions map to `requires_human_approval` and a
`not_started/base_revision_mismatch` terminal. No allowed outcome creates an
ExecutionAttempt.

## 5. Design Decisions

- Exact allowed input preserves the Phase 1 canonical ActionIntent →
  CommandIntent → PDR lineage digest.
- Changed current inputs are bound through typed, recursively null-preserving
  digests, so omitted, null, and nested-null values cannot collapse to the same
  PDR input lineage.
- An internal omission sentinel distinguishes an omitted `command_args`
  argument from an explicit null input; explicit null blocks.
- The module is pure Python 3.12 standard library code and has no subprocess,
  network, filesystem, OCI, environment, or GitHub surface.

## 6. TDD and Tests

- RED: Initial policy tests failed before the policy API existed. Independent
  review regressions also reproduced stale capability-base mapping, null and
  nested-null digest collapse, and explicit-null argument handling.
- GREEN: Implemented exact fixture policy assembly and the safe lineage digest
  encoding required by each regression.
- Cumulative verification: `uv run --no-sync python -m unittest discover -s tests -v`
  passed 153 tests; Phase 2 targeted tests passed 12 tests. Strict OpenSpec,
  prohibited-I/O, and `git diff --check` verification passed.

## 7. Important Fixes and Edge Cases

- Capability-mapped stale base revisions use the same approval terminal as the
  direct stale-base input.
- Every changed current input, including unknown, null, and nested-null values,
  produces distinct policy lineage without persisting raw values.
- Blocked, approval-required, and stale paths produce only no-start terminal
  facts and never create a process or workspace capability.

## 8. Commit

`6a1fe04` — `feat(governed-action-sandbox): add exact policy evaluation`

## 9. Acceptance

Only exact registered command lineage is allowed. Changed inputs receive fresh
PDR lineage, and blocked, approval-required, and stale outcomes remain pure
contract assembly with no execution side effect. Final independent closure
review found no P1/P2 issues.

## 10. Scope Boundary Confirmation

No real OCI image, subprocess, workspace, network, GitHub mutation, artifact
persistence, approval execution, retry, or Phase 3 behavior was implemented.

## 11. Follow-up

Phase 3 is the next incomplete canonical-plan phase. Do not start it without
explicit user authorization.
