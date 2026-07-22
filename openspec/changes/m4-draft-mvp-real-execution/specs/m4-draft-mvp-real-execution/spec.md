# M4 Draft-MVP Real Execution Specification

## ADDED Requirements

### Requirement: Real mutation SHALL require independent authority

A real-mutation request SHALL require a fresh mutation-scoped PDR. It SHALL
reject materialization and payload-eligibility PDRs, their structural forms,
and every `forgeflow-sim-*` identity before adapter construction.

#### Scenario: v1 authority reaches real request construction

- **WHEN** a v1 PDR or simulation identity is supplied
- **THEN** the request is rejected before an adapter is built

### Requirement: External effects SHALL be separately gated

The capability SHALL perform no Docker process, credential use, GitHub request,
branch, commit, or Draft PR until the corresponding readiness matrix is
explicitly accepted.

#### Scenario: external gate is absent

- **WHEN** a local Docker or fixture-mutation gate is not accepted
- **THEN** the relevant external adapter cannot be invoked

### Requirement: Allowed path SHALL remain fixture-only and bounded

The sole accepted end-to-end scenario SHALL target only the registered fixture
repository/base/Issue and create at most one branch, one commit, and one Draft
PR per idempotency key; all other paths have zero external effects.

#### Scenario: a replayed allowed request arrives

- **WHEN** the same accepted idempotency key is replayed
- **THEN** no additional branch, commit, or Draft PR is created
