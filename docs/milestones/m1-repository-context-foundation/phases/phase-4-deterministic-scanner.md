# Phase 4: Deterministic Scanner

## 1. Goal

Provide a deterministic, read-only repository scanner that operates only inside
the trusted workspace boundary established by Phase 3.

## 2. Scope

### Included

- Stable directory-entry ordering and repository candidate enumeration.
- Fixed ignore policy for `.git`, `.forgeflow/cache`, `.forgeflow/artifacts`,
  and OpenSpec fixture output directories.
- Bounded binary reads, NUL-byte binary detection, strict UTF-8 decoding, BOM
  removal, and line-ending normalization.
- Text, binary, unsupported-encoding, and truncation classification.
- Deterministic file, directory, and skipped-entry counts.

### Excluded

- Query normalization, matching, ranking, evidence construction, locators,
  content-hash output, result assembly, validation envelopes, and service logic.
- Unreadable-file limitations and line-limit limitation output; these remain
  hardening work under the reconciled canonical plan.
- Agents, workflows, DeerFlow integration, LLMs, embeddings, AST processing,
  semantic search, network, subprocesses, Git/PR, and memory.

## 3. Changed Files

| File | Change | Purpose |
| --- | --- | --- |
| `src/forgeflow/repository_context/__init__.py` | Modified | Export scanner types and entry point. |
| `src/forgeflow/repository_context/workspace.py` | Modified | Expose the resolved root for internal read-only scanner use. |
| `src/forgeflow/repository_context/scanner.py` | Added | Implement deterministic traversal, classification, bounded reads, and ignore policy. |
| `tests/repository_context/test_scanner.py` | Added | Verify scanner ordering, limits, text decoding, ignores, and symlink handling. |

## 4. Implementation

`scan_workspace()` traverses the `WorkspaceBoundary` root with `os.scandir()`
and sorts entries by observed name before processing. It skips symlinks, applies
the fixed ignore policy without consulting `.gitignore`, and returns immutable
`ScannedFile` entries plus deterministic discovery and skip counts.

Each candidate is read only up to the configured byte limit plus one detection
byte. A NUL byte classifies the file as binary before decoding; strict UTF-8
failure produces `unsupported_encoding`. Text candidates remove a leading BOM
and normalize CRLF and CR line endings to LF. The scanner never writes to the
workspace or returns file contents beyond the bounded inspected text.

## 5. Design Decisions

- Scanner ordering is explicit rather than inherited from filesystem iteration
  order.
- Ignore behavior is fixed and does not use Git or ecosystem conventions.
- Symlinks are traversal controls and are never followed or returned as file
  candidates.
- Classification is data-only and leaves retrieval, ranking, and evidence
  decisions to later phases.

## 6. TDD and Tests

The historical commit introduced focused scanner tests with the implementation.
A standalone RED transcript was not retained, so this record does not infer one.
The reconciliation independently verified the committed capability with Python
`unittest`.

| Verification | Result |
| --- | --- |
| Historical focused scanner coverage | 6 tests in `test_scanner.py` cover deterministic ordering, nested text, binary classification, fixed ignores, bounded reads, UTF-8 failure, and symlink non-following. |
| Reconciliation cumulative suite: `python3 -m unittest tests.repository_context.test_contracts tests.repository_context.test_canonical tests.repository_context.test_workspace tests.repository_context.test_scanner -v` | 40 tests passed. |

## 7. Important Fixes and Edge Cases

- Repeated scans of the same workspace return identical `ScanReport` values.
- `.gitignore` and dependency-directory conventions do not alter the fixed
  ignore policy.
- Binary and invalid UTF-8 files are classified without lossy decoding.
- Symlink entries are not followed, preventing scanner traversal outside the
  trusted workspace.

## 8. Commit

- Full commit hash: `14e9bae890e2a5102fedc959d88e2cb27a76d769`
- Commit message: `feat(scanner): add deterministic repository scanner`

## 9. Acceptance

The historical commit was independently re-verified against the Phase 1-4
cumulative suite. Its implementation is aligned with the reconciled Phase 4
scanner foundation: deterministic ordering, fixed ignores, bounded direct
reads, strict UTF-8 handling, binary detection, and no workspace mutation.

Status: **Accepted**.

## 10. Scope Boundary Confirmation

This phase did not add matching, ranking, evidence generation, line locators,
content-hash output, result assembly, validation envelopes, or a Repository
Context Service. It introduced no external tools, network access, agents,
workflows, DeerFlow runtime behavior, LLMs, embeddings, ASTs, semantic search,
Git/PR, or memory.

## 11. Follow-up

Next Phase: Matcher, Ranking, and Evidence.

Known reconciliation item: the historical scanner commit has no standalone RED
transcript. The independent reconciliation test run is recorded above; future
phases must follow the current TDD documentation rule prospectively.
