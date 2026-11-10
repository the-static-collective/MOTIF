"""GENIUS-010 adversarial convergence / source provenance / causal honesty."""
import json
import unittest

from convergence import (
    FAMILY_ALPHA, HYPOTHESES, MIN_EFFECT, REGIMES, THREADS, Observation,
    evaluate_candidate, evaluate_world, fisher_two_sided, generate,
    public_projection, rank_convergences, two_clock_convergence_packet,
)
from benchmark import HELDOUT_SEEDS, VALIDATION_SEEDS, run


class TestThreeIndependentThreads(unittest.TestCase):
    def test_fisher_exact_null_and_direction(self):
        self.assertEqual(fisher_two_sided(12, 24, 12, 24), 1)
        self.assertLess(fisher_two_sided(1, 24, 23, 24), 1e-8)
        self.assertAlmostEqual(
            fisher_two_sided(1, 24, 23, 24),
            fisher_two_sided(23, 24, 1, 24))
        with self.assertRaises(ValueError):
            fisher_two_sided(24, 23, 2, 24)

    def test_true_bridge_is_not_merely_shared_name(self):
        r=evaluate_world(101031, "HIDDEN_MOTIF")
        self.assertIn("hinge_timing", r["verdict"]["conditional_candidates"])
        self.assertNotIn("blue_ribbon", r["verdict"]["conditional_candidates"])
        self.assertEqual(r["verdict"]["lexical_only_baseline"], "blue_ribbon")
        self.assertEqual(r["verdict"]["status"],
                         "SYNTHETIC_CONDITIONAL_CONVERGENCE_CANDIDATE")
        self.assertEqual(len(r["weave"]["retrospective_callbacks"]), 3)
        self.assertTrue(r["no_external_action"])

    def test_convergence_requires_three_not_two_positive_threads(self):
        r=evaluate_world(101031, "PARTIAL")
        self.assertNotIn("hinge_timing", r["verdict"]["conditional_candidates"])
        by_hyp = {v["hypothesis"]: v for v in r["verdict"]["candidates"]}
        hinge=by_hyp["hinge_timing"]
        self.assertEqual(hinge["status"], "HOLD_CONVERGENCE_NOT_ESTABLISHED")
        rows={x["thread"]: x for x in hinge["interventional_replicates"]}
        self.assertFalse(rows["parcel"]["passes_direction_and_familywise_test"])
        self.assertEqual(len(r["weave"]["retrospective_callbacks"]), 0)

    def test_reverse_sign_is_not_a_joint_positive_cause(self):
        r=evaluate_world(101031, "REVERSED")
        self.assertNotIn("hinge_timing", r["verdict"]["conditional_candidates"])
        hinge=next(x for x in r["verdict"]["candidates"]
                   if x["hypothesis"] == "hinge_timing")
        signs={x["thread"]: x["risk_difference"]
               for x in hinge["interventional_replicates"]}
        self.assertGreater(signs["glasshouse"], 0)
        self.assertGreater(signs["broadcast"], 0)
        self.assertLess(signs["parcel"], 0)

    def test_confounded_observations_are_not_intervention_evidence(self):
        r=evaluate_world(101031, "CONFOUNDED")
        blue=next(x for x in r["verdict"]["candidates"]
                  if x["hypothesis"] == "blue_ribbon")
        self.assertTrue(all(
            x["observational_risk_difference"] > .5
            for x in blue["observational_associations"]))
        self.assertFalse(any(
            x["passes_direction_and_familywise_test"]
            for x in blue["interventional_replicates"]))
        self.assertEqual(r["verdict"]["conditional_candidates"], [])
        self.assertEqual(r["weave"]["retrospective_callbacks"], [])

    def test_echo_source_root_cannot_masquerade_as_three_witnesses(self):
        r=evaluate_world(101031, "ECHO_SOURCE")
        h=next(x for x in r["verdict"]["candidates"]
               if x["hypothesis"] == "hinge_timing")
        self.assertEqual(h["status"], "HOLD_NONINDEPENDENT_ORIGIN_ROOT")
        self.assertGreater(h["repeat_root_count"], 0)
        self.assertNotIn("hinge_timing", r["verdict"]["conditional_candidates"])
        self.assertFalse(r["weave"]["retrospective_callbacks"])

    def test_withheld_data_and_private_notes_never_cross_boundary(self):
        raw=generate(101031, "CONVERGENCE")
        shared=public_projection(raw)
        self.assertLess(len(shared),len(raw))
        self.assertTrue(all(not x.private_note for x in shared))
        out=rank_convergences(shared, randomization_attested=True)
        self.assertNotIn("PRIVATE_SIMULATOR_NOTE_NOT_TO_BE_EXPORTED",
                         json.dumps(out))
        nonpublic_ids={x.evidence_id for x in raw if not x.shareable}
        receipt_text=json.dumps(out)
        self.assertFalse(any(x in receipt_text for x in nonpublic_ids))
        self.assertTrue(out["no_real_world_causal_claim"])

    def test_no_automatic_causal_certification_even_on_three_significant_tests(self):
        shared=public_projection(generate(101031, "CONVERGENCE"))
        h=evaluate_candidate("hinge_timing", shared,
                             randomization_attested=True,
                             causal_mechanism_claim=True)
        self.assertEqual(h["status"], "CONDITIONAL_THREE_THREAD_CONVERGENCE")
        self.assertFalse(h["causal_mechanism_claim_allowed"])
        self.assertEqual(len(h["interventional_replicates"]), 3)
        self.assertTrue(all(
            row["two_sided_fisher_p"] <= h["per_comparison_alpha"]
            and row["risk_difference"] >= MIN_EFFECT
            and row["passes_direction_and_familywise_test"]
            for row in h["interventional_replicates"]))
        self.assertAlmostEqual(
            h["per_comparison_alpha"],
            FAMILY_ALPHA/(len(HYPOTHESES)*len(THREADS)))

    def test_attestation_is_not_cryptographic_authentication(self):
        shared=public_projection(generate(101031, "CONVERGENCE"))
        out=rank_convergences(shared, randomization_attested=False)
        self.assertFalse(out["conditional_candidates"])
        self.assertEqual(out["status"], "HOLD_NO_DEFENSIBLE_THREE_THREAD_BRIDGE")
        self.assertTrue(all(c["status"]=="HOLD_NO_VERIFIED_RANDOMIZATION"
                            for c in out["candidates"]))

    def test_no_replayed_receipt_even_with_new_origin_root(self):
        shared=list(public_projection(generate(101031, "CONVERGENCE")))
        row=next(x for x in shared if x.hypothesis=="hinge_timing")
        shared.append(Observation(
            row.hypothesis, row.thread, row.mode, row.assigned, row.outcome,
            row.evidence_id, "source://totally-different", True))
        h=evaluate_candidate("hinge_timing", tuple(shared),
                             randomization_attested=True)
        self.assertEqual(h["status"], "HOLD_REPLAYED_RECEIPT")

    def test_unredacted_report_is_rejected_even_if_shareable(self):
        raw=generate(101031,"CONVERGENCE")
        with self.assertRaises(ValueError):
            evaluate_candidate("hinge_timing",raw,randomization_attested=True)

    def test_two_clock_reinterpretation_not_retroactive_source_claim(self):
        r=evaluate_world(101031, "CONVERGENCE")
        packet=r["weave"]
        self.assertEqual(packet["status"],
                         "RESEARCH_ONLY_SOURCE_OWNED_REINTERPRETATION")
        self.assertEqual(len(packet["retrospective_callbacks"]),3)
        self.assertEqual(packet["original_witness_count"],3)
        self.assertEqual(set(packet["earlier_source_assertions"]),set(THREADS))
        for t in THREADS:
            self.assertEqual(packet["earlier_source_assertions"][t],
                             [f"{t} recorded a distinct unexplained anomaly"])
        self.assertTrue(all(c["status"]=="INTERPRETATION_NOT_TESTIMONY"
                            for c in packet["retrospective_callbacks"]))
        self.assertTrue(packet["no_original_record_edited"])

    def test_null_case_has_no_invented_callback(self):
        r=evaluate_world(101031,"NULL")
        self.assertEqual(r["verdict"]["conditional_candidates"],[])
        self.assertEqual(r["weave"]["retrospective_callbacks"],[])

    def test_strong_audited_classical_baseline_must_be_equally_good(self):
        for regime in REGIMES:
            r=evaluate_world(101031,regime)
            self.assertEqual(
                r["verdict"]["strong_classical_source_aware_baseline_candidates"],
                r["verdict"]["conditional_candidates"])
            self.assertTrue(r["no_external_action"])


