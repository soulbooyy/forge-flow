# Milestone 1 Implementation Plan: Repository Context Foundation

## 0. Plan Reconciliation

This plan is the reconciled execution authority for Milestone 1. It preserves
the OpenSpec scope while aligning phase numbering with accepted implementation
history:

- Phase 1 is Contract Foundation (`fd9813f`).
- Phase 2 is Canonical Identity (`9fa68b8`).
- Phase 3 is Workspace Security (`4b77b81`).
- Phase 4 is Deterministic Scanner (`14e9bae`).

The former plan combined contract and canonical identity work in Phase 1 and
therefore numbered workspace and scanner work one phase earlier. This
reconciliation changes planning and progress terminology only; it does not
rewrite historical commits or alter OpenSpec requirements.

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

### Phase 1: Contract Foundation

Implement:

- `RepositoryContextResult` schema
- validation error envelope schema
- limitation schema and stable codes
- evidence ref schema
- relevant file, search result, test hint, and run summary models
- immutable `repository-context/m1-defaults-v1` profile

Allowed:

- pure data models
- package and public-export setup

Forbidden:

- filesystem scanning
- repository reads
- runtime tracing system
- persistence
- DeerFlow integration

### Phase 2: Canonical Identity

Implement:

- deterministic canonical UTF-8 JSON serialization
- stable object-key ordering and compact serialization
- SHA-256 helper
- stable ID generation:
  - `rcr_sha256:<hex>` for results
  - `ev_sha256:<hex>` for evidence refs
  - `rce_sha256:<hex>` for validation errors
- identity-field omission without mutation

Allowed:

- pure canonicalization and hash helpers
- immutable contract values

Forbidden:

- workspace access or path validation
- scanner, matcher, ranking, evidence construction, or service behavior
- timestamps, random values, machine paths, or runtime state

### Phase 3: Workspace Security

Implement:

- workspace input validation
- required caller-supplied `workspace_ref.root_id`
- canonical workspace-relative path formatting
- path escape prevention
- symlink escape prevention

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

### Phase 4: Deterministic Scanner

Implement:

- deterministic traversal
- file and directory counting
- skipped file and skipped directory counting
- fixed ignore policy:
  - `.git/`
  - `.forgeflow/cache/`
  - `.forgeflow/artifacts/`
  - `openspec/changes/*/fixtures/output/`
- binary detection by NUL byte
- strict UTF-8 decoding
- UTF-8 BOM removal
- CRLF/CR to LF normalization
- bounded file reads
- oversized file handling
- unsupported encoding handling
- deterministic `text_truncated` classification

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

### Phase 5: Matcher, Ranking, and Evidence

Before Phase 5 production code, establish the minimum acceptance-fixture
foundation required by the OpenSpec:

- create one controlled workspace fixture with filename/path, text-only, and
  non-matching files;
- create expected matching and evidence contract fragments without raw source
  payloads;
- add an acceptance-style matching/evidence skeleton that fails because the
  Phase 5 public matching surface is absent;
- keep the skeleton independent of the future service and result-envelope
  assembly work in Phase 6.

These fixture and skeleton artifacts are a Phase 5 TDD precondition. They make
retrieval behavior contract-testable before matcher, ranking, and evidence
production code is introduced. Phase 7 expands this foundation into complete
end-to-end acceptance coverage.

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
- canonical evidence keys and `evidence_ref.id`
- text locators with 1-based inclusive line ranges and no columns
- file-level evidence with `locator: null`
- inspected-text `content_hash` and hash coverage metadata
- text-only `search_results`
- no dangling evidence references

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

### Phase 6: Result Envelope and Service

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
- `configuration_profile_id` validation for `repository-context/m1-defaults-v1`
- validation error construction and deterministic validation precedence
- public Repository Context Service entry point

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

Expand the Phase 5 fixture and skeleton foundation into complete end-to-end
acceptance coverage for:

- schema validation
- canonical IDs
- repeated deterministic execution
- validation error envelopes
- query normalization
- issue-text bounding
- path normalization
- ignore policy
- symlink escape and loop handling
- binary, unsupported, and oversized files
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

### Phase 8: Hardening

Implement only the remaining deterministic and security hardening identified by
Phase 1-7 acceptance results. This includes unreadable-file and line-limit
scanner behavior, platform-specific path behavior, stable limitation ordering,
and regression coverage for previously fixed defects.

Allowed:

- narrowly scoped robustness fixes and regression tests
- documentation reconciliation required by verified implementation facts

Forbidden:

- new feature scope, external dependencies, agents, workflows, network,
  subprocesses, Git/PR behavior, memory, LLMs, embeddings, ASTs, or semantic
  search

## 3. Suggested Module Boundaries

Recommended structure, adjusted if the repository already has a stronger convention:

```text
repository_context/
    __init__.py
    models.py
    profile.py
    canonical.py
    workspace.py
    scanner.py
    normalization.py
    matching.py
    evidence.py
    hints.py
    assembly.py
    validation.py
    service.py
```

Module responsibilities:

- `models.py`: success envelope, validation envelope, nested contract types
- `profile.py`: `repository-context/m1-defaults-v1` constants
- `canonical.py`: canonical serialization and stable identities
- `normalization.py`: query, issue text, path, and text matching normalization
- `workspace.py`: root validation, path confinement, and symlink checks
- `scanner.py`: traversal, file classification, and bounded text reads
- `matching.py`: filename/path/text matching, ranking inputs, score calculation, match reasons, and ordering
- `evidence.py`: evidence refs, locators, content hashes, search results
- `hints.py`: root-only `package.json` and `Makefile` hints
- `assembly.py`: caps, counts, limitations, run summary, final assembly
- `validation.py`: deterministic validation-error construction
- `service.py`: public Repository Context Service entry point

## 4. Dependency Order

Build in this order:

```text
models / profile
    |
canonical identity
    |
workspace boundary
    |
scanner
    |
acceptance fixture and matching/evidence skeleton
    |
normalization / matching / ranking / evidence
    |
validation / hints / result assembly / service
    |
acceptance fixtures
    |
hardening
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
