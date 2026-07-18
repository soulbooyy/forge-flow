# Re-baselined Phase 2: Transient Metadata Security Facts

## Goal

Implement profile-owned, deterministic security facts over a bounded transient
metadata projection anchored by `PreScanPatchMetadataIdentity`.

## Scope

- Scan only the accepted projection fields and record rule ID/field-name facts.
- Redact only in memory and return a digest, never projection text or a match.
- Treat profile mismatch, invalid projection, and any non-exact/tampered scan as
  `indeterminate` and ineligible for all later paths.
- Return no `PatchIntent`, `PatchArtifact`, candidate, terminal envelope,
  persistence object, or external side effect.

## TDD and Verification

- RED: the terminal-first policy tests failed against the historical
  intent/artifact-first API.
- GREEN: the policy suite passes 7/7.
- Cumulative implemented tests (Phase 1 contracts/canonical plus Phase 2
  policy) pass 16/16. Strict OpenSpec validation, diff hygiene, and the static
  no-I/O boundary check pass.

## Independent Review Gate

- Independent review required: Yes — this phase modifies the security boundary
  and profile-owned security fact generation.
- Subagent used: Yes — the user approved independent review for Phase 2.
- Review outcome: One P1 was corrected. Redaction now verifies the complete,
  expected scan fact before handling a result, so a self-consistent forged
  `failed` scan cannot manufacture a failed redaction fact; it yields only
  `indeterminate`.

## Scope Confirmation

No raw projection, matched text, source, diff, patch material, command output,
credentials, environment values, paths, candidate, `PatchIntent`,
`PatchArtifact`, terminal envelope, execution, approval, persistence, OCI,
GitHub, retry, network, or workspace mutation was added.
