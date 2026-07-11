## 1. Spec Review Gate

- [ ] 1.1 Confirm `proposal.md`, `design.md`, and `specs/repository-context/spec.md` all describe only the Milestone 1 Repository Context Foundation Slice.
- [ ] 1.2 Confirm all explicit exclusions remain excluded: role agents, workflow graph, orchestration runtime, DeerFlow core modification, patch generation, autonomous editing, test execution, validation loop, review automation, PR/branch/commit creation, production persistence, memory reads/writes, command execution, network access, LLM reasoning, semantic ranking, code summarization, symbol hints, and production secret scanning.
- [ ] 1.3 Confirm `RepositoryContextResult` is defined as immutable, non-authorizing context and evidence only.
- [ ] 1.4 Confirm validation errors are separate tagged envelopes and cannot contain partial successful-result fields.

## 2. Contract and Schema Skeletons

- [ ] 2.1 Define the successful `RepositoryContextResult` schema with required fields, `result_type: "repository_context_result"`, allowed `completion_status` values, and no `runtime_metadata`.
- [ ] 2.2 Define the validation error envelope schema with `result_type: "repository_context_validation_error"`, required `error_id`, validation-only fields, stable error codes, and no successful-result fields.
- [ ] 2.3 Define canonical JSON serialization helpers for successful results, evidence IDs, and validation errors, including identity-field self-exclusion.
- [ ] 2.4 Define deterministic ID formats: `rcr_sha256:<hex>`, `ev_sha256:<hex>`, and `rce_sha256:<hex>`.
- [ ] 2.5 Define `workspace_ref.root_id` validation and the initial allowed configuration profile `repository-context/m1-defaults-v1`, including the deterministic behaviors covered by that profile and the rule that future default changes require a new profile identity.
- [ ] 2.6 Define limitation object schema, stable limitation code set, limitation ordering, grouped-result limitations, and path-specific coverage limitations.
- [ ] 2.7 Define `run_summary` schema, `completion_status` derivation, deterministic `input_summary`, candidate counts, returned counts, discovery/scanning counts, and sorted `limitation_codes`.

## 3. Fixture Layout and Acceptance Skeletons

- [ ] 3.1 Create fixture directory conventions for input workspaces under `openspec/changes/repository-context-foundation/fixtures/workspaces/<case>/`.
- [ ] 3.2 Create expected-output conventions under `openspec/changes/repository-context-foundation/fixtures/expected/<case>/`.
- [ ] 3.3 Ensure generated outputs, if any, are outside scanned workspaces or under the ignored `openspec/changes/*/fixtures/output/` path.
- [ ] 3.4 Add acceptance-test skeletons that compare canonical contract payloads and validation error envelopes before read-only retrieval implementation begins.
- [ ] 3.5 Add fixture expectations for input normalization, query-only retrieval, issue-text truncation, path formatting, empty query, oversized query, missing workspace identity, invalid configuration profile, inaccessible workspace, and path escape.
- [ ] 3.6 Add fixture expectations for deterministic discovery, explicit ignore policy, ignored directory counting, no `.gitignore` semantics, nested fixture-output exclusion, and no recursive ignored-directory inspection.
- [ ] 3.7 Add fixture expectations for strict UTF-8 decoding, UTF-8 BOM handling, binary detection, unsupported encoding, CRLF/CR normalization, line-based substring matching, same-line duplicate collapse, locator semantics, content hashes, oversized files, and file scan truncation.
- [ ] 3.8 Add fixture expectations for ranking inputs, match score formula, match-reason projection, tie-breaking, relevant-file inclusion, excluded config/test/symbol ranking signals, and query-only ranking.
- [ ] 3.9 Add fixture expectations for evidence reference IDs, text-only search results, no dangling references, result caps, candidate-versus-returned counts, and grouped `result_set_truncated`.
- [ ] 3.10 Add fixture expectations for root-only `package.json` and `Makefile` test command hints, malformed optional metadata limitations, hint deduplication, hint ordering, and no ranking impact.
- [ ] 3.11 Add fixture expectations for empty repositories, no matches, unreadable files, symlink escapes, symlink loops, duplicate files at different paths, and symlink entries excluded from relevant files.
- [ ] 3.12 Add payload-avoidance fixtures with synthetic sensitive-looking values that verify no raw snippets, full file contents, host absolute paths, stack traces, environment variables, or unbounded raw inputs appear in outputs.
- [ ] 3.13 Add side-effect absence checks that snapshot fixture workspaces before and after retrieval and assert no repository file additions, removals, or content mutations.
- [ ] 3.14 Add guardrail checks that no subprocesses, shell commands, Git commands, package-manager commands, test commands, network calls, external PR or side-effect tools, dependency installation, memory reads, or memory writes are invoked.

## 4. Read-Only Retrieval Implementation

- [ ] 4.1 Implement workspace validation using caller-supplied logical workspace identity and allowed configuration profile.
- [ ] 4.2 Implement canonical workspace-relative path normalization and host-path exclusion.
- [ ] 4.3 Implement direct filesystem-only discovery with no command execution and no default network access.
- [ ] 4.4 Implement the explicit default ignore policy and skipped file/directory counting.
- [ ] 4.5 Implement symlink traversal-control handling without returning symlink entries as relevant files.
- [ ] 4.6 Implement bounded metadata reads, strict UTF-8 text reads, binary detection, unsupported-encoding handling, line-ending normalization, prefix truncation, and content hashing.
- [ ] 4.7 Implement line-based substring matching driven only by `query.normalized`.
- [ ] 4.8 Implement relevant-file candidate construction, text-only search results, evidence references, limitations, and no-dangling-reference invariants.

## 5. Ranking, Hints, and Result Assembly

- [ ] 5.1 Implement fixed ranking inputs and match score calculation using only filename, path, and capped text-match signals.
- [ ] 5.2 Implement deterministic match-reason projection and relevant-file sorting.
- [ ] 5.3 Implement root-only descriptive test command hints for strict `package.json` and `Makefile` rules.
- [ ] 5.4 Ensure test command hints are never executed and never affect scores or relevant-file ordering.
- [ ] 5.5 Implement result caps, result truncation order, grouped `result_set_truncated`, candidate counts, returned counts, and evidence pruning without dangling references.
- [ ] 5.6 Assemble immutable successful results with canonical IDs and bounded deterministic run summary.
- [ ] 5.7 Assemble validation error envelopes with canonical `error_id` and no successful-result fields.

## 6. Verification

- [ ] 6.1 Run OpenSpec validation for `repository-context-foundation`.
- [ ] 6.2 Run acceptance fixtures and verify deterministic repeated execution produces identical canonical successful-result IDs and validation error IDs.
- [ ] 6.3 Verify result IDs change when deterministic payload facts change, including limitations, skipped coverage, truncation, candidate/returned counts, evidence references, or configuration identity.
- [ ] 6.4 Verify no raw source snippets, full file contents, raw command output, host absolute paths, stack traces, environment variables, unbounded raw inputs, runtime metadata, or synthetic sensitive-looking values appear in outputs.
- [ ] 6.5 Verify read-only side-effect checks pass and no forbidden command, network, dependency, PR, external side-effect, or memory API is invoked.
- [ ] 6.6 Verify fixtures and implementation do not introduce symbol hints, config ranking, test-convention ranking, semantic ranking, LLM reasoning, validation execution, patch generation, or workflow runtime behavior.
