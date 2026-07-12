# RFC-007: DeerFlow Extension Strategy

## Status

Draft

RFC-007 is an RFC-001 acceptance precondition. RFC-001 should not become Accepted until RFC-007 defines the extension boundary between DeerFlow runtime foundations and ForgeFlow product-layer behavior.

Review stage: Grill-Me feedback has been incorporated as current draft decisions. RFC-007 remains Draft until pinned DeerFlow revision, extension-point capability assumptions, state mapping boundary, policy attachment feasibility, no-core-modification rule, and minimal Milestone 1 integration scope are documented.

## Current Draft Decisions

- ForgeFlow may depend on documented DeerFlow extension points, but undocumented DeerFlow dependencies must be recorded as integration assumptions.
- DeerFlow must be pinned before Milestone 1 implementation begins, preferably as a Git submodule under `third_party/deer-flow`, or with an equivalent immutable commit reference.
- Milestone 1 acceptance must not depend on local DeerFlow core modifications, temporary patches, or unmerged DeerFlow patches.
- ForgeFlow structured contracts and Durable Run Summary are authoritative product-layer state.
- DeerFlow messages, runtime state, and checkpoints may only carry mapped runtime state, transient context, recoverable references, or explicitly mapped contract-derived data.
- RFC-007 must include a DeerFlow extension-point capability assessment for RFC-004 policy attachment feasibility.
- Milestone 1 DeerFlow work must stay minimal and limited to read-only Repository Context assumptions, pinning/reference, no-core-modification proof, and documented limitations.
- Full workflow graph integration, role runtime implementation, write/test sandbox integration, approval pause/resume, PR side effects, and full checkpoint mapping are deferred to later milestones.
- RFC-007 must define RFC-001 DeerFlow Extension Acceptance Criteria and remain Draft until those criteria are documented.
- RFC-007 records its current DeerFlow revision and Milestone 1 extension-point assessment in `docs/architecture/assessments/deerflow-extension-points.md`.

## Context

ForgeFlow is built on DeerFlow and LangGraph, but its goal is not to rename DeerFlow, copy DeerFlow source, or modify DeerFlow internals without an explicit boundary. ForgeFlow is an enterprise autonomous software engineering agent platform focused on software maintenance workflows.

DeerFlow provides framework foundations such as:

- agent runtime foundations
- graph / workflow execution foundations
- thread / conversation foundations
- tool orchestration foundations
- middleware extension hooks
- checkpointing / persistence foundations
- observability / tracing hooks if available

ForgeFlow provides the software engineering product layer:

- software engineering domain model
- RFC-defined workflow roles
- structured contracts
- Repository Context Service
- sandbox and security governance
- policy-gated PR workflow
- evaluation framework
- product-level run summary

The extension strategy must keep these responsibilities separate enough that ForgeFlow can evolve as a product layer while still benefiting from DeerFlow upstream improvements.

## Problem Statement

Without a clear DeerFlow extension strategy:

- ForgeFlow may randomly modify DeerFlow core.
- ForgeFlow and DeerFlow ownership boundaries may become unclear.
- Future DeerFlow upstream updates may become difficult to adopt.
- Workflow roles may be incorrectly implemented as DeerFlow core concepts.
- ForgeFlow domain state may pollute DeerFlow generic runtime state.
- Middleware, tool, checkpoint, and trace ownership may become ambiguous.
- Implementation may couple prematurely to DeerFlow internal details.
- OpenSpec features may depend directly on unstable DeerFlow internals.
- Git history may fail to distinguish upstream adaptation from ForgeFlow product behavior.

ForgeFlow needs a deliberate extension model before implementing workflow roles, policy-gated tool execution, or Draft PR automation.

## Goals

- Define DeerFlow / ForgeFlow ownership boundary.
- Define current-stage integration strategy.
- Define acceptable extension patterns.
- Define forbidden extension patterns.
- Define how ForgeFlow domain state relates to DeerFlow runtime state.
- Define how ForgeFlow tools integrate with DeerFlow tool orchestration.
- Define how ForgeFlow policies integrate with DeerFlow middleware hooks.
- Define how ForgeFlow tracing and evaluation integrate with DeerFlow runtime.
- Define how future upstream sync or fork strategy should be handled.
- Define Milestone 1 constraints.

## Non-goals

