# M3 Validation and Review Slice Implementation Draft Plan

> **Non-canonical planning evidence.** Generated with Superpowers
> `writing-plans`; reconcile against the M3 OpenSpec, RFC-002, RFC-003,
> RFC-004, and ADR-008 before execution. This file never authorizes a phase.

**Goal:** Implement immutable, deterministic, fixture-only validation and
review contracts with auditable policy, artifact, and evidence lineage, without
creating an execution capability.

**Architecture:** A frozen contract and canonical-identity layer provides
separate completed-validation, validation-terminal, review, and error
envelopes. Pure policy fixtures and an in-memory fake executor supply bounded
facts; a service assembles contracts without reading a workspace or invoking a
tool. Public acceptance tests prove the separation of facts, review, and
governance.

**Tech Stack:** Python 3.12 standard library (`dataclasses`, `hashlib`, `json`,
`unicodedata`), `unittest`, existing ForgeFlow package layout, OpenSpec CLI.

## Global Constraints

- Use `validation-result/v1` / `vr_sha256:`, `validation-terminal/v1` /
  `vt_sha256:`, `review-result/v1` / `rr_sha256:`, and
  `validation-review-error/v1` / `vre_sha256:` exactly as specified.
- Accept only `validation-review/m3-fixture-v1` version `1` and
  `m3/deterministic-policy-fixture-v1`.
- Consume M2 only by immutable `PatchProposal.contract_id`; do not modify the
  proposal, reread M1 context, or treat any proposal/configuration field as
  execution authority.
- A `ValidationResult` has only completed deterministic attempt facts;
  `ValidationTerminal` has no attempt ID, command claim, exit code, or output.
- Do not add subprocess, shell, sandbox, workspace, filesystem, network,
  dependency-installation, credential, provider, MCP, DeerFlow, Git, PR, or
  retry-runtime behavior or imports.
- Persist references and safe summaries only; never raw source, command text,
  output, logs, reports, environment values, provider payloads, or credentials.
- Every phase follows RED → GREEN → REFACTOR, targeted and cumulative tests,
  `git diff --check`, focused commit, Completion Record, and progress update.

## File Structure

| File | Responsibility |
| --- | --- |
| `src/forgeflow/validation_review/models.py` | Frozen M3 contracts, transient fixture types, validation helpers, and envelope aliases. |
| `src/forgeflow/validation_review/profile.py` | Immutable fixture profile IDs, limits, controlled values, and forbidden field names. |
| `src/forgeflow/validation_review/canonical.py` | Canonical JSON and independent contract/PDR identity helpers. |
| `src/forgeflow/validation_review/policy.py` | Pure deterministic policy-fixture reference assembly; no I/O. |
| `src/forgeflow/validation_review/fixture_source.py` | In-memory fixture cases and fake attempt facts only. |
| `src/forgeflow/validation_review/service.py` | Validation terminal/result and review assembly with lineage checks. |
| `tests/validation_review/*.py` | Focused contract, canonical, policy, fixture, service, and acceptance tests. |
| `openspec/changes/validation-review-slice/fixtures/expected/` | Payload-free expected contract fragments by phase. |

## Phase 1: Contract Foundation and Canonical Fixtures

**Depends on:** accepted M3 OpenSpec and ADR-008.

**Files:** create `src/forgeflow/validation_review/{__init__.py,models.py,profile.py,canonical.py}`,
`tests/validation_review/{__init__.py,test_contracts.py,test_canonical.py}`, and
`openspec/changes/validation-review-slice/fixtures/expected/phase-1-contract/`
fragments for result, terminal, review, and error envelopes.

**Interfaces:** export `ValidationEnvelope`, `ValidationResult`,
`ValidationTerminal`, `ReviewResult`, `ValidationReviewError`,
`PolicyDecisionRecordRef`, `ReviewFinding`, `canonical_bytes()`,
`validation_result_id_for()`, `validation_terminal_id_for()`,
`review_result_id_for()`, `validation_review_error_id_for()`, and
`policy_decision_id_for()`.

- [ ] Write failing frozen/slotted contract tests covering exact literals,
  controlled values, canonical ordering, field bounds, separate terminal/result
  fields, prohibited execution/payload fields, and hash self-exclusion.
- [ ] Run `uv run --no-sync python -m unittest tests.validation_review.test_contracts tests.validation_review.test_canonical -v`; expect import failure because the package is absent.
- [ ] Implement only the profile, models, canonical helpers, public exports,
  and expected fragments with computed IDs.
- [ ] Re-run targeted tests, then `uv run --no-sync python -m unittest discover -s tests -v`; expect all existing tests and Phase 1 tests to pass.
- [ ] Commit `feat(validation-review): add contract foundation`; record Phase 1
  completion and progress only after acceptance.

