"""Proof that CANNON-reviewed GRAFT created new code consumed by MOTIF policy."""
import copy
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

import graft_backloop as m


class GraftBornOperatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet_path=Path(os.environ["CANNON_GRAFT_RECEIPT"])
        cls.graft=Path(os.environ["GRAFT_SOURCE"])
        cls.motif=Path(os.environ["MOTIF_ORIGINAL"])
        cls.packet=m.read_doc(cls.packet_path)
        cls.tmp=tempfile.TemporaryDirectory(prefix="graft-sensor-")
        cls.folder=Path(cls.tmp.name)/"new-motif-sensor"
        cls.report=m.build(cls.packet_path,cls.graft,cls.motif,cls.folder)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def exec_runner(self,folder=None):
        return subprocess.run([sys.executable,"run.py"],
             cwd=folder or self.folder,text=True,capture_output=True,timeout=20)

    def test_new_executable_genuinely_compiled_by_original_graft(self):
        original=m.regenerate_from_original_graft(self.graft)
        self.assertEqual(original["source"],self.packet["selected_operator"]["source"])
        self.assertEqual(original["selector"],["observed","reachable_actions"])
        self.assertEqual(original["code_installed"],False)
        self.assertEqual(original["source_sha256"],self.report["source_sha256"])

    def test_source_is_original_independent_unmerged_graft_revision(self):
        self.assertEqual(m.checked_git_source(self.graft,m.GRAFT_SHA,m.PINS_GRAFT),
                         self.graft.resolve())
        self.assertEqual(len(m.PINS_GRAFT),5)
        self.assertEqual(self.packet["selected_graft"]["commit"],m.GRAFT_SHA)

    def test_cannon_original_code_does_not_promote_to_real_permission(self):
        self.assertEqual(self.packet["disposition"],
                         "HOLD_FOR_MOTIF_LOCAL_SYNTHETIC_REVIEW")
        self.assertFalse(self.packet["is_signed"])
        self.assertFalse(self.packet["received_by_motif"])
        self.assertFalse(any(self.packet["authority"].values()))

    def test_generated_build_files_are_real_and_source_pinned(self):
        self.assertTrue((self.folder/"generated_sensor.mjs").exists())
        self.assertTrue((self.folder/"run.py").exists())
        self.assertTrue((self.folder/"observe.mjs").exists())
        spec=m.read_doc(self.folder/"manifest.json")
        self.assertEqual(spec["source_owner"] if "source_owner" in spec else
                         spec["operator_kind"],"GRAFT_GENERATED_NEW_EXECUTABLE_NUMERIC_PROJECTION")
        self.assertEqual(spec["motif_source_pins"],m.PINS_MOTIF)
        self.assertEqual(spec["graft_source_pins"],m.PINS_GRAFT)
        self.assertEqual(spec["status"],"HELD_LOCAL_EXECUTABLE_NOT_ADMITTED")
        self.assertFalse(any(spec["authority"].values()))
        for p,sha in m.PINS_MOTIF.items():
            self.assertEqual(m.blob(self.folder/p),sha)

    def test_new_motif_variant_executes_generated_js_in_fresh_process(self):
        p=self.exec_runner()
        self.assertEqual(p.returncode,0,p.stdout+p.stderr)
        output=json.loads(p.stdout)
        self.assertEqual(output["status"],
                         "EXECUTED_NEW_LOCAL_SENSOR_WITH_ORIGINAL_MOTIF_POLICY")
        self.assertEqual(output["source_owned_generated_operator"],
                         "GRAFT_GENERATED_NEW_EXECUTABLE_NUMERIC_PROJECTION")
        self.assertEqual(output["final_blind_correct"],4)
        self.assertEqual(len(output["observations"]),4)
        self.assertTrue(output["original_motif_003_policy_determined_by_sensor"])

    def test_compiled_sensor_changes_original_motif_counterfactual_policy(self):
        p=json.loads(self.exec_runner().stdout)
        self.assertTrue(all(x["naive_priority_differs"] for x in p["observations"]))
        self.assertEqual(
            [x["selected_original_003_policy"] for x in p["observations"]],
            ["new-choices","immediate","new-choices","immediate"])
        self.assertEqual(
            {x["generated_sensor_value"] for x in p["observations"]},
            {0,1,3,4})
        self.assertEqual(
            len({(x["recommended_original_003_operator"],
                  tuple(x["recommended_roles"])) for x in p["observations"]}),2)

    def test_strong_classical_same_information_baseline_still_ties(self):
        p=json.loads(self.exec_runner().stdout)
        self.assertTrue(p["fair_classical_selector_would_tie"])
        self.assertFalse(p["new_general_reasoning_algorithm_proven"])
        spec=m.read_doc(self.folder/"manifest.json")
        self.assertFalse(spec["baseline"]["fair_classical_superiority_proven"])
        self.assertEqual(spec["baseline"]["fair_classical_with_same_holdout_correct"],4)

    def test_no_real_world_actions_or_admission(self):
        p=json.loads(self.exec_runner().stdout)
        self.assertEqual(p["real_world_observations"],0)
        self.assertEqual(p["network_requests"],0)
        self.assertEqual(p["external_actions"],0)
        self.assertFalse(p["operator_admitted"])
        self.assertEqual(self.report["repo_writes"],0)
        self.assertFalse(self.report["admission"])

    def test_review_packet_digest_tamper_holds(self):
        fake=copy.deepcopy(self.packet)
        fake["selected_operator"]["selector"]=["advertised","reachable_actions"]
        with self.assertRaisesRegex(m.HOLD,"digest"):
            m.check_receipt(fake)

    def test_even_self_rehashed_false_external_authority_holds(self):
        fake=copy.deepcopy(self.packet)
        fake["authority"]["network"]=True
        body=dict(fake);body.pop("content_sha256")
        fake["content_sha256"]=m.jsdigest(body)
        with self.assertRaises(m.HOLD):
            m.check_receipt(fake)

    def test_self_rehashed_new_source_not_original_graft_holds(self):
        fake=copy.deepcopy(self.packet)
        fake["selected_operator"]["source"]+="\n// fake"
        fake["selected_operator"]["source_sha256"]=m.sha256(
            fake["selected_operator"]["source"].encode()).hexdigest()
        fake["original_graft_eval"]["winner"]["source_sha256"] = fake["selected_operator"]["source_sha256"]
        body=dict(fake);body.pop("content_sha256")
        fake["content_sha256"]=m.jsdigest(body)
        # Rehashing a fabricated source is not proof that GRAFT generated it.
        # The actual builder must independently recompile and REFUSE.
        with tempfile.TemporaryDirectory() as temp:
            pkt = Path(temp) / "self-rehashed-fake-receipt.json"
            pkt.write_text(json.dumps(fake))
            with self.assertRaisesRegex(m.HOLD, "recompilation"):
                m.build(pkt, self.graft, self.motif, Path(temp) / "invalid-build")

    def test_receipt_fake_real_provider_discovery_holds(self):
        fake=copy.deepcopy(self.packet)
        fake["source_packet"]["live_provider_discovered"]=True
        body=dict(fake);body.pop("content_sha256")
        fake["content_sha256"]=m.jsdigest(body)
        with self.assertRaises(m.HOLD):
            m.check_receipt(fake)

    def test_claim_superior_to_classical_holds_even_rehashed(self):
        fake=copy.deepcopy(self.packet)
        fake["independent_final_check"]["superior_to_matched_classical_baseline"]=True
        body=dict(fake);body.pop("content_sha256")
        fake["content_sha256"]=m.jsdigest(body)
        with self.assertRaises(m.HOLD):
            m.check_receipt(fake)

    def test_wrong_owner_revision_is_not_admitted(self):
        with self.assertRaises(m.HOLD):
            m.checked_git_source(m.ROOT,m.MOTIF_SHA,m.PINS_MOTIF)

    def test_cannot_write_over_existing_build(self):
        with self.assertRaisesRegex(m.HOLD,"overwrite"):
            m.build(self.packet_path,self.graft,self.motif,self.folder)

    def test_malicious_generated_code_edit_causes_build_hold(self):
        with tempfile.TemporaryDirectory() as temp:
            copied=Path(temp)/"sensor"
            shutil.copytree(self.folder,copied)
            script=copied/"generated_sensor.mjs"
            script.write_text(script.read_text()+"\n// malicious mutation")
            p=self.exec_runner(copied)
            self.assertNotEqual(p.returncode,0)
            self.assertEqual(json.loads(p.stdout)["stage"],"HOLD")

    def test_manifest_false_grant_cannot_self_authorize(self):
        with tempfile.TemporaryDirectory() as temp:
            copied=Path(temp)/"sensor"
            shutil.copytree(self.folder,copied)
            path=copied/"manifest.json"
            payload=m.read_doc(path)
            payload["authority"]["network"]=True
            body=dict(payload);body.pop("content_sha256")
            payload["content_sha256"]=m.jsdigest(body)
            path.write_text(json.dumps(payload))
            p=self.exec_runner(copied)
            self.assertNotEqual(p.returncode,0)
            self.assertEqual(json.loads(p.stdout)["stage"],"HOLD")

    def test_malformed_reading_causes_hold_instead_of_invented_action(self):
        with tempfile.TemporaryDirectory() as temp:
            copied=Path(temp)/"sensor"
            shutil.copytree(self.folder,copied)
            path=copied/"manifest.json"
            payload=m.read_doc(path)
            payload["final_blind_cases"][0]["response"]["body"]["observed"]["reachable_actions"]="unknown"
            body=dict(payload);body.pop("content_sha256")
            payload["content_sha256"]=m.jsdigest(body)
            path.write_text(json.dumps(payload))
            p=self.exec_runner(copied)
            self.assertNotEqual(p.returncode,0)
            self.assertEqual(json.loads(p.stdout)["stage"],"HOLD")

    def test_receipt_and_build_digests_reproduce(self):
        spec=m.read_doc(self.folder/"manifest.json")
        b=dict(spec);d=b.pop("content_sha256")
        self.assertEqual(m.jsdigest(b),d)
        p=json.loads(self.exec_runner().stdout)
        b=dict(p);d=b.pop("content_sha256")
        self.assertEqual(m.jsdigest(b),d)


if __name__=="__main__":
    unittest.main()