- Rewrite DeerFlow architecture.
- Decide the final long-term fork strategy.
- Implement ForgeFlow runtime.
- Create production agent classes.
- Create a service layer.
- Define the complete package structure.
- Implement DeerFlow adapters.
- Modify DeerFlow source code.
- Decide every future upstream contribution policy.
- Create an OpenSpec change.

## Ownership Boundary

DeerFlow-owned capabilities:

- generic agent runtime
- graph / workflow execution foundation
- thread / conversation lifecycle
- generic tool calling / tool orchestration
- generic middleware hook mechanism
- checkpointing / persistence mechanism
- generic tracing hooks
- model invocation infrastructure if applicable

ForgeFlow-owned capabilities:

- software engineering workflow semantics
- workflow role definitions from RFC-001
- domain-specific structured contracts from RFC-002
- `RepositoryContextResult`
- `PatchProposal`
- `ValidationResult`
- `ReviewResult`
- `PRResult`
- sandbox policy decisions from RFC-004
- security governance
- PR workflow semantics
- evaluation fixtures and metrics
- product-level run summary
- human approval semantics

ForgeFlow should not redefine DeerFlow generic runtime concepts unless a future RFC explicitly justifies it.

DeerFlow may execute generic graph and tool orchestration mechanics. ForgeFlow owns the product meaning of a software maintenance workflow, the contracts that pass between workflow roles, and the policy decisions that govern side effects.

## DeerFlow Integration Assumption Boundary

ForgeFlow may depend on documented DeerFlow extension points, but it must not silently depend on DeerFlow internals or undocumented extension behavior.

Any dependency on DeerFlow internal state shape, message format, checkpoint layout, tool registry internals, middleware ordering, tracing payload structure, or other undocumented runtime behavior must be recorded as an integration assumption before implementation.

Boundary-crossing implementation choices require RFC, ADR, or OpenSpec documentation before use.

Examples of boundary-crossing decisions include:

- storing ForgeFlow contract state directly inside DeerFlow message history
- relying on DeerFlow checkpoint internals for Durable Run Summary
- depending on undocumented middleware execution order
- bypassing ForgeFlow policy wrappers by calling DeerFlow tools directly
- mapping ForgeFlow workflow roles to DeerFlow-native components
- treating DeerFlow message history as product-layer state
- relying on DeerFlow trace payload internals for product-level run summary

Each integration assumption should explain:

- the DeerFlow behavior being relied on
- whether the behavior is documented or internal
- why the dependency is necessary
- what ForgeFlow boundary it affects
- what alternatives were considered
- how upstream DeerFlow changes would be detected
- what adapter or isolation layer protects ForgeFlow product semantics

DeerFlow provides runtime foundations; ForgeFlow must preserve its product contracts, policy boundaries, durable state model, and workflow semantics through explicit adapters and documented integration assumptions.

## Current Integration Strategy

ForgeFlow should not fork or modify DeerFlow core prematurely. During Milestone 0 and Milestone 1, DeerFlow should be treated as upstream framework foundation and reference implementation, not as ForgeFlow application code.

### Option A: DeerFlow as Separate Local Reference Repository

Benefits:

- Fits early learning and architecture research.
- Avoids polluting the ForgeFlow repository.
- Makes the DeerFlow codebase easy to read independently.
- Avoids submodule maintenance cost.

Costs:

- Does not pin the DeerFlow commit used by ForgeFlow.
- Makes full development environment reproduction harder on GitHub.

### Option B: DeerFlow as Git Submodule Under `third_party/deer-flow`

Benefits:

- Records the DeerFlow upstream commit explicitly.
- Preserves the ForgeFlow / DeerFlow boundary.
- Fits long-term reference and gradual integration.
- Helps track upstream updates over time.

Costs:

- Adds submodule workflow overhead.
- Requires new contributors to understand submodule usage.

### Option C: Fork DeerFlow Directly

Benefits:

- Fits deep DeerFlow core changes.
- Fits contributing patches back to DeerFlow upstream.

Costs:

- Makes ForgeFlow look like a DeerFlow fork.
- Blurs product-layer and framework-layer boundaries.
- Increases upstream sync cost.

### Option D: Copy DeerFlow Source Code Into ForgeFlow

Rejected.

Reasons:

- Loses upstream tracking.
- Makes updates difficult to synchronize.
- Makes framework code and product code hard to distinguish.
- Encourages boundary pollution.

### Recommendation

Milestone 0 may use a separate local DeerFlow reference repository for reading, comparison, and architecture research.

Before Milestone 1 implementation begins, ForgeFlow must pin the DeerFlow upstream revision used for extension feasibility assessment.

The preferred pinning mechanism is a Git submodule under `third_party/deer-flow`.

If a Git submodule is not used, ForgeFlow must record an equivalent immutable upstream commit reference in project documentation.

During Milestone 1, DeerFlow should be treated as upstream reference/framework source, not ForgeFlow application code.

## DeerFlow Version Pinning for Milestone 1

Milestone 0 may use a separate local DeerFlow reference repository for reading, comparison, and architecture research.

Before Milestone 1 implementation begins, ForgeFlow must pin the DeerFlow upstream revision used for extension feasibility assessment.

The preferred mechanism is a Git submodule under:

```text
third_party/deer-flow
```

If a Git submodule is not used, ForgeFlow must record an equivalent immutable upstream commit reference in project documentation.

The immutable reference must include:

- upstream repository URL
- commit SHA
- assessment date
- assessed extension points
- known integration assumptions
- reason for the selected revision

During Milestone 1, DeerFlow must be treated as a read-only upstream framework and runtime reference, not ForgeFlow application code.

ForgeFlow implementation should depend only on the pinned revision and documented extension points or explicitly recorded integration assumptions.

RFC-007 extension feasibility claims must identify the DeerFlow revision they were assessed against.

If the pinned DeerFlow revision changes, affected integration assumptions must be reviewed before relying on prior conclusions.

### DeerFlow Revision Record

Current recorded DeerFlow reference:

| Field | Value |
|---|---|
| Repository URL | `https://github.com/bytedance/deer-flow.git` |
| Recorded revision | `c0b917cce2cd8b8644a3ed17d58ddb31adc5299a` |
| Recorded date | 2026-07-10 |
| Usage mode | Immutable upstream commit reference; no submodule is currently present. |
| Assessment document | `docs/architecture/assessments/deerflow-extension-points.md` |

This recorded revision is sufficient to remove RFC-001's DeerFlow revision blocker for Milestone 1 scope guarding. It does not make RFC-007 Accepted, and it does not authorize implementation that depends on undocumented DeerFlow internals.

If ForgeFlow later chooses the preferred submodule path, the submodule should be added under `third_party/deer-flow` and pinned to this or another explicitly reviewed revision.

## No DeerFlow Core Modification in Milestone 1

Milestone 1 must treat DeerFlow as a read-only upstream framework and runtime reference.

ForgeFlow Milestone 1 acceptance must not depend on any local DeerFlow core modification, unmerged DeerFlow patch, or temporary change inside `third_party/deer-flow` or a local DeerFlow reference repository.

Any local modification to DeerFlow source is prohibited on the Milestone 1 implementation path unless a separate RFC or ADR has already approved it.

If an experiment requires modifying DeerFlow, it must be performed outside the Milestone 1 delivery path and documented as exploratory.

Exploratory DeerFlow modifications must not become hidden dependencies for:

- Repository Context Service
- workflow graph behavior
- state mapping
- policy enforcement
- checkpointing
- tool orchestration
- tracing
- Durable Run Summary
- product-level semantics

If a DeerFlow core change appears necessary, the default path is:

1. document the missing extension point
2. evaluate whether a ForgeFlow adapter or wrapper can preserve the boundary
3. record the integration assumption or limitation
4. propose an upstream contribution or RFC / ADR when needed
5. only then consider a fork or core modification

ForgeFlow should extend DeerFlow through documented extension points, adapters, wrappers, and explicit integration assumptions, not through silent framework patches.

## Extension Patterns

### Pattern 1: External Application Layer

ForgeFlow should implement domain-specific workflow, contracts, policies, and evaluation in its own source tree while using DeerFlow runtime, tool orchestration, middleware, checkpoint, and tracing foundations where appropriate.

### Pattern 2: Adapter Layer

If DeerFlow data structures, tool interfaces, or middleware hooks do not align directly with ForgeFlow contracts, ForgeFlow should use adapters to translate between framework-level primitives and product-level contracts.