**Acceptance:** Every envelope is immutable and independently identified; a
terminal cannot carry simulated attempt facts; fixtures are payload-free.

## Phase 2: Deterministic Policy and Attempt Fixtures

**Depends on:** accepted Phase 1.

**Files:** create `src/forgeflow/validation_review/{policy.py,fixture_source.py}`,
`tests/validation_review/{test_policy.py,test_fixture_source.py}`, and
`openspec/changes/validation-review-slice/fixtures/expected/phase-2-policy/`
fragments for allowed, blocked, approval-required, passed, and failed cases.

**Interfaces:** `policy_record_for(subject_contract_id, case_id) ->
PolicyDecisionRecordRef`, `load_validation_fixture(case_id) ->
FixtureValidationAttempt`, and `load_review_fixture(case_id) ->
FixtureReviewFindings`; unknown cases return no contract and are mapped by the
service to `ValidationReviewError`.

- [ ] Write failing tests for deterministic policy identity, exact three policy
  results, matched terminal reason requirements, attempt-case ordering, unknown
  cases, forbidden raw-payload field names, and absence of I/O imports.
- [ ] Run `uv run --no-sync python -m unittest tests.validation_review.test_policy tests.validation_review.test_fixture_source -v`; expect missing-module failure.
- [ ] Implement only in-memory fixture lookup and pure policy-reference
  construction; do not create command, sandbox, repository-config, or runtime
  interfaces.
- [ ] Re-run targeted and cumulative suites; expect pass.
- [ ] Commit `feat(validation-review): add deterministic policy fixtures`; record
  Phase 2 completion and progress only after acceptance.

**Acceptance:** `blocked` and `requires_human_approval` are policy facts that
produce no attempt fixture; fake fixtures cannot grant authority or leak data.

## Phase 3: Validation and Review Assembly Service

**Depends on:** accepted Phases 1–2.

**Files:** create `src/forgeflow/validation_review/service.py` and
`tests/validation_review/test_service.py`; modify `__init__.py`; add
`openspec/changes/validation-review-slice/fixtures/expected/phase-3-service/`
fragments for passed result, failed result, blocked terminal,
approval-required terminal, review, and validation error.

**Interfaces:** `build_validation_envelope(proposal, policy_case, fixture_case)
-> ValidationEnvelope | ValidationReviewError` and
`build_review_result(proposal, validation_result, policy_case, review_case) ->
ReviewResult | ValidationReviewError`.

- [ ] Write failing tests for proposal lineage, policy-result-to-terminal
  mapping, allowed passed/failed results, terminal absence of attempt facts,
  review input restrictions, PDR reference matching, dangling references, and
  payload-safe errors.
- [ ] Run `uv run --no-sync python -m unittest tests.validation_review.test_service -v`; expect missing-module failure.
- [ ] Implement deterministic orchestration only: validate lineage first,
  assemble a terminal before any fixture-attempt lookup for non-allowed policy,
  assemble completed results only for allowed policy, and calculate final IDs
  last.
- [ ] Re-run targeted and cumulative suites; expect pass.
- [ ] Commit `feat(validation-review): assemble fixture-only result flows`;
  record Phase 3 completion and progress only after acceptance.

**Acceptance:** A terminal cannot become a result or review; review observes a
completed result but cannot select governance outcome; service performs no I/O.

## Phase 4: Acceptance and Hardening

**Depends on:** accepted Phases 1–3.

**Files:** create `tests/validation_review/test_acceptance.py` and
`openspec/changes/validation-review-slice/fixtures/expected/phase-4-acceptance/`
fragments; modify only M3 `progress.md` after the accepted commit.

**Interfaces:** consume public `build_validation_envelope()` and
`build_review_result()` interfaces only; add no production interface.

- [ ] Write failing end-to-end fixture acceptance tests for repeated IDs,
  full lineage, all policy terminals, passed/failed facts, review severities,
  invalid inputs, raw-payload rejection, and absent execution/retry surfaces.
- [ ] Run `uv run --no-sync python -m unittest tests.validation_review.test_acceptance -v`; expect missing-module failure.
- [ ] Make only scoped corrections required by the acceptance suite; do not add
  command parsing, process execution, sandbox integration, retries, or runtime
  adapters.
- [ ] Run `openspec validate validation-review-slice --strict`, targeted
  acceptance, full `unittest discover`, static prohibited-import search,
  `git diff --check`, and `git status --short`.
- [ ] Commit `test(validation-review): add acceptance coverage`; record Phase 4
  completion, update progress, and stop for user confirmation.

**Acceptance:** All OpenSpec scenarios are deterministic-fixture covered; no
unexecuted flow claims execution facts; no side-effecting surface is introduced.
