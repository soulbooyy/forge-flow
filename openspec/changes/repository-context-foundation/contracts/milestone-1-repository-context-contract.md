# Milestone 1 Contract Design: Repository Context Foundation

## Purpose

This document defines the minimal stable contract layer for Milestone 1 Repository Context Foundation. It translates the accepted OpenSpec, RFC, and ADR decisions into an implementation-independent contract reference.

The contract is:

- deterministic repository context evidence
- an immutable result artifact
- a bounded serializable payload
- auditable and fixture-testable

The contract is not:

- agent state
- workflow state
- runtime trace
- authorization object
- persistence object
- planning object

## Source of Truth

Authoritative constraints come from:

- `openspec/changes/repository-context-foundation`
- RFC-001 Agent Architecture
- RFC-002 Contracts and State Model
- RFC-004 Sandbox and Security Governance
- RFC-007 DeerFlow Extension Strategy
- ADR-001 through ADR-006

When this document conflicts with the accepted OpenSpec, the OpenSpec controls.

## Tagged Envelope Union

Repository Context returns exactly one envelope:

```text
RepositoryContextEnvelope =
    RepositoryContextResult
  | RepositoryContextValidationError
```

Success uses:

```json
{ "result_type": "repository_context_result" }
```

Validation failure uses:

```json
{ "result_type": "repository_context_validation_error" }
```

Validation errors are not `RepositoryContextResult` objects. They must not contain `contract_id`, `relevant_files`, `search_results`, `evidence_refs`, `test_command_hints`, or successful-result `limitations`.

## Proposed Schema Structure

### RepositoryContextResult

Required fields:

- `schema_version`: string
- `result_type`: `"repository_context_result"`
- `contract_id`: `rcr_sha256:<hex>`
- `workspace_ref`: `WorkspaceRef`
- `query`: `NormalizedInput`
- `issue_text`: `BoundedOptionalInput`
- `relevant_files`: `RelevantFile[]`
- `search_results`: `SearchResult[]`
- `test_command_hints`: `TestCommandHint[]`
- `evidence_refs`: `EvidenceRef[]`
- `limitations`: `Limitation[]`
- `run_summary`: `RunSummary`

Rules:

- immutable after creation
- context/evidence only
- non-authorizing
- no `runtime_metadata`
- no raw source content
- no raw file contents
- no raw snippets
- no host absolute paths
- no timestamps
- no process identifiers
- no stack traces
- no runtime trace records
- no persistence metadata

### RepositoryContextValidationError

Required fields:

- `schema_version`: string
- `result_type`: `"repository_context_validation_error"`
- `error_id`: `rce_sha256:<hex>`
- `completion_status`: `"validation_error"`
- `error_code`: string
- `input_category`: string
- `message`: bounded user-safe string
- `summary`: `ValidationErrorSummary`

Optional fields:

- `input_ref`: bounded redacted reference

Rules:

- no `contract_id`
- no successful-result arrays
- no raw source content
- no full raw user input
- no host absolute paths
- no stack traces
- no runtime metadata

### WorkspaceRef

Required fields:

- `root_id`: caller-supplied logical workspace identity

Optional fields:

- `source_ref`: bounded caller-provided repository or fixture reference

Rules:

- participates in `contract_id`
- appears in deterministic input summary
- must not be derived from host absolute paths, timestamps, filesystem metadata, machine identity, or repository contents
- must be safe to persist

### NormalizedInput

Recommended fields for `query`:

- `normalized`: bounded normalized value
- `raw_ref`: optional caller-provided reference to raw input

Rules:

- query is the sole retrieval driver
- normalized query is non-empty
- oversized query is a validation error
- raw query is not embedded by default

### BoundedOptionalInput

Recommended fields for `issue_text`:

- `present`: boolean
- `normalized`: bounded normalized value, empty when absent
- `truncated`: boolean
- `raw_ref`: optional caller-provided reference to raw input

Rules:

- issue text is bounded context only
- does not affect retrieval
- does not affect ranking
- does not create search results
- does not create evidence refs
- full raw issue text is not embedded

### RelevantFile

Required fields:

- `path`: canonical workspace-relative path
- `file_kind`: string
- `ranking_inputs`: `RankingInputs`
- `match_score`: integer
- `match_reasons`: string[]
- `evidence_ref_ids`: string[]
- `limitation_codes`: string[]

Rules:

- means "a file with deterministic relevance evidence"
- not "every file encountered"
- appears only if discovered safely, not excluded before matching, and has at least one positive ranking reason
- ignored files and directories do not appear
- symlink entries do not appear
- file identity is canonical workspace-relative path only

