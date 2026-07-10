## ADDED Requirements

### Requirement: Repository Context Service is deterministic and read-only
The system SHALL provide a Repository Context Service that derives repository context from a declared workspace root, a query, and optional issue text using deterministic retrieval signals only.

The service MUST NOT use LLM reasoning for relevance judgment, code summarization, root-cause inference, repair strategy, semantic ranking, or test recommendation during Milestone 1.

The service MUST NOT generate patches, edit code, execute tests, create branches, create commits, create pull requests, read long-term memory, write long-term memory, implement workflow role agents, implement a workflow graph, or require full DeerFlow runtime integration.

Repeated runs over the same workspace content, query, optional issue text, and configuration MUST produce structurally equivalent deterministic payloads after excluding fields explicitly marked as runtime metadata.

Runtime timestamps, random values, process-specific values, host absolute paths, and nondeterministic filesystem traversal order MUST NOT affect relevant files, evidence references, search results, test command hints, ranking metadata, limitations, or deterministic input summaries.

#### Scenario: Deterministic repeated retrieval
- **WHEN** the service is invoked twice with the same workspace content, query, optional issue text, and configuration
- **THEN** the deterministic payloads are structurally equivalent after excluding explicit runtime metadata

#### Scenario: No LLM relevance dependency
- **WHEN** repository context is produced for a query
- **THEN** the result is explainable through deterministic retrieval inputs rather than LLM-generated relevance judgment or free-form semantic rationale

#### Scenario: Out-of-scope implementation is rejected
- **WHEN** a Milestone 1 repository context run identifies possible files or test commands
- **THEN** it does not edit files, produce a patch, execute a test command, start a repair loop, create a branch, create a commit, create a PR artifact, invoke long-term memory, or invoke workflow role agents

### Requirement: RepositoryContextResult contract is concrete and bounded
The system SHALL produce `RepositoryContextResult` as the only required Milestone 1 contract deliverable.

`RepositoryContextResult` MUST be serializable as a deterministic structured object whose deterministic payload is independent from explicit runtime metadata.

The top-level contract MUST contain these required fields:

- `schema_version`: non-empty string identifying the Repository Context contract schema.
- `contract_id`: stable deterministic identifier derived from deterministic input summary and deterministic payload, or another implementation-defined stable value that remains unchanged for equivalent deterministic payloads.
- `workspace_ref`: object describing the workspace without exposing host-specific absolute paths.
- `query`: object representing normalized query input.
- `issue_text`: object representing optional issue text input.
- `relevant_files`: ordered array of relevant file result objects, permitted to be empty.
- `search_results`: ordered array of search result objects, permitted to be empty.
- `test_command_hints`: ordered array of test command hint objects, permitted to be empty.
- `evidence_refs`: ordered array of evidence reference objects, permitted to be empty.
- `limitations`: ordered array of limitation objects, permitted to be empty.
- `run_summary`: minimal non-payload run-summary object.

The top-level contract MAY contain these optional fields:

- `runtime_metadata`: object containing explicit runtime metadata excluded from deterministic payload comparison.
- `symbol_hints`: ordered array of symbol hint objects, permitted only as optional deterministic output and not required for Milestone 1 acceptance.

The contract MUST NOT contain a patch, diff, final root-cause decision, code edit, PR content, memory write, workflow role authorization, raw source snippet, full file content, prompt, hidden runtime state, or full DeerFlow checkpoint.

#### Scenario: Required contract surface is present
- **WHEN** repository context retrieval completes successfully
- **THEN** the result includes all required top-level `RepositoryContextResult` fields with valid empty arrays or objects where no matches exist

#### Scenario: Future milestone contracts are absent
- **WHEN** a Milestone 1 context run completes
- **THEN** it does not require creation, validation, persistence, or use of `PatchProposal`, `ValidationResult`, `ReviewResult`, or `PRResult`

#### Scenario: Runtime metadata is isolated
- **WHEN** the result includes runtime-generated identifiers or timing metadata
- **THEN** those values appear only under `runtime_metadata` or an equivalent explicitly excluded metadata location and do not affect deterministic payload comparison

### Requirement: Input representation and validation are explicit
The `workspace_ref` field SHALL identify the repository workspace through safe metadata only.

`workspace_ref` MUST include:

