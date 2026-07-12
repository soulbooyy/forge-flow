# Phase 3 Report: Workspace/Path Foundation

## Scope

Implemented only the trusted workspace/path security boundary for Repository
Context Phase 3. No scanner, traversal, ignore policy, content reads, service,
validation envelope, integration, subprocess, Git, network, memory, LLM,
embedding, AST, or semantic-search behavior was added.

## Changed Files

- Created `src/forgeflow/repository_context/workspace.py`
  - `WorkspaceBoundaryError` with public `code: str`.
  - `WorkspaceBoundary.create`, `root_id`, `validate_workspace_ref`, and
    `canonical_path`.
  - Direct `pathlib` metadata and resolution only; no file-content access or
    directory enumeration.
- Created `tests/repository_context/test_workspace.py`
  - Covers canonical relative and nested paths, parent traversal, absolute
    containment, symlink escape, workspace identity mismatch, invalid root IDs,
    invalid roots, no host-root leakage, and the error-code annotation.
- Modified `src/forgeflow/repository_context/__init__.py`
  - Exports `WorkspaceBoundary` and `WorkspaceBoundaryError`.

## TDD Evidence

### RED: missing module

Test file was created before `workspace.py` existed.

Command:

```sh
/Users/soulboy/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest tests.repository_context.test_workspace -v
```

Observed result:

```text
ERROR: test_workspace (unittest.loader._FailedTest.test_workspace)
ModuleNotFoundError: No module named 'forgeflow.repository_context.workspace'
Ran 1 test in 0.000s
FAILED (errors=1)
```

### GREEN iteration

After the initial direct implementation, the workspace test command exposed two
platform-lexical failures: an absolute temporary path spelled below `/var` did
not lexically match its resolved `/private/var` form, and the resulting branch
misclassified the symlink escape. The boundary was corrected to retain the
trusted root's lexical absolute spelling for returned-relative-path handling,
while retaining the resolved root solely for containment enforcement.

The workspace suite then passed:

```text
Ran 9 tests in 0.003s
OK
```

### RED: public exception annotation

The fixed public interface declares `WorkspaceBoundaryError.code: str`, so a
test was added before the annotation.

Command:

```sh
/Users/soulboy/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest tests.repository_context.test_workspace.WorkspaceBoundaryTests.test_boundary_error_exposes_a_string_code -v
```

Observed result:

```text
ERROR: test_boundary_error_exposes_a_string_code
KeyError: 'code'
Ran 1 test in 0.001s
FAILED (errors=1)
```

The annotation was added before final Phase 1-3 verification.

## Required Phase 1-3 Verification

The required command was run twice:

```sh
/Users/soulboy/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest tests.repository_context.test_contracts tests.repository_context.test_canonical tests.repository_context.test_workspace -v
```

Run 1 result:

```text
Ran 30 tests in 0.005s
OK
```

Run 2 result:

```text
Ran 30 tests in 0.004s
OK
```

## Security Review

- Root identity is the caller-supplied `root_id`; it is never calculated from
  host paths, metadata, timestamps, machine state, or workspace contents.
- Root IDs reject empty, leading/trailing-whitespace, `.`, `..`, slash,
  backslash, and over-255-character values with `invalid_workspace_ref`.
- Workspace roots must exist and be directories, otherwise `invalid_workspace`.
- Relative `..` input is rejected before resolution with `path_escape`.
- Resolved containment is enforced against the resolved root. Absolute paths
  outside the root return `path_escape`; paths that lexically begin inside the
  workspace but resolve through an escaping symlink return `symlink_escape`.
- Returned values are lexical workspace-relative POSIX paths only. The test
  asserts that the temporary absolute root never appears in a return value.
- The implementation reads metadata/resolution only and neither enumerates the
  workspace nor reads target content.

## Self-Review

- Confirmed scope is limited to the three brief-authorized code/test files plus
  this required report.
- Confirmed `__init__.py` exports only the required public workspace types.
- Confirmed no new dependencies, network access, shell/subprocess behavior, or
  unrelated repository edits.
- Ran `git diff --check` successfully before report creation; it will be run
  again over the final report-inclusive diff before commit.
