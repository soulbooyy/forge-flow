"""Exact, registered M4 fixture policy constants."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class M4FixtureProfile:
    policy_profile_id: str
    policy_profile_version: str
    repository_id: str
    base_commit_sha: str
    oci_image_digest: str
    command_id: str
    executable: str
    args: tuple[str, ...]
    working_directory: str
    allowed_environment: tuple[str, ...]
    timeout_ms: int
    max_output_bytes: int
    max_wall_clock_ms: int
    max_sandbox_lifetime_ms: int
    max_workspace_write_bytes: int
    max_artifact_bytes: int
    max_diff_bytes: int
    max_changed_files: int
    max_tool_calls: int
    max_automatic_retries: int
    resource_limit_ids: tuple[str, ...]


M4_FIXTURE_V1 = M4FixtureProfile(
    policy_profile_id="forgeflow-m4-fixture-only",
    policy_profile_version="1.0.0",
    repository_id="1300511729",
    base_commit_sha="97c8220cd713ebf61124ac2de2f3eadc6e4dc222",
    oci_image_digest="sha256:81b691e3b5d43b2f4e717eaeef63437705addd115aee32917efd5d7387807f28",
    command_id="fixture-test-runner-v1",
    executable="python3",
    args=("-m", "unittest", "discover", "-s", "tests"),
    working_directory="workspace_root",
    allowed_environment=(),
    timeout_ms=120000,
    max_output_bytes=65536,
    max_wall_clock_ms=600000,
    max_sandbox_lifetime_ms=480000,
    max_workspace_write_bytes=10485760,
    max_artifact_bytes=2097152,
    max_diff_bytes=262144,
    max_changed_files=10,
    max_tool_calls=25,
    max_automatic_retries=0,
    resource_limit_ids=(
        "command_timeout_ms",
        "max_command_output_bytes",
        "max_sandbox_lifetime_ms",
        "max_wall_clock_ms",
        "max_workspace_write_bytes",
    ),
)