### RankingInputs

Required fields:

- `filename_match`: boolean
- `path_match`: boolean
- `text_match_count`: integer

Rules:

- the only ranking inputs allowed in Milestone 1
- `match_score` must be recomputable from these fields alone
- `match_reasons` is a deterministic projection of these fields
- no independent authoring

Forbidden ranking inputs:

- `config_match`
- `test_convention_match`
- `symbol_hint`
- semantic relevance
- issue-text signals
- LLM-derived signals
- AST or language-server signals

### SearchResult

Required fields:

- `path`: canonical workspace-relative path
- `locator`: `TextLocator`
- `evidence_ref_id`: string

Rules:

- only represents text-match results
- must not represent filename matches, path matches, config matches, or test hints
- every `evidence_ref_id` must resolve to an item in `evidence_refs`

### TestCommandHint

Required fields:

- `command`: canonical descriptive command
- `source`: canonical source path
- `evidence_ref_ids`: string[]

Rules:

- descriptive only
- never executed
- does not affect `match_score`
- does not affect relevant-file ordering
- does not authorize validation execution
- root `package.json` may emit `npm test`
- root `Makefile` may emit `make test`

### EvidenceRef

Required fields:

- `id`: `ev_sha256:<hex>`
- `path`: canonical workspace-relative path or omitted for non-path evidence
- `evidence_kind`: string
- `retrieval_signal`: string
- `locator`: `TextLocator | null`

Optional fields:

- `content_hash`: `ContentHash`
- `hash_scope`: `"full_inspected_text" | "truncated_inspected_range"`

Rules:

- references evidence, not raw evidence payload
- deterministic identity is derived from canonical evidence key with `id` omitted
- evidence key includes canonical path, evidence kind, retrieval signal, locator when present, and content hash when present
- no raw snippets
- no runtime data
- no host paths

### TextLocator

Required fields:

- `start_line`: integer
- `end_line`: integer

Rules:

- 1-based line numbers
- inclusive ranges
- no columns
- text matches require locator
- file-level evidence uses `locator: null`
- multiple matches on the same line collapse to one locator

### ContentHash

Required fields:

- `algorithm`: `"sha256"`
- `value`: lowercase hex string

Rules:

- verification metadata only
- not raw payload
- not secret scanning
- not proof that content is secret-free
- emitted only for inspected text evidence

### Limitation

Required fields:

- `code`: stable limitation code
- `scope`: `"input" | "workspace" | "directory" | "file" | "result"`
- `detail`: bounded safe string or bounded structured object

Optional fields:

- `path`: canonical workspace-relative path
- `count`: deterministic integer
- `related_evidence_ref_ids`: string[]

Initial codes:

- `empty_repository`
- `no_matches`
- `ignored_path`
- `binary_file_skipped`
- `oversized_file_skipped`
- `file_scan_truncated`
- `result_set_truncated`
- `unreadable_file`
- `unsupported_encoding`
- `symlink_escape`
- `symlink_loop`
- `path_escape`
- `incomplete_coverage`
- `issue_text_truncated`
- `malformed_metadata`

Rules:

- limitations are successful-result coverage boundaries
- limitations are not validation errors
- ordered by code, scope order, absent path before present path, canonical path, then deterministic tie-break fields
- `result_set_truncated` is one grouped result-level limitation when any result cap drops valid candidates

### RunSummary

Required fields:

- `operation_type`: `"repository_context"`
- `completion_status`: `"completed" | "completed_with_limitations"`
- `input_summary`: `InputSummary`
- `counts`: `RunCounts`
- `limitation_codes`: string[]

Rules:

- part of the successful result
- mechanically derivable from deterministic payload and configuration identity
- not a production trace system
- not a runtime execution record

### InputSummary

Required fields:

- `workspace_root_id`: string
- `configuration_profile_id`: `"repository-context/m1-defaults-v1"`
- `query_normalized`: bounded string
- `issue_text_present`: boolean
- `issue_text_truncated`: boolean
- `normalization_id`: string
- `limit_profile_id`: string
- `ignore_policy_id`: string

Rules:

- no host absolute paths
- no full raw issue text
- no runtime values

### RunCounts

Required fields:

- `discovered_files`: integer
- `discovered_directories`: integer
- `scanned_text_files`: integer
- `skipped_files`: integer
- `skipped_directories`: integer
- `candidates`: `CandidateCounts`
- `returned`: `ReturnedCounts`

