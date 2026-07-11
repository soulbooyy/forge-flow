## ADDED Requirements

### Requirement: Repository Context result envelopes SHALL be explicit deterministic contracts
The Repository Context capability SHALL return exactly one of two tagged envelopes:

- `result_type: "repository_context_result"` for a successful `RepositoryContextResult`
- `result_type: "repository_context_validation_error"` for an input or workspace validation failure

A successful `RepositoryContextResult` SHALL include `schema_version`, `contract_id`, `workspace_ref`, `query`, `issue_text`, `relevant_files`, `search_results`, `test_command_hints`, `evidence_refs`, `limitations`, and `run_summary`. It SHALL NOT include `runtime_metadata`, raw repository content, raw command output, host absolute paths, timestamps, process identifiers, execution duration, stack traces, environment variables, memory records, policy decisions, patch state, validation outcomes, branch state, commit state, or PR state.

`RepositoryContextResult.contract_id` SHALL be derived from canonical UTF-8 JSON bytes for the deterministic contract payload, with `contract_id` itself omitted before hashing. Canonical JSON SHALL sort object keys lexicographically, preserve arrays in their OpenSpec-defined deterministic order, include required empty arrays and objects, omit absent optional fields instead of serializing them as `null` unless a field explicitly requires `null`, use JSON booleans, use integer JSON numbers for counts, scores, limits, and line numbers, include no insignificant whitespace, and avoid floating point values. The hash format SHALL be `rcr_sha256:<lowercase-hex-sha256>`.

The canonical contract payload SHALL include deterministic contract facts, including `result_type`, `schema_version`, caller-supplied logical workspace identity, configuration profile identity, normalized inputs, relevant files, search results, evidence references, test command hints, limitations, deterministic run-summary counts, limit summaries, and limitation summaries. The payload SHALL exclude runtime-only or environment-specific values. Any change to limitations, skipped coverage, truncation, deterministic run-summary counts, positive evidence, returned ordering, or deterministic configuration identity SHALL change `contract_id`.

Validation failures SHALL be represented only by a validation error envelope. A validation error envelope SHALL include `result_type`, `schema_version`, `error_id`, `completion_status: "validation_error"`, `error_code`, `input_category`, a bounded user-safe `message`, and a bounded `summary`; it MAY include a bounded redacted `input_ref`. It SHALL NOT include `contract_id`, `relevant_files`, `search_results`, `test_command_hints`, `evidence_refs`, `limitations`, or any partial successful-result payload. `error_id` SHALL use the format `rce_sha256:<lowercase-hex-sha256>` and SHALL be derived from the canonical validation error payload with `error_id` omitted.

#### Scenario: Successful result identity is canonical
- **GIVEN** two runs with the same valid inputs, workspace contents, and configuration profile
- **WHEN** the service serializes the deterministic result payload using canonical JSON
- **THEN** both runs produce the same `contract_id`
- **AND** the serialized payload excludes `contract_id` itself, runtime metadata, host absolute paths, timestamps, process identifiers, durations, stack traces, raw source snippets, raw command output, and environment variables

#### Scenario: Coverage changes affect identity
- **GIVEN** two runs with the same positive matches
- **WHEN** one run also records a skipped file, ignored directory, truncation, unreadable file, malformed optional metadata, or different deterministic run-summary count
- **THEN** the two successful results produce different `contract_id` values

#### Scenario: Validation failure is not a partial result
- **GIVEN** an invalid required input
- **WHEN** validation fails before repository context is safely produced
- **THEN** the service returns `result_type: "repository_context_validation_error"`
- **AND** the envelope includes `error_id` but not `contract_id`
- **AND** the envelope includes none of the successful-result fields `relevant_files`, `search_results`, `test_command_hints`, `evidence_refs`, or `limitations`

