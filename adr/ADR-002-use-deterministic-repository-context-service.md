# ADR-002: Use Deterministic Repository Context Service

Status: Accepted  
Date: 2026-07-10

## Context

ForgeFlow's first implementation milestone is not the full GitHub Issue to Draft PR MVP. Milestone 1 is the Repository Context Foundation Slice.

The platform needs reliable repository facts before it can safely generate patches, run validation, perform review, or create draft pull requests. RFC-001 and RFC-002 establish that repository context should come from deterministic services and evidence references, not from autonomous agent inference.

## Decision

Milestone 1 uses a deterministic Repository Context Service, not a Repository Context Agent.

Repository Context Service returns repository facts, relevant files, evidence references, file/text search results, optional cheap language-agnostic symbol hints, and simple test command hints.

It produces `RepositoryContextResult`.

During Milestone 1, Repository Context Service must not perform LLM reasoning. It must not infer root cause, summarize code meaning as authoritative fact, rank results by unverifiable semantic judgment, select repair strategy, generate patches, edit code, run validation loops, create PRs, or write memory.

This keeps Milestone 1 as a foundation slice rather than the full MVP.

## Consequences

Positive consequences:

- Makes repository context reproducible and evidence-backed.
- Keeps repository facts separate from agent judgment.
- Gives later `PatchProposal`, `ValidationResult`, `ReviewResult`, and `PRResult` workflows a stable input boundary.
- Keeps Milestone 1 small enough to evaluate with controlled fixtures.
- Reduces the risk of building an implicit agent behind a service boundary.

Negative consequences / trade-offs:

- Milestone 1 will not demonstrate automatic repair or draft PR creation.
- Initial retrieval quality may be limited without LLM-assisted semantic ranking.
- More sophisticated code intelligence is deferred.

Follow-up implications:

- The first OpenSpec change should target Repository Context Service.
- Later LLM-assisted ranking or summarization requires separate RFC or OpenSpec approval.
- Future patch generation must consume `RepositoryContextResult` rather than bypassing deterministic context.
- Evaluation should include context retrieval precision, evidence quality, and test hint usefulness.

## Alternatives Considered

- Treat Repository Context as an agent: rejected for Milestone 1 because repository facts must be deterministic and evidence-backed.
- Build full Code Intelligence with dependency graph, issue retrieval, and embeddings first: rejected because it would expand Milestone 1 beyond the foundation slice.
- Start with patch generation before context service: rejected because it would make patches depend on unstable or implicit repository understanding.

## Related Documents

- [RFC-001: Agent Architecture](../rfcs/RFC-001-agent-architecture.md)
- [RFC-002: Contracts and State Model](../rfcs/RFC-002-contracts-and-state-model.md)
- [RFC-004: Sandbox and Security Governance](../rfcs/RFC-004-sandbox-and-security-governance.md)
- [Vision](../docs/product/vision.md)
- [Milestones](../docs/product/roadmap/milestones.md)
