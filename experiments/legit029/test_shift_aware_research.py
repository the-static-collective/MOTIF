"""LEGIT-029 adversarial checks: method-risk humility under shifted inputs."""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
from unittest.mock import patch
from pathlib import Path
import json
import sys
import unittest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import shift_worlds as worlds
import meta_guard as experiment
import information_engine as engine


class ShiftAwareResearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.policies,cls.training=experiment.prepare_training()

    def test_math_goal_contracts_and_registered_seeds(self):
        self.assertEqual(len(worlds.DOMAINS),3)
        self.assertFalse(set(worlds.GRAPH_TRAIN)&set(worlds.GRAPH_FUTURE))
        self.assertFalse(set(worlds.MATH_TRAIN)&set(worlds.MATH_FUTURE))
        self.assertFalse(set(worlds.MATH_TRAIN)&set(worlds.MATH_FUTURE_SHIFT))
        self.assertFalse(set(worlds.MATH_FUTURE)&set(worlds.MATH_FUTURE_SHIFT))
        with self.assertRaises(worlds.HOLD):
            worlds.graph_world(989898)
        with self.assertRaises(worlds.HOLD):
            worlds.math_world(worlds.DOMAINS[1],worlds.MATH_FUTURE[0],
                              "SEEN_SHIFT")

    def test_data_future_prohibition_when_training_and_freezing(self):
        with patch("meta_guard.worlds.future_worlds",
                   side_effect=AssertionError("future world was opened in training")):
            models,receipt=experiment.prepare_training()
        self.assertEqual(receipt["frozen_research_plan_sha256"],
                         self.training["frozen_research_plan_sha256"])
        self.assertTrue(receipt[
            "future_seed_datasets_not_requested_before_freeze"])
        self.assertEqual(set(models),set(worlds.DOMAINS))

    def test_multiple_training_environments_without_leaking_future(self):
        for domain in worlds.DOMAINS:
            stats=self.training["per_domain"][domain]
            self.assertGreaterEqual(len(stats["training_world_sizes"]),4)
            cv=stats["crossworld_policy_scores_and_decisions"]
            self.assertEqual(cv["train_world_count"],
                             len(stats["training_world_sizes"]))
            self.assertEqual(len(cv[
                "every_candidate_crossworld_performance"]),len(engine.ALL_METHODS))
            for method,scores in cv["every_candidate_crossworld_performance"].items():
                self.assertEqual(len(scores["folds"]),cv["train_world_count"])
                self.assertEqual(len(scores["world_regrets"]),cv["train_world_count"])
                self.assertEqual(max(scores["world_regrets"]),
                                 scores["worst_world_regret_vs_classical"])
                self.assertTrue(all(x["cases"]>0 for x in scores["folds"]))

    def test_empirical_worst_world_rejects_without_evidence(self):
        for domain in worlds.DOMAINS:
            cv=self.training["per_domain"][domain][
                "crossworld_policy_scores_and_decisions"]
            self.assertTrue(cv["assumes_no_exchangeability_or_iid_guarantee"])
            strong=cv["robust_empirical_candidate_selected"]
            if strong!=engine.CONVENTIONAL:
                selected=cv["every_candidate_crossworld_performance"][strong]
                self.assertLessEqual(selected["macro_regret_vs_classical"],
                                     -experiment.ROBUST_MEAN_MARGIN)
                self.assertLessEqual(selected["worst_world_regret_vs_classical"],0)
            else:
                self.assertFalse(cv["eligible_empirical_robust_candidates"])

    def test_shift_detector_uses_only_free_task_shape_not_outcomes(self):
        cases,_=worlds.training_worlds()
        for domain in worlds.DOMAINS:
            detector=self.training["per_domain"][domain]["input_shift_detector"]
            self.assertTrue(detector["input_metadata_only_no_question_answers"])
            self.assertTrue(detector["threshold_empirical_not_conformal_risk_bound"])
            self.assertEqual(detector["dimension"],4)
            first=next(iter(cases[domain].values()))[0]
            with patch("shift_worlds.previous.observation",
                       side_effect=AssertionError("query during metadata")):
                score=experiment.input_shift_score(detector,domain,first)
            self.assertGreaterEqual(score,0)

    def test_guard_refuses_far_outside_training_input_shape(self):
        domain="polynomial_modular_witness"
        policy=experiment.training_cv
        _=policy
        _,cv,detector=self.policies[domain]
        bizarre={"id":"novel_shape_without_probe",
                 "payload":{"objects":((0,0,0,0),(80000,90000,0,0))}}
        with patch("shift_worlds.previous.observation",
                   side_effect=AssertionError("a question was evaluated")):
            selected,distance,decision=experiment.select_method(
                cv,detector,domain,bizarre,"SHIFT_GATED_SIMPLE_CV")
        self.assertEqual(selected,engine.CONVENTIONAL)
        self.assertEqual(decision,"NOVEL_INPUT_REFUSAL")
        self.assertGreater(distance,detector["threshold"])

    def test_all_question_policy_freezes_recompute_exactly(self):
        per={}
        for domain,(models,_,detector) in self.policies.items():
            package=self.training["per_domain"][domain]
            checks=package["frozen_model_components_sha256"]
            for method,model in models.items():
                self.assertEqual(engine.sha256_plan(model),checks[method])
            self.assertEqual(sha256(json.dumps(detector,sort_keys=True,
                             separators=(",",":")).encode()).hexdigest(),
                             checks["DETECTOR"])
            self.assertEqual(sha256(json.dumps(checks,sort_keys=True,
                             separators=(",",":")).encode()).hexdigest(),
                             package["model_hash_sha256"])
            per[domain]=package["model_hash_sha256"]
        frozen=sha256(json.dumps(per,sort_keys=True,
                       separators=(",",":")).encode()).hexdigest()
        self.assertEqual(frozen,self.training["frozen_research_plan_sha256"])

    def test_graph_future_complements_are_flagged_dependent(self):
        source,origin=worlds.graph_world(worlds.GRAPH_FUTURE[0])
        derivative,derived_origin=worlds.graph_world(
            worlds.GRAPH_FUTURE[0],True)
        self.assertEqual(len(source),8)
        self.assertEqual(len(derivative),8)
        self.assertFalse(origin["complement_derived_from_same_seeded_carriers"])
        self.assertTrue(derived_origin[
            "complement_derived_from_same_seeded_carriers"])
        self.assertFalse(derived_origin["separately_sampled_graph_carriers"])

    def test_shifted_math_worlds_and_old_questions(self):
        import information_worlds as old
        for domain in worlds.DOMAINS[1:]:
            cases,origin=worlds.math_world(
                domain,worlds.MATH_FUTURE_SHIFT[0],"FAR_SHIFT")
            self.assertEqual(len(cases),16)
            self.assertEqual(origin["regime"],"FAR_SHIFT")
            old_q=old.candidate_questions(domain)[:2]
            for case in cases:
                self.assertTrue(all(not old.is_witness(old.observation(
                    domain,case,q)) for q in old_q))
                self.assertTrue(any(old.is_witness(old.observation(
                    domain,case,q)) for q in old.candidate_questions(domain)))

    def test_false_verified_mathematical_answer_forbidden(self):
        import information_worlds as old
        domain=worlds.DOMAINS[1]
        case=worlds.math_world(domain,worlds.MATH_TRAIN[0],
                              "SEEN_SHIFT")[0][0]
        model=self.policies[domain][0][engine.CONVENTIONAL]
        with patch("meta_guard.legacy.observation",
                   return_value=(-123456789,987654321)):
            with self.assertRaises(worlds.HOLD):
                experiment._exact_replay(domain,case,model)

    def test_full_future_evidence_no_hindsight_promotion(self):
        result=experiment.run()
        self.assertEqual(result["status"],experiment.STATUS)
        self.assertEqual(result["training_and_frozen_methods"][
            "frozen_research_plan_sha256"],
            self.training["frozen_research_plan_sha256"])
        self.assertEqual(set(result["aggregate_results"]),set(worlds.DOMAINS))
        self.assertIn("No exchangeability, independence or conformal risk guarantee",
                      result["limitations"])
        for domain,methods in result["aggregate_results"].items():
            expected=32 if domain=="graph_hom_witness" else 64
            self.assertEqual(set(methods),{
                engine.CONVENTIONAL, "RAW_OBSERVATION_DIVERSITY",
                "JOINT_SHANNON_ENTROPY","CONTEXTUAL_VALUE_OF_INFORMATION",
                *experiment.META_ARMS})
            for name,scores in methods.items():
                self.assertEqual(scores["cases"],expected)
                self.assertEqual(scores["solved"],expected,
                                 (domain,name))
            record=result["posthoc_diagnosis_not_used_for_any_future_policy"][domain]
            self.assertTrue(record[
                "winner_not_promoted_to_same_evaluation"])
            for world,arms in result["future_results"][domain].items():
                for name,values in arms.items():
                    for record in values["question_and_gate_receipts"]:
                        self.assertTrue(record[
                            "selected_using_earlier_training_only"])
                        self.assertEqual(record["questions"],
                                         len(record["question_receipts"]))
                        self.assertTrue(record["question_receipts"][-1][
                            "is_exact_counterexample"])
                        self.assertTrue(all(x["independent_oracle_agreed"]
                                            for x in record["question_receipts"]))


if __name__=="__main__":
    unittest.main()
