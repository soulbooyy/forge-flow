# Repository Context Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a deterministic, read-only Repository Context Service that returns either an immutable `RepositoryContextResult` or a separate `RepositoryContextValidationError` for the Milestone 1 contract.

**Architecture:** Implement a ForgeFlow-owned Python package under `src/forgeflow/repository_context` with no DeerFlow or command-runtime dependency. Pure immutable contract models and canonical identity helpers sit at the center; a workspace-confined filesystem scanner feeds deterministic matching, evidence construction, ranking, capping, and final result assembly. Contract fixtures live with the accepted OpenSpec, while executable tests live under `tests/repository_context` and drive each layer from the public service boundary.

**Tech Stack:** Python 3.12 standard library (`dataclasses`, `enum`, `hashlib`, `json`, `pathlib`, `unicodedata`), `unittest`, `pyproject.toml` packaging, OpenSpec CLI for specification validation when available.

## Global Constraints

- The only configuration profile is `repository-context/m1-defaults-v1`.
- Success schema version is `repository-context-result/v1`; validation schema version is `repository-context-validation-error/v1`.
- Canonical IDs use `rcr_sha256:<lowercase-hex>`, `ev_sha256:<lowercase-hex>`, and `rce_sha256:<lowercase-hex>`.
- Query normalization is Unicode NFC, trim, collapse whitespace to one ASCII space, then Unicode casefold for matching; normalized query length is 1 through 512 Unicode scalar values.
- Retained normalized issue text is capped at 4,096 Unicode scalar values and never drives retrieval, ranking, evidence, or no-match behavior.
- Maximum inspected text per file is 1,048,576 bytes and maximum scanned lines per file is 20,000.
- Text matches are casefolded line-local substring matches; duplicate occurrences on one line collapse to one 1-based inclusive locator.
- Ranking is exactly filename `100`, path `50`, and `25` per text locator, capped at 20 locators per file; ties use canonical path ascending.
- Returned caps are 50 relevant files, 200 search results, 300 evidence refs, and 10 test command hints.
- Ignore exactly `.git/`, `.forgeflow/cache/`, `.forgeflow/artifacts/`, and `openspec/changes/*/fixtures/output/`; do not honor `.gitignore` or ecosystem defaults.
- Inspect only through direct, workspace-confined filesystem APIs. No shell, subprocess, Git, search command, package manager, language server, network, dependency installation, test-command execution, memory API, or external side-effect tool may be called by the service.
- Returned paths are observed-case, `/`-separated, workspace-relative canonical paths with no leading slash, empty segment, `.`, `..`, duplicate separator, or host path.
- Symlinks are traversal-control entries only: never rank or read target content, and represent loops or escapes as deterministic limitations.
- Contracts contain references, locators, and verification hashes only; no raw snippet, full file, host absolute path, timestamp, duration, process data, environment data, stack trace, or runtime metadata.
- Result objects are frozen, deterministic, non-authorizing, and not production-persisted. Validation errors never contain partial success fields.
- Agents, workflows, orchestration, DeerFlow integration, patches, validation execution, Git/PR behavior, memory, LLMs, embeddings, ASTs, symbols, and semantic ranking remain out of scope.

---

## File Structure

```text
pyproject.toml
src/forgeflow/__init__.py
src/forgeflow/repository_context/__init__.py
src/forgeflow/repository_context/models.py
src/forgeflow/repository_context/profile.py
src/forgeflow/repository_context/canonical.py
src/forgeflow/repository_context/validation.py
src/forgeflow/repository_context/normalization.py
src/forgeflow/repository_context/workspace.py
src/forgeflow/repository_context/scanner.py
src/forgeflow/repository_context/matching.py
src/forgeflow/repository_context/evidence.py
src/forgeflow/repository_context/hints.py
src/forgeflow/repository_context/assembly.py
src/forgeflow/repository_context/service.py
tests/repository_context/test_contracts.py
tests/repository_context/test_validation.py
tests/repository_context/test_workspace.py
tests/repository_context/test_scanner.py
tests/repository_context/test_matching.py
tests/repository_context/test_assembly.py
tests/repository_context/test_acceptance.py
tests/repository_context/support.py
openspec/changes/repository-context-foundation/fixtures/workspaces/basic-context/src/payment_handler.py
openspec/changes/repository-context-foundation/fixtures/workspaces/basic-context/docs/payment-notes.txt
openspec/changes/repository-context-foundation/fixtures/workspaces/basic-context/README.md
openspec/changes/repository-context-foundation/fixtures/expected/basic-context/result.json
openspec/changes/repository-context-foundation/fixtures/expected/empty-query/error.json
```

