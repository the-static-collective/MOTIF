"""LEGIT-027 adversarial cross-domain rule-transfer checks."""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import json
import sys
import unittest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import tasks
import transfer


class CrossDomainTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.orders,cls.training=transfer.prepare_training()

    def test_verified_graph_source_rule_is_precisely_qualified(self):
        origin=transfer.prior_graph_rule()
        self.assertEqual(origin["source_meta"],
                         ["LEAF_FIRST","COUNT_DIVERSITY","STATIC"])
        self.assertEqual(origin["transferred_rule"],"COUNT_DIVERSITY")
        self.assertTrue(origin["graph_specific_LEAF_FIRST_gate_not_transferred"])
        self.assertTrue(origin[
            "not_zero_shot_frozen_graph_question_order"])

    def test_two_distinct_task_contracts_reject_wrong_questions(self):
        self.assertEqual(len(tasks.questions(tasks.DOMAINS[0])),35)
        self.assertEqual(len(tasks.questions(tasks.DOMAINS[1])),36)
        with self.assertRaises(tasks.Hold):
            tasks.questions("unregistered_domain")
        a=tasks.world(tasks.DOMAINS[0],tasks.TRAIN_SEEDS[0])[0][0]
        with self.assertRaises(tasks.Hold):
            tasks.observe(tasks.DOMAINS[0],a,(99,11))

    def test_training_and_future_seeds_never_overlap(self):
        self.assertEqual(tasks.TRAIN_SEEDS,(27011,27012))
        self.assertEqual(tasks.FUTURE_SEEDS,(27013,27014))
        self.assertFalse(set(tasks.TRAIN_SEEDS)&set(tasks.FUTURE_SEEDS))

    def test_every_engineer_case_has_exact_witness_but_old_probes_fail(self):
        for domain in tasks.DOMAINS:
            for seed in tasks.TRAIN_SEEDS+tasks.FUTURE_SEEDS:
                cases,receipt=tasks.world(domain,seed)
                self.assertEqual(len(cases),16)
                self.assertTrue(receipt["engineer_authored"])
                self.assertTrue(receipt["candidate_witness_existence_checked_during_generation"])
                old=tasks.questions(domain)[:2]
                all_q=tasks.questions(domain)
                for case in cases:
                    self.assertTrue(tasks.oracle_nonidentical(domain,case))
                    self.assertTrue(all(len(set(tasks.observe(domain,case,q)))==1
                                        for q in old))
                    self.assertTrue(any(len(set(tasks.observe(domain,case,q)))==2
                                        for q in all_q))

    def test_two_independently_implemented_oracles_agree_everywhere(self):
        for domain in tasks.DOMAINS:
            cases,_=tasks.world(domain,tasks.TRAIN_SEEDS[0])
            for case in cases:
                for question in tasks.questions(domain):
                    self.assertEqual(tasks.observe(domain,case,question),
                                     tasks.independent_observe(domain,case,question))

    def test_no_finite_negative_probe_sequence_proves_identity(self):
        for domain in tasks.DOMAINS:
            cases,_=tasks.world(domain,tasks.TRAIN_SEEDS[0])
            old=tasks.questions(domain)[:2]
            for case in cases:
                self.assertTrue(tasks.oracle_nonidentical(domain,case))
                r=transfer.replay(domain,(case,),{
                    "only_old":old})["only_old"]
                self.assertEqual(r["solved"],0)
                self.assertEqual(r["all_attempted_question_receipts"][0][
                    "verdict"],"ABSTAIN")

    def test_all_candidate_policies_use_exactly_equal_question_grammars(self):
        for domain in tasks.DOMAINS:
            full=set(tasks.questions(domain))
            for name,order in self.orders[domain].items():
                self.assertEqual(set(order),full,(domain,name))
                self.assertEqual(len(order),len(full))
            packet=self.training["domains"][domain]["frozen_selection"]
            serialized=json.dumps(packet["frozen_orders"],sort_keys=True,
                                  separators=(",",":")).encode()
            self.assertEqual(sha256(serialized).hexdigest(),packet[
                "frozen_all_order_sha256"])

    def test_future_worlds_not_read_when_learning_question_policy(self):
        original=transfer.world
        def forbid_future(domain,seed):
            if seed in tasks.FUTURE_SEEDS:
                raise AssertionError("future world used by training")
            return original(domain,seed)
        with patch("transfer.world",side_effect=forbid_future):
            orders,receipt=transfer.prepare_training()
        self.assertEqual(orders,self.orders)
        self.assertTrue(receipt["future_world_function_not_called"])

    def test_training_only_transfer_guard_can_refuse_graph_derived_rule(self):
        for domain in tasks.DOMAINS:
            note=self.training["domains"][domain]["crossvalidated_transfer_guard"]
            vals=note["crossvalidated_mean_questions"]
            graph="LEGIT026_GRAPH_SCORER_TRANSFERRED"
            conventional="TARGET_CLASSICAL_RESIDUAL_GREEDY"
            expected=(graph if vals[graph]<vals[conventional] else conventional)
            self.assertEqual(note["adopted_method"],expected)
            self.assertEqual(note["transfer_retained"],expected==graph)
            self.assertTrue(note["never_select_using_future_seed_results"])
            self.assertTrue(note["fallback_is_existing_classical_not_new_algorithm"])
            self.assertEqual(self.orders[domain]["TRAINING_CV_GUARDED_TRANSFER"],
                             self.orders[domain][expected])
            self.assertEqual({r["left_out_training_seed"] for rows in
                note["out_of_training_world_receipts"].values() for r in rows},
                set(tasks.TRAIN_SEEDS))

    def test_forged_modular_witness_cannot_be_verified(self):
        cases,_=tasks.world(tasks.DOMAINS[0],tasks.TRAIN_SEEDS[0])
        with patch("transfer.observe",return_value=(0,1)):
            with self.assertRaises(tasks.Hold):
                transfer.replay(tasks.DOMAINS[0],cases[:1],
                                {"forged":tasks.questions(tasks.DOMAINS[0])})

    def test_forged_constraint_countermodel_cannot_be_verified(self):
        cases,_=tasks.world(tasks.DOMAINS[1],tasks.TRAIN_SEEDS[0])
        with patch("transfer.observe",return_value=(True,False)):
            with self.assertRaises(tasks.Hold):
                transfer.replay(tasks.DOMAINS[1],cases[:1],
                                {"forged":tasks.questions(tasks.DOMAINS[1])})

    def test_full_independent_future_receipts_and_honest_research_hold(self):
        result=transfer.run()
        self.assertEqual(result["status"],transfer.STATUS)
        self.assertEqual(set(result["aggregate_results"]),set(tasks.DOMAINS))
        self.assertEqual(len(result["future_world_provenance"]),4)
        self.assertIn("Only scoring rule transferred, not graph-only structural gate",
                      result["resource_limitations"])
        for domain,methods in result["aggregate_results"].items():
            self.assertEqual(methods["NO_ESCAPE_OLD_TWO_QUESTIONS"]["solved"],0)
            for name,info in methods.items():
                self.assertEqual(info["cases"],32)
                if name!="NO_ESCAPE_OLD_TWO_QUESTIONS":
                    self.assertEqual(info["solved"],32,(domain,name))
            for seed,arms in result["future_evidence"][domain].items():
                for name,arm in arms.items():
                    for case in arm["all_attempted_question_receipts"]:
                        self.assertTrue(all(q["independent_verification"]
                                            for q in case["full_question_receipts"]))
                        self.assertEqual(case["questions"],
                                         len(case["full_question_receipts"]))
                        if name!="NO_ESCAPE_OLD_TWO_QUESTIONS":
                            self.assertTrue(case["full_question_receipts"][-1][
                                "is_valid_counterexample"])


if __name__=="__main__":
    unittest.main()
