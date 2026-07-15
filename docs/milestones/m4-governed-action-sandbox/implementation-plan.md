# Milestone 4: Governed Action and Sandbox Boundary Canonical Implementation Plan

## Authority and Status

This is the sole execution authority for the first M4 feature. It reconciles
the non-canonical [AI-assisted draft](../../_history/ai-assisted/implementation-plans/2026-07-15-governed-action-sandbox.md)
against the accepted [governed-action-sandbox OpenSpec](../../../openspec/changes/governed-action-sandbox/),
RFC-002, RFC-004, RFC-005, RFC-006, ADR-011, and registered fixture/image
inputs. Chat prompts do not redefine phase scope, files, interfaces, or
acceptance. No phase begins until explicitly authorized and assigned a M4
branch/worktree.

## Goal

Deliver immutable governed-action contracts, exact policy evaluation, and a
fail-closed OCI sandbox attempt seam for the one registered fixture test
command. This feature creates no patch, artifact store, approval workflow,
GitHub action, or automatic retry capability.

## Reconciliation of AI Draft

- The draft's four phases are retained: contract foundation; pure policy;
  OCI adapter/service; acceptance hardening.
- The OpenSpec controls all fields, identities, terminal semantics, and
  acceptance requirements. The draft's suggested file layout is retained only
  where it does not add a new public capability.
- The stale-base-revision amendment is authoritative: `requires_human_approval`
  is the PDR outcome; `not_started/base_revision_mismatch` is the attempt fact.
  This prevents repository state validation from being conflated with
  `sandbox_unavailable`, which is reserved for OCI capability failure.
- The draft's OCI CLI suggestion is an adapter implementation option, not a
  Docker/Podman product dependency. Phase 3 must use controlled fakes for all
  automated tests; an actual registered image run requires separate explicit
  fixture-owner authorization and reset/audit handling.
- No Phase 0 exists in implementation: M4 architecture and OpenSpec gates are
  closed. This plan does not authorize its own branch/worktree or Phase 1.

## Global Constraints

- Use Python 3.12 standard library and `unittest`; add no dependency.
- Use only `forgeflow-m4-fixture-only` version `1.0.0`, repository ID
  `1300511729`, base SHA `97c8220cd713ebf61124ac2de2f3eadc6e4dc222`, and OCI
  image digest
  `sha256:81b691e3b5d43b2f4e717eaeef63437705addd115aee32917efd5d7387807f28`.
- The sole command capability is `python3 -m unittest discover -s tests`, with
  `workspace_root`, empty environment, 120000 ms timeout, and 65536-byte output
  limit. No shell, extra argument, dynamic command, or dependency installation.
- PDR is the only authorization. `ActionIntent` and `CommandIntent` are
  declarative. No execution starts without a fresh allowed PDR.
- A stale base revision is `requires_human_approval` plus
  `not_started/base_revision_mismatch`, with no sandbox/GitHub mutation,
  artifact publish, execution facts, or old-authorization reuse.
- OCI capability failure is `not_started/sandbox_unavailable`; host-process,
  DeerFlow, permissive backend, or local-image fallback is forbidden.
- Output is transient/discarded and `artifact_ref_ids` is always empty. Never
  persist raw output, source, credentials, environment, workspace path, or
  runtime object.
- `max_automatic_retries` is 0. A started `cancelled` attempt uses only
  `cancelled_by_request`; no retry is created.
- Each phase follows RED → GREEN → REFACTOR, targeted and cumulative tests,
  strict OpenSpec validation, scope checks, focused commit, completion record,
  progress update, and independent review when required.

## Phase 1: Contract Foundation and Canonical Fixtures

**Depends on:** accepted OpenSpec, ADR-011, registered fixture/image inputs,
explicit Phase 1 authorization, and an assigned M4 branch/worktree.

**Files:**

- Create: `src/forgeflow/governed_action_sandbox/__init__.py` — deliberate
  public exports.
- Create: `src/forgeflow/governed_action_sandbox/models.py` — frozen
  ActionIntent, CommandIntent, PDR, ExecutionAttempt, observations, and error.
- Create: `src/forgeflow/governed_action_sandbox/canonical.py` — canonical JSON
  and self-excluding SHA-256 IDs.
- Create: `src/forgeflow/governed_action_sandbox/profile.py` — exact registered
  fixture constants and bounds.
- Create: `tests/governed_action_sandbox/{__init__.py,test_contracts.py,test_canonical.py}`.
- Create: `openspec/changes/governed-action-sandbox/fixtures/expected/phase-1-contract/` — computed safe fragments only.

**Interfaces:** frozen `ActionIntent`, `CommandIntent`,
`PolicyDecisionRecord`, `ExecutionAttempt`, `ResourceObservations`, and
`GovernedActionSandboxValidationError`; canonical ID helpers for each contract.

- [ ] Write failing tests for exact literals, frozen/slotted models, ID format,
  canonical self-exclusion, PDR ID equality, observation bounds, no raw fields,
  not-started fact absence, stale revision, and cancellation compatibility.
- [ ] Run RED: `uv run --no-sync python -m unittest tests.governed_action_sandbox.test_contracts tests.governed_action_sandbox.test_canonical -v`.
- [ ] Implement the smallest models/profile/canonical helpers; calculate final
  IDs only after validation.
- [ ] Run GREEN and cumulative `unittest discover`; create computed fixtures.
- [ ] Run strict OpenSpec/diff/status checks; commit
  `feat(governed-action-sandbox): add immutable execution contracts`; create
  the Phase 1 completion record and update progress.

