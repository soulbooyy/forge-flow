# ForgeFlow Git and Review Practices

## 1. When to Use Grill-Me

Grill-Me is a design review mechanism. It should pressure-test assumptions, expose scope creep, and sharpen architectural boundaries.

Use Grill-Me:

- after Project Foundation Proposal is drafted
- after each major RFC draft is ready
- when OpenSpec feature scope is unclear
- when scope creep or architecture boundary confusion appears

Do not use Grill-Me:

- for every small function
- for simple implementation tasks whose scope is already clear
- as a replacement for tests
- as a replacement for RFCs or OpenSpec documents

Modes:

- Report mode: produce a one-time architecture review report with critical questions, risks, scope cuts, and readiness checks.
- Interactive mode: ask one question at a time and wait for an answer before continuing.

Grill-Me feedback should be incorporated into the relevant document rather than left only in chat history.

## 2. When to Use RFC

Use an RFC for decisions that affect architecture, project boundaries, safety, state, contracts, runtime integration, or evaluation.

RFCs are appropriate for:

- cross-module architecture changes
- agent role or workflow changes
- state and contract design
- tool permission model
- sandbox security model
- observability and evaluation design
- DeerFlow extension strategy

RFCs are not appropriate for:

- small bug fixes
- single test changes
- documentation wording changes
- local implementation details that do not affect architecture boundaries

Recommended RFC structure:

- Title
- Status
- Context
- Problem Statement
- Goals
- Non-goals
- Proposed Design
- Alternatives Considered
- Trade-offs
- Risks
- Open Questions
- Decision Summary

An RFC may be accepted, rejected, superseded, or deferred.

## 3. When to Use OpenSpec

Use OpenSpec for feature-level planning before implementation.

Good OpenSpec candidates:

- Repository Context Service
- PatchProposal generation
- Validation workflow
- ReviewResult generation
- Draft PR creation

Each OpenSpec change should include at least:

- `proposal.md`
- `design.md`
- `tasks.md`

OpenSpec should not be used to:

- replace `vision.md`
- replace RFCs
- debate unresolved large architecture questions
- cover the entire GitHub Issue to Draft PR MVP in one change

The first OpenSpec change should be Repository Context Service, and only after the relevant RFC skeleton decisions exist.

## 4. When to Use ADR

Use ADRs to record accepted technical decisions.

Example ADR topics:

- Use DeerFlow as upstream reference.
- Treat agents as workflow roles in early phases.
- Use deterministic Repository Context Service.
- Require human approval for high-risk actions.
- Start evaluation with controlled fixtures instead of SWE-bench.

ADRs should be short and durable.

Recommended ADR structure:

- Context
- Decision
- Consequences
- Related RFCs

ADRs should not reopen the full debate. That belongs in RFCs.

## 5. Git Workflow

Use clear, specific commit messages.

Recommended examples:

```text
docs: add project vision
docs: define milestones and development process
docs(rfc): add agent architecture proposal
docs(rfc): refine state model after review
docs(openspec): add repository context service proposal
feat(context): implement repository file search
test(context): add repository context fixtures
chore: add DeerFlow upstream reference
```

Guidelines:

- documentation changes must be committed
- RFC, OpenSpec, and ADR changes should remain traceable to related code changes
- avoid vague messages such as `update`, `fix stuff`, or `misc changes`
- keep commits focused enough that project evolution can be understood from Git history

## 6. Branching Recommendation

Use a lightweight branch strategy suitable for a personal project that may become open source.

Recommendations:

- keep `main` stable
- use short-lived branches for documents, RFCs, specs, features, and fixes
- avoid heavyweight Git Flow unless project scale requires it later

Example branch names:

```text
docs/rfc-001-agent-architecture
docs/openspec-repository-context
feature/repository-context-service
fix/...
```

For implementation work belonging to a milestone, use the more specific
milestone-scoped name defined in `implementation-execution.md`:

```text
feature/m<NUMBER>-<milestone-topic-slug>
```

That branch remains assigned to the milestone's one worktree through closure;
individual phases use focused commits rather than new branches.

Merge only when the relevant document, spec, implementation, tests, or review expectations are satisfied.