class TestPrecommittedSyntheticHoldouts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report=run()

    def test_trial_freeze_provenance_and_source_outcomes(self):
        x=self.report
        self.assertEqual(x["status"],"RESEARCH_HOLD_ENGINEER_AUTHORED_CONVERGENCE")
        self.assertEqual(len(x["design_frozen_before_holdout_sha256"]),64)
        self.assertFalse(set(VALIDATION_SEEDS)&set(HELDOUT_SEEDS))
        self.assertEqual(set(x["holdout_summary"]),set(REGIMES))
        self.assertTrue(x["strong_classical_baseline_statistically_identical"])
        self.assertTrue(x["no_spiritual_historical_or_real_world_causal_claim"])
        self.assertTrue(x["no_external_action"])

    def test_positive_cases_supported_and_negative_families_have_no_bridge(self):
        rows=self.report["holdout_summary"]
        for name in ("CONVERGENCE","HIDDEN_MOTIF"):
            self.assertEqual(rows[name]["evaluated_cases"],len(HELDOUT_SEEDS))
            self.assertEqual(
                rows[name]["conditional_candidate_frequency"].get("hinge_timing"),
                len(HELDOUT_SEEDS))
        for name in ("NULL","CONFOUNDED","PARTIAL","REVERSED","ECHO_SOURCE"):
            self.assertEqual(rows[name]["any_conditional_bridge_cases"],0)
        self.assertEqual(rows["ECHO_SOURCE"]["source_or_attestation_hold_reasons"]
                         ["HOLD_NONINDEPENDENT_ORIGIN_ROOT"],len(HELDOUT_SEEDS))

    def test_receipts_are_source_attributed_not_secret_outcomes(self):
        x=self.report
        for name,case in x["source_owned_case_receipts"].items():
            self.assertEqual(case["regime"],name)
            self.assertTrue(case["withheld_not_scored_or_ingested"]>0)
            self.assertNotIn("PRIVATE_SIMULATOR_NOTE_NOT_TO_BE_EXPORTED",
                             json.dumps(case))
            for hyp in case["verdict"]["candidates"]:
                if "interventional_replicates" not in hyp:
                    continue
                for report in hyp["interventional_replicates"]:
                    self.assertEqual(
                        len(report["source_roots"]),len(report["evidence_refs"]))
                    self.assertTrue(all(x.startswith("receipt://")
                                        for x in report["evidence_refs"]))


if __name__=="__main__":
    unittest.main()
