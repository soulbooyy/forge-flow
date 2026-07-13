# Validation and Review Specification

## ADDED Requirements

### Requirement: M3 SHALL preserve M2 declarative-proposal boundaries

The capability SHALL accept only a supported successful `PatchProposal` by its
immutable `contract_id`. It SHALL NOT alter that proposal or treat candidate
paths, rationale, limitation codes, a proposal policy reference, or repository
configuration as execution authority. Every M3 terminal, result, and review
contract SHALL retain `patch_proposal_contract_id` lineage.

#### Scenario: A proposal cannot authorize simulated execution

- **GIVEN** a valid M2 `PatchProposal` whose policy reference is `allowed`
- **WHEN** M3 assembles a validation fixture flow
- **THEN** an independent M3 Policy Decision Record reference is required
- **AND** the proposal does not supply command text, an execution permit, or a
  workspace-access capability

### Requirement: Validation SHALL use separate completed and terminal envelopes

M3 SHALL expose `ValidationEnvelope = ValidationResult | ValidationTerminal`.
`ValidationResult` SHALL represent only a completed deterministic fixture
attempt with an attempt ID and controlled passed or failed facts.
`ValidationTerminal` SHALL represent only a governance terminal condition that
prevented an attempt, and SHALL contain no attempt ID, command claim, exit
code, output, report payload, or executed-command field. Exact fields,
controlled values, bounds, and canonical identity are normative in the M3
contract design.

#### Scenario: A blocked policy result does not claim execution

- **GIVEN** a valid proposal and a policy fixture result of `blocked`
- **WHEN** validation state is assembled
- **THEN** the result is a `ValidationTerminal` with terminal reason
  `policy_blocked`
- **AND** no `ValidationResult` or simulated attempt fact is emitted

#### Scenario: Approval-required validation remains terminal

- **GIVEN** a valid proposal and a policy fixture result of
  `requires_human_approval`
- **WHEN** validation state is assembled
- **THEN** the result is a `ValidationTerminal` with terminal reason
  `human_approval_required`
- **AND** it is not an approval record or permission to continue

### Requirement: Fixture attempts SHALL be deterministic and side-effect-free

M3 SHALL use only a bounded deterministic fixture or in-memory fake executor
to supply simulated attempt facts. The fixture and fake executor SHALL NOT
spawn a subprocess; inspect or mutate a workspace; read repository
configuration; access network, credentials, package installation, provider,
MCP, DeerFlow, Git, or PR capabilities; or emit raw command/output payloads.

#### Scenario: A completed fixture failure is not a repair request

- **GIVEN** an allowed policy fixture and a deterministic failed attempt case
- **WHEN** a `ValidationResult` is produced
- **THEN** it records only controlled failed facts and bounded references
- **AND** it contains no repair instruction, retry count, next-attempt
  directive, patch content, or changed-file directive

### Requirement: Review SHALL record findings but not governance decisions

`ReviewResult` SHALL consume only a valid `ValidationResult`, record bounded
findings with controlled severity and evidence references, and reference the
applicable Policy Decision Record. It SHALL NOT contain `blocked`,
`requires_human_approval`, approval, execution authorization, retry,
`approved_for_pr`, or PR-readiness fields. The policy fixture, not review,
selects the applicable policy outcome.

#### Scenario: A blocking finding cannot approve or block by itself

- **GIVEN** a `ReviewResult` with a blocking finding
- **WHEN** downstream policy evaluates that finding
- **THEN** the review records the finding and its evidence only
- **AND** a separate Policy Decision Record determines `blocked` or
  `requires_human_approval`

### Requirement: Lineage and persistence SHALL remain auditable and payload-free

The capability SHALL keep every M3 result and referenced Policy Decision Record
as an immutable independently identified contract. `ValidationResult`,
`ValidationTerminal`, and `ReviewResult` SHALL link using proposal contract ID,
attempt ID where present, policy-decision ID, artifact IDs, and
evidence-reference IDs. Artifact and evidence fields
SHALL contain only bounded identifiers, verification metadata, and safe
summaries; raw source, shell text, environment values, command output, logs,
reports, provider payloads, and credentials are forbidden.

#### Scenario: A fixture report cannot leak through artifact lineage

- **GIVEN** a fixture input with a raw output or report payload field
- **WHEN** M3 validates the fixture or contract input
- **THEN** it returns a separate safe validation error without copying or
  echoing the payload
- **AND** no successful, terminal, or review envelope is emitted

### Requirement: Invalid inputs SHALL use separate safe validation envelopes

The capability SHALL return the separate validation-error envelope defined by
the M3 contract design for unsupported proposal lineage, malformed fixture
data, an unknown fixture case or policy profile, an incompatible policy
decision, a dangling evidence or artifact reference, a forbidden payload field,
or unsupported review input. It SHALL contain no partial success, terminal, or
review fields and shall not initiate an attempt or fallback tool call.

#### Scenario: Review cannot run after validation terminal

- **GIVEN** a `ValidationTerminal`
- **WHEN** a caller requests a review
- **THEN** M3 returns a safe validation error
- **AND** it does not synthesize findings or change policy state

### Requirement: Fixtures SHALL prove contract boundaries before implementation

Before implementation, deterministic fixtures SHALL cover canonical identity
and lineage; passed and failed completed attempts; policy-blocked and
approval-required terminals; review severities and policy references; malformed
and forbidden-payload rejection; dangling references; absence of retry and
repair directives; and absence of subprocess, workspace, network, provider,
runtime, Git, or PR effects.

#### Scenario: Acceptance fixtures prove no execution surface

- **GIVEN** the complete M3 fixture suite
- **WHEN** acceptance checks complete
- **THEN** all terminal and result envelopes contain only the specified bounded
  contract data
- **AND** no command, sandbox, filesystem, network, dependency, provider,
  DeerFlow, Git, PR, or retry runtime has been invoked
