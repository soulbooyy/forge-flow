# ForgeFlow Document Governance

## 1. Document Types and Responsibilities

| Document | Responsibility |
|---|---|
| `docs/product/vision.md` | Project vision, target users, long-term direction, MVP boundary, Milestone 1 boundary, and core principles. |
| `docs/product/roadmap/milestones.md` | Stage planning. Defines Milestone 1, MVP, later phases, scope exclusions, and exit criteria. |
| `docs/architecture/foundation/project-foundation-proposal.md` | Pre-RFC foundation design proposal. It is early design input, not the final architecture specification. |
| `rfcs/` | Major architecture decisions such as Agent Architecture, State Model, Tool/MCP Integration, Sandbox Governance, Evaluation Framework, and DeerFlow Extension Strategy. |
| `openspec/` or `specs/changes/` | Feature-level specifications such as Repository Context Service, PatchProposal generation, Validation workflow, ReviewResult generation, and Draft PR creation. |
| `adr/` | Accepted architecture decision records, usually created after RFC discussion reaches a decision. |
| `docs/_history/ai-assisted/implementation-plans/` | Versioned, non-canonical detailed draft plans generated with Superpowers `writing-plans` after architecture and specification inputs are ready. |
| `docs/milestones/<milestone-slug>/implementation-plan.md` | Canonical implementation sequence, file-level work, dependencies, TDD steps, and phase acceptance conditions. |
| `docs/milestones/<milestone-slug>/` | Milestone status index and formal Phase Completion Records. |
| `retrospectives/` | Milestone retrospectives that record what worked, what failed, causes of rework, and follow-up improvements. |
| `README.md` | Project entry point. It should contain only stable high-level information and navigation to current docs. |

Documentation should be treated as part of the product, not as optional commentary.


## 2. Documentation Authority Hierarchy

```text
Vision
-> RFC
-> ADR
-> OpenSpec
-> Implementation Plan
-> Phase Completion Record
-> Milestone Progress
```

- Vision explains why the work exists.
- RFCs define the architecture.
- ADRs record settled architectural choices.
- OpenSpec defines the feature contract.
- The Implementation Plan defines how to execute the work.
- Phase Completion Records state what a phase actually completed.
- Milestone Progress states where the milestone currently stands.

## 3. Milestone Documentation Structure

Every milestone uses the same documentation structure. Create the milestone
directory when the milestone's canonical implementation plan is established:

```text
docs/milestones/
├── index.md
└── m<NUMBER>-<milestone-slug>/
    ├── index.md
    ├── implementation-plan.md
    ├── progress.md
    └── phases/
        ├── phase-1-<canonical-phase-name>.md
        ├── phase-2-<canonical-phase-name>.md
        └── ...
```

The milestone `index.md` is the entry point and contains a concise scope
summary, the authoritative-reference links, and navigation to the plan,
progress index, and completion records. `implementation-plan.md` is the one
canonical plan for the milestone. `progress.md` is the milestone-level status
index. `phases/` contains formal completion records only for phases that have
actually completed.

Do not create milestone-local copies of OpenSpec, RFCs, ADRs, or the
retrospective. Link to those authoritative records instead. The retrospective
is created after milestone closure at
`retrospectives/m<NUMBER>-<milestone-slug>.md`.

Before creating a canonical implementation plan, create one detailed
AI-assisted draft plan using Superpowers `writing-plans` and retain it at
`docs/_history/ai-assisted/implementation-plans/YYYY-MM-DD-<milestone-slug>.md`.
It is historical planning evidence, not a second canonical plan. The canonical
plan must explicitly reconcile the draft with the accepted OpenSpec, relevant
RFCs, and accepted ADRs.

## 4. Phase Completion Records and Progress

Every implementation phase in every milestone must have one formal Phase Completion Record at `docs/milestones/<milestone-slug>/phases/phase-<number>-<phase-name>.md`. Derive the file name from the reconciled canonical implementation-plan phase name in stable kebab-case; preserve established completion-record file names. Do not derive future file names from a chat prompt.

All Phase Completion Records use exactly this template. No later phase may use a shortened or different structure:

```text
# Phase X: <Phase Name>

## 1. Goal
## 2. Scope
### Included
### Excluded
## 3. Changed Files
## 4. Implementation
## 5. Design Decisions
## 6. TDD and Tests
## 7. Important Fixes and Edge Cases
## 8. Commit
## 9. Acceptance
## 10. Scope Boundary Confirmation
## 11. Follow-up
```

The `Changed Files` section uses a `File | Change | Purpose` table. The `TDD and Tests` section records RED, GREEN, any necessary refactor or corrective iteration, commands, targeted results, and cumulative-suite results. The record captures completed engineering facts, not agent dispatches, review-diff bodies, or temporary debugging narration.

After each phase commit, create or update both the Phase Completion Record and the milestone `progress.md`. The completion record contains phase detail; `progress.md` is a concise milestone index with phase status, commit, record link, current phase, next incomplete phase, and milestone-level reconciliation items. Neither document redefines requirements, architecture, or sequencing.

`progress.md` does not replace a Phase Completion Record, record detailed implementation, or define requirements or architecture.

Do not generate Superpowers briefs, review diffs, rereview diffs, or agent execution reports by default. New architecture decisions belong in ADRs, requirement changes in OpenSpec, and sequencing changes in the canonical implementation plan.

After updating the completion record and progress index, provide a concise summary and stop for user confirmation. Do not automatically begin the next phase.

## 5. Translation Policy

English process documents are canonical. Existing `.zh.md` process documents are maintained translations for stable, durable process rules. Rolling progress records and temporary execution artifacts are not translated by default.
