# DeerFlow Extension-Point Capability Assessment

## Status

Draft assessment for Milestone 1 readiness.

This document records the DeerFlow upstream reference and the skeleton-level extension-point capability assessment required by RFC-007 before RFC-001 can be accepted as the Agent Architecture baseline.

## Purpose

ForgeFlow depends on DeerFlow as an upstream framework foundation, but ForgeFlow must not silently couple its product semantics to DeerFlow internals.

This assessment documents:

- the DeerFlow upstream revision currently used for architectural assessment
- which DeerFlow capabilities appear relevant to ForgeFlow
- which capabilities are relevant to Milestone 1
- which assumptions are supported by public upstream evidence
- which risks and open questions remain before implementation

This is documentation-only. It does not create adapters, runtime integrations, workflow graph implementations, middleware, checkpoint mappers, policy engines, contract schemas, or workflow role implementation units.

## M4 Execution Architecture Readiness

M4 requires a new source-level assessment at immutable revision
`c0b917cce2cd8b8644a3ed17d58ddb31adc5299a`; the existing Milestone 1
README-level assessment is not evidence that M4 may use runtime hooks. Before
any M4 runtime-backed OpenSpec or implementation, assess and record whether
documented stable extension points support:

- workflow lifecycle and stop-condition propagation;
- pre-tool ForgeFlow policy interception and post-tool redacted capture;
- approval pause/resume without treating runtime state as approval truth;
- mapping checkpoint/recovery state to ForgeFlow-owned durable summaries;
- sandbox and tool lifecycle without credentials or policy bypass; and
- trace hooks that can emit bounded ForgeFlow correlation references.

The current decision is adapter-first: ForgeFlow contracts, policy, artifact
store, and DurableRunSummary remain runtime-neutral. No DeerFlow submodule or
deep integration is authorized by this readiness plan. A revision upgrade or
deeper dependency requires the governance defined in RFC-007 and ADR-009.

### M4 Source-Level Findings at the Recorded Revision

The fixed revision exposes useful integration surfaces, but none may become a
ForgeFlow product boundary without an adapter:

| M4 need | Observed source evidence | Assessment result |
| --- | --- | --- |
| Pre-tool interception | `guardrails/middleware.py` implements sync/async `wrap_tool_call` and defaults provider errors to fail-closed. | A usable interception seam exists, but its boolean allow/deny decision and best-effort journal event are not a ForgeFlow PDR, ApprovalRequest, or durable audit record. |
| Workflow interruption/checkpointing | `runtime/runs/worker.py` accepts `interrupt_before`/`interrupt_after` and uses a configurable checkpointer. | Runtime pause/recovery exists, but M4 approval state and DurableRunSummary must remain ForgeFlow-owned and mapped by an adapter. |
| Sandbox lifecycle | `sandbox/middleware.py` acquires a sandbox lazily and documents reuse across thread turns; `sandbox_config.py` permits environment injection and multiple providers. | Not an M4 sandbox default: M4 requires a temporary fixed-revision workspace, no credentials, no network, no dynamic installation, and policy-bound command execution. |
| Trace/journal | Guardrail journaling is optional/best-effort; README/config expose external tracing integrations. | Trace hooks may supply correlation references only. They are not durable product audit storage and must not receive unredacted M4 payloads. |

The source also shows that the runtime middleware builder defines a concrete
tool-wrapper order and that `GraphBubbleUp`/interrupt nodes can propagate
pause signals. Those are useful substrate observations, not stable ForgeFlow
integration guarantees: the builder is an internal DeerFlow assembly detail,
and the pause signal has no ForgeFlow `ApprovalRequest`/Decision lifecycle.
An M4 adapter must therefore own policy-before-tool ordering and map a paused
run to explicit ForgeFlow approval contracts; it must not depend on the
existing internal middleware list as its enforcement proof.

The capability gate is therefore **not accepted**. The next assessment work
must prove a ForgeFlow-owned adapter can enforce the required middleware order,
policy-before-tool semantics, approval pause/resume mapping, sandbox profile,
and redacted durable-event mapping without undocumented DeerFlow dependencies.

## DeerFlow Upstream Reference

| Field | Value |
|---|---|
| Repository URL | `https://github.com/bytedance/deer-flow.git` |
| Recorded revision | `c0b917cce2cd8b8644a3ed17d58ddb31adc5299a` |
| Recorded date | 2026-07-10 |
| Usage mode | Immutable upstream commit reference; no submodule is currently present in this repository. |
| Milestone 1 assumption | DeerFlow is treated as a read-only upstream framework/reference. Milestone 1 does not depend on modifying DeerFlow core, local DeerFlow patches, or unmerged upstream patches. |

Current repository inspection found no `.gitmodules` file and no `third_party/deer-flow` directory.

Recommended next command if the project chooses the submodule path later:

```bash
git submodule add https://github.com/bytedance/deer-flow.git third_party/deer-flow
git -C third_party/deer-flow checkout c0b917cce2cd8b8644a3ed17d58ddb31adc5299a
```

This assessment intentionally records the immutable revision without adding a submodule in this change.

