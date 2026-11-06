"""MOTIF-012: hidden-source, false-positive and source-identity falsification tests."""
from __future__ import annotations
import copy
import json
import os
import shutil
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path
import hidden_source as engine
import world_model as source009

class HiddenSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=Path(os.environ["MOTIF009_QUESTION_DIR"])
        cls.tmp=tempfile.TemporaryDirectory(prefix="motif012-")
        cls.root=Path(cls.tmp.name)
        cls.benchmark=engine.benchmark(cls.source,cls.root/"cases")
        cls.cases={name:source009.read(cls.root/"cases"/name/"inference.json")
          for name in ("HIDDEN_SHARED","INDEPENDENT_CONVERGENCE",
                       "TWO_ACTUAL_CLUSTERS","SIMILAR_WORDING_ONLY",
                       "NO_ORIGIN_EVIDENCE")}
        _,cls.worlds=engine.read_origin_pins(cls.source)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def posterior(self,name):
        return {h:engine.frac(x) for h,x in
            self.cases[name]["source_origin_posterior"].items()}

    def test_replays_original_009_real_png_worlds_and_011_structural_graph(self):
        scene=self.cases["HIDDEN_SHARED"]
        original,worlds=engine.read_origin_pins(self.source)
        self.assertEqual(len(worlds),4)
        self.assertEqual(len({w["start_png_sha256"] for w in worlds}),4)
        self.assertEqual(original["content_sha256"],scene["original_009_question_sha256"])
        self.assertTrue(scene["original_011_source_dependency_mechanism_replayed"])

    def test_five_self_declared_independent_origins_are_not_automatically_believed(self):
        case=self.cases["HIDDEN_SHARED"]
        self.assertEqual(len(case["new_simulated_reports"]),5)
        self.assertTrue(all(r["claims_independent_origin"] for r in case["new_simulated_reports"]))
        self.assertTrue(all(r["synthetic_not_real_testimony"] for r in case["new_simulated_reports"]))
        self.assertTrue(all(r["real_witness_authenticated"] is False for r in case["new_simulated_reports"]))
        self.assertEqual(case["authority"]["actual_people_identified"],0)

    def test_shared_upstream_token_hypothesis_favors_one_origin_under_authored_model(self):
        p=self.posterior("HIDDEN_SHARED")
        self.assertGreater(p["ONE_ORIGIN"],Fraction(19,20))
        self.assertLess(p["INDEPENDENT_FIVE"],Fraction(1,100))
        self.assertLess(p["ONE_ORIGIN"],1)
        self.assertEqual(sum(p.values()),1)

    def test_independently_documented_identical_wording_does_not_get_collapsed(self):
        p=self.posterior("INDEPENDENT_CONVERGENCE")
        self.assertGreater(p["INDEPENDENT_FIVE"],Fraction(19,20))
        self.assertLess(p["ONE_ORIGIN"],Fraction(1,100))
        self.assertEqual(self.cases["INDEPENDENT_CONVERGENCE"]
                         ["no_decision_without_asking"]["action"],"COUNT_FIVE")
        self.assertFalse(self.cases["INDEPENDENT_CONVERGENCE"]
                         ["authority"]["external_source_verified"])

    def test_two_upstream_artifacts_favor_two_clusters_without_claiming_certainty(self):
        p=self.posterior("TWO_ACTUAL_CLUSTERS")
        self.assertGreater(p["TWO_CLUSTERS"],Fraction(19,20))
        self.assertLess(p["TWO_CLUSTERS"],1)
        self.assertEqual(self.cases["TWO_ACTUAL_CLUSTERS"]
                         ["no_decision_without_asking"]["action"],"GROUP_TWO")

    def test_phrase_alone_does_not_prove_copying_or_independence(self):
        p=self.posterior("SIMILAR_WORDING_ONLY")
        self.assertTrue(all(Fraction(1,5)<v<Fraction(1,2) for v in p.values()))
        self.assertEqual(self.cases["SIMILAR_WORDING_ONLY"]
                         ["no_decision_without_asking"]["action"],"HOLD_NO_ORIGIN_CLAIM")

    def test_no_forensic_cue_also_retains_uncertainty(self):
        p=self.posterior("NO_ORIGIN_EVIDENCE")
        self.assertTrue(all(v>0 for v in p.values()))
        self.assertEqual(self.cases["NO_ORIGIN_EVIDENCE"]
                         ["no_decision_without_asking"]["action"],"HOLD_NO_ORIGIN_CLAIM")

    def test_joint_likelihood_keeps_phrase_and_timing_from_counting_twice(self):
        for case in self.cases.values():
            cue=case["joint_cue_evidence"]
            self.assertFalse(cue["phrase_and_timestamp_independently_counted"])
            self.assertFalse(cue["human_identity_confirmed"])
            self.assertFalse(cue["external_authentication_performed"])

    def test_rational_hidden_origin_posteriors_match_independent_classical_enumerator(self):
        for name,case in self.cases.items():
            p=self.posterior(name)
            equivalent=engine.conventional_direct_product(self.worlds,
                case["joint_cue_evidence"]["bundle"])
            self.assertEqual(p,equivalent)
            self.assertTrue(case["independently_enumerated_classical_control_equal"])

    def test_mixture_over_the_four_png_worlds_is_normalized_and_never_certainty(self):
        for case in self.cases.values():
            worlds={k:engine.frac(v) for k,v in case["world_posterior"].items()}
            self.assertEqual(set(worlds),set(engine.WORLD_IDS))
            self.assertEqual(sum(worlds.values()),1)
            self.assertTrue(all(0<v<1 for v in worlds.values()))
            full=sum(v for k,v in worlds.items() if k.endswith("FULL"))
            self.assertEqual(full,engine.frac(case["posterior_wall_full"]))

    def test_naive_count_five_wrongly_overconfident_on_shared_hidden_copy(self):
        hidden=self.cases["HIDDEN_SHARED"]
        latent=engine.frac(hidden["posterior_wall_full"])
        naive=engine.frac(hidden["naive_five_independent_report_posterior_wall_full"])
        self.assertGreater(naive,Fraction(999,1000))
        self.assertGreater(naive,latent)
        self.assertGreater(latent,Fraction(9,10))

    def test_decision_aware_active_question_has_nonnegative_value_of_information(self):
        for case in self.cases.values():
            a=case["question_policy_no_ask_loss"]
            b=case["question_policy_up_to_one_loss"]
            c=case["question_policy_up_to_two_loss"]
            self.assertGreaterEqual(a,b)
            self.assertGreaterEqual(b,c)
            self.assertAlmostEqual(a-c,case["information_value_of_questioning"])

    def test_vague_origin_features_trigger_an_unsent_provenance_question(self):
        case=self.cases["SIMILAR_WORDING_ONLY"]
        self.assertEqual(case["question_policy_up_to_two"]["kind"],"ASK")
        self.assertIn(case["question_policy_up_to_two"]["question_id"],
                      engine.QUESTION_MODELS)
        self.assertFalse(case["question_policy_up_to_two"]["sent_to_human"])

    def test_provenance_question_responses_are_a_proper_conditional_distribution(self):
        for q,item in engine.QUESTION_MODELS.items():
            for i,h in enumerate(engine.HYPOTHESES):
                self.assertEqual(sum(engine.frac(r[i]) for r in
                          item["responses"].values()),1)
            self.assertGreater(engine.frac(item["cost"]),0)

    def test_exact_question_policy_ties_a_distinct_exhaustive_classical_solver(self):
        for case in self.cases.values():
            p=self.posterior(case["fixture"])
            for depth in (0,1,2):
                a,_=engine.active_policy(p,depth)
                b=engine.independent_enumerator(p,depth)
                self.assertEqual(a,b)

    def test_a_rational_answer_updates_origin_posterior_without_creating_a_witness(self):
        belief=self.posterior("SIMILAR_WORDING_ONLY")
        new=engine.update_origin(belief,"ASK_ORIGINAL_ARTIFACTS","five_receipts")
        self.assertGreater(new["INDEPENDENT_FIVE"],belief["INDEPENDENT_FIVE"])
        self.assertEqual(sum(new.values()),1)

    def test_modal_oracle_path_is_explicitly_simulated_not_an_observation(self):
        for name in ("HIDDEN_SHARED","INDEPENDENT_CONVERGENCE","TWO_ACTUAL_CLUSTERS"):
            trace=self.cases[name]["synthetic_modal_oracle_path"]
            self.assertTrue(trace["not_a_real_observation"])
            self.assertFalse(any(t["human_contacted"] for t in trace["synthetic_modal_path"]))
            self.assertFalse(any(t["response_was_observed"] for t in trace["synthetic_modal_path"]))

    def test_all_five_cases_use_balanced_control_with_no_external_actions(self):
        self.assertEqual(len(self.benchmark["cases"]),5)
        self.assertTrue(self.benchmark["independent_and_hidden_shared_controls_both_present"])
        self.assertTrue(self.benchmark["matched_classical_latent_model_and_question_tree_equal"])
        self.assertFalse(self.benchmark["real_source_independence_proven"])
        self.assertEqual(self.benchmark["total_human_contacts"],0)
        self.assertEqual(self.benchmark["total_real_actions"],0)

    def test_missing_report_is_refused_without_extrapolating_to_new_witness(self):
        rs=[engine.report(i) for i in range(1,5)]
        with self.assertRaises(engine.HOLD):engine.verify_fixture(rs,engine.cue("NO_CUE"))

    def test_report_claim_forged_real_witness_even_with_a_new_digest_is_refused(self):
        rs=[engine.report(i) for i in range(1,6)]
        rs[0]["real_witness_authenticated"]=True
        body=dict(rs[0]);body.pop("content_sha256")
        rs[0]["content_sha256"]=engine.digest(body)
        with self.assertRaises(engine.HOLD):engine.verify_fixture(rs,engine.cue("NO_CUE"))

    def test_changed_upstream_receipt_not_evidence_of_real_independence(self):
        clue=engine.cue("INDEPENDENT_CAPTURE_AUDIT")
        clue["external_authentication_performed"]=True
        body=dict(clue);body.pop("content_sha256")
        clue["content_sha256"]=engine.digest(body)
        with self.assertRaises(engine.HOLD):
            engine.verify_fixture([engine.report(i) for i in range(1,6)],clue)

    def test_source_cue_cannot_rewrite_authored_likelihood_table_by_rehashing(self):
        clue=engine.cue("SHARED_UPSTREAM_TOKEN")
        clue["joint_cue_likelihoods"]["ONE_ORIGIN"]="999/1000"
        body=dict(clue);body.pop("content_sha256")
        clue["content_sha256"]=engine.digest(body)
        with self.assertRaises(engine.HOLD):
            engine.verify_fixture([engine.report(i) for i in range(1,6)],clue)

    def test_fraudulent_byte_tampering_of_an_original_009_png_holds(self):
        with tempfile.TemporaryDirectory() as t:
            copied=Path(t)/"question"
            shutil.copytree(self.source,copied)
            file=copied/"worlds"/"LEFT_FULL"/"start.png"
            file.write_bytes(file.read_bytes()+b"changed")
            with self.assertRaises(source009.HOLD):
                engine.read_origin_pins(copied)

    def test_unknown_origin_option_is_not_silently_added_to_posterior(self):
        with self.assertRaises(engine.HOLD):
            engine.scene("SECRET_GROUP_UNKNOWN")
        with self.assertRaises(engine.HOLD):
            engine.update_origin(engine.probability_prior(),
                                 "ASK_THIRD_PARTY","independent")
        with self.assertRaises(engine.HOLD):
            engine.active_policy(engine.probability_prior(),17)

    def test_every_original_report_and_assumption_is_retained_in_hashed_ledger(self):
        for case in self.cases.values():
            before=case["original_009_question_sha256"]
            for i,row in enumerate(case["evidence_ledger"],1):
                self.assertEqual(row["previous_sha256"],before)
                self.assertEqual(row["report_sha256"],row["report"]["content_sha256"])
                body=dict(row);before=body.pop("content_sha256")
                self.assertEqual(engine.digest(body),before)
                self.assertEqual(row["sequence"],i)
            self.assertEqual(before,case["last_receipt_sha256"])
            self.assertTrue(case["assumptions"]["latent_partition_options_restricted_to_one_two_five"])

    def test_world_model_cannot_be_claimed_authoritative_or_real(self):
        for case in self.cases.values():
            x=case["authority"]
            self.assertEqual(x["actual_people_identified"],0)
            self.assertEqual(x["real_reporters_contacted"],0)
            self.assertFalse(x["actual_question_sent"])
            self.assertFalse(x["external_source_verified"])
            self.assertEqual(x["real_world_images_observed"],0)
            self.assertEqual(x["actions_executed"],0)
            self.assertFalse(x["auto_admitted"])

    def test_source_packet_digest_preserved_even_for_an_unhelpful_case(self):
        p=self.cases["NO_ORIGIN_EVIDENCE"]
        body=dict(p);claim=body.pop("content_sha256")
        self.assertEqual(engine.digest(body),claim)
        body=dict(self.benchmark);claim=body.pop("content_sha256")
        self.assertEqual(engine.digest(body),claim)

    def test_existing_output_never_overwritten_even_when_rerun(self):
        with self.assertRaises(engine.HOLD):
            engine.run_case(self.source,"HIDDEN_SHARED",self.root/"cases"/"HIDDEN_SHARED")
        with self.assertRaises(engine.HOLD):
            engine.benchmark(self.source,self.root/"cases")

if __name__=="__main__":
    unittest.main()
