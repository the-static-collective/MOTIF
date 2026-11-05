"""Executable pressure tests for MOTIF-SK-001's invented cooperative world."""
from dataclasses import replace
import unittest

from smallest_key import (
    Goal, Intervention, World, find_smallest_key, fixture, options,
    reached, run_demo, simulate
)


class SmallestKeyTests(unittest.TestCase):
    def setUp(self):
        self.world, self.actions = fixture()
        self.protected = Goal("well", protect_existing=True)
        self.relaxed = Goal("well", protect_existing=False)
        self.by_id = {a.id: a for a in self.actions}

    def test_initial_capabilities_are_actor_relative(self):
        result = options(self.world)
        self.assertEqual(result["physical"], frozenset({("ben", "bike")}))
        self.assertEqual(result["admitted"], frozenset({("ben", "bike")}))
        self.assertEqual(result["visible"], frozenset({("ben", "bike")}))

    def test_cheapest_unguarded_choice_harms_other_actor(self):
        result = find_smallest_key(self.world, self.actions, self.relaxed, 4)
        self.assertEqual(result["status"], "PROPOSED_SYNTHETIC")
        self.assertEqual(result["actions"], ["loan-kit"])
        self.assertEqual(result["cost"], 1)
        self.assertEqual(result["opportunity_delta"]["visible"]["lost"],
                         ["ben:bike"])
        self.assertEqual(result["opportunity_delta"]["visible"]["gained"],
                         ["ada:well"])

    def test_protection_requires_composed_two_step_key(self):
        result = find_smallest_key(self.world, self.actions, self.protected, 4)
        self.assertEqual(result["status"], "PROPOSED_SYNTHETIC")
        self.assertEqual(result["cost"], 3)
        self.assertEqual(set(result["actions"]),
                         {"teach-ben-well", "tell-ben-well"})
        self.assertEqual(result["opportunity_delta"]["visible"]["gained"],
                         ["ben:well"])
        for scope in ("physical", "admitted", "visible"):
            self.assertEqual(result["opportunity_delta"][scope]["lost"], [])

    def test_skill_only_is_not_observer_visible(self):
        after = simulate(self.world, self.by_id["teach-ben-well"])
        self.assertIsNotNone(after)
        self.assertIn(("ben", "well"), options(after)["admitted"])
        self.assertNotIn(("ben", "well"), options(after)["visible"])

    def test_information_only_does_not_create_physical_capability(self):
        after = simulate(self.world, self.by_id["tell-ben-well"])
        self.assertIsNotNone(after)
        self.assertNotIn(("ben", "well"), options(after)["physical"])
        self.assertNotIn(("ben", "well"), options(after)["visible"])

    def test_composition_opens_visible_door(self):
        taught = simulate(self.world, self.by_id["teach-ben-well"])
        then_told = simulate(taught, self.by_id["tell-ben-well"])
        told = simulate(self.world, self.by_id["tell-ben-well"])
        then_taught = simulate(told, self.by_id["teach-ben-well"])
        self.assertEqual(then_told, then_taught)
        self.assertEqual(options(then_told)["visible"],
                         frozenset({("ben", "bike"), ("ben", "well")}))

    def test_tight_budget_abstains_without_fake_action(self):
        result = find_smallest_key(self.world, self.actions, self.protected, 2)
        self.assertEqual(result["status"], "ABSTAIN_NO_PATH")
        self.assertEqual(result["actions"], [])
        self.assertIsNone(result["cost"])

    def test_refusal_never_becomes_a_failed_attempt(self):
        blocked = self.by_id["blocked-gift"]
        self.assertFalse(blocked.admitted)
        self.assertIsNone(simulate(self.world, blocked))
        result = find_smallest_key(
            self.world, (blocked,), self.relaxed, 10)
        self.assertEqual(result["status"], "ABSTAIN_NO_PATH")

    def test_fallback_when_teaching_unavailable(self):
        only_mint = (self.by_id["make-spare-kit"],)
        result = find_smallest_key(self.world, only_mint, self.protected, 4)
        self.assertEqual(result["actions"], ["make-spare-kit"])
        self.assertEqual(result["cost"], 4)
        self.assertEqual(result["opportunity_delta"]["physical"]["lost"], [])

    def test_target_scopes_are_separate(self):
        result = find_smallest_key(
            self.world, self.actions,
            Goal("well", scope="admitted", protect_existing=True), 4)
        self.assertEqual(result["actions"], ["teach-ben-well"])
        self.assertEqual(result["cost"], 2)

    def test_named_actor_target_is_not_automatically_equivalent(self):
        result = find_smallest_key(
            self.world, self.actions,
            Goal("well", actor="ada", protect_existing=True), 4)
        self.assertEqual(result["actions"], ["make-spare-kit"])
        self.assertEqual(result["cost"], 4)

    def test_duplicate_tools_do_not_duplicate_capability(self):
        spare = simulate(self.world, self.by_id["make-spare-kit"])
        twice = replace(spare,
                        assets=spare.assets | {("kit-4", "kit")},
                        custody=spare.custody | {("ada", "kit-4")})
        self.assertEqual(options(spare), options(twice))

    def test_intermediate_deprivation_is_not_accepted(self):
        # A loan followed by a return must not silently erase the period in
        # which Ben lost bike repair. Every intermediate step is screened.
        return_kit = Intervention("return-kit", "loan", "ada", "ben", "kit-1", 1)
        candidate = find_smallest_key(
            self.world, self.actions + (return_kit,), self.protected, 4)
        self.assertNotIn("loan-kit", candidate["actions"])

    def test_reordered_actions_do_not_change_result(self):
        a = find_smallest_key(self.world, self.actions, self.protected, 4)
        b = find_smallest_key(
            self.world, tuple(reversed(self.actions)), self.protected, 4)
        self.assertEqual(a, b)

    def test_truncation_withholds_minimum_claim(self):
        result = find_smallest_key(
            self.world, self.actions, self.protected, 4, max_states=1)
        self.assertEqual(result["status"], "HOLD_TRUNCATED")
        self.assertEqual(result["actions"], [])

    def test_no_existing_goal_requires_an_intervention(self):
        after = simulate(self.world, self.by_id["make-spare-kit"])
        result = find_smallest_key(
            after, self.actions, Goal("well", actor="ada"), 4)
        self.assertEqual(result["status"], "ALREADY_REACHABLE")
        self.assertEqual(result["cost"], 0)

    def test_invalid_custody_and_duplicate_interventions(self):
        with self.assertRaises(ValueError):
            replace(self.world, custody=self.world.custody | {("ada", "kit-1")})
        with self.assertRaises(ValueError):
            find_smallest_key(
                self.world, self.actions + (self.actions[0],), self.protected, 4)
        with self.assertRaises(ValueError):
            Intervention("x", "mint", "maker", "ada", "k", 0)

    def test_no_side_effect_to_fixture_or_real_world(self):
        snapshot = self.world
        report = run_demo()
        self.assertEqual(self.world, snapshot)
        self.assertTrue(report["protected_plan"]["simulated_only"])
        self.assertTrue(report["unprotected_plan"]["simulated_only"])


if __name__ == "__main__":
    unittest.main()