## Assessment Scope

This is a Milestone 1 pre-implementation extension-point capability assessment. It is not a complete DeerFlow source-code audit.

Assessment inputs:

- current ForgeFlow RFCs and milestone documents
- public DeerFlow repository metadata and README-level documentation
- immutable upstream revision recorded by `git ls-remote https://github.com/bytedance/deer-flow.git HEAD`

This assessment is limited to whether DeerFlow appears suitable as an upstream reference or minimal runtime foundation for Milestone 1.

Milestone 1 scope remains:

- deterministic Repository Context Service
- `RepositoryContextResult`
- evidence references
- read-only repository workspace constraints
- bounded and redacted result capture
- product-level run summary alignment

Milestone 1 does not include:

- full ForgeFlow workflow graph integration
- production workflow role implementation units
- patch generation
- code editing
- test execution
- Human Approval pause/resume integration
- branch, commit, or draft PR creation
- full checkpoint mapping for `PatchProposal`, `ValidationResult`, `ReviewResult`, or `PRResult`

## Extension Point Assessment Table

| Capability | DeerFlow location / evidence | ForgeFlow need | Milestone 1 relevance | Observed support | Risk | Current decision |
|---|---|---|---|---|---|---|
| Graph / workflow execution | Public README describes DeerFlow as a super agent harness and references a LangGraph API endpoint at `DEERFLOW_LANGGRAPH_URL`. | ForgeFlow eventually needs graph execution for workflow roles, branching, retries, and stop conditions. | Low for Milestone 1 unless Repository Context Service is run through DeerFlow runtime. | Public documentation indicates graph/runtime foundations exist, but exact stable extension points are not source-verified in this assessment. | Undocumented graph internals may not support ForgeFlow transition policy without adapters. | Treat as upstream runtime reference for Milestone 1. Do not depend on graph internals for Repository Context acceptance. |
| Thread / run lifecycle | Public README documents thread-scoped goals, run checkpoint behavior, thread branching, conversation history, and Gateway-managed status. | ForgeFlow later needs run IDs, thread references, durable run summaries, and human review traceability. | Medium. Milestone 1 may reference run/thread identifiers if a DeerFlow runtime is used, but it does not require full lifecycle integration. | Public documentation suggests thread/run lifecycle support exists. | Mapping ForgeFlow run summaries to DeerFlow thread state could bypass RFC-002 if not documented. | Use only as recoverable runtime reference. ForgeFlow Durable Run Summary remains authoritative. |
| State / checkpointing | Public README mentions checkpointed assistant turns, branching from checkpoints, and LangGraph-related checkpoint behavior. | ForgeFlow later needs runtime recovery while preserving contract identity, evidence refs, artifact IDs, and redaction boundaries. | Low to medium. Milestone 1 can avoid checkpoint dependency unless DeerFlow runtime is used. | Checkpointing appears present, but checkpoint schema and extension API are not confirmed. | DeerFlow checkpoint internals may be unstable or unsuitable for ForgeFlow product state. | Do not treat DeerFlow checkpoints as product-layer truth. Any mapping requires RFC-002/RFC-007 documentation before implementation. |
| Tool registry / tool execution | Public README states DeerFlow includes core tools such as web search, web fetch, rendered web capture, file operations, bash execution, and supports custom tools via MCP servers and Python functions. | ForgeFlow needs controlled repository search/read tools, later sandbox edit tools, validation commands, and GitHub side-effect tools. | Medium. Milestone 1 may use read-only search/inspection patterns but should keep Repository Context Service ForgeFlow-owned. | Tool execution and extensibility appear documented at capability level. | Direct DeerFlow tool invocation could bypass RFC-004 policy gates. | Milestone 1 may reference DeerFlow tool patterns but must enforce ForgeFlow read-only policy and evidence boundaries outside opaque tool messages. |
| Middleware hooks | Public README indicates provider/tool recovery behavior and tracing integrations, but this assessment did not verify a stable middleware API from source. | ForgeFlow needs policy wrappers, cost controls, redaction, and future approval gates. | Low for Milestone 1 if Repository Context Service is implemented outside DeerFlow runtime; medium if DeerFlow tool execution is used. | Insufficient public evidence for stable middleware ordering or pre-tool policy interception. | RFC-004 policy attachment may require adapters or wrappers rather than DeerFlow-native middleware. | Record as an open integration assumption. Milestone 1 must not depend on unverified middleware internals. |
| Sandbox / command execution integration | Public README documents `AioSandboxProvider`, `LocalSandboxProvider`, isolated containers, per-thread directories, file tools, and host bash disabled by default. | ForgeFlow later needs governed sandbox edit/test execution and command policy. | Low. Milestone 1 is read-only and forbids arbitrary command execution. | DeerFlow appears to provide sandbox concepts, but ForgeFlow Milestone 1 does not need them. | DeerFlow sandbox defaults may not satisfy ForgeFlow security requirements without RFC-004 policy wrappers. | Treat as future reference only. Milestone 1 must not depend on write/test sandbox integration. |
| Tracing / observability hooks | Public README documents LangSmith tracing, Langfuse tracing, run status, workspace change summaries, and support bundles with redacted diagnostics. | ForgeFlow needs product-level run summary, evidence trace, redaction, and evaluation data. | Medium. Milestone 1 needs bounded/redacted context result summaries and evidence references. | Public documentation suggests tracing and diagnostics support exist. | DeerFlow trace payloads may not match ForgeFlow run summary semantics or redaction policy. | Use DeerFlow tracing as optional upstream signal. ForgeFlow owns product-level run summary semantics. |
| Model invocation boundaries | Public README describes model-agnostic configuration through `config.yaml`, OpenAI-compatible APIs, LangChain model providers, vLLM, Codex CLI, and Claude Code OAuth examples. | ForgeFlow needs clear boundaries for model use, especially no LLM reasoning inside Repository Context Service during Milestone 1. | Low. Milestone 1 Repository Context Service must be deterministic and should not require model invocation. | DeerFlow model configuration is documented at a high level. | Accidental model use in Repository Context could violate RFC-001 and RFC-002 determinism boundaries. | Do not use DeerFlow model invocation for Milestone 1 Repository Context retrieval or ranking. |
| Memory / summarization hooks | Public README documents manual context compaction, context engineering, sub-agent summarization, and long-term memory. | ForgeFlow needs strict memory boundaries and no Milestone 1 memory reads/writes. | Low. Milestone 1 explicitly excludes Long-term Memory reads and writes. | DeerFlow memory/summarization exists, but it is not needed for Milestone 1. | DeerFlow memory could introduce non-deterministic context if accidentally consulted. | Do not use DeerFlow memory or summarization for Milestone 1 `RepositoryContextResult`. |
| Configuration system | Public README documents setup wizard, `.env`, `config.yaml`, `config.example.yaml`, sandbox mode, model providers, web search, and execution/safety preferences. | ForgeFlow later needs configuration for policy profiles, tool capabilities, sandbox choices, and evaluation settings. | Low to medium. Milestone 1 may need local ForgeFlow configuration for read-only repository context. | DeerFlow configuration concepts exist, but ForgeFlow-specific policy/config semantics are not defined by DeerFlow. | Using DeerFlow config directly for ForgeFlow policy could blur ownership. | Keep ForgeFlow policy/config semantics ForgeFlow-owned. DeerFlow config may inform adapters later. |

