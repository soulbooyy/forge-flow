## Context

Milestone 1 needs a narrow Repository Context Foundation Slice that can supply deterministic repository context to later ForgeFlow stages without implementing those stages. The slice must be contract-first: callers receive bounded context and evidence references, not permissions, execution plans, mutable workflow state, or runtime tracing records.

This change defines the contract behavior for a deterministic Repository Context Service only. It intentionally avoids PlannerAgent, SoftwareEngineerAgent, ValidationAgent, ReviewAgent, PRAgent, workflow graph implementation, orchestration runtime, patch generation, autonomous code editing, validation execution, review automation, PR creation, branch creation, commit creation, memory reads or writes, LLM reasoning, semantic ranking, root-cause analysis, code summarization, production persistence, and DeerFlow core modification.

## Goals

- Define a precise `RepositoryContextResult` contract that can be implemented and fixture-tested.
- Define a separate validation error envelope for invalid required inputs and unsafe workspace conditions.
- Make result identity, evidence identity, ordering, normalization, matching, ranking, truncation, and counts deterministic across implementations.
- Preserve a strict read-only, no-command, no-network, no-memory workspace boundary.
- Keep test command hints descriptive and non-executable.
- Pin acceptance fixtures and expected contract fragments before implementation begins.

## Non-Goals

- No role-agent implementation.
- No workflow graph, DeerFlow runtime integration, or DeerFlow core modification.
- No command governance or sandbox-command layer.
- No patch generation, code editing, branch, commit, or PR side effects.
- No test execution, validation loop, or validation planning.
- No production tracing system, artifact store, contract lookup API, retention model, or access-control model.
- No memory reads or writes.
- No LLM, embedding, semantic, AST, or language-server reasoning inside repository context.
- No symbol hints in Milestone 1.
- No production secret scanning.

## Decisions

### 1. Use explicit success and validation envelopes

The service returns a tagged union. Successful inspection returns `result_type: "repository_context_result"` and a full immutable `RepositoryContextResult`. Validation failure returns `result_type: "repository_context_validation_error"` and never returns partial successful-result fields.

This keeps invalid-input behavior separate from incomplete-coverage behavior. Missing workspace identity, empty or oversized query, invalid configuration profile, inaccessible workspace, unsafe path escape, or unsupported workspace conditions are validation errors. Empty repositories, no matches, skipped files, truncated scans, malformed optional test-hint metadata, unreadable files, unsupported encodings, and result caps are limitations inside an otherwise successful result.

### 2. Derive identities from canonical deterministic payloads

`contract_id`, `evidence_ref.id`, and validation `error_id` are hash-derived from canonical JSON payloads with the identity field itself omitted. Canonical JSON uses UTF-8, lexicographic object-key ordering, deterministic array ordering, no insignificant whitespace, integer numbers for scores/counts/limits/lines, explicit empty required collections, omitted absent optionals, and no floats.

The successful contract hash includes semantic contract content, not implementation behavior. Runtime-only and environment-specific values are excluded. The resulting IDs are useful for fixture comparison, regression tests, caller-owned references, and future contracts, but they do not imply production persistence in Milestone 1.

### 3. Require caller-supplied logical workspace and configuration identity

The service input requires a safe caller-supplied `workspace_ref.root_id` and `configuration_profile_id`. Milestone 1 allows only `repository-context/m1-defaults-v1`. The service does not derive workspace identity from host paths, repository contents, filesystem metadata, timestamps, or machine state.

The configuration profile is the contract behavior version. It covers normalization, matching, ranking weights, score caps, scan limits, result limits, ignore policy, decoding, test hint discovery, side-effect boundaries, and deferred capabilities. Defaults must not silently change under the same profile identity; any future contract-affecting default change should introduce a new explicit profile such as `repository-context/m1-defaults-v2` through a later OpenSpec change.

### 4. Make normalization and matching cheap, exact, and language-agnostic

The query is normalized by NFC normalization, trimming, whitespace collapse, and casefolded matching views. `query.normalized` is the sole retrieval and ranking driver. Optional issue text is normalized and bounded as input context only; it does not drive retrieval, ranking, search results, evidence, or no-match behavior.

Milestone 1 text matching is line-based substring matching over normalized line views after strict UTF-8 decoding, UTF-8 BOM removal, CRLF/CR to LF normalization, and query normalization. Matches do not cross line boundaries. Duplicate occurrences on the same line collapse to one locator.

### 5. Restrict inspection to direct read-only filesystem APIs

Milestone 1 uses direct workspace-confined filesystem APIs or libraries for traversal, metadata reads, bounded text reads, decoding, hashing, ignore-policy application, path normalization, and symlink boundary enforcement. It forbids all command execution, including commands commonly considered read-only (`git`, `rg`, `grep`, `find`, package managers, test commands, and language servers).

