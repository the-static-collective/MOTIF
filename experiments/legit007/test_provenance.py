"""LEGIT-007 adverse provenance, source reliability and VOI falsifiers."""
from __future__ import annotations

from copy import deepcopy
import math
import unittest

from provenance import (HOLD,validate,posterior,route,terminal,
                        audit_distribution,evaluate_audit)
from simulator import demonstration,trial,N
from benchmark import vote,evaluate_trial,run
from exact_reference import reference
from bridge_013 import compare_013

class AdversarialWitnessTests(unittest.TestCase):
    def setUp(self):
        self.packet=demonstration()

    def test_nine_positive_voices_are_only_one_root(self):
        r=route(self.packet)
        self.assertEqual((r["report_nodes"],
                          r["distinct_declared_upstream_origins"],
                          r["duplicate_or_forwarded_report_nodes"]),(11,3,8))
        self.assertEqual(vote([x["claim"] for x in self.packet["nodes"]]),"PREDICT_TRUE")
        self.assertEqual(vote([x["claim"] for x in self.packet["nodes"] if x["kind"]=="ROOT"]),"PREDICT_FALSE")
        self.assertLess(r["posterior_true_given_declared_calibration"],.5)

    def test_deleting_copies_keeps_posterior(self):
        a=posterior(self.packet)
        x=deepcopy(self.packet)
        x["nodes"]=[z for z in x["nodes"] if z["kind"]=="ROOT"]
        b=posterior(x)
        self.assertAlmostEqual(a["posterior"],b["posterior"],places=14)
        self.assertEqual((a["echoes"],b["echoes"]),(8,0))

    def test_reverse_graph_order_no_effect(self):
        x=deepcopy(self.packet)
        x["nodes"].reverse()
        self.assertEqual(posterior(x)["origin_signature"],
                         posterior(self.packet)["origin_signature"])
        self.assertAlmostEqual(posterior(x)["posterior"],
                               posterior(self.packet)["posterior"],places=14)

    def test_deep_copy_chain_resolves_initial_root(self):
        x=trial(1).public
        graph=validate(x)
        self.assertEqual(len(graph["resolved"]),len(x["nodes"]))
        for node in x["nodes"]:
            if node["kind"]=="COPY":
                root=graph["by_id"][graph["resolved"][node["id"]]]
                self.assertEqual(root["kind"],"ROOT")
                self.assertEqual(root["claim"],node["claim"])

    def test_duplicate_alias_same_origin_is_one_vote(self):
        x=deepcopy(self.packet)
        same=deepcopy(x["nodes"][0])
        same["id"]="alias"
        x["nodes"].append(same)
        self.assertAlmostEqual(posterior(x)["posterior"],
                               posterior(self.packet)["posterior"],places=14)
        self.assertEqual(posterior(x)["echoes"],9)

    def test_equivocation_same_root_holds(self):
        x=deepcopy(self.packet)
        same=deepcopy(x["nodes"][0])
        same["id"]="alias"
        same["claim"]=not same["claim"]
        x["nodes"].append(same)
        self.assertEqual(route(x)["status"],"HOLD_INPUT")

    def test_unknown_ancestor_holds_and_proposes_verification(self):
        x=deepcopy(self.packet)
        x["nodes"][1]["parent"]="lost_source"
        r=route(x)
        self.assertEqual(r["status"],"HOLD_INPUT")
        self.assertEqual(r["suggested_investigation"],
                         "VERIFY_UPSTREAM_LINEAGE_UNSENT")
        self.assertFalse(r["investigation_issued"])

    def test_unresolved_lineage_holds_and_proposes_verification(self):
        x=deepcopy(self.packet)
        x["nodes"].append({"id":"mystery","kind":"LINEAGE_UNKNOWN",
                           "parent":None,"claim":False,"origin":None,"channel":None})
        r=route(x)
        self.assertEqual(r["status"],"HOLD_INPUT")
        self.assertEqual(r["suggested_investigation"],
                         "VERIFY_UPSTREAM_LINEAGE_UNSENT")

    def test_false_copy_tampering_holds(self):
        x=deepcopy(self.packet)
        x["nodes"][1]["claim"]=not x["nodes"][1]["claim"]
        self.assertEqual(route(x)["status"],"HOLD_INPUT")

    def test_provenance_cycle_holds(self):
        x=deepcopy(self.packet)
        x["nodes"][1]["parent"]=x["nodes"][1]["id"]
        self.assertIn("Circular",route(x)["reason"])

    def test_forged_multiparent_synthesis_holds(self):
        x=deepcopy(self.packet)
        x["nodes"][1]["parent"]=["p0","n0"]
        self.assertEqual(route(x)["status"],"HOLD_INPUT")

    def test_declared_identity_is_not_authentication(self):
        r=route(self.packet)
        self.assertFalse(r["source_identity_cryptographically_authenticated"])
        self.assertFalse(r["conditional_independence_empirically_validated"])
        self.assertTrue(r["uncalibrated_real_world_trust"])
        self.assertFalse(r["world_actuated"])
        self.assertFalse(r["real_world_authority"])

    def test_renamed_copy_as_fake_independent_source_is_still_undetectable(self):
        x=deepcopy(self.packet)
        fake=deepcopy(x["nodes"][0])
        fake["id"]="forged_source"
        fake["origin"]="invented_root"
        x["nodes"].append(fake)
        self.assertNotAlmostEqual(posterior(x)["posterior"],
                                  posterior(self.packet)["posterior"],places=8)
        self.assertFalse(route(x)["source_identity_cryptographically_authenticated"])

    def test_missing_independent_calibration_holds(self):
        x=deepcopy(self.packet)
        x["calibration"]=[r for r in x["calibration"]
                          if r["channel"]!="noisy"]
        self.assertEqual(route(x)["status"],"HOLD_INPUT")

    def test_real_world_source_provenance_not_implicitly_accepted(self):
        x=deepcopy(self.packet)
        x["calibration"][0]["provenance"]="SELF_ATTESTED"
        self.assertEqual(route(x)["status"],"HOLD_INPUT")

    def test_bad_source_calibration_counts_fail_closed(self):
        for bad in (-1,10001,True,4.2):
            x=deepcopy(self.packet)
            x["calibration"][0]["correct"]=bad
            self.assertEqual(route(x)["status"],"HOLD_INPUT")

    def test_bad_audit_cost_and_accuracy_fail_closed(self):
        for key,value in (("cost",-1),("cost",float("nan")),
                          ("accuracy",1.0),("accuracy",.5)):
            x=deepcopy(self.packet)
            x["audits"][0][key]=value
            self.assertEqual(route(x)["status"],"HOLD_INPUT")

    def test_live_authority_and_hidden_truth_fields_rejected(self):
        x=deepcopy(self.packet)
        x["scope"]="LIVE_PATIENT_DECISION"
        self.assertEqual(route(x)["status"],"HOLD_INPUT")
        x=deepcopy(self.packet)
        x["truth"]=True
        self.assertEqual(route(x)["status"],"HOLD_INPUT")

    def test_contrarian_calibrated_source_can_reverse_testimony(self):
        r=posterior(trial(2).public)
        c=next(x for x in r["contributions"] if x["channel"]=="contrarian")
        self.assertLess(c["reliability_mean"],.5)
        self.assertEqual(math.copysign(1,c["signed_log_odds"]),
                         -1 if c["claim"] else 1)

    def test_cost_of_not_auditing_is_explicit(self):
        self.assertEqual(terminal(.5)[0],"ABSTAIN")
        q={"id":"check","accuracy":.90,"cost":.11}
        result=evaluate_audit(.5,q)
        self.assertAlmostEqual(result["expected_total_risk"],.21,places=8)
        self.assertLess(result["expected_total_risk"],.27)
        self.assertEqual(len(result["outcomes"]),2)

    def test_expensive_audit_not_executed(self):
        x=deepcopy(self.packet)
        x["audits"][0]["cost"]=.95
        x["audits"][1]["cost"]=.95
        result=route(x)
        self.assertIsNone(result["proposal"])
        self.assertNotEqual(result["decision"],"ASK_SYNTHETIC_AUDIT")

    def test_audit_conditional_probability_conserves_prior(self):
        for p in (.1,.5,.73,.99):
            dist=audit_distribution(p,.87)
            self.assertAlmostEqual(sum(row[1] for row in dist),1,places=14)
            self.assertAlmostEqual(sum(row[1]*row[2] for row in dist),
                                   p,places=12)

    def test_empty_audit_menu_still_holds_no_real_execution(self):
        x=deepcopy(self.packet)
        x["audits"]=[]
        result=route(x)
        self.assertEqual(result["status"],"TERMINAL_RESEARCH_HOLD")
        self.assertIsNone(result["proposal"])

    def test_hidden_state_excluded_from_public_trial(self):
        t=trial(0)
        self.assertNotIn("truth",t.public)
        self.assertNotIn("audit_outcomes",t.public)
        self.assertIs(type(t.truth),bool)

    def test_all_320_cases_match_strong_independent_classical_bayes(self):
        for i in range(N):
            report=evaluate_trial(trial(i))
            self.assertTrue(report["classical_exact_tie"])
            self.assertFalse(report["correct_world_state_revealed_to_router"])

    def test_existing_motif013_actual_witness_likelihood_regression(self):
        r=compare_013(self.packet)
        self.assertTrue(r["match_to_12_decimals"])
        self.assertFalse(r["independent_baseline"])
        self.assertFalse(r["source_identity_authenticated"])

    def test_full_benchmark_retains_matched_classical_tie(self):
        r=run()
        self.assertEqual(r,run())
        self.assertEqual(r["cases"],320)
        self.assertFalse(r["source_identity_verified"])
        self.assertFalse(r["classical_bayes_superiority_claim"])
        self.assertFalse(r["external_actions_taken"])
        self.assertEqual(r["policies"]["lineage_router_with_unsent_audit"],
                         r["policies"]["independent_classical_exact_bayes_voi"])
        self.assertGreater(r["policies"]["raw_report_majority"]["mean_realized_loss"],
                           r["policies"]["lineage_router_with_unsent_audit"]["mean_realized_loss"])
        self.assertEqual(r["demonstration_nine_reports_one_origin"]["forwarded_or_duplicate"],8)

    def test_all_audits_are_unexecuted_proposals(self):
        for i in range(N):
            x=route(trial(i).public)
            self.assertFalse(x["world_actuated"])
            if x["proposal"]:
                self.assertFalse(x["proposal"]["issued"])

if __name__=="__main__":
    unittest.main()