Responsibilities are deliberately narrow: `models.py` owns immutable payload types, `profile.py` owns all versioned defaults, `canonical.py` owns serialization and hashes, `validation.py` owns input-to-error conversion, `workspace.py` owns confinement and ignore decisions, `scanner.py` owns bounded reads, `matching.py` owns direct signals and score calculation, `evidence.py` owns references and locators, `hints.py` owns root-only descriptive hints, `assembly.py` owns graph-consistent caps/counts/limitations, and `service.py` is the only public orchestration entry point.

## Implementation Phases

### Phase 1: Package Foundation and Immutable Contract Models

**Files:**
- Create: `pyproject.toml`
- Create: `src/forgeflow/__init__.py`
- Create: `src/forgeflow/repository_context/__init__.py`
- Create: `src/forgeflow/repository_context/models.py`
- Create: `src/forgeflow/repository_context/profile.py`
- Create: `tests/repository_context/test_contracts.py`

**Interfaces:**
- Consumes: OpenSpec field definitions and profile constants only.
- Produces: frozen dataclasses `RepositoryContextRequest`, `RepositoryContextResult`, `RepositoryContextValidationError`, `WorkspaceRef`, `NormalizedInput`, `BoundedOptionalInput`, `RelevantFile`, `RankingInputs`, `SearchResult`, `TestCommandHint`, `EvidenceRef`, `TextLocator`, `ContentHash`, `Limitation`, `InputSummary`, `CandidateCounts`, `ReturnedCounts`, and `RunSummary`; `RepositoryContextEnvelope` union; profile constant `M1_DEFAULTS`.

**Test strategy:** Use model-construction tests to pin tags, schema versions, immutability, required empty tuples, enum/code values, and the absence of runtime or future-stage fields. Keep filesystem behavior entirely out of this phase.

- [ ] **Step 1: Add the minimal package/test configuration**

Create `pyproject.toml` with Python `>=3.12`, `src` package discovery, and a test command that requires no third-party test framework:

```toml
[build-system]
requires = ["setuptools>=69"]
build-backend = "setuptools.build_meta"

[project]
name = "forgeflow"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = []

[tool.setuptools.packages.find]
where = ["src"]
```

- [ ] **Step 2: Write failing contract model tests**

In `tests/repository_context/test_contracts.py`, construct representative nested values and assert `FrozenInstanceError` on mutation, exact literal tags/schema versions, tuple defaults, and `dataclasses.fields()` excludes `runtime_metadata`, `run_id`, timestamps, patch, validation, branch, commit, PR, and memory fields.

```python
class ContractModelTests(unittest.TestCase):
    def test_ranking_inputs_are_immutable_and_narrow(self):
        value = RankingInputs(filename_match=True, path_match=False, text_match_count=1)
        self.assertEqual(
            [field.name for field in fields(value)],
            ["filename_match", "path_match", "text_match_count"],
        )
        with self.assertRaises(FrozenInstanceError):
            value.text_match_count = 2
```

- [ ] **Step 3: Run the model test and verify failure**

Run: `PYTHONPATH=src python -m unittest tests.repository_context.test_contracts -v`

Expected: FAIL because `forgeflow.repository_context.models` does not exist.

- [ ] **Step 4: Implement the immutable models and versioned profile**

Use `@dataclass(frozen=True, slots=True)` and tuples for contract arrays. Define all limits and policy IDs in one frozen profile object:

```python
M1_DEFAULTS = RepositoryContextProfile(
    configuration_profile_id="repository-context/m1-defaults-v1",
    normalization_id="m1-nfc-trim-collapse-casefold-v1",
    limit_profile_id="m1-default-limits-v1",
    ignore_policy_id="m1-default-ignore-v1",
    max_query_chars=512,
    max_issue_text_chars=4096,
    max_text_bytes_per_file=1_048_576,
    max_lines_per_file=20_000,
    max_text_locators_per_file=20,
    max_relevant_files=50,
    max_search_results=200,
    max_evidence_refs=300,
    max_test_command_hints=10,
)
```

