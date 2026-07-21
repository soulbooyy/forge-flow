# Milestone <MILESTONE_NUMBER>: <MILESTONE_NAME> Canonical Implementation Plan

## Authority and Status

This is the sole execution authority for this milestone. It reconciles the
[AI-assisted draft](<AI_ASSISTED_DRAFT_LINK>) against <AUTHORITATIVE_INPUTS>.
Chat prompts do not redefine phase scope, files, interfaces, or acceptance.
It follows [Agent Execution Authority and Stop Rules](../../process/agent-execution-authority.md), subject to narrower feature-specific limits.

## Goal

<MILESTONE_GOAL>

## Reconciliation of AI Draft

- <PHASE_BOUNDARY_RECONCILIATION>
- <DEPENDENCY_AND_SCOPE_RECONCILIATION>
- <TDD_AND_ACCEPTANCE_RECONCILIATION>

## Global Constraints

- <CONSTRAINT>

## Phase <PHASE_NUMBER>: <PHASE_NAME>

**Depends on:** <DEPENDENCIES>

**Files:**

- Create/Modify: `<PATH>` — <PURPOSE>

**Interfaces:** <PUBLIC_OR_INTERNAL_INTERFACE_BOUNDARY>

- [ ] Write the targeted failing test and record the RED command/result.
- [ ] Implement the smallest scoped behavior and run targeted GREEN tests.
- [ ] Refactor only within phase scope; run the cumulative implemented suite.
- [ ] Run `git diff --check` and inspect `git status --short`.
- [ ] Create one focused commit, the Completion Record, and progress update.

**Acceptance:** <PHASE_ACCEPTANCE_CRITERIA>
