# Validation and Review Slice Design

## Design Review Record

Grill-Me review was completed before this change. The accepted outcomes are
recorded in ADR-008 and applied here: fixture identity is not authority;
policy-stopped flows have no simulated execution facts; artifacts and evidence
are references rather than raw payloads; review is not approval; and retry is
not part of any M3 result contract.

## Boundaries

M3 consumes an immutable successful M2 `PatchProposal` by `contract_id` only.
It must not alter the proposal, reread M1 context, infer source content, or
turn a candidate change into a command.

`ValidationResult` records only facts from a completed deterministic fixture
attempt. `ValidationTerminal` records why no validation attempt occurred due
to a governance terminal condition. `ReviewResult` records findings over a
completed `ValidationResult`; it references a Policy Decision Record but never
selects its result.

All envelopes are independent, immutable contracts. Their lineage uses
`PatchProposal.contract_id`, an attempt ID where an attempt completed, Policy
Decision Record IDs, and bounded artifact/evidence references. The complete
field and identity rules are normative in
[the M3 contract design](contracts/milestone-3-validation-review-contract.md).

## Contract Shape

```text
ValidationEnvelope = ValidationResult | ValidationTerminal

PatchProposal
  -> PolicyDecisionRecord reference
  -> ValidationResult | ValidationTerminal
  -> ReviewResult (ValidationResult only)
  -> PolicyDecisionRecord reference
```

A deterministic fixture or fake executor may produce only the controlled
attempt facts needed for a `ValidationResult`. It cannot produce a terminal
policy decision, select a policy profile, create an artifact payload, or
execute a command. Policy fixtures independently produce the referenced policy
decisions.

## Security and Policy Boundary

The fake executor is in-memory and deterministic. It must not spawn a process,
inspect or mutate a workspace, access repository configuration, network,
credentials, package installation, provider/MCP/DeerFlow runtime, Git, or PR
integration. M3 has no command text, working directory, exit code, stdout,
stderr, environment value, or raw report field.

The only modeled policy results are `allowed`, `blocked`, and
`requires_human_approval`. A policy profile selects the outcome. `blocked`
emits a `ValidationTerminal` with no attempt ID; `requires_human_approval`
emits a distinct `ValidationTerminal` with no attempt ID. Neither is approval
or permission to continue. An `allowed` decision may be paired only with a
deterministic fixture attempt in M3; it does not authorize future execution.

Repository configuration may be represented only as an untrusted declarative
hint in a future change. It has no input or authorization role in M3.

## Failure and Stop Behavior

- Unsupported, absent, or incompatible M2 proposal lineage, malformed fixture
  data, dangling evidence/artifact reference, unknown policy profile, or
  incompatible policy reference returns a separate safe validation/review
  contract validation error; no partial success is emitted.
- A `blocked` or `requires_human_approval` policy result produces its matching
  `ValidationTerminal`, not a `ValidationResult`, fake exit code, fake output,
  or fake executed-command claim.
- A completed fixture attempt may produce a passed or failed
  `ValidationResult`; failed is an observed fixture fact, not a repair request
  or retry instruction.
- `ReviewResult` is produced only from a valid completed `ValidationResult`.
  It cannot be emitted from a terminal validation flow, and it cannot alter a
  policy outcome.
- No M3 result contains retry count, next-attempt directive, repair plan,
  patch instruction, approval field, or PR readiness field.