### Requirement: Inputs SHALL be bounded, normalized, and explicitly versioned
The service input SHALL include a caller-supplied logical `workspace_ref.root_id`, a caller-supplied `configuration_profile_id`, a workspace root, a query, and MAY include issue text. `workspace_ref.root_id` SHALL be safe to persist and SHALL NOT be derived from host absolute paths, filesystem metadata, repository contents, timestamps, machine identity, secrets, or runtime metadata. Missing or unsafe workspace identity SHALL return `missing_workspace_ref` or `invalid_workspace`.

The only Milestone 1 configuration profile SHALL be `repository-context/m1-defaults-v1`. The service SHALL reject any other profile with a validation error such as `invalid_config_profile`. The profile identity SHALL be echoed in `run_summary.input_summary` and included in the canonical contract payload. The profile SHALL identify all deterministic behavior covered by Milestone 1, including normalization rules, matching rules, ranking weights, score caps, ignore policy, scan limits, result limits, decoding policy, and test-hint policy. These defaults SHALL NOT change silently under the same profile identity; any future contract-affecting change SHALL require a new explicit profile identity such as `repository-context/m1-defaults-v2`.

Input normalization SHALL be fixed for Milestone 1: apply Unicode NFC normalization, trim leading and trailing whitespace, collapse internal whitespace runs to one ASCII space, and derive a case-insensitive matching view using Unicode casefolding. `query.normalized` SHALL be the sole retrieval and ranking driver. Optional `issue_text.normalized` SHALL be recorded only as bounded input context; it SHALL NOT produce match reasons, evidence references, search results, scores, no-match behavior, or ranking changes.

The default profile SHALL bound inputs. `query.normalized` SHALL be non-empty and SHALL NOT exceed 512 Unicode scalar values. Empty, whitespace-only, or oversized queries SHALL produce validation errors such as `empty_query` or `query_too_large`. Optional issue text SHALL NOT fail an otherwise valid run only because it is oversized; instead the service SHALL normalize and retain at most 4096 Unicode scalar values, record deterministic truncation or omission in `run_summary.input_summary`, and emit an `issue_text_truncated` limitation when truncation occurs. The contract SHALL NOT persist unbounded raw query text, raw issue bodies, logs, stack traces, credentials, or binary-like input. Caller-provided raw references MAY be recorded only as bounded references, not embedded raw content.

#### Scenario: Query drives retrieval
- **GIVEN** a valid query and issue text that mentions additional files
- **WHEN** the service retrieves repository context
- **THEN** only `query.normalized` drives filename, path, text matching, ranking, search results, evidence references, and no-match behavior
- **AND** `issue_text.normalized` appears only as bounded input context

#### Scenario: Oversized issue text is bounded
- **GIVEN** a valid query and optional issue text longer than the configured issue-text bound
- **WHEN** the service produces a successful result
- **THEN** the result includes a bounded normalized issue-text value or bounded reference
- **AND** the result includes an `issue_text_truncated` limitation
- **AND** the result does not embed the full raw issue text

### Requirement: Workspace inspection SHALL be read-only, filesystem-only, and workspace-confined
Milestone 1 SHALL inspect workspaces only through direct language/runtime filesystem APIs or libraries confined to the workspace. The service SHALL NOT execute commands of any kind, including shell commands, subprocesses, `git`, `rg`, `grep`, `find`, package managers, test commands, language servers, external tools, or tool-backed search. The service SHALL NOT install dependencies, access the network by default, write repository files, create branches, create commits, create PRs, read or write memory, generate patches, run validation loops, or modify DeerFlow core.

Every filesystem read SHALL pass canonical path normalization, ignore-policy evaluation, workspace-boundary checks, and symlink authorization before content is inspected. Returned paths SHALL be canonical workspace-relative paths using `/` separators, SHALL NOT start with `/`, SHALL NOT contain `.` or `..` segments, SHALL NOT contain empty segments or duplicate separators, SHALL preserve the path casing observed in the workspace, and SHALL never expose host absolute paths in successful results or validation errors. Lexical sorting and tie-breaking SHALL compare this canonical returned-path representation.

