"""LEGIT-008: source trust, mathematical parity and strategy generation tests."""
from __future__ import annotations

from copy import deepcopy
import math
import unittest

from custody import HOLD,seal_simulated,verify,guarded,sha
from planner import plan,decide,rollout
from strong_reference import exhaustive,simulate
from synthesis import synthesize,selected_plan,TRAIN_SAMPLES,GRAMMAR,features
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from benchmark import benchmark
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"legit007"))
from simulator import demonstration,trial,N
from provenance import posterior,route as previous_route


class ProofCarryingStrategyTests(unittest.TestCase):
    def setUp(self):
        self.sample=demonstration()
        self.pins=seal_simulated(self.sample)

    def test_sealed_source_demo_is_structurally_sound(self):
        r=verify(self.sample,self.pins)
        self.assertEqual(r["root_count"],3)
        self.assertEqual(r["copy_nodes"],8)
        self.assertEqual(r["provenance_chain_nodes_checked"],11)
        self.assertTrue(r["source_integrity_relative_to_pins"])
        self.assertFalse(r["origin_identity_authenticated"])
        self.assertFalse(r["pinned_manifest_signature_verified"])

    def test_unchanged_parent_child_permutation_matches(self):
        x=deepcopy(self.sample)
        x["nodes"].reverse()
        r=verify(x,self.pins)
        self.assertEqual(r["root_count"],3)
        self.assertEqual(r["copy_nodes"],8)

    def test_attack_fake_independent_root_blocked(self):
        packet=deepcopy(self.sample)
        fake=deepcopy(packet["nodes"][0])
        fake["id"]="forged"
        fake["origin"]="independent_new_origin"
        packet["nodes"].append(fake)
        self.assertEqual(guarded(packet,self.pins)["status"],
                         "HOLD_UNTRUSTED_CUSTODY")
        self.assertNotEqual(posterior(packet)["posterior"],
                            posterior(self.sample)["posterior"])

    def test_deleted_origin_blocked(self):
        x=deepcopy(self.sample)
        x["nodes"]=[r for r in x["nodes"] if r["id"] not in ("n0",)]
        self.assertEqual(guarded(x,self.pins)["status"],
                         "HOLD_UNTRUSTED_CUSTODY")

    def test_altered_source_observation_blocked(self):
        x=deepcopy(self.sample)
        root=next(r for r in x["nodes"] if r["id"]=="n0")
        root["claim"]=True
        self.assertEqual(guarded(x,self.pins)["status"],
                         "HOLD_UNTRUSTED_CUSTODY")

    def test_forged_calibration_blocked(self):
        x=deepcopy(self.sample)
        x["calibration"][0]["correct"]+=1
        self.assertEqual(guarded(x,self.pins)["status"],
                         "HOLD_UNTRUSTED_CUSTODY")

    def test_fake_new_audit_accuracy_blocked(self):
        x=deepcopy(self.sample)
        x["audits"][0]["accuracy"]=.999
        self.assertEqual(guarded(x,self.pins)["status"],
                         "HOLD_UNTRUSTED_CUSTODY")

    def test_pin_manifest_tamper_blocked(self):
        x=deepcopy(self.pins)
        x["root_commitments"]["review_a"]="f"*64
        self.assertEqual(guarded(self.sample,x)["status"],
                         "HOLD_UNTRUSTED_CUSTODY")

    def test_self_resigned_manifest_does_not_prove_real_identity(self):
        x=deepcopy(self.sample)
        x["nodes"][0]["origin"]="made_up_identity"
        forged_pins=seal_simulated(x)
        receipt=verify(x,forged_pins)
        self.assertFalse(receipt["origin_identity_authenticated"])
        self.assertFalse(receipt["pinned_manifest_signature_verified"])
        # Demonstrates that WITH control of both data and pins, an attacker
        # can generate a newly consistent (but unauthenticated) record.
        self.assertTrue(receipt["source_integrity_relative_to_pins"])

    def test_unknown_lineage_still_holds(self):
        x=deepcopy(self.sample)
        x["nodes"][1]["parent"]="not_known"
        self.assertEqual(guarded(x,self.pins)["status"],
                         "HOLD_UNTRUSTED_CUSTODY")

    def test_depth_zero_stops(self):
        p=posterior(self.sample)["posterior"]
        r=plan(p,self.sample["audits"],0)
        self.assertEqual(r["tree"]["action"],"ABSTAIN" if
                         abs(p-.5)<.23 else ("PREDICT_TRUE" if p>.5 else "PREDICT_FALSE"))
        self.assertEqual(r["states_visited"],1)

    def test_two_step_exact_weakly_dominates_one_step_in_expectation(self):
        for i in range(0,N,7):
            packet=trial(i).public
            p=posterior(packet)["posterior"]
            a=plan(p,packet["audits"],1)
            b=plan(p,packet["audits"],2)
            self.assertLessEqual(b["tree"]["expected_risk"],
                                 a["tree"]["expected_risk"]+1e-12)
            self.assertGreaterEqual(b["states_visited"],a["states_visited"])

    def test_two_step_matches_independent_strong_classical_exact(self):
        for i in range(N):
            packet=trial(i).public
            b=plan(posterior(packet)["posterior"],packet["audits"],2)
            ref=exhaustive(packet)
            self.assertAlmostEqual(b["tree"]["expected_risk"],
                                   ref["expected_risk"],places=10)
            self.assertEqual(b["tree"]["action"],ref["root"]["kind"])

    def test_no_second_audit_repeated_on_same_path(self):
        for i in (0,19,32,99,161,222,319):
            t=trial(i)
            b=plan(posterior(t.public)["posterior"],t.public["audits"],2)
            out=rollout(b["tree"],t.audit_outcomes,t.truth)
            self.assertLessEqual(out["audits_simulated"],2)
            self.assertEqual(len({a["audit_id"] for a in out["path"]}),
                             len(out["path"]))

    def test_two_step_leaves_old_one_step_unchanged(self):
        for i in range(0,N,9):
            packet=trial(i).public
            b=plan(posterior(packet)["posterior"],packet["audits"],1)
            old=previous_route(packet)
            self.assertAlmostEqual(b["tree"]["expected_risk"],
                                   old["selected_expected_total_risk"],
                                   delta=1e-8)

    def test_strong_classical_rollout_same_hidden_world(self):
        for i in range(0,N,13):
            t=trial(i)
            r=exhaustive(t.public)
            a=plan(posterior(t.public)["posterior"],t.public["audits"],2)
            x=rollout(a["tree"],t.audit_outcomes,t.truth)
            y=simulate(r["root"],t.audit_outcomes,t.truth,
                       {j["id"]:j["cost"] for j in t.public["audits"]})
            self.assertAlmostEqual(x["loss"],y[0],places=12)
            self.assertEqual(x["audits_simulated"],y[1])

    def test_no_actual_audit_dispatched(self):
        r=decide(self.sample,self.pins,2)
        self.assertEqual(r["audits_dispatched"],0)
        self.assertFalse(r["real_world_authority"])
        self.assertFalse(r["claimed_novel_math"])
        self.assertEqual(r["status"],"RESEARCH_PROPOSAL_ONLY")

    def test_unpinned_source_is_not_planned(self):
        x=deepcopy(self.sample)
        x["audits"][0]["cost"]+=.1
        result=decide(x,self.pins)
        self.assertIsNone(result["policy"])
        self.assertEqual(result["status"],"HOLD_UNTRUSTED_CUSTODY")

    def test_training_has_no_world_or_outcome_labels(self):
        packets=[trial(i).public for i in range(TRAIN_SAMPLES)]
        self.assertTrue(all("truth" not in x and
                            "audit_outcomes" not in x for x in packets))
        strategy=synthesize(packets)
        self.assertFalse(strategy["used_hidden_outcomes"])
        self.assertEqual(strategy["train_count"],160)
        self.assertEqual(strategy["candidate_count"],len(GRAMMAR))

    def test_training_attempt_to_inject_hidden_truth_fails(self):
        packets=[trial(i).public for i in range(TRAIN_SAMPLES)]
        packets[0]=dict(packets[0],truth=True)
        with self.assertRaises(ValueError):
            synthesize(packets)

    def test_train_recipe_only_comes_from_registered_grammar(self):
        packets=[trial(i).public for i in range(TRAIN_SAMPLES)]
        strategy=synthesize(packets)
        row=strategy["recipe"]
        self.assertIn((row["kind"],row["threshold"]),GRAMMAR)
        p=trial(300).public
        result=selected_plan(p,strategy)
        self.assertIn(result["depth"],(1,2))
        self.assertFalse(result["real_world_authority"])

    def test_unknown_strategy_cannot_promote_algorithm(self):
        packets=[trial(i).public for i in range(TRAIN_SAMPLES)]
        strategy=synthesize(packets)
        strategy["recipe"]["kind"]="FREE_UNRESTRICTED_SAT_INVENTION"
        with self.assertRaises(ValueError):
            selected_plan(trial(299).public,strategy)

    def test_full_frozen_heldout_and_classical_tie(self):
        r=benchmark()
        self.assertEqual(r,benchmark())
        self.assertEqual(r["train_public_packets"],160)
        self.assertEqual(r["heldout_cases"],160)
        self.assertEqual(r["audits_dispatched"],0)
        self.assertFalse(r["claim_to_surpass_classical_mathematics"])
        self.assertFalse(r["source_pin_trust_externally_verified"])
        self.assertEqual(
            r["policies"]["fixed_two_step"]["realized_loss_mean"],
            r["policies"]["independent_exact_classical_two_step"]["realized_loss_mean"])
        self.assertLessEqual(
            r["policies"]["fixed_two_step"]["conditional_expected_risk_mean"],
            r["policies"]["fixed_one_step"]["conditional_expected_risk_mean"])

if __name__=="__main__":
    unittest.main()