- `root_id`: stable logical workspace identifier or caller-provided workspace reference.
- `root_display_name`: optional non-authoritative display label, permitted to be empty or absent.
- `path_format`: value indicating that paths exposed in the result are normalized workspace-relative paths.

`workspace_ref` MUST NOT include host-specific absolute paths by default.

The `query` field MUST include:

- `raw_ref` or `raw`: the caller-provided query reference or bounded query text.
- `normalized`: deterministic normalized query string used for retrieval.
- `is_empty`: boolean indicating whether the normalized query is empty.

The `issue_text` field MUST include:

- `present`: boolean indicating whether optional issue text was provided.
- `raw_ref` or `raw`: caller-provided issue text reference or bounded issue text when present.
- `normalized`: deterministic normalized issue text used for retrieval, permitted to be empty.

Empty query and whitespace-only query MUST return a structured validation error and MUST NOT perform repository scanning.

Absent optional issue text MUST be represented as `present: false` and MUST NOT be treated as an error.

Invalid workspace input or inaccessible workspace root MUST return a structured validation error and MUST NOT return a successful `RepositoryContextResult`.

Structured validation errors MUST include a stable error code, bounded message, and the invalid input category; they MUST NOT include raw source contents, host absolute paths, stack traces, or secrets.

#### Scenario: Empty query is rejected
- **WHEN** the service receives an empty query
- **THEN** it returns a structured validation error with a stable empty-query code and does not scan repository files

#### Scenario: Whitespace-only query is rejected
- **WHEN** the service receives a whitespace-only query
- **THEN** it returns a structured validation error with a stable empty-query code and does not scan repository files

#### Scenario: Optional issue text absent
- **WHEN** the service receives a valid query without optional issue text
- **THEN** it returns a valid `RepositoryContextResult` whose `issue_text.present` value is false

#### Scenario: Invalid workspace input is rejected
- **WHEN** the workspace input cannot identify a valid workspace root
- **THEN** the service returns a structured validation error and does not inspect repository files

#### Scenario: Inaccessible workspace root is rejected
- **WHEN** the workspace root cannot be accessed for read-only inspection
- **THEN** the service returns a structured validation error and does not produce a successful `RepositoryContextResult`

### Requirement: Workspace access is normalized, confined, and read-only
The system SHALL confine all Repository Context Service repository reads to the declared workspace root.

Before authorization or reading, the system MUST normalize and resolve the workspace root and candidate paths according to the host filesystem.

The system MUST reject parent-directory escape, symlink escape, reads outside the workspace root, repository writes, dependency installation, default network access, and arbitrary command execution for Milestone 1 repository context behavior.

Absolute input paths MAY be accepted only as workspace root input or caller-supplied references; any path exposed through `RepositoryContextResult` MUST be normalized, workspace-relative, and MUST NOT contain `..`.

Symlinks MUST be resolved before file access. Symlink targets outside the workspace root MUST NOT be read. Symlink loops MUST be skipped and represented through a limitation.

Nested directories are allowed. Nested repository markers such as nested `.git` directories MUST NOT expand the authorized workspace boundary beyond the declared workspace root.

Case-sensitivity behavior MAY follow the host filesystem, but ordering and matching MUST remain deterministic for the same workspace on the same platform.

Read-only tool capability levels MUST be treated as capability classifications, not as authorization decisions.

#### Scenario: Path traversal is blocked
- **WHEN** repository context retrieval encounters a requested or discovered path that would resolve outside the workspace root through `..`
- **THEN** the system excludes that path from repository inspection and records a limitation or validation error without exposing a host absolute path

#### Scenario: Symlink escape is blocked
- **WHEN** repository context retrieval encounters a symlink whose resolved target is outside the workspace root
- **THEN** the system does not read the target and records a limitation for the skipped symlink

#### Scenario: Symlink loop is skipped
- **WHEN** repository context retrieval encounters a symlink loop
- **THEN** the system skips the loop and records a limitation without failing the whole successful result unless the workspace itself is inaccessible

#### Scenario: Repository writes are not performed
- **WHEN** the Repository Context Service searches files, text, configuration, symbols, or test conventions
- **THEN** it does not modify repository files, create repository files, or install dependencies in the workspace

#### Scenario: Arbitrary execution is not required
- **WHEN** repository context retrieval needs file or text search
- **THEN** it uses approved read-only inspection behavior and does not require arbitrary command execution or default network access