Symlink entries SHALL be treated only as traversal-control artifacts in Milestone 1. They SHALL NOT be ranked, SHALL NOT appear in `relevant_files`, SHALL NOT produce filename or path relevance evidence, and SHALL NOT expose target content. Symlink escapes and loops SHALL produce structured limitations such as `symlink_escape` or `symlink_loop` and deterministic run-summary counts.

#### Scenario: Path escape is rejected
- **GIVEN** an input workspace path or discovered entry that would escape the workspace after normalization or symlink resolution
- **WHEN** the service evaluates the path
- **THEN** the service does not inspect escaped content
- **AND** unsafe required workspace input produces a validation error such as `path_escape`
- **AND** unsafe discovered entries are represented only through limitations and counts

#### Scenario: No command execution
- **GIVEN** a valid workspace
- **WHEN** the service discovers files or searches text
- **THEN** it performs inspection only through workspace-confined filesystem APIs or libraries
- **AND** it does not invoke shell commands, subprocesses, Git, search commands, package managers, test commands, language servers, network calls, memory APIs, or external side-effect tools

### Requirement: Discovery and ignore behavior SHALL be deterministic and narrow
The `repository-context/m1-defaults-v1` profile SHALL use only the OpenSpec-defined ignore policy. It SHALL ignore exactly these path rules:

- `.git/`
- `.forgeflow/cache/`
- `.forgeflow/artifacts/`
- `openspec/changes/*/fixtures/output/`

The default profile SHALL NOT apply `.gitignore`, `.ignore`, global Git excludes, VCS ignore semantics, dependency-directory defaults, build-output defaults, all-hidden-directory defaults, or ecosystem-specific ignore rules. Files such as `.gitignore` SHALL be treated as ordinary workspace files unless excluded by an explicit Milestone 1 ignore rule.

Ignored files SHALL count as one skipped file when encountered. Ignored directories SHALL count as one skipped directory when encountered; discovery SHALL NOT descend into them and SHALL NOT recursively count or inspect their contents. Skipped files and directories SHALL be reflected in deterministic run-summary counts and limitations where applicable, and the result SHALL NOT imply ignored content was inspected.

Canonical workspace-relative path SHALL be the sole file identity. The service SHALL NOT deduplicate files by inode, hard-link identity, or content hash. Identical evidence at different canonical paths SHALL remain distinct; duplicate evidence SHALL be deduplicated only within the same canonical path and canonical evidence key.

#### Scenario: Explicit ignore policy only
- **GIVEN** a workspace containing `.gitignore`, `node_modules/`, `.cache/`, `dist/`, and `.forgeflow/cache/`
- **WHEN** the default profile discovers files
- **THEN** `.forgeflow/cache/` is ignored
- **AND** `.gitignore`, `node_modules/`, `.cache/`, and `dist/` are scanned unless another explicit Milestone 1 rule excludes them

#### Scenario: Ignored directory is counted once
- **GIVEN** an ignored directory containing nested files
- **WHEN** discovery encounters the ignored directory
- **THEN** `run_summary.counts.skipped_directories` increases by one
- **AND** discovery does not descend into the ignored directory
- **AND** nested contents do not produce evidence, relevant files, or recursive skipped-file counts

### Requirement: Text inspection, matching, locators, and content hashes SHALL be canonical
Milestone 1 text inspection SHALL use strict UTF-8 decoding only. The service SHALL detect binary files before decoding using the presence of a NUL byte in the inspected prefix. UTF-8 BOM SHALL be permitted and removed before normalized text processing. Invalid UTF-8 SHALL produce an `unsupported_encoding` limitation; lossy replacement decoding, Latin-1 fallback, and heuristic charset detection SHALL NOT be used. After decoding, CRLF and CR line endings SHALL be normalized to LF before matching, locator calculation, and content hashing.

