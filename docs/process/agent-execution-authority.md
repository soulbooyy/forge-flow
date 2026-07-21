# Agent Execution Authority and Stop Rules

## Purpose

This policy defines when an implementation agent continues autonomously and when it must request a user decision. It creates no product, credential, or external-side-effect authority.

## Default: Continue Accepted Work

Within user-authorized feature/phase scope, continue RED/GREEN tests, scoped fixes, independent review, review corrections, re-tests, records, focused commits, and authorized phase transitions. Review dispatch, waiting, and re-review are execution steps, never handoff points.

## Mandatory User Decision

Stop only when an accepted authority cannot safely determine an action that: expands an external side effect (GitHub mutation, network, credential use, deployment, destructive external overwrite); changes a contract, authority, security boundary, or durable-data meaning; lacks required authoritative input; conflicts materially with accepted authority; or expands scope/implements a non-goal.

State the decision, why it cannot be inferred, safe waiting state, options, and recommendation.

## Not Pause Conditions

Do not pause for ordinary test failures/fixes, review lifecycle, canonical-plan implementation choices, progress/completion records, focused commits, or authorized rebase/merge work.

## Feature Exceptions

Canonical plans reference this policy and may impose narrower limits. Neither this policy nor a plan authorizes an external side effect absent explicit authority.
