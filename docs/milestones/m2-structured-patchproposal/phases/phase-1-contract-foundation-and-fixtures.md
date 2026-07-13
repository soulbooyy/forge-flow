# Phase 1: Contract Foundation and Fixtures

## 1. Goal

Establish the immutable, provider-neutral `PatchProposal` contract foundation,
the fixed M2 conservative profile, canonical identity helpers, and payload-free
expected fixtures before policy evaluation or proposal-source behavior exists.

## 2. Scope

### Included

- Frozen, slotted success and validation-envelope contract models and public
  exports.
- The immutable `patch-proposal/m2-conservative-v1` profile and source identity.
- Canonical JSON plus proposal, validation-error, candidate-digest, and policy
  decision identity helpers.
- Contract/canonical tests and two expected envelope fixtures with real IDs.

### Excluded

- Policy evaluation, sensitive-path matching, approval decisions, or blocked
  outcome assembly.
- Fixture source lookup, `RepositoryContextResult` evidence validation, and
  proposal service behavior.
- Workspace access, provider/MCP/DeerFlow integration, diff generation,
  commands, network access, mutation, Git/PR behavior, and memory.

## 3. Changed Files

| File | Change | Purpose |
| --- | --- | --- |
| `src/forgeflow/patch_proposal/__init__.py` | Added | Export the Phase 1 public contract and canonical APIs. |
| `src/forgeflow/patch_proposal/models.py` | Added | Define immutable success/error envelopes and supporting value objects. |
| `src/forgeflow/patch_proposal/profile.py` | Added | Define the fixed conservative M2 profile. |
| `src/forgeflow/patch_proposal/canonical.py` | Added | Serialize contract values and derive stable identities. |
| `tests/patch_proposal/__init__.py` | Added | Establish the M2 contract test package. |
| `tests/patch_proposal/test_contracts.py` | Added | Verify contract shape, literals, immutability, profile, and exclusions. |
| `tests/patch_proposal/test_canonical.py` | Added | Verify canonical bytes, identity self-exclusion, and fixture equality. |
| `openspec/changes/structured-patch-proposal/fixtures/expected/phase-1-contract/success-envelope.json` | Added | Lock a complete payload-free success envelope with computed IDs. |
| `openspec/changes/structured-patch-proposal/fixtures/expected/phase-1-contract/validation-error.json` | Added | Lock a separate payload-free validation envelope with a computed ID. |

## 4. Implementation

The new package provides frozen, slotted dataclasses for bounded task input,
root-cause hypotheses, fix strategy, candidate changes, policy-decision
references, successful proposals, and validation errors. Constructors reject
invalid controlled values, bounds, identity formats, non-canonical paths, and
non-deterministic collection ordering. The profile pins the M2 source,
evaluator, limits, controlled values, constraint codes, and versioned path-rule
data; it does not yet evaluate paths.

Canonical serialization uses compact, sorted UTF-8 JSON and rejects floats or
unsupported values. Proposal and validation-error IDs omit only their own
identity field. Candidate digest derives from ordered `(path, change_kind,
rationale)` tuples; policy-decision identity omits only `decision_id`.

## 5. Design Decisions

- The contract layer is data-only and performs no policy, source, workspace,
  provider, or service work; those responsibilities remain in later phases.
- Success and validation outcomes are separate tagged types, preventing a
  partial successful proposal from appearing in an error envelope.
- Canonical helpers are local to `patch_proposal` but preserve M1's deterministic
  JSON semantics without importing runtime behavior.
- Expected fixtures contain references and hashes only; they contain no source,
  diff, prompt, provider payload, command, or environment value.

## 6. TDD and Tests

- RED: `uv run --no-sync python -m unittest tests.patch_proposal.test_contracts tests.patch_proposal.test_canonical -v` failed with `ModuleNotFoundError: No module named 'forgeflow.patch_proposal'` before implementation.
- GREEN: the same targeted command passed 8/8 after adding the minimal package,
  models, profile, canonical helpers, and computed expected fixtures.
- Refactor/correction: the fixture-lock test initially exposed absent expected
  JSON files; generated and checked in the real deterministic envelopes, with
  no production-scope expansion.
- Review correction: added RED tests for invalid contract construction and
  missing profile rule data, then added constructor-level validation and
  immutable rule declarations. The targeted suite passed 11/11.
- Cumulative verification: `uv run --no-sync python -m unittest discover -s tests -v` passed 74/74; `openspec validate structured-patch-proposal --strict` and `git diff --check` passed.

## 7. Important Fixes and Edge Cases

- Canonical serialization rejects floats and unknown object values rather than
  silently coercing identity inputs.
- Candidate digest changes when a candidate rationale changes, preventing stale
  policy-decision identity reuse.
- The M2 profile now retains the accepted blocked and approval-required path
  categories as immutable data, so Phase 2 can evaluate a versioned profile
  without embedding policy rules in evaluator code.
- Contract tests explicitly reject raw payload, runtime, execution, and
  provider-related field names.

## 8. Commit

- Full commit hash: `968da294177e386b0bcbf0442a6bc03ccdcd2f19`
- Commit message: `feat(patch-proposal): add contract foundation`

## 9. Acceptance

The targeted contract/canonical suite verified frozen/slotted models, schema
and result literals, constructor-level contract rejection, separate error
fields, fixed profile values and path-rule data, deterministic identities, and
exact expected fixtures. The cumulative suite passed 74 tests. The two fixture
IDs are computed from canonical payloads, not placeholders.

Status: **Accepted**.

## 10. Scope Boundary Confirmation

This phase added no policy evaluator, fixture source, proposal service,
workspace read, provider/MCP/DeerFlow integration, diff, command, network,
mutation, Git/PR, memory, or Phase 2+ abstraction.

## 11. Follow-up

Next Phase: Patch-Boundary Assessment Adapter. It requires explicit user
authorization before starting.