- [ ] **Step 5: Run the model tests**

Run: `PYTHONPATH=src python -m unittest tests.repository_context.test_contracts -v`

Expected: PASS; no filesystem is accessed.

- [ ] **Step 6: Commit the contract foundation**

```bash
git add pyproject.toml src/forgeflow tests/repository_context/test_contracts.py
git commit -m "feat: define repository context contracts"
```

### Phase 2: Canonical JSON, Stable IDs, and Validation Envelope

**Files:**
- Create: `src/forgeflow/repository_context/canonical.py`
- Create: `src/forgeflow/repository_context/normalization.py`
- Create: `src/forgeflow/repository_context/validation.py`
- Create: `tests/repository_context/test_validation.py`
- Modify: `tests/repository_context/test_contracts.py`

**Interfaces:**
- Consumes: Phase 1 dataclasses and `M1_DEFAULTS`.
- Produces: `canonical_bytes(value, *, omit_fields=frozenset()) -> bytes`, `with_evidence_id(EvidenceRef) -> EvidenceRef`, `with_contract_id(RepositoryContextResult) -> RepositoryContextResult`, `build_validation_error(...) -> RepositoryContextValidationError`, `normalize_query(str) -> NormalizedInput`, and `normalize_issue_text(str | None) -> BoundedOptionalInput`.

**Test strategy:** Pin exact UTF-8 canonical bytes and recompute SHA-256 independently in tests. Verify self-ID omission, optional-field omission, explicit required `null`, integer-only payloads, normalization boundaries, and that empty query yields only the validation envelope with a repeatable `error_id`.

- [ ] **Step 1: Write failing canonicalization and validation tests**

Cover sorted object keys, compact separators, UTF-8 preservation, tuple-to-array conversion, absent optional omission, `EvidenceRef.locator is None` retained as JSON `null`, and rejection of floats. Add the first required error case:

```python
def test_empty_query_has_stable_error_id(self):
    first = validate_request(self.valid_request(query=" \t\n "))
    second = validate_request(self.valid_request(query="\n"))
    self.assertEqual(first.result_type, "repository_context_validation_error")
    self.assertEqual(first.error_code, "empty_query")
    self.assertEqual(first.error_id, second.error_id)
    self.assertNotIn("contract_id", canonical_mapping(first))
```

- [ ] **Step 2: Run the focused tests and verify failure**

Run: `PYTHONPATH=src python -m unittest tests.repository_context.test_validation -v`

Expected: FAIL on missing canonical and validation modules.

- [ ] **Step 3: Implement canonical serialization and hash constructors**

Convert dataclasses recursively, omit only explicitly absent optionals and the current identity field, preserve required `locator: null`, reject floats, then serialize with `ensure_ascii=False`, `sort_keys=True`, and separators `(',', ':')`. Compute IDs from the resulting bytes with `hashlib.sha256`.

- [ ] **Step 4: Implement normalization and validation precedence**

Use `unicodedata.normalize("NFC", value)`, `" ".join(value.split())`, and `.casefold()` only for matching views. Validate in deterministic order: workspace root presence/accessibility/confinement, `workspace_ref.root_id`, configuration profile, empty query, query size. Use bounded safe messages and summaries that never expose the host path or full invalid input.

- [ ] **Step 5: Run identity and validation tests twice**

Run: `PYTHONPATH=src python -m unittest tests.repository_context.test_contracts tests.repository_context.test_validation -v`

Expected: both runs PASS with identical asserted IDs.

- [ ] **Step 6: Commit canonical identity and validation**

```bash
git add src/forgeflow/repository_context tests/repository_context/test_contracts.py tests/repository_context/test_validation.py
git commit -m "feat: add canonical repository context identities"
```

### Phase 3: Acceptance Fixture Skeleton and Expected Error

