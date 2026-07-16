# M4 Patch Metadata Security Profile

## Purpose

This controlled, versioned supplement to the registered M4 fixture policy
profile defines Feature 2 security facts over bounded change-artifact metadata
only. It never receives, accesses, generates, or persists raw source, raw diff,
patch material, command output, credentials, environment values, or workspace
paths.

## Identity and Scope

```yaml
profile_id: forgeflow-m4-patch-metadata-security
profile_version: 1
secret_scan_rule_set_id: m4-patch-metadata-secret-scan-v1
scanner_version: deterministic-metadata-scanner-v1
redaction_rule_set_id: m4-patch-metadata-redaction-v1
```

The only scanner input is the canonical, bounded UTF-8 metadata projection of
these fields:

```text
PatchIntent.target_scope
PatchIntent.change_description
PatchArtifact.target_scope
```

All identifiers, digests, repository identity, base revision, policy identity,
lineage fields, paths, raw payload fields, and unknown fields are excluded from
the projection. An input that cannot be projected exactly is `indeterminate`;
it is not scanned permissively.

The immutable contract bounds the projection before scanning: at most 10
slash-separated target-scope paths of at most 512 Unicode code points, a
single-line `change_description` of at most 1,000 code points, and bounded
rule-ID/field finding summaries only. These bounds exclude multiline raw
source/diff representations before the scanner receives metadata.

## Deterministic Secret-like Detection Rules

Rules run in the stated order over each allowlisted string field. Every match
records only the rule ID and field name as a structured, ordered, unique
finding pair; matched text is never retained in any contract, candidate, log,
or error. A passed scan has no findings, a blocked scan has at least one, and a
failed or indeterminate scan has none plus its controlled safe reason code.

| Rule ID | Deterministic match | Severity |
| --- | --- | --- |
| `private-key-marker` | Case-sensitive `-----BEGIN ` followed by uppercase letters, spaces, or digits, then `PRIVATE KEY-----` | blocking |
| `github-token-prefix` | A token beginning `ghp_`, `gho_`, `ghu_`, `ghs_`, or `ghr_`, followed by 20 or more ASCII letters or digits | blocking |
| `credential-assignment` | Case-insensitive identifier `api_key`, `apikey`, `access_token`, `secret`, `password`, or `token`, followed by `:` or `=`, optional whitespace, and 8 or more non-whitespace characters | blocking |
| `jwt-like-token` | Three dot-separated URL-safe base64url segments, each at least 8 characters, whose first segment starts `eyJ` | blocking |

The profile reports at most one finding per `(rule_id, field_name)` pair, ordered
by rule-table order then field-name order. It has no low-confidence or
approval-eligible result.

## Scan Result Semantics

| Result | Deterministic condition | Candidate eligibility |
| --- | --- | --- |
| `passed` | Every allowlisted field projects successfully and no rule matches. | Eligible only after `not_needed` redaction. |
| `blocked` | One or more blocking rules match. | Never eligible. |
| `failed` | The scanner cannot complete its declared deterministic evaluation because its own required operation fails. | Never eligible. |
| `indeterminate` | Projection is incomplete, a field is not valid bounded UTF-8 text, or the active profile/rule-set identity does not exactly match this record. | Never eligible. |

`failed`, `indeterminate`, and `blocked` are security facts. Under the
registered fixture profile, any later PDR that consumes one is `blocked`.
None may be converted to `requires_human_approval`.

## Deterministic Metadata Redaction

The redactor consumes only the same projected metadata and the ordered scan
findings. It replaces each matched span with the literal
`[REDACTED:<rule_id>]`, applying rules in scan order and replacing overlapping
spans once using the earlier rule. It then canonical-serializes the redacted
metadata projection and exposes only its SHA-256 digest; it never returns or
persists the redacted projection itself.

`RedactionFact.status` is exactly one of:

| Status | Condition |
| --- | --- |
| `not_needed` | Scan passed and canonical metadata needs no replacement. |
| `redacted` | One or more replacements completed. This never makes a blocked scan candidate-eligible. |
| `failed` | The redactor cannot complete its declared deterministic operation. |
| `indeterminate` | Projection, finding lineage, or rule-set identity cannot be proved exact. |

An output digest exists only for `not_needed` or `redacted`. A candidate exists
only for `SecretScanResult.result: passed` with `RedactionFact.status:
not_needed`; a redacted blocked result remains ineligible.

## Authority and Status

This profile is the only Feature 2 metadata security rule source. The M4
fixture registration remains the authority for budgets and fail-closed PDR
outcomes. Any rule or scope change requires a new profile version and OpenSpec
reconciliation; repository, Issue, user, agent, or artifact inputs cannot
override it.

```yaml
status: Accepted # Draft | Accepted
readiness_blocker: None. Feature 2 OpenSpec and canonical-plan gates remain required.
```

## References

- [M4 Fixture Environment Registration](m4-fixture-environment-registration.md)
- [RFC-004: Sandbox and Security Governance](../../rfcs/RFC-004-sandbox-and-security-governance.md)
- [Feature 2 contract](../../openspec/changes/deterministic-patch-artifact-security/contracts/m4-deterministic-patch-artifact-security-contract.md)
