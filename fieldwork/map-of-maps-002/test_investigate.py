"""Guardrail tests for MOTIF Map 002; real source execution in GitHub CI."""
import importlib.util
import json
import pathlib
import tempfile
import unittest
from unittest.mock import patch
p=pathlib.Path(__file__).with_name("investigate.py")
spec=importlib.util.spec_from_file_location("motif_map002",p)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class NativeInquiryTests(unittest.TestCase):
 def test_exact_six_independent_source_owners_held_to_version_pins(self):
  l=m.get_lock()
  self.assertEqual(set(x["id"] for x in l["source_owners"]),
   {"alex","dogram","planz-native","planz-proposal","graft-native","playdeck"})
  self.assertEqual(l["permission"],"LOCAL_PUBLIC_SNAPSHOT_ANALYSIS_ONLY")
  self.assertTrue(l["safety"]["local_mocks_are_not_real_network_observations"])
 def test_source_owner_commit_guard_is_not_just_document_hash(self):
  l=m.get_lock()
  with tempfile.TemporaryDirectory() as d:
   root=pathlib.Path(d)
   for owner in l["source_owners"]:
    folder=root/owner["id"];folder.mkdir()
    for f in owner["files"]:
     path=folder/f["path"];path.parent.mkdir(exist_ok=True,parents=True)
     path.write_text("safe synthetic source contents")
     f["blob"]=m.blob(path.read_bytes())
   class G:
    stdout="0"*40+"\n"
   with patch.object(m.subprocess,"run",return_value=G()):
    with self.assertRaisesRegex(ValueError,"HOLD_STALE_SOURCE_HEAD"):
     m.verify_native(root,l)
   def original_git(command,**kwargs):
    class Response:
     stdout=next(o["commit"] for o in l["source_owners"]
          if "/"+o["id"]+"/" in command[2]+"/")+"\n"
    return Response()
   with patch.object(m.subprocess,"run",side_effect=original_git):
    self.assertEqual(len(m.verify_native(root,l)),sum(len(o["files"]) for o in l["source_owners"]))
    first=root/"alex"/"alex_runtime"/"derivation.py"
    first.write_text("tampered")
    with self.assertRaisesRegex(ValueError,"HOLD_CHANGED_NATIVE_BYTES"):
     m.verify_native(root,l)
 def test_symlink_original_source_is_refused(self):
  l=m.get_lock()
  with tempfile.TemporaryDirectory() as d:
   root=pathlib.Path(d);folder=root/"alex";folder.mkdir()
   outside=root/"outside.txt";outside.write_text("sensitive")
   f=folder/"alex_runtime"/"derivation.py";f.parent.mkdir()
   f.symlink_to(outside)
   with patch.object(m.subprocess,"run") as stub:
    stub.return_value.stdout=l["source_owners"][0]["commit"]+"\n"
    with self.assertRaisesRegex(ValueError,"HOLD_MISSING_NATIVE_FILE"):
     m.verify_native(root,l)
 def test_playdeck_type_claim_cannot_be_inferred_from_proposal_name(self):
  edge={
   "id":"PLZ_TO_PLAYDECK","knownNative":False,"support":"unsupported",
   "fromType":"static-collective/planz-recursive-reactor/v1/proposal",
   "toType":"playdeck.PerformanceReceipt/v0.1"}
  with tempfile.TemporaryDirectory() as d:
   root=pathlib.Path(d)
   for rel in [
    "planz-proposal/reactor/recursive.mjs",
    "playdeck/packages/core/src/PerformanceReceipt.ts",
    "playdeck/packages/receipts/src/validateReceipt.ts",
    "playdeck/packages/receipts/src/sealReceipt.ts"
   ]:
    p=root/rel;p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text("no authored receipt contract here")
   with self.assertRaisesRegex(ValueError,"HOLD_PLANZ_OWNER_PROPOSAL_STATE_CHANGED"):
    m.original_type_probe(root,edge)
   bad=dict(edge);bad["support"]="supported"
   with self.assertRaisesRegex(ValueError,"HOLD_MAP_SELECTED_UNVERIFIED_EDGE_CHANGED"):
    m.original_type_probe(root,bad)
 def test_original_question_not_automatically_grant(self):
  self.assertFalse(m.get_lock()["safety"]["no_external_execution"] is False)
  self.assertEqual(m.SCHEMA,"motif.map-of-maps-native-court/v1")

if __name__=="__main__":unittest.main()
