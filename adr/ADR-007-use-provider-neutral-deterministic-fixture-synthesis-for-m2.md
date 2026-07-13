# ADR-007: Use Provider-Neutral Deterministic Fixture Synthesis for M2

## Status

Accepted

## Context

M2 must establish `PatchProposal` as an evidence-backed declarative contract
without expanding the milestone into model invocation, external tool execution,
runtime coupling, source-content export, or sandbox editing. M1 intentionally
returns evidence references rather than source payloads, so a real provider
would require new governance for context disclosure, redaction, identity,
failure handling, audit, and retention.

## Decision

M2 uses a local deterministic fixture source behind a provider-neutral proposal
source interface. The source consumes only a supported `RepositoryContextResult`
and bounded task input and yields a bounded draft for `PatchProposal` validation.
It must not reread a workspace, include raw source, invoke an LLM, call MCP,
use DeerFlow runtime provider behavior, access the network, execute commands,
or mutate a workspace.

M2 records the source identity `m2/deterministic-fixture-v1` and the evaluated
policy profile identity. It does not persist raw fixture payloads, prompts,
provider transcripts, tool-call records, or runtime traces in `PatchProposal`.

Real provider integration is a separate future OpenSpec and must define its
own data-minimization, redaction, provider identity, failure, audit, artifact,
and policy-attachment behavior.

## Consequences

- M2 can deterministically test contract identity, evidence closure, validation
  errors, risk handling, and policy binding without external dependencies.
- `PatchProposal` remains stable when a future LLM, MCP, or DeerFlow adapter is
  substituted behind the provider-neutral boundary.
- M2 does not demonstrate model-generated repair reasoning; that is intentional
  and belongs to the later provider-integration change.

## Alternatives Considered

- Real LLM/provider in M2: rejected because it introduces unaccepted context,
  audit, retention, and failure-governance scope.
- MCP or DeerFlow runtime adapter in M2: rejected because it creates runtime
  integration and policy-attachment dependencies without testing contract value.
