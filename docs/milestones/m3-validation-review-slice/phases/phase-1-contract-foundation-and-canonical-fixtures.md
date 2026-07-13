# Phase 1: Contract Foundation and Canonical Fixtures

## 1. Goal

Establish the immutable, deterministic, payload-free M3 contract foundation:
`ValidationResult`, `ValidationTerminal`, `ReviewResult`, Policy Decision
Record references, safe validation errors, the fixture profile, canonical
identity helpers, and expected fixtures.

## 2. Scope

### Included

- Frozen, slotted M3 result, terminal, review, policy-reference, finding, and
  validation-error models.
- The immutable `validation-review/m3-fixture-v1` profile and controlled values.
- Canonical JSON and independent result, terminal, review, error, and policy
  identity helpers.
- Focused contract/canonical tests and four expected payload-free fixtures.

### Excluded

- Policy-fixture evaluation, fake-executor lookup, validation/review service
  assembly, or public acceptance service behavior.
- Command execution, command parsing, sandbox/runtime behavior, workspace I/O,
  network, dependency installation, retry, provider/MCP/DeerFlow, Git, or PR
  integration.

## 3. Changed Files

| File | Change | Purpose |
| --- | --- | --- |
| `src/forgeflow/validation_review/__init__.py` | Added | Export the Phase 1 contract and canonical APIs. |
| `src/forgeflow/validation_review/models.py` | Added | Define immutable M3 envelopes and value objects. |
| `src/forgeflow/validation_review/profile.py` | Added | Pin the M3 fixture profile, bounds, controlled values, and forbidden fields. |
| `src/forgeflow/validation_review/canonical.py` | Added | Canonically serialize contract values and derive self-excluding identities. |
| `tests/validation_review/__init__.py` | Added | Establish the M3 test package. |
| `tests/validation_review/test_contracts.py` | Added | Verify envelope fields, immutability, exclusions, and terminal-policy compatibility. |
| `tests/validation_review/test_canonical.py` | Added | Verify deterministic canonical bytes and independent identities. |
| `openspec/changes/validation-review-slice/fixtures/expected/phase-1-contract/validation-result.json` | Added | Lock a completed-attempt envelope with a computed ID. |
| `openspec/changes/validation-review-slice/fixtures/expected/phase-1-contract/validation-terminal.json` | Added | Lock a policy-blocked terminal with no attempt fact. |
| `openspec/changes/validation-review-slice/fixtures/expected/phase-1-contract/review-result.json` | Added | Lock a review envelope with a policy reference but no governance outcome field. |
| `openspec/changes/validation-review-slice/fixtures/expected/phase-1-contract/validation-review-error.json` | Added | Lock a separate safe validation-error envelope. |

## 4. Implementation

The new package provides frozen, slotted dataclasses that reject malformed hash
identifiers, unsupported controlled values, non-canonical ordering, incompatible
terminal-policy lineage, unbounded collections, and invalid envelope literals.
`ValidationResult` models only a completed fixture attempt. `ValidationTerminal`
has no attempt ID, fixture case, outcome, command, exit code, or output field.
`ReviewResult` holds findings and Policy Decision Record references without a
governance outcome or approval field.

Canonical serialization uses compact, lexicographically sorted UTF-8 JSON and
rejects floats and unsupported values. Each envelope identity excludes only its
own identity field. The expected fixtures contain deterministic IDs and
references only; they contain no raw payloads.

## 5. Design Decisions

- Completed attempt facts, governance terminals, review observations, and
  policy decisions are independent immutable contracts.
- A terminal requires a matching `blocked` or `requires_human_approval` policy
  reference and cannot claim execution facts.
- Review references a completed validation-result identity and cannot contain
  authorization, retry, or PR-readiness fields.
- This phase establishes data-only contracts; all I/O and service assembly are
  deferred to later canonical phases and remain fixture-only.

## 6. TDD and Tests

- RED: `uv run --no-sync python -m unittest tests.validation_review.test_contracts tests.validation_review.test_canonical -v` failed with `ModuleNotFoundError: No module named 'forgeflow.validation_review'` before implementation.
- GREEN: the same targeted command passed 7/7 after adding the minimal contract
  package, profile, canonical helpers, and expected fixtures.
- Cumulative verification: `uv run --no-sync python -m unittest discover -s tests -v` passed 105/105.
- Static boundary verification found no `subprocess`, network, or filesystem
  execution imports in `src/forgeflow/validation_review`.
- Specification and diff verification: `openspec validate validation-review-slice --strict` and `git diff --check` passed.

## 7. Important Fixes and Edge Cases

- Validation-error fields are separate from terminal, result, and review fields
  so malformed inputs cannot produce partial success.
- Policy decision records are independently identified and bound to their
  subject contract, preventing a result or terminal from reusing a mismatched
  policy record.
- Canonical serialization preserves ordered tuples and rejects floats rather
  than silently coercing identity inputs.

## 8. Commit

- Full commit hash: `d7b84f66d60205ac0346fb0058827b39f437cc8b`
- Commit message: `feat(validation-review): add contract foundation`

## 9. Acceptance

The targeted tests verified immutable/slotted models, envelope separation,
controlled values, terminal-policy compatibility, forbidden execution fields,
and deterministic identities. The full suite passed 105 tests. Expected
fixtures use computed canonical IDs, not placeholders.

Status: **Accepted**.

## 10. Scope Boundary Confirmation

This phase added no policy evaluator, fake executor, service, command runner,
sandbox, workspace access, network, dependency installation, retry, provider,
runtime, Git, or PR integration.

## 11. Follow-up

Next Phase: Deterministic Policy and Attempt Fixtures. It requires explicit
user authorization before starting.