## Milestone 1 Conclusion

Milestone 1 should not require modifying DeerFlow core.

Milestone 1 may use DeerFlow as:

- upstream reference
- runtime foundation if needed
- pattern source for middleware, tool, and runtime design

ForgeFlow should own:

- Repository Context Service
- `RepositoryContextResult`
- evidence references
- read-only policy constraints
- product-level run summary

Milestone 1 acceptance must not depend on:

- local DeerFlow core modifications
- unmerged DeerFlow patches
- temporary changes inside `third_party/deer-flow`
- DeerFlow memory or summarization
- DeerFlow model invocation for repository relevance
- DeerFlow sandbox write/test execution
- DeerFlow PR or external side-effect integration

The recorded DeerFlow revision appears sufficient as an upstream reference for RFC-001 acceptance because the remaining Milestone 1 implementation can be ForgeFlow-owned and deterministic. DeerFlow runtime integration remains optional for Milestone 1 and must not become a hidden dependency.

## Risks

- This assessment did not inspect a local DeerFlow source checkout or submodule.
- Public README-level evidence does not prove stable internal APIs, middleware ordering, checkpoint schema, or tool registry internals.
- If Milestone 1 chooses to execute Repository Context Service through DeerFlow runtime rather than using DeerFlow as reference, a narrower implementation-specific assessment may be required.
- RFC-004 policy attachment for future write/test/PR workflows is not proven by this Milestone 1 assessment.
- DeerFlow upstream may change after the recorded revision; affected assumptions must be reviewed if the pinned revision changes.

## Open Questions

- Should ForgeFlow add DeerFlow as a Git submodule under `third_party/deer-flow` before Milestone 1 implementation begins?
- Which documented DeerFlow extension points should be considered stable enough for later workflow graph integration?
- If DeerFlow runtime is used in Milestone 1, how will read-only path policy and evidence capture attach without depending on undocumented internals?
- Should a follow-up ADR record the exact DeerFlow reference strategy once the project chooses local reference vs submodule?
- Which DeerFlow source files should be inspected in a future source-level assessment before Milestone 2 or the Draft PR MVP?

## Assessment Decision

For RFC-001 acceptance purposes, this assessment records:

- an immutable DeerFlow upstream revision
- no current ForgeFlow submodule
- no Milestone 1 dependency on DeerFlow core modification
- no Milestone 1 dependency on DeerFlow write/test sandbox integration
- no Milestone 1 dependency on DeerFlow model invocation, memory, or summarization
- a skeleton-level view of DeerFlow capabilities relevant to future extension

RFC-007 may reference this document as the current DeerFlow extension-point capability assessment for Milestone 1 scope guarding. Later milestones should perform deeper source-level assessments before relying on DeerFlow internals, middleware ordering, checkpoint layouts, or side-effect execution paths.