This avoids accidentally implementing a command-governance slice and keeps RFC-004-style policy decisions outside repository context. The result is context and evidence only; it authorizes no later actions.

### 6. Keep path identity canonical and workspace-relative

Returned paths are canonical workspace-relative paths using `/`, preserving observed casing and excluding leading slash, `.` segments, `..` segments, empty segments, duplicate separators, and host absolute paths. Lexical ordering uses this returned representation.

Canonical workspace-relative path is the only file identity. The service does not deduplicate by inode, hard link, or content hash. Symlinks are traversal-control artifacts only in Milestone 1; they are not relevant files and do not expose target content.

### 7. Use a fixed narrow ignore policy

The default profile ignores only `.git/`, `.forgeflow/cache/`, `.forgeflow/artifacts/`, and `openspec/changes/*/fixtures/output/`. It does not honor `.gitignore`, `.ignore`, global Git excludes, ecosystem defaults, hidden-directory defaults, dependency-directory defaults, or build-output defaults.

Ignored directories are counted once and not descended into. This keeps discovery deterministic and prevents generated fixture outputs or ForgeFlow artifacts from polluting context while avoiding broad hidden implementation defaults.

### 8. Use direct scoring signals only

`ranking_inputs` is the single scoring source and contains only `filename_match`, `path_match`, and capped `text_match_count`. The default score is filename match `100`, path match `50`, and `25` per counted text locator up to the per-file cap. Sorting uses score descending and canonical path ascending.

`match_reasons` is a deterministic projection of ranking inputs. There is no `config_match`, `test_convention_match`, `symbol_hint`, issue-text signal, semantic signal, inferred framework signal, LLM signal, AST signal, or language-server signal.

### 9. Keep evidence references separate from payloads

Evidence references identify where deterministic evidence came from and may include verification metadata such as SHA-256 content hashes for inspected text. They do not persist raw snippets, full file contents, host absolute paths, command output, stack traces, or runtime metadata.

Search results are text-match locators only. Filename/path matches are represented through relevant-file ranking inputs, match reasons, and evidence references. Test command hints are separate descriptive metadata.

### 10. Keep test command hints root-only and non-executable

Milestone 1 test hints inspect only root `package.json` and root `Makefile`. A strict top-level `scripts.test` string in root `package.json` emits `npm test`. A non-recipe target line in root `Makefile` whose target list includes exactly `test` emits `make test`.

Hints are deduplicated, sorted, evidenced, included in the successful contract, and never executed. They do not affect ranking. Malformed optional metadata produces non-fatal limitations.

### 11. Make limitations and run summary part of the deterministic contract

Limitations are successful-result coverage records only. They describe incomplete or bounded inspection, skipped paths, truncation, unsupported files, malformed optional metadata, empty repositories, no matches, and result caps. They are structurally ordered and included in the contract hash.

`run_summary` is inside the successful result and is mechanically derivable from deterministic payload facts and configuration identity. It is not a production tracing system. Counts distinguish discovery/scanning counts from candidate and returned result-array counts so result truncation is observable without dangling references.

### 12. Pin fixtures before implementation

Milestone 1 is contract-first. Acceptance-test skeletons, fixture workspaces, expected contract fragments, expected validation errors, ordering assertions, limitation expectations, evidence-shape checks, payload-avoidance checks, and side-effect absence checks must exist before retrieval implementation begins.

Fixture workspaces are separate from expected outputs and generated outputs. Generated outputs must never be written inside scanned workspaces. Fixture side-effect checks verify that repository content and path lists do not change, and that no command, network, dependency installation, PR, external side-effect, or memory API is invoked.

## Risks and Mitigations

- **Risk: Contract shape becomes too broad.** Mitigation: keep Milestone 1 fields limited to deterministic repository context, evidence references, limitations, test hints, and run summary; defer symbol hints, semantic analysis, and future workflow artifacts.
- **Risk: Determinism varies across implementations.** Mitigation: specify canonical JSON, exact normalization, fixed scoring, tie-breakers, path formatting, limits, and fixture expectations.
- **Risk: Read-only boundary is weakened by read-only commands.** Mitigation: forbid all command execution and allow only workspace-confined filesystem APIs.
- **Risk: Evidence references leak payloads.** Mitigation: store references, locators, and hashes rather than raw snippets or full content; explicitly exclude production secret scanning while testing payload avoidance.
- **Risk: Stable IDs imply storage infrastructure.** Mitigation: define IDs for identity and references only; keep production persistence and lookup APIs out of Milestone 1.