**Files:**
- Create: `openspec/changes/repository-context-foundation/fixtures/workspaces/basic-context/src/payment_handler.py`
- Create: `openspec/changes/repository-context-foundation/fixtures/workspaces/basic-context/docs/payment-notes.txt`
- Create: `openspec/changes/repository-context-foundation/fixtures/workspaces/basic-context/README.md`
- Create: `openspec/changes/repository-context-foundation/fixtures/expected/basic-context/result.json`
- Create: `openspec/changes/repository-context-foundation/fixtures/expected/empty-query/error.json`
- Create: `tests/repository_context/support.py`
- Create: `tests/repository_context/test_acceptance.py`

**Interfaces:**
- Consumes: canonical serialization and validation from Phase 2.
- Produces: `fixture_workspace(name) -> Path`, `load_expected(case, filename) -> dict[str, object]`, and `snapshot_workspace(root) -> tuple[tuple[str, str], ...]` where each item is canonical relative path plus SHA-256 content digest.

**Test strategy:** Establish expected files before scanner code. The empty-query case passes immediately; the basic-context success test deliberately fails until the public service exists. The fixture contains one filename/path match, one text-only match, and one non-match, with no generated output under the workspace.

- [ ] **Step 1: Add the controlled fixture workspace**

Use a query such as `payment handler`. Make `src/payment_handler.py` match by filename/path, put the normalized phrase on known lines in `docs/payment-notes.txt`, and keep `README.md` unrelated. Do not include raw expected source payload in result JSON.

- [ ] **Step 2: Add expected empty-query JSON with its real computed `error_id`**

Generate the value only through the Phase 2 canonical helper during implementation, then check in the literal expected envelope. The expected file contains the complete validation envelope and none of the success-only keys.

- [ ] **Step 3: Add acceptance skeletons**

```python
def test_empty_query_matches_expected_envelope(self):
    actual = inspect_repository(self.request(query="   "))
    self.assertEqual(canonical_mapping(actual), load_expected("empty-query", "error.json"))

def test_basic_context_matches_expected_contract(self):
    before = snapshot_workspace(self.workspace)
    actual = inspect_repository(self.request(query="payment handler"))
    self.assertEqual(canonical_mapping(actual), load_expected("basic-context", "result.json"))
    self.assertEqual(snapshot_workspace(self.workspace), before)
```

- [ ] **Step 4: Run acceptance tests and record the intended split**

Run: `PYTHONPATH=src python -m unittest tests.repository_context.test_acceptance -v`

Expected: empty-query test PASS; basic-context test FAIL because `inspect_repository` is not implemented.

- [ ] **Step 5: Commit the contract-first fixtures**

```bash
git add openspec/changes/repository-context-foundation/fixtures tests/repository_context
git commit -m "test: pin repository context acceptance fixtures"
```

### Phase 4: Workspace Boundary and Deterministic Scanner

**Files:**
- Create: `src/forgeflow/repository_context/workspace.py`
- Create: `src/forgeflow/repository_context/scanner.py`
- Create: `tests/repository_context/test_workspace.py`
- Create: `tests/repository_context/test_scanner.py`

**Interfaces:**
- Consumes: profile, canonical path strings, immutable `Limitation` values.
- Produces: `WorkspaceBoundary.create(root: Path)`, `WorkspaceBoundary.canonical_entry(path: Path) -> str`, `WorkspaceBoundary.should_ignore(path: str, is_dir: bool) -> bool`, and `scan_workspace(boundary, profile) -> ScanReport`. `ScanReport` contains sorted `ScannedFile` records, deterministic discovery/skip counts, and ordered limitations; `ScannedFile` contains path, file kind, normalized inspected text or `None`, line tuple, content hash or `None`, and hash scope or `None`.

**Test strategy:** Build temporary controlled workspaces outside OpenSpec fixtures. Test path formatting, exact ignore rules, `.gitignore` non-semantics, stable lexical traversal, symlink exclusion/escape/loop behavior, NUL binary classification, strict UTF-8 failure, BOM and line-ending normalization, byte/line bounds, and unreadable-file behavior where platform permissions permit.

- [ ] **Step 1: Write failing boundary tests**

Assert canonical paths never expose the temporary root; reject lexical/resolved escapes; ensure symlinks never produce scanned files; and verify only the four explicit ignore rules match.

- [ ] **Step 2: Run boundary tests and verify failure**