Text matching SHALL be line-based substring matching. The service SHALL split canonical inspected text into lines, derive a normalized and casefolded matching view for the query and each line, and match `query.normalized` as a substring within each normalized line. Matches SHALL NOT cross line boundaries. Multiple occurrences or overlapping matches on the same line SHALL collapse into one text locator; matching lines on different lines SHALL produce separate locators up to the configured per-file locator cap.

Text locators SHALL use 1-based line numbers and inclusive line ranges. `start_line` and `end_line` SHALL be required for text matches, columns SHALL be omitted, and file-level evidence SHALL use `locator: null`. For truncated scans, the service SHALL scan a prefix from the start of the file so reported line numbers remain original normalized file line numbers, and uninspected content beyond the scanned range SHALL produce a `file_scan_truncated` limitation.

Inspected text evidence SHALL include `content_hash` verification metadata using SHA-256 over the canonical inspected text representation or canonical inspected range. Evidence SHALL record whether the hash covers the full inspected file or only a truncated inspected range. Skipped, ignored, unreadable, binary, or unsupported files SHALL NOT receive inspected-text content hashes. Content hashes are allowed evidence verification metadata, not raw source payload, not secret scanning, and not proof that content is secret-free.

#### Scenario: Same-line duplicates collapse
- **GIVEN** an inspected UTF-8 text file with multiple occurrences of the normalized query on the same line
- **WHEN** text matching is performed
- **THEN** the service emits one text locator for that line
- **AND** the locator uses 1-based inclusive line numbers

#### Scenario: Unsupported encoding is not searched
- **GIVEN** a file that fails strict UTF-8 decoding
- **WHEN** the service inspects the file
- **THEN** the file does not produce text-match search results or inspected-text content hashes
- **AND** the result records an `unsupported_encoding` limitation

### Requirement: Ranking and relevant files SHALL use fixed direct evidence only
`relevant_files` SHALL include only discovered, non-ignored files with at least one positive Milestone 1 match reason derived from direct filename, path, or text matching. Files with only limitations and no positive match SHALL NOT appear in `relevant_files`. Ignored files and directories SHALL NOT appear in `relevant_files`. Binary, unreadable, unsupported-encoding, or oversized files MAY appear only when they have a positive filename or path match and SHALL carry appropriate file kind and limitations without implying text inspection. Symlink entries SHALL NOT appear.

Each `relevant_files` item SHALL include canonical `path`, `file_kind`, integer `match_score`, `ranking_inputs`, `match_reasons`, and `evidence_ref_ids`. `ranking_inputs` SHALL be the single source of truth for scoring and SHALL include exactly `filename_match: boolean`, `path_match: boolean`, and `text_match_count: integer`. `text_match_count` SHALL be the capped number of text locators used for scoring. The default score formula SHALL be:

- `100` points when `filename_match` is true
- `50` points when `path_match` is true
- `25` points for each text locator counted in `text_match_count`, up to the configured per-file cap

`match_reasons` SHALL be a deterministic projection of `ranking_inputs`, ordered exactly as `filename_match`, `path_match`, `text_match`, including each reason only when the corresponding signal is positive. Milestone 1 SHALL NOT include `config_match`, `test_convention_match`, `symbol_hint`, semantic relevance signals, inferred framework metadata, issue-text signals, LLM-derived signals, AST signals, or language-server signals.

Relevant files SHALL be sorted by `match_score` descending, then canonical path ascending. Any future change to weights, caps, tie-breakers, or allowed ranking inputs SHALL require a new explicit configuration profile identity.

#### Scenario: Score is recomputable from ranking inputs
- **GIVEN** a returned relevant file
- **WHEN** a fixture applies the documented formula to its `ranking_inputs`
- **THEN** the computed score equals `match_score`
- **AND** `match_reasons` contains only the ordered projection of positive ranking inputs

#### Scenario: Ranking tie is stable
- **GIVEN** two relevant files with equal `match_score`
- **WHEN** the service orders `relevant_files`
- **THEN** the file with the lexically smaller canonical path appears first

