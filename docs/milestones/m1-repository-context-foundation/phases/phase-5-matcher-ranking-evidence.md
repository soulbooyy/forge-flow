# Phase 5: Matcher, Ranking, and Evidence

## 1. Goal

Implement deterministic query normalization, direct repository matching, fixed
ranking, and evidence projection over Phase 4 scanner candidates.

## 2. Scope

### Included

- NFC, trim, whitespace-collapse, and casefolded query normalization.
- Bounded issue-text normalization as input context only.
- Direct filename, path, and line-based text matching.
- Same-line duplicate collapse, capped text locators, fixed scoring, deterministic
  match reasons, and score/path ordering.
- File-level and text-match evidence, stable evidence IDs, text-only search
  results, and inspected-text SHA-256 verification hashes.
- A controlled matching fixture, expected contract fragment, and acceptance-style
  matching/evidence skeleton before production retrieval logic.

### Excluded

- Validation precedence, result caps, limitations, run summary, final contract ID,
  test hints, and the public Repository Context Service.
- Unreadable-file and line-limit hardening.
- Agents, workflows, DeerFlow integration, LLMs, embeddings, AST processing,
  semantic search, network, subprocesses, Git/PR, and memory.

## 3. Changed Files

| File | Change | Purpose |
| --- | --- | --- |
| `openspec/changes/repository-context-foundation/fixtures/workspaces/phase-5-matching/src/payment.py` | Added | Provide a filename/path/text positive-match fixture. |
| `openspec/changes/repository-context-foundation/fixtures/workspaces/phase-5-matching/docs/notes.txt` | Added | Provide a text-only positive-match fixture. |
| `openspec/changes/repository-context-foundation/fixtures/workspaces/phase-5-matching/README.md` | Added | Provide a non-matching fixture file. |
| `openspec/changes/repository-context-foundation/fixtures/expected/phase-5-matching/matching.json` | Added | Pin a payload-free matching and locator contract fragment. |
| `src/forgeflow/repository_context/__init__.py` | Modified | Export Phase 5 public matching and normalization APIs. |
| `src/forgeflow/repository_context/normalization.py` | Added | Implement deterministic query and bounded issue-text normalization. |
| `src/forgeflow/repository_context/matching.py` | Added | Implement direct signals, ranking, ordering, and search-result projection. |
| `src/forgeflow/repository_context/evidence.py` | Added | Construct file/text evidence, hashes, and stable evidence IDs. |
| `tests/repository_context/test_matching.py` | Added | Verify the fixture skeleton and Phase 5 deterministic behavior. |

## 4. Implementation

`normalize_query()` retains a normalized display value and a separate casefolded
matching view. `normalize_issue_text()` bounds normalized issue text but does not
feed it into matching APIs.

`match_scanned_files()` accepts only Phase 4 `ScannedFile` values and direct
query signals. It derives `RankingInputs`, `match_score`, and ordered
`match_reasons`; relevant files are ordered by descending score and canonical
path. Text matches are line-local and emit one locator per matching line.

`evidence.py` emits file-level evidence without locators for filename/path
signals and text evidence with a 1-based inclusive locator, SHA-256 inspected
text hash, and full/truncated hash scope. `SearchResult` is emitted only for
text evidence. Evidence IDs use the Phase 2 canonical identity helper.

## 5. Design Decisions

- Query display normalization and casefolded matching are separate, preserving a
  stable normalized input while keeping matching case-insensitive.
- Only filename, path, and text-locator counts influence scores; issue text is
  structurally unable to influence retrieval.
- Evidence contains references, locators, and hashes rather than snippets or
  full content.
- Search results are ordered by canonical path and locator and cannot represent
  filename or path-only matches.
- Phase 5 establishes the minimum fixture and acceptance skeleton required by
  OpenSpec; Phase 7 remains responsible for complete end-to-end acceptance.

## 6. TDD and Tests

The RED test and fixture skeleton were added before the production modules. The
targeted command failed with `ModuleNotFoundError` for
`forgeflow.repository_context.matching`, demonstrating the missing Phase 5
public surface. GREEN added only normalization, matching, evidence, and exports.

Test framework: Python `unittest`.

| Verification | Result |
| --- | --- |
| RED: `python3 -m unittest tests.repository_context.test_matching -v` | Expected missing-module failure for `forgeflow.repository_context.matching`. |
| Targeted GREEN: same command | 5 tests passed. |
| Cumulative Phase 1-5 suite: `python3 -m unittest tests.repository_context.test_contracts tests.repository_context.test_canonical tests.repository_context.test_workspace tests.repository_context.test_scanner tests.repository_context.test_matching -v` | 45 tests passed. |

## 7. Important Fixes and Edge Cases

- NFC and whitespace normalization produce one casefolded matching view.
- Multiple or overlapping text occurrences on a line produce one locator.
- Equal scores use canonical path ascending as the relevant-file tie-breaker.
- File-level evidence uses `locator: null` and produces no search result.
- Truncated text evidence hashes only the inspected range and records the
  corresponding hash scope.

## 8. Commit

- Full implementation commit hash: `aba1e3dd59e14e029a1e78f5f9e0bf5efb63d240`
- Commit message: `feat(retrieval): add deterministic matching evidence`

## 9. Acceptance

The fixture skeleton and targeted tests verify direct signals, normalized query
behavior, issue-text isolation, line locators, score recomputability, stable
tie-breaking, evidence references, text-only search results, and hash scope.
The cumulative Phase 1-5 suite passed with 45 tests.

Status: **Accepted**.

## 10. Scope Boundary Confirmation

This phase did not implement result-envelope assembly, validation-error
construction, test hints, result caps, limitations, run summary, final contract
identity, or a public Repository Context Service. It introduced no command,
network, write, agent, workflow, DeerFlow, LLM, embedding, AST, semantic-search,
Git/PR, or memory behavior.

## 11. Follow-up

Next Phase: Result Envelope and Service.

No Phase 5 reconciliation item remains.