`CandidateCounts` fields:

- `relevant_files`
- `search_results`
- `evidence_refs`
- `test_command_hints`

`ReturnedCounts` fields:

- `relevant_files`
- `search_results`
- `evidence_refs`
- `test_command_hints`
- `limitations`

Rules:

- returned counts equal returned array lengths
- candidate counts distinguish pre-cap results from returned arrays

## Identity and Canonical Serialization

### Canonical JSON

Canonical JSON uses:

- UTF-8 JSON bytes
- object keys sorted lexicographically
- deterministic array ordering
- no insignificant whitespace
- JSON booleans
- integer values for counts, scores, limits, and line numbers
- required empty collections included
- absent optional fields omitted instead of serialized as `null`, unless the field explicitly requires `null`
- no floating-point values

### Contract ID

`contract_id` format:

```text
rcr_sha256:<lowercase-hex-sha256>
```

Hash input:

- canonical deterministic `RepositoryContextResult` payload
- `contract_id` omitted

Included identity facts:

- schema version
- `result_type`
- workspace identity
- configuration identity
- normalized bounded inputs
- relevant files
- search results
- evidence refs
- test command hints
- limitations
- deterministic run-summary counts
- limitation summaries

Changes that must change `contract_id`:

- evidence changes
- ranking changes
- limitation changes
- truncation changes
- ignored or skipped coverage changes
- deterministic count changes
- configuration profile changes

### Evidence ID

`EvidenceRef.id` format:

```text
ev_sha256:<lowercase-hex-sha256>
```

Hash input:

- canonical evidence key
- `id` omitted

Canonical evidence key fields:

- canonical workspace-relative path when present
- evidence kind
- retrieval signal
- locator when present
- content hash when present

### Error ID

`error_id` format:

```text
rce_sha256:<lowercase-hex-sha256>
```

Hash input:

- canonical validation error envelope
- `error_id` omitted

## Contract Invariants

- Exactly one envelope type is returned.
- `result_type` is required in both envelopes.
- Validation errors are never partial successful results.
- Successful results are immutable after creation.
- Successful results are non-authorizing context/evidence only.
- `contract_id`, `error_id`, and `EvidenceRef.id` exclude themselves from their own hash inputs.
- All returned paths are canonical workspace-relative paths.
- Host absolute paths never appear in outputs.
- Query is the sole retrieval driver.
- Issue text is bounded context only.
- `search_results` contain only text matches.
- `ranking_inputs` contains only `filename_match`, `path_match`, and `text_match_count`.
- `match_score` is recomputable from `ranking_inputs`.
- `match_reasons` is derived from `ranking_inputs`.
- Every evidence reference ID used by relevant files, search results, or test hints resolves to a returned `EvidenceRef`.
- Returned counts equal returned array lengths.
- Limitations describe successful-result coverage boundaries only.
- No raw repository content, raw snippets, command output, runtime metadata, or unbounded raw user input appears in either envelope.

## Example Successful RepositoryContextResult

