"""MOTIF-019F: tests of actual classical search, native organs and failed transfers."""
import unittest
from dataclasses import replace
from math import inf

from bridge import OrganHold, PIN_DOGRAM, PIN_QUESTION, gated_discriminator, question_frontier, verify_sources
from classical import Operator, Task, develop_methods, find_plan, hmax, verify_plan
from engine import episode, fixture_cases, propose_guard, sample_clue
from online import SyntheticWorld, base_problem, run_online, static_fallback, weighted_problem
from benchmark import benchmark


class NativeClassicalMethods(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = fixture_cases()

    def test_original_native_sources_are_pinned(self):
        self.assertEqual(verify_sources(), {
            "national_treasure": PIN_QUESTION, "dogram": PIN_DOGRAM
        })

    def test_original_question_box_asks_not_answers(self):
        receipt = question_frontier(sample_clue())
        self.assertEqual(receipt["aperture"], "discriminator")
        self.assertIn("cheapest discriminating observation", receipt["question"])
        self.assertNotIn("answer", receipt["native_receipt"])
        self.assertEqual(receipt["original_source_blob"], PIN_QUESTION)

    def test_missing_source_does_not_cross_to_dogram(self):
        result = propose_guard("open_gate", *self.cases,
                               sample_clue(include_source=False))
        self.assertEqual(result.status, "HOLD_MISSING_QUESTION_FOUNDATION")
        self.assertIsNone(result.feature)
        self.assertIsNone(result.native_dogram_blob)
        self.assertIn("earliest recoverable source", result.question)

    def test_native_dogram_separates_and_nontrivial_validation_breaks_badge(self):
        result = propose_guard("open_gate", *self.cases, sample_clue())
        self.assertEqual(result.status, "ELIGIBLE_MODEL_GUARD_ONLY")
        self.assertEqual(result.feature.name, "PATH2:carries:opens:gate")
        self.assertEqual(result.feature.guard_fact, "token")
        self.assertEqual(result.native_dogram_blob, PIN_DOGRAM)
        self.assertEqual(result.native_question_blob, PIN_QUESTION)
        self.assertTrue(any(x.startswith("DIRECT:wears:badge:DISPROVED")
                            for x in result.rejected_rivals))
        self.assertFalse(result.explicit_permission)

    def test_indistinguishable_rivals_cause_hold(self):
        train, discovery, _ = self.cases
        review = (
            episode("review-a","REVIEW",True,True,True,"one"),
            episode("review-b","REVIEW",False,False,False,"two"),
        )
        outcome = propose_guard("open_gate", train, discovery, review, sample_clue())
        self.assertEqual(outcome.status, "HOLD_AMBIGUOUS_OR_FALSIFIED")

    def test_out_of_grammar_synthetic_mechanism_refused(self):
        train, discovery, review = self.cases
        contradicted = list(review)
        contradicted[0] = replace(contradicted[0], succeeded=False)
        outcome = propose_guard("open_gate", train, discovery, contradicted, sample_clue())
        self.assertEqual(outcome.status, "HOLD_AMBIGUOUS_OR_FALSIFIED")

    def test_duplicate_or_leaked_evidence_split_refused(self):
        train, discovery, review = self.cases
        duplicate = replace(review[0], case_id=train[0].case_id)
        outcome = propose_guard("open_gate", train, discovery,
                                (duplicate, *review[1:]), sample_clue())
        self.assertEqual(outcome.status, "HOLD_INVALID_EVIDENCE_SPLIT")
        leaking = replace(discovery[0], succeeded=True)
        outcome2 = propose_guard("open_gate", train,
                                 (leaking, *discovery[1:]), review, sample_clue())
        self.assertEqual(outcome2.status, "HOLD_INVALID_EVIDENCE_SPLIT")

    def test_actual_classical_search_distinguishes_steps_from_cost(self):
        task = weighted_problem()
        bfs = find_plan(task, "BFS")
        ucs = find_plan(task, "UCS")
        astar = find_plan(task, "ASTAR_HMAX")
        self.assertEqual(bfs.actions, ("a_direct",))
        self.assertAlmostEqual(bfs.cost, 7.)
        self.assertEqual(ucs.actions, ("b_collect", "c_finish"))
        self.assertAlmostEqual(ucs.cost, 2.)
        self.assertAlmostEqual(astar.cost, ucs.cost)
        self.assertTrue(verify_plan(task, ucs.actions)[0])
        self.assertFalse(verify_plan(task, ("c_finish",))[0])
        self.assertLessEqual(hmax(task, task.facts), ucs.cost)

    def test_method_cartridges_generated_at_invocation_not_prebaked_routes(self):
        task = weighted_problem()
        foundry = develop_methods(task)
        self.assertIsNotNone(foundry.chosen)
        self.assertIn(foundry.chosen.algorithm, ("UCS", "ASTAR_HMAX"))
        self.assertAlmostEqual(foundry.reference.cost, 2.0)
        self.assertEqual(len(foundry.candidates), 3)
        self.assertEqual(
            next(x for x in foundry.candidates if x.algorithm == "BFS").status,
            "REFUSE_MORE_COSTLY_THAN_UCS",
        )
        other = base_problem().replace_guard("open_gate","token")
        second = develop_methods(other)
        self.assertEqual(second.chosen.model_version, 1)
        self.assertNotEqual(second.chosen.action_model_hash,
                            foundry.chosen.action_model_hash)
        self.assertFalse(second.chosen.external_effects)

    def test_search_bound_and_impossible_goal_refuse(self):
        t = weighted_problem()
        self.assertEqual(find_plan(t, "UCS", max_expanded=1).status,
                         "HOLD_SEARCH_LIMIT")
        missing = Task(frozenset({"start"}), frozenset({"never"}),
                       t.operators)
        self.assertEqual(find_plan(missing, "ASTAR_HMAX").status, "HOLD_NO_PLAN")
        self.assertIsNone(develop_methods(missing).chosen)

    def test_synthetic_independent_actuator_disproves_naive_model(self):
        model = base_problem()
        self.assertEqual(find_plan(model, "UCS").actions,
                         ("open_gate", "deliver"))
        world = SyntheticWorld(model.facts, {"open_gate":frozenset({"token"})})
        actual = world.attempt(next(x for x in model.operators if x.name == "open_gate"))
        self.assertFalse(actual.success)
        self.assertEqual(actual.before, actual.after)
        self.assertEqual(actual.observed_status, "REPORTED_NOT_APPLIED")
        self.assertEqual(world.state, model.facts)

    def test_live_replanning_changes_method_model_from_action_receipt(self):
        result = run_online("TOKEN", "FOUNDRY")
        self.assertEqual(result["status"], "DELIVERED")
        self.assertAlmostEqual(result["total_cost"], 4.2)
        self.assertEqual(result["learned_guard"], "token")
        self.assertGreaterEqual(result["final_model_version"], 1)
        acts = [r["action_receipt"]["name"] for r in result["receipts"]]
        self.assertEqual(acts, ["open_gate", "collect_token", "open_gate", "deliver"])
        self.assertFalse(result["receipts"][0]["action_receipt"]["success"])
        self.assertTrue(result["receipts"][2]["action_receipt"]["success"])
        self.assertFalse(result["outside_world_authority"])

    def test_classical_ucs_same_information_ties_method_foundry(self):
        grown = run_online("TOKEN", "FOUNDRY")
        strongest = run_online("TOKEN", "UCS_ONLY")
        self.assertEqual(strongest["status"], "DELIVERED")
        self.assertAlmostEqual(grown["total_cost"], strongest["total_cost"])
        self.assertAlmostEqual(static_fallback()["total_cost"], 7.)
        self.assertLess(grown["total_cost"], static_fallback()["total_cost"])

    def test_missing_question_foundation_forces_conservative_detour(self):
        run = run_online("TOKEN", "FOUNDRY", source_complete=False)
        self.assertEqual(run["status"], "DELIVERED")
        self.assertAlmostEqual(run["total_cost"], 7.)
        self.assertEqual(run["learned_guard"], None)
        self.assertIn("HOLD_MISSING_QUESTION_FOUNDATION", run["failures_retained"])

    def test_prior_success_does_not_prove_future_world_shift(self):
        run = run_online("SHIFT_BADGE", "FOUNDRY")
        self.assertEqual(run["status"], "DELIVERED")
        self.assertAlmostEqual(run["total_cost"], 9.2)
        self.assertEqual(run["learned_guard"], "token")
        self.assertIn("HOLD_UNEXPLAINED_OR_CHANGED_CAUSE", run["failures_retained"])
        self.assertGreater(run["total_cost"], static_fallback("SHIFT_BADGE")["total_cost"])

    def test_reproducible_receipt_does_not_hide_negative_controls(self):
        results = benchmark()
        self.assertEqual(results["native_original_git_blobs"]["dogram"], PIN_DOGRAM)
        self.assertEqual(results["missing_source"]["dogram_was_called"], False)
        self.assertAlmostEqual(results["weighted_classical_control"]
                               ["classical_UCS_optimal_cost"],2.)
        self.assertEqual(results["online"]["independent_shift_world"]["status"],
                         "DELIVERED")
        self.assertEqual(results["boundaries"]["real_actions"], False)


if __name__ == "__main__":
    unittest.main()
