# ForgeFlow Implementation Execution

## 1. Lightweight Implementation Execution

This mode applies to narrowly scoped, accepted implementation phases in every ForgeFlow milestone. It preserves TDD, scope control, focused commits, formal completion records, and durable progress without treating AI execution artifacts as long-term engineering documentation.

### 1.1 Authoritative Inputs

Before starting a phase, read the current feature specification, relevant RFCs, accepted ADRs, the canonical implementation plan, and the milestone `progress.md`. Chat prompts may provide context, but they do not define phase interfaces, file lists, acceptance criteria, or scope.

The authority order for conflicts is:

1. OpenSpec or the accepted feature specification for requirements, acceptance criteria, and exclusions.
2. Accepted ADRs for binding architecture decisions.
3. RFCs for architecture boundaries and deferred decisions.
4. The canonical implementation plan for implementation sequence and task detail.
5. Milestone progress for execution state only.

If these sources conflict or do not identify a safe next phase, stop implementation and report the conflict. Do not invent an architecture decision or silently revise an authoritative source.

### 1.2 Phase Identification

Identify the next phase from the canonical implementation plan and the last completed entry in the milestone `progress.md`. Reconcile any mismatch between execution numbering and the canonical plan before implementation begins.

### 1.3 Test-Driven Development

Each phase follows RED -> GREEN -> REFACTOR:

- add or change a test before production behavior;
- confirm it fails because the current capability is absent or incorrect;
- implement the smallest code that satisfies the current phase;
- run targeted tests, then the complete implemented suite;
- perform only small, phase-scoped refactoring after green.

Tests added after a complete implementation are not a substitute for this sequence.

### 1.4 Scope Control

Implement exactly one canonical-plan phase at a time. Do not add future-phase abstractions, modify unrelated modules, or expand feature scope. Missing or conflicting authority is a stop condition, not permission to fill the gap.

### 1.5 Git and Commit Strategy

Use the branch and worktree assigned to the milestone. Do not create a new branch or worktree for each phase unless the canonical plan or an accepted workflow decision explicitly requires it.

Create one focused commit per phase. Before committing, run targeted tests, the complete implemented test suite, `git diff --check`, and `git status --short`; inspect generated files and unrelated modifications.

### 1.6 Review Strategy

The default lightweight review is a self-review of the current diff, passing tests, and scope boundaries. Do not generate subagent briefs, review diffs, rereview diffs, or long checkpoint reports by default.

Escalate to independent review when a change modifies a feature contract, security boundary, canonical identity algorithm, external dependency, or cross-platform security behavior; when it diverges from the canonical plan; or when explicitly requested by the user.
