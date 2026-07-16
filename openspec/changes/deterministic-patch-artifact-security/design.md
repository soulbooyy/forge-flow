# Deterministic Patch Artifact and Security Scanning Design

## Design Review Record

Grill-Me Report mode challenged five failure modes: treating an artifact as an
applied workspace fact, treating a scan result as authorization, inventing a
diff renderer without source authority, leaking Feature 3 persistence into this
slice, and allowing a failure or indeterminate result to reach approval. The
accepted answers are respectively: no application occurs; only a fresh PDR can
authorize a later action; Feature 2 constructs metadata only and defers patch
materialization; Feature 3 owns publication and durable references; and the
registered profile fail-closes all of those security outcomes as `blocked`.

## Boundaries

The feature consumes an immutable M2 `PatchProposal`, registered fixture
repository identity, fixed base revision, and versioned fixture policy profile.
It derives a `PatchIntent`, constructs a metadata-only `PatchArtifact`, and
emits security facts scoped to that bounded metadata.

```text
PatchProposal
  -> PatchIntent
  -> PatchArtifact
  -> SecretScanResult + RedactionFact
  -> optional RedactedArtifactReferenceCandidate
```

The candidate is not a persisted artifact, filesystem location, patch payload,
publication event, or authority. Feature 3 may later consume an eligible
candidate through its controlled store boundary. A later accepted feature with
explicit source-access and application authority alone may materialize or apply
a patch; no Feature 2 contract implies that a repository workspace changed.

## Contract Shape

Every contract is immutable and identity-bound through canonical UTF-8 JSON
serialization and SHA-256 digest. Identity inputs exclude runtime timestamps,
random UUIDs, agent-generated identifiers, raw patch payloads, raw source, raw
command output, credentials, environment values, and temporary workspace paths.
References use ForgeFlow-owned IDs or digests rather than filesystem paths.

The normative minimum fields and forbidden data are in
[the Feature 2 contract](contracts/m4-deterministic-patch-artifact-security-contract.md).
The OpenSpec does not introduce a scanner/redaction rule set: identity, version,
metadata-field allowlist, detection, and redaction behavior must come from the
accepted [M4 Patch Metadata Security Profile](../../../docs/fixtures/m4-patch-metadata-security-profile.md).

## Security and Policy Boundary

`SecretScanResult` and `RedactionFact` record only scoped facts. They cannot
allow, block, approve, execute, write, commit, or publish an artifact. The
registered profile fixes scanner failure, redaction failure, any indeterminate
security result, and a blocked finding as `blocked`; none may be represented as
`requires_human_approval` or yield an artifact-reference candidate.

Feature 2 never creates raw patch material, a diff, or source material. Scanner
and redactor inputs are bounded contract metadata only; those inputs never
enter a contract, artifact store, summary, log, PR body, or error payload. A
successful candidate proves only that Feature 3 may later evaluate publication.
A future materialization, write, execution, commit, or PR action needs explicit
later authority and a new PDR over its current inputs.

## Failure and Stop Behavior

- invalid lineage, unsupported registered profile/rule set, forbidden payload,
  malformed metadata-construction input, or path-bound violation returns a
  bounded validation error and no partial contract;
- scanner failure, blocked secret finding, or indeterminate security result
  emits the applicable scan fact, no candidate, and must be consumed as
  `blocked` by a later fresh PDR;
- redaction failure emits the applicable redaction fact, no candidate, and must
  be consumed as `blocked` by a later fresh PDR; and
- Feature 2 never retries, materializes or applies a patch, writes a workspace,
  persists an artifact, invokes an OCI backend, or invokes GitHub.
