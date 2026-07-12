# Phase 1: Contract Foundation

## 1. Goal

Establish the immutable, versioned Repository Context contract foundation required before filesystem or retrieval behavior is introduced.

## 2. Scope

### Included

- Repository Context request, success, validation-error, summary, evidence, result, limitation, and supporting data contracts.
- Tagged result and validation-error envelope types.
- The immutable `repository-context/m1-defaults-v1` profile.
- Public package exports and the initial unittest configuration.

### Excluded

- Canonical serialization and stable identifiers.
- Input validation behavior, workspace access, scanning, matching, ranking, evidence construction, result assembly, and service behavior.
- Agents, workflows, orchestration, DeerFlow runtime integration, LLMs, embeddings, AST processing, network, subprocesses, Git/PR, and memory.

## 3. Changed Files

| File | Change | Purpose |
| --- | --- | --- |
| `.gitignore` | Modified | Ignore generated Python and test-cache artifacts. |
| `pyproject.toml` | Added | Define the Python package and unittest-compatible project metadata. |
| `src/forgeflow/__init__.py` | Added | Establish the ForgeFlow package. |
| `src/forgeflow/repository_context/__init__.py` | Added | Provide the initial Repository Context public exports. |
| `src/forgeflow/repository_context/models.py` | Added | Define immutable Repository Context contract models and envelope union. |
| `src/forgeflow/repository_context/profile.py` | Added | Define the immutable M1 defaults profile. |
| `tests/__init__.py` | Added | Enable the documented unittest module invocation. |
| `tests/repository_context/__init__.py` | Added | Establish the Repository Context test package. |
| `tests/repository_context/test_contracts.py` | Added | Verify contract shape, literal values, immutability, and exclusions. |

## 4. Implementation

`models.py` adds frozen, slotted dataclasses for the request, workspace reference, normalized and bounded inputs, evidence and locators, result candidates, limits, run summaries, and both terminal envelopes. `RepositoryContextResult` pins the `repository_context_result` type and `repository-context-result/v1` schema; `RepositoryContextValidationError` pins its validation type, schema, and `validation_error` completion state. Collection-valued contract fields use tuples with explicit empty defaults.

`profile.py` exposes `RepositoryContextProfile` and `M1_DEFAULTS`, including the fixed configuration profile identifier and M1 limits. The package exports make the contracts available without adding runtime behavior.

## 5. Design Decisions

- Contracts are immutable and slotted so the foundation has stable, narrow data shapes without mutable runtime state.
- Success and validation outcomes are separate tagged types, allowing callers to distinguish terminal shapes without introducing service logic.
- Contract literals and M1 defaults are pinned in the model layer rather than inferred from environment or runtime configuration.
- Supporting nested types remain data-only; they do not perform validation, serialization, or retrieval.

## 6. TDD and Tests

The RED test run failed because the `forgeflow` contract module did not yet exist. GREEN added only the package, immutable models, profile, and exports. A corrective TDD iteration added the structured truncation limitation detail and tightened the profile literal after the contract tests exposed the missing API.

Test framework: Python `unittest`.

| Verification | Result |
| --- | --- |
| RED: `python3 -m unittest tests.repository_context.test_contracts -v` | Expected import failure for the missing contract package/API. |
| Targeted GREEN: same command | 8 tests passed. |
| Cumulative suite at Phase completion | 8 tests passed. |

## 7. Important Fixes and Edge Cases

- `Limitation.detail` supports either a string or an immutable `ResultSetTruncatedDetail`, preserving structured truncation information.
- Required collections are tuples with explicit empty defaults.
- `InputSummary.configuration_profile_id` is limited to the M1 profile literal; runtime and future-stage fields are intentionally absent.

## 8. Commit

- Full commit hash: `fd9813f1a62eead8d87a88de2f6592590783ab75`
- Commit message: `feat(contract): add repository context contracts`

## 9. Acceptance

The contract tests verified immutable models, pinned tags and schema versions, tuple collections, profile values, and the absence of runtime or future-phase fields. The final checkpoint accepted the contract-first design as aligned with the Repository Context OpenSpec and RFC-002 state-model direction.

Status: **Accepted**.

## 10. Scope Boundary Confirmation

This phase did not implement canonical JSON, IDs, validation execution, workspace boundaries, scanner behavior, matchers, ranking, evidence generation, result assembly, or a Repository Context Service. It introduced no external runtime, agent, workflow, DeerFlow, LLM, embedding, AST, network, subprocess, Git/PR, or memory capability.

## 11. Follow-up

Next Phase: Canonical Identity.

Reconciliation status: phase numbering was aligned with the canonical plan on
2026-07-12; no Phase 1 follow-up remains.
