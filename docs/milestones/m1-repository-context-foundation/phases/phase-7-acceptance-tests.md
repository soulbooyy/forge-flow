# Phase 7: Acceptance Tests

## 1. Goal

Add deterministic end-to-end acceptance coverage for the implemented Milestone 1
Repository Context contract using fixed workspaces, expected contract fragments,
and side-effect checks.

## 2. Scope

### Included

- Service-level coverage for deterministic repeated execution, canonical IDs,
  normalized query input, validation envelopes, bounded issue text, and
  query-only retrieval.
- Fixed workspace and expected-output fragments covering stable path ordering,
  fixed ignore policy, root-only test hints, content-hash evidence, and
  no-dangling-reference invariants.
- Temporary read-only test fixtures for symlink escape, binary and invalid UTF-8
  candidates, line-based text matching, same-line duplicate collapse, ranking
  tie-breaking, and bounded text reads.
- Snapshot verification that service inspection does not mutate its fixture
  workspace.

### Excluded

- Production implementation changes.
- Phase 8 hardening for unreadable files, line-limit behavior,
  platform-specific path behavior, and remaining deterministic robustness work.
- Test-command execution, fixture mutation by the service, patch generation,
  network or external-tool use, agents, workflows, DeerFlow integration, LLMs,
  embeddings, ASTs, semantic search, Git/PR behavior, or memory.

## 3. Changed Files

| File | Change | Purpose |
| --- | --- | --- |
| `tests/repository_context/test_acceptance.py` | Added | Exercise the public service against deterministic acceptance fixtures and temporary boundary cases. |
| `openspec/changes/repository-context-foundation/fixtures/workspaces/phase-7-acceptance/README.md` | Added | Identify the fixed fixture workspace. |
| `openspec/changes/repository-context-foundation/fixtures/workspaces/phase-7-acceptance/.gitignore` | Added | Demonstrate that Git ignore rules are not applied. |
| `openspec/changes/repository-context-foundation/fixtures/workspaces/phase-7-acceptance/Makefile` | Added | Provide the root-only `make test` hint fixture. |
| `openspec/changes/repository-context-foundation/fixtures/workspaces/phase-7-acceptance/package.json` | Added | Provide the root-only `npm test` hint fixture. |
| `openspec/changes/repository-context-foundation/fixtures/workspaces/phase-7-acceptance/private.env` | Added | Supply synthetic sensitive-looking fixture content for payload-boundary checks. |
| `openspec/changes/repository-context-foundation/fixtures/workspaces/phase-7-acceptance/docs/notes.txt` | Added | Supply a text-only direct match. |
| `openspec/changes/repository-context-foundation/fixtures/workspaces/phase-7-acceptance/src/payment.py` | Added | Supply filename, path, and text direct matches. |
| `openspec/changes/repository-context-foundation/fixtures/workspaces/phase-7-acceptance/node_modules/kept-by-policy.txt` | Added | Verify dependency directories are not implicitly ignored. |
| `openspec/changes/repository-context-foundation/fixtures/workspaces/phase-7-acceptance/.forgeflow/cache/payment.txt` | Added | Verify an explicitly ignored directory is not descended into. |
| `openspec/changes/repository-context-foundation/fixtures/expected/phase-7-acceptance/result-fragment.json` | Added | Pin stable result paths, hints, and scan-count fragment. |
| `openspec/changes/repository-context-foundation/fixtures/expected/phase-7-acceptance/empty-query-error.json` | Added | Pin the stable validation-envelope fragment. |

## 4. Implementation

`test_acceptance.py` invokes the public `inspect_repository()` entry point rather
than internal phases. The fixed `phase-7-acceptance` workspace is scanned twice
with equivalent normalized queries and compared for complete equality. Expected
fragments assert returned paths, root-only hint commands, and deterministic scan
counts without storing a duplicate full contract payload.

The suite checks that returned evidence IDs resolve, text-match evidence has a
SHA-256 content hash, and returned paths remain canonical workspace-relative
POSIX paths. It also snapshots every fixture file before and after inspection.

Temporary workspaces verify that external symlink targets are not returned,
binary and unsupported-encoding candidates cannot create text results, text
beyond the configured bounded read range cannot match, and repeated tokens on a
single line produce one locator per line. Equal-scored files are ordered by
canonical path.

## 5. Design Decisions

- Acceptance assertions use small expected contract fragments instead of a
  second, hand-maintained full serialized result.
- The fixture includes `.gitignore` and `node_modules/` to prove the scanner
  follows only the narrow fixed policy; `.forgeflow/cache/` provides the
  explicit ignored-directory counterexample.
- Synthetic sensitive-looking fixture data tests payload boundaries without
  introducing secret detection or redaction policy.
- Tests inspect descriptive hints but never execute `make test`, `npm test`, or
  any repository command.

## 6. TDD and Tests

The acceptance test module was added before its Phase 7 fixture and expected
fragments. The initial RED run failed because those assets did not exist. GREEN
added the minimal immutable fixture, expected fragments, and assertions. The
follow-up test correction aligned the assertions with the fixed ignore policy
and the contract's bounded normalized issue-text field.

Test framework: Python `unittest` through the repository's `uv` environment.

| Verification | Result |
| --- | --- |
| RED: `uv run python -m unittest tests.repository_context.test_acceptance -v` | Expected missing-fixture and expected-fragment failures. |
| Targeted GREEN: `uv run --no-sync python -m unittest tests.repository_context.test_acceptance -v` | 8 tests passed. |
| Cumulative suite: `uv run --no-sync python -m unittest discover -s tests -v` | 57 tests passed. |
| Staged diff validation: `git diff --cached --check` | Passed. |

## 7. Important Fixes and Edge Cases

- Query casefolding is a matching view, while `query.normalized` preserves
  normalized casing; equivalence tests therefore vary whitespace only.
- `.forgeflow/cache/` is the explicit ignored path, not all `.forgeflow/`
  content.
- `issue_text.normalized` is intentionally bounded context; the test verifies
  the raw whitespace form is not persisted rather than asserting normalized
  content is absent.
- External symlinks, binary candidates, and invalid UTF-8 candidates do not
  expose inspected text or create text search results.

## 8. Commit

- Full implementation commit hash: `2744b25dbddcda955892a79b0011940455b113b7`
- Commit message: `test(acceptance): add repository context coverage`

## 9. Acceptance

The acceptance suite verifies deterministic public-service behavior, validation
envelopes, normalized inputs, workspace path containment, fixed ignore behavior,
text-only search results, evidence closure and hashing, root-only descriptive
test hints, bounded reads, payload avoidance, and fixture side-effect absence.
The complete implemented suite passed with 57 tests.

The test-only implementation aligns with the OpenSpec acceptance-fixture
requirements and does not alter any contract, architecture, or production code.

Status: **Accepted**.

## 10. Scope Boundary Confirmation

This phase did not add a scanner, matcher, ranking rule, evidence-generation
logic, result assembly, service behavior, workspace policy, or canonical ID
algorithm. It did not implement Phase 8 unreadable-file, line-limit, or
platform-specific hardening. It introduced no writes to fixture workspaces,
command execution, network, subprocess, Git/PR, memory, agent, workflow,
DeerFlow runtime, LLM, embedding, AST, or semantic-search behavior.

## 11. Follow-up

Next Phase: Hardening.

Known reconciliation item: Phase 8 remains responsible for the hardening scope
defined by the canonical implementation plan.
