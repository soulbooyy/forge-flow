# M2 Structured PatchProposal Implementation Draft Plan

> **Non-canonical planning evidence.** Generated with Superpowers
> `writing-plans`; reconcile against the M2 OpenSpec, RFC-003, ADR-007, and the
> canonical plan before execution. This file never authorizes a phase.

**Goal:** Implement a deterministic, fixture-only, evidence-backed
`PatchProposal` contract and conservative policy assessment without any provider
call, workspace read, mutation, command, network, or side effect.

**Architecture:** A frozen contract layer validates and canonically identifies
proposal envelopes. A pure policy evaluator consumes ordered candidate changes
and the versioned M2 policy profile. A fixture source returns controlled draft
data; a service validates it against immutable M1 context, evaluates policy,
and returns one terminal envelope.

**Tech Stack:** Python 3.12 standard library (`dataclasses`, `hashlib`, `json`,
`unicodedata`), `unittest`, existing `src` package layout, OpenSpec CLI.

## Global Constraints

- Success is `patch-proposal/v1` with `pp_sha256:<lowercase-hex>` identity;
  validation failure is `patch-proposal-validation-error/v1` with
  `ppe_sha256:<lowercase-hex>` identity.
- Accept only `m2/deterministic-fixture-v1` and
  `patch-proposal/m2-conservative-v1` version `1`.
- Preserve M1 context immutability and reference only its `contract_id` and
  returned evidence IDs; do not reread a workspace.
- Do not emit source, diff, prompt, provider payload, command, network, Git,
  PR, memory, runtime, or approval data.
- Use the contract-design ordering and bounds exactly; policy decisions are
  invalidated by a candidate path, change kind, rationale, policy profile,
  evaluator, decision, or risk-flag change.
- Each implementation phase uses RED → GREEN → REFACTOR, one focused commit,
  one completion record, and one progress update.

## File Structure

| File | Responsibility |
| --- | --- |
| `src/forgeflow/patch_proposal/models.py` | Frozen request, success, error, candidate, policy-reference, and fixture-draft data models. |
| `src/forgeflow/patch_proposal/profile.py` | Immutable v1 limits, IDs, enums, and exact path-rule data. |
| `src/forgeflow/patch_proposal/canonical.py` | Canonical JSON plus proposal, error, candidate-digest, and policy-decision identity helpers. |
| `src/forgeflow/patch_proposal/policy.py` | Pure candidate-boundary assessment; no I/O. |
| `src/forgeflow/patch_proposal/fixture_source.py` | In-memory controlled draft lookup only. |
| `src/forgeflow/patch_proposal/service.py` | Terminal envelope assembly, provenance validation, and policy orchestration. |
| `tests/patch_proposal/*.py` | Focused TDD tests by responsibility. |
| `openspec/changes/structured-patch-proposal/fixtures/expected/` | Contract fragments, policy outcomes, fixture source cases, and acceptance fragments. |

## Phase 1: Contract Foundation and Fixtures

**Depends on:** accepted M2 OpenSpec, RFC-003, ADR-007, and the M2 policy
profile.

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

**Interfaces:**

```python
def canonical_bytes(value: object, *, omit_fields: frozenset[str] = frozenset()) -> bytes: ...
def proposal_id_for(value: PatchProposal) -> str: ...
def proposal_error_id_for(value: PatchProposalValidationError) -> str: ...
def candidate_digest_for(changes: tuple[CandidateChange, ...]) -> str: ...
def policy_decision_id_for(value: PolicyDecisionRef) -> str: ...
```

- [ ] Write contract tests for frozen/slotted models, exact literals, bounds,
  required tuples, success/error field separation, and forbidden payload fields.
- [ ] Run `uv run --no-sync python -m unittest tests.patch_proposal.test_contracts tests.patch_proposal.test_canonical -v`; expect import failure because the package is absent.
- [ ] Implement the exact dataclasses and profile from the M2 contract design;
  implement canonical JSON matching M1 behavior, with only each identity field
  omitted from its own hash input.
- [ ] Add fixture fragments with real computed IDs from representative objects;
  do not use placeholder hashes.
- [ ] Re-run the targeted command; expect all new contract/canonical tests to pass.
- [ ] Run `uv run --no-sync python -m unittest discover -s tests -v`; expect M1 regression tests plus the new Phase 1 tests to pass.
- [ ] Commit only the Phase 1 files with `feat(patch-proposal): add contract foundation`.

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

**Interfaces:**

```python
def assess_boundary(
    changes: tuple[CandidateChange, ...],
    profile: PatchProposalProfile,
) -> PolicyDecisionRef | PolicyBlockedError: ...
```

