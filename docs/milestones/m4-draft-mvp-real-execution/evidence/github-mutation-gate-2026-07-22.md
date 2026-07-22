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
| Credential eligibility | rejected |

## Gate result

The locally configured GitHub CLI authentication is a general OAuth credential
with broad repository authority. The fixture registration permits only a
fixture-scoped fine-grained token or GitHub App installation. The credential
does not satisfy that constraint, so the mutation gate is **not accepted**.

No token value, raw GitHub payload, request body, source content, or command
output is retained in this record. The required recovery is to configure an
approved fixture-only credential, then repeat this read-only preflight before
any mutation attempt.