Adapters should make coupling explicit. They must not hide ForgeFlow product state inside opaque DeerFlow messages.

### Pattern 3: Policy Wrapper

ForgeFlow security governance must not be scattered only inside agent prompts. Tool execution should be wrapped by policy, middleware, or runtime gates that can enforce RFC-004 decisions before execution or publication.

### Pattern 4: Contract-first Integration

ForgeFlow workflow roles should hand off information through RFC-002 structured contracts, not through free-form text or DeerFlow internal message history alone.

### Pattern 5: Read-only Upstream Reference During Milestone 1

During Milestone 1, ForgeFlow should treat DeerFlow as read-only reference or framework foundation. ForgeFlow should not directly modify DeerFlow core to implement Repository Context Service.

## Forbidden or Discouraged Patterns

The following patterns are forbidden or discouraged unless a future accepted RFC explicitly changes the boundary:

- Directly modifying DeerFlow core without RFC approval.
- Storing ForgeFlow domain state inside opaque DeerFlow messages only.
- Treating DeerFlow thread messages as the only source of business state.
- Letting Planner directly control DeerFlow runtime execution.
- Treating workflow roles as DeerFlow-native services before RFC approval.
- Bypassing ForgeFlow contracts and passing free-form text between roles.
- Embedding security policy only in prompts.
- Creating PRs or external side effects without policy gates.
- Copying DeerFlow source into ForgeFlow.
- Building Milestone 1 by implementing the full autonomous repair workflow.

## State Integration Strategy

DeerFlow runtime state should be used for generic execution and checkpointing. ForgeFlow domain state should be modeled explicitly through structured contracts and Durable Run Summary.

ForgeFlow should not rely only on message history for business state.

Runtime State may reference DeerFlow thread and run identifiers. Durable Run Summary should persist ForgeFlow-specific audit information. Long-term Memory policy is controlled by ForgeFlow, not by generic runtime behavior.

### ForgeFlow State Authority and DeerFlow Runtime State Boundary

ForgeFlow structured contracts and Durable Run Summary are the authoritative product-layer state.

DeerFlow messages, runtime state, and checkpoints provide execution support, recovery support, and runtime continuity, but they must not become the authoritative store for ForgeFlow business state unless explicitly mapped by RFC-002 and RFC-007.

DeerFlow runtime state and checkpoints may carry:

- execution state
- transient context
- checkpoint metadata
- recoverable references
- explicitly mapped contract-derived data

They must not replace:

- structured contracts
- Durable Run Summary
- Policy Decision Records
- Approval Request artifacts
- artifact records
- evidence references
- retry lineage
- validation status
- review status
- PR evidence
- durable audit history

If ForgeFlow stores contract-derived data in DeerFlow checkpoints for runtime recovery, the mapping must preserve:

- contract identity
- schema version
- evidence references
- artifact IDs
- policy decision IDs when applicable
- approval request or approval decision IDs when applicable
- promotion/redaction boundaries defined by RFC-002

DeerFlow message history may be used as conversational or execution context, but it must not be treated as the authoritative source for:

- product facts
- policy decisions
- retry lineage
- PR evidence
- validation status
- review status
- durable audit history

Any mapping from ForgeFlow contracts, artifacts, policy records, approval records, or Durable Run Summary fields into DeerFlow runtime state, checkpoint structures, or message history must be documented before implementation.

The mapping must identify:

- what is stored
- why it is needed for runtime recovery
- whether it is authoritative or derived
- how it is versioned
- how it is redacted
- how it is reconstructed or validated

ForgeFlow must not bypass RFC-002 by treating opaque DeerFlow messages, checkpoint internals, or runtime payloads as product-layer state.

### Option A: Store Everything in DeerFlow Messages

Rejected.

Reasons:

- Difficult to validate.
- Hard to evaluate.
- Weak policy integration.
- Hard to generate PR summaries.
- Poor contract boundary.

### Option B: Extend DeerFlow State Directly

Possible later, but not the Milestone 1 default.

Reasons:

- May couple ForgeFlow to DeerFlow internals.
- Requires a follow-up RFC-007 decision or OpenSpec if needed.

### Option C: ForgeFlow Domain State With DeerFlow Runtime References

Recommended for early milestones.

Reasons:

- Clear ownership.
- Easier testing.
- Easier evaluation.
- Avoids polluting generic runtime state.

