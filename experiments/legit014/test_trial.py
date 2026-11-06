"""LEGIT-014 falsifiers for actual performance-gated self-improvement.

Tests prove that bad algebra is rejected by Z3, valid but slower code is
not automatically admitted, the winner is frozen before holdout, and the
new source remains an inert exact-template draft. No gain may be claimed
without a strong separate classical solver and real heldout timings.
"""
from __future__ import annotations
from copy import deepcopy
from pathlib import Path
from importlib.util import spec_from_file_location,module_from_spec
import hashlib
import json
import sys
import unittest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"legit013"))
sys.path.insert(0,str(HERE.parent/"legit012"))
sys.path.insert(0,str(HERE))
from graph_reference import cases,check_graph,scan
from formal_oracle import prove_rule
from transform import (HOLD,PARENT_SHA,PROPOSALS,train_profile,
    get_parent,propose_round_one,next_round,distinct,validate,prove,
    emit,limited_load,compile_proved,independent_regression,catalog,_make_columns)
_spec=spec_from_file_location("legit014_local_benchmark",HERE/"benchmark.py")
_benchmark=module_from_spec(_spec)
_spec.loader.exec_module(_benchmark)
evaluate=_benchmark.evaluate
training_cases=_benchmark.training_cases
unseen_cases=_benchmark.unseen_cases


class SelfImprovementTrialTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.profile=train_profile()
        cls.rows=catalog()
        cls.cols=_make_columns(cls.rows)
        cls.trials=propose_round_one(cls.profile)
        cls.proof=compile_proved({"parent":"FIRST","rules":[["P_ZERO","ZERO"]]})
        cls.benchmark,cls.generated=evaluate()

    def test_real_previous_source_loaded_by_hash(self):
        parent=get_parent()
        self.assertTrue(callable(parent.solve))
        self.assertEqual(len(self.rows),152)
        self.assertEqual(hashlib.sha256(Path(parent.__file__).read_bytes()).hexdigest(),PARENT_SHA)

    def test_original_actual_profiler_supplies_observations(self):
        self.assertEqual(self.profile["origins"]["training_graphs"],32)
        self.assertGreater(self.profile["origins"]["training_transitions"],10000)
        self.assertIn("P_FULL",self.profile["support"])
        self.assertIn("P_ZERO",self.profile["support"])
        self.assertFalse(self.profile["test_outputs_used"])

    def test_round_one_created_from_profile_not_manually_selected_winner(self):
        self.assertGreaterEqual(len(self.trials),4)
        self.assertEqual(len({json.dumps(p,sort_keys=True) for p in self.trials}),
                         len(self.trials))
        self.assertIn({"parent":"FIRST","rules":[]},self.trials)

    def test_second_round_changes_measured_first_round_plan(self):
        existing={json.dumps(p,sort_keys=True) for p in self.trials}
        proposals=next_round({"parent":"FIRST","rules":[["P_FULL","COLUMN"]]},
                             self.profile,set())
        self.assertGreater(len(proposals),0)
        self.assertTrue(any(p["parent"]=="LAST" or p["rules"]!=[["P_FULL","COLUMN"]]
                            for p in proposals))
        self.assertTrue(all(len(p["rules"])<=2 for p in proposals))

    def test_unknown_arbitrary_source_rule_cannot_enter_search(self):
        for p in ({"parent":"SHELL","rules":[]},
                  {"parent":"FIRST","rules":[["P_ZERO","EXEC_PYTHON"]]},
                  {"parent":"FIRST","rules":[["P_ZERO","ZERO"],["P_ZERO","ZERO"]]}):
            with self.assertRaises(HOLD):
                validate(p)

    def test_genuine_Z3_rejects_unsound_generalization(self):
        evidence=prove_rule("P_ZERO","COLUMN",152)
        self.assertEqual(evidence["result"],"SAT")
        self.assertFalse(evidence["valid_all_masks"])
        witness=evidence["counterexample"]
        self.assertNotEqual(int(witness["incorrect"],16),
                            int(witness["reference"],16))

    def test_valid_shortcut_requires_actual_Z3_UNSAT_proof(self):
        proof=self.proof["proof"]
        self.assertTrue(proof["all_rules_verified"])
        self.assertEqual(len(proof["proofs"]),3)
        self.assertTrue(all(c["z3_verdict"]=="UNSAT" for c in proof["proofs"]))
        self.assertFalse(self.proof["not_production"] is False)

    def test_alternate_source_does_not_execute_even_when_parses(self):
        original=self.proof["source"]
        with self.assertRaises(HOLD):
            limited_load(original+"\ndef extra(): return 3\n",self.proof["plan"])
        with self.assertRaises(HOLD):
            limited_load(original+"\nimport os\n",self.proof["plan"])

    def test_proved_candidate_matches_finite_oracles(self):
        info=independent_regression(self.rows,self.cols,self.proof)
        self.assertEqual(info["states"],6561)
        self.assertTrue(info["all_outputs_match"])

    def test_training_and_unseen_synthetic_seeds_disjoint(self):
        training=training_cases()
        future=unseen_cases()
        self.assertEqual(len(training),36)
        self.assertEqual(len(future),80)
        self.assertTrue(all(a[1]!=b[1] for a in training for b in future))

    def test_profiler_does_not_read_heldout_data(self):
        self.assertFalse(self.benchmark["selection_used_holdout_data"])
        self.assertEqual(self.benchmark["feedback_rounds"],2)
        self.assertGreater(self.benchmark["round_two_variants_created_from_measured_feedback"],0)

    def test_trial_checks_semantics_on_every_unseen_graph(self):
        self.assertEqual(self.benchmark["heldout_graphs"],80)
        self.assertEqual(self.benchmark["heldout_incorrect_outputs"],0)
        self.assertEqual(self.benchmark["full_partial_truth_lattice_checked"],6561)
        self.assertGreater(self.benchmark["heldout_states"],10000)

    def test_real_timing_comparison_includes_strong_tuned_classical(self):
        timings=self.benchmark["heldout_repeated_ms"]
        self.assertEqual(set(timings),
                         {"prior_012","prior_013","strong_classical","candidate"})
        self.assertTrue(all(len(row["samples_ms"])==11 for row in timings.values()))
        self.assertEqual(set(self.benchmark["wins_out_of_11_repeats"]),
                         {"prior_013","strong_classical"})

    def test_acceptance_requires_explicit_predeclared_improvement_gates(self):
        gates=self.benchmark["gate"]
        self.assertIn("at_least_8_percent_faster_vs_prior",gates)
        self.assertIn("at_least_8_percent_faster_vs_strong_classical",gates)
        self.assertIn("win_at_least_10_of_11_repeats_vs_both",gates)
        self.assertIn("no_family_regression_gt_10_percent_vs_strong",gates)
        self.assertFalse(gates["independently_authored_test_corpus"])
        self.assertFalse(gates["production_auto_merge"])
        self.assertEqual(self.benchmark["status"],
                         ("RETAIN_RESEARCH_CANDIDATE_FOR_INDEPENDENT_REVIEW"
                          if self.benchmark["internal_retain_gate_passed"]
                          else "HOLD_NO_RELIABLE_RUNTIME_IMPROVEMENT"))

    def test_competitor_is_not_strawman(self):
        ops=self.benchmark["heldout_operation_counts"]
        self.assertGreater(ops["strong_intersections"],0)
        self.assertGreater(ops["generated_intersections"],0)
        self.assertTrue(self.benchmark["performance_proof_of_general_advantage"] is False)
        self.assertFalse(self.benchmark["independently_authored_external_challenge"])

    def test_all_failed_variants_remain_in_inspectable_feedback_ledger(self):
        reviews=self.benchmark["training_reviews"]
        self.assertGreaterEqual(len(reviews),5)
        self.assertEqual(len({r["id"] for r in reviews}),len(reviews))
        self.assertEqual(sum(r["status"]=="TRAINING_FROZEN_WINNER" for r in reviews),1)
        self.assertGreater(sum(r["status"]=="REJECT_TRAINING_SLOWER_ALTERNATIVE"
                               for r in reviews),0)
        self.assertEqual(self.benchmark["proposed_candidate_count"],len(reviews))

    def test_real_smt_counterexample_rejects_wrong_source_before_timing(self):
        rejected=[x for x in self.benchmark["training_reviews"]
                  if x["status"]=="REJECT_INCORRECT_OR_UNPROVED"]
        self.assertGreater(len(rejected),0)
        self.assertTrue(any("SMT_SAT_COUNTEREXAMPLE" in x["error_detail"]
                            for x in rejected))
        self.assertTrue(all("training_median_ms" not in x for x in rejected))
        self.assertTrue(all(x["round"]=="ROUND_ONE_INJECTED_UNSOUND_FALSIFIER"
                            for x in rejected))

    def test_committed_candidate_source_is_provably_executable_but_inert(self):
        saved=(HERE/"generated"/"candidate_rewrite.py").read_text(encoding="utf-8")
        receipt=json.loads((HERE/"generated"/"candidate_manifest.json").read_text(
            encoding="utf-8"))
        self.assertEqual(saved,emit(receipt["source_plan"]))
        self.assertEqual(hashlib.sha256(saved.encode()).hexdigest(),
                         receipt["generated_source_sha256"])
        checked=compile_proved(receipt["source_plan"])
        self.assertEqual(checked["source"],saved)
        self.assertEqual(independent_regression(
            self.rows,self.cols,checked)["states"],6561)
        self.assertFalse(receipt["automatic_promotion_permitted"])
        self.assertTrue(receipt["human_review_required"])

    def test_saved_performance_result_is_a_falsifiable_hold_not_fake_win(self):
        archived=json.loads((HERE/"generated"/"performance_trial_report.json").read_text(
            encoding="utf-8"))
        saved=json.loads((HERE/"generated"/"candidate_manifest.json").read_text(
            encoding="utf-8"))
        # Timing selection can legitimately differ across CI runner replays:
        # validate original frozen trial, NOT bit-for-bit match to new jitter.
        self.assertEqual(archived["experiment"],"MOTIF-LEGIT-014")
        self.assertEqual(archived["frozen_selected_source_sha256"],
                         saved["generated_source_sha256"])
        self.assertEqual(archived["frozen_selected_plan"],saved["source_plan"])
        self.assertEqual(archived["heldout_incorrect_outputs"],0)
        self.assertEqual(archived["heldout_graphs"],80)
        self.assertEqual(archived["status"],"HOLD_NO_RELIABLE_RUNTIME_IMPROVEMENT")
        self.assertFalse(archived["internal_retain_gate_passed"])
        self.assertFalse(saved["heldout_passed_internal_speed_gate"])
        self.assertTrue(any(row["status"]=="REJECT_INCORRECT_OR_UNPROVED"
                            for row in archived["training_reviews"]))

    def test_source_has_no_external_authority(self):
        manifest=self.generated["manifest"]
        self.assertEqual(manifest["status"],"DRAFT_NO_AUTOMATIC_PROMOTION")
        self.assertFalse(manifest["automatic_promotion_permitted"])
        self.assertFalse(manifest["real_world_authority"])
        self.assertTrue(manifest["human_review_required"])
        self.assertFalse(manifest["independent_external_validation_complete"])
        self.assertTrue(self.generated["source"].startswith(
            '"""Generated by MOTIF LEGIT-014'))

if __name__=="__main__":
    unittest.main()
