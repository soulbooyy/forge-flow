# Phase 8: Hardening

## 1. Goal

Close the remaining deterministic and security hardening gaps identified by the
Phase 7 acceptance suite: unreadable-file handling, line-bounded scanning,
symlink coverage reporting, and stable limitation ordering.

## 2. Scope

### Included

- Deterministic scanner limitations for binary files, unsupported UTF-8,
  unreadable files, bounded file scans, external symlinks, and symlink loops.
- Enforcement of `max_lines_per_file` using complete normalized-line prefixes.
- Propagation of scanner limitations into successful result envelopes and
  matching `RelevantFile.limitation_codes`.
- Stable sorting of limitation evidence IDs and remaining ordering ties by
  bounded detail.
- Regression coverage for scanner, service, acceptance, path-boundary, and
  canonical identity behavior.

### Excluded

- New retrieval capabilities, ranking signals, result fields, configuration
  profiles, or public service entry points.
- Command execution, fixture mutation, network access, subprocesses, Git/PR
  behavior, memory, agents, workflows, DeerFlow integration, LLMs, embeddings,
  ASTs, semantic search, production persistence, or secret-scanning policy.

## 3. Changed Files

| File | Change | Purpose |
| --- | --- | --- |
| `src/forgeflow/repository_context/scanner.py` | Modified | Bound text inspection by lines and produce deterministic scan coverage limitations. |
| `src/forgeflow/repository_context/assembly.py` | Modified | Merge scanner limitations, attach file limitation codes, and normalize deterministic limitation ordering. |
| `tests/repository_context/test_scanner.py` | Modified | Cover line bounds, unreadable files, binary/encoding limitations, and symlink escape/loop handling. |
| `tests/repository_context/test_service.py` | Modified | Cover canonical ordering of related evidence IDs and remaining limitation-order ties. |
| `tests/repository_context/test_acceptance.py` | Modified | Assert successful envelopes expose scanner limitations for unsupported and truncated content. |

## 4. Implementation

`ScanReport` now carries immutable coverage limitations alongside deterministic
candidate and count data. The scanner records a safe workspace-relative path
for unreadable files, binary files, unsupported encodings, bounded inspections,
external symlinks, and symlink loops. It does not inspect symlink target
content or return symlink targets as candidates.

After strict UTF-8 decoding and newline normalization, the scanner retains at
most `max_lines_per_file` complete lines. A byte- or line-bounded inspection is
marked `text_truncated`, so text evidence continues to identify its inspected
range rather than claiming full-file coverage.

Result assembly combines scanner and test-hint limitations before calculating
the final contract ID. It sorts each limitation's evidence IDs, resolves any
remaining limitation ordering ties by bounded detail, and projects file-scoped
codes onto returned relevant files without changing their direct-match evidence
or ranking.

## 5. Design Decisions

- Line limiting occurs after canonical newline normalization and retains whole
  lines, preserving original 1-based locator semantics.
- Non-text and unreadable inputs remain safe successful-result coverage facts,
  not validation errors or text evidence sources.
- Symlink entries remain non-candidates. Only unsafe external and looping
  targets receive explicit limitations; no target content is read or returned.
- Limitation normalization happens during assembly, immediately before the
  contract is constructed and hashed, so all successful outputs have one stable
  ordering rule.

## 6. TDD and Tests

The hardening tests were written before production changes. The first RED run
showed that line limits were unused, `ScanReport` had no limitations, read
errors propagated, scanner coverage did not reach the service envelope, and
limitation evidence IDs retained caller order. A second RED test showed that
equal limitation keys still retained caller detail order. GREEN added only the
scanner and assembly changes needed for those failures.

Test framework: Python `unittest` through the repository's `uv` environment.

| Verification | Result |
| --- | --- |
| RED: `uv run --no-sync python -m unittest tests.repository_context.test_scanner tests.repository_context.test_service tests.repository_context.test_acceptance -v` | Expected 4 failures and 4 missing-coverage errors. |
| RED ordering regression: `uv run --no-sync python -m unittest tests.repository_context.test_service.RepositoryContextServiceTests.test_assembly_uses_detail_to_break_remaining_limitation_ties -v` | Expected deterministic-order failure. |
| Targeted GREEN: `uv run --no-sync python -m unittest tests.repository_context.test_scanner tests.repository_context.test_service tests.repository_context.test_acceptance -v` | 24 tests passed. |
| Cumulative suite: `uv run --no-sync python -m unittest discover -s tests -v` | 63 tests passed. |
| Staged diff validation: `git diff --cached --check` | Passed. |

## 7. Important Fixes and Edge Cases

- A file whose text exceeds the line or byte bound produces
  `file_scan_truncated`; uninspected text cannot create matches.
- Binary and invalid UTF-8 files cannot create text results or content hashes,
  but positive file/path matches retain their appropriate limitation codes.
- A simulated permission failure becomes `unreadable_file` and does not abort a
  deterministic scan.
- External symlinks and self-referential loops are skipped without exposing
  target content and record `symlink_escape` or `symlink_loop` respectively.
- Existing Windows-drive, UNC-like path, double-slash, parent-traversal, and
  prefix-boundary regressions continued to pass in the full suite.

## 8. Commit

- Full implementation commit hash: `362d626bb7feae55fab0f5e8df79f8fd8f10aa9c`
- Commit message: `feat(scanner): harden deterministic coverage`

## 9. Acceptance

Phase 8 verifies that bounded and incomplete inspection is represented as
deterministic coverage limitations, scanner failures do not leak target or host
path data, and limitation ordering is part of stable contract behavior. The
complete Milestone 1 implementation suite passed with 63 tests.

The implementation remains aligned with the OpenSpec read-only deterministic
contract and preserves the existing workspace security boundary.

Status: **Accepted**.

## 10. Scope Boundary Confirmation

This phase did not introduce a new capability outside the canonical hardening
scope. It did not alter OpenSpec, RFC, ADR, configuration identity, canonical
serialization, scoring, evidence construction rules, result shape, command
policy, or workflow architecture. No command runner, network client, external
dependency, persistence layer, agent, workflow, DeerFlow runtime, LLM,
embedding, AST, semantic search, Git/PR, or memory behavior was added.

## 11. Follow-up

Next Phase: None. Milestone 1 implementation phases are complete.

Known reconciliation item: milestone closure, documentation status, and any
future feature planning remain outside this Phase.
