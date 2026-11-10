"""LEGIT-028 falsification-focused tests for information geometry."""
from __future__ import annotations

from hashlib import sha256
from unittest.mock import patch
from pathlib import Path
import json
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import information_worlds as w
import information_engine as g
import run_information_geometry as e


class InformationGeometryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.policies,cls.training=e.training_and_freeze()

    def test_three_genuinely_different_output_contracts(self):
        self.assertEqual(set(w.DOMAINS),{
            "graph_hom_witness","polynomial_modular_witness",
            "integer_constraint_countermodel"})
        self.assertEqual(len(w.candidate_questions(w.DOMAINS[0])),21)
        self.assertEqual(len(w.candidate_questions(w.DOMAINS[1])),35)
        self.assertEqual(len(w.candidate_questions(w.DOMAINS[2])),36)

    def test_entropy_is_not_goal_utility_counterexample(self):
        domain="graph_hom_witness"
        q=w.candidate_questions(domain)
        rows=[]
        for i in range(4):
            answers={probe:(0,0) for probe in q}
            answers[q[0]]=(i,i)   # Lots of variation, zero witness utility.
            answers[q[1]]=(0,1)   # Few distinct values, guaranteed witness.
            rows.append({"id":str(i),"answers":answers})
        signature=g.morphology(domain,rows)
        raw=g.static_order(domain,rows,
            "RAW_OBSERVATION_DIVERSITY",signature)
        useful=g.static_order(domain,rows,
            "MARGINAL_WITNESS_PROBABILITY",signature)
        self.assertEqual(raw[0],q[0])
        self.assertEqual(useful[0],q[1])
        self.assertGreater(signature["per_question"][q[0]][
            "joint_pair_entropy_bits"],signature["per_question"][q[1]][
            "joint_pair_entropy_bits"])
        self.assertEqual(signature["per_question"][q[0]][
            "witness_probability_empirical"],0)
        self.assertEqual(signature["per_question"][q[1]][
            "witness_probability_empirical"],1)

    def test_all_eligible_methods_have_full_question_access(self):
        for domain in w.DOMAINS:
            expected=set(w.candidate_questions(domain))
            for method,policy in self.policies[domain].items():
                self.assertEqual(policy["domain"],domain)
                if policy["order"] is not None:
                    self.assertEqual(set(policy["order"]),expected)
                    self.assertEqual(len(policy["order"]),len(expected))
                else:
                    self.assertIn(method,g.ADAPTIVE | {"GEOMETRY_CV_GUARDED_ROUTER"})

    def test_future_is_never_loaded_before_training_policy_freeze(self):
        with patch("run_information_geometry.worlds.future_worlds",
                   side_effect=AssertionError("evaluation leakage")):
            strategies,report=e.training_and_freeze()
        self.assertEqual(report["frozen_all_domain_policy_sha256"],
                         self.training["frozen_all_domain_policy_sha256"])
        self.assertEqual(set(strategies),set(w.DOMAINS))
        self.assertTrue(report[
            "future_graph_and_math_worlds_not_requested_before_frozen_hash"])

    def test_all_policy_fingerprints_can_be_recomputed(self):
        for domain in w.DOMAINS:
            for method,policy in self.policies[domain].items():
                self.assertEqual(
                    g.sha256_plan(policy),
                    self.training["domains"][domain]["frozen_method_sha256"][
                        method])
        blob=json.dumps(self.training["all_domain_policy_fingerprints"],
                        sort_keys=True,separators=(",",":")).encode()
        self.assertEqual(sha256(blob).hexdigest(),self.training[
            "frozen_all_domain_policy_sha256"])

    def test_morphology_identifies_binary_vs_multivalued(self):
        self.assertEqual(self.training["domains"][
            "integer_constraint_countermodel"]["observational_morphology"][
                "kind"],"EMPIRICALLY_BINARY")
        for domain in ("graph_hom_witness","polynomial_modular_witness"):
            self.assertEqual(self.training["domains"][domain][
                "observational_morphology"]["kind"],
                "EMPIRICALLY_MULTIVALUED")

    def test_cv_guard_can_refuse_an_entropy_enthusiast(self):
        for domain in w.DOMAINS:
            protocol=self.training["domains"][domain][
                "leave_one_training_world_out"]
            cv=protocol["comparators"]
            best=protocol["best_candidate_geometry_method"]
            incumbent=cv[g.CONVENTIONAL]["macro_world_mean_questions"]
            test=cv[best]["macro_world_mean_questions"]+e.MIN_DELTA
            self.assertEqual(protocol["geometry_promoted"],test<incumbent-1e-9)
            if not protocol["geometry_promoted"]:
                self.assertEqual(protocol["adopted_method"],g.CONVENTIONAL)
                self.assertIsNotNone(protocol["rejection_reason"])
            self.assertTrue(protocol["future_worlds_not_read_for_selection"])
            self.assertEqual(protocol["candidate_method_count"],len(g.ALL_METHODS))

    def test_contextual_policies_use_only_previous_failed_answers(self):
        domain="polynomial_modular_witness"
        rows=g.records(domain,w.training_worlds()[0][domain][
            "math_train_seed_27011"])
        for method in g.ADAPTIVE:
            model=g.compile_policy(domain,rows,method)
            prior_question=g.next_question(model,[])
            result=g.simulate(model,"real_train_case",
                lambda q: rows[0]["answers"][q])
            self.assertTrue(result["solved"])
            self.assertEqual(result["all_attempted_questions"][0][0],
                             prior_question)
            actual=[q for q,answer in result["all_attempted_questions"]]
            self.assertEqual(len(set(actual)),len(actual))
            self.assertLessEqual(len(actual),35)

    def test_independent_math_oracles_agree_on_actual_probes(self):
        train,_=w.training_worlds()
        for domain in w.DOMAINS[1:]:
            first=next(iter(train[domain].values()))[0]
            for q in w.candidate_questions(domain):
                self.assertEqual(w.observation(domain,first,q),
                                 w.independent_observation(domain,first,q))

    def test_forged_exact_witness_refused_during_future_replay(self):
        train,_=w.training_worlds()
        domain="polynomial_modular_witness"
        first=next(iter(train[domain].values()))[0]
        prior=self.policies[domain]
        with patch("run_information_geometry.worlds.observation",
                   return_value=(0,1)):
            with self.assertRaises(w.HOLD):
                e.evaluate(domain,(first,),{"fake":prior[g.CANONICAL]})

    def test_finite_negative_questions_do_not_claim_equivalence(self):
        train,_=w.training_worlds()
        domain="integer_constraint_countermodel"
        cases=next(iter(train[domain].values()))
        old=w.candidate_questions(domain)[:2]
        for case in cases:
            self.assertTrue(all(not w.is_witness(w.observation(
                domain,case,q)) for q in old))
            self.assertTrue(any(w.is_witness(w.observation(
                domain,case,q)) for q in w.candidate_questions(domain)))

    def test_run_independent_future_worlds_and_per_question_receipts(self):
        result=e.run()
        self.assertEqual(result["status"],e.STATUS)
        self.assertEqual(len(result["future_world_provenance"]),3)
        self.assertEqual(set(result["aggregate_results"]),set(w.DOMAINS))
        for domain,rows in result["aggregate_results"].items():
            baseline=rows["NO_EXPANSION_OLD_QUESTIONS"]
            self.assertEqual(baseline["solved"],0)
            self.assertEqual(baseline["cases"],16 if domain==
                             "graph_hom_witness" else 32)
            for method,row in rows.items():
                if method!="NO_EXPANSION_OLD_QUESTIONS":
                    self.assertEqual(row["solved"],row["cases"],(domain,method))
                self.assertGreater(row["questions"],0)
            for world,arms in result["new_world_evidence"][domain].items():
                for method,entry in arms.items():
                    for receipt in entry["receipts"]:
                        self.assertTrue(receipt["all_questions_exactly_verified"])
                        self.assertEqual(receipt["questions"],
                                         len(receipt["all_attempted_questions"]))
                        self.assertTrue(all(
                            q["independent_oracle_agreed"] for q in
                            receipt["all_attempted_questions"]))
                        if method!="NO_EXPANSION_OLD_QUESTIONS":
                            self.assertTrue(receipt["all_attempted_questions"][-1][
                                "is_exact_witness"])

if __name__=="__main__":
    unittest.main()
