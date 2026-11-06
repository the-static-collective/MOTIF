"""MOTIF-011: provenance graph adversarial, dependency and classical controls."""
import copy
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from fractions import Fraction

import source_graph as graph
import world_model as prior

class EvidenceFrontierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.question=Path(os.environ["MOTIF009_QUESTION_DIR"])
        cls.tmp=tempfile.TemporaryDirectory(prefix="motif011-")
        cls.home=Path(cls.tmp.name)
        cls.summary=graph.benchmark(cls.question,cls.home/"benchmark")
        cls.partial=prior.read(cls.home/"benchmark"/"LEFT_PARTIAL"/"replay.json")
        cls.full=prior.read(cls.home/"benchmark"/"RIGHT_FULL"/"replay.json")
        _,cls.worlds=prior.verify_original(cls.question)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_original_model_contains_four_real_source_checked_pngs(self):
        packet,worlds=prior.verify_original(self.question)
        self.assertEqual(len(worlds),4)
        self.assertEqual(len(set(w["start_png_sha256"] for w in worlds)),4)
        self.assertEqual(self.partial["original_009_source_sha256"],
                         packet["content_sha256"])

    def test_one_wrong_root_and_six_copies_count_as_one_evidence_factor(self):
        steps=self.partial["steps"]
        self.assertEqual(len(steps),10)
        self.assertEqual(self.partial["independent_roots_count"],4)
        self.assertEqual(self.partial["derived_retransmissions_ignored_as_new_likelihoods"],6)
        original=steps[0]["posterior"]
        for step in steps[1:7]:
            self.assertFalse(step["contributed_independent_factor"])
            self.assertEqual(step["posterior"],original)
            self.assertNotEqual(step["naive_as_if_independent_posterior"],
                                original)

    def test_independently_declared_counterevidence_changes_beliefs(self):
        a=self.partial["steps"]
        self.assertNotEqual(a[6]["posterior"],a[7]["posterior"])
        self.assertNotEqual(a[7]["posterior"],a[8]["posterior"])
        self.assertNotEqual(a[8]["posterior"],a[9]["posterior"])
        self.assertTrue(a[7]["contributed_independent_factor"])
        self.assertTrue(a[8]["contributed_independent_factor"])
        self.assertTrue(a[9]["contributed_independent_factor"])

    def test_conflicting_witness_roots_are_not_deleted(self):
        ledger=self.partial["conflict_ledger"]
        self.assertTrue(ledger["independent_roots_contradict"])
        self.assertEqual(ledger["opposing_roots_preserved"],
                         ["R001","R008","R009","R010"])
        self.assertFalse(ledger["actual_independence_attested"])

    def test_independent_classical_product_matches_each_root_posterior(self):
        roots={}
        for step in self.partial["steps"]:
            if step["contributed_independent_factor"]:
                r=step["report"]
                roots[r["origin_id"]]=r
            expected=graph.source_posterior(roots,self.worlds)
            actual=prior.typed_weights(step["posterior"])
            self.assertEqual(actual,expected)

    def test_replication_exaggerates_the_initial_wrong_rumor(self):
        result=self.partial["scoring"]
        self.assertAlmostEqual(result["frozen_true_extent_probability"],.2)
        self.assertAlmostEqual(result["grouped_true_extent_probability"],.8)
        self.assertLess(result["naive_true_extent_probability"],.002)
        self.assertLess(result["grouped_brier"],result["naive_brier"])

    def test_opposite_full_world_also_resists_false_repetition(self):
        score=self.full["scoring"]
        self.assertGreater(score["grouped_true_extent_probability"],.98)
        self.assertLess(score["naive_true_extent_probability"],.02)
        self.assertLess(score["grouped_brier"],score["naive_brier"])

    def test_all_four_synthetic_truths_better_than_naive_copy_counting(self):
        self.assertEqual(len(self.summary["cases"]),4)
        self.assertTrue(self.summary["grouped_beats_naive_in_all_designed_cases"])
        self.assertLess(self.summary["mean_grouped_brier"],.03)
        self.assertGreater(self.summary["mean_naive_brier"],.9)
        self.assertLess(self.summary["mean_grouped_decision_regret"],
                        self.summary["mean_naive_decision_regret"])

    def test_actual_decisions_never_executed_when_posterior_changes(self):
        p=self.partial
        self.assertEqual(p["decision"]["source_grouped"],"HOLD_NO_ACTION")
        self.assertEqual(p["decision"]["naive_copy_counterexample"],
                         "DECLARE_UNREACHABLE")
        self.assertEqual(p["decision"]["grouped_simulated_regret"],2.)
        self.assertEqual(p["decision"]["naive_simulated_regret"],5.)
        self.assertFalse(p["decision"]["real_actions_executed"])

    def test_next_question_recomputed_each_provenance_change_but_never_sent(self):
        for record in self.partial["steps"]:
            self.assertIn(record["next_question_proposed_but_unsent"],
                          (None,*prior.classical.QUESTIONS))
            self.assertEqual(record["human_observations"],0)
            self.assertEqual(record["physical_actions"],0)
        self.assertEqual(self.partial["authority"]["real_human_reports_received"],0)

    def test_append_only_chain_records_every_duplicate_and_opposing_root(self):
        previous=self.partial["original_009_source_sha256"]
        for i,row in enumerate(self.partial["steps"],1):
            self.assertEqual(row["previous_receipt_sha256"],previous)
            self.assertEqual(row["sequence"],i)
            body=dict(row)
            previous=body.pop("content_sha256")
            self.assertEqual(graph.digest(body),previous)
            self.assertEqual(row["report_sha256"],row["report"]["content_sha256"])
        self.assertEqual(previous,self.partial["last_evidence_chain_sha256"])
        self.assertEqual(len(list((self.home/"benchmark"/"LEFT_PARTIAL").glob("step-*.json"))),10)

    def test_derived_report_does_not_mint_an_original_sensor(self):
        for report in self.partial["steps"][1:7]:
            self.assertIsNone(report["report"]["root_sensor_event"])
            self.assertFalse(report["report"]["claimed_independent_root"])

    def test_duplicate_report_claiming_independence_even_if_rehashed_is_held(self):
        copies=graph.fixture("LEFT_PARTIAL")
        copies[1]["claimed_independent_root"]=True
        body=dict(copies[1]);body.pop("content_sha256")
        copies[1]["content_sha256"]=graph.digest(body)
        with self.assertRaises(graph.HOLD):graph.verify_graph(copies)

    def test_unresolved_dependency_parent_and_cross_origin_parent_refused(self):
        copies=graph.fixture("LEFT_PARTIAL")
        copies[1]["parent_report_id"]="R009"
        body=dict(copies[1]);body.pop("content_sha256")
        copies[1]["content_sha256"]=graph.digest(body)
        with self.assertRaises(graph.HOLD):graph.verify_graph(copies)
        copies=graph.fixture("LEFT_PARTIAL")
        copies[1]["parent_report_id"]="R008"
        body=dict(copies[1]);body.pop("content_sha256")
        copies[1]["content_sha256"]=graph.digest(body)
        with self.assertRaises(graph.HOLD):graph.verify_graph(copies)

    def test_derived_copy_claim_different_from_root_is_refused(self):
        copies=graph.fixture("LEFT_PARTIAL")
        copies[1]["claim_value"]="partial"
        body=dict(copies[1]);body.pop("content_sha256")
        copies[1]["content_sha256"]=graph.digest(body)
        with self.assertRaises(graph.HOLD):graph.verify_graph(copies)

    def test_forged_physical_witness_flag_is_never_read_as_evidence(self):
        copies=graph.fixture("LEFT_PARTIAL")
        copies[0]["actual_human_witness"]=True
        body=dict(copies[0]);body.pop("content_sha256")
        copies[0]["content_sha256"]=graph.digest(body)
        with self.assertRaises(graph.HOLD):graph.verify_graph(copies)

    def test_independence_is_a_declared_fixture_not_authentication(self):
        copies=graph.fixture("LEFT_PARTIAL")
        copies[0]["source_independence_verified"]=True
        body=dict(copies[0]);body.pop("content_sha256")
        copies[0]["content_sha256"]=graph.digest(body)
        with self.assertRaises(graph.HOLD):graph.verify_graph(copies)
        self.assertTrue(self.partial["assumptions"]["shared_unreported_upstream_sources_can_escape_detector"])

    def test_root_sensor_content_cannot_silently_change_after_hash_recomputation(self):
        reports=graph.fixture("LEFT_PARTIAL")
        reports[0]["root_sensor_event"]["simulated_sensor_output"]="partial"
        sensor=reports[0]["root_sensor_event"]
        body=dict(sensor);body.pop("content_sha256")
        sensor["content_sha256"]=graph.digest(body)
        body=dict(reports[0]);body.pop("content_sha256")
        reports[0]["content_sha256"]=graph.digest(body)
        with self.assertRaises(graph.HOLD):graph.verify_graph(reports)

    def test_origin_split_to_second_root_with_same_identity_is_refused(self):
        reports=graph.fixture("LEFT_PARTIAL")
        reports[1]=graph.event(2,"A","full") # mint a new root under existing A
        with self.assertRaises(graph.HOLD):graph.verify_graph(reports)

    def test_bad_order_duplicates_or_excessive_reports_are_refused(self):
        reports=graph.fixture("LEFT_PARTIAL")
        with self.assertRaises(graph.HOLD):graph.verify_graph(reports*4)
        reports[1]["sequence"]=1
        body=dict(reports[1]);body.pop("content_sha256")
        reports[1]["content_sha256"]=graph.digest(body)
        with self.assertRaises(graph.HOLD):graph.verify_graph(reports)

    def test_absent_or_changed_source_images_are_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)/"images"
            shutil.copytree(self.question,folder)
            file=folder/"worlds"/"LEFT_FULL"/"start.png"
            file.write_bytes(file.read_bytes()+b"x")
            with self.assertRaises(prior.HOLD):prior.verify_original(folder)

    def test_single_root_with_repeaters_matches_one_root_only_posterior(self):
        root=graph.fixture("LEFT_PARTIAL")[0]
        copies=[root]+graph.fixture("LEFT_PARTIAL")[1:7]
        origins,_,conflict=graph.verify_graph(copies)
        self.assertEqual(len(origins),1)
        self.assertFalse(conflict["independent_roots_contradict"])
        x=graph.source_posterior(origins,self.worlds)
        expected=prior.increment(prior.PRIORS,self.worlds,root["root_sensor_event"])
        self.assertEqual(x,expected)

    def test_synthetic_source_provenance_is_not_a_real_source_signature(self):
        self.assertFalse(self.partial["authority"]["root_source_attestations_verified"])
        self.assertFalse(self.partial["assumptions"]["reliability_not_estimated_from_real_data"] is False)
        self.assertFalse(self.partial["assumptions"]["out_of_support_worlds_not_considered"] if "out_of_support_worlds_not_considered" in self.partial["assumptions"] else False)
        self.assertTrue(self.summary["not_a_claim_of_independent_witness_authentication"])
        self.assertEqual(self.summary["external_actions"],0)

    def test_no_overwrite_of_original_ledger_and_full_benchmark(self):
        with self.assertRaises(graph.HOLD):
            graph.benchmark(self.question,self.home/"benchmark")
        with self.assertRaises(graph.HOLD):
            graph.replay(self.question,"LEFT_PARTIAL",self.home/"benchmark"/"LEFT_PARTIAL")

    def test_json_receipt_reproducible_and_original_prior_kept(self):
        p=self.partial
        body=dict(p);claimed=body.pop("content_sha256")
        self.assertEqual(graph.digest(body),claimed)
        self.assertEqual(prior.typed_weights(p["original_priors"]),prior.PRIORS)
        body=dict(self.summary);claimed=body.pop("content_sha256")
        self.assertEqual(graph.digest(body),claimed)

if __name__=="__main__":unittest.main()
