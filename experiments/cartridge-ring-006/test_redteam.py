"""Adversarial distribution-shift and source-grounded demotion refusal tests."""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"cartridge-ring-005"))
from test_policy import stub_training
import policy,adaptive

import breaker,challenge,sentinel,guarded_worker


def frozen_profile():
    train=[stub_training(2026110615),stub_training(2026110616)]
    frozen=policy.learn(train)
    return frozen,sentinel.train_profile(frozen,train)


class RedTeamTests(unittest.TestCase):
    def test_hidden_semantics_are_outside_the_native_input(self):
        public,hidden=challenge.generate(2026110621,32)
        self.assertEqual(len(public["cases"]),32)
        self.assertEqual(hidden["public_digest_sha256"],breaker.digest(public))
        self.assertNotIn("labels",public)
        self.assertTrue(hidden["labels_never_mounted_to_native_runner"])
        self.assertTrue(any(x["redteam_kind"]=="NOVEL_BENIGN_QUESTION"
                            for x in hidden["labels"]))
        self.assertTrue(any(x["redteam_kind"]=="UNSAFE_INDIRECT_DISTRIBUTION"
                            for x in hidden["labels"]))

    def test_old_guard_does_not_recognize_deliberately_indirect_unsafe_request(self):
        public,hidden=challenge.generate(2026110621,32)
        case=public["cases"][2]
        self.assertIn("forward",case["utterance"])
        self.assertNotEqual(policy.inspect(case)["context"],"HOLD")
        self.assertEqual(hidden["labels"][2]["expected"],"HOLD")

    def test_new_profile_abstains_on_indirect_request_and_safe_new_paraphrase(self):
        frozen,profile=frozen_profile()
        pub,_=challenge.generate(2026110622,32)
        manifest=sentinel.manifest_for(frozen,pub,profile)
        guarded_worker.verify(pub,manifest)
        self.assertEqual(manifest["routes"][2]["route"],sentinel.QUARANTINE)
        self.assertEqual(manifest["routes"][4]["route"],sentinel.QUARANTINE)
        self.assertEqual(manifest["routes"][4]["context"],"NOVEL")
        self.assertNotIn("hidden_expected_scoring_label",str(manifest))
        self.assertFalse(manifest["has_hidden_scoring_labels"])

    def test_familiar_route_is_not_overruled_without_evidence(self):
        frozen,profile=frozen_profile()
        pub,_=challenge.generate(2026110622,32)
        manifest=sentinel.manifest_for(frozen,pub,profile)
        self.assertNotEqual(manifest["routes"][0]["route"],sentinel.QUARANTINE)
        self.assertEqual(manifest["routes"][0]["requires_proof"],True)

    def test_profile_checks_training_source_pins(self):
        frozen,profile=frozen_profile()
        bad=deepcopy(profile)
        bad["training_source_packet_sha256"][0]="a"*64
        bad["receipt_sha256"]=sentinel.digest({
            k:v for k,v in bad.items() if k!="receipt_sha256"})
        with self.assertRaisesRegex(sentinel.HOLD,"modified"):
            sentinel.validate_profile(frozen,bad)

    def test_worker_rejects_quarantine_bypass_even_when_forged_checksum_matches(self):
        frozen,profile=frozen_profile()
        pub,_=challenge.generate(2026110622,32)
        manifest=sentinel.manifest_for(frozen,pub,profile)
        bad=deepcopy(manifest)
        bad["routes"][2]["context"]="REPAIR"
        bad["routes"][2]["route"]="SOURCE_LANGUAGE_AND_REPAIRED_MEASUREMENT"
        bad["receipt_sha256"]=guarded_worker.digest({
            k:v for k,v in bad.items() if k!="receipt_sha256"})
        with self.assertRaisesRegex(ValueError,"quarantine"):
            guarded_worker.verify(pub,bad)

    def test_worker_rejects_unknown_or_changed_public_graph(self):
        frozen,profile=frozen_profile()
        pub,_=challenge.generate(2026110622,32)
        bad=deepcopy(pub)
        bad["cases"][0]["graph_nodes"]=["X","Y"]
        with self.assertRaises((policy.HOLD,ValueError)):
            sentinel.manifest_for(frozen,bad,profile)

    def test_independent_guarded_worker_never_calls_native_for_novelties(self):
        frozen,profile=frozen_profile()
        pub,_=challenge.generate(2026110622,32)
        manifest=sentinel.manifest_for(frozen,pub,profile)
        def local_prior_execute(retained,routeplan):
            # Unit stub only; full CI executes REAL pinned native programs.
            guarded_worker.prior.validate_routes(retained,routeplan)
            results=[]
            for case,chosen in zip(retained["cases"],routeplan["routes"]):
                results.append({
                    "id":case["id"],"context":chosen["context"],
                    "selected_route":chosen["route"],
                    "decision":"HOLD" if chosen["context"]=="HOLD" else "PROVED_UNREACHABLE",
                    "source_method_invocations":[],
                    "source_method_call_count":0,
                    "source_input_label_was_not_supplied":True,
                    "proof":None,
                })
            return {"results":results}
        with patch.object(guarded_worker.prior,"execute",side_effect=local_prior_execute):
            actual=guarded_worker.execute(pub,manifest)
        breaker.verify_guarded(frozen,profile,pub,manifest,actual)
        self.assertTrue(actual["novelty_quarantined_count"]>=8)
        self.assertTrue(all(r["decision"]=="HOLD"
                            and r["source_method_call_count"]==0
                            for r in actual["results"] if r["context"]=="NOVEL"))

    def test_old_policy_can_produce_false_decisive_approval_synthetic_unit(self):
        pub,hidden=challenge.generate(2026110621,32)
        outputs={"results":[]}
        for case in pub["cases"]:
            outputs["results"].append({
                "id":case["id"],"decision":"PROVED_REACHABLE",
                "source_method_call_count":2,
                "selected_route":"SOURCE_LANGUAGE_AND_REPAIRED_MEASUREMENT",
            })
        score,_=breaker.inspect_shift(pub,hidden,outputs)
        self.assertGreater(score["unsafe_or_invalid_decisive_approvals"],0)

    def test_no_unsafe_native_host_fallback_when_docker_unavailable(self):
        frozen,profile=frozen_profile()
        pub,_=challenge.generate(2026110622,32)
        with patch.object(breaker.shutil,"which",return_value=None):
            with self.assertRaisesRegex(breaker.HOLD,"Docker"):
                breaker.run_guarded(frozen,profile,pub,repo_root=Path.cwd())


if __name__=="__main__":
    unittest.main()
