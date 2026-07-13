# Phase 2: Deterministic Policy and Attempt Fixtures

## 1. Goal

Establish pure, deterministic M3 policy fixtures and in-memory validation/review
fixture facts without creating a command, sandbox, workspace, network, or
runtime execution surface.

## 2. Scope

### Included

- A pure `policy_record_for()` fixture adapter for `allowed`, `blocked`, and
  `requires_human_approval` Policy Decision Record references.
- In-memory completed validation-attempt and review-finding fixture lookup.
- Payload-free expected policy and attempt fragments with computed PDR IDs.
- Focused policy/fixture tests, fixture locking, unknown-case rejection, and
  static no-I/O checks.

### Excluded

- Validation/review service assembly, terminal/result construction, or public
  workflow behavior.
- Command execution, sandbox/runtime behavior, workspace/config access,
  network, dependency installation, retry, provider/MCP/DeerFlow, Git, or PR
  integration.

## 3. Changed Files

| File | Change | Purpose |
| --- | --- | --- |
| `src/forgeflow/validation_review/policy.py` | Added | Construct computed deterministic Policy Decision Record fixtures. |
| `src/forgeflow/validation_review/fixture_source.py` | Added | Supply fixed in-memory validation-attempt and review-finding facts. |
| `tests/validation_review/test_policy.py` | Added | Verify all policy outcomes, computed IDs, unknown cases, forbidden-field profile data, and expected fragments. |
| `tests/validation_review/test_fixture_source.py` | Added | Verify completed facts, review facts, unknown cases, expected fragments, and no-I/O source boundary. |
| `openspec/changes/validation-review-slice/fixtures/expected/phase-2-policy/allowed.json` | Added | Lock an allowed PDR fixture. |
| `openspec/changes/validation-review-slice/fixtures/expected/phase-2-policy/blocked.json` | Added | Lock a blocked PDR fixture. |
| `openspec/changes/validation-review-slice/fixtures/expected/phase-2-policy/requires-human-approval.json` | Added | Lock an approval-required PDR fixture. |
| `openspec/changes/validation-review-slice/fixtures/expected/phase-2-policy/passed-attempt.json` | Added | Lock a passed completed-attempt fixture. |
| `openspec/changes/validation-review-slice/fixtures/expected/phase-2-policy/failed-attempt.json` | Added | Lock a failed completed-attempt fixture. |

## 4. Implementation

The policy adapter maps only three controlled case IDs to immutable PDR facts.
It calculates each `decision_id` from the PDR payload with only the identity
field omitted. Unknown cases are lookup failures. The fixture source holds two
completed validation facts and one blocking review finding in module-level
in-memory values; it performs no configuration read, workspace operation, or
tool invocation.

## 5. Design Decisions

- Policy fixtures are explicit test data, not a policy engine or execution
  authorization mechanism.
- `blocked` and `requires_human_approval` produce governance facts only; they
  do not create a validation attempt fixture.
- Fixture attempt facts have no command or output field; review fixtures have
  findings only and no policy decision field.
- Expected JSON fragments are verified against generated values, preventing
  PDR ID or fixture-content drift.

## 6. TDD and Tests

- RED: `uv run --no-sync python -m unittest tests.validation_review.test_policy tests.validation_review.test_fixture_source -v` failed with missing `forgeflow.validation_review.policy` and `fixture_source` modules before implementation.
- GREEN: the same targeted command passed 7/7 after adding the minimal pure
  policy adapter and in-memory fixture source.
- Fixture-lock correction: JSON arrays and Python tuples initially compared as
  different representations in the policy fixture test. The test now compares
  JSON-native values; targeted coverage passed 9/9.
- Cumulative verification: `uv run --no-sync python -m unittest discover -s tests -v` passed 116/116.
- Static boundary verification found no subprocess, network, or filesystem
  execution imports in `src/forgeflow/validation_review`.
- Specification and diff verification: `openspec validate validation-review-slice --strict` and `git diff --check` passed.
- Independent review was explicitly approved before review. It found no
  blocking issue in the Phase 2 diff.

## 7. Important Fixes and Edge Cases

- PDR IDs change with decision and risk flags, preventing a fixture outcome
  from reusing the identity of another outcome.
- Unknown policy, validation, and review fixture cases fail deterministically
  rather than falling back to workspace, provider, or tool behavior.
- Attempt fragments retain only IDs, case ID, outcome, and controlled finding
  codes; raw reports and execution details cannot enter fixture facts.

## 8. Commit

- Full commit hash: `569d1f2c56e2217fdad22d0c9486eb8505433116`
- Commit message: `feat(validation-review): add deterministic policy fixtures`

## 9. Acceptance

All three policy outcomes are deterministic, independently identified, and
fixture-locked. The completed attempt and review fixtures are in-memory,
payload-free, and have no I/O or execution surface. Targeted tests passed 9/9;
the full suite passed 116/116. The independent review found no blocking issue.

Status: **Accepted**.

## 10. Scope Boundary Confirmation

This phase added no service assembly, command runner, sandbox, workspace or
configuration access, network, dependency installation, retry, provider,
runtime, Git, or PR integration.

## 11. Follow-up

Next Phase: Validation and Review Assembly Service. It requires explicit user
authorization before starting.
