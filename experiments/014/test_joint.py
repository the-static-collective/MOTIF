"""MOTIF-014 — falsifiers for credibility-of-credibility and model uncertainty."""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import importlib.util
import inspect
import json
import unittest

# Keep local evaluator ahead of inherited 009/008 paths on import.
import oracle
import benchmark
import joint
from cartridge import validate_cartridge,checksum


class WitnessOfWitnessesTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.spec=oracle.create_world("FIRST",11)
        cls.private_cal=oracle.calibration_set(cls.spec,benchmark.CALIBRATION)
        cls.private_train=oracle.trial_set(cls.spec,"train",benchmark.TRAIN)
        cls.cal=tuple(c.public for c in cls.private_cal)
        cls.train=tuple(t.public for t in cls.private_train)
        cls.estimate=joint.fit(cls.cal,cls.train,
                               cls.spec.predicate_names,grammar="motif")

    def test_joint_learner_does_not_import_oracle_or_read_secret_truth(self):
        s=inspect.getsource(joint)
        self.assertNotIn("import oracle",s)
        self.assertNotIn("from oracle import",s)
        self.assertNotIn("secret.truth",s)
        self.assertNotIn("hidden_rule(",s)

    def test_public_calibration_contains_no_true_labels(self):
        c=self.cal[0]
        self.assertFalse(hasattr(c,"truth"))
        self.assertFalse(hasattr(c,"world"))
        self.assertFalse(hasattr(c,"actual_success"))
        self.assertIn(c.provenance,("SYNTHETIC_UNADJUDICATED_CALIBRATION",))

    def test_public_action_contains_no_true_outcome_or_realized_control(self):
        t=self.train[0]
        self.assertFalse(hasattr(t,"truth"))
        self.assertFalse(hasattr(t,"actually_applied"))
        self.assertFalse(hasattr(t,"family"))
        self.assertIsInstance(t.before,frozenset)

    def test_stochastic_outcomes_not_deterministic_rules(self):
        outcomes=oracle.trial_set(self.spec,"test",96)
        self.assertEqual(outcomes,oracle.trial_set(self.spec,"test",96))
        for pair in oracle.PORTS:
            labels=[x.truth for x in outcomes if x.public.requested==pair]
            self.assertTrue(any(labels))
            self.assertTrue(not all(labels))

    def test_calibration_is_truth_latent_even_when_auditor_reports(self):
        c=self.private_cal
        self.assertTrue(any(x.public.audit_says_success != x.truth
            for x in c if x.public.audit_says_success is not None))
        self.assertTrue(any(x.public.audit_says_success is None for x in c))

    def test_actual_implementation_of_noncompliance_and_bad_receipts(self):
        items=oracle.trial_set(self.spec,"train",96)
        self.assertGreater(sum(x.actually_applied != x.public.requested
                               for x in items),5)
        audit=[x for x in items
               if x.public.audit_says_first_port_applied is not None]
        self.assertTrue(any(x.public.audit_says_first_port_applied !=
                             x.actually_applied[0] for x in audit))

    def test_shared_upstream_forwarders_dont_inflate_posterior(self):
        drop=lambda records:tuple(replace(x,reporters=tuple(
            claim for claim in x.reporters if claim.reporter!="s0_forward"))
            for x in records)
        without=joint.fit(drop(self.cal),drop(self.train),
                          self.spec.predicate_names)
        self.assertGreater(self.estimate.forwarded_duplicates,0)
        self.assertEqual(without.forwarded_duplicates,0)
        for a,b in zip(self.estimate.weights,without.weights):
            self.assertAlmostEqual(a,b,places=14)

    def test_contradictory_forwarder_same_origin_is_held(self):
        source=oracle.Witness("s0","original",True)
        forwarded=oracle.Witness("s0","s0_forward",False)
        bad=replace(self.cal[0],reporters=(source,forwarded))
        with self.assertRaisesRegex(joint.HOLD,"Conflicting testimony"):
            joint.fit((bad,)+self.cal[1:],self.train,self.spec.predicate_names)

    def test_unverified_real_claim_cannot_replace_synthetic_evidence(self):
        fake=replace(self.cal[0],provenance="SIGNED_REAL_CERTIFICATE")
        with self.assertRaises(joint.HOLD):
            joint.fit((fake,)+self.cal[1:],self.train,self.spec.predicate_names)

    def test_disagreeing_witnesses_are_integrated_not_majority_voted(self):
        disagree=[x for x in self.train if
                  len({r.says_success for r in x.reporters})>1]
        self.assertGreater(len(disagree),0)
        posterior=self.estimate
        self.assertAlmostEqual(sum(posterior.weights),1,places=12)
        self.assertEqual(len(posterior.states),960)

    def test_auditor_uncertainty_is_jointly_retained(self):
        result=self.estimate
        q=result.parameter_means()["q"]
        interval=result.parameter_interval("q")
        self.assertTrue(.58<=interval[0]<=interval[1]<=.95)
        self.assertTrue(interval[0]<=q<=interval[1])
        self.assertTrue(len({s.q for s,w in zip(result.states,result.weights)
                             if w>1e-14})>1)

    def test_auditor_wrong_claims_alter_posterior_not_ground_truth(self):
        modified=tuple(replace(x,audit_says_success=(
            not x.audit_says_success if x.audit_says_success is not None
            else None)) for x in self.cal)
        shifted=joint.fit(modified,self.train,self.spec.predicate_names)
        self.assertNotEqual(
            round(self.estimate.parameter_means()["q"],6),
            round(shifted.parameter_means()["q"],6))

    def test_below_chance_source_possible_in_grid(self):
        r1=self.estimate.parameter_means()["r1"]
        self.assertLess(r1,.5)
        self.assertIn(.2,joint.R_GRID)
        self.assertNotEqual(r1,.5)

    def test_audit_and_actuator_mean_uncertainty_not_preapproved(self):
        params=self.estimate.parameter_means()
        self.assertTrue(.58<=params["q"]<=.95)
        self.assertTrue(.55<=params["c"]<=.92)
        self.assertTrue(.2<=params["r0"]<=.9)

    def test_missing_audit_is_marginalized_not_discarded(self):
        self.assertGreater(self.estimate.missing_audit_receipts,0)
        self.assertEqual(self.estimate.intervention_count,benchmark.TRAIN)
        no_audit=tuple(replace(x,audit_says_first_port_applied=None)
                       for x in self.train)
        fit=joint.fit(self.cal,no_audit,self.spec.predicate_names)
        self.assertEqual(fit.intervention_count,benchmark.TRAIN)
        self.assertEqual(fit.missing_audit_receipts,benchmark.TRAIN)

    def test_graph_must_match_commanded_not_imaginary_applied_control(self):
        x=self.train[0]
        changed=replace(x,requested=(not x.requested[0],x.requested[1]))
        with self.assertRaisesRegex(joint.HOLD,"Command graph"):
            joint.fit(self.cal,(changed,)+self.train[1:],
                      self.spec.predicate_names)

    def test_invalid_non_boolean_report_is_refused(self):
        x=self.cal[0]
        report=oracle.Witness("s1","s1","uncertain")
        altered=replace(x,reporters=(report,))
        with self.assertRaises(joint.HOLD):
            joint.fit((altered,)+self.cal[1:],self.train,
                      self.spec.predicate_names)

    def test_r0_calibration_is_not_assumed_true_at_one(self):
        p=self.estimate.parameter_means()["r0"]
        self.assertTrue(.2<p<=.9)
        self.assertNotEqual(p,1)

    def test_full_grammar_is_more_expansive_on_identical_input(self):
        expanded=joint.fit(self.cal,self.train,self.spec.predicate_names,
                           grammar="all_boolean")
        self.assertEqual(len(expanded.states),17*4*4*4*3)
        self.assertEqual(len(expanded.model_weights()),17)
        self.assertAlmostEqual(sum(expanded.weights),1,places=12)
        self.assertIn("BOOL_0110",expanded.model_weights()) # XOR

    def test_forecast_and_epistemic_interval_are_bounded(self):
        for pair in joint.PAIRS:
            p=self.estimate.forecast(pair)
            lo,hi=self.estimate.predictive_interval(pair)
            self.assertTrue(0<p<1)
            self.assertTrue(0<=lo<=p<=hi<=1)

    def test_calibration_likelihood_marginalizes_unknown_truth(self):
        state=self.estimate.states[0]
        example=(True,False,True)
        likelihood=joint.calibration_likelihood(example,state)
        self.assertTrue(0<likelihood<1)
        self.assertNotAlmostEqual(likelihood,.5)

    def test_intervention_likelihood_marginalizes_unseen_applied_setting(self):
        state=self.estimate.states[0]
        full=((True,False),True,False,None)
        likelihood=joint.intervention_likelihood(full,state)
        self.assertTrue(0<likelihood<1)
        self.assertNotEqual(state.c,1)

    def test_shift_diagnostic_is_frozen_and_does_not_update_models(self):
        before=self.estimate.weights
        validation=tuple(x.public for x in
                         oracle.trial_set(self.spec,"validation",24))
        reported=joint.validation_diagnostic(self.estimate,validation,
                                             self.spec.predicate_names)
        self.assertEqual(before,self.estimate.weights)
        self.assertEqual(reported["records"],24)
        self.assertTrue(reported["threshold_is_heuristic_not_calibrated"])

    def test_decision_can_abstain_without_removing_internal_forecast(self):
        hold=joint.decide(self.estimate,(False,True),shift_warning=True)
        self.assertEqual(hold["status"],"HOLD_RELIABILITY_OR_MECHANISM_SHIFT")
        self.assertTrue(0<hold["forecast_success"]<1)
        self.assertFalse(hold["verified_real_world_authority"])

    def test_questions_include_meta_calibration_and_no_actuator_dispatch(self):
        suggestion=joint.propose_inquiry(self.estimate,budget=2)
        self.assertEqual(suggestion["status"],"PROPOSE_SYNTHETIC_ONLY")
        self.assertIn(suggestion["action"],("CALIBRATION","INTERVENTION"))
        self.assertFalse(suggestion["real_world_authority"])
        self.assertGreater(suggestion["expected_joint_information_bits"],0)

    def test_policy_rejects_forbidden_and_over_budget_questions(self):
        rejected=joint.propose_inquiry(self.estimate,allowed=(),budget=2)
        unfunded=joint.propose_inquiry(self.estimate,budget=0)
        self.assertEqual(rejected["status"],"HOLD_UNSAFE")
        self.assertEqual(unfunded["status"],"HOLD_BUDGET")
        self.assertIsNone(rejected["action"])
        self.assertIsNone(unfunded["settings"])

    def test_out_of_grammar_xor_cannot_be_assumed_first(self):
        self.assertEqual(joint.outcome_probability("FIRST",(True,True)),.88)
        self.assertEqual(joint.outcome_probability("BOOL_0110",(True,True)),.12)
        self.assertEqual(joint.outcome_probability("OTHER",(True,True)),.5)

    def test_checksum_validated_portable_009_trees_remain_held(self):
        artifact=joint.cartridge_ensemble(
            self.estimate,self.train,self.spec.predicate_names)
        self.assertEqual(artifact["status"],"HOLD_PROPOSAL_ONLY")
        self.assertTrue(artifact["source_and_auditor_identities_are_not_authenticated"])
        self.assertEqual(len(artifact["components"]),4)
        self.assertFalse(artifact["real_world_authority"])
        body={k:v for k,v in artifact.items() if k!="checksum_sha256"}
        self.assertEqual(artifact["checksum_sha256"],checksum(body))
        self.assertNotIn("w14_",json.dumps(artifact))
        for part in artifact["components"]:
            self.assertEqual(validate_cartridge(json.dumps(part["tree"])).id,
                             part["tree"]["id"])

    def test_comparison_uses_same_stochastic_simulation_and_no_test_truth_for_fit(self):
        x=benchmark.evaluate("FIRST",11)
        self.assertEqual(x["training_events_used_in_joint_update"],48)
        self.assertEqual(x["heldout"],benchmark.TEST)
        self.assertTrue(x["stochastic_outcomes_belong_to_evaluator_only"])
        self.assertEqual(x["real_world_operations"],0)
        self.assertEqual(x["classical_16_boolean_models_plus_other"],17)
        self.assertEqual(x["motif_tree_models_plus_other"],5)

    def test_distribution_shift_changes_actual_hidden_channel(self):
        for name,offset in (("SOURCE_SHIFT",0),("AUDIT_SHIFT",2),
                            ("COMPLIANCE_SHIFT",3)):
            spec=oracle.create_world(name,11)
            self.assertNotEqual(
                oracle.rates(spec,"train")[offset],
                oracle.rates(spec,"validation")[offset])

    def test_probability_scoring_penalizes_confidence_in_stochastic_world(self):
        self.assertAlmostEqual(benchmark.brier(True,1),0)
        self.assertAlmostEqual(benchmark.brier(True,0),1)
        self.assertGreater(benchmark.logloss(True,.01),
                           benchmark.logloss(True,.9))

    def test_full_receipt_is_identical_to_new_seeded_stochastic_rerun(self):
        location=Path(__file__).parent/"experiment-results.json"
        self.assertEqual(json.loads(location.read_text()),benchmark.benchmark())


if __name__=="__main__":
    unittest.main()
