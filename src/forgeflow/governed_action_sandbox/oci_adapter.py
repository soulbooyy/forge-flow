"""Injected, fail-closed OCI capability seam; no concrete runtime backend."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Protocol

from .models import CommandIntent, ResourceObservations


@dataclass(frozen=True, slots=True)
class OciCapabilityProof:
    image_digest_proven: bool
    network_disabled: bool
    credentials_absent: bool
    dynamic_installation_disabled: bool
    fixed_revision_workspace: bool
    workspace_writes_confined: bool
    artifact_store_unmounted: bool

    def __post_init__(self) -> None:
        if any(type(value) is not bool for value in (
            self.image_digest_proven, self.network_disabled, self.credentials_absent,
            self.dynamic_installation_disabled, self.fixed_revision_workspace,
            self.workspace_writes_confined, self.artifact_store_unmounted,
        )):
            raise ValueError("OCI capability proofs must be literal booleans")

    @property
    def proven(self) -> bool:
        return all((self.image_digest_proven, self.network_disabled, self.credentials_absent,
                    self.dynamic_installation_disabled, self.fixed_revision_workspace,
                    self.workspace_writes_confined, self.artifact_store_unmounted))


@dataclass(frozen=True, slots=True)
class OciRunFacts:
    image_digest_proven: bool
    network_disabled: bool
    credentials_absent: bool
    dynamic_installation_disabled: bool
    fixed_revision_workspace: bool
    workspace_writes_confined: bool
    artifact_store_unmounted: bool
    workspace_destroyed: bool
    started: bool
    status: Literal["succeeded", "failed", "cancelled", "timed_out", "not_started"]
    failure_reason: str | None
    exit_code: int | None
    started_at: str | None
    finished_at: str | None
    resource_observations: ResourceObservations

    def __post_init__(self) -> None:
        if any(type(value) is not bool for value in (
            self.image_digest_proven, self.network_disabled, self.credentials_absent,
            self.dynamic_installation_disabled, self.fixed_revision_workspace,
            self.workspace_writes_confined, self.artifact_store_unmounted,
            self.workspace_destroyed, self.started,
        )):
            raise ValueError("OCI run facts booleans must be literal booleans")

    @property
    def security_facts_valid(self) -> bool:
        return all((self.image_digest_proven, self.network_disabled, self.credentials_absent,
                    self.dynamic_installation_disabled, self.fixed_revision_workspace,
                    self.workspace_writes_confined, self.artifact_store_unmounted,
                    self.workspace_destroyed))

class OciBackend(Protocol):
    def prove(self, command: CommandIntent) -> OciCapabilityProof: ...
    def run(self, command: CommandIntent) -> OciRunFacts: ...
