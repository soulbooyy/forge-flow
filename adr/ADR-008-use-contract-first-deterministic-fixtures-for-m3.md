# ADR-008: Use Contract-First Deterministic Fixtures for M3

## Status

Accepted

## Context

M3 introduces `ValidationResult`, `ReviewResult`, artifact lineage, and
policy-decision handoffs after M2's immutable declarative `PatchProposal`.
Implementing real validation commands now would force unaccepted choices about
sandbox technology, executor identity, command allowlists, network access,
dependency installation, output redaction, artifact retention, and runtime
retry enforcement. Those choices are broader than the M3 contract slice.

## Decision

M3 uses a contract-first, deterministic-fixture approach. It may use a bounded
fake executor solely to synthesize deterministic attempt facts for testing
`ValidationResult`, `ReviewResult`, artifact lineage, policy-decision state,
and terminal failure semantics.

M3 does not execute commands, create a sandbox, inspect or mutate a workspace,
access a network, install dependencies, access credentials, invoke a provider,
MCP server, or DeerFlow runtime, or create Git or PR side effects. Retry is
outside M3; a future execution-runtime change must define retry against
execution attempts without mutating validation contracts.

Future command execution requires its own accepted OpenSpec. A versioned
ForgeFlow policy profile is its sole authorization source. Repository
configuration may provide declarative hints but may not authorize execution.
Blocking review outcomes are selected by policy as either `blocked` or
`requires_human_approval`; neither outcome is approval or execution authority.

## Consequences

- M3 can test auditable contract identity, lineage, policy transitions, and
  safe terminal outcomes without creating a side-effecting execution path.
- The future executor remains replaceable because M3 records ForgeFlow-owned
  facts rather than tool-specific runtime payloads.
- M3 cannot demonstrate real test execution, sandbox isolation, command
  parsing against live tools, or retry enforcement; these remain explicit
  future work.

## Design Review

Grill-Me review challenged whether a fake executor could accidentally become an
ungoverned execution path, whether a policy terminal outcome could be confused
with an attempted command, whether simulated logs could bypass payload and
retention controls, whether review could become approval, and whether retry
could leak workflow control into a result contract.

The accepted constraints are:

- fixture identity, a repository hint, and a `PatchProposal` are never command
  authority; only a future versioned ForgeFlow policy profile may authorize an
  execution attempt;
- M3 lineage must distinguish a policy-stopped flow from a simulated attempt
  fact; an unstarted flow must not claim an exit code, command output, or an
  executed command;
- artifacts and evidence in M3 are bounded references or deterministic fixture
  identifiers, never raw simulated logs, shell text, environment values, or
  source payloads;
- review findings can influence only a policy fixture outcome and cannot
  authorize continuation, approval, retry, or PR readiness; and
- M3 contracts contain no retry counter, repair instruction, or next-attempt
  directive. Future runtime retry policy must retain immutable attempt lineage
  rather than rewrite a validation result.

The M3 OpenSpec must make these distinctions testable using separate success,
terminal, and policy-fixture scenarios before implementation is planned.

## Alternatives Considered

- Build a minimal local command runner in M3: rejected because it would make
  security and sandbox decisions before their governing authority is accepted.
- Treat repository test configuration as execution authorization: rejected
  because repository-owned content cannot grant a ForgeFlow capability.
- Include repair retries in `ValidationResult`: rejected because retry is
  runtime policy and would blur immutable findings with workflow control.