## Tool Integration Strategy

DeerFlow may provide generic tool execution infrastructure. ForgeFlow defines domain-specific tool contracts and capability levels.

Tool execution must respect RFC-004 policy gates. Repository Context Service should use read-only capabilities in Milestone 1. External side-effect tools such as GitHub PR creation require policy eligibility.

Tool outputs should produce `evidence_refs` and `artifact_ids` when relevant. Tool errors should be recorded in Durable Run Summary or referenced artifacts without embedding unbounded raw payloads.

Tool permission levels are owned by ForgeFlow policy, even if execution is delegated through DeerFlow mechanisms.

## Middleware Integration Strategy

DeerFlow may provide middleware hooks. ForgeFlow owns domain-specific middleware semantics.

Security middleware, cost control, patch boundary, approval gates, and trace enrichment are ForgeFlow concerns. RFC-004 defines governance policy. RFC-007 defines that those policies must attach to DeerFlow extension points explicitly rather than being hidden in prompts.

Middleware must not be implemented only as prompt instructions.

If a DeerFlow hook is insufficient for a required ForgeFlow policy gate, the gap must be documented in an RFC, ADR, or OpenSpec before implementation depends on internal DeerFlow behavior.

## DeerFlow Extension-Point Capability Assessment

RFC-007 must include a documented DeerFlow extension-point capability assessment before RFC-001 acceptance or before Milestone 1 implementation relies on DeerFlow integration assumptions.

The current Milestone 1 assessment is recorded in `docs/architecture/assessments/deerflow-extension-points.md`.

The assessment must identify whether the pinned DeerFlow revision provides usable documented extension points, adapters, or wrappers for the ForgeFlow governance boundaries required by RFC-004.

At minimum, the assessment should cover support for:

- pre-tool policy evaluation
- post-tool result capture
- command or action intent association
- middleware ordering
- checkpoint mapping
- trace event enrichment
- error handling
- stop-condition propagation
- later approval pause/resume behavior when it enters scope
- later external side-effect gating when it enters scope

For Milestone 1, the required assessment scope may be limited to read-only Repository Context access.

For Milestone 1, the assessment must confirm that the following can be supported without modifying DeerFlow core:

- workspace-confined read/search governance
- bounded and redacted result capture
- evidence reference recording
- trace or summary linkage
- deterministic Repository Context Service support

Capabilities that are not yet required for Milestone 1 may be recorded as future extension assumptions.

Future extension assumptions may include:

- sandbox-local write/test execution
- Human Approval pause/resume
- commit creation
- draft PR creation
- external side-effect gating
- full checkpoint mapping for `PatchProposal`, `ValidationResult`, `ReviewResult`, or `PRResult`

These future assumptions must not be treated as proven until a later RFC, ADR, or OpenSpec validates the relevant DeerFlow extension points.

If required RFC-004 governance cannot be attached through documented DeerFlow extension points, adapters, or wrappers, RFC-007 must record the limitation and RFC-001 must remain Draft until the integration strategy is revised.

### Milestone 1 Assessment Summary

The current assessment concludes:

- Milestone 1 should not require modifying DeerFlow core.
- Milestone 1 may use DeerFlow as upstream reference, runtime foundation if needed, and pattern source for middleware/tool/runtime design.
- ForgeFlow owns Repository Context Service, `RepositoryContextResult`, evidence references, read-only policy constraints, and product-level run summary.
- Milestone 1 should not depend on DeerFlow model invocation, memory, summarization, sandbox-local write/test execution, or PR side-effect integration.
- Public upstream evidence is sufficient for skeleton-level RFC-001 scope guarding, but it is not a complete DeerFlow source-code audit.

Future milestones must perform deeper source-level assessment before relying on DeerFlow internals, middleware ordering, checkpoint layouts, or side-effect execution paths.

## Workflow Graph Integration

RFC-001 defines workflow roles. DeerFlow runtime may execute graph nodes or agent steps. ForgeFlow owns workflow graph semantics.

Planner output is declarative, advisory, and non-binding. The workflow graph decides branching, retries, stops, and escalation based on contracts and policy decisions.

Runtime execution control must not be owned by Planner.

Milestone 1 should not implement the full workflow graph for the Draft PR MVP. Milestone 1 should focus on deterministic Repository Context Service and `RepositoryContextResult`.

