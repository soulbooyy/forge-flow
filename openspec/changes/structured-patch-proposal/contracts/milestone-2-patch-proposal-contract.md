# Milestone 2 Contract Design: Structured PatchProposal

## Purpose

This reference makes the accepted M2 OpenSpec implementable without allowing an
implementation phase to invent schema, identity, or policy-reference behavior.
It is subordinate to the M2 OpenSpec change.

## Tagged Envelope Union

```text
PatchProposalEnvelope = PatchProposal | PatchProposalValidationError
```

Success has `result_type: "patch_proposal"`. Validation failure has
`result_type: "patch_proposal_validation_error"`; it never contains a partial
proposal, candidate changes, risk flags, or policy decision reference.

## PatchProposal

Required fields:

- `schema_version`: `"patch-proposal/v1"`
- `result_type`: `"patch_proposal"`
- `contract_id`: `pp_sha256:<lowercase-hex>`
- `proposal_source_id`: `"m2/deterministic-fixture-v1"`
- `repository_context_contract_id`: `rcr_sha256:<lowercase-hex>`
- `task_input`: `TaskInput`
- `root_cause_hypotheses`: non-empty `RootCauseHypothesis[]`
- `fix_strategy`: `FixStrategy`
- `candidate_changes`: non-empty `CandidateChange[]`
- `risk_flags`: `RiskFlag[]`, possibly empty
- `limitation_codes`: `LimitationCode[]`, possibly empty
- `policy_decision`: `PolicyDecisionRef`

Rules:

- the contract is frozen, non-authorizing, and contains no raw source, diff,
  shell text, command output, provider payload, prompt, absolute path,
  environment value, runtime trace, timestamp, run ID, or mutable workflow state;
- every supporting or candidate evidence ID resolves to the referenced M1
  context result; the proposal does not copy that evidence payload;
- `policy_decision.decision: "blocked"` is represented only by a validation
  error with `error_code: "policy_blocked"`, never a successful proposal;
- `requires_human_approval` is a successful declarative proposal with the
  `policy_requires_human_approval` risk flag; it is not an approval artifact.

### TaskInput

Required fields:

- `task_ref`: safe caller-supplied logical reference, 1–128 Unicode code points
- `summary`: NFC-normalized, trimmed, whitespace-collapsed task summary,
  1–1,000 Unicode code points

The summary is bounded task context, not a raw issue payload, source payload,
or provider prompt. It does not authorize workspace access.

### RootCauseHypothesis

Required fields:

- `statement`: 1–500 Unicode code points
- `uncertainty`: `"low" | "medium" | "high"`
- `supporting_evidence_ref_ids`: non-empty sorted tuple of M1 evidence IDs

Hypotheses sort by `statement` in Unicode code-point order, then `uncertainty`,
then their evidence-ID tuple. At most three occur in one proposal.

### FixStrategy

Required fields:

- `summary`: 1–1,000 Unicode code points
- `constraint_codes`: sorted tuple containing exactly `"evidence_backed"`,
  `"minimal_change"`, `"no_execution"`, and `"policy_bounded"`

### CandidateChange

Required fields:

- `path`: canonical workspace-relative path
- `change_kind`: `"modify_existing_file" | "add_test_file" |
  "add_non_sensitive_file" | "remove_file"`
- `rationale`: 1–500 Unicode code points
- `supporting_evidence_ref_ids`: non-empty sorted tuple of M1 evidence IDs

Candidates sort by `path`, then `change_kind`, then `rationale`. At most three
occur in one proposal. Candidate paths, kinds, and ordering are the policy
evaluation input; a later edit still needs its own Level 1 Action Intent.

### RiskFlag and LimitationCode

`RiskFlag` values are exactly `"policy_requires_human_approval"`,
`"environment_path"`, `"high_risk_path"`, `"deletion_intent"`, and
`"policy_profile_revalidation_required"`. They are sorted and unique.

`LimitationCode` values are exactly `"fixture_only_source"`,
`"no_source_payload"`, `"no_diff_generated"`, and `"no_validation_executed"`.
They are sorted and unique.

### PolicyDecisionRef

Required fields:

- `decision_id`: `pdr_sha256:<lowercase-hex>`
- `decision`: `"allowed" | "requires_human_approval"`
- `policy_profile_id`: `"patch-proposal/m2-conservative-v1"`
- `policy_version`: integer `1`
- `evaluator_id`: `"m2/deterministic-boundary-evaluator-v1"`
- `evaluated_candidate_digest`: `sha256:<lowercase-hex>`
- `risk_flags`: sorted unique `RiskFlag[]`
- `revalidation_required`: boolean `true`

`evaluated_candidate_digest` is SHA-256 over canonical JSON for the ordered
candidate `(path, change_kind, rationale)` tuples. `decision_id` is SHA-256 over the
canonical PolicyDecisionRef payload with `decision_id` omitted. Any change to
ordered candidate paths/kinds/rationales, policy profile ID/version, evaluator ID,
decision, or risk flags produces a different `decision_id`; the old decision
cannot be reused.

## PatchProposalValidationError

Required fields:

- `schema_version`: `"patch-proposal-validation-error/v1"`
- `result_type`: `"patch_proposal_validation_error"`
- `error_id`: `ppe_sha256:<lowercase-hex>`
- `completion_status`: `"validation_error"`
- `error_code`: `ValidationErrorCode`
- `input_category`: `"repository_context" | "task_input" | "proposal_draft" |
  "policy_profile" | "candidate_change"`
- `message`: bounded safe message, at most 500 Unicode code points
- `summary`: `ValidationErrorSummary`

`ValidationErrorCode` values are exactly `"unsupported_repository_context"`,
`"dangling_evidence_ref"`, `"empty_hypotheses"`, `"invalid_task_input"`,
`"invalid_candidate_change"`, `"invalid_change_kind"`, `"bounds_exceeded"`,
`"invalid_policy_profile"`, `"policy_blocked"`, `"fixture_draft_malformed"`,
and `"raw_payload_forbidden"`.

`ValidationErrorSummary` contains only `repository_context_contract_id` when
available, `task_ref` when available, and `policy_profile_id` when available.
It contains no raw task summary, source content, or provider payload.

## Canonical Identity

Canonical JSON uses UTF-8, lexicographic object-key ordering, compact
separators, integers only, explicit required empty arrays, omitted absent
optional fields, and deterministic array ordering stated above. Floats and
unknown object values are validation failures.

`PatchProposal.contract_id` is `pp_sha256:` plus SHA-256 of its canonical
payload with `contract_id` omitted. Its hash includes all required success
fields, including task input, evidence references, limitations, and policy
decision reference.

`PatchProposalValidationError.error_id` is `ppe_sha256:` plus SHA-256 of the
canonical error payload with `error_id` omitted.

## Design Review Record

Grill-Me challenged circular identity, hidden provider authority, blocked versus
approval-required outcomes, stale policy reuse, payload leakage, and unordered
claims. The design resolves them through independent policy-decision identity,
separate failure envelopes, explicit revalidation, fixture-only source identity,
strict payload exclusions, and deterministic ordering.
