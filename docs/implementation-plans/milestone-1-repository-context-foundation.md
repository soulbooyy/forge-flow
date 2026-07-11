# Milestone 1 Implementation Plan: Repository Context Foundation

## 1. Implementation Goals

Milestone 1 delivers a deterministic Repository Context Service that produces either:

- `RepositoryContextResult`
- `RepositoryContextValidationError`

The exact deliverable is a read-only repository-context capability that accepts a workspace, caller-supplied `workspace_ref.root_id`, `configuration_profile_id`, query, and optional issue text, then returns deterministic bounded context and evidence references.

Included:

- schema models for success and validation envelopes
- canonical JSON serialization
- `contract_id`, `evidence_ref.id`, and `error_id` generation
- workspace-confined read-only filesystem inspection
- canonical path normalization
- symlink boundary enforcement
- fixed ignore policy
- strict UTF-8 text inspection
- binary, unsupported, oversized, and unreadable file handling
- query normalization
- filename, path, and line-based text matching
- deterministic ranking
- evidence refs, locators, and content hashes
- text-only `search_results`
- root-only descriptive test command hints
- limitations and run summary
- deterministic fixtures and acceptance tests

Excluded:

- commands, subprocesses, Git commands, `rg`, `grep`, or `find`
- network access
- dependency installation
- test execution
- validation planning
- patch generation
- code editing
- branch, commit, or PR creation
- memory reads or writes
- production persistence or lookup APIs
- DeerFlow runtime integration or core modification
- role agents
- LLM, embedding, semantic, AST, symbol, or language-server analysis

## 2. Implementation Phases

### Phase 1: Project Structure and Contracts

Implement:

- `RepositoryContextResult` schema
- validation error envelope schema
- limitation schema and stable codes
- evidence ref schema
- relevant file, search result, test hint, and run summary models
- canonical serialization
- hash ID generation:
  - `rcr_sha256:<hex>`
  - `ev_sha256:<hex>`
  - `rce_sha256:<hex>`

Allowed:

- pure data models
- schema validation
- canonical JSON helpers
- deterministic hash helpers

Forbidden:

- filesystem scanning
- repository reads
- runtime tracing system
- persistence
- DeerFlow integration

### Phase 2: Workspace Boundary Layer

Implement:

- workspace input validation
- required caller-supplied `workspace_ref.root_id`
- required `configuration_profile_id`
- initial allowed profile: `repository-context/m1-defaults-v1`
- canonical workspace-relative path formatting
- path escape prevention
- symlink escape and loop detection
- fixed ignore policy:
  - `.git/`
  - `.forgeflow/cache/`
  - `.forgeflow/artifacts/`
  - `openspec/changes/*/fixtures/output/`

Allowed:

- direct filesystem metadata reads
- path normalization
- symlink authorization checks

Forbidden:

- shell commands
- Git APIs or Git commands
- `.gitignore` semantics
- network access
- repository writes

### Phase 3: Deterministic Scanner

Implement:

- deterministic traversal
- file and directory counting
- skipped file and skipped directory counting
- binary detection by NUL byte
- strict UTF-8 decoding
- UTF-8 BOM removal
- CRLF/CR to LF normalization
- bounded file reads
- oversized file handling
- unsupported encoding handling
- unreadable file limitations
- file scan truncation limitations

Allowed:

- workspace-confined direct filesystem reads
- bounded text inspection
- deterministic limitations

Forbidden:

- external tools
- language-specific parsing
- dependency installation
- hidden ecosystem ignore rules
- raw snippet persistence

### Phase 4: Retrieval Engine

Implement:

- query normalization:
  - NFC
  - trim
  - whitespace collapse
  - casefolded matching view
- issue text normalization as bounded context only
- filename matching
- path matching
- line-based text substring matching
- same-line duplicate collapse
- `ranking_inputs`
- `match_score`
- derived `match_reasons`
- deterministic ordering

Allowed:

- direct filename, path, and text evidence
- fixed score formula
- path tie-breakers

Forbidden:

- issue-text-driven retrieval
- `config_match`
- `test_convention_match`
- `symbol_hint`
- semantic ranking
- LLM relevance
- AST or language-server analysis

### Phase 5: Evidence Construction

Implement:

- canonical evidence keys
- `evidence_ref.id`
- text locators:
  - 1-based lines
  - inclusive ranges
  - no columns
- file-level evidence with `locator: null`
- inspected-text `content_hash`
- hash coverage metadata
- text-only `search_results`
- no dangling evidence references

