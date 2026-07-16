# Governed Action and Sandbox Boundary Design

## Design Review Record

Grill-Me design challenge completed before this change. It tested four boundary
failures: treating the approved image as authorization, treating an image shell
as a general command capability, recording absent execution facts, and falling
back to host execution when OCI constraints cannot be proved. The accepted
answers are: the Policy Decision Record alone authorizes the current intent;
only the exact fixture command is capable; `not_started` carries no image,
exit-code, or output fact; and lack of proof produces `sandbox_unavailable`
before a mutation. These outcomes are consistent with RFC-002, RFC-004, and
ADR-011 and are normative in this change.

## Boundaries

The feature consumes only immutable lineage references: a normalized fixture
`TaskInput` ID, allowlisted repository ID, fixed base revision, registered
policy profile, and approved OCI image identity. It does not retrieve an Issue,
read repository configuration as authority, create a patch, or mutate GitHub.

`ActionIntent` is declarative. `CommandIntent` is a policy-constrained rendering
of that intent, not permission. A fresh `PolicyDecisionRecord` is the sole
authorization decision. `ExecutionAttempt` records actual lifecycle facts only.
The OCI adapter is an infrastructure seam: ForgeFlow owns policy, contracts,
lineage, and terminal semantics; Docker/Podman or another conforming backend
only supplies the isolated capability.

The OCI seam separates pre-start capability proof from execution: the backend
first returns a bounded `OciCapabilityProof`, and only a fully proven backend
may receive `run(CommandIntent)`. This prevents a post-start proof failure from
being rewritten as a false `not_started` fact.

The execution service receives an explicit immutable evaluated-input tuple:
`ActionIntent`, `CommandIntent`, and `PolicyDecisionRecord`, plus the injected
OCI execution environment. It does not evaluate a new policy decision, read a
repository or workspace to infer current state, inspect an approval store, or
accept a policy outcome from a backend. It validates the supplied references
and common immutable lineage, then treats the PDR as the sole authorization
fact for that exact tuple. This makes the execution-layer gate directly
testable: `blocked`, approval-required, and stale-base PDRs cannot reach the
adapter.

## Contract Shape

```text
TaskInput reference + fixture repository/revision
  -> ActionIntent
  -> CommandIntent (exact registered command + OCI digest)
  -> fresh PolicyDecisionRecord
  -> execute_governed_attempt(ActionIntent, CommandIntent, PDR, OciBackend)
  -> ExecutionAttempt
```

Every contract is immutable and contains `schema_version`, `contract_id`,
`run_id`, and `created_at`. `ActionIntent` also has `action_id`; an attempt has
`attempt_id`. Contract IDs use the existing canonical UTF-8 JSON / SHA-256
identity convention, with the ID field omitted before hashing. `created_at` is
an immutable audit field but is excluded from deterministic identity.

The complete fields, controlled values, optional-fact conditions, and error
envelopes are normative in
[the M4 governed-action/sandbox contract](contracts/m4-governed-action-sandbox-contract.md).

## Security and Policy Boundary

The fixture policy profile grants exactly one structured capability:
`fixture-test-runner-v1` = `python3 -m unittest discover -s tests` from
`workspace_root`, with no environment entries, a 120000 ms timeout, and a
65536-byte output limit. Every command value, policy profile version,
repository and OCI image digest must match the registered inputs exactly. A
repository, command, profile, or image mismatch is `policy_blocked`; a stale
base revision instead produces `requires_human_approval` and a
`not_started`/`base_revision_mismatch` attempt. Timeout or any declared budget
exhaustion is `resource_limit_exceeded`.

For a started attempt, the OCI adapter must prove an image pinned to the
registered digest, no network, no credential injection, no dynamic dependency
installation, a temporary isolated workspace fixed to the registered revision,
workspace-only writes, and no artifact-store mount. It destroys that workspace
at attempt end. An adapter backend that cannot prove any condition returns
`sandbox_unavailable`; it may not use a host process or any permissive
fallback.

No contract persists raw command output, environment, credentials, workspace
paths, raw source, or unredacted artifact content. This first feature has no
artifact store or redaction implementation: output may be held transiently only
to enforce the output budget and determine terminal facts, then is discarded;
its `artifact_ref_ids` are empty. A later trace/store change may introduce
bounded redacted artifact references. The image registration is a read-only
external input; it neither grants execution nor permits a different image.

## Failure and Stop Behavior

- `blocked` produces a `not_started` attempt with `policy_blocked`; it has no
  image, exit code, output, workspace, or started timestamp. The execution
  service returns this fact directly from the injected PDR and does not call
  the backend.
- `requires_human_approval` produces a `not_started` attempt with
  `approval_required`; it creates no approval record, does not call the
  backend, and does not continue.
- A stale base revision produces `requires_human_approval` plus a
  `not_started` attempt with `base_revision_mismatch`. It produces no sandbox
  mutation, GitHub mutation, artifact publication, exit code, resource
  observation, or execution artifact reference. A later human-approved run
  must create new ActionIntent, CommandIntent, and PolicyDecisionRecord lineage
  bound to the current revision; the old attempt remains immutable. The stale
  fact is supplied by the PDR/current-input preparation path, not inferred by
  the OCI adapter.
- A missing, unregistered, mismatched, or unprovable OCI capability produces
  `not_started` with `sandbox_unavailable`, before any execution or external
  mutation. This capability taxonomy never includes a repository base-revision
  mismatch.
- A started execution may end only as `succeeded`, `failed`, `cancelled`, or
  `timed_out`; non-success requires the applicable bounded failure reason. A
  cancelled attempt must have started and uses only `cancelled_by_request`; it
  is not a command failure and creates no retry.
- Base-revision mismatch and resource-limit exhaustion use their existing
  RFC-002 failure reasons and stop later work. Parser and redaction failures
  are reserved for their owning later features; this change has no parser or
  redaction capability and must not emit either reason.
- There is no automatic retry: `max_automatic_retries` is `0`. A later run
  needs new immutable intent, decision, and attempt lineage; it cannot reuse
  an old authorization.
