# RFC-004: Sandbox and Security Governance

## Status

Draft

## Purpose

Define ForgeFlow sandbox, security, policy, approval, and side-effect governance required to support RFC-001 Agent Architecture.

## Scope

RFC-004 owns sandbox command, path, network, and resource policy; sensitive file policy; diff thresholds; secret scanning; cost and retry caps; and approval policy.

## Owns

- sandbox command policy
- sandbox path policy
- network access policy
- resource limits
- sensitive file policy
- diff size and changed-file thresholds
- secret scanning policy
- cost caps
- retry caps
- approval policy
- side-effect authorization policy

## Does Not Own

- workflow role definitions
- exact contract schemas
- DeerFlow extension mechanics
- product-level trace shape
- evaluation metrics

## Relationship with RFC-001

RFC-001 defines which roles may not own policy, approval, retries, or side effects. RFC-004 must define the policy mechanisms that enforce those boundaries.

## Open Questions

- Which actions require Human Approval?
- What files are sensitive by default?
- What commands are allowed, denied, or approval-gated?
- What diff thresholds trigger approval?
- How should retry budgets be enforced?
- How should side effects be authorized and audited?
