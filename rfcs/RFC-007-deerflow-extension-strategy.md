# RFC-007: DeerFlow Extension Strategy

## Status

Draft

RFC-007 is an RFC-001 acceptance precondition. RFC-001 should not become Accepted until RFC-007 defines the extension boundary between DeerFlow runtime foundations and ForgeFlow product-layer behavior.

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

For Milestone 0 and Milestone 1, ForgeFlow should prefer a separate local reference repository or a Git submodule, depending on repository maturity.

If the project adopts a submodule, DeerFlow should live under a clear third-party location such as `third_party/deer-flow` and be treated as upstream reference/framework source, not ForgeFlow application code.

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

## Relationship with RFC-002

RFC-002 defines structured contracts and state boundaries. RFC-007 defines where those contracts live relative to DeerFlow runtime state.

ForgeFlow contracts should not be hidden only inside DeerFlow message history. Durable Run Summary belongs to the ForgeFlow product layer. Long-term Memory policy belongs to ForgeFlow.

## Relationship with RFC-004

RFC-004 defines sandbox and security governance. RFC-007 defines how security governance attaches to DeerFlow middleware, tool, and runtime hooks.

DeerFlow may execute tools, but ForgeFlow policy decides capability eligibility. External side effects require ForgeFlow policy gates and may require Human Approval.

## Relationship with Milestone 1

Milestone 1 is the Repository Context Foundation Slice.

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

## Open Questions

- Should DeerFlow be a local reference repo or Git submodule for Milestone 1?
- Which DeerFlow extension points are stable enough to rely on?
- Where should ForgeFlow package code live?
- How should ForgeFlow contracts map to DeerFlow messages, state, and checkpoints?
- Which middleware hooks are required?
- Which tool registry mechanism should be used?
- Should ForgeFlow contribute generic improvements upstream?
- When should a fork be considered?
- How will compatibility be tested after DeerFlow upstream updates?
- What DeerFlow internals, if any, must be documented as temporary dependencies before Milestone 1 implementation?

## Decision Summary

- Treat DeerFlow as upstream framework/reference, not product layer.
- ForgeFlow owns software engineering domain semantics.
- Do not modify DeerFlow core during Milestone 1 unless explicitly approved by a future RFC.
- Prefer external application layer and adapters.
- Keep workflow roles as ForgeFlow concepts.
- Keep structured contracts outside opaque message-only state.
- Attach security governance through explicit policy, middleware, and runtime gates.
- Repository Context Service is a ForgeFlow-owned deterministic service.
- Milestone 1 must not require a deep DeerFlow fork.

## Acceptance Preconditions

RFC-007 should become Accepted only after:

- DeerFlow / ForgeFlow ownership boundary is agreed.
- Current integration strategy is agreed.
- Acceptable extension patterns are documented.
- Forbidden coupling patterns are documented.
- State integration strategy is compatible with RFC-002.
- Security integration strategy is compatible with RFC-004.
- Workflow role interpretation is compatible with RFC-001.
- Milestone 1 constraints are consistent with `docs/milestones.md`.
- No conflict with Repository Context Service OpenSpec readiness is found.
