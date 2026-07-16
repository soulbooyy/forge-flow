# M4 Contract Design: Deterministic Patch Artifact and Security Scanning

## Shared Rules

`PatchIntent`, `PatchArtifact`, `SecretScanResult`, and `RedactionFact` are
immutable facts. Their IDs are canonical-serialization digests; a timestamp,
random UUID, agent-generated identifier, path, or runtime object must not be
the sole identity or lineage key. Contracts contain references and bounded
metadata, never raw patch content, raw diff, raw source, raw command output,
credentials, environment values, or temporary workspace paths.

Neither a successful contract nor `RedactedArtifactReferenceCandidate` grants
write, execution, commit, PR, persistence, or approval authority. A later
action requires a fresh PDR over its current inputs.

## PatchIntent

Required minimum fields:

- `contract_version`;
- `repository_identity` and `base_revision` bound to the registered fixture;
- `intent_id`;
- `target_scope`;
- `change_description`; and
- `lineage_digest` binding the originating PatchProposal and the listed input
  facts.

`target_scope` contains at most 10 sorted unique slash-separated logical paths,
each at most 512 Unicode code points, without an absolute, drive-prefixed,
backslash, or parent-escaping form. `change_description` is single-line metadata
of at most 1,000 Unicode code points, not source, diff, or patch content. The
contract must not contain authorization, approval, execution
permission, write permission, an applied-workspace assertion, or a persistent
artifact reference.

## PatchArtifact

Required minimum fields:

- `artifact_id`;
- `repository_identity` and `base_revision`;
- `patch_intent_id`;
- `target_scope`;
- `metadata_digest`; and
- `lineage_digest` binding the PatchIntent, repository identity, base revision,
  policy-profile identity, and metadata digest.

It is a metadata-only change artifact fact deterministically constructed from
the referenced `PatchIntent`. It must not contain `raw_patch_content`, raw
diff, source material, commit hash, pull-request URL, execution status,
workspace path, or an assertion that the patch was applied.

## SecretScanResult

Required minimum fields:

- `scan_id`;
- `artifact_id`;
- `rule_set_id: "m4-patch-metadata-secret-scan-v1"` and
  `scanner_version: "deterministic-metadata-scanner-v1"`, both supplied by the
  accepted M4 Patch Metadata Security Profile;
- `result`, one of `passed`, `blocked`, `failed`, or `indeterminate`;
- bounded `findings_summary`; and
- `failure_reason` when the result is `failed` or `indeterminate`.

`findings_summary` contains only structured, ordered, unique pairs of a
registered rule ID and an allowlisted metadata field name, at most one per pair;
it has no free-text member and never contains matched text. `passed` requires
an empty finding tuple; `blocked` requires a non-empty finding tuple; and
`failed` or `indeterminate` require an empty finding tuple plus a controlled
safe failure code. `blocked` is a security fact meaning that the scanner found
content which the profile treats as unsafe. It is not a PDR outcome and does
not by itself authorize or perform a stop; the next PDR consumes that fact and
is required to be `blocked` under the registered profile.

## RedactionFact

Required minimum fields:

- `redaction_id`;
- `input_artifact_id`;
- `output_artifact_digest` only when a redacted output was successfully
  produced;
- `rule_set_id: "m4-patch-metadata-redaction-v1"` supplied by the accepted M4
  Patch Metadata Security Profile; and
- `status`, exactly `not_needed`, `redacted`, `failed`, or `indeterminate`.

A failed or indeterminate redaction must not create an output digest that can
be used as a candidate reference. A candidate exists only for a `passed` scan
and `not_needed` redaction; a `redacted` result from a blocked scan remains
ineligible.

## RedactedArtifactReferenceCandidate

This is a Feature 2 in-memory eligibility fact, not a durable contract or
artifact-store object. It has `contract_version`, a deterministic `candidate_id`,
the PatchArtifact ID, SecretScanResult ID, RedactionFact ID, redacted metadata
digest, lineage digest, and applicable profile/rule-set identity. It may exist
only when the scoped metadata scan passed and redaction completed successfully.
It cannot contain a filesystem path, raw artifact payload, raw diff, or source
material. Feature 3 alone may publish it and assign a ForgeFlow-owned durable
artifact reference.

## Validation Error Envelope

Invalid lineage, unknown or mismatched registered profile/rule-set identity,
forbidden payload field, malformed metadata-construction input, or a path-bound
violation returns `deterministic_patch_artifact_security_validation_error`. It contains
only a schema version, digest-derived error ID, bounded error code, and one
controlled safe summary template; it returns no raw rejected value or partial
success contract.
