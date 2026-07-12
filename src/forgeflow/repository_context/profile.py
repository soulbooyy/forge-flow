"""Versioned defaults for the Repository Context contract."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RepositoryContextProfile:
    configuration_profile_id: str
    normalization_id: str
    limit_profile_id: str
    ignore_policy_id: str
    max_query_chars: int
    max_issue_text_chars: int
    max_text_bytes_per_file: int
    max_lines_per_file: int
    max_text_locators_per_file: int
    max_relevant_files: int
    max_search_results: int
    max_evidence_refs: int
    max_test_command_hints: int


M1_DEFAULTS = RepositoryContextProfile(
    configuration_profile_id="repository-context/m1-defaults-v1",
    normalization_id="m1-nfc-trim-collapse-casefold-v1",
    limit_profile_id="m1-default-limits-v1",
    ignore_policy_id="m1-default-ignore-v1",
    max_query_chars=512,
    max_issue_text_chars=4096,
    max_text_bytes_per_file=1_048_576,
    max_lines_per_file=20_000,
    max_text_locators_per_file=20,
    max_relevant_files=50,
    max_search_results=200,
    max_evidence_refs=300,
    max_test_command_hints=10,
)