- Removed generated `__pycache__` directories after verification.

## Concerns

None. Symlink tests ran successfully on this platform and were not skipped.

## Security Finding Fix Addendum

### TDD RED

Focused regression tests were added before changing production code for:

- Windows drive and UNC absolute-like canonical inputs;
- Windows drive/path-like root IDs during boundary creation;
- `validate_workspace_ref(WorkspaceRef(root_id="C:"))`.

Command:

```sh
/Users/soulboy/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest tests.repository_context.test_workspace.WorkspaceBoundaryTests.test_windows_absolute_like_paths_are_rejected_on_posix_hosts tests.repository_context.test_workspace.WorkspaceBoundaryTests.test_unsafe_or_missing_root_id_is_rejected tests.repository_context.test_workspace.WorkspaceBoundaryTests.test_drive_like_workspace_ref_is_invalid_before_identity_matching -v
```

Observed RED result:

```text
Ran 3 tests in 0.002s
FAILED (failures=4)
```

The two drive-spelled paths and `C:` root ID were incorrectly accepted. The
validation case raised `workspace_identity_mismatch` instead of
`invalid_workspace_ref`.

### TDD GREEN

The focused workspace suite passed after the production fix:

```text
Ran 12 tests in 0.004s
OK
```

The required Phase 1-3 suite was then run twice with the bundled Python 3.12
runtime. Both runs passed:

```text
Ran 32 tests in 0.005s
OK

Ran 32 tests in 0.006s
OK
```

### Fix Notes

- `canonical_path` now checks the original input spelling with
  `PureWindowsPath` before converting backslashes to POSIX separators. Any
  non-empty Windows drive/UNC anchor raises `path_escape`, so drive and UNC
  host-like inputs cannot become returned relative strings on POSIX hosts.
- Safe root ID validation applies the same drive/UNC path-form check. This
  rejects `C:` and anchored Windows path-like values as
  `invalid_workspace_ref` before identity comparison.
- No public API, later Phase behavior, or unrelated files were changed.

## Takeover Validation Evidence

The carried security review fix was re-inspected without changing its production
or test code. The focused regression command passed under the bundled Python
3.12 runtime:

```sh
/Users/soulboy/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest tests.repository_context.test_workspace.WorkspaceBoundaryTests.test_windows_absolute_like_paths_are_rejected_on_posix_hosts tests.repository_context.test_workspace.WorkspaceBoundaryTests.test_unsafe_or_missing_root_id_is_rejected tests.repository_context.test_workspace.WorkspaceBoundaryTests.test_drive_like_workspace_ref_is_invalid_before_identity_matching -v
```

```text
Ran 3 tests in 0.002s
OK
```

The required Phase 1-3 suite was then run twice again:

```text
Run 1: Ran 32 tests in 0.005s
OK

Run 2: Ran 32 tests in 0.006s
OK
```

## Cross-Platform Review Fix

The re-review identified that rejecting every Windows-drive spelling would also
reject a valid in-workspace absolute path on a native Windows host. The
platform-specific classification test was added first.

### RED

```text
AttributeError: module 'forgeflow.repository_context.workspace' has no attribute '_is_foreign_windows_path'
Ran 1 test in 0.001s
FAILED (errors=1)
```

### GREEN

`_is_foreign_windows_path` now rejects drive/UNC forms only when the current
host is not Windows. On Windows, native `Path` handling continues to apply the
same resolved-root containment check used for other absolute paths.

```text
Ran 13 tests in 0.009s
OK
```

## POSIX Double-Slash Review Fix

The final review found that a valid POSIX `//`-prefixed in-workspace absolute
path was treated as a Windows UNC path. A regression test was added first.

### RED

```text
WorkspaceBoundaryError: path_escape
Ran 1 test in 0.002s
FAILED (errors=1)
```

The first narrow classification fix exposed a second lexical-relative issue:
the resolved path was contained, but `//` spelling could not be relativized to
the trusted root. The relative-derivation helper now collapses one leading
slash only after containment succeeds.

### GREEN

```text
Ran 14 tests in 0.008s
OK
```
