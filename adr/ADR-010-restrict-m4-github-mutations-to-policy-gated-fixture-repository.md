# ADR-010: Restrict M4 GitHub Mutations to a Policy-Gated Fixture Repository

## Status

Accepted

## Context

M4 is ForgeFlow's first Draft PR path and therefore its first GitHub external
side effect. Arbitrary, production, organization, or unregistered repositories
would introduce unresolved authorization, data-egress, audit, and credential
governance.

## Decision

M4 permits only one pre-registered fixture/test repository through a
deny-by-default versioned policy profile. The ForgeFlow-owned GitHub adapter is
the only component that may call GitHub APIs. Sandboxes and Command Intents do
not receive network or GitHub credentials.

The adapter may read only the pre-registered fixture Issue bound to that
repository and its expected base revision. It must normalize the result into an
immutable redacted `TaskInput`; raw Issue and GitHub response payloads cannot
enter the ForgeFlow artifact store or DurableRunSummary. Users and agents may
not select arbitrary repositories, Issues, or organization resources.

Repository owner/name/ID, Issue number/ID, fixed base commit SHA, credential
mode, and reset/audit procedure are required fixture-environment registration
inputs. They are not M4 architecture defaults or values the adapter may invent.
Until a controlled profile registers them, no GitHub mutation configuration or
implementation is authorized.

The adapter may create only a controlled branch, commit, and Draft PR after a
fresh allowed Policy Decision Record binds repository identity, base revision,
branch/commit identity, PatchArtifact identity, and idempotency key. It uses a
runtime-injected opaque credential, preferring a repository-scoped GitHub App
installation token; a fixture-only fine-grained test token is the limited
fallback. Merge, default-branch writes, protection-rule changes, and all other
production GitHub mutations are excluded.

The adapter renders the Draft PR body deterministically from scanned, redacted
ForgeFlow contracts. Its limited publication whitelist and its pre-publication
secret-scan/redaction gate are defined by RFC-004 and RFC-005. It must block,
rather than publish, any raw external payload, unredacted finding, scan failure,
or indeterminate safety result.

## Consequences

- M4 validates an auditable external-effect path without granting general
  repository automation authority.
- Credential material cannot enter contracts, artifacts, summaries, logs, or
  PR bodies.
- M4 validates a real but narrowly bounded Issue-to-Draft-PR path without
  creating a general GitHub data-ingestion capability.
- Enterprise repository onboarding requires a separate OpenSpec/ADR with its
  own Issue-input onboarding, permission, approval, retention, and audit model.

## Related RFCs

- [RFC-003](../rfcs/RFC-003-tool-and-mcp-integration.md)
- [RFC-004](../rfcs/RFC-004-sandbox-and-security-governance.md)
- [RFC-005](../rfcs/RFC-005-observability-and-trace-model.md)
