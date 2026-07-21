# Fixture GitHub Draft PR Adapter Specification

## ADDED Requirements

### Requirement: Mutation SHALL be fixture-bound and policy-gated

The adapter SHALL mutate only the registered fixture repository and Issue after
a fresh allowed PDR binds current repository, base revision, artifact, approval,
and idempotency lineage.

#### Scenario: Mismatched lineage blocks mutation

- **WHEN** any registered identity or fresh PDR binding differs
- **THEN** the adapter returns a bounded terminal and creates no branch, commit,
  or Draft PR

### Requirement: Draft PR publication SHALL be deterministic and redacted

The adapter SHALL derive the body solely from scanned/redacted structured facts
and SHALL exclude raw Issue, source, diff, patch, command output, credential,
path, and GitHub payload content.

#### Scenario: Unsafe body input blocks publication

- **WHEN** required redaction cannot be proved
- **THEN** no GitHub mutation occurs

### Requirement: External effects SHALL be idempotent

The adapter SHALL bind each allowed operation to one idempotency key and SHALL
not automatically retry an ambiguous GitHub request.

#### Scenario: Replayed key creates no new mutation

- **WHEN** the same valid key is replayed
- **THEN** the existing reconciled result is returned and no new branch, commit,
  or Draft PR is created