### Requirement: Relevant file and search result shapes are defined
Each `relevant_files` item SHALL represent one workspace-confined file considered relevant by deterministic retrieval.

Each relevant file object MUST include:

- `path`: normalized workspace-relative path with no `..`.
- `file_kind`: controlled value such as `text`, `binary`, `unsupported_encoding`, `unreadable`, or `oversized`.
- `match_score`: deterministic numeric score where higher values rank earlier.
- `match_reasons`: ordered deduplicated array of controlled match reason values.
- `ranking_inputs`: deterministic object containing the retrieval signal counts or booleans used to compute `match_score`.
- `evidence_ref_ids`: ordered deduplicated array of evidence reference identifiers related to this file.
- `limitations`: ordered array of limitation codes specific to this file, permitted to be empty.

Each `search_results` item MUST include:

- `path`: normalized workspace-relative path with no `..`.
- `evidence_ref_id`: identifier of the evidence reference for the match.
- `match_kind`: controlled value such as `filename`, `path`, `text`, `config`, or `test_convention`.
- `locator`: bounded locator such as a line range when available, permitted to be absent for file-level matches.

Binary, unreadable, unsupported-encoding, and oversized files MUST NOT be treated as text-inspected. They MAY appear as relevant files only when deterministic non-content signals match, and they MUST include an appropriate file kind and limitation.

#### Scenario: Valid repository with file-name match
- **WHEN** a valid repository contains a file whose normalized filename matches the normalized query
- **THEN** the result includes that file in `relevant_files` with `filename_match`, deterministic ranking inputs, and an evidence reference

#### Scenario: Valid repository with text match
- **WHEN** a valid repository contains a text file whose inspected content matches the normalized query
- **THEN** the result includes a text search result with a bounded locator and related evidence reference

#### Scenario: Empty repository returns empty result
- **WHEN** a valid accessible workspace contains no inspectable repository files
- **THEN** the service returns a valid `RepositoryContextResult` with empty result arrays and a limitation indicating empty or no inspectable files

#### Scenario: No-match query returns empty result
- **WHEN** a valid repository contains files but no deterministic retrieval signal matches the query
- **THEN** the service returns a valid `RepositoryContextResult` with empty `relevant_files`, `search_results`, and `evidence_refs`, plus a no-match limitation

### Requirement: Ranking metadata and ordering are deterministic
The system SHALL rank relevant files and search results using deterministic metadata derived from reproducible repository signals.

`match_score` MUST be a deterministic numeric score where higher scores sort before lower scores.

Ranking input categories MUST be limited to deterministic signals such as:

- `filename_match`
- `path_match`
- `text_match`
- `config_match`
- `test_convention_match`
- `symbol_hint` when optional symbol hints are implemented

`match_reasons` MUST use controlled values from those ranking input categories and MUST be sorted in a stable documented order.

Relevant files MUST be ordered by:

1. descending `match_score`
2. stable ordered `match_reasons`
3. normalized workspace-relative `path` in ascending lexical order

Search results and evidence references MUST be ordered by normalized workspace-relative path, locator order when present, evidence kind, retrieval signal, and stable identifier.

Test command hints, limitations, and symbol hints when present MUST use deterministic ordering and deduplication rules.

Duplicate matches across retrieval signals MUST be merged into one relevant file entry with combined match reasons, combined ranking inputs, and deduplicated evidence reference identifiers.

Duplicate evidence references MUST be deduplicated by a stable key composed from path, evidence kind, locator, and retrieval signal.

The service MUST NOT expose broad probabilistic `confidence` or free-form `ranking_rationale` for Milestone 1.

#### Scenario: Ranking tie uses path tie-break
- **WHEN** two relevant files have equal match scores and equivalent match reasons
- **THEN** the file with the lexically earlier normalized workspace-relative path appears first

#### Scenario: Duplicate matches are merged
- **WHEN** the same file matches through filename, path, and text retrieval signals
- **THEN** the result contains one relevant file entry with deduplicated match reasons, combined ranking inputs, and deduplicated evidence reference identifiers

#### Scenario: Match score is reproducible
- **WHEN** a file is ranked as relevant
- **THEN** its `match_score` is derived from recorded deterministic `ranking_inputs`