### Requirement: Evidence, search results, and test command hints SHALL have separate narrow responsibilities
`evidence_refs` SHALL contain references and verification metadata, not raw evidence payloads. `evidence_ref.id` SHALL use a canonical deterministic ID derived from a canonical evidence key with `id` omitted. The evidence key SHALL include canonical path when present, evidence kind, retrieval signal, normalized locator when present, and deterministic verification metadata such as inspected-text `content_hash` when present. The ID format SHALL be `ev_sha256:<lowercase-hex-sha256>`. Evidence IDs SHALL exclude runtime metadata, host absolute paths, timestamps, process identifiers, random values, execution details, raw snippets, and full source payloads.

`search_results` SHALL contain only bounded text-match results found inside inspected text content. A search result SHALL include canonical path, required text locator, and `evidence_ref_id`. Filename, path, configuration-file status, and test-convention facts SHALL NOT appear as search results and SHALL NOT use fake locators.

`test_command_hints` SHALL be descriptive metadata only. They SHALL be included in the canonical payload when emitted but SHALL NOT be executed, SHALL NOT affect `match_score`, SHALL NOT affect relevant-file ranking, and SHALL NOT authorize validation execution. Test-hint discovery SHALL inspect only root-level `<workspace_root>/package.json` and `<workspace_root>/Makefile` when they are inside the allowed scan boundary.

Root `package.json` handling SHALL parse strict JSON only, reject comments and trailing commas, consider only a top-level `scripts.test` string, and emit canonical command `npm test`. Invalid JSON or unsupported metadata SHALL produce a non-fatal limitation, not a validation error and not a hint. The service SHALL NOT infer Yarn, pnpm, Bun, dependencies, frameworks, lockfiles, or raw script bodies.

Root `Makefile` handling SHALL ignore blank and comment-only lines, detect a non-recipe target line whose target list includes exactly `test`, and emit canonical command `make test`. `.PHONY: test` alone, pattern rules, includes, variables, recipes, and command bodies SHALL NOT be parsed or emitted as hints.

Hints SHALL include evidence references to metadata files or metadata lines, SHALL be deduplicated by canonical command and source, and SHALL be sorted lexicographically by canonical command then source path. Nested `package.json` or `Makefile` files MAY be searched as ordinary files but SHALL NOT emit test command hints.

#### Scenario: Text search results are not path hits
- **GIVEN** a file whose path matches the query but whose text does not
- **WHEN** the service returns context
- **THEN** the file may appear in `relevant_files` with path evidence
- **AND** no `search_results` entry is emitted for that path-only match

#### Scenario: Root test hint is descriptive
- **GIVEN** a root `package.json` with a strict top-level `scripts.test` string
- **WHEN** the service emits test command hints
- **THEN** it emits a deterministic `npm test` hint with evidence references
- **AND** the hint is not executed and does not affect file scores or ordering

### Requirement: Limits, truncation, limitations, and run summary SHALL be deterministic
The `repository-context/m1-defaults-v1` profile SHALL define these default bounds:

- maximum normalized query length: 512 Unicode scalar values
- maximum retained normalized issue-text length: 4096 Unicode scalar values
- maximum inspected text bytes per file: 1,048,576
- maximum scanned lines per file: 20,000
- maximum text match locators per file used for scoring: 20
- maximum returned relevant files: 50
- maximum returned search results: 200
- maximum returned evidence references: 300
- maximum returned test command hints: 10

Truncation and caps SHALL be explicit. Partial file scans SHALL produce limitations, skipped or truncated content SHALL NOT be represented as fully inspected, and `match_score` SHALL use only documented capped counts. Result-set truncation SHALL occur after deterministic candidate discovery, scoring, and sorting. The service SHALL first compute candidate relevant files, search results, evidence references, and test hints within scan limits; sort relevant-file candidates deterministically; apply `max_relevant_files`; retain only search results associated with retained relevant files; sort and cap `search_results`; sort and cap test command hints; and finally retain only evidence references referenced by retained relevant files, returned search results, or returned test hints.

