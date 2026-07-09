# RFC-002: Contracts and State Model

## Status

Draft

## Purpose

Define ForgeFlow contract schemas and state boundaries required to support RFC-001 Agent Architecture.

## Scope

RFC-002 owns exact contract schemas, runtime / durable / memory state separation, contract versioning, evidence reference format, and retry lineage.

## Owns

- `RepositoryContextResult`
- `PatchProposal`
- `ValidationResult`
- `ReviewResult`
- `PRResult`
- evidence reference format
- contract versioning
- runtime state vs durable state vs memory state separation
- retry lineage and artifact lineage

## Does Not Own

- workflow role authority boundaries
- sandbox security policy
- approval policy
- DeerFlow extension mechanics
- product-level trace format
- evaluation metrics

## Relationship with RFC-001

RFC-001 defines role and control boundaries. RFC-002 must provide contract and state models that support those boundaries without promoting workflow roles into implementation units.

## Open Questions

- What is the minimal schema for each first-stage contract?
- How should evidence references be represented?
- How should artifact lineage be tracked across retries?
- Which fields are runtime-only, durable, or memory-eligible?
- How should contract versions be handled?
