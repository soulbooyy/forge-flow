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

## Registration

```yaml
sandbox_image_registration:
  image_reference:
  image_digest:
  registry:
  approval_owner:
  security_review_reference:
  registered_at:
  registration_version:
```

`image_digest` must be the immutable manifest digest of the reviewed image
that the OCI adapter will use. `latest`, floating tags, and local unregistered
images are forbidden. This document records image-identity governance only; it
does not contain credentials, registry secrets, or runtime output.

## Registration Status

```yaml
status: Pending # Pending | Registered | Approved
readiness_blocker: Required OCI image registration has not been supplied by the controlled image environment.
```

`Registered` means the controlled image environment supplied every required
value and ForgeFlow reconciled it. `Approved` records the explicit approval of
that completed external registration for the applicable M4 feature gate.

## References

- [M4 Fixture Environment Registration](m4-fixture-environment-registration.md)
- [M4 execution architecture readiness](../product/roadmap/milestones.md)
- [RFC-004: Sandbox and Security Governance](../../rfcs/RFC-004-sandbox-and-security-governance.md)
- [RFC-006: Evaluation Framework](../../rfcs/RFC-006-evaluation-framework.md)
