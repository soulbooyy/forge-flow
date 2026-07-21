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

## Recoverable Execution Failures

Treat the following as self-recoverable execution work, not a user decision:

- malformed tool-call or patch syntax;
- transient sandbox/cache/lock failures;
- an incomplete command invocation;
- a failed test, import, formatting check, or local verification command; and
- a reviewer finding that remains within accepted scope.

For a recoverable failure, the agent must:

1. inspect the error;
2. correct the command, patch, or scoped implementation;
3. rerun the relevant verification; and
4. continue the review/fix loop.

Do not end a turn or request confirmation solely because a recoverable failure
occurred.

## In-Progress Work Is Not a Stop Condition

- “In review”, “review findings received”, “in a repair loop”, “tests running”,
  “retest pending”, and “documentation pending” are commentary states only.
- While a user-authorized phase remains incomplete, the agent must continue to
  the next safe execution step automatically.
- The agent may end a turn during in-progress work only for a Mandatory User
  Decision defined by this policy, a user interruption, or an unavoidable
  external-state wait that has exhausted safe in-scope work.
- A final response must not merely report an incomplete repair loop when a
  safe implementation, test, review, documentation, or commit step remains.
- A statement that the agent is "continuing into" a named test, review, fix,
  or commit step creates an immediate obligation to execute that step in the
  same ongoing task; it must not be followed by an empty final status message.
- Do not send a final response while an authorized review, fix, test, commit,
  or phase-completion chain remains unfinished. “Review initiated”, “review
  pending”, and “tests passed before review” are explicitly non-terminal.

## Feature Exceptions

- Canonical plans reference this policy.
- Canonical plans may impose narrower limits.
- Neither this policy nor a plan authorizes an external side effect absent explicit authority.
