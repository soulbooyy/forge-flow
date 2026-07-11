# ADR-004: Use Immutable Deterministic Repository Context Contracts

## Status

Accepted

## Context

ADR-002 established that Milestone 1 uses a deterministic Repository Context Service rather than a Repository Context Agent. The `repository-context-foundation` OpenSpec revision refined that direction into a stronger contract boundary: Repository Context Service produces a deterministic `RepositoryContextResult` or a separate validation error envelope.

This decision affects more than the Milestone 1 implementation. Later patch, validation, review, PR, audit, and workflow-state artifacts will need to reference repository context without mutating it or treating it as authorization. Future contributors may reasonably ask whether `RepositoryContextResult` can be amended with validation outcomes, policy decisions, patch state, PR state, runtime metadata, or storage references. That ambiguity should be resolved at the architecture-decision level, not only in the OpenSpec schema.

The accepted OpenSpec also supersedes ADR-002's earlier allowance for optional Milestone 1 symbol hints. Symbol hints are deferred from Milestone 1 and require a future OpenSpec change.

## Decision

ForgeFlow treats `RepositoryContextResult` as an immutable, deterministic, non-authorizing product contract.

After creation, `RepositoryContextResult` must not be modified in place, appended to, or extended with later-stage state. Later artifacts may reference its `contract_id` and `evidence_ref.id` values, but they must carry their own schemas, identities, and authority boundaries.

`RepositoryContextResult` is context and evidence only. It does not authorize additional reads, command execution, test execution, edits, patches, commits, branches, PR creation, memory operations, network access, or external side effects. Later stages must perform their own OpenSpec-authorized policy checks.

ForgeFlow uses deterministic contract identity for repository context. `contract_id` is derived from canonical serialization of deterministic contract content and excludes the `contract_id` field itself. Deterministic configuration identity and caller-supplied logical workspace identity participate in the contract identity. Deterministic coverage changes, including limitations, skipped coverage, truncation, and run-summary counts, are part of the contract identity.

Validation failures are separate contract envelopes, not partial `RepositoryContextResult` objects. Validation error identity is separate from successful result identity.

## Alternatives Considered

- Allow later stages to mutate `RepositoryContextResult`: rejected because it would make `contract_id` unreliable and blur repository context with workflow scratch state.
- Treat repository context as an authorization record: rejected because policy authority belongs to later policy and workflow stages, not context retrieval.
- Use implementation-defined stable IDs: rejected because implementation-local stability is insufficient for fixture comparison, audit references, and cross-implementation consistency.
- Keep symbol hints as optional Milestone 1 contract output: rejected after Grill-Me review because optional symbol hints introduce ambiguous extraction, scoring, evidence, and fixture semantics.

## Consequences

Positive consequences:

- Later workflow artifacts can safely reference repository context without changing it.
- Contract identity remains stable, inspectable, and suitable for regression fixtures.
- Repository context cannot silently become policy, validation, patch, or PR state.
- Future additions such as symbol hints, semantic ranking, or mutable workflow annotations require explicit OpenSpec review.

Negative consequences / trade-offs:

- Later stages must create separate artifacts instead of enriching the context result in place.
- More up-front care is required for canonical serialization and identity rules.
- Some convenience metadata must remain outside the contract or in separate non-authoritative debug channels.

