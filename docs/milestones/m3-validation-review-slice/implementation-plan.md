# Milestone 3: Validation and Review Slice Canonical Implementation Plan

## Authority and Status

This is the sole execution authority for M3. It reconciles the non-canonical
[AI-assisted draft](../../_history/ai-assisted/implementation-plans/2026-07-14-validation-review-slice.md)
against the M3 OpenSpec, RFC-002, RFC-003, RFC-004, and ADR-008. Chat prompts
do not redefine phase scope, files, interfaces, or acceptance. No phase begins
until explicitly authorized and the required milestone branch/worktree is
assigned.

## Goal

Deliver immutable, deterministic, fixture-only `ValidationResult`,
`ValidationTerminal`, and `ReviewResult` contracts with auditable policy,
artifact, and evidence lineage. M3 must not create an execution, sandbox, or
retry capability.

## Reconciliation of AI Draft

- The draft's four phases are retained in canonical order: contract foundation;
  deterministic policy/attempt fixtures; service assembly; acceptance and
  hardening.
- The M3 OpenSpec contract design, not the draft, controls fields, controlled
  values, bounds, envelope separation, identity, and failure semantics.
- ADR-008 controls the fixture-only boundary: a fake executor is not command
  authority; policy terminals contain no simulated attempt facts; review is not
  approval; retry remains out of scope.
- RFC-003 and RFC-004 prohibit M3 from adding actual tool execution or treating
  repository configuration as authorization. No Phase 0 exists in execution;
  architecture and specification decisions are already authoritative.

## Global Constraints

- Use Python 3.12 standard library and `unittest`; add no dependency.
- Use only `validation-result/v1` / `vr_sha256:`, `validation-terminal/v1` /
  `vt_sha256:`, `review-result/v1` / `rr_sha256:`, and
  `validation-review-error/v1` / `vre_sha256:`.
- Use only `validation-review/m3-fixture-v1` version `1` and
  `m3/deterministic-policy-fixture-v1`.
- Consume M2 `PatchProposal` by immutable `contract_id`; never modify it,
  reread M1 context, or treat proposal/configuration content as authority.
- Do not add subprocess, shell, sandbox, workspace, filesystem, network,
  dependency-installation, credential, provider, MCP, DeerFlow, Git, PR, or
  retry-runtime behavior or imports.
- Store only bounded references and safe summaries; no raw source, command,
  output, report, environment, provider, or credential payload.
- Every phase follows RED → GREEN → REFACTOR, then targeted and cumulative
  tests, `git diff --check`, focused commit, Completion Record, and progress
  update.

## Phase 1: Contract Foundation and Canonical Fixtures

**Depends on:** accepted M3 OpenSpec and ADR-008.

**Files:**

- Create: `src/forgeflow/validation_review/__init__.py` — public M3 API.
- Create: `src/forgeflow/validation_review/models.py` — frozen envelopes and
  value objects.
- Create: `src/forgeflow/validation_review/profile.py` — M3 fixture profile.
- Create: `src/forgeflow/validation_review/canonical.py` — canonical identity.
- Create: `tests/validation_review/__init__.py`
- Create: `tests/validation_review/test_contracts.py`
- Create: `tests/validation_review/test_canonical.py`
- Create: `openspec/changes/validation-review-slice/fixtures/expected/phase-1-contract/{validation-result.json,validation-terminal.json,review-result.json,validation-review-error.json}`

**Interfaces:** `ValidationEnvelope`, `ValidationResult`,
`ValidationTerminal`, `ReviewResult`, `ValidationReviewError`,
`PolicyDecisionRecordRef`, `ReviewFinding`, `canonical_bytes()`, and the four
contract identity helpers named in the draft.

- [ ] Write targeted failing tests for frozen/slotted envelopes, exact literals,
  bounds, ordering, result/terminal separation, forbidden execution/payload
  fields, and canonical self-excluding IDs; record the RED command/result.
- [ ] Implement the smallest profile, models, canonical helpers, exports, and
  computed expected fragments required to make those tests pass.
- [ ] Run targeted GREEN tests, then the cumulative implemented suite; refactor
  only within the new package.
- [ ] Run `git diff --check`, inspect `git status --short`, commit
  `feat(validation-review): add contract foundation`, create
  `phases/phase-1-contract-foundation-and-canonical-fixtures.md`, and update
  progress.

**Acceptance:** envelopes are immutable and deterministically identified; a
terminal has no attempt fact; no fixture contains raw payloads.