Run: `PYTHONPATH=src python -m unittest tests.repository_context.test_workspace -v`

Expected: FAIL on missing `WorkspaceBoundary`.

- [ ] **Step 3: Implement confinement and ignore decisions**

Use `Path.relative_to`, `os.scandir`, and `DirEntry.is_symlink()` without following links. Convert accepted relative parts with `PurePosixPath`; reject empty, `.`, and `..` parts. Treat symlink entries as skipped traversal controls and emit only bounded canonical-path limitations.

- [ ] **Step 4: Write failing scanner classification tests**

Create files for ASCII/UTF-8, BOM, CRLF/CR, NUL bytes, invalid UTF-8, byte cap, line cap, ignored directories, and equal names inserted in reverse order. Assert exact scan order, counts, hashes, hash scopes, and limitation order.

- [ ] **Step 5: Implement deterministic traversal and bounded reads**

Sort every directory's entries by observed canonical name before processing. Read at most the configured byte boundary plus one detection byte, detect NUL before strict UTF-8 decoding, normalize line endings, cap lines, and hash exactly the normalized inspected text bytes represented by `hash_scope`.

- [ ] **Step 6: Run workspace and scanner tests**

Run: `PYTHONPATH=src python -m unittest tests.repository_context.test_workspace tests.repository_context.test_scanner -v`

Expected: PASS with no subprocess or network patch needed.

- [ ] **Step 7: Commit the read-only scanner**

```bash
git add src/forgeflow/repository_context/workspace.py src/forgeflow/repository_context/scanner.py tests/repository_context/test_workspace.py tests/repository_context/test_scanner.py
git commit -m "feat: add deterministic filesystem scanner"
```

### Phase 5: Direct Matching, Ranking, Evidence, and Line Locators

**Files:**
- Create: `src/forgeflow/repository_context/matching.py`
- Create: `src/forgeflow/repository_context/evidence.py`
- Create: `tests/repository_context/test_matching.py`

**Interfaces:**
- Consumes: normalized query, `ScannedFile`, canonical identity helpers, and profile score/cap values.
- Produces: `match_file(file, query, profile) -> MatchCandidate | None`, `score(RankingInputs) -> int`, `match_reasons(RankingInputs) -> tuple[str, ...]`, `build_evidence(candidate) -> tuple[EvidenceRef, ...]`, and `build_search_results(candidate) -> tuple[SearchResult, ...]`.

**Test strategy:** Pin filename versus full-path behavior, line-local casefolded substring matching, same-line duplicate collapse, no cross-line matches, locator cap, score formula, reason order, score/path sorting, evidence hash inclusion, stable evidence IDs, and the rule that path-only matches never become search results.

- [ ] **Step 1: Write failing matching and ranking tests**

```python
def test_score_and_reason_projection(self):
    inputs = RankingInputs(True, True, 2)
    self.assertEqual(score(inputs), 200)
    self.assertEqual(match_reasons(inputs), ("filename_match", "path_match", "text_match"))

def test_duplicate_occurrences_on_one_line_collapse(self):
    candidate = match_file(self.text_file("needle needle\nneedle\n"), self.query("needle"), M1_DEFAULTS)
    self.assertEqual(candidate.locators, (TextLocator(1, 1), TextLocator(2, 2)))
```

- [ ] **Step 2: Run matching tests and verify failure**

Run: `PYTHONPATH=src python -m unittest tests.repository_context.test_matching -v`

Expected: FAIL on missing matching/evidence functions.

- [ ] **Step 3: Implement the three allowed retrieval signals**

Compare the casefolded normalized query to the filename, canonical path, and each normalized line. Keep one locator per line, cap scoring locators at 20, construct `RankingInputs`, derive reasons in the exact required order, and return `None` only when all signals are false/zero.

- [ ] **Step 4: Implement evidence references and search results**

Create file-level evidence with `locator=None` for filename/path signals and line evidence for text signals. Include the scanned content hash and scope only on text evidence; compute every evidence ID from its canonical evidence key. Emit one `SearchResult` per returned text locator and none for filename/path-only evidence.

- [ ] **Step 5: Run matching tests twice**

