# ForgeFlow Documentation Registry

This registry describes where ForgeFlow knowledge lives and which documents are
authoritative for a given question. It is an index, not a second specification.

| Document class | Location | Authority | Update trigger |
| --- | --- | --- | --- |
| Product vision | `docs/product/` | Product direction | Intent or MVP boundary changes |
| Milestone roadmap | `docs/product/roadmap/` | Milestone scope and status | Milestone planning or closure |
| RFC | `rfcs/` | Architecture boundaries and rationale | Architecture proposal or revision |
| ADR | `adr/` | Accepted architecture decision | Decision acceptance or supersession |
| OpenSpec | `openspec/` | Feature requirements and acceptance criteria | Approved feature change |
| Process rules | `docs/process/` | Engineering workflow and documentation governance | Process decision |
| Implementation plan | `docs/milestones/<slug>/implementation-plan.md` | Phase sequence and implementation detail | Accepted planning reconciliation |
| Phase record | `docs/milestones/<slug>/phases/` | Completed phase facts | Each accepted phase |
| Milestone progress | `docs/milestones/<slug>/progress.md` | Current milestone execution state | Each phase or closure |
| Retrospective | `retrospectives/` | Completed-milestone learning | Milestone closure |
| Historical material | `docs/_history/` | Non-canonical reference only | Archival migration |

English stable documents are canonical. Existing `.zh.md` files are maintained
translations for stable product, architecture, and process rules. Rolling
progress, Phase records, and retrospectives are not translated by default.

When sources conflict, use the authority order defined in
[engineering workflow](process/engineering-workflow.md).