## Observability and Evaluation Integration

DeerFlow may provide tracing hooks or runtime events. ForgeFlow owns product-level run summary and evaluation metrics.

Trace data should align with RFC-002 contracts and RFC-004 redaction policy. Evaluation should use controlled fixtures in early milestones.

Run summary should reference artifacts instead of embedding all raw source or log content.

RFC-005 owns detailed trace and run summary shape. RFC-006 owns evaluation fixture and metric definitions. RFC-007 only defines the DeerFlow extension boundary for runtime events, hooks, and integration points.

## Upstream Sync Strategy

If ForgeFlow uses DeerFlow as a submodule, it should track the DeerFlow upstream commit explicitly.

ForgeFlow should avoid local modifications inside DeerFlow unless explicitly approved. If DeerFlow core changes become necessary, they must be documented through a new RFC or ADR.

ForgeFlow should prefer contributing generic improvements upstream rather than maintaining large private patches.

ForgeFlow product behavior should remain outside DeerFlow core.

Compatibility assumptions should be recorded in RFC-007 or follow-up documentation.

A future decision may move from submodule/reference to fork if deep DeerFlow core changes become necessary, but that should be a deliberate RFC or ADR decision.

## Relationship with RFC-001

RFC-001 defines Agent Architecture. RFC-007 defines how that architecture sits on top of DeerFlow.

Workflow roles are ForgeFlow concepts. DeerFlow runtime may execute graph nodes or agent steps, but it does not own ForgeFlow product semantics.

Planner output remains advisory. Repository Context Service is a ForgeFlow-owned deterministic service. Human approval semantics are ForgeFlow-owned policy behavior. PR role behavior is ForgeFlow-owned and policy-gated.

RFC-007 now records the concrete DeerFlow revision/reference assumption and links to `docs/architecture/assessments/deerflow-extension-points.md`. For RFC-001 acceptance purposes, this resolves the DeerFlow revision and Milestone 1 extension-point assessment blockers at skeleton level.

This does not promote RFC-007 to Accepted. RFC-007 remains Draft until its own acceptance review confirms that its broader extension strategy is complete.

## Relationship with RFC-002

RFC-002 defines structured contracts and state boundaries. RFC-007 defines where those contracts live relative to DeerFlow runtime state.

ForgeFlow contracts should not be hidden only inside DeerFlow message history. Durable Run Summary belongs to the ForgeFlow product layer. Long-term Memory policy belongs to ForgeFlow.

## Relationship with RFC-004

RFC-004 defines sandbox and security governance. RFC-007 defines how security governance attaches to DeerFlow middleware, tool, and runtime hooks.

DeerFlow may execute tools, but ForgeFlow policy decides capability eligibility. External side effects require ForgeFlow policy gates and may require Human Approval.

## Relationship with Milestone 1

Milestone 1 is the Repository Context Foundation Slice.

Milestone 1 must not become a full DeerFlow runtime integration project.

Milestone 1 should:

- use DeerFlow only as reference or minimal runtime foundation if needed
- avoid modifying DeerFlow core
- avoid implementing the full autonomous repair workflow
- avoid production role implementation units
- focus on deterministic Repository Context Service
- produce `RepositoryContextResult`
- preserve `evidence_refs` / `artifact_ids` alignment with RFC-002
- obey read-only policy constraints from RFC-004

Milestone 1 should not:

- implement `PatchProposal` generation
- implement PR creation
- implement Validation repair loop
- promote workflow roles into runtime classes
- require a deep DeerFlow fork

## Minimal DeerFlow Integration Scope for Milestone 1

Milestone 1 must not become a full DeerFlow runtime integration project.

For Milestone 1, DeerFlow-related work is limited to the minimum needed to support or assess deterministic read-only Repository Context Service.

Required before Milestone 1 implementation begins:

- pin the DeerFlow revision or record an equivalent immutable upstream commit reference
- document DeerFlow extension-point assumptions relevant to read-only Repository Context access
- confirm that Repository Context Service does not require DeerFlow core modification
- state whether DeerFlow is used only as an upstream reference or as a minimal runtime foundation for Milestone 1
- record known limitations, unsupported assumptions, and deferred integration risks

Deferred to later milestones:

