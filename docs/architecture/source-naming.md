# Source Naming and Package Boundary Rules

## Purpose

Production source names describe what the software does. They do not describe
when it was built, which milestone funded it, or which delivery phase happened
to introduce it.

## Rules

1. Package, module, class, function, variable, enum value, API field, and
   public import names MUST use domain behavior or data meaning.
2. Production names MUST NOT contain milestone, phase, feature-number, sprint,
   experiment, slice, prototype, MVP, temporary-project, or worktree labels.
   Examples include `m4`, `phase_2`, `feature4`, `draft_mvp`, and `spike`.
3. Documentation may use milestone and phase labels for history, planning,
   evidence, and release tracking. Those labels MUST NOT leak into `src/` API
   names or persisted contract fields.
4. A package name MUST remain truthful after a milestone ends. Prefer
   `materialization`, `real_mutation`, `draft_pr`, or `approval_trace` over a
   delivery label.
5. New functionality MUST be placed under the narrowest stable domain
   namespace. Do not create a generic `mvp`, `experimental`, or `misc`
   namespace merely to group current work.
6. Renames of public imports MUST use a temporary compatibility re-export only
   when downstream consumers require a migration window. New code MUST use the
   semantic import path immediately.

## Governed Repository Changes Namespace

The repository-change workflow is a durable domain called **governed changes**.
Its production namespace is `forgeflow.governed_changes`:

```text
forgeflow.governed_changes/
├── action_execution/
├── artifact_security/
├── approval_trace/
├── draft_pr/
├── materialization/
└── real_mutation/
```

The names describe the capability owned by each package, rather than a
milestone. Future package placement follows the same rule:

| Responsibility | Production import path |
| --- | --- |
| controlled snapshot transformation and ephemeral payloads | `forgeflow.governed_changes.materialization` |
| fresh authority and requests for actual repository changes | `forgeflow.governed_changes.real_mutation` |
| fixture-only Draft PR adapter | `forgeflow.governed_changes.draft_pr` |

## Enforcement

- Every structural change includes an import-boundary test and a repository
  search for prohibited delivery labels in the affected `src/` subtree.
- Review rejects a name that explains project history instead of software
  behavior.
- Architecture records map milestones to packages; source packages never map
  themselves back to milestone identifiers.