Run: `PYTHONPATH=src python -m unittest tests.repository_context.test_matching -v`

Expected: both runs PASS; IDs and ordering are identical.

- [ ] **Step 6: Commit direct matching and evidence**

```bash
git add src/forgeflow/repository_context/matching.py src/forgeflow/repository_context/evidence.py tests/repository_context/test_matching.py
git commit -m "feat: add deterministic repository matching"
```

### Phase 6: Result Assembly and Public Vertical Slice

**Files:**
- Create: `src/forgeflow/repository_context/hints.py`
- Create: `src/forgeflow/repository_context/assembly.py`
- Create: `src/forgeflow/repository_context/service.py`
- Modify: `src/forgeflow/repository_context/__init__.py`
- Create: `tests/repository_context/test_assembly.py`
- Modify: `tests/repository_context/test_acceptance.py`
- Finalize: `openspec/changes/repository-context-foundation/fixtures/expected/basic-context/result.json`

**Interfaces:**
- Consumes: all earlier phases.
- Produces: public `inspect_repository(request: RepositoryContextRequest) -> RepositoryContextEnvelope`, `discover_test_hints(scan_report)`, and `assemble_result(...) -> RepositoryContextResult`.

**Test strategy:** Drive the complete success path through `inspect_repository`. Assert exact `RelevantFile`, `SearchResult`, `EvidenceRef`, limitations, candidate/returned counts, completion status, input summary, stable contract ID, graph consistency, and immutable output. Add root-only package/Makefile hint tests but keep hints outside the first basic fixture unless needed by the expected contract.

- [ ] **Step 1: Write failing assembly tests**

Cover relevant-file sorting, unique evidence sorting, returned-array counts, `completed` versus `completed_with_limitations`, unique sorted limitation codes, empty repository/no-match limitations, and no dangling references.

- [ ] **Step 2: Write failing root-only hint tests**

Assert strict root `package.json` `scripts.test` emits only `npm test`; a root non-recipe Makefile target containing exact `test` emits only `make test`; malformed JSON emits `malformed_metadata`; nested metadata emits no hint; and no raw script/recipe appears in output.

- [ ] **Step 3: Run assembly tests and verify failure**

Run: `PYTHONPATH=src python -m unittest tests.repository_context.test_assembly -v`

Expected: FAIL on missing assembly/service modules.

- [ ] **Step 4: Implement hints and graph-consistent result assembly**

Sort candidates first, apply relevant-file cap, retain associated search results, sort/cap search results and hints, retain referenced evidence only, and add exactly one grouped `result_set_truncated` limitation when any valid candidate is dropped. Derive all counts from pre-cap candidates and final arrays; derive completion status and limitation codes mechanically; assign `contract_id` last.

- [ ] **Step 5: Implement the public service entry point**

`inspect_repository` validates first and immediately returns validation errors. On valid input it normalizes bounded issue text, creates the workspace boundary, scans, matches, constructs evidence/hints, assembles the immutable result, and never catches exceptions into messages that expose host paths or stack traces.

- [ ] **Step 6: Finalize and run the first vertical-slice fixture**

Run: `PYTHONPATH=src python -m unittest tests.repository_context.test_acceptance.AcceptanceTests.test_basic_context_matches_expected_contract -v`

Expected: PASS with one filename/path match, one text match, line locator(s), inspected-text content hash, resolved evidence references, deterministic run summary, and the checked-in real `contract_id`.

- [ ] **Step 7: Run all contract-through-service tests**

Run: `PYTHONPATH=src python -m unittest discover -s tests -v`

Expected: PASS.

- [ ] **Step 8: Commit the working vertical slice**

```bash
git add src/forgeflow/repository_context tests/repository_context openspec/changes/repository-context-foundation/fixtures/expected/basic-context/result.json
git commit -m "feat: complete repository context vertical slice"
```

### Phase 7: Bounds, Coverage Limitations, and Determinism Hardening

**Files:**
- Modify: `src/forgeflow/repository_context/scanner.py`
- Modify: `src/forgeflow/repository_context/assembly.py`
- Modify: `src/forgeflow/repository_context/validation.py`
- Modify: `tests/repository_context/test_scanner.py`
- Modify: `tests/repository_context/test_assembly.py`
- Modify: `tests/repository_context/test_validation.py`
- Modify: `tests/repository_context/test_acceptance.py`

