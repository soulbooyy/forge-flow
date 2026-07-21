# Controlled Materialization and Payload Simulation Specification

## ADDED Requirements

### Requirement: Source SHALL be harness-registered and revalidated

The capability SHALL accept only a harness-injected registered snapshot bound
to repository ID, locked base SHA, and snapshot digest. It SHALL reject caller
paths, directories, URLs, checkouts, symbolic refs, mismatched snapshots, and
all fallback source selection.

#### Scenario: Snapshot mismatch blocks materialization

- **WHEN** the injected snapshot or target file differs from its registered digest
- **THEN** the capability returns a controlled terminal and creates no payload

### Requirement: Materialization SHALL use only registered transformers

The manifest SHALL contain only registered transformer/target/input identities.
It SHALL contain no source, diff, replacement text, template, script, or
dynamic transformation language.

#### Scenario: Unregistered transformer blocks materialization

- **WHEN** a manifest selects an unregistered transformer or wrong input digest
- **THEN** the capability returns a controlled terminal and creates no payload

### Requirement: Authorities SHALL be fresh and non-elevatable

Materialization and payload-eligibility SHALL each require a fresh, exact,
scope-specific PDR. A materialization PDR SHALL bind the verified source and
registered transformation inputs only; a payload-eligibility PDR SHALL bind
the completed payload identity and its facts only. Neither SHALL authorize
real mutation. Each PDR SHALL contain a non-overlapping `authority_kind`,
unique attempt ID, and issued-at/expiry interval. The allowed authority kinds
are `materialization`, `payload_eligibility`, and future-only `real_mutation`.
The v1 types SHALL not represent `real_mutation`.

#### Scenario: Prior PDR cannot authorize real mutation

- **WHEN** a materialization or payload-eligibility PDR is presented to a real
  mutation surface
- **THEN** that surface rejects it fail-closed

### Requirement: Real mutation schemas SHALL be isolated from v1 PDRs

A future real-mutation request schema SHALL accept only a fresh PDR whose
authority kind is `real_mutation`. It SHALL not import or deserialize the v1
materialization or payload-eligibility PDR types, and SHALL reject those kinds
and `forgeflow-sim-*` identities before an adapter or provider call.

#### Scenario: Structurally similar v1 PDR is rejected by a real mutation schema

- **WHEN** a materialization or payload-eligibility PDR is supplied where a
  real-mutation PDR is required
- **THEN** schema validation rejects it before adapter construction

### Requirement: Payload bytes SHALL remain ephemeral

Materialized bytes and payload handles SHALL remain harness-private and
single-lifecycle. `MaterializedCommitPayload` SHALL contain only identities,
digests, lineage, and fact references.

#### Scenario: Expired handle blocks fake simulation

- **WHEN** the handle expires or its payload/repository/base/digest/PDR binding differs
- **THEN** fake simulation returns a controlled terminal and performs no effect

### Requirement: Terminals SHALL be controlled and non-sensitive

The capability SHALL use the controlled terminal vocabulary defined by RFC-008.
Each terminal SHALL persist only its documented bounded fields and SHALL have
zero automatic retries. A manual retry SHALL create a new attempt, fresh
scope-matched PDRs, and a new ephemeral handle. Validation failure and
validation infrastructure failure SHALL remain distinct terminals.

#### Scenario: Infrastructure failure is distinct from a validation failure

- **WHEN** the fixed validation sandbox or runner cannot create an execution fact
- **THEN** the capability returns `validation_infrastructure_failed`, not
  `validation_failed`, and retains no command output or payload bytes

### Requirement: Simulation SHALL not be a provider mutation

The fake adapter SHALL produce only deterministic `forgeflow-sim-*` identities.
Those identities SHALL not enter real mutation request schemas, provider-facing
contracts, or real adapter import surfaces.

#### Scenario: Simulation identity is rejected by real mutation surface

- **WHEN** a `forgeflow-sim-*` identity is supplied to a real mutation surface
- **THEN** the surface rejects it fail-closed
