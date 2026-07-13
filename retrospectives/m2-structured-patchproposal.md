# Milestone 2 Retrospective: Structured PatchProposal Slice

## Outcome

Milestone 2 delivered the deterministic, fixture-only `PatchProposal` slice
defined by the `structured-patch-proposal` OpenSpec change. All four canonical
implementation phases are accepted. The result is an immutable, evidence-backed
declarative proposal or a separate safe validation envelope, governed by the
versioned `patch-proposal/m2-conservative-v1` profile. It deliberately has no
provider, MCP, DeerFlow runtime, workspace, command, diff, mutation,
validation-execution, Git, PR, network, or memory capability.

## Evidence

- OpenSpec validation: `openspec validate structured-patch-proposal --strict`
  passed on 2026-07-14.
- Final implementation verification: `uv run --no-sync python -m unittest
  discover -s tests -v` passed with 98 tests on 2026-07-14.
- The static prohibited-import search for the M2 production package returned no
  matches for side-effect-related modules.
- The [Milestone 2 progress index](../docs/milestones/m2-structured-patchproposal/progress.md)
  links every accepted Phase Completion Record and implementation commit.
- The Phase 4 acceptance suite locks deterministic success and safe
  validation-error fragments through the public service boundary.

## What Worked

- Contract-first specification made envelope separation, canonical identities,
  evidence closure, and payload avoidance testable before service assembly.
- The conservative, explicitly versioned policy profile kept path limits,
  sensitive-path handling, approval escalation, and policy decision identity
  reproducible rather than implementation-defined.
- Fixture-only, provider-neutral synthesis made it possible to verify the
  intended handoff contract without introducing context egress, provider
  identity, retention, tool attachment, or runtime-failure governance.
- Focused phase commits and completion records preserved an auditable path from
  design supplement through boundary assessment, service assembly, and public
  acceptance coverage.

## Reconciliation and Lessons

- Phase 3 exposed an unspecified transient fixture-draft boundary. A targeted
  Grill-Me review and OpenSpec/contract supplement resolved it before service
  implementation. Future milestones should surface provider or adapter input
  boundaries explicitly during readiness review.
- Milestone execution initially paused until its required branch/worktree was
  assigned and recorded. The execution-environment rule now makes that
  prerequisite explicit before Phase 1.
- The original Phase 4 assertions assumed non-contract field names and a
  stronger-than-specified ban on stable error-code vocabulary. Acceptance tests
  must bind to the accepted contract names and protect untrusted payload values,
  not accidentally prohibit safe fixed terminology.
- Closure found stale OpenSpec task, roadmap, and README status. Milestone
  closure must reconcile project-level navigation as well as phase-local
  records.

## Deferred Work

- Milestone 3 owns validation and review contracts, command authority, bounded
  execution semantics, and any retry policy; M2 does not authorize them.
- Real LLM, MCP, DeerFlow, or other provider integration requires a separate
  OpenSpec and governance for context egress, redaction, provider identity,
  failures, audit retention, and tool-policy attachment.
- Source edits, diffs, sandbox mutation, test execution, Git/PR workflows,
  approval workflow, and production evaluation remain future, independently
  governed work.

## Closure Decision

Milestone 2 is complete. The branch is eligible for normal integration review
because its accepted OpenSpec, canonical plan, phase records, closure evidence,
and project-level navigation are reconciled. Branch merge, pull-request
creation, release, or worktree cleanup remain separate Git decisions.
