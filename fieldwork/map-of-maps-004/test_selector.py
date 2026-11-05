from __future__ import annotations
import importlib.util,json,tempfile
from pathlib import Path
from unittest.mock import patch
import unittest
p=Path(__file__).with_name("ask_selector.py")
spec=importlib.util.spec_from_file_location("map004",p)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class SelectorLinkTests(unittest.TestCase):
 def test_real_original_MOTIF_native_receipt_pinned(self):
  c=json.loads(m.LOCK_FILE.read_text())
  f=m.ROOT/c["native_receipt"]["path"]
  self.assertEqual(m.blob(f.read_bytes()),c["native_receipt"]["blob"])
  self.assertEqual(c["schema"],"motif.freegraph-inquiry-source-lock/v1")
  self.assertFalse(c["external_lsd_code_executed"])
  self.assertFalse(any(c["rights"].values()))
 def test_repo_source_file_allowlist(self):
  c=json.loads(m.LOCK_FILE.read_text())
  self.assertEqual(len(c["files"]),7)
  self.assertIn("scripts/inquiry_selector.py",c["files"])
  self.assertIn("scripts/motif_reason_bridge.py",c["files"])
  self.assertIn("research/reason-space-002/instruments.json",c["files"])
 def test_missing_freegraph_source_does_not_exec(self):
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaisesRegex(m.Hold,"NATIVE_FREEGRAPH_MISSING"):
    m.checked_sources(Path(d)/"unavailable")
 def test_wrong_owner_commit_fail_closed(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d)
   with patch.object(m.subprocess,"run") as q:
    q.return_value.stdout="0"*40+"\n"
    with self.assertRaisesRegex(m.Hold,"FREEGRAPH_NOT_SOURCE_OWNER_COMMIT"):
     m.checked_sources(root)
 def test_grant_change_invalidates_source_lock(self):
  with tempfile.TemporaryDirectory() as d:
   c=json.loads(m.LOCK_FILE.read_text())
   c["rights"]["network"]=True
   fake=Path(d)/"lock.json";fake.write_text(json.dumps(c))
   with patch.object(m,"LOCK_FILE",fake):
    with self.assertRaisesRegex(m.Hold,"PERMISSION_OR_REPORT_LOCK_CHANGED"):
     m.checked_sources(Path(d))
 def test_source_modification_cannot_be_silently_imported(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);c=json.loads(m.LOCK_FILE.read_text())
   for path in c["files"]:
    f=root/path;f.parent.mkdir(parents=True,exist_ok=True)
    f.write_text("harmless non-matching original source")
   with patch.object(m.subprocess,"run") as call:
    call.return_value.stdout=c["freegraph_commit"]+"\n"
    with self.assertRaisesRegex(m.Hold,"SOURCE_BLOB_CHANGED"):
     m.checked_sources(root)

if __name__=="__main__":unittest.main()
