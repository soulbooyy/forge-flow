# RFC-007: DeerFlow Extension Strategy

## Status

Draft

## Purpose

Define how ForgeFlow extends DeerFlow without becoming a shallow fork or duplicating generic runtime primitives.

## Scope

RFC-007 owns DeerFlow extension points, graph integration, thread state extension, tool registry integration, checkpoint mapping, middleware hooks, and trace hook mapping.

## Owns

- DeerFlow graph integration strategy
- ForgeFlow workflow graph integration
- thread state extension strategy
- tool registry integration
- checkpoint mapping
- middleware hook usage
- trace hook mapping
- boundaries between DeerFlow runtime primitives and ForgeFlow product semantics

## Does Not Own

- workflow role authority boundaries
- exact contract schemas
- sandbox security policy
- approval policy
- evaluation metrics

## Relationship with RFC-001

RFC-001 defines that DeerFlow runs the graph while ForgeFlow defines the software-engineering workflow. RFC-007 must validate that DeerFlow extension points can support this boundary.

## Open Questions

- Which DeerFlow extension points should ForgeFlow use first?
- How should ForgeFlow state extend DeerFlow thread/run state?
- How should tool policy integrate with DeerFlow tool invocation?
- How should checkpoints map to ForgeFlow artifacts and contracts?
- How should DeerFlow trace hooks map to product-level run summaries?
- What must remain upstream-compatible?
