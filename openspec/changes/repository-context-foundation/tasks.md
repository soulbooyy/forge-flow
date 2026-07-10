## 1. Spec Review Gate

- [ ] 1.1 Review `repository-context-foundation` proposal, design, and spec against RFC-001, RFC-002, RFC-004, and RFC-007.
- [ ] 1.2 Confirm that `symbol_hints` are optional and not required for Milestone 1 acceptance.
- [ ] 1.3 Confirm that Milestone 1 acceptance does not depend on DeerFlow runtime integration or DeerFlow core modification.

## 2. Contract Shape

- [ ] 2.1 Define the Milestone 1 `RepositoryContextResult` schema or typed contract with required and optional top-level fields.
- [ ] 2.2 Define nested shapes for workspace reference, query, optional issue text, relevant files, search results, evidence references, test command hints, limitations, runtime metadata, and run summary.
- [ ] 2.3 Define permitted empty values, validation errors, and serialization expectations for the contract.
- [ ] 2.4 Define controlled values for `match_reasons`, `ranking_inputs`, evidence kinds, limitation codes, file kinds, and completion status.
- [ ] 2.5 Define `evidence_refs` shape without embedding raw source payloads by default.
- [ ] 2.6 Add validation for absence of out-of-scope future contracts: `PatchProposal`, `ValidationResult`, `ReviewResult`, and `PRResult`.

## 3. Deterministic Fixtures

- [ ] 3.1 Create fixture repositories or fixture directories for deterministic file-name and text search.
- [ ] 3.2 Add fixture coverage for empty repository, no-match query, absent issue text, empty query, and whitespace-only query.
- [ ] 3.3 Add fixture coverage for ranking ties, duplicate matches across retrieval signals, and duplicate evidence references.
- [ ] 3.4 Add fixture coverage for workspace boundary enforcement, including parent path escape, symlink escape, and symlink loop cases.
- [ ] 3.5 Add fixture coverage for ignored files, hidden directories according to ignore policy, binary files, oversized files, unreadable files, and unsupported encodings.
- [ ] 3.6 Add fixture coverage verifying that suggested fixes or test commands do not trigger patch generation or test execution.

## 4. Read-Only Retrieval

- [ ] 4.1 Implement workspace root resolution, path normalization, and workspace-relative returned path formatting.
- [ ] 4.2 Block parent-directory escape, symlink escape, and symlink loops during file discovery and file inspection.
- [ ] 4.3 Implement deterministic file search and text search over workspace-confined files.
- [ ] 4.4 Implement deterministic ranking from filename, path, text, configuration, test convention, and optional symbol hint signals.
- [ ] 4.5 Implement stable ordering, tie-breaking, duplicate match merging, and duplicate evidence reference deduplication.
- [ ] 4.6 Produce bounded limitations for skipped paths, ignored files, unavailable analyzers, weak signals, truncated scans, and incomplete coverage.

## 5. Hints, Evidence, and Run Summary

- [ ] 5.1 Implement test command hints as non-executable repository context derived from deterministic project conventions.
- [ ] 5.2 Implement optional cheap language-agnostic symbol hints only if feasible without LLM reasoning or language-server dependency.
- [ ] 5.3 Attach evidence references to relevant files, search results, optional symbol hints, and test command hints.
- [ ] 5.4 Ensure raw source snippets are not persisted in `RepositoryContextResult` by default.
- [ ] 5.5 Add minimal non-payload `run_summary` metadata with operation type, deterministic input summary, counts, limitation codes, and completion status.

## 6. Verification

- [ ] 6.1 Validate the OpenSpec change with `openspec validate repository-context-foundation`.
- [ ] 6.2 Add automated tests for `RepositoryContextResult` contract validation.
- [ ] 6.3 Add automated tests for deterministic repeated retrieval.
- [ ] 6.4 Add automated tests for read-only workspace confinement and symlink escape blocking.
- [ ] 6.5 Add automated tests for empty results, invalid input, ranking ties, duplicate matches, skipped files, and minimal run summary metadata.
- [ ] 6.6 Document any remaining Milestone 1 limitations before implementation review.
