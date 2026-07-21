# Change: Controlled Materialization and Payload Simulation

## Why

M4 requires a governed bridge from metadata-only lineage to a deterministic,
locally verifiable commit payload without mistaking metadata references for
content or granting real GitHub mutation authority.

## Scope

- registered snapshot and transformer identities;
- separate materialization and payload-eligibility PDR scopes;
- ephemeral materialized bytes and `MaterializedCommitPayload` digest lineage;
- fixed-profile, network-disabled local Docker materialization and validation;
- deterministic fake Git-data simulation and zero-effect acceptance coverage.

## Non-goals

- caller-selected source/path/URL/checkout, free-form diff, template,
  replacement text, arbitrary script, LLM patch, persistent payload artifact,
  Git CLI, network, credential, real GitHub repository, branch/blob/tree/
  commit/ref/Draft PR write, or mutation-scoped PDR implementation.