**Interfaces:**
- Consumes/produces: no new public interfaces; hardens the Phase 6 envelope behavior.

**Test strategy:** Add parameterized subtests for every initial limitation/error code and every cap. Re-run the same fixture after reordered filesystem creation and assert byte-identical canonical output. Assert coverage changes alter `contract_id` even when positive matches stay unchanged.

- [ ] **Step 1: Add failing validation matrix tests**

Cover `missing_workspace_ref`, `invalid_workspace`, `invalid_config_profile`, `empty_query`, `query_too_large`, inaccessible root, and required-root path escape. Assert deterministic precedence, bounded messages, stable error IDs, and zero success-only keys.

- [ ] **Step 2: Add failing limitation and cap tests**

Cover all initial codes: `empty_repository`, `no_matches`, `ignored_path`, `binary_file_skipped`, `oversized_file_skipped`, `file_scan_truncated`, `result_set_truncated`, `unreadable_file`, `unsupported_encoding`, `symlink_escape`, `symlink_loop`, `path_escape`, `incomplete_coverage`, `issue_text_truncated`, and `malformed_metadata`. Assert required structural ordering and candidate/returned differences.

- [ ] **Step 3: Add identity-sensitivity and repeatability tests**

Run identical inputs twice, recreate files in reverse insertion order, and compare canonical bytes. Then add one ignored/skipped/limited coverage fact and assert a different `contract_id` while positive evidence remains unchanged.

- [ ] **Step 4: Implement only the missing bounded behaviors**

Extend existing scanner/assembly/validation paths without adding new retrieval signals or broad exception payloads. Keep one deterministic source for limitation sorting and one source for all returned counts.

- [ ] **Step 5: Run the full suite twice**

Run: `PYTHONPATH=src python -m unittest discover -s tests -v`

Expected: both runs PASS with the same fixture IDs.

- [ ] **Step 6: Commit deterministic coverage hardening**

```bash
git add src/forgeflow/repository_context tests/repository_context
git commit -m "test: harden repository context determinism"
```

### Phase 8: Side-Effect, Payload-Avoidance, and OpenSpec Acceptance Gate

**Files:**
- Modify: `tests/repository_context/support.py`
- Modify: `tests/repository_context/test_acceptance.py`
- Modify: `openspec/changes/repository-context-foundation/tasks.md`

**Interfaces:**
- Consumes: public `inspect_repository` only.
- Produces: final Milestone 1 acceptance evidence; no production interface changes.

**Test strategy:** Snapshot path/content hashes before and after. Patch forbidden Python APIs at test boundaries (`subprocess`, sockets/HTTP entry points where imported, mutation methods) to fail if called. Search canonical output for synthetic sensitive-looking source content, fixture root paths, environment values, and forbidden runtime fields. Validate OpenSpec and mark only demonstrably completed task items.

- [ ] **Step 1: Add failing side-effect and forbidden-call guards**

Patch `subprocess.run`, `subprocess.Popen`, `os.system`, socket connection entry points, and filesystem mutation helpers to raise `AssertionError`. Execute the basic fixture and assert the workspace path/content snapshot is unchanged.

- [ ] **Step 2: Add payload-avoidance assertions**

Place a synthetic secret-like value in a controlled fixture file and assert the canonical envelope includes only its canonical path, locator, evidence ID, and hash metadata. Assert the serialized output excludes the value itself, absolute workspace root, environment values, `runtime_metadata`, timestamps, duration, stack traces, and raw script/recipe bodies.

- [ ] **Step 3: Run all acceptance tests**

Run: `PYTHONPATH=src python -m unittest tests.repository_context.test_acceptance -v`

Expected: PASS with no workspace changes and no forbidden API calls.

- [ ] **Step 4: Run the complete verification suite**

Run: `PYTHONPATH=src python -m unittest discover -s tests -v`

Expected: PASS.

Run: `openspec validate repository-context-foundation --strict`

Expected: PASS. If the installed OpenSpec CLI uses change paths, run its repository-documented equivalent and record the exact successful command in the commit message or review notes.

- [ ] **Step 5: Review scope and update the OpenSpec checklist**