#### Scenario: Match reasons are controlled
- **WHEN** a result explains why a file matched
- **THEN** `match_reasons` uses controlled retrieval reason values rather than free-form semantic rationale

### Requirement: Evidence references are separated from payloads
The system SHALL represent evidence through compact `evidence_refs` that identify where evidence came from and how it can be verified.

Evidence references MUST be separate from evidence payloads. Raw source snippets, full file contents, and unbounded tool output MUST NOT be embedded or persisted by default in `RepositoryContextResult`.

Each evidence reference MUST include:

- `id`: stable identifier or stable deduplication key.
- `path`: normalized workspace-relative path with no `..`.
- `evidence_kind`: controlled value such as `file_path`, `file_name`, `text_match`, `config_match`, `test_convention`, `symbol_hint`, or `diagnostic`.
- `retrieval_signal`: controlled ranking input category that produced the evidence.
- `locator`: bounded location such as line range when available, permitted to be absent for file-level evidence.
- `content_hash`: optional deterministic hash or verification metadata when content was inspected.

Evidence references MUST NOT imply that ignored, skipped, unreadable, binary, oversized, or unsupported-encoding files were text-inspected.

Source content MAY be re-read later only through an authorized workspace read path outside the default `RepositoryContextResult` payload.

#### Scenario: Evidence is inspectable without embedded source
- **WHEN** a relevant file or search result appears in `RepositoryContextResult`
- **THEN** the associated `evidence_refs` identify the path, evidence kind, retrieval signal, and bounded locator or verification metadata without embedding raw source snippets

#### Scenario: Source payloads are not default contract data
- **WHEN** repository context retrieval finds source lines that match the query
- **THEN** the result references their locations but does not persist raw source payloads by default

#### Scenario: Duplicate evidence references are deduplicated
- **WHEN** two retrieval paths produce the same evidence key
- **THEN** the result contains one evidence reference for that key and all related results point to that evidence reference identifier

### Requirement: Skipped and limited files are represented explicitly
The system SHALL represent skipped or partially inspected files through limitations without implying inspection that did not occur.

Ignored files and ignored directories MUST be excluded from scanning according to the configured deterministic ignore policy. If no project-specific ignore policy is defined, the default policy MUST be documented by implementation and applied deterministically.

Hidden directories MAY be ignored only through the configured deterministic ignore policy. The chosen policy MUST be reflected in limitations or run summary counts when hidden paths are skipped.

Oversized files MUST be skipped or partially scanned according to a deterministic configured size limit. Partial scans MUST record truncation through a limitation.

Binary files, unreadable files, unsupported encodings, symlink loops, symlink escapes, and truncated result sets MUST produce limitation entries when encountered during discovery or matching.

Limitation entries MUST include a stable code, affected workspace-relative path when applicable, and bounded detail. They MUST NOT include raw source content, host absolute paths, stack traces, or secrets.

#### Scenario: Ignored file is not inspected
- **WHEN** a file is excluded by the deterministic ignore policy
- **THEN** the file is not inspected and the result does not imply content evidence from that file

#### Scenario: Hidden directory follows ignore policy
- **WHEN** a hidden directory is skipped by the deterministic ignore policy
- **THEN** the run summary or limitations record skipped coverage without implying those files were inspected

#### Scenario: Binary file is skipped for text search
- **WHEN** a binary file is discovered during retrieval
- **THEN** the service does not perform text matching on it and records a binary-file limitation if the file affects coverage or matching

#### Scenario: Oversized file records truncation or skip
- **WHEN** a file exceeds the configured deterministic size limit
- **THEN** the service records an oversized-file or truncated-scan limitation and does not embed file content

#### Scenario: Unsupported encoding is recorded
- **WHEN** a file cannot be decoded by the supported deterministic text decoding policy
- **THEN** the service skips text inspection for that file and records an unsupported-encoding limitation

### Requirement: Test command hints are deterministic and non-executable
The system SHALL represent `test_command_hints` as descriptive repository-context hints only.

Test command hints MUST be emitted only from deterministic repository conventions such as known config files, package metadata, test directory names, or documented project configuration.

Test command hints MUST NOT be inferred through LLM reasoning and MUST NOT be executed during Milestone 1.

Each test command hint MUST include:

- `command`: descriptive command string.
- `source`: deterministic source or convention that produced the hint.
- `evidence_ref_ids`: ordered deduplicated evidence reference identifiers supporting the hint.

