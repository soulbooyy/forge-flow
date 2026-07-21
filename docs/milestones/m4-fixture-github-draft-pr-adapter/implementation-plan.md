# M4 Feature 4: Fixture-Repository GitHub Draft PR Adapter Canonical Plan

## Authority

This plan follows the accepted Feature 4 OpenSpec, ADR-010, RFC-002/004/005,
and the registered M4 fixture environment. It authorizes neither implementation
nor a GitHub mutation until an explicit Phase 1 authorization is recorded.
It follows [Agent Execution Authority and Stop Rules](../../process/agent-execution-authority.md). GitHub calls, opaque credential use, and external mutations retain their explicit feature-specific gates.

## Global Constraints

- The adapter is the only component allowed to call GitHub APIs.
- It accepts only registered fixture repository/Issue/base-revision identity,
  opaque runtime credential, fresh allowed PDR, and bounded ForgeFlow facts.
- It never persists raw Issue data, source, diff, patch, command output,
  credential, environment, local path, or GitHub API payload.
- It creates at most one branch, one commit, and one Draft PR per idempotency
  key; ambiguous outcomes have zero automatic retry.
- No non-draft PR, merge, arbitrary repository access, or credential
  provisioning is in scope.

## Phases

### Phase 1: Immutable Mutation Contracts and Idempotency

Create bounded request, terminal, idempotency, and `PRResult` models with
canonical IDs, exact fixture lineage, and no external I/O.

### Phase 2: Eligibility and Redacted Body Assembly

Create pure validation of fresh PDR/approval/artifact/summary lineage and a
deterministic body renderer using only the RFC-004/005 publication whitelist.

### Phase 3: Controlled Fixture GitHub Adapter

Implement the sole adapter seam with injected opaque credential, pre-mutation
checks, no automatic retry, idempotency reconciliation, and bounded ambiguous
post-request terminals. Real mutation remains fixture-only.

### Phase 4: Acceptance and External-Effect Hardening

Prove allowed path limits, denied/approval/fault zero-mutation behavior,
idempotency replay, redaction, reset/audit procedure, and all exclusions.

## Acceptance

Each phase requires RED → GREEN → verification → independent review → focused
commit → completion record/progress update. Before any real GitHub mutation,
the exact feature-specific readiness gate and external-effect acceptance matrix
must be accepted.
