# Deterministic Patch Artifact and Security Scanning Specification

## ADDED Requirements

### Requirement: Patch intent and artifact SHALL remain metadata-only facts

The capability SHALL derive an immutable `PatchIntent` from immutable upstream
lineage and SHALL deterministically construct a metadata-only `PatchArtifact`
against the bound repository identity and fixed base revision. A PatchArtifact
SHALL describe target scope and change lineage only; it SHALL NOT contain a
diff, source material, patch content, application state, or authorization for
patch materialization, execution, commit, PR, or persistence.

#### Scenario: Metadata construction produces no workspace side effect

- **GIVEN** valid registered fixture lineage and a valid PatchProposal
- **WHEN** the capability constructs a PatchArtifact
- **THEN** the result binds the PatchIntent, repository identity, and base
  revision through immutable lineage
- **AND** it creates no workspace mutation, command, OCI call, commit, branch,
  PR, or artifact-store object

### Requirement: Identity and lineage SHALL be deterministic and payload-free

Every Feature 2 fact SHALL use canonical serialization and a digest-derived
identity, preserving its required upstream lineage. Contracts and errors SHALL
exclude raw patch, raw diff, raw source, raw command output, credentials,
environment values, and temporary workspace paths.

#### Scenario: Forbidden raw payload is rejected safely

- **GIVEN** input containing a forbidden raw-payload field
- **WHEN** the capability validates it
- **THEN** it returns only the bounded validation-error envelope
- **AND** it copies neither the rejected value nor a partial contract

### Requirement: Security rules SHALL be profile-owned and fact-producing

The capability SHALL obtain scanner/redaction rule-set identity, version,
metadata-field allowlist, deterministic detection/redaction behavior, and
applicable path budgets only from the accepted M4 Patch Metadata Security
Profile and registered versioned fixture policy profile. `SecretScanResult` and
`RedactionFact` SHALL record security facts and SHALL NOT evaluate or substitute
for a PolicyDecisionRecord.

#### Scenario: Input cannot choose a security rule set

- **GIVEN** a PatchIntent, PatchArtifact, Issue-derived value, or agent value
  naming a different rule set or budget
- **WHEN** the capability validates the registered profile lineage
- **THEN** it returns a bounded validation error
- **AND** no scan, candidate reference, workspace mutation, or external side
  effect occurs

#### Scenario: Metadata-only rule set yields deterministic facts

- **GIVEN** metadata containing a value that matches one registered blocking
  rule in an allowlisted field
- **WHEN** the capability scans and redacts the metadata projection
- **THEN** it emits an ordered bounded finding summary and a `blocked` scan fact
- **AND** it exposes no matched text, raw metadata projection, patch material,
  source material, or candidate reference

### Requirement: Unsafe security outcomes SHALL fail closed

The capability SHALL yield no `RedactedArtifactReferenceCandidate` for scanner
failure, redaction failure, indeterminate security result, or a blocked secret
finding. A later PDR consuming any of those results SHALL be `blocked` under
the registered fixture profile; the capability SHALL NOT convert them to
approval required.

#### Scenario: Indeterminate scan cannot reach approval or publication

- **GIVEN** a PatchArtifact whose registered scan produces `indeterminate`
- **WHEN** the capability records the security fact
- **THEN** it produces no candidate reference
- **AND** it performs no application, persistence, commit, PR, or approval
  action

### Requirement: Metadata redaction SHALL remain pre-persistence before Feature 3

Feature 2 SHALL NOT generate, render, retain, or persist raw patch material,
raw diff, or source material. It SHALL scan and redact only bounded metadata;
it SHALL NOT persist a partial redacted object, a path, or a durable reference.
Only a passed metadata scan and successful metadata redaction MAY produce an
in-memory candidate for Feature 3 publication.

#### Scenario: Redaction failure leaves no eligible artifact

- **GIVEN** a metadata-only PatchArtifact whose redaction fails
- **WHEN** the capability records the RedactionFact
- **THEN** it produces no candidate or partial artifact-store object
- **AND** no patch material, diff, or source material enters a contract,
  summary, log, or external publication
