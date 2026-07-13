# Milestone 2: Structured PatchProposal Canonical Implementation Plan

## Authority and Status

This is the sole execution authority for M2. It reconciles the non-canonical
[AI-assisted draft](../../_history/ai-assisted/implementation-plans/2026-07-13-structured-patchproposal.md)
against the M2 OpenSpec, accepted RFC-003, and ADR-007. No phase begins until
explicitly authorized; chat prompts do not redefine phase scope or files.

## Goal

Deliver a deterministic, fixture-only `PatchProposal` contract that references
immutable M1 evidence, produces a versioned conservative policy outcome, and
never creates an executable edit, diff, command, provider call, or side effect.

## Reconciliation of AI Draft

- The draft's four phases are retained as canonical Phases 1–4 in the same order.
- The M2 contract design, not the draft, controls envelope fields, IDs, bounds,
  ordering, and validation semantics.
- The policy profile controls paths, risk flags, and revalidation. In
  particular, environment files require approval, `auth` matches exact path
  segments only, and `remove_file` requires approval unless blocked first.
- The draft's fixture source is limited to `m2/deterministic-fixture-v1`; no
  real LLM, MCP, DeerFlow runtime, workspace read, or network dependency is
  permitted.
- No Phase 0 exists in execution: architecture/specification decisions are
  already authoritative in RFCs, ADRs, and OpenSpec.

## Global Constraints

- Use Python 3.12 standard library and `unittest`; add no dependency.
- Success uses `patch-proposal/v1` and `pp_sha256:`; validation error uses
  `patch-proposal-validation-error/v1` and `ppe_sha256:`.
- Accept only `patch-proposal/m2-conservative-v1` version `1` and source
  `m2/deterministic-fixture-v1`.
- Preserve M1 `RepositoryContextResult`; reference only returned IDs and never
  reread its workspace or embed source payloads.
- Every phase follows RED → GREEN → REFACTOR, then targeted tests, cumulative
  tests, `git diff --check`, focused commit, completion record, and progress
  update.

## Phase 1: Contract Foundation and Fixtures

**Depends on:** accepted M2 OpenSpec, RFC-003, ADR-007, and policy profile.

**Files:**

- Create: `src/forgeflow/patch_proposal/__init__.py`
- Create: `src/forgeflow/patch_proposal/models.py`
- Create: `src/forgeflow/patch_proposal/profile.py`
- Create: `src/forgeflow/patch_proposal/canonical.py`
- Create: `tests/patch_proposal/__init__.py`
- Create: `tests/patch_proposal/test_contracts.py`
- Create: `tests/patch_proposal/test_canonical.py`
- Create: `openspec/changes/structured-patch-proposal/fixtures/expected/phase-1-contract/success-envelope.json`
- Create: `openspec/changes/structured-patch-proposal/fixtures/expected/phase-1-contract/validation-error.json`

**Interfaces:** `PatchProposalEnvelope`, `PatchProposal`,
`PatchProposalValidationError`, `TaskInput`, `RootCauseHypothesis`,
`FixStrategy`, `CandidateChange`, `PolicyDecisionRef`,
`canonical_bytes()`, `proposal_id_for()`, `proposal_error_id_for()`,
`candidate_digest_for()`, and `policy_decision_id_for()` exactly as specified
in the M2 contract design.

- [ ] Write tests that import the missing package and assert frozen/slotted
  models, exact schema/result literals, controlled values, bounds, ordering,
  self-excluding IDs, and success/error field separation.
- [ ] Run `uv run --no-sync python -m unittest tests.patch_proposal.test_contracts tests.patch_proposal.test_canonical -v`; expect import failure.
- [ ] Implement only the Phase 1 models, profile, canonical helpers, exports,
  and payload-free fixture fragments.
- [ ] Re-run the targeted command; expect pass. Run
  `uv run --no-sync python -m unittest discover -s tests -v`; expect all M1
  tests plus Phase 1 tests to pass.
- [ ] Commit with `feat(patch-proposal): add contract foundation`; create
  `phases/phase-1-contract-foundation-and-fixtures.md`; update `progress.md`.

**Acceptance:** IDs are deterministic; envelope fields cannot leak raw payloads
or mutate M1 context; contract fixture IDs are computed, not placeholders.

## Phase 2: Patch-Boundary Assessment Adapter

**Depends on:** accepted Phase 1.

**Files:**

- Create: `src/forgeflow/patch_proposal/policy.py`
- Create: `tests/patch_proposal/test_policy.py`
- Create: `openspec/changes/structured-patch-proposal/fixtures/expected/phase-2-policy/allowed.json`
- Create: `openspec/changes/structured-patch-proposal/fixtures/expected/phase-2-policy/blocked.json`
- Create: `openspec/changes/structured-patch-proposal/fixtures/expected/phase-2-policy/requires-human-approval.json`

