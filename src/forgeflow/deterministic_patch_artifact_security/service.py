"""Pure assembly of Feature 2 metadata security facts from an M2 proposal."""

from __future__ import annotations

from dataclasses import replace
from typing import TypeAlias

from forgeflow.patch_proposal.canonical import (
    candidate_digest_for,
    policy_decision_id_for,
    proposal_id_for,
)
from forgeflow.patch_proposal.models import PatchProposal
from forgeflow.patch_proposal.profile import M2_CONSERVATIVE_V1

from .canonical import (
    artifact_id_for,
    intent_id_for,
    sha256_hex,
    validation_error_id_for,
)
from .models import (
    DeterministicPatchArtifactSecurityValidationError,
    PatchArtifact,
    PatchIntent,
    RedactedArtifactReferenceCandidate,
    RedactionFact,
    SecretScanResult,
)
from .policy import candidate_for, redact_metadata, scan_metadata
from .profile import M4_PATCH_METADATA_SECURITY_V1


PatchSecurityFacts: TypeAlias = tuple[
    PatchIntent,
    PatchArtifact,
    SecretScanResult,
    RedactionFact,
    RedactedArtifactReferenceCandidate | None,
]
PatchSecurityEnvelope: TypeAlias = (
    PatchSecurityFacts | DeterministicPatchArtifactSecurityValidationError
)

_REGISTERED_REPOSITORY_IDENTITY = "fixture-repository-1300511729"
_REGISTERED_BASE_REVISION = "97c8220cd713ebf61124ac2de2f3eadc6e4dc222"


def build_patch_security_facts(
    proposal: object, repository_identity: object, base_revision: object
) -> PatchSecurityEnvelope:
    """Build metadata-only security facts without I/O, policy evaluation, or authority."""
    if not _valid_inputs(proposal, repository_identity, base_revision):
        return _validation_error("invalid_patch_security_input")
    assert isinstance(proposal, PatchProposal)
    assert isinstance(repository_identity, str)
    assert isinstance(base_revision, str)

    try:
        intent = _patch_intent(proposal, repository_identity, base_revision)
        artifact = _patch_artifact(intent, proposal)
    except (TypeError, ValueError, UnicodeError):
        return _validation_error("metadata_construction_invalid")

    scan = scan_metadata(intent, artifact, M4_PATCH_METADATA_SECURITY_V1)
    redaction = redact_metadata(intent, artifact, scan, M4_PATCH_METADATA_SECURITY_V1)
    candidate = candidate_for(
        intent, artifact, scan, redaction, M4_PATCH_METADATA_SECURITY_V1
    )
    return (intent, artifact, scan, redaction, candidate)


def _valid_inputs(
    proposal: object, repository_identity: object, base_revision: object
) -> bool:
    return (
        isinstance(proposal, PatchProposal)
        and proposal.contract_id == proposal_id_for(proposal)
        and proposal.policy_decision.decision_id
        == policy_decision_id_for(proposal.policy_decision)
        and proposal.policy_decision.evaluated_candidate_digest
        == candidate_digest_for(proposal.candidate_changes)
        and proposal.proposal_source_id == M2_CONSERVATIVE_V1.proposal_source_id
        and proposal.schema_version == "patch-proposal/v1"
        and proposal.result_type == "patch_proposal"
        and proposal.policy_decision.policy_profile_id
        == M2_CONSERVATIVE_V1.policy_profile_id
        and proposal.policy_decision.policy_version == M2_CONSERVATIVE_V1.policy_version
        and proposal.policy_decision.evaluator_id == M2_CONSERVATIVE_V1.evaluator_id
        and proposal.policy_decision.revalidation_required is True
        and proposal.limitation_codes
        == tuple(sorted(M2_CONSERVATIVE_V1.allowed_limitation_codes))
        and repository_identity == _REGISTERED_REPOSITORY_IDENTITY
        and base_revision == _REGISTERED_BASE_REVISION
    )


def _patch_intent(
    proposal: PatchProposal, repository_identity: str, base_revision: str
) -> PatchIntent:
    lineage_digest = "sha256:" + sha256_hex(
        {
            "proposal_id": proposal.contract_id,
            "repository_context_contract_id": proposal.repository_context_contract_id,
            "policy_decision_id": proposal.policy_decision.decision_id,
            "repository_identity": repository_identity,
            "base_revision": base_revision,
        }
    )
    provisional = PatchIntent(
        contract_version="m4-patch-artifact-security/v1",
        repository_identity=repository_identity,
        base_revision=base_revision,
        intent_id="sha256:" + "0" * 64,
        target_scope=tuple(change.path for change in proposal.candidate_changes),
        change_description=" | ".join(
            change.rationale for change in proposal.candidate_changes
        ),
        lineage_digest=lineage_digest,
    )
    return replace(provisional, intent_id=intent_id_for(provisional))


def _patch_artifact(intent: PatchIntent, proposal: PatchProposal) -> PatchArtifact:
    metadata_digest = "sha256:" + sha256_hex(
        {
            "patch_intent_id": intent.intent_id,
            "target_scope": intent.target_scope,
            "profile_id": M4_PATCH_METADATA_SECURITY_V1.profile_id,
            "profile_version": M4_PATCH_METADATA_SECURITY_V1.profile_version,
        }
    )
    lineage_digest = "sha256:" + sha256_hex(
        {
            "patch_intent_id": intent.intent_id,
            "repository_identity": intent.repository_identity,
            "base_revision": intent.base_revision,
            "proposal_policy_decision_id": proposal.policy_decision.decision_id,
            "profile_id": M4_PATCH_METADATA_SECURITY_V1.profile_id,
            "profile_version": M4_PATCH_METADATA_SECURITY_V1.profile_version,
            "metadata_digest": metadata_digest,
        }
    )
    provisional = PatchArtifact(
        contract_version=intent.contract_version,
        artifact_id="sha256:" + "0" * 64,
        repository_identity=intent.repository_identity,
        base_revision=intent.base_revision,
        patch_intent_id=intent.intent_id,
        target_scope=intent.target_scope,
        metadata_digest=metadata_digest,
        lineage_digest=lineage_digest,
    )
    return replace(provisional, artifact_id=artifact_id_for(provisional))


def _validation_error(
    error_code: str,
) -> DeterministicPatchArtifactSecurityValidationError:
    provisional = DeterministicPatchArtifactSecurityValidationError(
        schema_version="m4-patch-artifact-security/v1",
        error_id="sha256:" + "0" * 64,
        error_code=error_code,
        summary="metadata security input is invalid",
    )
    return replace(provisional, error_id=validation_error_id_for(provisional))
