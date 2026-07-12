# Phase 2: Canonical Identity

## 1. Goal

Provide deterministic canonical JSON serialization and pure SHA-256 identity helpers for Repository Context contracts.

## 2. Scope

### Included

- Canonical UTF-8 JSON bytes with stable object-key ordering and compact separators.
- SHA-256 digest helper.
- Stable `rcr_sha256:`, `ev_sha256:`, and `rce_sha256:` identifiers.
- Public exports and focused canonicalization tests.

### Excluded

- Workspace or path validation, scanner behavior, query normalization, matching, ranking, evidence-generation logic, result assembly, and service behavior.
- Agents, workflows, DeerFlow integration, LLMs, embeddings, AST processing, semantic search, network, subprocesses, Git/PR, and memory.

## 3. Changed Files

| File | Change | Purpose |
| --- | --- | --- |
| `src/forgeflow/repository_context/__init__.py` | Modified | Export canonical serialization and identity helpers. |
| `src/forgeflow/repository_context/canonical.py` | Added | Implement pure canonical JSON, SHA-256, and stable-ID helpers. |
| `tests/repository_context/test_canonical.py` | Added | Verify deterministic serialization, rejection behavior, and IDs. |

## 4. Implementation

`canonical_bytes()` serializes supported contract values as compact UTF-8 JSON with lexicographically sorted mapping keys. It preserves list and tuple order, represents tuples as arrays, recursively omits selected identity fields, and rejects floats, non-string mapping keys, and unsupported types with `TypeError`.

`sha256_hex()` hashes the canonical bytes. `contract_id_for()`, `evidence_id_for()`, and `error_id_for()` omit only their own identity fields before hashing and return the required prefixed lowercase SHA-256 values. The helpers neither mutate nor rebuild contract instances.

## 5. Design Decisions

- Identity is derived solely from canonical contract content, never timestamps, random values, machine paths, or runtime state.
- Canonicalization is intentionally pure and narrow; it does not validate input or perform any filesystem work.
- Optional `None` fields are omitted, while the contract-required `EvidenceRef.locator=None` remains an explicit JSON `null`.
- Each ID helper removes only the identity field it is responsible for, avoiding hidden cross-object normalization.

## 6. TDD and Tests

The RED run added `test_canonical.py` before `canonical.py`; it failed on the missing public `canonical_bytes` API while Phase 1 tests continued to pass. GREEN added the smallest pure canonicalization surface. A corrective TDD iteration narrowed `locator: null` preservation from all mappings to the specific `EvidenceRef` contract.

Test framework: Python `unittest`.

| Verification | Result |
| --- | --- |
| RED: `python3 -m unittest tests.repository_context.test_contracts tests.repository_context.test_canonical -v` | Expected import failure for missing `canonical_bytes`. |
| Targeted correction: `python3 -m unittest tests.repository_context.test_canonical -v` | RED exposed over-broad generic `locator: null` behavior; GREEN passed 12 tests. |
| Cumulative Phase 1-2 suite: `python3 -m unittest tests.repository_context.test_contracts tests.repository_context.test_canonical -v` | 20 tests passed. |

## 7. Important Fixes and Edge Cases

- Reordered mapping keys produce identical canonical bytes and hashes.
- Content changes alter the resulting identity.
- Floats and unsupported values fail explicitly instead of receiving runtime-dependent representations.
- Only `EvidenceRef.locator` preserves `None` as JSON `null`; generic optional mapping and dataclass fields continue to be omitted.

## 8. Commit

- Full commit hash: `9fa68b8db27f785829221c7b3a6994229fbe693f`
- Commit message: `feat(contract): add canonical repository context identities`

## 9. Acceptance

Tests verified byte-for-byte stable serialization, key-order independence, content-sensitive IDs, identity-field omission, required namespaces, and explicit rejection of unsupported values. The final review accepted the helper surface as deterministic and aligned with the Repository Context contract.

Status: **Accepted**.

## 10. Scope Boundary Confirmation

This phase did not add validation execution, workspace boundaries, scanners, matchers, ranking, evidence-generation behavior, result envelopes, or a Repository Context Service. It introduced no agent, workflow, DeerFlow, LLM, embedding, AST, semantic-search, network, subprocess, Git/PR, or memory system.

## 11. Follow-up

Next Phase: Workspace Security.

Reconciliation status: phase numbering was aligned with the canonical plan on
2026-07-12; no Phase 2 follow-up remains.
