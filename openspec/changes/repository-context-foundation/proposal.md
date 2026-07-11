# Change: Repository Context Foundation

## Why

ForgeFlow Milestone 1 needs a deterministic repository-context contract before any role agents, workflow runtime, editing, validation, review, PR, memory, or DeerFlow integration work begins. Later stages need a bounded way to reference repository evidence, but Milestone 1 must not grant authority, execute tools, mutate repositories, or persist production artifacts.

This change defines the Repository Context Foundation Slice as a contract-first capability. It makes repository context precise enough for fixture-driven implementation while preserving the narrow Milestone 1 boundary.

## What Changes

- Add the `repository-context` specification for a deterministic Repository Context Service.
- Define a tagged successful `RepositoryContextResult` envelope and a separate tagged validation error envelope.
- Define canonical deterministic identity rules for `contract_id`, `evidence_ref.id`, and validation `error_id`.
- Require caller-supplied logical workspace identity and explicit configuration profile identity covering normalization, matching, ranking weights, caps, ignore policy, limits, decoding, and test-hint behavior.
- Define exact input normalization, query-only retrieval, bounded issue-text context, line-based substring text matching, and strict UTF-8 decoding.
- Define canonical workspace-relative path formatting, path escape prevention, symlink traversal-control behavior, and direct filesystem-only inspection.
- Define the default ignore policy for `repository-context/m1-defaults-v1`.
- Define fixed ranking inputs, score formula, tie-breaking, and deterministic match reasons.
- Define evidence references, text-only search results, inspected-text content hashes, and root-only descriptive test command hints.
- Define scan limits, result limits, truncation behavior, limitation shape and ordering, candidate versus returned counts, and run-summary semantics.
- Define immutable, non-authorizing, bounded-payload contract behavior.
- Require controlled fixtures and acceptance-test skeletons before read-only retrieval implementation begins.

## Scope

This change includes only the Milestone 1 Repository Context Foundation Slice:

- deterministic Repository Context Service contract
- read-only repository access through workspace-confined filesystem APIs or libraries
- workspace input with caller-supplied logical `workspace_ref.root_id`
- query input as the sole retrieval and ranking driver
- optional issue text as bounded context only
- deterministic file discovery and text search
- canonical path normalization and path escape prevention
- symlink detection for traversal safety only
- deterministic ranking metadata
- evidence references and inspected-text verification hashes
- relevant files
- text-match search results
- simple descriptive test command hints
- `RepositoryContextResult`
- separate validation error envelope
- minimal run-summary alignment inside the contract
- controlled evaluation fixtures and expected outputs
- side-effect absence acceptance checks

## Explicit Exclusions

This change does not introduce:

- PlannerAgent
- SoftwareEngineerAgent
- ValidationAgent
- ReviewAgent
- PRAgent
- workflow graph implementation
- orchestration runtime
- DeerFlow core modification
- full DeerFlow runtime integration
- patch generation
- autonomous code editing
- test execution
- validation loop
- validation planning
- review automation
- PR creation
- branch creation
- commit creation
- production artifact persistence
- contract lookup APIs
- memory reads
- memory writes
- command execution, including read-only commands such as `git`, `rg`, `grep`, or `find`
- dependency installation
- default network access
- LLM reasoning inside Repository Context Service
- semantic ranking
- embeddings
- root-cause analysis
- code summarization
- AST or language-server analysis
- symbol hints
- production secret scanning

## Contract Boundary

`RepositoryContextResult` is context and evidence only. It is not a policy decision and does not authorize later file reads, commands, tests, edits, patches, memory operations, network access, branches, commits, PRs, or external side effects. Later workflow stages may reference `contract_id` and `evidence_ref.id` values, but they must produce separate contracts or artifacts and perform their own OpenSpec-authorized policy checks.

Successful results are immutable after creation. Validation errors are separate envelopes and must not contain partial successful-result fields. Stable IDs support deterministic fixtures, regression tests, caller-owned references, and future linking, but Milestone 1 does not define production storage or lookup infrastructure.

## Impact

- Implementers will have a precise contract for Repository Context Service behavior before writing retrieval code.
- Acceptance fixtures will pin normalization, matching, scoring, evidence, limits, validation errors, side-effect boundaries, and canonical IDs.
- Later ForgeFlow stages can depend on repository context as bounded non-authorizing input without inheriting execution, persistence, memory, or policy semantics.
- Future changes that add symbol hints, semantic analysis, command-backed search, VCS ignore behavior, production persistence, secret scanning, validation planning, or DeerFlow runtime integration must be proposed through separate OpenSpec changes.
