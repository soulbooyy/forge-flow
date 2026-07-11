# ADR-006: Store Evidence References, Not Evidence Payloads

## Status

Accepted

## Context

Repository context must be useful for later inspection, fixtures, audit references, and workflow artifacts without turning Milestone 1 into a persistence, observability, or secret-scanning system. The OpenSpec revision defines evidence references, locators, content hashes, limitations, and bounded run summaries, while excluding raw repository payloads by default.

This decision belongs in ADR because future contributors may reasonably want to store raw snippets, full file contents, tool outputs, runtime metadata, or production artifacts for debugging and convenience. That would alter ForgeFlow's security, privacy, persistence, and contract boundaries across multiple milestones.

## Decision

ForgeFlow stores repository evidence as references and verification metadata, not raw evidence payloads, in Milestone 1 repository context contracts.

`RepositoryContextResult` may include canonical workspace-relative paths, locators, deterministic evidence IDs, inspected-text content hashes, limitation records, and bounded run-summary facts. It must not include raw source snippets, full file contents, raw command output, host absolute paths, stack traces, environment variables, runtime metadata, or unbounded raw user input.

Inspected-text content hashes are allowed as evidence verification metadata. They are not raw payloads, not proof that content is secret-free, and not a substitute for production secret scanning.

Milestone 1 does not introduce production persistence, artifact storage, contract lookup APIs, retention policy, access-control model, storage migration, or storage-integrity infrastructure. Stable IDs support deterministic fixtures, regression tests, caller-owned references, and future linking only.

Production secret scanning is out of scope for Milestone 1. Payload-avoidance fixtures may include synthetic sensitive-looking values to verify bounded output behavior, but they must not imply secret detection or redaction capability.

## Alternatives Considered

- Store raw snippets for convenience: rejected because snippets can leak source, secrets, customer data, or sensitive issue content and create persistence obligations.
- Store full file contents in context results: rejected because repository context should identify evidence, not persist repository payloads.
- Add production artifact storage in Milestone 1: rejected because stable IDs do not require storage infrastructure, retention rules, or lookup APIs in the foundation slice.
- Add secret scanning before evidence references: rejected because detector rules, false positives, redaction semantics, and policy records are separate security work.

## Consequences

Positive consequences:

- Keeps repository context contracts bounded and safer to persist by callers.
- Preserves inspectability through paths, locators, IDs, limitations, and hashes.
- Avoids prematurely designing artifact storage and retention infrastructure.
- Keeps secret scanning as an explicit future security capability rather than an implicit claim.

Negative consequences / trade-offs:

- Human inspection may require re-reading the workspace at the referenced path and locator.
- Debugging without raw snippets may require additional local tooling.
- Content hashes can still reveal limited information in some threat models and must be handled as contract metadata with appropriate access control in future persistence work.

