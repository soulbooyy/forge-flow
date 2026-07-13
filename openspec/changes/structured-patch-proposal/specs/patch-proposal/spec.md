# Patch Proposal Specification

## ADDED Requirements

### Requirement: PatchProposal SHALL be an evidence-backed, non-authorizing contract

The capability SHALL accept only a successful, supported
`RepositoryContextResult` and bounded task input. A successful response SHALL
be a tagged `PatchProposal` envelope with a schema version, immutable contract
identity, `repository_context_contract_id`, bounded root-cause hypotheses, one
bounded fix strategy, ordered candidate changes, risk flags, limitations, and
evidence references. Every hypothesis and candidate change SHALL reference one
or more evidence IDs present in the referenced repository-context contract.
It SHALL record `proposal_source_id: "m2/deterministic-fixture-v1"`,
`policy_profile_id: "patch-proposal/m2-conservative-v1"`, and
`policy_version: 1`.

The successful envelope SHALL use `schema_version: "patch-proposal/v1"` and
`contract_id: "pp_sha256:<lowercase-hex>"`; its exact required fields,
controlled values, field bounds, ordering, and canonical identity behavior are
normative in the M2 contract design. The contract ID SHALL hash the canonical
successful payload with only `contract_id` omitted.

The proposal SHALL NOT authorize reading, writing, command execution, test
execution, network access, memory access, branch creation, commit creation,
PR creation, approval reuse, or policy bypass. It SHALL NOT mutate the
referenced repository-context contract.

#### Scenario: A proposal retains evidence lineage
- **GIVEN** a valid repository-context contract with evidence references
- **WHEN** a proposal identifies a candidate changed file
- **THEN** that candidate references only evidence IDs from the input contract
- **AND** the proposal records the input `repository_context_contract_id`
- **AND** no raw source payload is added to either contract

### Requirement: PatchProposal SHALL remain declarative and diff-free in this change

Candidate changes SHALL identify only canonical workspace-relative paths,
controlled change kinds, bounded rationale, and evidence references. They
SHALL NOT include raw unified diffs, file contents, edit commands, shell
commands, byte offsets, executable patches, or provider-specific tool calls.

#### Scenario: A proposal is not an edit permit
- **GIVEN** a proposal with an `allowed` boundary assessment
- **WHEN** a later component considers editing the workspace
- **THEN** it still requires a new policy-evaluated Level 1 Action Intent
- **AND** no edit occurs through this capability

### Requirement: Patch boundary assessment SHALL be explicit and non-bypassing
The capability SHALL evaluate candidate paths and declared scope against an
accepted M2 patch-boundary policy profile before it emits a successful proposal.
The assessment SHALL reference a Policy Decision Record whose result is exactly
`allowed`, `blocked`, or `requires_human_approval`.

`blocked` proposals SHALL not be emitted as successful proposals. A
`requires_human_approval` result SHALL be recorded as a risk/stop condition and
SHALL NOT be interpreted as approval. An `allowed` result SHALL remain scoped
to this declarative proposal and SHALL NOT authorize a later diff, edit,
command, or side effect.

The assessment SHALL enforce the candidate, hypothesis, rationale, change-kind,
blocked-path, approval-required-path, and re-evaluation rules in
[`m2-patch-proposal-v1`](../../policy-profiles/m2-patch-proposal-v1.md). A
future profile SHALL use a new profile identity or version; this profile's
behavior SHALL NOT be changed silently.

#### Scenario: Sensitive candidate path requires escalation
- **GIVEN** a candidate change whose path matches an accepted sensitive-path rule
- **WHEN** the boundary policy evaluates the proposal
- **THEN** the assessment is `requires_human_approval` or `blocked` according
  to that policy profile
- **AND** the proposal does not claim authorization to modify the path

### Requirement: Invalid input SHALL use a separate validation envelope
The capability SHALL return a validation envelope for unsupported context schema
versions, missing repository-context contract IDs, dangling evidence references,
empty hypotheses, malformed bounded task input, or an unavailable policy profile:
`result_type: "patch_proposal_validation_error"`. The validation envelope
SHALL contain no successful proposal fields and SHALL use a bounded safe error
summary.

The validation envelope SHALL use
`schema_version: "patch-proposal-validation-error/v1"` and
`error_id: "ppe_sha256:<lowercase-hex>"`. Its error ID SHALL hash the canonical
error payload with only `error_id` omitted. It SHALL use only the controlled
error codes, input categories, and bounded summary fields in the M2 contract
design.

#### Scenario: Missing evidence stops proposal creation
- **GIVEN** a candidate change that cites an evidence ID absent from the input context
- **WHEN** proposal validation runs
- **THEN** the capability returns a patch-proposal validation error
- **AND** it does not reread the workspace or emit a partial proposal

### Requirement: Fixtures SHALL precede implementation and prove boundary preservation

Before implementation, controlled fixtures SHALL cover successful evidence
lineage, canonical ordering and identity, invalid context envelopes, dangling
evidence rejection, empty or unsupported task input, sensitive-path escalation,
candidate-size boundary results, exact high-risk path-segment matching,
environment-file escalation, deletion escalation, raw-payload avoidance,
absence of workspace mutation, absence of command/network/memory calls, and
rejection of diff or tool-call fields.

#### Scenario: Fixtures prove no side effects
- **GIVEN** a fixture proposal run
- **WHEN** acceptance checks complete
- **THEN** the workspace snapshot is unchanged
- **AND** no subprocess, sandbox edit, test, network, memory, Git, or PR tool
  has been invoked
