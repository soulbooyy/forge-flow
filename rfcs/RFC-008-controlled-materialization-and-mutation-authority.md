# RFC-008: Controlled Materialization and Mutation Authority

## Status

Draft

## Context

M4 Features 1–4 establish governed execution facts, metadata-only patch
security, durable metadata lineage, and a fail-closed Draft-PR adapter seam.
They deliberately do not authorize source access, patch materialization, or a
real GitHub mutation. A commit requires controlled content bytes, but a
Feature 3 metadata reference does not prove that such bytes exist or are
authorized.

## Decision Direction

Introduce a separate capability with three non-interchangeable authorities:

- **materialization authority** permits one registered transformer to operate
  on one verified, harness-injected source snapshot;
- **payload eligibility authority** permits fake local mutation simulation for
  one completed materialized payload; and
- **real mutation authority** is future-only and must use a separate,
  mutation-scoped fresh PDR.

No earlier PDR may be reused, inherited, or elevated into real mutation
authority. A real adapter must reject `forgeflow-sim-*` identities and every
materialization/payload-eligibility PDR.

## v1 Boundary

- Accept only one registered fixture repository, locked base SHA, and
  harness-injected `repository_id + base_sha + snapshot_digest` identity.
- Reject caller paths, directories, URLs, checkouts, symbolic refs, and any
  snapshot/target digest mismatch; never fall back to the current workspace or
  network retrieval.
- Use a registered, versioned transformer selected only by
  `transformation_id + transformation_version + target_file_id +
  expected_input_digest`. A manifest contains no source, diff, replacement
  text, template, script, or dynamic transformation language.
- Execute materialization only in a fixed-image, network-disabled Docker
  sandbox with empty environment, no credentials, read-only snapshot mount,
  harness-owned temporary output, and the Feature 1 resource profile.
- Reuse only Feature 1's registered validation command and profile. Validation
  facts never authorize eligibility or mutation.
- Keep materialized bytes and the non-serializable payload handle transient to
  one harness lifecycle. They cannot enter contracts, artifact stores, logs,
  or DurableRunSummary.
- Permit only deterministic local fake Git-data simulation. Its IDs use the
  `forgeflow-sim-*` namespace and are not Git/GitHub object IDs.

## Contracts

`RegisteredSourceSnapshot` is an internal registration/harness fact.
`TransformationManifest`, `MaterializationPDR`, `MaterializedCommitPayload`,
and `PayloadEligibilityPDR` are immutable, digest-identified contracts.
`target_file_id` is resolved by the controlled registry to a canonical
repository-relative path; adapters must not reinterpret it.

Every PDR SHALL carry a controlled `authority_kind` enum, a unique attempt ID,
an issued-at/expiry interval, and exact immutable bindings. The enum values
are non-overlapping: `materialization`, `payload_eligibility`, and the
future-only `real_mutation`.

- A `materialization` PDR binds repository ID, locked base SHA, snapshot
  digest, transformation ID/version, target-file ID, expected input digest,
  and the Feature 1 profile ID/version.
- A `payload_eligibility` PDR binds repository ID, locked base SHA,
  `MaterializedCommitPayload` identity, all materialized output digests, and
  the exact security, validation, and review fact references used to decide
  eligibility.
- A future `real_mutation` PDR has a separately defined schema and binds a
  future mutation attempt and provider-facing payload identity. It is outside
  v1 and cannot be synthesized from either earlier PDR.

A real-mutation request schema SHALL accept only a fresh `real_mutation` PDR.
It SHALL neither import nor deserialize materialization or payload-eligibility
PDR types, and SHALL reject those authority kinds and all `forgeflow-sim-*`
identities before an adapter/provider call.

`MaterializedCommitPayload` contains only file identity, pre/post digests,
security/validation/review references, lineage, and PDR identities. It never
contains content bytes, diff, path, or handle.

## Failure and Retry

The controlled terminal vocabulary is:

| Terminal | Trigger | Permitted durable fields | Retry rule |
| --- | --- | --- | --- |
| `source_revalidation_failed` | registered repository, base SHA, snapshot, target-file, or input digest does not exactly match | attempt ID, registered identities, expected/observed digest identifiers, controlled reason code | manual only; new attempt and fresh materialization PDR |
| `materialization_not_authorized` | materialization PDR is absent, stale, denied, or not exact-scope-bound | attempt ID, PDR ID/status, registered identities, controlled reason code | manual only; new attempt and fresh materialization PDR |
| `materialization_failed` | registered transformer, sandbox output, or output digest/allowlist check fails | attempt ID, transformer/target identities, input/output digest identifiers, bounded security facts, controlled reason code | manual only; new attempt and fresh materialization PDR |
| `validation_failed` | the registered validation command completes with a failing assertion/result | attempt ID, validation profile reference, bounded execution fact, exit classification, controlled reason code | manual only; new attempt and fresh scope-matched PDRs |
| `validation_infrastructure_failed` | sandbox, fixed profile, image, runner, or bounded execution setup is unavailable or cannot produce an execution fact | attempt ID, validation profile reference, bounded infrastructure classification, controlled reason code | manual only; new attempt and fresh scope-matched PDRs |
| `payload_not_eligible` | payload-eligibility PDR is absent, stale, denied, or not exactly bound to the completed payload | attempt ID, payload identity, PDR ID/status, controlled reason code | manual only; new attempt and fresh payload-eligibility PDR |
| `simulation_binding_failed` | handle is expired or any handle/payload/digest/repository/base/PDR binding differs | attempt ID, payload identity, registered identities, controlled reason code | manual only; new attempt, fresh scope-matched PDRs, and new handle |
| `real_mutation_rejected` | a simulation identity or a materialization/payload PDR reaches a real mutation surface | attempt ID, rejected identity class, controlled reason code | not retriable by this capability; future real mutation needs a new mutation-scoped attempt and PDR |

The permitted fields never include bytes, diff text, paths, a handle, command
output, credentials, or scanner match text. Automatic retries are zero.
Validation assertion failure remains distinct from validation infrastructure
failure.

## Non-goals

No real GitHub repository use, credentials, branch/blob/tree/commit/ref/Draft
PR write, Git CLI, remote write, arbitrary transformer, LLM patch, free-form
diff, persistent payload artifact, retention, or encryption is included.
