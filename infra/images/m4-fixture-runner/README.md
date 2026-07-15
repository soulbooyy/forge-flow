# M4 Fixture Runner OCI Image

## Scope

This directory defines the ForgeFlow-owned, fixture-only OCI runner intended
for the registered `soulbooyy/forgeflow-m4-fixture` repository. Its sole
supported M4 command capability is:

```text
python3 -m unittest discover -s tests
```

It is not a general shell, a production runtime, or an adapter implementation.
The OCI adapter must pass the structured command explicitly; the image defines
no shell entrypoint and no default command.

## Build Definition

- Base image: `python:3.12.11-alpine3.22@sha256:efcdfa6a6b2fd2afb9c7dfa9a5b288a6f68338b5cfdebe6b637d986067d85757`.
- Python: Python 3.12 from that base image.
- Runtime user: `fixture` (non-root), home and working directory `/workspace`.
- Build context: intentionally empty apart from this definition and review
  metadata; it does not copy ForgeFlow source or fixture-repository source.
- Dependencies: no third-party Python packages and no package-manager command
  are added by this image.

The base image is fixed by an explicit version and manifest digest, but is not
itself the registered identity. The final ForgeFlow image must be pushed and
registered by its immutable registry manifest digest.

## Security Review Record

Review status: **M4 fixture-only owner approved after registry publication verification**

Review owner: ForgeFlow fixture environment owner (M4 fixture-only owner
approval; no independent security-team approval is claimed).

The pending review confirms the intended boundary:

- no credentials, tokens, SSH keys, or registry secrets are added;
- no dynamic dependency installation is permitted;
- no ForgeFlow artifact store may be mounted;
- `/workspace` is the intended sole writable runtime mount;
- the adapter, not this image, must enforce `--network none` (or an equivalent
  OCI runtime network isolation option), workspace mount mode, resource limits,
  credential exclusion, and workspace cleanup;
- no `curl`, `wget`, `git`, `ssh`, compiler, or extra package is added by this
  definition.

The Alpine/Python base may inherently contain BusyBox shell and package-manager
components. They are not invoked by this definition and must be explicitly
reviewed at controlled build registration; their presence does not authorize
shell-based `CommandIntent` execution.

### Local Verification Evidence (2026-07-14)

The fixture-only owner performed the following local checks with Docker Desktop
on Linux/aarch64:

- `docker build --no-cache --tag forgeflow-m4-fixture-runner:v1 infra/images/m4-fixture-runner` completed successfully.
- `docker run ... python3 --version` returned `Python 3.12.11`.
- `docker run ... id -u` returned `100`, confirming the configured non-root
  user.
- The registered fixture test command completed successfully against a
  temporary, patched fixture workspace mounted read-only, with `--network none`,
  `--read-only`, and a temporary `/tmp` tmpfs.
- The observed unittest output was only a small test report, far below the
  externally enforced 65536-byte policy limit.

The local image identifier is deliberately not recorded as a registration
digest. After the initial denied push, the fixture-only owner completed an
authorized GHCR publish. On 2026-07-15, GHCR resolved
`ghcr.io/soulbooyy/forgeflow-m4-fixture-runner:v1` to OCI image-index digest
`sha256:81b691e3b5d43b2f4e717eaeef63437705addd115aee32917efd5d7387807f28`.
That registry digest, rather than a local image ID, is recorded in the
authoritative M4 Sandbox Image Registration.

## Required Controlled-Build Verification

The following commands are required after a Docker or Podman daemon is
available. They are not yet claimed as executed by this record.

```text
docker build --tag forgeflow-m4-fixture-runner:v1 infra/images/m4-fixture-runner
docker run --rm forgeflow-m4-fixture-runner:v1 python3 --version
docker run --rm forgeflow-m4-fixture-runner:v1 id -u
docker run --rm --network none --read-only \
  --mount type=bind,src=<temporary-fixture-workspace>,dst=/workspace,readonly \
  --tmpfs /tmp:rw,noexec,nosuid,size=16m \
  forgeflow-m4-fixture-runner:v1 python3 -m unittest discover -s tests
```

Before registration, the controlled environment must additionally verify that
the test output is at most 65536 bytes, no network or dynamic installation is
needed, the container retains no workspace state after exit, and no artifact
store is mounted. The image must then be pushed to an authorized controlled
registry under an explicit version tag (for example `v1`), and its registry
manifest digest—not its local image ID—must be registered.

## Known Limits

This definition alone cannot prove runtime network isolation, CPU or memory
limits, mount restrictions, or registry identity. Those are adapter/runtime or
controlled-registry checks and remain fail-closed prerequisites for M4.
