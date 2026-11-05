"""Adversarial bounded tests for the read-only multi-source field map."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
p=Path(__file__).with_name("engine.py")
spec=importlib.util.spec_from_file_location("field_map_engine",p)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
DATA={
 "atlas-families":{"owner":"the-static-collective","constellations":[
  {"slug":"a","repositories":["MOTIF","planZ"]},
  {"slug":"b","repositories":["GRAFT","CANNON"]}]},
 "atlas-relations":{"schema":"static-git-atlas/relations-v1","relations":[{
   "from_repo":"GRAFT","to_repo":"MOTIF","source_url":"https://github.com/example",
   "status":"declared","authority_owner":"GRAFT"}]},
 "atlas-visibility":{"schema":"static-git-atlas/visibility-policy-v1",
   "restricted_default_projection":"omit"},
 "atlas-inventory-summary":"Captured: **2026-11-05T15:27:31+00:00** · **90 public repositories** · **2579 branch refs** (including defaults) · **1350 open PRs**.",
 "planz-attention":{"schema":"planz/public-attention-v1","authority":"INDEX_ONLY",
  "edition":"synthetic","reviewedOn":"2026-11-05",
  "entries":[{"id":"ATLAS-BRIDGE-002","source":"https://github.com/example/issues/13",
    "disposition":"PROPOSED","nextGate":"Review owner","blockedBy":["SOURCE_PIN_REVIEW"],
    "executionAllowed":False,"fieldOutcome":"NOT_VERIFIED",
    "thirdPartyApproval":"NOT_ESTABLISHED"}]},
 "graft-donor-registry":{"schema":"graft.donor-code-registry/v1",
  "policy":{"raw_witness_data_imported":False},"candidates":[{"id":"first"}],
  "adapters":[{"id":"some"}]},
 "cannon-question-field":{"schema":"cannon.interface-field-source-lock/v1",
  "authority":"NONE","policies":{"autoBridge":False},
  "edges":[{"id":"PLZ_TO_CANNON","knownNative":True},
           {"id":"PLZ_TO_PLAYDECK","knownNative":False,"support":"unsupported",
            "evidenceClass":"speculation","sourceCase":"UNTESTED",
            "claim":"A proposal is not a receipt","fromType":"planZ",
            "toType":"PlayDeck"}]}
}
class FieldMapTests(unittest.TestCase):
 def setUp(self):
  self.t=tempfile.TemporaryDirectory()
  self.root=Path(self.t.name)/"source"
  self.root.mkdir()
  self.manifest={"schema":"motif.map-sources-lock/v1",
   "policy":{"public_sources_only":True,"automatic_promotion":False},
   "sources":[]}
  for tier,ident,checkout,path,kind in [
   (1,"atlas-families","atlas","atlas/constellations.json","json"),
   (1,"atlas-relations","atlas","atlas/relations.json","json"),
   (1,"atlas-visibility","atlas","atlas/visibility-policy.json","json"),
   (1,"atlas-inventory-summary","atlas","atlas/generated/README.md","markdown"),
   (2,"planz-attention","planz","public/attention-v1.json","json"),
   (3,"graft-donor-registry","graft","candidate-registry.json","json"),
   (3,"cannon-question-field","cannon","registry/multi-repo-question-field-v1.json","json")
  ]:
   file=self.root/checkout/path
   file.parent.mkdir(parents=True,exist_ok=True)
   contents=(DATA[ident] if kind=="markdown" else json.dumps(DATA[ident]))
   file.write_text(contents,encoding="utf8")
   self.manifest["sources"].append({
    "id":ident,"tier":tier,"checkout":checkout,
    "repo":m.OWNERS[checkout],"commit":"1"*40,
    "path":path,"blob":m.git_blob(file.read_bytes()),
    "kind":kind,"max_bytes":25000})
  self.lock=Path(self.t.name)/"lock.json"
  self.persist()
 def persist(self):
  self.lock.write_text(json.dumps(self.manifest))
 def tearDown(self):self.t.cleanup()
 def read(self,tier):
  return m.run(self.root,tier,self.lock)
 def test_progressive_tiers_really_change_question_and_scope(self):
  a,b,c=[self.read(k) for k in (1,2,3)]
  self.assertEqual([x["source_count"] for x in (a,b,c)],[4,5,7])
  self.assertEqual([len(x["questions"]) for x in (a,b,c)],[1,2,3])
  self.assertEqual(c["atlas"]["reported_public_repositories"],90)
  self.assertEqual(c["atlas"]["reported_branch_refs"],2579)
  self.assertEqual(c["planz"]["plan_attention"] if "plan_attention" in c["planz"] else
                   c["plan_attention"]["authorized_to_execute"],0)
  self.assertEqual(c["technical_evidence"]["held_cross_owner_candidates"],1)
  self.assertFalse(c["technical_evidence"]["selected_unproven_edge"]["is_runtime_compatible"])
  self.assertEqual(c["motif_first_next_experiment"]["result_status"],"PROPOSED_NOT_EXECUTED")
  self.assertFalse(c["external_actions"])
  self.assertEqual(c["network_requests_from_reasoner"],0)
 def test_changed_source_bytes_fail_closed(self):
  f=self.root/"atlas/atlas/relations.json"
  f.write_text('{"changed":true}')
  with self.assertRaisesRegex(ValueError,"SOURCE_BLOB_MISMATCH"):self.read(1)
 def test_symlinked_sources_fail_closed(self):
  f=self.root/"atlas/atlas/relations.json"
  content=f.read_bytes()
  f.unlink()
  alternate=Path(self.t.name)/"other.json"
  alternate.write_bytes(content)
  f.symlink_to(alternate)
  with self.assertRaisesRegex(ValueError,"MISSING_OR_SYMLINK"):self.read(1)
 def test_visibility_cannot_be_silently_reinterpreted(self):
  f=self.root/"atlas/atlas/visibility-policy.json"
  obj=json.loads(f.read_text());obj["restricted_default_projection"]="presence"
  f.write_text(json.dumps(obj))
  self.manifest["sources"][2]["blob"]=m.git_blob(f.read_bytes())
  self.persist()
  with self.assertRaisesRegex(ValueError,"ATLAS_PUBLIC_AUTHORITY_BOUNDARY"):self.read(1)
 def test_held_plan_must_not_turn_into_execution(self):
  f=self.root/"planz/public/attention-v1.json"
  obj=json.loads(f.read_text());obj["entries"][0]["executionAllowed"]=True
  f.write_text(json.dumps(obj))
  self.manifest["sources"][4]["blob"]=m.git_blob(f.read_bytes())
  self.persist()
  with self.assertRaisesRegex(ValueError,"PLANZ_UNAUTHORIZED_PROMOTION"):self.read(2)
 def test_unverified_adapter_cannot_be_labelled_supported(self):
  f=self.root/"cannon/registry/multi-repo-question-field-v1.json"
  obj=json.loads(f.read_text());obj["edges"][1]["support"]="supported"
  f.write_text(json.dumps(obj))
  self.manifest["sources"][6]["blob"]=m.git_blob(f.read_bytes())
  self.persist()
  with self.assertRaisesRegex(ValueError,"UNVERIFIED_BRIDGE_PROMOTED"):self.read(3)
 def test_no_arbitrary_paths(self):
  self.manifest["sources"][0]["path"]="../secret"
  self.persist()
  with self.assertRaisesRegex(ValueError,"BAD_SOURCE_PIN"):self.read(1)
 def test_no_automatic_private_access_or_expansion(self):
  obj=self.read(3)
  self.assertFalse(obj["private_sources_read"])
  self.assertFalse(obj["automatic_canon_promotion"])
  self.assertFalse(obj["auto_source_writes"])
  self.assertIsNone(obj["joules_measured"])
  self.assertIsNone(obj["next_tier"])
 def test_invalid_tier_fails(self):
  with self.assertRaisesRegex(ValueError,"INVALID_TIER"):self.read(4)

if __name__=="__main__":unittest.main()
