# GitHub CLI Provider Closure — 2026-07-22

## Scope

This batch supplies the sole concrete provider for the registered fixture
mutation. It was tested exclusively through an injected fake runner; it did
not invoke GitHub, a credential, or a mutation.

## Boundary

The provider owns fixed `gh api` Git-data requests and one fixed `gh pr create`
request. It accepts no shell expression, caller repository, URL, branch suffix,
target path, commit message, PR title/body, or credential. Request bodies use
JSON stdin, including base64-encoded transient content for the Git blob.

Reconciliation treats only a verified HTTP 404 as branch absence. Any other
provider failure propagates to the orchestration adapter as a fail-closed
result. Branch, blob, tree, commit, and ref identities must all satisfy their
registered syntax before a later provider write can use them.

## Verification and review

The provider tests cover fixed base reads, Git-data commit request shape,
base64 content transport, foreign request rejection before CLI invocation,
not-found versus unavailable reconciliation, and malformed identity stop
behavior. Static checks confirm no shell, HTTP client, token literal, or
environment-token path exists. Independent review initially found and the
batch fixed three P1 issues: over-broad absent-branch handling, loose branch
binding, and unvalidated Git identities. Final review passed.
