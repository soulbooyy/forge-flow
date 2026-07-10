## Why

ForgeFlow is ready to move from RFC boundary hardening into Milestone 1, but implementation must begin from a narrow, reviewable OpenSpec so the Repository Context Foundation Slice does not drift into the full autonomous repair workflow.

This change defines the first product capability: deterministic, read-only repository context retrieval that produces `RepositoryContextResult` without LLM relevance reasoning, patch generation, test execution, memory access, or PR side effects.

## What Changes

- Introduce the `repository-context` capability for Milestone 1.
- Define the required behavior of a deterministic Repository Context Service.
- Define the Milestone 1 `RepositoryContextResult` contract surface.
- Define deterministic empty-result, invalid-input, ordering, tie-breaking, deduplication, and skipped-file behavior.
- Require deterministic ranking metadata: `match_score`, `match_reasons`, `ranking_inputs`, `evidence_refs`, and `limitations`.
- Require evidence references to identify source locations and verification metadata without embedding raw source payloads by default.
- Require read-only, workspace-confined repository access.
- Require minimal non-payload trace/run-summary metadata aligned with the contract.
- Require controlled evaluation fixtures for repository context behavior.
- Explicitly exclude patch generation, code editing, test execution, validation repair loops, review automation, PR creation, long-term memory reads/writes, and full DeerFlow runtime integration.

## Capabilities

### New Capabilities

- `repository-context`: Deterministic, read-only retrieval of repository context for a query or optional issue text, producing `RepositoryContextResult` with evidence references and bounded retrieval metadata.

### Modified Capabilities

None.

## Impact

- Affected documentation: `openspec/changes/repository-context-foundation/`, RFC alignment with `rfcs/RFC-001-agent-architecture.md`, `rfcs/RFC-002-contracts-and-state-model.md`, `rfcs/RFC-004-sandbox-and-security-governance.md`, and `rfcs/RFC-007-deerflow-extension-strategy.md`.
- Affected future implementation: a ForgeFlow-owned read-only Repository Context Service, contract model for `RepositoryContextResult`, retrieval fixtures, deterministic ordering rules, workspace confinement rules, and minimal product-level trace or run summary alignment.
- Dependencies: no new runtime dependency is required by this OpenSpec. DeerFlow remains an immutable upstream reference for Milestone 1 and must not be modified or required for acceptance unless a later OpenSpec explicitly narrows that integration.