**Interfaces:** `assess_boundary(changes, profile) -> PolicyDecisionRef |
PolicyBlockedError`; it is pure and has no filesystem, network, command, or
provider dependency.

- [ ] Write failing tests for the three decisions, profile/version identity,
  exact auth-segment behavior, environment escalation, deletion escalation,
  secret blocking, bounds, deterministic risk flags, and stale-decision IDs.
- [ ] Run `uv run --no-sync python -m unittest tests.patch_proposal.test_policy -v`; expect import failure.
- [ ] Implement only the profile-driven evaluator and expected policy fragments.
- [ ] Re-run targeted and cumulative suites; expect pass.
- [ ] Commit with `feat(patch-proposal): add boundary assessment`; create
  `phases/phase-2-patch-boundary-assessment-adapter.md`; update progress.

**Acceptance:** blocked candidates produce no successful policy reference;
approval-required is declarative only; a rationale or policy identity change
invalidates the decision ID.

## Phase 3: Deterministic Fixture Proposal-Source Adapter

**Depends on:** accepted Phases 1–2.

**Files:**

- Modify: `src/forgeflow/patch_proposal/models.py`
- Modify: `src/forgeflow/patch_proposal/__init__.py`
- Create: `src/forgeflow/patch_proposal/fixture_source.py`
- Create: `src/forgeflow/patch_proposal/service.py`
- Create: `tests/patch_proposal/test_fixture_source.py`
- Create: `tests/patch_proposal/test_service.py`
- Create: `openspec/changes/structured-patch-proposal/fixtures/expected/phase-3-source/valid-draft.json`
- Create: `openspec/changes/structured-patch-proposal/fixtures/expected/phase-3-source/malformed-draft-error.json`

**Interfaces:** `load_fixture_draft(case_id) -> FixtureProposalDraft` and
`build_patch_proposal(context, task_input, draft) -> PatchProposalEnvelope`.
`FixtureProposalDraft` is transient and contains only root-cause drafts,
`fix_strategy_summary`, and candidate-change drafts. The service owns fixed
constraint codes, limitation codes, source/profile identity, policy evaluation,
and terminal-envelope assembly. M2 source lookup supports `valid-default`
only; unknown cases are lookup failures, while malformed or forbidden-payload
service input maps to the contract-defined validation envelope.

- [ ] Write failing tests for deterministic in-memory `valid-default` lookup
  and all terminal error conditions: unsupported M1 context, dangling
  evidence, malformed draft, oversize fields, forbidden raw payload, invalid
  profile, and policy block.
- [ ] Run `uv run --no-sync python -m unittest tests.patch_proposal.test_fixture_source tests.patch_proposal.test_service -v`; expect import failure.
- [ ] Implement only fixture lookup, validation, policy orchestration, and final
  terminal-envelope assembly; calculate final proposal identity last.
- [ ] Re-run targeted and cumulative suites; expect pass.
- [ ] Commit with `feat(patch-proposal): add deterministic fixture service`;
  create `phases/phase-3-deterministic-fixture-proposal-source-adapter.md`;
  update progress.

**Acceptance:** service performs no provider/runtime/workspace/command/network
action; every proposal evidence ID resolves to the supplied M1 context.

## Phase 4: Acceptance and Hardening

**Depends on:** accepted Phases 1–3.

**Files:**

- Create: `tests/patch_proposal/test_acceptance.py`
- Create: `openspec/changes/structured-patch-proposal/fixtures/expected/phase-4-acceptance/result-fragment.json`
- Create: `openspec/changes/structured-patch-proposal/fixtures/expected/phase-4-acceptance/validation-error-fragment.json`
- Modify: `docs/milestones/m2-structured-patchproposal/progress.md`

- [ ] Write failing public-service acceptance tests for determinism, canonical
  identities, evidence closure, policy outcomes, revalidation, terminal-error
  separation, payload avoidance, and side-effect absence.
- [ ] Run `uv run --no-sync python -m unittest tests.patch_proposal.test_acceptance -v`; expect import failure.
- [ ] Make only scoped fixes needed to pass the acceptance suite; do not add an
  integration, command runner, sandbox edit, validation executor, or workflow.
- [ ] Run `openspec validate structured-patch-proposal --strict`, targeted
  acceptance, full `unittest discover`, a static forbidden-import search,
  `git diff --check`, and `git status --short`.
- [ ] Commit with `test(patch-proposal): add acceptance coverage`; create
  `phases/phase-4-acceptance-and-hardening.md`; update progress and stop.

**Acceptance:** all OpenSpec scenarios are fixture-covered; repeated equivalent
runs have identical IDs; no raw source/payload or prohibited side-effect is
introduced.