**Acceptance:** every contract is immutable and deterministic; no not-started
attempt carries started facts; stale revision and cancellation are factual,
non-authorizing, and non-retryable.

## Phase 2: Exact Policy and Terminal Assembly

**Depends on:** accepted Phase 1.

**Files:**

- Create: `src/forgeflow/governed_action_sandbox/policy.py` — pure current-input
  PDR evaluation and intent assembly.
- Modify: `src/forgeflow/governed_action_sandbox/__init__.py` — export only the
  accepted policy/intent API.
- Create: `tests/governed_action_sandbox/test_policy.py`.
- Create: `openspec/changes/governed-action-sandbox/fixtures/expected/phase-2-policy/` — allowed, blocked, approval, and stale-revision fragments.

**Interfaces:** `build_action_intent`, `build_command_intent`, and
`evaluate_command_intent`; all return contracts only and perform no I/O.

- [ ] Write failing tests for exact command/image/profile/repository values,
  fresh PDR lineage, mismatch blocking, approval-required terminals, and stale
  revision mapping to `requires_human_approval` plus
  `not_started/base_revision_mismatch`.
- [ ] Run RED: `uv run --no-sync python -m unittest tests.governed_action_sandbox.test_policy -v`.
- [ ] Implement pure policy assembly; never read repository configuration,
  environment, Issue content, credentials, workspace, or OCI runtime.
- [ ] Run targeted GREEN, cumulative suite, prohibited-I/O import check,
  OpenSpec/diff/status checks; commit
  `feat(governed-action-sandbox): add exact policy evaluation`; create the
  Phase 2 completion record and update progress.

**Acceptance:** only exact registered command lineage is allowed; every changed
input receives a fresh PDR; all blocked/approval/stale paths create no process
or workspace.

## Phase 3: Fail-Closed OCI Adapter and Attempt Service

**Depends on:** accepted Phases 1–2 and explicit authorization for this phase.

**Files:**

- Create: `src/forgeflow/governed_action_sandbox/oci_adapter.py` — injected OCI
  backend protocol, capability proof, shell-free argv, bounded facts, cleanup.
- Create: `src/forgeflow/governed_action_sandbox/service.py` — PDR-first attempt
  orchestration.
- Modify: `src/forgeflow/governed_action_sandbox/__init__.py` — export accepted
  service interfaces.
- Create: `tests/governed_action_sandbox/{test_oci_adapter.py,test_service.py}`.
- Create: `openspec/changes/governed-action-sandbox/fixtures/expected/phase-3-service/` — controlled terminal fragments.

**Interfaces:** `OciBackend.prove_and_run(CommandIntent) -> OciRunFacts` and
`execute_governed_attempt(ActionIntent, OciBackend) -> ExecutionAttempt | GovernedActionSandboxValidationError`.

- [ ] Write failing tests with controlled fake backends for no-network/credential/image/workspace proof, no host fallback, blocked/approval/stale zero launch, command failure, timeout/output budget, and post-start cancellation.
- [ ] Run RED: `uv run --no-sync python -m unittest tests.governed_action_sandbox.test_oci_adapter tests.governed_action_sandbox.test_service -v`.
- [ ] Implement the minimal adapter seam. It must form no shell command, prove
  every OCI constraint before start, discard output after bounded accounting,
  destroy the temporary workspace, and return `sandbox_unavailable` before
  launch if any proof fails.
- [ ] Run GREEN with fakes only. Run an actual registered OCI image only after
  separate fixture-owner approval and registered reset/audit evidence.
- [ ] Run cumulative verification and focused checks; commit
  `feat(governed-action-sandbox): add fail-closed oci attempt service`; create
  the Phase 3 completion record and update progress.

**Acceptance:** OCI capability failure remains distinct from repository state;
no disallowed path launches an adapter; a started cancellation is truthful and
never becomes command failure or retry.

## Phase 4: Acceptance Matrix and Boundary Hardening

**Depends on:** accepted Phases 1–3.

**Files:**

- Create: `tests/governed_action_sandbox/test_acceptance.py`.
- Create: `openspec/changes/governed-action-sandbox/fixtures/expected/phase-4-acceptance/` — bounded expected fragments.
- Modify only scoped Phase 1–3 files required by failing acceptance tests.

**Interfaces:** use only the Phase 1–3 public APIs; add no new public surface.

- [ ] Write failing acceptance tests for canonical IDs, all PDR outcomes,
  stale revision zero facts, OCI capability failure, command/limit/timeout/
  cancellation terminals, zero retry, zero artifact refs, raw payload rejection,
  and prohibited imports/effects.
- [ ] Run RED: `uv run --no-sync python -m unittest tests.governed_action_sandbox.test_acceptance -v`.
- [ ] Make only scoped corrections; do not add patch, scan/redaction, approval,
  artifact, GitHub, provider, DeerFlow, or retry capabilities.
- [ ] Run final targeted/full tests, strict OpenSpec validation, prohibited
  surface search, `git diff --check`, and `git status --short`.
- [ ] Commit `test(governed-action-sandbox): add acceptance coverage`; create
  Phase 4 completion record, update progress, conduct required independent
  review, and stop for user confirmation.

**Acceptance:** every OpenSpec scenario is deterministic and covered; fault or
denial paths create zero external mutations; actual OCI evaluation remains a
separately authorized fixture-owner operation.