- full ForgeFlow workflow graph integration
- runtime implementation of Planner, Software Engineer, Validation, Review, or PR roles
- sandbox-local write and test execution integration
- Human Approval pause/resume integration
- GitHub branch, commit, draft PR, or other external side-effect integration
- full checkpoint mapping for `PatchProposal`, `ValidationResult`, `ReviewResult`, or `PRResult`
- production-grade DeerFlow adapter layer
- full policy middleware integration for write, test, PR, or external side-effect workflows

Milestone 1 may document future DeerFlow integration assumptions, but it must not implement or require them for Repository Context acceptance.

The purpose of RFC-007 in Milestone 1 is to make upstream assumptions reproducible and prevent hidden coupling, not to complete the full ForgeFlow-DeerFlow runtime integration.

## Alternatives Considered

### Alternative A: Build ForgeFlow Entirely Inside DeerFlow Core

Rejected.

This would blur ownership boundaries, make upstream sync difficult, and pollute the framework layer with ForgeFlow product behavior.

### Alternative B: Copy DeerFlow Source Into ForgeFlow

Rejected.

This would lose upstream tracking, increase maintenance cost, and make framework code difficult to distinguish from ForgeFlow product code.

### Alternative C: Use DeerFlow as External Framework / Reference With ForgeFlow-owned Product Layer

Recommended.

This preserves clear boundaries, supports incremental integration, and allows ForgeFlow to evolve without prematurely forking DeerFlow.

### Alternative D: Fork DeerFlow Immediately

Not recommended for Milestone 1.

Forking may become appropriate if deep core changes are proven necessary, but an early fork would increase maintenance cost before ForgeFlow has validated its product-layer boundaries.

## Trade-offs

- Upstream compatibility vs customization speed: avoiding core changes slows some custom behavior but keeps upstream updates feasible.
- Submodule/reference clarity vs contributor convenience: explicit upstream references improve traceability but add workflow overhead.
- Adapter layer complexity vs direct coupling: adapters add code and design work but prevent hidden coupling to DeerFlow internals.
- Contract-first integration vs faster prototype: structured contracts slow early prototyping but support evaluation, policy gates, and PR summaries.
- Framework purity vs product velocity: strict boundaries may feel slower, but they keep product behavior auditable and maintainable.
- Avoiding DeerFlow core changes vs missing extension hooks: staying external may expose gaps that require later RFC or ADR decisions.

## Risks

- DeerFlow extension points may be insufficient.
- DeerFlow internal APIs may change.
- Submodule workflow may be inconvenient.
- Too much adapter code may slow development.
- Avoiding core changes may delay necessary runtime features.
- Forking too early may isolate ForgeFlow from upstream improvements.
- Treating DeerFlow as a black box may hide important runtime constraints.
- Over-constraining Milestone 1 may delay the vertical MVP.
- RFC-007 assumptions may conflict with future Repository Context Service OpenSpec details; such conflicts should be captured without expanding Milestone 1 scope.
- A pinned DeerFlow revision may reveal insufficient documented extension points for RFC-004 policy attachment.
- Undocumented DeerFlow dependencies may be missed unless integration assumptions are reviewed during OpenSpec planning.
- Local DeerFlow experiments may accidentally become hidden dependencies if not kept outside the Milestone 1 delivery path.

## Open Questions

- Should the recorded DeerFlow revision be converted into a Git submodule pin before Milestone 1 implementation begins?
- Which DeerFlow extension points are stable enough to rely on?
- Where should ForgeFlow package code live?
- How should ForgeFlow contracts map to DeerFlow messages, state, and checkpoints?
- Which middleware hooks are required?
- Which tool registry mechanism should be used?
- Should ForgeFlow contribute generic improvements upstream?
- When should a fork be considered?
- How will compatibility be tested after DeerFlow upstream updates?
- What DeerFlow internals, if any, must be documented as temporary dependencies before Milestone 1 implementation?
- What documented DeerFlow hooks, adapters, or wrappers can support read-only Repository Context governance without core modification?
- What limitations should be recorded if DeerFlow cannot support RFC-004 policy attachment assumptions through documented extension points?

## Decision Summary

