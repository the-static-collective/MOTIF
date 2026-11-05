"""MOTIF Map 003 source-owner and read-only graph integration guards."""
from __future__ import annotations
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

here=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("motif_003_freegraph",here/"ask_freegraph.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class SourceOwnedFreeGraphTests(unittest.TestCase):
 def test_frozen_real_native_report_identity(self):
  report=m.REPO/m.REPORT_PATH
  self.assertTrue(report.is_file())
  self.assertEqual(m.git_blob(report.read_bytes()),m.REPORT_BLOB)
 def test_source_pins_are_an_exact_allowlist(self):
  config=json.loads(m.LOCK.read_text())
  self.assertEqual(config["schema"],"motif.freegraph-join/v1")
  self.assertEqual(config["freegraph_source_owner"]["commit"],m.FG_COMMIT)
  self.assertEqual({x["path"]:x["blob"] for x in
     config["freegraph_source_owner"]["files"]},m.SOURCE_PINS)
  self.assertEqual(len(m.SOURCE_PINS),4)
  self.assertFalse(any(config["rights"].values()))
 def test_missing_original_freegraph_will_hold(self):
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaisesRegex(m.Hold,"FREEGRAPH_CHECKOUT_REQUIRED"):
    m.verify(Path(d)/"does-not-exist",m.REPO/m.REPORT_PATH)
 def test_modified_permission_lock_does_not_gain_network(self):
  with tempfile.TemporaryDirectory() as d:
   lock=json.loads(m.LOCK.read_text())
   lock["rights"]["network"]=True
   fake=Path(d)/"changed.json";fake.write_text(json.dumps(lock))
   with patch.object(m,"LOCK",fake):
    with self.assertRaisesRegex(m.Hold,"SOURCE_GRANT_INVALID"):
     m.verify(Path(d),m.REPO/m.REPORT_PATH)
 def test_missing_real_source_blob_refused_before_import(self):
  with tempfile.TemporaryDirectory() as d:
   folder=Path(d)
   with patch.object(m.subprocess,"run") as runner:
    runner.return_value.stdout=m.FG_COMMIT+"\n"
    with self.assertRaisesRegex(m.Hold,"FREEGRAPH_SOURCE_MISSING_OR_SYMLINK"):
     m.verify(folder,m.REPO/m.REPORT_PATH)
 def test_invalid_report_path_is_rejected_after_fake_source_identity_checks(self):
  with tempfile.TemporaryDirectory() as d:
   folder=Path(d)/"freegraph";folder.mkdir()
   config=json.loads(m.LOCK.read_text())
   fake_pins={}
   for item in config["freegraph_source_owner"]["files"]:
    f=folder/item["path"]
    f.parent.mkdir(parents=True,exist_ok=True)
    f.write_text("local harmless test fixture")
    item["blob"]=m.git_blob(f.read_bytes())
    fake_pins[item["path"]]=item["blob"]
   lock=Path(d)/"fake-lock.json";lock.write_text(json.dumps(config))
   unapproved=Path(d)/"unapproved.json"
   unapproved.write_text('{"note":"not the pinned historical report"}')
   with patch.object(m,"SOURCE_PINS",fake_pins),patch.object(m,"LOCK",lock),patch.object(m.subprocess,"run") as runner:
    runner.return_value.stdout=m.FG_COMMIT+"\\n"
    with self.assertRaisesRegex(m.Hold,"MOTIF_REPORT_UNAUTHORIZED_OR_RELOCATED"):
     m.verify(folder,unapproved)

if __name__=="__main__":
 unittest.main()
