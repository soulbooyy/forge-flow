# RFC-003: Tool and MCP Integration

## Status

Accepted — 2026-07-13.

## Context

Milestone 2 needs to turn immutable `RepositoryContextResult` evidence into a
structured `PatchProposal`. The roadmap lists RFC-003 as an M2 dependency, but
the repository had no RFC-003 document. Without it, an implementation could
silently choose a model, tool surface, direct filesystem write path, or DeerFlow
integration point. Those are architecture decisions, not implementation detail.

## Decisions

- ForgeFlow owns product-level capability contracts; DeerFlow or MCP may supply
  execution mechanics only behind ForgeFlow policy wrappers.
- M2 proposal synthesis is a non-side-effecting capability. It may consume a
  bounded, immutable `RepositoryContextResult` and task input, but it may not
  reread the workspace, execute commands, write files, invoke a shell, access
  the network, or create a diff artifact.
- M2 uses only a local deterministic fixture source behind a provider-neutral
  proposal-source interface. It does not invoke a real LLM, MCP server,
  DeerFlow runtime provider, network service, or external tool.
- The M2 fixture source accepts only a supported `RepositoryContextResult` and
  bounded task input; it receives no extra raw workspace content, source
  snippets, prompts, environment values, or credentials.
- The fixture source returns a bounded declarative draft that is validated and
  converted into a ForgeFlow-owned `PatchProposal`. Its raw fixture payload is
  transient and must not become a durable contract field.
- A real model/provider invocation is deferred to a separate accepted OpenSpec.
  That future change must define input/output bounds, provider identity,
  redaction, failure envelopes, audit identity, artifact retention, and policy
  attachment before implementation.
- A future sandbox-local edit or diff tool is Level 1. It requires a separate
  Action Intent, policy decision, path/diff/secret controls, and an accepted
  M2 extension before any implementation depends on it.
- Tool outputs must be converted into ForgeFlow-owned typed contracts; raw MCP
  or provider payloads are transient and must not become durable contract
  fields by default.

## M2 Integration Boundary

The M2 proposal source is identified as `m2/deterministic-fixture-v1`. It is a
test-controlled input source, not a capability to inspect a workspace or call a
provider. M2 contract fields may record this source identifier and the policy
profile identity, but must not record a provider transcript, prompt, raw source
payload, tool-call ID, command, or runtime trace.

Because M2 invokes no DeerFlow or MCP execution mechanism, it does not depend
on a DeerFlow tool-registry or middleware attachment point. Those concerns
remain future integration decisions rather than assumed M2 behavior.

## M3 Integration Boundary

Milestone 3 extends the contract-first approach to `ValidationResult` and
`ReviewResult`, artifact lineage, and policy-decision handoffs. It may use
only deterministic fixtures or a fake executor to produce bounded simulated
attempt facts. This is test infrastructure for ForgeFlow-owned contracts, not
a command-execution capability.

The M3 fixture or fake-executor boundary must not spawn a process, inspect or
mutate a workspace, read repository configuration as authority, access a
network, install dependencies, access credentials, invoke a provider, MCP
server, or DeerFlow runtime, or create Git/PR side effects. Its transient
inputs and outputs must not become raw durable contract payloads.

Any future command execution requires a separate accepted OpenSpec. Its sole
authorization source must be a versioned ForgeFlow policy profile; repository
configuration may supply declarative hints such as a test-entry suggestion but
cannot grant execution authority. That future change must define a governed
executor, Command Intent, fresh Policy Decision Record, artifact/redaction
handling, and failure semantics before it invokes a command.

## Non-goals

- Selecting or integrating a production model provider.
- Implementing MCP servers or adapters.
- Defining sandbox technology.
- Enabling filesystem mutation, test execution, Git, network, commits, or PRs.
- Treating a deterministic fixture or fake executor as a sandbox or command
  execution implementation.
- Modifying DeerFlow core.

## Future Acceptance Preconditions

Any OpenSpec that introduces a real provider, MCP server, DeerFlow runtime
provider, source-content expansion, or tool call must reconcile with RFC-002,
RFC-004, RFC-007, and this RFC. It must establish that the new capability cannot
bypass policy, payload, persistence, or runtime ownership boundaries.

## Relationship to Milestone 2

M2 may implement only the deterministic fixture source and provider-neutral
contract adapter specified here. It must not implement a real synthesis
provider or a governed tool integration.