Test command hints MAY be empty. When present, they MUST be deduplicated by command and source, then ordered by command and source lexically.

#### Scenario: Test hint is descriptive only
- **WHEN** a deterministic repository convention suggests a test command
- **THEN** the result may include a test command hint with supporting evidence but does not execute the command

#### Scenario: Test hints may be empty
- **WHEN** no deterministic repository convention suggests a test command
- **THEN** the result contains an empty `test_command_hints` array without error

### Requirement: Symbol hints are optional and non-authoritative
The system SHALL treat `symbol_hints` as optional non-authoritative output and MAY include them only when cheap language-agnostic deterministic extraction is implemented.

Symbol hints are not required for Milestone 1 acceptance.

When present, symbol hints MUST be derived from deterministic text patterns or other cheap language-agnostic signals. They MUST NOT require LLM reasoning, language-server dependency, semantic code indexing, or root-cause inference.

When absent, the result MUST remain valid and MUST include no failure solely because symbol hints were not produced.

#### Scenario: Symbol hints absent by default
- **WHEN** deterministic symbol hint extraction is not implemented
- **THEN** the service still returns a valid `RepositoryContextResult` without requiring `symbol_hints`

#### Scenario: Symbol hints remain non-authoritative
- **WHEN** the result includes `symbol_hints`
- **THEN** those hints are represented as repository context only and do not authorize semantic relevance claims, test execution, validation, or repair behavior

### Requirement: Minimal run summary alignment is non-payload and bounded
The system SHALL include or emit minimal non-payload run-summary metadata for Milestone 1 repository context operations.

The `run_summary` field in `RepositoryContextResult` MUST include:

- `operation_type`: stable value for repository context retrieval.
- `input_summary`: deterministic summary of normalized query, issue text presence, workspace reference, and configuration identity.
- `counts`: object containing deterministic counts such as discovered files, scanned files, matched files, skipped files, evidence references, limitations, and test command hints.
- `limitation_codes`: ordered deduplicated limitation codes.
- `completion_status`: controlled value such as `completed`, `completed_with_limitations`, or `validation_error`.

The run summary MUST NOT persist raw snippets, full file contents, prompts, hidden runtime state, full tool payloads, or full DeerFlow checkpoints.

Any separate Durable Run Summary record for Milestone 1 MUST be derived from `RepositoryContextResult` and its bounded runtime metadata. It MUST preserve ForgeFlow structured contracts as authoritative product-layer state.

#### Scenario: Run summary contains counts only
- **WHEN** repository context retrieval completes
- **THEN** `run_summary` records operation type, input summary, counts, limitation codes, and completion status without raw evidence payloads

#### Scenario: Validation error summary is bounded
- **WHEN** repository context retrieval fails validation before scanning
- **THEN** any emitted summary records the validation status and stable error code without raw source content or host absolute paths

### Requirement: Evaluation fixtures cover Milestone 1 behavior
The system SHALL define controlled evaluation fixtures for Repository Context Service behavior before broad implementation.

Fixtures MUST cover deterministic file search, text search, optional symbol hints when implemented, test command hints, evidence references, workspace boundary enforcement, ranking metadata, skipped files, empty results, validation errors, and explicit exclusions.

Fixtures MUST NOT require patch generation, code editing, test execution, review automation, PR creation, memory access, workflow graph implementation, or full DeerFlow runtime integration.

#### Scenario: Fixture verifies deterministic ranking
- **WHEN** a fixture repository and query are evaluated
- **THEN** expected relevant files, match reasons, ranking inputs, evidence references, and limitations can be compared reproducibly

#### Scenario: Fixture verifies workspace boundary
- **WHEN** a fixture contains a symlink or path reference that would escape the workspace root
- **THEN** evaluation verifies the escaped target is not read and the limitation or diagnostic is recorded

#### Scenario: Fixture verifies exclusions
- **WHEN** a fixture query suggests an obvious code fix or test command
- **THEN** evaluation verifies the service returns context and hints only, without producing patches or executing tests

#### Scenario: Fixture verifies empty and skipped cases
- **WHEN** fixtures include empty repositories, no-match queries, ignored files, binary files, oversized files, unreadable files, and unsupported encodings
- **THEN** evaluation verifies each case produces the specified valid empty result, limitation, or structured validation error
