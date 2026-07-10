## Context

Milestone 1 is the Repository Context Foundation Slice. RFC-001 is accepted as the current agent architecture baseline and scope guard. RFC-002, RFC-004, and RFC-007 remain draft documents with Grill-Me feedback incorporated; this OpenSpec treats them as boundary inputs for Milestone 1 rather than as permission to implement broader workflow capabilities.

The Repository Context Service is a ForgeFlow-owned deterministic service. It gathers repository facts from a workspace root, query, and optional issue text. It must not act as a Planner, Software Engineer, Validation, Review, or PR role, and it must not introduce LLM judgment into retrieval or ranking.

## Goals / Non-Goals

**Goals:**

- Define the minimum deterministic Repository Context Service behavior for Milestone 1.
- Define the `RepositoryContextResult` contract fields and evidence boundaries.
- Define deterministic empty-result, invalid-input, ordering, deduplication, and skipped-file behavior before implementation begins.
- Confine all repository inspection to read-only, workspace-root-contained operations.
- Make retrieval ranking reproducible through deterministic signals.
- Provide controlled fixtures that can verify behavior without broad production implementation.

**Non-Goals:**

- No patch generation, code editing, diff creation, validation execution, repair loop, review automation, branch creation, commit creation, or PR creation.
- No concrete Planner, Software Engineer, Validation, Review, or PR agent implementation units.
- No long-term memory reads or writes.
- No LLM reasoning for relevance judgment, summarization, root-cause inference, repair strategy, semantic ranking, or test recommendation.
- No full DeerFlow graph/runtime integration, DeerFlow core modification, local DeerFlow patch, or dependency on unmerged DeerFlow changes.
- No production policy engine or full trace/run summary system beyond minimal Milestone 1 alignment.

## Decisions

### Decision 1: Implement Repository Context as a deterministic service

The service will rank and return context using reproducible repository signals such as file path matches, filename matches, text search matches, cheap language-agnostic symbol hints, project configuration, and test naming conventions.

Alternatives considered:

- LLM relevance ranking: rejected for Milestone 1 because it violates RFC-001 and RFC-002 determinism boundaries.
- Full semantic code indexing: deferred because Milestone 1 should avoid broad implementation and language-specific analyzer complexity.

### Decision 2: Use `RepositoryContextResult` as the only required Milestone 1 contract

The Milestone 1 contract will include schema/run identity, workspace and query references, relevant files, search results, optional symbol hints, test command hints, evidence references, deterministic ranking metadata, and limitations.

The deterministic repository-context payload should be distinguishable from runtime metadata. Runtime-generated values such as a run identifier may exist for traceability, but they must not affect deterministic payload comparison.

Alternatives considered:

- Include `PatchProposal`, `ValidationResult`, `ReviewResult`, or `PRResult`: rejected because those are future milestone directions only.
- Persist raw snippets in the contract by default: rejected because evidence references must remain separate from evidence payloads.

### Decision 3: Keep repository access read-only and workspace-confined

All file inspection must resolve under the declared workspace root, reject parent-directory escape, reject symlink escape, avoid repository writes, avoid dependency installation, avoid arbitrary command execution, and avoid default network access.

Returned paths should be normalized workspace-relative paths. Host-specific absolute paths should remain outside `RepositoryContextResult` so durable records do not expose unsafe local filesystem details.

Alternatives considered:

- Reuse a later write/test sandbox shape immediately: rejected because Milestone 1 does not need write or command execution infrastructure.
- Treat read-only tools as automatically safe: rejected because read-only access can still expose sensitive data and must be policy-aware.

### Decision 4: Treat DeerFlow as optional reference material for Milestone 1

The Milestone 1 Repository Context path should be ForgeFlow-owned and must not require DeerFlow core modification. The recorded DeerFlow revision may remain an immutable upstream reference.

Alternatives considered:

- Implement the capability inside DeerFlow core: rejected because it blurs the ForgeFlow product layer and upstream runtime boundary.
- Require full DeerFlow runtime graph integration now: deferred because Repository Context acceptance can be proven without it.

### Decision 5: Defer symbol hints from Milestone 1 acceptance

Cheap language-agnostic symbol hints are allowed only as optional output when deterministic extraction is already available. They are not required for Milestone 1 acceptance.

Alternatives considered:

- Require symbol hints in the first implementation slice: rejected because it could pull the milestone toward language-specific parsing or analyzer dependencies.
- Forbid symbol hints entirely: rejected because ADR-002 allows optional cheap language-agnostic hints when they remain deterministic.

### Decision 6: Use structural deterministic comparison

Repeated repository-context runs must produce structurally equivalent deterministic payloads after excluding explicitly marked runtime metadata. Canonical serialization may be used by tests, but wall-clock timestamps, random values, process IDs, nondeterministic traversal order, and host absolute paths must not affect the deterministic payload.

Alternatives considered:

- Require byte-equivalent whole-result serialization: rejected because minimal run metadata may include runtime identifiers.
- Allow vague equivalence: rejected because evaluation fixtures need objectively testable comparison rules.

### Decision 7: Keep trace alignment minimal and non-payload

Milestone 1 trace/run-summary alignment is limited to non-payload operational facts that can be derived from or associated with `RepositoryContextResult`, such as operation type, deterministic input summary, scanned/matched/skipped/limited counts, limitation codes, and completion status.

Alternatives considered:

- Define a production tracing system now: rejected because RFC-005-level observability is outside Milestone 1.
- Persist raw snippets or full tool payloads for debugging: rejected because RFC-002 and RFC-004 require bounded references and redaction boundaries.

## Risks / Trade-offs

- Deterministic retrieval may miss semantically relevant files that an LLM or language server might find. Mitigation: expose `limitations` and controlled retrieval metadata, then add richer analyzers in later accepted specs.
- Evidence references without source payloads may require a second lookup for human inspection. Mitigation: include stable paths, line ranges, hashes, and retrieval metadata.
- Test command hints may be mistaken for authorization to execute tests. Mitigation: specify hints as non-executable context only; test execution is out of scope.
- Strict deterministic ordering may require extra normalization logic across platforms. Mitigation: define workspace-relative path ordering and require same-workspace same-platform determinism without mandating a portable case-sensitivity model.
- RFC-002, RFC-004, and RFC-007 are still Draft while RFC-001 is Accepted. Mitigation: this OpenSpec uses their current draft decisions only as Milestone 1 constraints and does not rely on broader acceptance.

## Migration Plan

This is the first OpenSpec change in the repository, so there is no existing OpenSpec capability to migrate.

Implementation should proceed only after this change is reviewed and accepted. The first implementation slice should add fixtures and a minimal read-only Repository Context path, then validate it against the scenarios in this spec.

## Open Questions

- Should the project later add DeerFlow as a Git submodule under `third_party/deer-flow`, or keep the current immutable revision record as sufficient for Milestone 1?
- What exact fixture repositories should be used for the first deterministic retrieval evaluation set?
- Should optional symbol hints be implemented in the first code slice or recorded as a Milestone 1 stretch item if cheap language-agnostic extraction is insufficient?
