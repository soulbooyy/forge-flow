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

### 1.2 Milestone Execution Environment Assignment

Before starting Phase 1, assign one isolated branch and worktree to the entire
milestone. The required names are:

```text
Branch:    feature/m<NUMBER>-<milestone-topic-slug>
Worktree:  .worktrees/m<NUMBER>-<milestone-topic-slug>
```

The worktree directory must be ignored by Git. Record the exact assigned
branch, worktree, and execution mode in the milestone `progress.md` under
`Execution Environment` before writing Phase 1 tests or production code. If
the assignment is absent, Phase 1 is blocked even when its architecture,
specification, plan, and user authorization are otherwise ready.

The same branch and worktree remain assigned through milestone closure. A
phase does not create a branch boundary: it uses the assigned environment and
ends with one focused commit, verification, a Completion Record, and a progress
update. Create a different branch or worktree only when an accepted workflow
decision or the canonical plan explicitly requires it.

This model has three distinct boundaries: a milestone owns isolation scope, a
phase owns execution scope, and a commit owns review scope.

### 1.3 Phase Identification

Identify the next phase from the canonical implementation plan and the last completed entry in the milestone `progress.md`. Reconcile any mismatch between execution numbering and the canonical plan before implementation begins.

When a new milestone enters implementation, initialize the standard milestone
documentation structure defined in `document-governance.md`: `index.md`, the
canonical `implementation-plan.md`, `progress.md`, and an empty `phases/`
directory. Create a Phase Completion Record only when its phase is accepted;
its file name must be derived from the canonical plan. This structure is
mandatory for every milestone and every phase; no abbreviated alternative is
permitted.

### 1.4 Test-Driven Development

Each phase follows RED -> GREEN -> REFACTOR:

- add or change a test before production behavior;
- confirm it fails because the current capability is absent or incorrect;
- implement the smallest code that satisfies the current phase;
- run targeted tests, then the complete implemented suite;
- perform only small, phase-scoped refactoring after green.

Tests added after a complete implementation are not a substitute for this sequence.

### 1.5 Scope Control

Implement exactly one canonical-plan phase at a time. Do not add future-phase abstractions, modify unrelated modules, or expand feature scope. Missing or conflicting authority is a stop condition, not permission to fill the gap.

### 1.6 Git and Commit Strategy

Use the branch and worktree assigned to the milestone. Do not create a new
branch or worktree for each phase unless the canonical plan or an accepted
workflow decision explicitly requires it.

Create one focused commit per phase. Before committing, run targeted tests, the complete implemented test suite, `git diff --check`, and `git status --short`; inspect generated files and unrelated modifications.

### 1.7 Review Strategy

The default lightweight review is a self-review of the current diff, passing tests, and scope boundaries. Do not generate subagent briefs, review diffs, rereview diffs, or long checkpoint reports by default.

Escalate to independent review when a change modifies a feature contract, security boundary, canonical identity algorithm, external dependency, or cross-platform security behavior; when it diverges from the canonical plan; or when explicitly requested by the user.

### 1.8 Execution-Assistance Boundary

Superpowers is a recommended execution-assistance framework. It may help apply
the existing plan through TDD, verification, focused review, and other
engineering discipline, but it is not a ForgeFlow architecture dependency or a
required implementation framework. An equivalent framework or disciplined
manual practice may replace it.

The Lightweight Implementation Execution rules above remain mandatory
regardless of the assistant or framework selected. Tool choice must not change
the authority of RFCs, ADRs, OpenSpec, the canonical implementation plan, or
the milestone lifecycle; it must not create a runtime, package, provider, or
repository dependency on the selected tool.
