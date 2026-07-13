# M2 PatchProposal Policy Profile v1

## Identity

- `policy_profile_id`: `patch-proposal/m2-conservative-v1`
- `policy_version`: `1`
- `evaluator_id`: `m2/deterministic-boundary-evaluator-v1`

Every successful `PatchProposal` must record these values and reference the
Policy Decision Record that evaluated its exact ordered candidate path set. A
proposal must be re-evaluated if its candidate paths, policy profile ID/version,
or declared intent changes.

## Bounded Proposal Intent

- At most 3 root-cause hypotheses.
- At most 3 candidate changes.
- Each hypothesis rationale: at most 500 Unicode code points.
- Fix strategy: at most 1,000 Unicode code points.
- Each candidate-change rationale: at most 500 Unicode code points.
- Candidate-change kinds are exactly `modify_existing_file`,
  `add_test_file`, `add_non_sensitive_file`, or `remove_file`.
- A candidate path must be canonical workspace-relative and must cite one or
  more evidence IDs from the referenced M1 context.

These bounds constrain declarative contract payload only. They do not authorize
an edit, a diff, a command, or a side effect.

## Decision Rules

The evaluator returns exactly one result for the proposal:

- `blocked` when any candidate path matches a credential or secret-like path;
- `requires_human_approval` when no blocked rule matches and any candidate is a
  `remove_file` or matches a high-risk path;
- `allowed` only when all bounds pass and no blocked or high-risk rule matches.

Bounds failure, an unsupported path spelling, missing M1 evidence, or a missing
profile identity is a patch-proposal validation error, not an `allowed` result.

For a successful proposal, risk flags are mechanically derived and sorted:

- `allowed` produces no risk flags;
- every `requires_human_approval` decision includes
  `policy_requires_human_approval`;
- an environment-file match adds `environment_path`;
- any other approval-required path match adds `high_risk_path`;
- a `remove_file` candidate adds `deletion_intent`.

A blocked decision returns the `policy_blocked` validation envelope and cannot
produce a successful proposal or risk-flag array.

### Blocked paths

The following canonical paths are treated as suspected credential or secret
locations and are `blocked` by path policy alone:

- paths under `secrets/`, `secret/`, `credentials/`, or `credential/`;
- files ending in `.pem`, `.key`, `.p12`, `.pfx`, or `.jks`;
- files named `id_rsa`, `id_dsa`, `id_ecdsa`, or `id_ed25519`.

This is a path-only guardrail, not secret scanning. A future diff or artifact
still requires independent secret scanning under RFC-004.

### Requires-human-approval paths

The following categories require approval when no blocked rule applies:

- environment configuration: any `.env` or `.env.*` file;
- CI/CD: `.github/workflows/`, `.gitlab-ci.yml`, `Jenkinsfile`, `.circleci/`,
  `azure-pipelines.yml`, or `azure-pipelines.yaml`;
- deployment or infrastructure: `deploy/`, `deployment/`, `infra/`,
  `infrastructure/`, `k8s/`, `helm/`, `terraform/`, or files ending in `.tf`;
- authentication, authorization, permission, access-control, cryptography, or
  crypto paths, matched case-insensitively only when a normalized path segment
  equals one of `auth`, `authentication`, `authorization`, `permission`,
  `permissions`, `access-control`, `access_control`, `crypto`, or
  `cryptography`;
- database migrations: `migrations/`, `migration/`, `db/migrate/`, or
  `database/migrations/`;
- dependency lockfiles: `package-lock.json`, `npm-shrinkwrap.json`,
  `yarn.lock`, `pnpm-lock.yaml`, `poetry.lock`, `Pipfile.lock`, `Cargo.lock`,
  `go.sum`, `Gemfile.lock`, or `composer.lock`.

Deletion is approval-required regardless of path category unless a blocked rule
matches first. This makes `remove_file` evaluable without a circular
"non-sensitive" classification.

## Extensibility

Future profiles may add rules, lower limits, or define separately reviewed
exceptions only through a new `policy_profile_id` or `policy_version`. No
implementation may silently change this profile's limits, matching rules, or
decision semantics.
