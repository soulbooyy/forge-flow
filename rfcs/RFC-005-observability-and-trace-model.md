# RFC-005: Observability and Trace Model

## Status

Draft

## Context

M4 is the first ForgeFlow slice with controlled execution and GitHub Draft PR
side effects. Runtime state, DeerFlow checkpoints, sandbox output, and GitHub
responses cannot become product-layer truth or an unbounded persistence path.

## Current Draft Decisions

- ForgeFlow owns the durable audit model; `DurableRunSummary` is the sole
  product-layer summary for a run.
- M4 persists only append-oriented, bounded contract IDs, policy and approval
  lineage, redacted artifact references, execution terminal state, resource
  summary, and Draft PR result.
- The local controlled artifact store is outside the target repository and
  workspace. It stores immutable references and redacted artifacts only.
- The local controlled harness injects the only artifact-store root; paths from
  users, agents, Issues, or repository configuration cannot select or redirect
  it. ForgeFlow-owned IDs, not paths, are durable artifact identities.
- Raw command output, environment values, source, unredacted logs, credentials,
  and complete GitHub payloads are not durable records.
- A fixture Issue is normalized into a redacted immutable `TaskInput`; only its
  Issue identity, content hash, redacted task summary, and adapter/evidence
  references may enter durable lineage.
- DeerFlow state and checkpoints are transient or recovery inputs only; any
  promotion into a ForgeFlow summary requires explicit mapping and redaction.

## Goals

- Define M4 trace, artifact, redaction, and durable-summary ownership.
- Preserve lineage from issue/task input through policy, execution, review, and
  Draft PR side effects.
- Make failure, approval, idempotency, resource, and stop information auditable
  without retaining raw sensitive payloads.

## Non-goals

- Implement a remote artifact backend, encryption, retention service, or access
  control system.
- Treat runtime checkpoints, GitHub responses, or provider payloads as durable
  ForgeFlow contracts.
- Define a dashboard, telemetry vendor, or production SRE monitoring system.

## M4 Durable Summary Boundary

A `DurableRunSummary` must reference immutable contracts rather than embed
their raw payloads. Its minimum directional lineage is `TaskInput` / Issue
reference,
repository identity and fixed revision, `PatchProposal`, `PatchIntent`,
`PatchArtifact`, `SecretScanResult`, `CommandIntent`, `ExecutionAttempt`,
review evaluation, Policy Decision Records, Approval Requests/Decisions when
present, artifact references, Draft PR result, resource summary, retry policy,
and final stop reason.

Every persisted artifact must first pass the versioned redaction and size
policy. A failed scan/redaction operation cannot fall back to raw persistence.

### M4 Local Controlled Artifact Store

The ForgeFlow-owned local controlled harness injects one artifact-store root
outside both the target repository and sandbox workspace. Each run receives an
independent, non-colliding directory below that root. M4 permits only creation
of immutable artifacts and append-oriented summary/event records; it does not
permit mutation of an already published artifact.

Artifact publication is fixed to this fail-closed sequence:

```text
generate -> scan/redact -> temporary write -> atomic publish
         -> content-hash and ForgeFlow-owned-ID verification
```

Only a successfully published object may receive an artifact reference. Any
failure leaves no partial object eligible for contract lineage, summary
reference, commit creation, or Draft PR packaging. Durable references are
identified primarily by ForgeFlow-owned run ID, artifact ID, contract ID, and
Policy Decision Record ID; a filesystem path is a resolvable implementation
location, never the sole identity.

M4 deliberately excludes deletion and retention behavior, remote backends,
encryption, and multi-tenant access control. Those are enterprise-governance
requirements for a later OpenSpec and must not be inferred from this local MVP
store.

### M4 Layered Terminal Audit Boundary

`DurableRunSummary` must preserve the distinction between governance decision,
execution fact, finding, and external side effect by referencing their
immutable contracts rather than flattening them into one status. It must record
the referenced `PolicyDecisionRecord.outcome` (`allowed`,
`requires_human_approval`, or `blocked`) separately from the referenced
`ExecutionAttempt.status` (`succeeded`, `failed`, `cancelled`, `timed_out`, or
`not_started`). A non-successful attempt's bounded failure reason is one of
`policy_blocked`, `approval_required`, `sandbox_unavailable`,
`command_failed`, `parser_failed`, `redaction_failed`,
`base_revision_mismatch`, or `resource_limit_exceeded`.

The summary may reference `SecretScanResult`, `ReviewResult`, approval
artifacts, and `PRResult`, but must not reinterpret a finding as authorization
or an absent external side effect as an execution failure. It records a
redacted, bounded stop reason and contract lineage sufficient to distinguish
policy prevention, approval wait, execution failure, and Draft PR adapter
failure without persisting raw command output, source, credentials, or GitHub
payloads.

### M4 Task-Input Audit Boundary

The only M4 external task input is a pre-registered Issue read by the
ForgeFlow-owned GitHub adapter from the single fixture repository. The durable
record may reference the normalized `TaskInput` contract, Issue identity,
content hash, expected base revision, and adapter/evidence reference. It must
not persist the raw Issue body or complete GitHub response. This preserves
input lineage without creating a general external-data ingestion or retention
path.

## Open Questions

- Which bounded execution/resource fields are required for the first summary
  schema?
- Which summary fields are safe to publish in a Draft PR body?
- What retention, encryption, access-control, and remote-backend policy is
  required before enterprise repository onboarding?

## M4 Readiness Preconditions

Before an M4 OpenSpec may introduce persistence or a Draft PR adapter, it must
define exact contract fields, artifact identity, redaction failure semantics,
size bounds, and the mapping from runtime events to ForgeFlow-owned durable
records. It must not make a DeerFlow checkpoint or GitHub payload authoritative.

## Decision Summary

ForgeFlow owns a bounded, redacted, append-oriented durable audit summary and
local controlled artifact store. Runtime and external-tool payloads remain
transient unless explicitly transformed into those ForgeFlow-owned contracts.
