# Approval, Trace, and Durable Summary Design

## Design Review Record

Grill-Me Report mode required exact approval binding, metadata-only publication,
ForgeFlow-owned IDs, append-only redacted summaries, and fail-closed publication.

## Boundaries

`RedactedArtifactReferenceCandidate` is the only publication input. Feature 3
publishes immutable metadata artifacts and returns durable IDs; it never sees or
constructs source, diff, or patch content. Approval is an independent fact and
does not authorize publication, execution, commit, or PR by itself.

## Contract Shape

ApprovalRequest/Decision, MetadataArtifactReference, TraceEvent, and
DurableRunSummary are immutable, digest-identified contracts. Approval binds
subject, candidate/reference, base revision, policy profile, lineage digest,
decision and expiry. Summary stores bounded redacted references only.

The normative field direction and fail-closed rules are in
`contracts/m4-approval-trace-durable-summary-contract.md`.

## Security and Policy Boundary

The harness injects the sole artifact-store root. Paths never become durable
identity. Publication is temporary-write, atomic-publish, hash/ID verification;
any failure yields no reference or summary link. A fresh PDR remains the only
authorization for any later action.

## Failure and Stop Behavior

Expired/mismatched approval, ineligible candidate, profile mismatch, redaction
failure, store failure, or verification failure fail closed with no partial
eligible reference. No automatic retry occurs.
