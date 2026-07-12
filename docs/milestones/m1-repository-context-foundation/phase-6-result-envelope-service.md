# Phase 6: Result Envelope and Service

## 1. Goal

Assemble deterministic Repository Context success and validation envelopes and
expose the public read-only service entry point.

## 2. Scope

### Included

- Deterministic validation errors for unsupported configuration profiles, empty
  queries, oversized queries, and invalid workspace inputs.
- Root-only descriptive `npm test` and `make test` hints with evidence refs.
- Candidate/returned counts, result caps, grouped result truncation, limitations,
  run summary, completion status, final contract ID, and no-dangling-reference
  assembly.
- Public `inspect_repository()` orchestration over existing boundary, scanner,
  matcher, evidence, and identity components.

### Excluded

- Phase 7 complete acceptance coverage and Phase 8 hardening.
- Unreadable-file and line-limit scanner behavior.
- Command execution, validation execution, production storage, policy decisions,
  agents, workflows, DeerFlow integration, LLMs, embeddings, AST processing,
  semantic search, network, Git/PR, and memory.

## 3. Changed Files

| File | Change | Purpose |
| --- | --- | --- |
| `src/forgeflow/repository_context/__init__.py` | Modified | Export the public service entry point. |
| `src/forgeflow/repository_context/validation.py` | Added | Construct deterministic validation-error envelopes. |
| `src/forgeflow/repository_context/hints.py` | Added | Discover strict root-only descriptive test hints and their evidence. |
| `src/forgeflow/repository_context/assembly.py` | Added | Apply caps, counts, limitations, run summary, and final contract identity. |
| `src/forgeflow/repository_context/service.py` | Added | Orchestrate validation, scanning, matching, hints, and result assembly. |
| `tests/repository_context/test_service.py` | Added | Verify validation, stable service results, hints, and cap invariants. |

## 4. Implementation

`inspect_repository()` validates the trusted workspace, configuration profile,
and normalized query before scanning. Invalid input returns a separate
`RepositoryContextValidationError` with a stable `error_id` and no successful
result fields.

For valid input, the service normalizes bounded issue text, scans through the
existing workspace boundary, matches direct evidence, discovers root-only hints,
and calls `assemble_result()`. Assembly applies deterministic caps, retains only
referenced evidence, derives counts and ordered limitations, chooses completion
status, and assigns `contract_id` last.

`hints.py` reads only root `package.json` and `Makefile` through direct file APIs.
It emits canonical descriptive commands, never executes them, and records
malformed metadata as a non-fatal limitation.

## 5. Design Decisions

- Validation envelopes are built separately from successful results, preventing
  partial success payloads from leaking into invalid-input responses.
- Result caps are applied before final evidence retention so every returned
  reference resolves and the contract can report grouped truncation.
- Hint discovery is intentionally strict and root-only; raw script and recipe
  content never appears in the contract.
- Contract identity is calculated after all deterministic result fields,
  limitations, and counts are finalized.

## 6. TDD and Tests

The service and assembly test module was added before production modules. The
initial RED run failed because `forgeflow.repository_context.assembly` did not
exist. GREEN added the minimum Phase 6 modules and public export.

Test framework: Python `unittest`.

| Verification | Result |
| --- | --- |
| RED: `python3 -m unittest tests.repository_context.test_service -v` | Expected missing-module failure for `forgeflow.repository_context.assembly`. |
| Targeted GREEN: same command | 4 tests passed. |
| Cumulative Phase 1-6 suite: `python3 -m unittest tests.repository_context.test_contracts tests.repository_context.test_canonical tests.repository_context.test_workspace tests.repository_context.test_scanner tests.repository_context.test_matching tests.repository_context.test_service -v` | 49 tests passed. |

## 7. Important Fixes and Edge Cases

- Whitespace-only queries produce the same stable `empty_query` validation ID.
- Unsupported profiles produce `invalid_config_profile` without scanning.
- Root-only hints are sorted and remain descriptive; `make test` and `npm test`
  are never executed.
- Result caps retain only evidence referenced by retained files, search results,
  or hints and add one grouped `result_set_truncated` limitation.

## 8. Commit

- Full implementation commit hash: `d43e2e56cf3feac17209d8c4e5c9b82049c2986f`
- Commit message: `feat(context): add deterministic result service`

## 9. Acceptance

Targeted tests verify the distinct validation envelope, deterministic repeated
success results, root-only hint behavior, candidate/returned counts, result
truncation, and reference integrity. The cumulative Phase 1-6 suite passed with
49 tests.

Status: **Accepted**.

## 10. Scope Boundary Confirmation

This phase did not execute test hints, add production persistence or lookup APIs,
implement Phase 7 comprehensive acceptance evaluation, or address Phase 8
hardening gaps. It introduced no command runner, network, agent, workflow,
DeerFlow runtime, LLM, embedding, AST, semantic-search, Git/PR, or memory
behavior.

## 11. Follow-up

Next Phase: Acceptance Tests.

No Phase 6 reconciliation item remains.
