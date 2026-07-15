# M4 Contract Design: Governed Action and Sandbox Boundary

## Shared Rules

All successful contracts in this change are immutable and contain
`schema_version: "m4-governed-action-sandbox/v1"`, `contract_id`, `run_id`, and
`created_at`. `created_at` is an RFC-002-required immutable RFC 3339 UTC audit
timestamp, but is omitted from identity hashing. IDs use
`<kind>_sha256:<lowercase-hex>` and are SHA-256 over canonical UTF-8 JSON with
the ID field omitted: lexicographic object keys, compact separators, integer
numbers only, explicit required empty arrays, omitted absent optional fields,
and OpenSpec-defined deterministic array ordering. No raw command output,
environment, credential, workspace path, raw source, runtime object, or
unredacted artifact is valid in any contract.

Every reference is an immutable ForgeFlow-owned ID, not a filesystem path or
runtime object. `evidence_ref_ids` and `artifact_ref_ids`, where allowed, are
sorted unique IDs only. A contract with two identity-named fields states their
relationship explicitly; for a Policy Decision Record, both identity fields
are omitted before its hash is calculated.

## ActionIntent

Required fields:

- `contract_id`: `ai_sha256:<lowercase-hex>`;
- `action_id`: `action_sha256:<lowercase-hex>` derived from the same canonical
  payload as `contract_id`;
- `kind`: exactly `"execute_fixture_test"`;
- `task_input_contract_id`, `repository_id`, and `base_commit_sha`;
- `requested_command_id`: exactly `"fixture-test-runner-v1"`; and
- `policy_profile_id: "forgeflow-m4-fixture-only"` and
  `policy_profile_version: "1.0.0"`.

It is declarative and cannot contain command text, an approval, a Policy
Decision Record outcome, an OCI image, workspace access, or execution fact.

## CommandIntent

Required fields:

- `contract_id`: `ci_sha256:<lowercase-hex>`;
- `action_intent_contract_id`, `repository_id`, and `base_commit_sha` matching
  the referenced ActionIntent;
- `command_id: "fixture-test-runner-v1"`;
- `executable: "python3"`;
- `args`: exactly `["-m", "unittest", "discover", "-s", "tests"]`;
- `working_directory: "workspace_root"` and `allowed_environment: []`;
- the approved registered `oci_image_digest`;
- `timeout_ms: 120000` and `max_output_bytes: 65536`; and
- the same policy-profile ID and version as the ActionIntent.

No extra argument, shell wrapper, environment entry, dynamic value, image tag,
or substitute image is valid. CommandIntent construction itself does not start
an attempt.

## PolicyDecisionRecord

Required fields:

- `contract_id` and `decision_id`, both `pdr_sha256:<lowercase-hex>` and
  exactly equal;
- `subject_contract_id` naming the CommandIntent;
- `input_lineage_digest: sha256:<lowercase-hex>` over the referenced current
  ActionIntent, CommandIntent, repository/base revision, policy profile, and
  registered image identity;
- policy-profile ID/version, sorted `reason_codes`, sorted `evidence_ref_ids`,
  `outcome`, and `evaluated_at`;
- `outcome`: exactly `"allowed" | "requires_human_approval" | "blocked"`.

It is the only authorization source. Any changed input requires a new record;
an old `allowed` record is never reusable authorization.

## ExecutionAttempt

Required fields:

- `contract_id`: `ea_sha256:<lowercase-hex>`;
- `attempt_id: attempt_sha256:<lowercase-hex>`;
- `command_intent_contract_id` and `policy_decision_contract_id`;
- `status`: exactly `"succeeded" | "failed" | "cancelled" | "timed_out" |
  "not_started"`; and
- `resource_observations` with these integer fields: `wall_clock_ms`
  (0–600000), `sandbox_lifetime_ms` (0–480000), `command_output_bytes`
  (0–65536), `workspace_write_bytes` (0–10485760), `artifact_bytes: 0`,
  `diff_bytes: 0`, `changed_files: 0`, and `tool_call_count` (0 when not
  started; 1 when the OCI adapter starts the sole command), plus sorted unique
  `limits_reached` values from the registered profile; and
- `artifact_ref_ids: []`. This feature has no artifact-store or redaction
  capability, so it never emits an output artifact reference.

`failure_reason` is required exactly when status is non-successful and is one
of RFC-002's M4 failure reasons. This feature may emit only
`policy_blocked`, `approval_required`, `sandbox_unavailable`,
`base_revision_mismatch`, `command_failed`, `resource_limit_exceeded`, and
`cancelled_by_request`;
`parser_failed` and `redaction_failed` are reserved for their owning later
features. A `not_started` attempt has no OCI image
digest, exit code, workspace reference, or started timestamp. A started attempt
carries the registered image digest and may carry an integer exit code and
started/finished timestamps only after those facts occur. Output is transiently
bounded and discarded; it is never a contract field or artifact reference in
this change. `status: "cancelled"` requires and permits only
`failure_reason: "cancelled_by_request"`; that reason requires a started
attempt and never authorizes retry.

## Validation Error Envelope

Invalid lineage, unsupported schema/profile/command, an image identity
mismatch, forbidden payload field, invalid fact combination, or dangling
reference returns `governed_action_sandbox_validation_error`. It contains
`schema_version`, `error_id: gase_sha256:<lowercase-hex>`, bounded
`error_code`, and a bounded safe summary. It has no partial success contract,
raw rejected value, Policy Decision Record, or attempt fact.
