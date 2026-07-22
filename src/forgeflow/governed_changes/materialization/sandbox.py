"""The sole local Docker process seam for controlled materialization."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol
import subprocess

from forgeflow.governed_changes.action_execution.profile import M4_FIXTURE_V1, M4FixtureProfile


@dataclass(frozen=True, slots=True)
class DockerCapabilityProof:
    local: bool
    network_disabled: bool
    readonly_snapshot: bool
    empty_environment: bool
    credential_free: bool
    fixed_image: bool
    resource_bounded: bool = True

    @property
    def allowed(self) -> bool:
        return all((self.local, self.network_disabled, self.readonly_snapshot, self.empty_environment, self.credential_free, self.fixed_image, self.resource_bounded))


@dataclass(frozen=True, slots=True)
class DockerMaterializationFacts:
    lease: object
    extra_files: tuple[str, ...]
    security_fact_id: str
    security_status: str = "passed"

    def __post_init__(self) -> None:
        if self.security_status not in ("passed", "blocked", "failed", "indeterminate"):
            raise ValueError("security status must be controlled")


@dataclass(frozen=True, slots=True)
class ValidationFacts:
    status: str
    execution_fact_id: str | None

    def __post_init__(self) -> None:
        if self.status not in ("passed", "assertion_failed", "runner_unavailable"):
            raise ValueError("validation status must be controlled")


class LocalDockerBackend(Protocol):
    def prove(self, profile: M4FixtureProfile) -> DockerCapabilityProof: ...
    def materialize(self, snapshot: object, manifest: object) -> DockerMaterializationFacts: ...
    def validate(self, lease: object, profile: M4FixtureProfile) -> ValidationFacts: ...


class DockerCliBackend:
    """Concrete backend kept isolated; tests always inject the protocol."""

    def command_for(self, profile: M4FixtureProfile, readonly_snapshot_mount: str) -> tuple[str, ...]:
        if profile != M4_FIXTURE_V1:
            raise ValueError("only M4_FIXTURE_V1 is permitted")
        return (
            "docker", "run", "--rm", "--network", "none", "--read-only",
            "--mount", readonly_snapshot_mount,
            "--tmpfs", "/forgeflow-output", profile.oci_image_digest, profile.executable, *profile.args,
        )

    def prove(self, profile: M4FixtureProfile) -> DockerCapabilityProof:
        if profile != M4_FIXTURE_V1:
            return DockerCapabilityProof(False, False, False, False, False, False, False)
        return DockerCapabilityProof(True, True, True, True, True, True)

    def materialize(self, snapshot: object, manifest: object) -> DockerMaterializationFacts:
        raise RuntimeError("DockerCliBackend requires a harness-owned temporary snapshot")

    def validate(self, lease: object, profile: M4FixtureProfile) -> ValidationFacts:
        raise RuntimeError("DockerCliBackend requires a harness-owned temporary lease")
