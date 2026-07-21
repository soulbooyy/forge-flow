# Agent Execution Authority and Stop Rules

## Purpose

- Define when an implementation agent continues autonomously.
- Define when it must request a user decision.
- Do not create product, credential, or external-side-effect authority.

## Default: Continue Accepted Work

Within user-authorized feature/phase scope, continue:

- RED/GREEN tests;
- scoped fixes;
- independent review and review corrections;
- re-tests;
- progress and completion records;
- focused commits; and
- authorized phase transitions.

Treat review dispatch, waiting, and re-review as execution steps, never as handoff points.

## Mandatory User Decision

Stop only when accepted authority cannot safely determine an action that:

- expands an external side effect, including GitHub mutation, network access,
  credential use, deployment, or destructive external overwrite;
- changes a contract, authority, security boundary, or durable-data meaning;
- lacks a required authoritative input;
- conflicts materially with accepted authority; or
- expands scope or implements an explicit non-goal.

When stopping, state:

- the decision;
- why it cannot be inferred;
- the safe waiting state;
- available options; and
- a recommendation.

## Not Pause Conditions

Do not pause for:

- ordinary test failures and fixes;
- any review lifecycle step;
- canonical-plan implementation choices;
- progress/completion records;
- focused commits; or
- authorized rebase/merge work.

## Feature Exceptions

- Canonical plans reference this policy.
- Canonical plans may impose narrower limits.
- Neither this policy nor a plan authorizes an external side effect absent explicit authority.
