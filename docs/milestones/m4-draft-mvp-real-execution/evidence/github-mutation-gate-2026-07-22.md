# Fixture GitHub Mutation Gate — 2026-07-22

## Scope

This is a read-only credential-governance preflight for the single registered
fixture Draft-PR scenario. It did not create a branch, commit, Draft PR, or
other GitHub mutation.

## Verified registration facts

| Field | Result |
| --- | --- |
| Repository | `soulbooyy/forgeflow-m4-fixture` — private, default branch `main` |
| Issue | #1 — open, registered fixture issue |
| Base revision | remains the registered immutable SHA |
| Credential eligibility | accepted after replacement |

## Gate result

The original general OAuth credential was replaced with a fine-grained token.
Read-only checks confirm the registered fixture repository, its numeric ID,
its `main` default branch, and the registered open Issue #1. The fixture owner
attests that the token is restricted to this repository with the registered
minimal permissions. GitHub intentionally does not expose the complete
fine-grained grant to the client, so this record retains no token value or
unredacted credential metadata. The mutation gate is **accepted**.

No token value, raw GitHub payload, request body, source content, or command
output is retained in this record. The next step is implementation and review
of the fixture-only adapter before the single authorized mutation scenario.
