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
- Raw command output, environment values, source, unredacted logs, credentials,
  and complete GitHub payloads are not durable records.
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
their raw payloads. Its minimum directional lineage is task/issue reference,
repository identity and fixed revision, `PatchProposal`, `PatchIntent`,
`PatchArtifact`, `SecretScanResult`, `CommandIntent`, `ExecutionAttempt`,
review evaluation, Policy Decision Records, Approval Requests/Decisions when
present, artifact references, Draft PR result, resource summary, retry policy,
and final stop reason.

Every persisted artifact must first pass the versioned redaction and size
policy. A failed scan/redaction operation cannot fall back to raw persistence.

## Open Questions

- What local artifact-store path, ownership, and atomic-write model will M4
  use?
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