- Treat DeerFlow as upstream framework/reference, not product layer.
- ForgeFlow owns software engineering domain semantics.
- Pin DeerFlow before Milestone 1 implementation, preferably as `third_party/deer-flow` or through an equivalent immutable commit reference.
- Do not allow Milestone 1 acceptance to depend on local DeerFlow core modifications, temporary changes, or unmerged patches.
- Prefer external application layer and adapters.
- Keep workflow roles as ForgeFlow concepts.
- Keep ForgeFlow structured contracts and Durable Run Summary as authoritative product-layer state.
- Keep DeerFlow messages, runtime state, and checkpoints limited to mapped runtime state, transient context, recoverable references, or explicitly mapped contract-derived data.
- Attach security governance through explicit policy, middleware, and runtime gates.
- Require a DeerFlow extension-point capability assessment for RFC-004 policy attachment feasibility.
- Repository Context Service is a ForgeFlow-owned deterministic service.
- Milestone 1 must not require a deep DeerFlow fork.
- Milestone 1 DeerFlow integration scope is limited to pinning/reference, read-only Repository Context assumptions, no-core-modification proof, and documented limitations.

## RFC-001 DeerFlow Extension Acceptance Criteria

RFC-007 is sufficient to unblock RFC-001 acceptance only after the DeerFlow extension assumptions required by RFC-001 have been documented at skeleton level.

At minimum, RFC-007 must confirm that:

- the DeerFlow upstream revision used for assessment is pinned or immutably recorded
- the DeerFlow / ForgeFlow ownership boundary is accepted
- any dependency on DeerFlow internals or undocumented extension behavior is recorded as an integration assumption
- Milestone 1 does not depend on DeerFlow core modification, local DeerFlow patches, or unmerged upstream patches
- ForgeFlow structured contracts and Durable Run Summary remain the authoritative product-layer state
- any DeerFlow runtime/checkpoint/message mapping preserves RFC-002 contract identity, schema version, evidence references, artifact IDs, policy decision IDs when applicable, approval record IDs when applicable, and promotion/redaction boundaries
- RFC-004 policy attachment feasibility has been assessed at skeleton level, including whether pre-tool policy evaluation, post-tool capture, trace enrichment, checkpoint mapping, stop-condition propagation, and later approval pause/resume or external side-effect gating can be supported without modifying DeerFlow core
- the minimal Milestone 1 DeerFlow integration scope is limited to pinning/reference, read-only Repository Context assumptions, no-core-modification proof, and documented limitations
- any unsupported extension assumptions, integration gaps, or upstream risks are recorded as risks or open questions rather than silently assumed away

If these criteria are not satisfied, RFC-001 must remain Draft until RFC-007 records the missing DeerFlow assumptions or revises the integration strategy.

## Acceptance Notes

RFC-007 now records the DeerFlow upstream reference and Milestone 1 extension-point capability assessment required to unblock RFC-001 acceptance.

Current acceptance note for RFC-001:

- DeerFlow revision is immutably recorded as `c0b917cce2cd8b8644a3ed17d58ddb31adc5299a`.
- The assessment document is `docs/architecture/assessments/deerflow-extension-points.md`.
- Milestone 1 does not depend on adding a DeerFlow submodule.
- Milestone 1 does not depend on local DeerFlow core modifications, temporary patches, or unmerged upstream patches.
- Milestone 1 can keep Repository Context Service ForgeFlow-owned and deterministic.
- Full workflow graph integration, write/test sandbox integration, Human Approval pause/resume, PR side effects, and production-grade DeerFlow adapters remain deferred.

These notes are intended only to remove RFC-001's DeerFlow extension blocker. They do not accept RFC-007 itself.

## Acceptance Preconditions

RFC-007 should become Accepted only after:

- DeerFlow / ForgeFlow ownership boundary is agreed.
- Current integration strategy is agreed.
- DeerFlow revision pinning or immutable reference strategy is agreed.
- Acceptable extension patterns are documented.
- Forbidden coupling patterns are documented.
- Integration assumption rules are documented.
- State integration strategy is compatible with RFC-002.
- Security integration strategy is compatible with RFC-004.
- DeerFlow extension-point capability assessment is documented at skeleton level.
- Workflow role interpretation is compatible with RFC-001.
- Milestone 1 no-core-modification rule is accepted.
- Minimal Milestone 1 DeerFlow integration scope is accepted.
- Milestone 1 constraints are consistent with `docs/product/roadmap/milestones.md`.
- No conflict with Repository Context Service OpenSpec readiness is found.