```json
{
  "contract_id": "rcr_sha256:1111111111111111111111111111111111111111111111111111111111111111",
  "evidence_refs": [
    {
      "content_hash": {
        "algorithm": "sha256",
        "value": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
      },
      "evidence_kind": "file_text_match",
      "hash_scope": "full_inspected_text",
      "id": "ev_sha256:2222222222222222222222222222222222222222222222222222222222222222",
      "locator": {
        "end_line": 12,
        "start_line": 12
      },
      "path": "src/context.py",
      "retrieval_signal": "text_match"
    },
    {
      "content_hash": {
        "algorithm": "sha256",
        "value": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
      },
      "evidence_kind": "file_path_match",
      "hash_scope": "full_inspected_text",
      "id": "ev_sha256:3333333333333333333333333333333333333333333333333333333333333333",
      "locator": null,
      "path": "src/repository_context.py",
      "retrieval_signal": "path_match"
    }
  ],
  "issue_text": {
    "normalized": "",
    "present": false,
    "truncated": false
  },
  "limitations": [],
  "query": {
    "normalized": "repository context"
  },
  "relevant_files": [
    {
      "evidence_ref_ids": [
        "ev_sha256:3333333333333333333333333333333333333333333333333333333333333333"
      ],
      "file_kind": "text",
      "limitation_codes": [],
      "match_reasons": [
        "path_match"
      ],
      "match_score": 50,
      "path": "src/repository_context.py",
      "ranking_inputs": {
        "filename_match": false,
        "path_match": true,
        "text_match_count": 0
      }
    },
    {
      "evidence_ref_ids": [
        "ev_sha256:2222222222222222222222222222222222222222222222222222222222222222"
      ],
      "file_kind": "text",
      "limitation_codes": [],
      "match_reasons": [
        "text_match"
      ],
      "match_score": 25,
      "path": "src/context.py",
      "ranking_inputs": {
        "filename_match": false,
        "path_match": false,
        "text_match_count": 1
      }
    }
  ],
  "result_type": "repository_context_result",
  "run_summary": {
    "completion_status": "completed",
    "counts": {
      "candidates": {
        "evidence_refs": 2,
        "relevant_files": 2,
        "search_results": 1,
        "test_command_hints": 0
      },
      "discovered_directories": 2,
      "discovered_files": 3,
      "returned": {
        "evidence_refs": 2,
        "limitations": 0,
        "relevant_files": 2,
        "search_results": 1,
        "test_command_hints": 0
      },
      "scanned_text_files": 3,
      "skipped_directories": 0,
      "skipped_files": 0
    },
    "input_summary": {
      "configuration_profile_id": "repository-context/m1-defaults-v1",
      "ignore_policy_id": "m1-default-ignore-v1",
      "issue_text_present": false,
      "issue_text_truncated": false,
      "limit_profile_id": "m1-default-limits-v1",
      "normalization_id": "m1-nfc-trim-collapse-casefold-v1",
      "query_normalized": "repository context",
      "workspace_root_id": "fixture-basic-context"
    },
    "limitation_codes": [],
    "operation_type": "repository_context"
  },
  "schema_version": "repository-context-result/v1",
  "search_results": [
    {
      "evidence_ref_id": "ev_sha256:2222222222222222222222222222222222222222222222222222222222222222",
      "locator": {
        "end_line": 12,
        "start_line": 12
      },
      "path": "src/context.py"
    }
  ],
  "test_command_hints": [],
  "workspace_ref": {
    "root_id": "fixture-basic-context",
    "source_ref": "openspec-fixture:basic-context"
  }
}
```

The example IDs are placeholders showing format only. Real IDs must be computed from canonical payloads.

## Example Validation Error

```json
{
  "completion_status": "validation_error",
  "error_code": "empty_query",
  "error_id": "rce_sha256:4444444444444444444444444444444444444444444444444444444444444444",
  "input_category": "query",
  "message": "Query must contain a non-empty normalized value.",
  "result_type": "repository_context_validation_error",
  "schema_version": "repository-context-validation-error/v1",
  "summary": {
    "configuration_profile_id": "repository-context/m1-defaults-v1",
    "query_present": true,
    "workspace_root_id": "fixture-basic-context"
  }
}
```

The example `error_id` is a placeholder showing format only. A real `error_id` must be computed from the canonical validation error payload with `error_id` omitted.

## Intentionally Excluded Fields

The contract intentionally excludes:

- `runtime_metadata`
- timestamps
- process identifiers
- execution duration
- host absolute paths
- stack traces
- environment variables
- raw source content
- raw file contents
- raw snippets
- raw command output
- unbounded raw query
- full raw issue text
- agent state
- planner state
- patch state
- validation state
- review state
- PR state
- memory state
- DeerFlow runtime state
- production persistence metadata
- authorization decisions
- policy decision records
- branch or commit state
- network side-effect records

## Design Choices

### Separate validation envelope instead of partial result

Validation failures are a distinct envelope so callers cannot mistake invalid input for successful repository inspection. This keeps failure identity and successful contract identity separate.

### Bounded issue text inside the contract

Issue text is represented as bounded context because it may help later stages understand input provenance, but it does not drive retrieval in Milestone 1. This prevents query expansion, issue analysis, and semantic ranking from entering the foundation slice.

### Evidence refs instead of snippets

Evidence refs preserve auditability through paths, locators, IDs, and hashes without embedding raw repository payloads. This aligns with the privacy and persistence boundary in ADR-006.

### Limitation codes on RelevantFile

`RelevantFile.limitation_codes` is a compact projection for local file awareness. The authoritative limitation objects remain in the top-level `limitations` array.

### RunSummary inside RepositoryContextResult

`run_summary` is included because deterministic counts and completion status participate in the contract identity. It is not a separate runtime tracing system.

### Placeholder IDs in examples

Examples use fixed placeholder hashes for readability. Acceptance fixtures must compute and compare real IDs using canonical serialization.

