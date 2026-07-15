# Governed Action and Sandbox Specification

## ADDED Requirements

### Requirement: Intent SHALL remain separate from authorization and execution

The capability SHALL construct immutable `ActionIntent` and `CommandIntent`
only from the registered fixture lineage and exact policy-profile capability.
Neither intent SHALL authorize execution. A fresh immutable
`PolicyDecisionRecord` over the current CommandIntent lineage SHALL be the only
authorization decision source.

#### Scenario: A declarative action cannot start a command

- **GIVEN** a valid ActionIntent and CommandIntent
- **WHEN** no fresh PolicyDecisionRecord is present
- **THEN** no ExecutionAttempt starts
- **AND** the capability does not create a workspace, process, or external side
  effect

### Requirement: Command capability SHALL be exact and fixture-specific

The capability SHALL accept only `fixture-test-runner-v1` with the exact
executable, ordered arguments, workspace-root directory, empty environment,
120000 ms timeout, and 65536-byte output limit specified in the M4 fixture
policy profile. It SHALL bind CommandIntent to the approved OCI image digest.

#### Scenario: Command variation is blocked

- **GIVEN** an ActionIntent requesting an extra argument, shell wrapper,
  environment entry, alternate working directory, or different image
- **WHEN** policy evaluates the intent
- **THEN** the PolicyDecisionRecord outcome is `blocked`
- **AND** any resulting attempt is `not_started` with `policy_blocked`

### Requirement: OCI execution SHALL prove the controlled boundary

For an allowed current CommandIntent, the ForgeFlow-owned OCI adapter SHALL
prove the registered image digest, no network, no credential injection, no
dynamic dependency installation, isolated fixed-revision temporary workspace,
workspace-only writes, and absence of an artifact-store mount. It SHALL destroy
the workspace after the attempt. It SHALL NOT fall back to a host process,
DeerFlow sandbox, or a backend default.

#### Scenario: An unprovable backend fails closed

- **GIVEN** an allowed CommandIntent and a backend that cannot prove one OCI
  boundary condition
- **WHEN** the adapter evaluates capability
- **THEN** the attempt is `not_started` with `sandbox_unavailable`
- **AND** no command, GitHub mutation, or host fallback occurs

### Requirement: Stale base revision SHALL require a new governed evaluation

A stale base revision SHALL produce a fresh PolicyDecisionRecord outcome of
`requires_human_approval` and an ExecutionAttempt of `not_started` with
`base_revision_mismatch`. It SHALL produce no sandbox mutation, GitHub
mutation, artifact publication, exit code, resource observation, or execution
artifact reference. A later human-approved execution SHALL use new immutable
intent and decision contracts bound to the current revision; it SHALL NOT
reuse the stale attempt or authorization.

#### Scenario: Stale revision preserves fact and governance separately

- **GIVEN** a CommandIntent whose base revision is no longer the registered
  current revision
- **WHEN** policy evaluates its current lineage
- **THEN** the PolicyDecisionRecord is `requires_human_approval`
- **AND** the ExecutionAttempt is `not_started` with
  `base_revision_mismatch` and no execution facts

### Requirement: ExecutionAttempt SHALL record only observed lifecycle facts

The capability SHALL emit `ExecutionAttempt` using the contract shape in the
M4 governed-action/sandbox contract. It SHALL separate PolicyDecisionRecord
outcome from attempt status and SHALL not fabricate image, exit-code, output,
workspace, or timestamp facts.

#### Scenario: Approval-required flow has no execution facts

- **GIVEN** a fresh PolicyDecisionRecord with outcome
  `requires_human_approval`
- **WHEN** the feature records the terminal state
- **THEN** the attempt is `not_started` with `approval_required`
- **AND** it contains no image, exit-code, output, workspace, or approval
  decision record

### Requirement: Failures and budgets SHALL stop without retry

The capability SHALL represent only its applicable RFC-002 bounded failure
reasons; `parser_failed` and `redaction_failed` SHALL NOT be emitted because
this change owns neither capability. Timeout and declared resource exhaustion
SHALL use `resource_limit_exceeded`; there SHALL be zero automatic retries. A
later run SHALL create new intent, decision, and attempt lineage rather than
reuse prior authorization.

#### Scenario: Controlled cancellation is not command failure

- **GIVEN** an allowed attempt that has actually started
- **WHEN** a controlled cancellation request terminates it
- **THEN** its status is `cancelled` and its only failure reason is
  `cancelled_by_request`
- **AND** no retry, `command_failed` fact, or external mutation occurs

#### Scenario: Output budget exhausts before later work

- **GIVEN** an allowed started attempt whose output exceeds 65536 bytes
- **WHEN** the adapter enforces the profile budget
- **THEN** the attempt records `resource_limit_exceeded`
- **AND** no subsequent commit, Draft PR, retry, or external mutation occurs

### Requirement: Contract persistence SHALL be payload-free and auditable

All successful contracts SHALL use canonical immutable IDs and ForgeFlow-owned
lineage references. ExecutionAttempt SHALL emit the exact bounded resource
observations defined in the M4 contract design and `artifact_ref_ids: []`. This
change SHALL NOT persist raw command output, environment, credentials,
workspace paths, raw source, runtime objects, or unredacted artifacts. Invalid
inputs SHALL return only the bounded validation-error envelope.

#### Scenario: A raw output field is rejected safely

- **GIVEN** a contract input containing a raw command-output payload field
- **WHEN** the capability validates that input
- **THEN** it returns `governed_action_sandbox_validation_error`
- **AND** it copies neither the rejected value nor a partial attempt into the
  result
