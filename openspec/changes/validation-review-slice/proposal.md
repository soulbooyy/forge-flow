# Change: Validation and Review Slice

## Why

M2 produces an immutable, declarative `PatchProposal`, but it deliberately
does not execute validation or express review findings. M3 establishes the
next safe handoff: auditable validation-attempt facts, review findings, artifact
lineage, and policy-decision references without introducing a command runner,
sandbox, provider, or runtime integration.

## Scope

- define immutable `ValidationResult`, `ValidationTerminal`, and `ReviewResult`
  contract envelopes and their lineage to a M2 `PatchProposal`;
- define deterministic fixture/fake-executor inputs that synthesize bounded,
  non-side-effecting validation-attempt facts;
- define fixture-backed Policy Decision Record references and review findings;
- define artifact/evidence reference boundaries, terminal failure semantics,
  canonical identity, and acceptance fixtures.

## Non-goals

- real command execution, shell invocation, sandbox implementation, workspace
  access or mutation, network access, dynamic dependency installation, or
  credential access;
- a real provider, MCP server, DeerFlow runtime integration, Git, commit, PR,
  or artifact-store integration;
- retry, repair-loop, approval-workflow, or policy-engine implementation;
- treating repository configuration, a `PatchProposal`, a fixture, or a review
  finding as execution authority.

## Architecture Readiness Gate

The Architecture Readiness Gate is closed for M3 specification and later
fixture-only implementation work:

1. [ADR-008](../../../adr/ADR-008-use-contract-first-deterministic-fixtures-for-m3.md)
   accepts the contract-first, deterministic-fixture M3 boundary.
2. RFC-002 defines separate immutable contract families and the M3 lineage
   boundary; RFC-004 keeps policy outcomes and execution authorization outside
   M3; RFC-003 prohibits treating the fake executor as a tool integration.
3. Grill-Me conclusions are recorded in ADR-008: a policy-stopped flow cannot
   claim execution facts; artifact references cannot contain raw output; review
   cannot become approval; and retry remains out of scope.

This gate does not authorize actual command execution or alter the Draft status
of RFC-002 and RFC-004 beyond their M3 bounded directions.

## Impact

M3 creates ForgeFlow-owned contracts and deterministic fixtures only. A future
execution change must introduce a separate accepted OpenSpec with a versioned
ForgeFlow policy profile as its sole command-authorization source.
