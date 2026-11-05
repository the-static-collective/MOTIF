import threading
import unittest
from dataclasses import replace

from benchmark import benchmark
from demo import fixture
from forest import LivingForest, Road
from multiplex import Hypothesis, best_answer


class LivingForestTests(unittest.TestCase):
    def setUp(self):
        self.hypotheses, self.roads = fixture()

    def test_lookahead_sees_future_affordance_not_immediate_gain(self):
        forest = LivingForest(self.hypotheses, self.roads)
        plan = forest.plan()
        self.assertEqual(plan.selected, ("SCOUT",))
        self.assertEqual(plan.status, "MULTI_INQUIRY")
        self.assertAlmostEqual(plan.current_accuracy, 0.5)
        self.assertAlmostEqual(plan.expected_final_accuracy, 1.0)
        self.assertAlmostEqual(plan.expected_total_cost, 0.90)
        self.assertEqual(len(plan.forecasts), 2)
        expected = {
            (("SCOUT", "0"),): ("FAST_A_0", "FAST_B_0"),
            (("SCOUT", "1"),): ("FAST_A_1", "FAST_B_1"),
        }
        for forecast in plan.forecasts:
            self.assertEqual(forecast.next_selected, expected[forecast.result])
            self.assertEqual(forecast.newly_available, expected[forecast.result])
            self.assertAlmostEqual(forecast.probability, 0.5)
        self.assertEqual(forest.observed, {})  # imagining is not observing

    def test_two_rounds_actual_branch_prunes_and_stops(self):
        forest = LivingForest(self.hypotheses, self.roads)
        first, receipt = forest.run_synthetic_round(lambda road: road.predicted["101"])
        self.assertEqual(first.selected, ("SCOUT",))
        self.assertEqual(receipt.newly_available, ("FAST_A_1", "FAST_B_1"))
        self.assertEqual(len(forest.live), 4)
        second, observed = forest.run_synthetic_round(lambda road: road.predicted["101"])
        self.assertEqual(second.selected, ("FAST_A_1", "FAST_B_1"))
        self.assertEqual(observed.status, "ANSWER")
        self.assertEqual(forest.live, ("101",))
        self.assertEqual(best_answer(forest._posterior(forest.live)), ("YES", 1.0))
        self.assertAlmostEqual(forest.spent, 0.90)
        self.assertEqual(forest.plan().selected, ())
        self.assertEqual(len(forest.history), 2)

    def test_second_level_is_actually_concurrent(self):
        forest = LivingForest(self.hypotheses, self.roads)
        forest.run_synthetic_round(lambda road: road.predicted["011"])
        barrier = threading.Barrier(2)
        def resolver(road):
            barrier.wait(timeout=5)
            return road.predicted["011"]
        plan, witnessed = forest.run_synthetic_round(resolver)
        self.assertEqual(set(plan.selected), {"FAST_A_0", "FAST_B_0"})
        self.assertEqual(witnessed.status, "ANSWER")

    def test_contradicting_evidence_is_held_with_provenance(self):
        forest = LivingForest(self.hypotheses, self.roads)
        plan = forest.plan()
        old = forest.live
        record = forest.accept(plan, {"SCOUT": "UNKNOWN"})
        self.assertEqual(record.status, "HOLD_MODEL_FALSIFIED")
        self.assertEqual(forest.live, old)
        self.assertEqual(forest.observed, {})
        self.assertAlmostEqual(forest.spent, 0.20)
        self.assertEqual(len(forest.counterexamples), 1)
        self.assertEqual(forest.counterexamples[0]["reported"][0][1], "scout-source")
        self.assertEqual(forest.plan().status, "HOLD_MODEL_FALSIFIED")

    def test_prohibit_unauthorized_and_duplicate_sources(self):
        forest = LivingForest(self.hypotheses, self.roads)
        self.assertNotIn("BLOCKED", forest.plan().selected)
        self.assertNotIn("DUP_SCOUT", forest.plan().selected)
        self.assertEqual(forest._ready({})[0].name, "BAIT")
        self.assertNotIn("DUP_SCOUT", [r.name for r in forest._ready({})])
        with self.assertRaises(ValueError):
            forest.accept(forest.plan(), {"BLOCKED": "YES"})
        with self.assertRaises(ValueError):
            forest.accept(forest.plan(), {})

    def test_tentative_answer_can_coexist_with_new_question(self):
        hypotheses = [Hypothesis("yes", "YES", 0.85), Hypothesis("no", "NO", 0.15)]
        roads = [Road("CHECK", "VERIFY", 0.20,
                      {"yes": "Y", "no": "N"}, "independent")]
        forest = LivingForest(hypotheses, roads, budget=0.5)
        plan = forest.plan()
        self.assertEqual(plan.status, "ANSWER_AND_EXPLORE")
        self.assertEqual(plan.tentative_answer, "YES")
        self.assertEqual(plan.selected, ("CHECK",))
        forest.run_synthetic_round(lambda road: road.predicted["no"])
        self.assertEqual(forest.plan().tentative_answer, "NO")

    def test_attention_limit_can_defeat_parallel_resolution(self):
        roads = [
            replace(r, human=(r.name.startswith("FAST_")))
            for r in self.roads
        ]
        forest = LivingForest(self.hypotheses, roads, max_human=1)
        plan = forest.plan()
        self.assertLess(plan.expected_final_accuracy, 1.0)
        for _ in range(2):
            plan, witnessed = forest.run_synthetic_round(lambda road: road.predicted["010"])
            if witnessed is None:
                break
        self.assertLessEqual(forest.human_used, 1)

    def test_depth_ablation_removes_scout_preference(self):
        forest = LivingForest(self.hypotheses, self.roads, rounds=1)
        plan = forest.plan()
        self.assertEqual(plan.selected, ("BAIT",))
        self.assertAlmostEqual(plan.expected_final_accuracy, 0.625)

    def test_no_stale_plan_reuse_and_bad_graph_rejected(self):
        forest = LivingForest(self.hypotheses, self.roads)
        old = forest.plan()
        forest.run_synthetic_round(lambda road: road.predicted["101"])
        with self.assertRaises(ValueError):
            forest.accept(old, {"SCOUT": "1"})
        with self.assertRaises(ValueError):
            LivingForest(self.hypotheses, [
                Road("CYCLIC", "ASK", 1, {h.name: "X" for h in self.hypotheses},
                     "source", requires=(("CYCLIC", "X"),))])

    def test_research_benchmark_preserves_strong_fixed_diagnostic(self):
        result = benchmark()
        results = result["results"]
        self.assertEqual(results["living_forest"]["correct_of_8"], 8)
        self.assertEqual(results["fixed_classical_diagnostic"]["correct_of_8"], 8)
        self.assertEqual(results["myopic_joint_batch"]["correct_of_8"], 5)
        self.assertAlmostEqual(results["living_forest"]["mean_query_cost"], 0.90)

    def test_canonical_observation_order_reuses_search_state(self):
        forest = LivingForest(self.hypotheses, self.roads)
        memo = {}
        living = ("000", "001")
        first = forest._search(living, {"SCOUT": "0", "FAST_A_0": "0"}, 0.5, 1, 1, memo)
        second = forest._search(living, {"FAST_A_0": "0", "SCOUT": "0"}, 0.5, 1, 1, memo)
        self.assertEqual(first, second)
        self.assertGreater(forest._cache_hits, 0)


if __name__ == "__main__":
    unittest.main()