- [ ] Write failing tests for allowed ordinary paths; secret-like paths blocked;
  `.env`, CI/CD, exact auth segment, lockfile, migration, and deletion paths
  approval-required; `author/` remains non-sensitive; deterministic digest and
  decision identity change when a rationale changes.
- [ ] Run `uv run --no-sync python -m unittest tests.patch_proposal.test_policy -v`; expect missing-module failure.
- [ ] Implement a pure evaluator using only supplied candidate fields and the
  immutable profile. Return no success policy record for blocked candidates;
  derive sorted risk flags mechanically.
- [ ] Serialize the three expected policy fragments from evaluated objects and
  assert exact equality in tests.
- [ ] Re-run the targeted suite and then the cumulative suite; expect pass.
- [ ] Commit only Phase 2 files with `feat(patch-proposal): enforce conservative boundary policy`.

**Acceptance:** blocked candidates produce no successful policy reference;
approval-required is declarative only; a rationale or policy identity change
invalidates the decision ID.

## Phase 3: Deterministic Fixture Proposal-Source Adapter

**Depends on:** accepted Phases 1–2.

**Files:**

- Create: `src/forgeflow/patch_proposal/fixture_source.py`
- Create: `src/forgeflow/patch_proposal/service.py`
- Create: `tests/patch_proposal/test_fixture_source.py`
- Create: `tests/patch_proposal/test_service.py`
- Create: `openspec/changes/structured-patch-proposal/fixtures/expected/phase-3-source/valid-draft.json`
- Create: `openspec/changes/structured-patch-proposal/fixtures/expected/phase-3-source/malformed-draft-error.json`

**Interfaces:**

```python
def load_fixture_draft(case_id: str) -> FixtureProposalDraft: ...
def build_patch_proposal(
    context: RepositoryContextResult,
    task_input: TaskInput,
    draft: FixtureProposalDraft,
) -> PatchProposalEnvelope: ...
```

- [ ] Write failing tests proving fixture lookup is deterministic and performs
  no filesystem, provider, command, network, or workspace action; test service
  rejection of unsupported context, dangling evidence, malformed draft,
  oversized text, policy block, and raw-payload fields.
- [ ] Run `uv run --no-sync python -m unittest tests.patch_proposal.test_fixture_source tests.patch_proposal.test_service -v`; expect missing-module failure.
- [ ] Implement in-memory fixture selection and terminal service assembly.
  Validate all M1 evidence IDs before policy evaluation, convert a block to the
  validation envelope, and calculate the final proposal ID last.
- [ ] Add payload-free source fixtures and assert returned outputs equal their
  expected fragments while raw fixture strings never occur in terminal output.
- [ ] Re-run targeted and cumulative tests; expect pass.
- [ ] Commit only Phase 3 files with `feat(patch-proposal): add deterministic fixture service`.

**Acceptance:** service performs no provider/runtime/workspace/command/network
action; every proposal evidence ID resolves to the supplied M1 context.

## Phase 4: Acceptance and Hardening

**Depends on:** accepted Phases 1–3.

**Files:**

- Create: `tests/patch_proposal/test_acceptance.py`
- Create: `openspec/changes/structured-patch-proposal/fixtures/expected/phase-4-acceptance/result-fragment.json`
- Create: `openspec/changes/structured-patch-proposal/fixtures/expected/phase-4-acceptance/validation-error-fragment.json`
- Modify: `docs/milestones/m2-structured-patchproposal/progress.md`

**Interfaces:** consumes only `build_patch_proposal()` and public exported
models; produces no new production interface.

- [ ] Write failing acceptance tests for repeated canonical IDs, evidence
  closure, profile binding, every policy outcome, error-envelope separation,
  side-effect absence, and prohibited raw payload/diff/tool fields.
- [ ] Run `uv run --no-sync python -m unittest tests.patch_proposal.test_acceptance -v`; expect missing-module failure.
- [ ] Implement only fixes necessary for the acceptance tests; do not add a
  provider, sandbox, command runner, edit, test executor, or workflow graph.
- [ ] Run OpenSpec validation, targeted acceptance, full suite,
  `git diff --check`, and a static search confirming no prohibited integration
  imports or subprocess/network calls in `src/forgeflow/patch_proposal`.
- [ ] Create the Phase 4 completion record and update progress after its focused commit; do not begin any later milestone phase automatically.

**Acceptance:** all OpenSpec scenarios are fixture-covered; repeated equivalent
runs have identical IDs; no raw source/payload or prohibited side-effect is
introduced.
