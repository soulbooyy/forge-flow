# Phase 3: Deterministic Fixture Proposal-Source Adapter

## 1. Goal

Provide the provider-neutral, deterministic M2 fixture source and terminal
service that convert immutable M1 evidence plus bounded task input into either
a complete declarative `PatchProposal` or a separate validation envelope.

## 2. Scope

### Included

- Transient fixture-draft value objects with intent and evidence IDs only.
- In-memory `valid-default` fixture lookup with deterministic unknown-case
  failure.
- Evidence-first service validation, fixed M2 limitations and constraints,
  policy orchestration, terminal validation-envelope mapping, and final
  proposal identity calculation.
- Payload-free expected fixture fragments and focused source/service tests.

### Excluded

- Provider, LLM, MCP, DeerFlow runtime, workspace, filesystem, command,
  network, memory, Git, PR, diff, mutation, or test-execution behavior.
- Phase 4 acceptance coverage and hardening work.

## 3. Changed Files

| File | Change | Purpose |
| --- | --- | --- |
| `openspec/changes/structured-patch-proposal/contracts/milestone-2-patch-proposal-contract.md` | Modified | Define the transient fixture-draft boundary and safe error mapping. |
| `openspec/changes/structured-patch-proposal/design.md` | Modified | Record the targeted Phase 3 Grill-Me outcome. |
| `openspec/changes/structured-patch-proposal/specs/patch-proposal/spec.md` | Modified | Add normative fixture-synthesis requirements. |
| `docs/milestones/m2-structured-patchproposal/implementation-plan.md` | Modified | Reconcile the Phase 3 interface and affected files. |
| `src/forgeflow/patch_proposal/models.py` | Modified | Add transient fixture-draft value objects. |
| `src/forgeflow/patch_proposal/fixture_source.py` | Added | Provide in-memory `valid-default` draft lookup only. |
| `src/forgeflow/patch_proposal/service.py` | Added | Validate, evaluate policy, and assemble terminal envelopes. |
| `src/forgeflow/patch_proposal/__init__.py` | Modified | Export Phase 3 public APIs and transient draft types. |
| `tests/patch_proposal/test_fixture_source.py` | Added | Verify deterministic source lookup and payload-free draft shape. |
| `tests/patch_proposal/test_service.py` | Added | Verify evidence closure, terminal errors, policy results, bounds, and fixtures. |
| `openspec/changes/structured-patch-proposal/fixtures/expected/phase-3-source/valid-draft.json` | Added | Lock the deterministic transient fixture draft. |
| `openspec/changes/structured-patch-proposal/fixtures/expected/phase-3-source/malformed-draft-error.json` | Added | Lock the safe malformed-draft terminal envelope. |

## 4. Implementation

The source returns only the frozen in-memory `valid-default` fixture draft.
Drafts carry root-cause intent, a fix-strategy summary, candidate intent, and
evidence IDs; they cannot select source identity, policy profile, constraints,
limitations, or policy outcomes.

The service accepts only a supported `RepositoryContextResult`, a `TaskInput`,
and a transient draft. It rejects forbidden payload field names without reading
their values, converts and bounds draft intent, verifies all evidence IDs
against the supplied M1 result before policy assessment, maps blocked policy to
a validation envelope, and computes the final proposal identity last.

## 5. Design Decisions

- A targeted Grill-Me review was required because Phase 3 exposed an
  unspecified public draft boundary. Its accepted conclusions are recorded in
  the M2 OpenSpec design; no new RFC or ADR was needed.
- The service owns fixed limitation codes and strategy constraints, preventing
  the fixture source from claiming policy or authorization authority.
- Malformed, raw-payload, bounds, profile, context, evidence, and policy-block
  outcomes are terminal validation envelopes with safe fixed messages only.
- The service verifies the exact `rcr_sha256:` identity prefix before it can
  create a success envelope, avoiding construction-time exceptions for
  unsupported M1 contexts.

## 6. TDD and Tests

- RED: `uv run --no-sync python -m unittest tests.patch_proposal.test_fixture_source
  tests.patch_proposal.test_service -v` failed because the Phase 3 draft/source
  and service APIs did not exist.
- GREEN: source and service behavior passed after the minimal transient-draft
  conversion chain was implemented; the fixture-lock test then exposed the
  intentionally absent expected JSON fragments.
- Refactor/correction: generated deterministic source/error fragments. A
  further RED regression exposed that a non-`rcr_sha256:` M1 identity could
  reach final construction; narrowed the context check to return the required
  validation envelope instead.
- Targeted verification: the source/service command passed 8/8.
- Cumulative verification: `uv run --no-sync python -m unittest discover -s
  tests -v` passed 92/92; `openspec validate structured-patch-proposal --strict`
  and `git diff --check` passed.

## 7. Important Fixes and Edge Cases

- The source only supports `valid-default`; unknown cases cannot fall back to
  filesystem or provider behavior.
- Candidate and hypothesis evidence references must be returned by the exact
  supplied M1 context before policy evaluation.
- A forbidden raw-payload field maps to `raw_payload_forbidden` without its
  associated value appearing in the terminal message or summary.
- Blocked paths produce `policy_blocked` validation envelopes and never a
  partial or successful proposal.

## 8. Commit

- Specification supplement: `5017382bf013d4a4f523ffaa9b27b1c3278a1068`
  (`docs(m2): define fixture draft boundary`)
- Implementation: `669f861eb07ad142e0a97a3f0c8c2f2f9e4a5cfc`
  (`feat(patch-proposal): add deterministic fixture service`)

## 9. Acceptance

The service produces deterministic fixture-only proposals with complete M1
evidence lineage, fixed source/limitation/profile binding, and final canonical
identity. It returns distinct safe validation envelopes for unsupported
context, dangling evidence, malformed or raw-payload draft input, bounds,
invalid profile, and policy block. The cumulative suite passed 92 tests.

Status: **Accepted**.

## 10. Scope Boundary Confirmation

This phase added no real provider or DeerFlow/MCP integration, workspace read,
filesystem access, command, network, memory, diff, mutation, Git/PR, approval
workflow, or Phase 4 acceptance abstraction.

## 11. Follow-up

Next Phase: Acceptance and Hardening. It requires explicit user authorization
before starting.
