import unittest
from dataclasses import replace

from benchmark import benchmark
from diagnostic import examine_room, run_policy
from grower import (
    QuestionOffer, IndependentReceipt, draft_questions, review_question
)
from oracle import TestWorld, problem, reviewed_receipts


class GrowingDiagnosticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hypotheses, cls.roads, cls.offers = problem()
        cls.proposals = {
            p.offer.name: p
            for p in draft_questions(
                [h.name for h in cls.hypotheses],
                cls.roads, cls.offers
            )
        }

    def test_invents_named_composite_question_from_typed_probes(self):
        proposal = self.proposals["FUSED_PORTS"]
        self.assertEqual(proposal.source_component_names, ("GLOBAL_A", "GLOBAL_B"))
        self.assertEqual(proposal.candidate.predicted["101"], '["0","1"]')
        self.assertFalse(proposal.candidate.allowed)
        self.assertEqual(proposal.status, "HOLD_UNREVIEWED")
        self.assertEqual(len(proposal.digest), 64)

    def test_no_sensor_or_cost_can_be_invented_without_provider(self):
        with self.assertRaises(ValueError):
            draft_questions(
                [h.name for h in self.hypotheses],
                self.roads,
                [QuestionOffer("MAGICAL", ("TARGET_ANSWER", "GLOBAL_A"),
                               "invented", 0.01)]
            )
        with self.assertRaises(ValueError):
            draft_questions(
                [h.name for h in self.hypotheses],
                self.roads,
                [QuestionOffer("DOUBLE", ("GLOBAL_A", "GLOBAL_A"),
                               "invented", 0.01)]
            )
        self.assertEqual(
            draft_questions([h.name for h in self.hypotheses], self.roads, ()),
            ()
        )

    def test_independent_finite_review_admits_only_synthetic_prediction(self):
        p = self.proposals["FUSED_PORTS"]
        r = review_question(p, reviewed_receipts(p.offer))
        self.assertEqual(r.status, "ELIGIBLE_SYNTHETIC_ONLY")
        self.assertEqual(r.reviewed, 16)
        self.assertFalse(r.counterexamples)
        self.assertTrue(r.admissible_road.allowed)
        self.assertEqual(r.authority, "SYNTHETIC_PREDICTION_ONLY")

    def test_declared_shortcut_fails_independent_counterexample(self):
        p = self.proposals["FALSE_SHORTCUT"]
        r = review_question(p, reviewed_receipts(p.offer))
        self.assertEqual(r.status, "REFUSE_INDEPENDENT_FALSIFICATION")
        self.assertIsNone(r.admissible_road)
        self.assertTrue(any(x.startswith("COUNTEREXAMPLE") for x in r.counterexamples))

    def test_forbidden_and_insufficient_review_stay_held(self):
        p = self.proposals["FORBIDDEN_PORTS"]
        r = review_question(p, ())
        self.assertEqual(r.status, "HOLD_PERMISSION")
        self.assertIsNone(r.admissible_road)
        valid = self.proposals["FUSED_PORTS"]
        self.assertEqual(
            review_question(valid, reviewed_receipts(valid.offer)[:2]).status,
            "HOLD_INSUFFICIENT_REVIEW",
        )

    def test_same_case_counted_twice_is_not_independent(self):
        p = self.proposals["FUSED_PORTS"]
        rs = list(reviewed_receipts(p.offer))
        rs[-1] = replace(rs[-1], case_id=rs[0].case_id)
        r = review_question(p, rs)
        self.assertEqual(r.status, "REFUSE_INDEPENDENT_FALSIFICATION")
        self.assertTrue(any(x.startswith("DUPLICATE_CASE") for x in r.counterexamples))

    def test_wrong_provider_phase_and_price_are_not_swept_under_rug(self):
        p = self.proposals["FUSED_PORTS"]
        rs = list(reviewed_receipts(p.offer))
        rs[1] = replace(rs[1], declared_provider="unrelated", phase="TEST", charged_cost=0.0)
        report = review_question(p, rs)
        self.assertEqual(report.status, "REFUSE_INDEPENDENT_FALSIFICATION")
        self.assertTrue(any(x.startswith("SOURCE_MISMATCH") for x in report.counterexamples))
        self.assertTrue(any(x.startswith("UNAUTHORIZED_PHASE") for x in report.counterexamples))
        self.assertTrue(any(x.startswith("COST_MISMATCH") for x in report.counterexamples))

    def test_meta_diagnostic_knows_fixed_perfect_accuracy_is_not_cost_optimal(self):
        p = self.proposals["FUSED_PORTS"]
        review = review_question(p, reviewed_receipts(p.offer))
        improvement = examine_room(self.hypotheses, self.roads, p, review)
        self.assertEqual(improvement.status, "ELIGIBLE_FOR_EXPLICIT_LOCAL_POLICY_REVIEW")
        self.assertAlmostEqual(improvement.incumbent_accuracy, 1.0)
        self.assertAlmostEqual(improvement.challenger_accuracy, 1.0)
        self.assertAlmostEqual(improvement.incumbent_mean_cost, 0.90)
        self.assertAlmostEqual(improvement.challenger_mean_cost, 0.65)
        self.assertAlmostEqual(improvement.measured_cost_gap, 0.25)
        self.assertEqual(improvement.authority, "NO_AUTOMATIC_POLICY_INSTALL")

    def test_grown_method_does_not_force_an_unhelpful_expensive_change(self):
        p = self.proposals["OVERPRICED_PORTS"]
        review = review_question(p, reviewed_receipts(p.offer))
        self.assertEqual(review.status, "ELIGIBLE_SYNTHETIC_ONLY")
        inspect = examine_room(self.hypotheses, self.roads, p, review)
        self.assertEqual(inspect.status, "HOLD_NO_VALIDATED_IMPROVEMENT")
        self.assertAlmostEqual(inspect.challenger_mean_cost, 0.90)
        self.assertAlmostEqual(inspect.measured_cost_gap, 0.0)

    def test_unreviewed_candidate_cannot_be_installed_or_used(self):
        p = self.proposals["FUSED_PORTS"]
        bad = review_question(p, ())
        d = examine_room(self.hypotheses, self.roads, p, bad)
        self.assertEqual(d.status, "HOLD_UNVERIFIED")
        with self.assertRaises(ValueError):
            run_policy("GROWN_FOREST", self.hypotheses, self.roads,
                       TestWorld("101", "TEST"), p.candidate, p)

    def test_refitted_strong_classical_optimum_ties_the_new_method(self):
        p = self.proposals["FUSED_PORTS"]
        r = review_question(p, reviewed_receipts(p.offer))
        for h in self.hypotheses:
            w = TestWorld(h.name, "TEST")
            grown = run_policy("GROWN_FOREST", self.hypotheses, self.roads, w,
                               r.admissible_road, p)
            classical = run_policy("CLASSICAL_EXACT_REFIT", self.hypotheses, self.roads,
                                   w, r.admissible_road, p)
            self.assertEqual(grown.cost, classical.cost)
            self.assertEqual(grown.correct, classical.correct)
            self.assertTrue(grown.correct)
            self.assertAlmostEqual(grown.cost, .65)
            self.assertEqual(grown.selected, (("FUSED_PORTS",),))

    def test_after_review_hidden_drift_can_make_forest_confidently_wrong(self):
        p = self.proposals["DRIFT_FUSED_PORTS"]
        r = review_question(p, reviewed_receipts(p.offer))
        self.assertEqual(r.status, "ELIGIBLE_SYNTHETIC_ONLY")
        result = [
            run_policy("GROWN_FOREST", self.hypotheses, self.roads,
                       TestWorld(h.name, "TEST"), r.admissible_road, p)
            for h in self.hypotheses
        ]
        self.assertEqual(sum(x.correct for x in result), 4)
        self.assertEqual(sum(x.holding for x in result), 0)
        self.assertFalse(all(x.correct for x in result))

    def test_documented_frozen_benchmark_preserves_both_pos_and_negative(self):
        result = benchmark()
        good = result["heldout"]["FUSED_PORTS"]
        drift = result["heldout"]["DRIFT_FUSED_PORTS"]
        self.assertEqual(good["frozen_original"]["correct_of_8"], 8)
        self.assertEqual(good["grown_forest"]["correct_of_8"], 8)
        self.assertAlmostEqual(good["grown_forest"]["mean_query_cost"], .65)
        self.assertAlmostEqual(good["classical_exact_refit"]["mean_query_cost"], .65)
        self.assertEqual(drift["grown_forest"]["correct_of_8"], 4)
        self.assertEqual(len(drift["failures"]), 4)
        self.assertFalse(result["explicit_boundaries"]["adopted_live"])


if __name__ == "__main__":
    unittest.main()