## Phase 2: Deterministic Policy and Attempt Fixtures

**Depends on:** accepted Phase 1.

**Files:**

- Create: `src/forgeflow/validation_review/policy.py` — pure policy fixtures.
- Create: `src/forgeflow/validation_review/fixture_source.py` — in-memory
  attempt and review fixture lookup.
- Create: `tests/validation_review/test_policy.py`
- Create: `tests/validation_review/test_fixture_source.py`
- Create: `openspec/changes/validation-review-slice/fixtures/expected/phase-2-policy/{allowed.json,blocked.json,requires-human-approval.json,passed-attempt.json,failed-attempt.json}`

**Interfaces:** `policy_record_for(subject_contract_id, case_id)`,
`load_validation_fixture(case_id)`, and `load_review_fixture(case_id)`; all are
pure/in-memory and return no command or runtime object.

- [ ] Write targeted failing tests for exact three policy outcomes, deterministic
  PDR IDs, terminal-reason compatibility, fixture ordering, unknown cases,
  forbidden payload names, and absence of I/O imports; record RED.
- [ ] Implement only pure PDR-reference assembly and controlled in-memory
  fixture lookup; create computed expected fragments.
- [ ] Run targeted GREEN tests, the cumulative suite, `git diff --check`, and
  status inspection; commit `feat(validation-review): add deterministic policy fixtures`,
  create the Phase 2 completion record, and update progress.

**Acceptance:** blocked and approval-required cases yield governance facts but
no attempt fixture; a fixture cannot grant execution authority or expose data.

## Phase 3: Validation and Review Assembly Service

**Depends on:** accepted Phases 1–2.

**Files:**

- Create: `src/forgeflow/validation_review/service.py` — deterministic envelope
  orchestration and lineage validation.
- Modify: `src/forgeflow/validation_review/__init__.py` — export service API.
- Create: `tests/validation_review/test_service.py`
- Create: `openspec/changes/validation-review-slice/fixtures/expected/phase-3-service/{passed-result.json,failed-result.json,blocked-terminal.json,approval-required-terminal.json,review-result.json,validation-error.json}`

**Interfaces:** `build_validation_envelope(proposal, policy_case, fixture_case)`
and `build_review_result(proposal, validation_result, policy_case, review_case)`
return only the M3 contract union or `ValidationReviewError`.

- [ ] Write targeted failing tests for proposal/PDR lineage, policy-to-terminal
  mapping, allowed passed/failed results, absence of terminal attempt facts,
  terminal review rejection, dangling references, and safe error mapping;
  record RED.
- [ ] Implement the minimum in-memory orchestration: validate lineage first;
  create terminals before any attempt lookup for non-allowed policy; assemble
  completed results for allowed policy; calculate final identity last.
- [ ] Run targeted GREEN and cumulative tests, `git diff --check`, and status
  inspection; commit `feat(validation-review): assemble fixture-only result flows`,
  create the Phase 3 completion record, and update progress.

**Acceptance:** terminal flows cannot emit results or reviews; review can
observe completed facts but cannot determine governance; service has no I/O.

## Phase 4: Acceptance and Hardening

**Depends on:** accepted Phases 1–3.

**Files:**

- Create: `tests/validation_review/test_acceptance.py`
- Create: `openspec/changes/validation-review-slice/fixtures/expected/phase-4-acceptance/{validation-fragment.json,terminal-fragment.json,review-fragment.json,error-fragment.json}`
- Modify: `docs/milestones/m3-validation-review-slice/progress.md` — only after
  Phase 4 acceptance.

**Interfaces:** use only the Phase 3 public service API; no new production API.

- [ ] Write failing acceptance tests for repeated IDs, complete lineage, policy
  terminals, passed/failed facts, review severities, malformed inputs,
  forbidden payload rejection, and absence of execution/retry surfaces; record
  RED.
- [ ] Make only scoped changes required by acceptance; do not add an executor,
  command parser, sandbox, retry, or runtime adapter.
- [ ] Run `openspec validate validation-review-slice --strict`, targeted
  acceptance, full `unittest discover`, prohibited-import search,
  `git diff --check`, and `git status --short`.
- [ ] Commit `test(validation-review): add acceptance coverage`, create
  `phases/phase-4-acceptance-and-hardening.md`, update progress, and stop for
  user confirmation.

**Acceptance:** every OpenSpec scenario is fixture-covered; no unexecuted flow
claims execution facts; no side-effecting surface is introduced.