The final result SHALL have no dangling references. Every `relevant_files[].evidence_ref_ids`, `search_results[].evidence_ref_id`, and `test_command_hints[].evidence_ref_ids` value SHALL resolve to a top-level `evidence_refs` item. If any otherwise valid candidate, locator, hint, or evidence reference is dropped by a result cap, the result SHALL include exactly one grouped `result_set_truncated` limitation with `scope: "result"` and bounded structured detail naming affected capped arrays.

Limitations SHALL be successful-result coverage records only. A limitation SHALL include `code`, `scope`, and bounded safe `detail`; it MAY include canonical `path`, deterministic `count`, and `related_evidence_ref_ids`. Initial limitation codes SHALL include `empty_repository`, `no_matches`, `ignored_path`, `binary_file_skipped`, `oversized_file_skipped`, `file_scan_truncated`, `result_set_truncated`, `unreadable_file`, `unsupported_encoding`, `symlink_escape`, `symlink_loop`, `path_escape`, `incomplete_coverage`, `issue_text_truncated`, and `malformed_metadata`. Limitations SHALL be ordered by `code` ascending, then scope using `input < workspace < directory < file < result`, then absent path before present path, then canonical path ascending, then deterministic count or bounded detail if needed. `related_evidence_ref_ids` SHALL be sorted by canonical evidence ID.

`run_summary` SHALL be part of the successful `RepositoryContextResult` and SHALL be mechanically derivable from the deterministic result payload and configuration profile identity. Any separately emitted summary SHALL be a non-authoritative derived view. `completion_status` in successful results SHALL be `completed` only when `limitations` is empty and `completed_with_limitations` whenever `limitations` is non-empty. Validation errors SHALL use only `completion_status: "validation_error"` in the validation envelope.

`run_summary.counts` SHALL distinguish discovery/scanning counts from capped result arrays. It SHALL include single deterministic counts for `discovered_files`, `discovered_directories`, `scanned_text_files`, `skipped_files`, and `skipped_directories`. It SHALL also include `counts.candidates.relevant_files`, `counts.candidates.search_results`, `counts.candidates.evidence_refs`, and `counts.candidates.test_command_hints`, plus `counts.returned.relevant_files`, `counts.returned.search_results`, `counts.returned.evidence_refs`, `counts.returned.test_command_hints`, and `counts.returned.limitations`. Returned counts SHALL equal returned array lengths. `run_summary.limitation_codes` SHALL be the unique sorted set of limitation codes.

#### Scenario: No matches is a successful limited result
- **GIVEN** a valid workspace and query with no deterministic filename, path, or text matches
- **WHEN** the service completes repository inspection
- **THEN** it returns `result_type: "repository_context_result"`
- **AND** `relevant_files`, `search_results`, and match-related evidence are empty
- **AND** the result includes a grouped `no_matches` limitation
- **AND** `run_summary.completion_status` is `completed_with_limitations`

#### Scenario: Result caps preserve graph consistency
- **GIVEN** candidate results exceeding one or more result caps
- **WHEN** the service applies result truncation
- **THEN** all returned references resolve to returned `evidence_refs`
- **AND** the result includes one grouped `result_set_truncated` limitation
- **AND** candidate counts exceed returned counts for the affected arrays

### Requirement: Repository Context results SHALL be non-authorizing, immutable, and not production-persisted by Milestone 1
`RepositoryContextResult` SHALL be non-authorizing context and evidence only. It SHALL NOT approve later reads, commands, tests, edits, memory operations, network access, PR side effects, branch creation, commit creation, or policy decisions. Later workflow stages MAY reference the result but SHALL perform their own OpenSpec-authorized policy evaluation.

`RepositoryContextResult` SHALL be immutable after creation. Later stages SHALL NOT mutate it, append fields, mark files as approved, add validation outcomes, attach policy decisions, add patch or PR state, or store future-stage workflow state inside it. Later contracts or artifacts MAY reference `repository_context_contract_id` and specific `evidence_ref.id` values, but they SHALL carry their own schemas and identities.