Check only tasks whose code and tests now exist. Confirm no source module names or imports mention agents, workflows, orchestration, DeerFlow, patches, Git/PR, memory, network clients, LLMs, embeddings, ASTs, language servers, or semantic ranking.

- [ ] **Step 6: Commit the acceptance gate**

```bash
git add tests/repository_context openspec/changes/repository-context-foundation/tasks.md openspec/changes/repository-context-foundation/fixtures
git commit -m "test: verify repository context acceptance boundaries"
```

## Dependency Order

```text
Phase 1: immutable models + versioned profile
    -> Phase 2: canonical JSON + IDs + input validation
        -> Phase 3: fixture and expected-envelope skeletons
            -> Phase 4: workspace confinement + deterministic scanning
                -> Phase 5: direct matching + ranking + evidence
                    -> Phase 6: result assembly + public vertical slice
                        -> Phase 7: limits and determinism hardening
                            -> Phase 8: side-effect and OpenSpec acceptance gate
```

Phase 3 intentionally precedes retrieval implementation. Phases 4 and 5 may be developed independently after their shared Phase 1/2 contracts exist, but Phase 6 must consume both. Phase 7 must not widen public interfaces; it closes remaining OpenSpec cases through existing boundaries. Phase 8 is the release gate and depends on the complete service.

## Acceptance Criteria

1. A request containing a valid workspace root, safe caller-supplied `workspace_ref.root_id`, profile `repository-context/m1-defaults-v1`, and query returns `result_type: "repository_context_result"` with all required arrays and run-summary fields.
2. The checked-in basic fixture returns at least one filename/path match and one text match, with deterministic ranking, text-only search results, 1-based line locators, content hashes for inspected text evidence, and no dangling evidence IDs.
3. Repeated runs over identical logical input and content produce byte-identical canonical JSON, identical `EvidenceRef.id` values, and the same `contract_id`; deterministic coverage changes alter the contract ID.
4. Empty/whitespace-only query returns `result_type: "repository_context_validation_error"`, `completion_status: "validation_error"`, `error_code: "empty_query"`, and a stable `error_id`, with no success-only fields.
5. Every returned path is canonical and workspace-relative; absolute paths and escaped or symlink-target content never appear.
6. Inspection uses only direct filesystem APIs, obeys the exact ignore policy, follows stable traversal order, uses strict UTF-8 and bounded reads, and reports all incomplete coverage through deterministic limitations/counts.
7. Ranking inputs contain only filename, path, and capped text-match count; score, reason order, and tie-breaking are fully recomputable from the contract.
8. Result caps preserve reference graph consistency, distinguish candidate from returned counts, and emit exactly one grouped `result_set_truncated` limitation when candidates are dropped.
9. Root-only test hints, when present, are exactly `npm test` or `make test`, are evidenced and sorted, never execute, and never affect ranking.
10. Result and validation payloads contain no raw snippets/full files, synthetic secret-like source value, host path, command output, environment data, stack trace, timestamp, duration, runtime metadata, or future-stage state.
11. Workspace snapshots are identical before and after every acceptance run; forbidden subprocess, command, network, dependency, test execution, memory, PR, and mutation APIs are not invoked.
12. The full Python test suite and strict OpenSpec validation pass, and the implementation introduces no agents, workflow/orchestration runtime, DeerFlow integration, patch generation, Git/PR behavior, memory, LLM, embedding, AST, symbol, or semantic-ranking code.

## Self-Review Record

- Spec coverage: all OpenSpec requirements map to Phases 1 through 8; the requested first vertical slice completes in Phase 6, while the remaining accepted Milestone 1 bounds and acceptance cases close in Phases 7 and 8.
- Placeholder scan: no implementation step contains `TBD`, `TODO`, “implement later,” or an unspecified “write tests” instruction.
- Type consistency: the public entry point is consistently `inspect_repository(RepositoryContextRequest) -> RepositoryContextEnvelope`; canonical/hash, scan, match, evidence, hint, and assembly interfaces are introduced before consumers use them.
- Scope check: this is one independently testable subsystem. No separate agent, workflow, runtime, persistence, or DeerFlow sub-plan is needed or permitted for this milestone.
