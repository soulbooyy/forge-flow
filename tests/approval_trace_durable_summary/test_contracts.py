from dataclasses import FrozenInstanceError
import hashlib
import json
import unittest
from forgeflow.approval_trace_durable_summary.models import ApprovalRequest,ApprovalDecision,MetadataArtifactReference,TraceEvent,DurableRunSummary
from forgeflow.approval_trace_durable_summary.canonical import request_id_for,decision_id_for,artifact_reference_id_for,event_id_for,summary_id_for
D="sha256:"+"a"*64
D2="sha256:"+"b"*64
SCHEMA="forgeflow.approval-trace-durable-summary.v1"
class ContractTests(unittest.TestCase):
 def test_request_is_frozen_and_bound(self):
  v=ApprovalRequest(SCHEMA,D,D,D,"fixture-repository-1300511729","a"*40,"fixture",1,D,("sensitive_path",),1)
  with self.assertRaises(FrozenInstanceError):v.expires_at=2
 def test_rejects_payload_and_uncontrolled_decision(self):
  with self.assertRaises(ValueError): ApprovalRequest(SCHEMA,D,D,D,"x/secret", "a"*40,"fixture",1,D,("sensitive_path",),1)
  with self.assertRaises(ValueError): ApprovalRequest(SCHEMA,D,D,D,"fixture", "a"*40,"fixture",1,D,("ghp_abcdefghijklmnopqrstuvwx",),1)
  with self.assertRaises(ValueError): ApprovalDecision(SCHEMA,D,D,D,"authorized",1)
 def test_rejects_mutable_or_unordered_reference_collections(self):
  with self.assertRaises(ValueError): TraceEvent(SCHEMA,D,"run-0001","artifact_published",[D],"ok")
  with self.assertRaises(ValueError): TraceEvent(SCHEMA,D,"run-0001","artifact_published",(),"ok")
  with self.assertRaises(ValueError): TraceEvent(SCHEMA,D,"run-0001","artifact_published",(D,D),"ok")
  with self.assertRaises(ValueError): TraceEvent(SCHEMA,D,"run-0001","artifact_published",(D2,D),"ok")
  for field in range(4):
   collections=[(D,),(D,),(D,),(D,)]
   collections[field]=[D]
   with self.assertRaises(ValueError): DurableRunSummary(SCHEMA,D,"run-0001",*collections,"complete")
   collections=[(D,),(D,),(D,),(D,)]
   collections[field]=()
   with self.assertRaises(ValueError): DurableRunSummary(SCHEMA,D,"run-0001",*collections,"complete")
   collections=[(D,),(D,),(D,),(D,)]
   collections[field]=(D,D)
   with self.assertRaises(ValueError): DurableRunSummary(SCHEMA,D,"run-0001",*collections,"complete")
  with self.assertRaises(ValueError): DurableRunSummary(SCHEMA,D,"run-0001",(D2,D),(D,),(D,),(D,),"complete")
 def test_rejects_invalid_schema_profile_and_safe_text(self):
  with self.assertRaises(ValueError): ApprovalRequest("v",D,D,D,"fixture-repository-1300511729","a"*40,"profile-001",1,D,("sensitive_path",),1)
  with self.assertRaises(ValueError): ApprovalRequest(SCHEMA,D,D,D,"raw source contents","a"*40,"profile-001",0,D,("sensitive_path",),1)
  with self.assertRaises(ValueError): ApprovalRequest(SCHEMA,D,D,D,"repository-001","a"*40,"profile-001",True,D,("sensitive_path",),1)
  with self.assertRaises(ValueError): MetadataArtifactReference(SCHEMA,D,"run-0001",D,D,D,"profile-001",0,D)
  with self.assertRaises(ValueError): MetadataArtifactReference(SCHEMA,D,"run-0001",D,D,D,"profile-001",True,D)
  with self.assertRaises(ValueError): MetadataArtifactReference(SCHEMA,D,"run-0001"*40,D,D,D,"profile-001",1,D)
 def test_reference_trace_and_summary_are_frozen_and_reject_payloads(self):
  reference=MetadataArtifactReference(SCHEMA,D,"run-0001",D,D,D,"profile-001",1,D)
  event=TraceEvent(SCHEMA,D,"run-0001","artifact_published",(D,),"ok")
  summary=DurableRunSummary(SCHEMA,D,"run-0001",(D,),(D,),(D,),(D,),"complete")
  for value,field in ((reference,"run_id"),(event,"detail_code"),(summary,"final_stop_reason")):
   with self.assertRaises(FrozenInstanceError): setattr(value,field,"raw/source")
  with self.assertRaises(ValueError): MetadataArtifactReference(SCHEMA,D,"run/path",D,D,D,"profile-001",1,D)
  with self.assertRaises(ValueError): TraceEvent(SCHEMA,D,"run-0001","artifact_published",(D,),"BEGIN PRIVATE KEY")
  with self.assertRaises(ValueError): DurableRunSummary(SCHEMA,D,"run/source",(D,),(D,),(D,),(D,),"complete")
 def test_every_identity_helper_is_a_fixed_point(self):
  request=ApprovalRequest(SCHEMA,D,D,D,"repository-001","a"*40,"profile-001",1,D,("sensitive_path",),1)
  decision=ApprovalDecision(SCHEMA,D,D,D,"approved",1)
  reference=MetadataArtifactReference(SCHEMA,D,"run-0001",D,D,D,"profile-001",1,D)
  event=TraceEvent(SCHEMA,D,"run-0001","artifact_published",(D,),"ok")
  summary=DurableRunSummary(SCHEMA,D,"run-0001",(D,),(D,),(D,),(D,),"complete")
  for value,field,helper in ((request,"request_id",request_id_for),(decision,"decision_id",decision_id_for),(reference,"artifact_reference_id",artifact_reference_id_for),(event,"event_id",event_id_for),(summary,"summary_id",summary_id_for)):
   identity=helper(value)
   fields={name:getattr(value,name) for name in value.__dataclass_fields__}
   fields[field]=identity
   self.assertEqual(identity,helper(value.__class__(**fields)))
 def test_each_identity_helper_includes_every_other_identity_field(self):
  request=ApprovalRequest(SCHEMA,D,D,D,"repository-001","a"*40,"profile-001",1,D,("sensitive_path",),1)
  decision=ApprovalDecision(SCHEMA,D,D,D,"approved",1)
  reference=MetadataArtifactReference(SCHEMA,D,"run-0001",D,D,D,"profile-001",1,D)
  event=TraceEvent(SCHEMA,D,"run-0001","artifact_published",(D,),"ok")
  summary=DurableRunSummary(SCHEMA,D,"run-0001",(D,),(D,),(D,),(D,),"complete")
  for value,identity_field,helper in ((request,"request_id",request_id_for),(decision,"decision_id",decision_id_for),(reference,"artifact_reference_id",artifact_reference_id_for),(event,"event_id",event_id_for),(summary,"summary_id",summary_id_for)):
   fields={name:getattr(value,name) for name in value.__dataclass_fields__}
   fields.pop(identity_field)
   expected="sha256:"+hashlib.sha256(json.dumps(fields,sort_keys=True,separators=(",", ":")).encode()).hexdigest()
   self.assertEqual(expected,helper(value))
