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
| `docs/templates/` | Reusable lifecycle-document templates. They fix document responsibilities and required structure, not milestone-specific conclusions. |
| `openspec/templates/change/` | Reusable feature-change templates for OpenSpec proposal, design, tasks, and specification documents. |
| `docs/milestones/<milestone-directory-slug>/implementation-plan.md` | Canonical implementation sequence, file-level work, dependencies, TDD steps, and phase acceptance conditions. |
| `docs/milestones/<milestone-directory-slug>/` | Milestone status index and formal Phase Completion Records. |
| `retrospectives/` | Milestone retrospectives that record what worked, what failed, causes of rework, and follow-up improvements. |
| `README.md` | Project entry point. It should contain only stable high-level information and navigation to current docs. |

Documentation should be treated as part of the product, not as optional commentary.


## 2. Documentation Authority Hierarchy

```text
Vision
-> RFC (when major architecture exploration is needed)
-> ADR (when an architecture decision is accepted)
-> OpenSpec
-> Canonical Implementation Plan
-> Implementation
-> Phase Completion Record
-> Milestone Progress
```

- Vision explains why the work exists.
- RFCs define architecture when a major architectural question requires
  exploration; they are not routine milestone paperwork.
- ADRs record accepted architecture decisions; they are not required when no
  such decision is made.
- OpenSpec defines the feature contract.
- The canonical Implementation Plan defines how to execute the work.
- Implementation follows the accepted OpenSpec, ADRs, and canonical plan; it
  is an activity, not a competing documentation authority.
- Phase Completion Records state what a phase actually completed.
- Milestone Progress states where the milestone currently stands.

An AI-assisted draft never appears in this authority chain. It is non-authoritative
planning evidence and may inform the canonical plan only through explicit
reconciliation against the accepted repository authority.

## 3. Milestone Documentation Structure

Every milestone uses the same documentation structure. Create the milestone
directory when the milestone's canonical implementation plan is established:

For naming, `<milestone-topic-slug>` is the stable kebab-case topic name without
the milestone number (for example, `structured-patchproposal`).
`<milestone-directory-slug>` is `m<NUMBER>-<milestone-topic-slug>` (for
example, `m2-structured-patchproposal`). These terms are intentionally
different: the directory identifies the milestone number, while the historical
draft filename uses the topic name only.

```text
docs/milestones/
├── index.md
└── m<NUMBER>-<milestone-topic-slug>/
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
`retrospectives/m<NUMBER>-<milestone-topic-slug>.md`.

Before creating a canonical implementation plan, create one detailed
AI-assisted draft plan using Superpowers `writing-plans` and retain it at
`docs/_history/ai-assisted/implementation-plans/YYYY-MM-DD-<milestone-topic-slug>.md`.
It is historical planning evidence, not a second canonical plan. The canonical
plan must explicitly reconcile the draft with the accepted OpenSpec, relevant
RFCs, and accepted ADRs.

Both the draft and canonical plan use `Phase 1`, `Phase 2`, and so on as their
top-level execution structure. A phase is the unit of authorization, focused
commit, completion record, progress update, and acceptance. Use ordered tasks
or checkbox steps only inside a phase for its TDD and verification work. The
canonical plan controls phase names and boundaries after reconciliation;
historical drafts are not rewritten merely to retrofit an older format.

## 4. Phase Completion Records and Progress

Every implementation phase in every milestone must have one formal Phase
Completion Record at
`docs/milestones/<milestone-directory-slug>/phases/phase-<number>-<phase-name>.md`.
Derive the file name from the reconciled canonical implementation-plan phase
name in stable kebab-case; preserve established completion-record file names.
Do not derive future file names from a chat prompt.

Instantiate
[`docs/templates/milestone/phase-completion-record.template.md`](../templates/milestone/phase-completion-record.template.md)
without changing its required section structure. The `Changed Files` section
uses a `File | Change | Purpose` table. The `TDD and Tests` section records
RED, GREEN, any necessary refactor or corrective iteration, commands, targeted
results, and cumulative-suite results. The record captures completed engineering
facts, not agent dispatches, review-diff bodies, or temporary debugging
narration.

After each phase commit, create or update both the Phase Completion Record and the milestone `progress.md`. The completion record contains phase detail; `progress.md` is a concise milestone index with phase status, commit, record link, current phase, next incomplete phase, and milestone-level reconciliation items. Neither document redefines requirements, architecture, or sequencing.

`progress.md` does not replace a Phase Completion Record, record detailed implementation, or define requirements or architecture.

Do not generate Superpowers briefs, review diffs, rereview diffs, or agent execution reports by default. New architecture decisions belong in ADRs, requirement changes in OpenSpec, and sequencing changes in the canonical implementation plan.

After updating the completion record and progress index, provide a concise summary and stop for user confirmation. Do not automatically begin the next phase.

## 5. Translation Policy

English process documents are canonical. Existing `.zh.md` process documents are maintained translations for stable, durable process rules. Rolling progress records and temporary execution artifacts are not translated by default.

## 6. Template Lifecycle Governance

Templates standardize document responsibilities, lifecycle, and required
sections. They do not require every milestone to create every document, and
they do not supply requirements, architecture decisions, scope, or acceptance
criteria. Replace all angle-bracket placeholders when instantiating a template.

### 6.1 Milestone Lifecycle Templates

Use the following templates when their lifecycle condition is met:

| Template | Lifecycle condition | Authority and purpose |
|---|---|---|
| `docs/templates/milestone/index.template.md` | Create when the canonical plan is established. | Milestone entry point and links only. |
| `docs/templates/ai-assisted/implementation-draft.template.md` | Create after OpenSpec and any relevant accepted RFCs/ADRs are ready, before the canonical plan. | Non-authoritative Superpowers `writing-plans` evidence; must be reconciled. |
| `docs/templates/milestone/implementation-plan.template.md` | Create after draft review and reconciliation. | The one canonical execution plan. |
| `docs/templates/milestone/progress.template.md` | Create with the canonical plan; update after every accepted phase. | Execution state only. |
| `docs/templates/milestone/phase-completion-record.template.md` | Create only after an accepted phase commit. | Completed engineering facts for that phase. |
| `docs/templates/milestone/retrospective.template.md` | Create at milestone closure. | Outcome, evidence, lessons, and deferred work. |

The milestone index, canonical plan, and progress index are standard lifecycle
documents for an implementation milestone. A phase completion record exists
only for a completed phase, and a retrospective exists only after closure.

### 6.2 OpenSpec Change Templates

Every OpenSpec change uses the templates under `openspec/templates/change/` for
its required `proposal.md`, `design.md`, `tasks.md`, and feature
`specs/<capability>/spec.md`. The change may add narrowly scoped contract,
policy-profile, fixture, or other supporting documents when its accepted scope
requires them; such supporting documents are not empty mandatory boilerplate.

### 6.3 Conditional Architecture Records

Create an RFC only for a major architecture exploration or unresolved
cross-cutting boundary. Create an ADR only when a decision is accepted and
needs a durable record. Neither is a per-milestone checklist item. If an
OpenSpec depends on either record, link the accepted record rather than
copying its content into the milestone directory.

### 6.4 Adoption and Tooling Boundary

Instantiate templates manually for M2 and M3 and improve them only when actual
use exposes a stable gap. Do not add document-generation scripts, scaffolding
commands, or automatic synchronization during this validation period. Any
future tooling must preserve the authority chain and must not make an
AI-assisted draft authoritative.
