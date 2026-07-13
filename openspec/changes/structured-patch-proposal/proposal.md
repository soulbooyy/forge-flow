# Change: Structured PatchProposal Slice

## Why

Milestone 1 provides immutable, deterministic repository facts but deliberately
does not infer root cause, select a fix, or edit code. Milestone 2 needs a
separate, evidence-backed `PatchProposal` contract so later validation and PR
work can inspect patch intent without treating model output as authority.

## Scope

- define tagged `PatchProposal` success and validation-error envelopes;
- consume a successful `RepositoryContextResult` by contract and evidence IDs;
- represent bounded root-cause hypotheses, fix strategy, candidate changed
  files, risk flags, limitations, and evidence references;
- evaluate proposal facts against an accepted patch-boundary policy profile;
- provide controlled fixtures and acceptance criteria before implementation.

## Non-goals

- source-code edits, diff generation, sandbox mutation, command execution, or
  test execution;
- Git, branch, commit, PR, network, memory, or DeerFlow-core side effects;
- retry loops, validation, review, policy-engine implementation, or human
  approval workflow implementation;
- automatic authorization of sensitive-file changes.

## Architecture Readiness Gate

The Architecture Readiness Gate is closed for Phase 1 contract/fixture work:

1. Accepted RFC-003 and ADR-007 limit M2 to a provider-neutral deterministic
   fixture source; M2 has no DeerFlow, MCP, LLM, network, or tool attachment.
2. M2 applies the existing RFC-002 contract/evidence and RFC-004 policy-decision
   boundaries through the accepted ADR and this feature specification. Their
   broader RFC status remains unchanged and does not authorize future provider
   or side-effect work.
3. `patch-proposal/m2-conservative-v1` defines sensitive-path matching,
   candidate-file and intent-size limits, decision semantics, and approval
   escalation without weakening RFC-004.

Phase 1 remains subject to the canonical implementation plan. No sandbox,
provider, command, diff, or source-edit implementation is authorized by this
gate closure.

## Impact

The resulting contract will be a non-authorizing handoff to later policy,
validation, review, and PR stages. The change intentionally narrows the
roadmap's optional sandbox diff to a future accepted extension; no current M2
artifact may contain or authorize an executable diff.
