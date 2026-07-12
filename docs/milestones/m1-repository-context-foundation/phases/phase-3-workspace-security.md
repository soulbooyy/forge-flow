# Phase 3: Workspace Security

## 1. Goal

Establish the trusted workspace and path-containment boundary that later Repository Context file access must use.

## 2. Scope

### Included

- Caller-supplied `workspace_ref.root_id` validation and identity matching.
- Trusted workspace root validation.
- Stable, workspace-relative POSIX canonical paths.
- Parent traversal, external absolute-path, prefix-bypass, and symlink-escape protection.
- Cross-platform path-form checks needed to preserve the boundary.

### Excluded

- Scanning, directory traversal, ignore policy, text reads, binary detection, matching, ranking, evidence generation, result assembly, and service logic.
- Agents, workflows, DeerFlow integration, LLMs, embeddings, AST processing, semantic search, network, subprocesses, Git/PR, and memory.

## 3. Changed Files

| File | Change | Purpose |
| --- | --- | --- |
| `src/forgeflow/repository_context/__init__.py` | Modified | Export the public workspace-boundary types. |
| `src/forgeflow/repository_context/workspace.py` | Added | Implement trusted-root identity and read-only path-containment checks. |
| `tests/repository_context/test_workspace.py` | Added | Verify deterministic canonical paths and security boundary edge cases. |

## 4. Implementation

`WorkspaceBoundary.create()` binds an existing directory to a caller-supplied logical `root_id`; it does not infer identity from host paths, metadata, or workspace content. `validate_workspace_ref()` rejects unsafe identities and mismatches with stable error codes.

`canonical_path()` rejects lexical parent traversal before resolution, enforces containment against the resolved root, and returns only a lexical workspace-relative POSIX path. External absolute paths return `path_escape`; an in-workspace lexical path that resolves through a symlink outside the root returns `symlink_escape`. The module uses `pathlib` metadata and resolution for boundary enforcement only; it does not enumerate directories or read content.

## 5. Design Decisions

- The trusted root and logical caller identity are separate: root identity is explicit input, not a value derived from machine-specific filesystem data.
- Resolved paths enforce security containment, while lexical relative spelling is retained for stable, host-path-free output.
- Error codes are small, stable public values: `invalid_workspace`, `invalid_workspace_ref`, `workspace_identity_mismatch`, `path_escape`, and `symlink_escape`.
- Windows drive and UNC forms are treated as foreign absolute-like paths on non-Windows hosts; on Windows, native `Path` containment remains applicable.

## 6. TDD and Tests

The initial RED run added the workspace tests before the module and failed on the missing `workspace` API. GREEN introduced the minimal boundary. Follow-up RED/GREEN cycles added the public error-code annotation and cross-platform path regressions.

Test framework: Python `unittest`.

| Verification | Result |
| --- | --- |
| RED: `python3 -m unittest tests.repository_context.test_workspace -v` | Expected missing-module failure. |
| Targeted workspace suite | 14 tests passed after the final POSIX double-slash regression fix. |
| Targeted Windows-form regressions | 3 tests passed. |
| Cumulative Phase 1-3 suite: `python3 -m unittest tests.repository_context.test_contracts tests.repository_context.test_canonical tests.repository_context.test_workspace -v` | 34 tests passed. |

## 7. Important Fixes and Edge Cases

- Preserve the trusted lexical root for relative-path derivation while using the resolved root for containment; this handles lexical `/var` versus resolved `/private/var` forms without weakening symlink checks.
- Reject `..` traversal and absolute paths outside the workspace before any future file access.
- Reject Windows drive and UNC host-like paths on non-Windows hosts, including drive-like `root_id` values such as `C:`.
- Allow native Windows paths to use normal containment checks instead of treating every drive spelling as foreign.
- Handle a valid POSIX `//`-prefixed in-workspace absolute path after successful containment, without confusing it with a Windows UNC path.
- Use `relative_to()` containment rather than string-prefix checks, preventing root-prefix collisions.

## 8. Commit

- Full commit hash: `4b77b81971c9390e41f4a2beec50508c5919e4ea`
- Commit message: `feat(security): add workspace path boundary`

## 9. Acceptance

Tests verified deterministic relative output, root identity validation, parent traversal rejection, external absolute-path rejection, symlink escape rejection, and platform-specific path handling. The final independent security review accepted the boundary as consistent with the OpenSpec security constraints and the sandbox-governance direction.

Status: **Accepted**.

## 10. Scope Boundary Confirmation

This phase did not introduce a scanner, ignore rules, file traversal, content reads, binary detection, matching, ranking, evidence generation, a result envelope, or a Repository Context Service. It introduced no LLM, embedding, AST, semantic-search, network, shell/subprocess, Git/PR, memory, agent, workflow, or DeerFlow runtime behavior.

## 11. Follow-up

Next Phase: Deterministic Scanner.

Reconciliation status: phase numbering was aligned with the canonical plan on
2026-07-12.
