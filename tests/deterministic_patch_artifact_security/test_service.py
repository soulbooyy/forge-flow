"""Terminal-first service tests."""
from __future__ import annotations
from dataclasses import replace
import unittest
from forgeflow.deterministic_patch_artifact_security.models import DeterministicPatchArtifactSecurityValidationError, PatchSecurityTerminal
from forgeflow.deterministic_patch_artifact_security.service import build_patch_security_facts
from forgeflow.patch_proposal.canonical import candidate_digest_for, policy_decision_id_for, proposal_id_for
from forgeflow.patch_proposal.models import CandidateChange, FixStrategy, PatchProposal, PolicyDecisionRef, RootCauseHypothesis, TaskInput
R="fixture-repository-1300511729"; B="97c8220cd713ebf61124ac2de2f3eadc6e4dc222"
def proposal(rationale="Correct nullable state."):
 c=CandidateChange("src/payment_handler.py","modify_existing_file",rationale,("ev_sha256:"+"a"*64,)); d=PolicyDecisionRef("pdr_sha256:"+"0"*64,"allowed","patch-proposal/m2-conservative-v1",1,"m2/deterministic-boundary-evaluator-v1",candidate_digest_for((c,)),(),True); d=replace(d,decision_id=policy_decision_id_for(d)); p=PatchProposal("pp_sha256:"+"0"*64,"m2/deterministic-fixture-v1","rcr_sha256:"+"b"*64,TaskInput("M2-001","Guard nullable payment state"),(RootCauseHypothesis("Payment state can be absent.","medium",("ev_sha256:"+"a"*64,)),),FixStrategy("Correct behavior.",("evidence_backed","minimal_change","no_execution","policy_bounded")),(c,),d,(),("fixture_only_source","no_diff_generated","no_source_payload","no_validation_executed")); return replace(p,contract_id=proposal_id_for(p))
class Tests(unittest.TestCase):
 def test_passed_path_builds_facts_and_candidate(self):
  x=build_patch_security_facts(proposal(),R,B); self.assertNotIsInstance(x,(DeterministicPatchArtifactSecurityValidationError,PatchSecurityTerminal)); i,a,s,rd,c=x; self.assertEqual(s.result,"passed"); self.assertEqual(rd.status,"not_needed"); self.assertEqual(i.pre_scan_metadata_id,s.pre_scan_metadata_id); self.assertEqual(c.patch_artifact_id,a.artifact_id)
 def test_blocked_path_returns_terminal_without_intent_or_artifact(self):
  marker="ghp_abcdefghijklmnopqrstuvwx"; x=build_patch_security_facts(proposal("token="+marker),R,B); self.assertIsInstance(x,PatchSecurityTerminal); self.assertEqual(x.terminal_status,"blocked"); self.assertNotIn(marker,repr(x)); self.assertFalse(hasattr(x,"patch_intent"))
 def test_invalid_lineage_is_safe_error(self):
  x=build_patch_security_facts(replace(proposal(),contract_id="pp_sha256:"+"f"*64),R,B); self.assertIsInstance(x,DeterministicPatchArtifactSecurityValidationError)
