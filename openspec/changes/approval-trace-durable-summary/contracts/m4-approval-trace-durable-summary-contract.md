# M4 Feature 3 Contract Direction

All contracts are frozen, canonical SHA-256 digest-identified facts. They
contain ForgeFlow-owned IDs, bounded enums, and redacted references only; never
raw source, diff, patch payload, command output, credential, environment value,
or filesystem path.

## ApprovalRequest and ApprovalDecision

ApprovalRequest contains `request_id`, subject contract ID, candidate/reference
ID, repository identity, base revision, policy-profile ID/version, lineage
digest, requested reason codes, and `expires_at`. ApprovalDecision contains
`decision_id`, request ID, lineage digest, `approved` or `denied`, and expiry.
It is invalid when expired or when any bound input differs. Neither fact is a
PolicyDecisionRecord or an execution/publication authorization.

## MetadataArtifactReference

Publication input is only Feature 2's eligible candidate. The output contains
`artifact_reference_id`, run ID, candidate ID, artifact metadata ID, content
digest, profile identity, and lineage digest. Its content is canonical bounded
metadata/reference data only. A local location is never included in the
contract or summary.

## TraceEvent and DurableRunSummary

TraceEvent has event ID, run ID, bounded event kind, referenced contract IDs,
and redacted bounded detail code. DurableRunSummary has run ID, summary ID,
ordered event/reference IDs, policy/approval/artifact lineage, bounded resource
facts, and final stop reason. It is append-oriented: published entries are not
rewritten.

## Bounds and Fail-closed Rules

The registered fixture policy supplies `max_artifact_bytes`; Feature 3 adds no
override. The harness supplies the sole store root. Candidate ineligibility,
profile mismatch, approval mismatch/expiry, redaction failure, temporary write,
atomic publish, hash verification, or append failure creates no eligible
reference and no partial summary linkage. Automatic retries are zero.