Milestone 1 SHALL NOT introduce production persistence, artifact storage, contract lookup APIs, retention policy, access-control model, durable run-summary storage, migration scheme, or storage-integrity mechanism. Stable IDs SHALL support fixture comparison, regression tests, caller-owned handling, and future references only.

Milestone 1 SHALL explicitly exclude production secret scanning. The service SHALL reduce payload leakage by avoiding raw snippets, full file contents, unbounded user inputs, host absolute paths, stack traces, environment variables, raw command output, and runtime metadata. Fixtures MAY include synthetic sensitive-looking values to verify payload avoidance, but SHALL NOT require secret detection, classification, redaction policy, or secret-specific policy decisions.

#### Scenario: Result does not authorize later actions
- **GIVEN** a result with `completion_status: "completed"` and no limitations
- **WHEN** a later stage considers tests, edits, memory writes, network access, commits, branches, or PR creation
- **THEN** the repository context result alone does not authorize those actions

#### Scenario: Later artifacts reference but do not mutate
- **GIVEN** a future artifact that depends on repository context
- **WHEN** it records provenance
- **THEN** it references `contract_id` and relevant `evidence_ref.id` values
- **AND** it does not modify the original `RepositoryContextResult`

### Requirement: Acceptance fixtures SHALL pin contract behavior before implementation
The OpenSpec change SHALL define Milestone 1 acceptance-test skeletons and fixture expected outputs before read-only retrieval implementation begins. Fixture input workspaces SHALL live under `openspec/changes/repository-context-foundation/fixtures/workspaces/<case>/`. Expected outputs SHALL live separately under `openspec/changes/repository-context-foundation/fixtures/expected/<case>/`. Generated test outputs, if any, SHALL live outside the scanned workspace or under the explicitly ignored `openspec/changes/*/fixtures/output/` path. The service SHALL run only against the specific fixture workspace root, not the parent fixtures directory.

Acceptance fixtures SHALL cover deterministic contract IDs, validation error envelopes, input normalization, query-only retrieval, path formatting, ignore behavior, read-only boundary checks, symlink escape handling, strict UTF-8 decoding, binary and unsupported files, oversized and truncated files, line-based matching, duplicate match collapse, fixed scoring, tie-breaking, relevant-file inclusion, text-only search results, evidence ID generation, content hashes, root-only test hints, malformed optional metadata limitations, result caps, candidate versus returned counts, no dangling evidence references, limitations ordering, empty repositories, no matches, immutable/non-authorizing semantics, payload avoidance, and side-effect absence.

Acceptance checks SHALL snapshot fixture workspaces before and after retrieval and assert that no repository files are modified, no files or directories are added or removed under the workspace, and generated outputs are not updated in place. They SHALL assert that no subprocesses, shell commands, Git commands, package-manager commands, test commands, network calls, PR or external side-effect tools, dependency installation, memory reads, or memory writes are invoked. Content hashes and path lists SHALL be strict; filesystem metadata such as mtimes MAY be best-effort where platform behavior is fragile. Temporary files, if required by a future implementation, SHALL be outside the repository workspace and SHALL NOT appear in the result.

#### Scenario: Fixtures precede implementation
- **GIVEN** Milestone 1 implementation has not begun
- **WHEN** the change is reviewed for implementation readiness
- **THEN** acceptance-test skeletons and expected contract fragments exist for the deterministic behaviors listed in this requirement
- **AND** service implementation tasks depend on those fixtures

#### Scenario: Sensitive-looking payload is not embedded
- **GIVEN** a fixture workspace containing a synthetic sensitive-looking value
- **WHEN** the service returns repository context
- **THEN** expected output may include canonical paths, evidence references, locators, content hashes, and limitations
- **AND** expected output does not include the raw synthetic secret-like value or full file content
