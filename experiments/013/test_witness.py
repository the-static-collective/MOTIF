"""MOTIF-013: stochastic uncertainty, provenance, Bayesian comparisons, abstention."""
from __future__ import annotations
from dataclasses import replace
from pathlib import Path
import inspect
import json
import math
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"008"))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"009"))
sys.path.insert(0,str(Path(__file__).resolve().parent))
import oracle
import benchmark  # Resolve local evaluator before 009 imports add older benchmark paths.
import witness_model as model
from cartridge import validate_cartridge


class ProbabilisticWitnessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.w=oracle.world("FIRST",11)
        cls.audit=oracle.calibration(cls.w)
        cls.samples=oracle.records(cls.w,"train",benchmark.TRAIN)
        cls.public=tuple(x.public for x in cls.samples)
        cls.fit=model.fit(cls.audit,cls.public)

    def test_oracle_hidden_from_learner_module(self):
        source=inspect.getsource(model)
        self.assertNotIn("import oracle",source)
        self.assertNotIn("from oracle import",source)
        self.assertNotIn("true_mechanism(",source)
        self.assertNotIn("success_probability(spec",source)

    def test_public_graph_excludes_latent_outcome_and_private_world(self):
        visible=self.samples[0].public
        self.assertFalse(hasattr(visible,"truth"))
        self.assertFalse(hasattr(visible,"realized"))
        self.assertFalse(hasattr(visible,"family"))
        self.assertFalse(hasattr(visible,"source_accuracies"))
        self.assertTrue(isinstance(visible.before,frozenset))
        self.assertIn(("pending",visible.roles[1]),visible.before)

    def test_heldout_actual_interventions_not_accidentally_revealed(self):
        test=oracle.records(self.w,"test",120)
        self.assertTrue(all(t.public.audited_applied is None for t in test))
        self.assertTrue(all(not hasattr(t.public,"truth") for t in test))

    def test_seeded_bernoulli_outcomes_are_reproducible_but_not_deterministic_rules(self):
        x=oracle.records(self.w,"test",120)
        self.assertEqual(x,oracle.records(self.w,"test",120))
        for intended in oracle.PAIRS:
            outcomes=[case.truth for case in x if case.public.commanded==intended]
            self.assertTrue(any(outcomes))
            self.assertTrue(not all(outcomes))
        self.assertNotEqual(x,oracle.records(oracle.world("FIRST",23),"test",120))

    def test_noise_and_compliance_failures_actually_occur(self):
        records=oracle.records(self.w,"test",120)
        self.assertGreater(sum(case.realized!=case.public.commanded for case in records),8)
        self.assertGreater(sum(any(report.claim!=case.truth
             for report in case.public.witnesses) for case in records),20)

    def test_audited_calibration_is_separate_from_training_truth(self):
        self.assertEqual(len(self.audit.source_accuracy_counts),3)
        self.assertEqual(len(self.audit.actuator_compliance_counts),2)
        self.assertEqual(sum(row[2] for row in self.audit.source_accuracy_counts),180)
        self.assertEqual(sum(row[2] for row in self.audit.actuator_compliance_counts),160)
        self.assertFalse(hasattr(self.audit,"family"))
        self.assertFalse(hasattr(self.audit,"truth"))

    def test_posterior_source_reliabilities_can_be_below_half(self):
        origins=self.fit.origins()
        self.assertGreater(origins["source_0"],.75)
        self.assertLess(origins["source_2"],.5)
        self.assertGreater(self.fit.compliance_means()[0],.5)

    def test_contrarian_source_is_not_falsely_treated_as_friendly_witness(self):
        a=model._witness_likelihood((("source_2",False),),
                                     {"source_2":.2},True)
        b=model._witness_likelihood((("source_2",False),),
                                     {"source_2":.2},False)
        self.assertAlmostEqual(a,.8)
        self.assertAlmostEqual(b,.2)
        self.assertGreater(a,b)

    def test_same_upstream_forwarded_claims_count_once(self):
        stripped=tuple(replace(x,witnesses=tuple(w for w in x.witnesses
                     if w.reporter!="source_0_forwarded")) for x in self.public)
        no_copies=model.fit(self.audit,stripped)
        for key,p in self.fit.posterior:
            self.assertAlmostEqual(p,dict(no_copies.posterior)[key],places=12)
        self.assertGreater(self.fit.duplicate_forwarded_claims,0)
        self.assertEqual(no_copies.duplicate_forwarded_claims,0)
        self.assertEqual(no_copies.independent_origins,
                         self.fit.independent_origins)

    def test_conflicting_reports_within_one_origin_are_held(self):
        a=oracle.Witness("source_0","original",True)
        b=oracle.Witness("source_0","forwarded",False)
        fabricated=replace(self.public[0],witnesses=(a,b))
        with self.assertRaisesRegex(model.HOLD,"Contradictory"):
            model.fit(self.audit,(fabricated,))

    def test_unverified_non_synthetic_provenance_is_held(self):
        bad=replace(self.public[0],provenance="CLAIMED_EXTERNAL_TRUTH")
        with self.assertRaisesRegex(model.HOLD,"Only local synthetic"):
            model.fit(self.audit,(bad,))

    def test_missing_actual_control_receipt_prevents_causal_attribution(self):
        row=self.public[0]
        base=model.fit(self.audit,())
        held=model.fit(self.audit,(replace(row,audited_applied=None),))
        self.assertEqual(base.posterior,held.posterior)
        self.assertEqual(held.unverifiable_actuation,1)
        self.assertEqual(held.admissible_records,0)

    def test_missing_witness_outcome_does_not_count_as_observation(self):
        real=next(x for x in self.public if x.audited_applied is not None)
        empty=replace(real,witnesses=())
        estimate=model.fit(self.audit,(empty,))
        self.assertEqual(estimate.admissible_records,0)
        self.assertEqual(estimate.missing_witnesses,1)

    def test_source_calibration_cannot_be_forged_as_a_real_claim(self):
        with self.assertRaisesRegex(model.HOLD,"independent synthetic"):
            model.fit(replace(self.audit,provenance="AUTHENTICATED_REAL"),())

    def test_missing_actuator_calibration_blocks_model(self):
        with self.assertRaisesRegex(model.HOLD,"Missing independent"):
            model.fit(replace(self.audit,actuator_compliance_counts=(
                self.audit.actuator_compliance_counts[0],)),())

    def test_log_space_posterior_is_normalized_and_nonnegative(self):
        masses=self.fit.masses()
        self.assertAlmostEqual(sum(masses.values()),1.0,places=12)
        self.assertEqual(set(masses),set(model.ALL))
        self.assertTrue(all(0<=x<=1 for x in masses.values()))
        self.assertGreater(masses["FIRST"],.95)

    def test_future_commands_include_uncertain_actuator_compliance(self):
        p=model.predict(self.fit,(True,False))
        self.assertGreater(p,.5)
        # Lower than the known successful-control probability .85 because
        # intended settings sometimes fail to be realized.
        self.assertLess(p,.85)

    def test_source_beta_interval_is_genuine_distribution_not_single_point(self):
        from_model=model.source_reliability_intervals(self.fit,seed=4,draws=800)
        self.assertEqual(len(from_model),3)
        for row in from_model.values():
            low,high=row["interval_90"]
            self.assertLess(low,row["posterior_mean"])
            self.assertLess(row["posterior_mean"],high)
            self.assertFalse(row["real_world_source_identity_verified"])

    def test_model_and_compliance_interval_is_explicitly_conditional(self):
        low,high=model.confidence_intervals(self.fit,(False,True),seed=3,draws=400)
        self.assertTrue(0<=low<=high<=1)
        self.assertGreater(high-low,0)

    def test_matched_bayesian_baseline_uses_same_audited_reports(self):
        cell=benchmark.bayesian_four_cell(self.public,self.fit)
        self.assertEqual(set(cell),set(oracle.PAIRS))
        self.assertTrue(all(.01<p<.99 for p in cell.values()))
        q=benchmark.four_cell_forecast(cell,self.fit,(True,False))
        self.assertGreaterEqual(q,0)
        self.assertLessEqual(q,1)

    def test_nonparametric_baseline_not_guaranteed_to_lose(self):
        report=benchmark.benchmark()["summary"]
        self.assertGreater(report["mean_internal_brier"],0)
        self.assertGreater(report["mean_classical_bayesian_four_cell_brier"],0)
        self.assertEqual(report["comparison_classical_bayesian_independent_cells"],
                         True)
        self.assertEqual(report["heldout_trial_total"],3600)

    def test_model_family_has_explicit_unknown_not_a_fabricated_tree(self):
        self.assertAlmostEqual(model.outcome_probability("OTHER",(False,True)),.5)
        self.assertNotIn("OTHER",model.PROGRAMS)
        self.assertEqual(len(model.PROGRAMS),4)

    def test_xor_can_expose_model_inadequacy_without_false_causal_certainty(self):
        values=[benchmark.evaluate("XOR",seed) for seed in oracle.SEEDS]
        self.assertTrue(any(x["other_posterior"]>.4 for x in values))
        self.assertTrue(any(x["issued_prediction_coverage"]<1 for x in values))
        # We do NOT claim all unsupported worlds were identified.
        self.assertTrue(any(x["issued_prediction_coverage"]==1 for x in values))

    def test_shift_can_be_detected_on_validation_without_test_labels(self):
        shifts=[benchmark.evaluate("SHIFT",seed) for seed in oracle.SEEDS]
        self.assertTrue(any(x["validation_drift_warning"]["shift_warning"]
                            for x in shifts))
        self.assertTrue(any(x["issued_prediction_coverage"]==1
                            for x in shifts))
        # Unknown distribution changes are not reliably detected in 5 worlds.

    def test_validation_warning_freezes_training_model(self):
        b=model.fit(self.audit,self.public)
        value=model.event_predictive_log_ratio(
            b,tuple(x.public for x in oracle.records(self.w,"validation",32)))
        self.assertEqual(b,self.fit)
        self.assertGreater(value["validation_independent_records"],0)

    def test_brier_and_logloss_are_proper_scoring_rules(self):
        self.assertAlmostEqual(benchmark.brier(True,1),0)
        self.assertAlmostEqual(benchmark.brier(True,0),1)
        self.assertGreater(benchmark.logloss(True,.1),
                           benchmark.logloss(True,.9))
        self.assertGreater(benchmark.brier(False,.8),
                           benchmark.brier(False,.3))

    def test_calibration_reports_bins_and_frequency_without_leak(self):
        values=[0,1,1,0]
        preds=[.05,.95,.55,.45]
        stat=benchmark.calibration_summary(values,preds)
        self.assertAlmostEqual(sum(x["n"] for x in stat["bins"]),4)
        self.assertGreaterEqual(stat["ece"],0)
        self.assertLessEqual(stat["ece"],1)

    def test_synthetic_question_is_bounded_not_executed(self):
        start=model.fit(self.audit,())
        p=model.choose_question(start,allowed=model.PAIRS,
                                costs={x:1 for x in model.PAIRS},budget=2)
        self.assertEqual(p["status"],"PROPOSE_SYNTHETIC_ONLY")
        self.assertFalse(p["world_actuated"])
        self.assertFalse(p["human_authority_verified"])
        self.assertGreater(p["information_bits_if_all_origins_report"],0)

    def test_unsafe_or_unaffordable_information_is_not_dispatched(self):
        start=model.fit(self.audit,())
        costs={x:5 for x in model.PAIRS}
        blocked=model.choose_question(start,allowed=(),costs=costs,budget=2)
        self.assertEqual(blocked["status"],"HOLD_UNSAFE")
        broke=model.choose_question(start,allowed=model.PAIRS,
                                    costs=costs,budget=2)
        self.assertEqual(broke["status"],"HOLD_BUDGET")
        self.assertIsNone(blocked["command"])
        self.assertIsNone(broke["command"])

    def test_four_real_decision_tree_cartridges_keep_unresolved_mass(self):
        candidate=model.tree_cartridges(
            self.fit,self.public,self.w.control_predicates)
        self.assertEqual(candidate["schema"],
                         "motif.probabilistic-tree-ensemble.v0")
        self.assertEqual(candidate["status"],"HOLD_PROPOSAL_ONLY")
        self.assertEqual(len(candidate["components"]),4)
        self.assertTrue(candidate[
            "source_counts_are_unadjudicated_witness_claims"])
        self.assertFalse(candidate["real_world_authority"])
        self.assertAlmostEqual(sum(x["posterior_weight"]
            for x in candidate["components"])+candidate["unmodeled_mass"],
            1.0,places=6)
        for data in candidate["components"]:
            recovered=validate_cartridge(json.dumps(data["tree"]))
            self.assertEqual(data["tree"]["id"],recovered.id)
        self.assertNotIn("e13_",json.dumps(candidate))

    def test_artifact_content_hash_does_not_claim_origin_authentication(self):
        from cartridge import checksum
        item=model.tree_cartridges(
            self.fit,self.public,self.w.control_predicates)
        body={k:v for k,v in item.items() if k!="checksum_sha256"}
        self.assertEqual(checksum(body),item["checksum_sha256"])
        self.assertNotIn("authenticated_source",item)

    def test_report_proves_truth_not_read_by_model_and_maintains_coverage(self):
        r=benchmark.benchmark()
        s=r["summary"]
        self.assertFalse(s["heldout_truth_exposed_to_learner"])
        self.assertFalse(s["training_truth_exposed_to_learner"])
        self.assertTrue(s["model_is_approximate_plug_in_bayesian"])
        self.assertEqual(s["external_actions"],0)
        self.assertGreater(s["sum_deduplicated_forwarded_claims"],0)
        self.assertGreater(s["sum_held_unverified_controls"],0)
        self.assertTrue(0<=s["overall_prediction_issued_coverage"]<=1)

    def test_complete_ci_receipt_matches_fresh_stochastic_seeded_runs(self):
        archive=json.loads((Path(__file__).parent/
                            "experiment-results.json").read_text())
        self.assertEqual(archive,benchmark.benchmark())


if __name__=="__main__":
    unittest.main()
