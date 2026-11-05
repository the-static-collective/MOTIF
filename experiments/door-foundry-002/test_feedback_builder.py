"""CANNON -> MOTIF reverse loop: genuine original receipt, three build variants,
mutant evidence and no autonomous repo edits or real-world claims."""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

import feedback_builder as fb


class CannonFeedbackTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.receipt = Path(os.environ["CANNON_RECEIPT"])
        cls.selection = Path(os.environ["CANNON_SELECTION"])
        cls.source = Path(os.environ["MOTIF_SOURCE"])
        cls.tmp = tempfile.TemporaryDirectory(prefix="motif-build-002-")
        cls.output = Path(cls.tmp.name) / "new-builds"
        cls.selected = fb.read_json(cls.selection)
        cls.packet = fb.read_json(cls.receipt)
        cls.report = fb.make_builds(cls.receipt, cls.selection,
                                    cls.source, cls.output)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def run_candidate(self, target, root=None):
        path = (root or self.output) / ("motif-build-" + target.replace("_","-"))
        return subprocess.run([sys.executable, "run.py"], cwd=path,
                              text=True, capture_output=True, timeout=20)

    def test_original_cannon_receipt_really_consumed(self):
        self.assertEqual(self.report["cannon_commit"], fb.CANNON_COMMIT)
        self.assertEqual(self.report["motif_source_commit"], fb.SOURCE_COMMIT)
        self.assertEqual(self.report["origin"], "CANNON_UNMERGED_SELECTION")
        self.assertEqual(self.report["cannon_receipt_sha256"],
                         self.packet["content_sha256"])
        self.assertEqual(self.report["disposition"], "HOLD_FOR_OPERATOR_REVIEW")

    def test_verified_source_is_specific_unmerged_commit(self):
        fb.verify_native_source(self.source)
        self.assertEqual(len(fb.PINNED), 6)

    def test_three_distinct_new_runnable_motif_builds_exist(self):
        self.assertEqual(len(self.report["generated"]), 3)
        names = {x["target"] for x in self.report["generated"]}
        self.assertEqual(names, {"frontier", "macro_replay", "door"})
        self.assertEqual(
            {len(x["capabilities"]) for x in self.report["generated"]},
            {2, 3, 5})
        self.assertEqual(
            len({tuple(x["capabilities"]) for x in self.report["generated"]}),
            3)

    def test_real_original_source_is_bundled_not_reinvented(self):
        for data in self.report["generated"]:
            path = self.output / data["folder"]
            spec = fb.read_json(path/"manifest.json")
            self.assertEqual(spec["source_commit"], fb.SOURCE_COMMIT)
            self.assertEqual(spec["cannon_review_receipt_sha256"],
                             self.packet["content_sha256"])
            self.assertEqual(spec["disposition"],
                             "LOCAL_BUILD_CANDIDATE_NOT_ADMITTED")
            for rel, blob in spec["copied_owner_files"].items():
                self.assertEqual(fb.git_blob(path / rel), blob)
                self.assertEqual(blob, fb.PINNED[rel])

    def test_frontier_new_build_actually_executes(self):
        done = self.run_candidate("frontier")
        self.assertEqual(done.returncode, 0, done.stderr+done.stdout)
        doc = json.loads(done.stdout)
        self.assertEqual(doc["target"], "frontier")
        self.assertGreaterEqual(doc["result"]["candidate_count"], 2)
        self.assertGreaterEqual(doc["result"]["new_affordance_count"], 1)
        self.assertEqual(len(doc["selected_capabilities"]), 2)
        self.assertTrue(doc["no_external_actions"])

    def test_macro_new_build_actually_executes(self):
        done = self.run_candidate("macro_replay")
        self.assertEqual(done.returncode, 0, done.stderr+done.stdout)
        doc = json.loads(done.stdout)
        self.assertEqual(doc["target"], "macro_replay")
        self.assertEqual(len(doc["selected_capabilities"]), 3)
        self.assertEqual(doc["result"]["expanded_primitive_steps"], 3)
        self.assertEqual(len(doc["result"]["predicted_new_facts"]), 3)

    def test_door_new_build_actually_executes_and_admits_baseline_tie(self):
        done = self.run_candidate("door")
        self.assertEqual(done.returncode, 0, done.stderr+done.stdout)
        doc = json.loads(done.stdout)
        self.assertEqual(doc["target"], "door")
        self.assertEqual(len(doc["selected_capabilities"]), 5)
        self.assertTrue(doc["result"]["classic_002_also_succeeds"])
        self.assertEqual(doc["result"]["expanded_primitive_steps"], 3)
        self.assertEqual(doc["status"], "EXECUTED_LOCAL_SYNTHETIC_CANDIDATE")

    def test_generated_report_does_not_pretend_to_modify_the_source(self):
        self.assertEqual(self.report["real_world_actions"], 0)
        self.assertEqual(self.report["automatic_git_commits"], 0)
        self.assertFalse(self.report["source_changed"])
        self.assertFalse(self.report["automatic_promotion"])
        self.assertEqual(self.report["field_outcomes_observed"], 0)

    def test_cannon_signed_or_admitted_status_is_not_inferred(self):
        for item in self.report["generated"]:
            spec = fb.read_json(self.output/item["folder"]/"manifest.json")
            self.assertEqual(spec["authority"], fb.AUTHORITY)
            self.assertFalse(any(spec["authority"].values()))
            self.assertEqual(spec["scope"],"SYNTHETIC_RESEARCH_ONLY")

    def test_corrupted_cannon_receipt_digest_refused(self):
        packet = dict(self.packet, content_sha256="0"*64)
        with self.assertRaisesRegex(fb.HOLD,"digest mismatch"):
            fb.verify_receipt(packet,self.selected)

    def test_self_rehashed_false_cannon_approval_refused(self):
        packet = json.loads(json.dumps(self.packet))
        packet["selection"]["selected_as_canon"] = True
        raw = dict(packet);raw.pop("content_sha256")
        packet["content_sha256"] = fb.digest(raw)
        with self.assertRaisesRegex(fb.HOLD, "promote held"):
            fb.verify_receipt(packet,self.selected)

    def test_self_rehashed_field_outcome_refused(self):
        packet = json.loads(json.dumps(self.packet))
        packet["evidence"]["observed_human_outcome"] = True
        raw = dict(packet);raw.pop("content_sha256")
        packet["content_sha256"] = fb.digest(raw)
        with self.assertRaises(fb.HOLD):
            fb.verify_receipt(packet,self.selected)

    def test_self_rehashed_implicit_permission_refused(self):
        packet = json.loads(json.dumps(self.packet))
        packet["actor_or_receiver_authorized"] = True
        raw = dict(packet);raw.pop("content_sha256")
        packet["content_sha256"] = fb.digest(raw)
        with self.assertRaises(fb.HOLD):
            fb.verify_receipt(packet,self.selected)

    def test_wrong_cannon_selected_commit_refused(self):
        selected = dict(self.selected,selected_commit="0"*40)
        with self.assertRaises(fb.HOLD):
            fb.verify_selection(selected)

    def test_cannon_selected_false_permission_refused(self):
        selected = json.loads(json.dumps(self.selected))
        selected["authority"]["permission_to_execute_external_effects"] = True
        with self.assertRaises(fb.HOLD):
            fb.verify_selection(selected)

    def test_cannon_rerouted_source_file_refused(self):
        selected = json.loads(json.dumps(self.selected))
        selected["pinned_files"]["experiments/002/motif002.py"]="0"*40
        with self.assertRaises(fb.HOLD):
            fb.verify_selection(selected)

    def test_current_branch_not_mistaken_for_selected_source(self):
        with self.assertRaisesRegex(fb.HOLD,"not pinned"):
            fb.verify_native_source(fb.ROOT)

    def test_output_overwrite_refused(self):
        with self.assertRaisesRegex(fb.HOLD,"already exists"):
            fb.make_builds(self.receipt,self.selection,self.source,self.output)

    def test_missing_provider_is_not_a_new_build(self):
        caps = fb.verify_contracts(self.source, self.selected)
        with self.assertRaises(fb.door.HOLD):
            fb.door.compose(tuple(x for x in caps
                                  if x.handler != "compile_original_006"),
                            {"world","goal"},target="door")

    def test_tampered_generated_spec_refused(self):
        with tempfile.TemporaryDirectory() as temp:
            dest=Path(temp)/"motif-build-frontier"
            shutil.copytree(self.output/"motif-build-frontier",dest)
            spec=fb.read_json(dest/"manifest.json")
            spec["authority"]["external_execution"]=True
            (dest/"manifest.json").write_text(json.dumps(spec))
            result=self.run_candidate("frontier",root=Path(temp))
            self.assertNotEqual(result.returncode,0)
            self.assertEqual(json.loads(result.stdout)["stage"],"HOLD")

    def test_tampered_generated_source_refused(self):
        with tempfile.TemporaryDirectory() as temp:
            dest=Path(temp)/"motif-build-macro-replay"
            shutil.copytree(self.output/"motif-build-macro-replay",dest)
            p=dest/"experiments/002/motif002.py"
            p.write_bytes(p.read_bytes()+b"\n# fork\n")
            result=self.run_candidate("macro_replay",root=Path(temp))
            self.assertNotEqual(result.returncode,0)
            self.assertEqual(json.loads(result.stdout)["stage"],"HOLD")

    def test_tampered_generated_runner_refused(self):
        with tempfile.TemporaryDirectory() as temp:
            dest=Path(temp)/"motif-build-door"
            shutil.copytree(self.output/"motif-build-door",dest)
            p=dest/"run.py"
            p.write_bytes(p.read_bytes()+b"\n# altered\n")
            result=self.run_candidate("door",root=Path(temp))
            self.assertNotEqual(result.returncode,0)
            self.assertEqual(json.loads(result.stdout)["stage"],"HOLD")

    def test_receipt_report_reconstructible(self):
        report=fb.read_json(self.output/"build-report.json")
        raw=dict(report);sha=raw.pop("content_sha256")
        self.assertEqual(fb.digest(raw),sha)
        self.assertEqual(report,self.report)


if __name__=="__main__":
    unittest.main()
