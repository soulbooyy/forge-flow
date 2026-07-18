"""Pure terminal-first assembly of Feature 2 metadata security facts."""
from __future__ import annotations
from dataclasses import replace
from typing import TypeAlias
from forgeflow.patch_proposal.canonical import candidate_digest_for, policy_decision_id_for, proposal_id_for
from forgeflow.patch_proposal.models import PatchProposal
from forgeflow.patch_proposal.profile import M2_CONSERVATIVE_V1
from .canonical import artifact_id_for, candidate_id_for, intent_id_for, pre_scan_metadata_id_for, sha256_hex, terminal_id_for, validation_error_id_for
from .models import DeterministicPatchArtifactSecurityValidationError, PatchArtifact, PatchIntent, PatchSecurityTerminal, PreScanPatchMetadataIdentity, RedactedArtifactReferenceCandidate, RedactionFact, SecretScanResult
from .policy import redact_metadata, scan_metadata
from .profile import M4_PATCH_METADATA_SECURITY_V1

PatchSecurityFacts: TypeAlias = tuple[PatchIntent, PatchArtifact, SecretScanResult, RedactionFact, RedactedArtifactReferenceCandidate]
PatchSecurityEnvelope: TypeAlias = PatchSecurityFacts | PatchSecurityTerminal | DeterministicPatchArtifactSecurityValidationError
_REPOSITORY = "fixture-repository-1300511729"; _BASE = "97c8220cd713ebf61124ac2de2f3eadc6e4dc222"

def build_patch_security_facts(proposal: object, repository_identity: object, base_revision: object) -> PatchSecurityEnvelope:
    if not _valid_inputs(proposal, repository_identity, base_revision): return _error("invalid_patch_security_input")
    assert isinstance(proposal, PatchProposal) and isinstance(repository_identity, str) and isinstance(base_revision, str)
    projection = (("PreScanMetadataProjection.change_description", " | ".join(c.rationale for c in proposal.candidate_changes)), ("PreScanMetadataProjection.target_scope", "\n".join(c.path for c in proposal.candidate_changes)))
    try:
        pre = _pre(proposal, repository_identity, base_revision, projection)
        scan = scan_metadata(pre, projection, M4_PATCH_METADATA_SECURITY_V1)
        redaction = redact_metadata(pre, projection, scan, M4_PATCH_METADATA_SECURITY_V1)
    except (TypeError, ValueError, UnicodeError): return _error("metadata_construction_invalid")
    if scan.result != "passed" or redaction.status != "not_needed": return _terminal(pre, scan, redaction)
    intent = _intent(pre, scan, proposal); artifact = _artifact(intent, proposal)
    candidate = _candidate(pre, artifact, scan, redaction)
    return intent, artifact, scan, redaction, candidate

def _valid_inputs(p: object, r: object, b: object) -> bool:
    return isinstance(p, PatchProposal) and p.contract_id == proposal_id_for(p) and p.policy_decision.decision_id == policy_decision_id_for(p.policy_decision) and p.policy_decision.evaluated_candidate_digest == candidate_digest_for(p.candidate_changes) and p.proposal_source_id == M2_CONSERVATIVE_V1.proposal_source_id and p.schema_version == "patch-proposal/v1" and p.result_type == "patch_proposal" and p.policy_decision.policy_profile_id == M2_CONSERVATIVE_V1.policy_profile_id and p.policy_decision.policy_version == M2_CONSERVATIVE_V1.policy_version and p.policy_decision.evaluator_id == M2_CONSERVATIVE_V1.evaluator_id and p.policy_decision.revalidation_required is True and p.limitation_codes == tuple(sorted(M2_CONSERVATIVE_V1.allowed_limitation_codes)) and r == _REPOSITORY and b == _BASE

def _pre(p: PatchProposal, r: str, b: str, projection: tuple[tuple[str,str],...]) -> PreScanPatchMetadataIdentity:
    x=PreScanPatchMetadataIdentity("m4-patch-artifact-security/v1", "sha256:"+"0"*64, r,b,tuple(c.path for c in p.candidate_changes),"sha256:"+sha256_hex({"proposal_id":p.contract_id,"policy_id":p.policy_decision.decision_id,"projection_digest":sha256_hex(projection)})); return replace(x,pre_scan_metadata_id=pre_scan_metadata_id_for(x))
def _intent(pre: PreScanPatchMetadataIdentity, scan: SecretScanResult, p: PatchProposal) -> PatchIntent:
    x=PatchIntent(pre.contract_version,pre.repository_identity,pre.base_revision,"sha256:"+"0"*64,pre.pre_scan_metadata_id,pre.target_scope,"sha256:"+sha256_hex({"pre_scan":pre.pre_scan_metadata_id,"scan":scan.scan_id}),"sha256:"+sha256_hex({"pre_scan":pre.pre_scan_metadata_id,"scan":scan.scan_id,"policy":p.policy_decision.decision_id})); return replace(x,intent_id=intent_id_for(x))
def _artifact(i: PatchIntent,p: PatchProposal)->PatchArtifact:
    md="sha256:"+sha256_hex({"intent":i.intent_id,"profile":M4_PATCH_METADATA_SECURITY_V1.profile_id}); x=PatchArtifact(i.contract_version,"sha256:"+"0"*64,i.repository_identity,i.base_revision,i.intent_id,i.target_scope,md,"sha256:"+sha256_hex({"intent":i.intent_id,"policy":p.policy_decision.decision_id,"metadata":md})); return replace(x,artifact_id=artifact_id_for(x))
def _candidate(pre: PreScanPatchMetadataIdentity,a:PatchArtifact,s:SecretScanResult,r:RedactionFact)->RedactedArtifactReferenceCandidate:
    x=RedactedArtifactReferenceCandidate(a.contract_version,"sha256:"+"0"*64,a.artifact_id,pre.pre_scan_metadata_id,s.scan_id,r.redaction_id,r.output_metadata_digest or "sha256:"+"0"*64,"sha256:"+sha256_hex({"artifact":a.artifact_id,"scan":s.scan_id,"redaction":r.redaction_id}),M4_PATCH_METADATA_SECURITY_V1.profile_id,M4_PATCH_METADATA_SECURITY_V1.profile_version,s.rule_set_id,r.rule_set_id); return replace(x,candidate_id=candidate_id_for(x))
def _terminal(pre:PreScanPatchMetadataIdentity,s:SecretScanResult,r:RedactionFact)->PatchSecurityTerminal:
    reason = "security_rule_blocked" if s.result=="blocked" else ("scanner_operation_failed" if s.result=="failed" else ("redaction_operation_failed" if r.status=="failed" else (s.failure_reason or "metadata_projection_invalid")))
    status = "blocked" if s.result=="blocked" else ("failed" if reason in ("scanner_operation_failed","redaction_operation_failed") else "indeterminate")
    x=PatchSecurityTerminal(pre.contract_version,"sha256:"+"0"*64,pre.pre_scan_metadata_id,pre.lineage_digest,s,r,status,reason); return replace(x,terminal_id=terminal_id_for(x))
def _error(code:str)->DeterministicPatchArtifactSecurityValidationError:
    x=DeterministicPatchArtifactSecurityValidationError("m4-patch-artifact-security/v1","sha256:"+"0"*64,code,"metadata security input is invalid"); return replace(x,error_id=validation_error_id_for(x))