Allowed:

- evidence references
- locators
- content hashes as verification metadata

Forbidden:

- raw snippets
- full file contents
- host absolute paths
- command output
- runtime metadata

### Phase 6: Result Assembly

Implement:

- relevant files
- evidence refs
- search results
- root-only test command hints:
  - root `package.json` to `npm test`
  - root `Makefile` to `make test`
- limitations ordering
- candidate vs returned counts
- result caps
- grouped `result_set_truncated`
- `run_summary`
- `completion_status`
- final `contract_id`

Allowed:

- bounded deterministic output
- immutable result construction
- validation error construction

Forbidden:

- executing test hints
- production storage
- durable lookup APIs
- policy decisions
- validation execution

### Phase 7: Acceptance Tests

Implement fixtures and tests for:

- schema validation
- canonical IDs
- repeated deterministic execution
- validation error envelopes
- query normalization
- issue-text bounding
- path normalization
- ignore policy
- symlink escape and loop handling
- binary, unsupported, oversized, and unreadable files
- line-based text matching
- same-line duplicate collapse
- ranking and tie-breaking
- evidence refs and content hashes
- text-only search results
- test command hints
- truncation and candidate vs returned counts
- no dangling refs
- payload avoidance
- side-effect absence

Allowed:

- fixture repositories
- expected outputs
- canonical comparison helpers
- workspace before/after snapshots

Forbidden:

- using tests to execute repository test commands
- generating patches
- mutating fixture workspaces
- relying on network or external tools

## 3. Suggested Module Boundaries

Recommended structure, adjusted if the repository already has a stronger convention:

```text
repository_context/
    __init__.py
    models.py
    errors.py
    limits.py
    identity.py
    canonical_json.py
    normalization.py
    workspace.py
    scanner.py
    matcher.py
    ranking.py
    evidence.py
    test_hints.py
    result_builder.py
    service.py
```

Module responsibilities:

- `models.py`: success envelope, validation envelope, nested contract types
- `errors.py`: validation error codes and construction helpers
- `limits.py`: `repository-context/m1-defaults-v1` constants
- `canonical_json.py`: canonical serialization
- `identity.py`: `contract_id`, `evidence_ref.id`, `error_id`
- `normalization.py`: query, issue text, path, and text matching normalization
- `workspace.py`: root validation, path confinement, symlink checks, ignore policy
- `scanner.py`: traversal, file classification, bounded text reads, scan limitations
- `matcher.py`: filename/path/text matching
- `ranking.py`: ranking inputs, score calculation, match reasons, ordering
- `evidence.py`: evidence refs, locators, content hashes, search results
- `test_hints.py`: root-only `package.json` and `Makefile` hints
- `result_builder.py`: caps, counts, limitations, run summary, final assembly
- `service.py`: public Repository Context Service entry point

## 4. Dependency Order

Build in this order:

```text
models / limits / canonical_json
    |
identity
    |
normalization
    |
workspace boundary
    |
scanner
    |
matcher
    |
ranking
    |
evidence
    |
test_hints
    |
result_builder
    |
service
    |
acceptance fixtures
```

Acceptance skeletons should be introduced early, before scanner and service behavior becomes de facto contract.

## 5. First Implementation Milestone

Smallest vertical slice:

Input:

- valid workspace root
- caller-supplied `workspace_ref.root_id`
- `configuration_profile_id: repository-context/m1-defaults-v1`
- query

Fixture:

- one tiny workspace
- one file matching by filename
- one file matching by text
- one non-matching file

Output:

- successful `RepositoryContextResult`
- deterministic `relevant_files`
- text-only `search_results`
- evidence refs with locators and content hash
- fixed `ranking_inputs`
- recomputable `match_score`
- deterministic `run_summary`
- stable `contract_id`

Also include one validation fixture:

- empty query to validation error envelope with stable `error_id`

## 6. Risks

- Accidental scope expansion into agents, validation planning, patches, PRs, or DeerFlow runtime.
- Contract drift if implementation choices appear before fixture expectations.
- Nondeterministic filesystem traversal or path ordering.
- Hidden reliance on Git, shell tools, `.gitignore`, or platform-specific behavior.
- Raw payload leakage through snippets, errors, logs, or debug fields.
- Confusing test command hints with executable validation plans.
- Treating `contract_id` as production persistence infrastructure.
- Letting issue text become implicit query expansion.
- Result caps causing dangling evidence references.
- Symlink handling accidentally exposing target content or alternate file identity.
