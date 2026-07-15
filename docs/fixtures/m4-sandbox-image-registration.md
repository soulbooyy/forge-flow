# M4 Sandbox Image Registration

## Purpose

This is the sole authoritative registration record for the OCI sandbox image
used by the first M4 controlled-execution feature. It records external,
security-reviewed execution-environment identity; it is distinct from the
repository and Issue inputs registered in
[M4 Fixture Environment Registration](m4-fixture-environment-registration.md).

The registration is an external M4 execution-readiness gate. Until it is
registered and approved, no executable `CommandIntent` exists, the sandbox
capability gate is not passed, and the first M4 execution-feature OpenSpec
remains blocked. Values must be provided by the controlled OCI image
environment. They must not be generated, inferred, or substituted by an image
tag.

## Image Registration

```yaml
sandbox_image_registration:
  image_reference: ghcr.io/soulbooyy/forgeflow-m4-fixture-runner@sha256:81b691e3b5d43b2f4e717eaeef63437705addd115aee32917efd5d7387807f28
  image_digest: sha256:81b691e3b5d43b2f4e717eaeef63437705addd115aee32917efd5d7387807f28
  registry: ghcr.io
  image_version: v1
  base_image_reference: python:3.12.11-alpine3.22@sha256:efcdfa6a6b2fd2afb9c7dfa9a5b288a6f68338b5cfdebe6b637d986067d85757
  runtime_user: fixture (UID 100)
  supported_command_id: fixture-test-runner-v1
  network_policy: runtime-enforced-none
  dynamic_dependency_installation: prohibited
```

`image_reference` must include the immutable registry manifest digest, not only
an image tag. `image_digest` must be the same immutable manifest digest. The
image is ForgeFlow-owned and must not be a public image selected as the final
registered environment.

## Security Registration

```yaml
sandbox_image_security_registration:
  approval_owner: soulbooyy (M4 fixture-only owner)
  security_review_reference: ../../infra/images/m4-fixture-runner/README.md#security-review-record
  registered_at: 2026-07-15T07:00:01Z
  registration_version: m4-sandbox-image-registration-v1
```

`image_digest` must be the immutable manifest digest of the reviewed image
that the OCI adapter will use. `latest`, floating tags, and local unregistered
images are forbidden. This document records image-identity governance only; it
does not contain credentials, registry secrets, or runtime output.

## Runtime Constraints

The registered image must have a fixed runtime version, require no network or
dynamic dependency installation for the registered fixture command, and
contain no unapproved tools. It must be compatible with the versioned M4
fixture policy profile.

Network isolation, credential exclusion, workspace-only writes, resource
limits, and artifact-store exclusion are runtime/OCI-adapter enforcement
responsibilities. The image registration must not claim that the image alone
enforces them.

## Usage Boundary

This image is only for the registered fixture repository, M4 governed
execution, and an approved `CommandIntent`. It must not be used for arbitrary
repositories, production work, user-selected images, or runtime image
replacement.

## Registration Status

```yaml
status: Approved # Pending | Registered | Approved
readiness_blocker: None. The OCI image identity and owner-approval gate is satisfied; each later M4 feature retains its own OpenSpec and readiness requirements.
```

`Registered` means the controlled image environment supplied every required
value and ForgeFlow reconciled it. `Approved` records the explicit approval of
that completed external registration for the applicable M4 feature gate.

While `Pending`, the governed-execution OpenSpec, sandbox implementation, and
`CommandIntent` execution remain blocked.

## References

- [M4 Fixture Environment Registration](m4-fixture-environment-registration.md)
- [M4 execution architecture readiness](../product/roadmap/milestones.md)
- [RFC-004: Sandbox and Security Governance](../../rfcs/RFC-004-sandbox-and-security-governance.md)
- [RFC-006: Evaluation Framework](../../rfcs/RFC-006-evaluation-framework.md)
