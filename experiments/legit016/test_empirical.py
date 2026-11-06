"""LEGIT-016 adversarial empirical reasoning and real-source tests.

No future probability may be inferred from a hand-selected set of typed
rewrite candidates. The repeat measurements represent one experimental
workload family, not multiple independent inventions. Tests are written
to treat a successful executable proof as insufficient to claim growth.
"""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from math import isfinite
from statistics import median
from importlib.util import spec_from_file_location,module_from_spec
import json
import sys
import unittest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from evidence import archive,summarize,HOLD,TRIAL,ECONOMY,BASELINES
from measurement import measure,registered_source_hashes,registered_challenge
from decision import compare,prospective_record

class EmpiricalWitnessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.archive=archive()
        cls.retrospective=summarize(cls.archive)
        cls.measurement=measure()
        cls.decision=compare(cls.measurement)

    def test_prior_was_actual_formally_verified_but_unpromoted(self):
        self.assertEqual(self.archive["prior_status"],
                         "HOLD_NO_RELIABLE_RUNTIME_IMPROVEMENT")
        self.assertEqual(self.archive["heldout_graphs"],80)
        self.assertEqual(self.archive["heldout_states"],117243)
        self.assertTrue(self.archive["all_outputs_correct_in_old_finite_domain"])
        self.assertFalse(self.archive["actual_compound_reinvestment_measured"])
        self.assertEqual(self.archive["independent_trial_count"],0)

    def test_source_sha_is_checked_against_committed_python_and_manifest(self):
        expected=sha256((TRIAL/"candidate_rewrite.py").read_bytes()).hexdigest()
        self.assertEqual(expected,self.archive["source_sha256"])
        prior=json.loads((TRIAL/"candidate_manifest.json").read_text())
        self.assertEqual(prior["generated_source_sha256"],expected)
        self.assertFalse(prior["automatic_promotion_permitted"])

    def test_prior_economy_did_not_convert_rejected_source_into_return(self):
        prior=json.loads(ECONOMY.read_text())
        self.assertEqual(prior["real_prior_trial_boundary"]["observed_status"],
                         "HOLD_NO_RELIABLE_RUNTIME_IMPROVEMENT")
        self.assertFalse(prior["real_prior_trial_boundary"]
                         ["permitted_to_count_as_real_compounding_return"])
        self.assertFalse(prior["discovery_probabilities_real_world_validated"])

    def test_formal_count_is_not_assumed_success_probability(self):
        self.assertEqual(self.archive["candidate_count"],10)
        self.assertEqual(self.archive["proven_candidate_count"],9)
        self.assertEqual(self.archive["injected_unsound_negative_controls"],1)
        self.assertFalse(self.archive["future_success_probability_identifiable"])
        self.assertEqual(self.retrospective["posterior_success_probability"],
                         "UNIDENTIFIABLE")
        self.assertEqual(self.retrospective["estimated_compounding_factor"],
                         "UNIDENTIFIABLE")

    def test_raw_measurements_reconstruct_old_reported_medians(self):
        for name,times in self.archive["raw_ms"].items():
            self.assertEqual(len(times),11)
            self.assertAlmostEqual(median(times),
                                   self.archive["recorded_median_ms"][name],
                                   places=5)

    def test_old_candidate_lost_to_earlier_best_generation(self):
        comparisons=self.retrospective["baseline_comparisons"]
        self.assertLess(comparisons["prior_012"]
                        ["observed_median_ms_saved_per_80_graph_batch"],0)
        self.assertIsNone(comparisons["prior_012"]
                          ["exploratory_full_cost_break_even_batches"])
        self.assertGreater(comparisons["prior_013"]
                           ["exploratory_full_cost_break_even_batches"],1000)
        self.assertGreater(self.retrospective["discovery_and_verification_setup_ms"],
                           4500)

    def test_014_repeats_do_not_count_as_11_inventions(self):
        self.assertEqual(self.retrospective["independent_research_success_trials"],0)
        self.assertFalse(self.retrospective["has_observed_successive_approved_improvements"])
        self.assertTrue(self.retrospective["read_only"])
        self.assertTrue(self.archive["heldout_from_different_seeds_not_different_authors"])

    def test_new_challenge_registers_separate_but_same_family_seeds(self):
        cases=registered_challenge()
        self.assertEqual(len(cases),24)
        self.assertEqual({name for name,_ in cases},{"LIGHT","MEDIUM","DENSE"})
        self.assertTrue(all(len(graph)>1 for _,graph in cases))
        self.assertEqual(self.measurement["new_seed_start"],120000)

    def test_all_previous_real_programs_reexecuted_under_pinned_hash(self):
        pinned=registered_source_hashes()
        self.assertEqual(set(pinned),{"prior_012","prior_013","candidate_014"})
        self.assertEqual(pinned,self.measurement["source_sha256"])
        self.assertTrue(self.measurement["external_z3_reverified_prior_finite_rewrite"])
        self.assertGreater(self.measurement["external_proof_and_source_compile_ms"],0)

    def test_new_experiment_computes_true_answers_not_just_speed(self):
        self.assertEqual(self.measurement["experiment"],"MOTIF-LEGIT-016")
        self.assertEqual(self.measurement["new_seed_graphs"],24)
        self.assertEqual(self.measurement["exact_scan_reference_graphs"],24)
        self.assertEqual(self.measurement["output_mismatches"],0)
        self.assertGreater(self.measurement["new_seed_graph_states"],10000)

    def test_wall_and_cpu_metrics_are_separate_and_raw(self):
        raw=self.measurement["raw_repeat_samples"]
        self.assertEqual(set(raw),
                         {"candidate_014","prior_012","prior_013","strong_classical"})
        self.assertEqual(self.measurement["sample_count_per_arm"],9)
        for name,values in raw.items():
            self.assertEqual(len(values["wall_ms"]),9)
            self.assertEqual(len(values["cpu_ms"]),9)
            self.assertTrue(all(isfinite(x) and x>0 for x in values["wall_ms"]))
            self.assertAlmostEqual(median(values["wall_ms"]),
                self.measurement["descriptive_medians_ms"][name]["wall"],places=5)

    def test_independent_strong_classical_and_setup_cost_recorded(self):
        self.assertGreater(self.measurement["shared_precomputed_source_index_setup_ms"],0)
        self.assertGreater(self.measurement["strong_classical_index_setup_ms"],0)
        mem=self.measurement["peak_traced_python_allocation_sample"]
        self.assertEqual(len(mem),4)
        self.assertTrue(all(v["sample_graphs"]==3 and
                            v["peak_traced_python_bytes"]>0 for v in mem.values()))

    def test_new_evidence_does_not_establish_compounding_returns(self):
        report=self.decision
        self.assertEqual(report["promotion_decision"],
                         "HOLD_NOT_ENOUGH_INDEPENDENT_EVIDENCE")
        self.assertEqual(report["observed_compounding_rate"],"NOT_ESTIMABLE")
        self.assertFalse(report["new_algorithm_source_generated"])
        self.assertFalse(report["promotion_gate"]["independent_test_author"])
        self.assertFalse(report["promotion_gate"]["calibrated_probability_of_future_upgrade_success"])
        self.assertFalse(report["promotion_gate"]["observed_two_successive_promoted_improvements"])

    def test_new_episode_crosschecks_actual_014_not_inventing_samples(self):
        retrospective=self.decision["real_014_retrospective"]
        self.assertEqual(retrospective,self.retrospective)
        for name,comparison in self.decision["cross_trial_descriptive_comparisons"].items():
            self.assertFalse(comparison["separate_research_innovation_trials"])
            self.assertFalse(comparison["independent_external_test_authorship"])
            self.assertFalse(comparison["same_exact_graphs"])
            self.assertTrue(comparison["same_source_programs"])

    def test_promoting_on_simple_microbenchmark_is_forbidden(self):
        gates=self.decision["promotion_gate"]
        self.assertFalse(gates["production_promotion_allowed"])
        self.assertFalse(gates["statistical_generalization_across_hardware"])
        self.assertFalse(gates["full_end_to_end_cost_amortization_demonstrated"])
        self.assertFalse(gates["external_custody_authentication"])

    def test_committed_trial_packet_has_real_raw_samples_and_retains_hold(self):
        saved=json.loads((HERE/"generated"/"empirical_witness_report.json")
                         .read_text(encoding="utf-8"))
        self.assertEqual(saved["experiment"],"MOTIF-LEGIT-016")
        self.assertEqual(saved["new_016_observed_episode"]["new_seed_graph_states"],
                         28560)
        self.assertEqual(saved["new_016_observed_episode"]["new_seed_graphs"],24)
        self.assertEqual(saved["promotion_decision"],
                         "HOLD_NOT_ENOUGH_INDEPENDENT_EVIDENCE")
        self.assertFalse(saved["promotion_gate"]["production_promotion_allowed"])
        self.assertFalse(saved["promotion_gate"]["independent_test_author"])
        self.assertEqual(saved["real_014_retrospective"],self.retrospective)
        # A rerun on another runner is expected to have *different* timings.
        # Validate the committed raw measurements internally rather than
        # demanding they match the current, noisy runtime.
        from decision import _checked
        stats=_checked(saved["new_016_observed_episode"])
        self.assertGreater(stats["candidate_014"]["wall_ms"],0)
        self.assertEqual(saved["new_016_observed_episode"]["source_sha256"],
                         registered_source_hashes())
        self.assertEqual(saved["current_observations"]["prior_012"]
                         ["meets_8_percent_and_8_of_9_descriptive_gate"],False)
        self.assertEqual(saved["observed_compounding_rate"],"NOT_ESTIMABLE")

    def test_real_source_remeasurement_still_loses_to_012_in_frozen_episode(self):
        saved=json.loads((HERE/"generated"/"empirical_witness_report.json")
                         .read_text(encoding="utf-8"))
        ours=saved["current_observations"]["prior_012"]
        self.assertLess(ours["relative_gain_wall"],0)
        self.assertLess(ours["wins_out_of_9_index_aligned_samples"],8)
        self.assertFalse(ours["all_candidate_samples_faster_than_all_reference_samples"])
        self.assertEqual(saved["real_014_retrospective"]["baseline_comparisons"]
                         ["prior_012"]["exploratory_full_cost_break_even_batches"],None)

    def test_fake_faster_timings_cannot_change_epistemic_provenance(self):
        fake=deepcopy(self.measurement)
        for item in fake["raw_repeat_samples"]["candidate_014"]["wall_ms"]:
            self.assertGreater(item,0)
        fake["raw_repeat_samples"]["candidate_014"]["wall_ms"]=[1.0]*9
        fake["raw_repeat_samples"]["candidate_014"]["cpu_ms"]=[1.0]*9
        fake["descriptive_medians_ms"]["candidate_014"]={"wall":1.0,"cpu":1.0}
        result=compare(fake)
        self.assertTrue(result["promotion_gate"]
                        ["new_016_candidate_meets_all_descriptive_thresholds"])
        self.assertFalse(result["promotion_gate"]["production_promotion_allowed"])
        self.assertEqual(result["observed_compounding_rate"],"NOT_ESTIMABLE")

    def test_tampered_source_receipt_is_rejected_even_if_stated_correct(self):
        fake=deepcopy(self.measurement)
        fake["output_mismatches"]=1
        with self.assertRaises(HOLD):
            compare(fake)

    def test_fake_number_of_samples_is_rejected(self):
        fake=deepcopy(self.measurement)
        fake["raw_repeat_samples"]["strong_classical"]["cpu_ms"].pop()
        with self.assertRaises(HOLD):
            compare(fake)

    def test_unregistered_performance_nan_and_negative_are_rejected(self):
        for bad in (float("nan"),float("inf"),-1):
            fake=deepcopy(self.measurement)
            fake["raw_repeat_samples"]["candidate_014"]["wall_ms"][0]=bad
            with self.assertRaises(HOLD):
                compare(fake)

    def test_input_contract_for_next_external_investigator(self):
        template={
            "candidate_sha256":"1"*64,"reference_sha256":"2"*64,
            "preregistered_plan_sha256":"3"*64,
            "research_cost_ms":120,"proof_and_review_cost_ms":50,
            "rollback_cost_ms":25,"workload_family":"REASONING_DAG",
            "outcome":"VERIFIED_GAIN","source_external_custody_verified":False,
            "source_generated_from_same_test_set":False,
            "raw_test_timings":[100,101,102],
        }
        from decision import prospective_record
        result=prospective_record(template)
        self.assertEqual(result["status"],"RECEIVED_UNVERIFIED_FOR_RESEARCH_ONLY")
        self.assertFalse(result["algorithm_promoted"])
        fake=dict(template,source_external_custody_verified=True)
        self.assertEqual(prospective_record(fake)["status"],
                         "HOLD_UNVERIFIABLE_EXTERNAL_ATTESTATION")

    def test_forged_external_certificate_boolean_cannot_authorize(self):
        from decision import prospective_record
        base={
            "candidate_sha256":"1"*64,"reference_sha256":"2"*64,
            "preregistered_plan_sha256":"3"*64,
            "research_cost_ms":0,"proof_and_review_cost_ms":0,
            "rollback_cost_ms":0,"workload_family":"EXTERNAL_TEST",
            "outcome":"VERIFIED_GAIN","source_external_custody_verified":True,
            "source_generated_from_same_test_set":False,
            "raw_test_timings":[1,1,1]
        }
        self.assertEqual(prospective_record(base)["status"],
                         "HOLD_UNVERIFIABLE_EXTERNAL_ATTESTATION")
        bad=dict(base,candidate_sha256="broken")
        with self.assertRaises(HOLD):prospective_record(bad)

    def test_prospective_data_cannot_omit_rollback_or_source(self):
        from decision import prospective_record
        bad={
            "candidate_sha256":"1"*64,"reference_sha256":"2"*64,
            "preregistered_plan_sha256":"3"*64,
            "research_cost_ms":0,"proof_and_review_cost_ms":0,
            "workload_family":"TEST","outcome":"VERIFIED_GAIN",
            "source_external_custody_verified":False,
            "source_generated_from_same_test_set":False,
            "raw_test_timings":[1,1,1]
        }
        with self.assertRaises(HOLD):prospective_record(bad)

if __name__=="__main__":
    unittest.main()
