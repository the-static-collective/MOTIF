"""CONFLUENCE-004 adversarial assertions for the 'second door' discipline."""
from __future__ import annotations
from copy import deepcopy
from dataclasses import replace
import unittest

from second_door import (
    AgentState, Owner, VARIANTS, bounded_search, classical_dijkstra, nominal_reach,
    run, select_external_corridors, seal, motif003_aperture, benchmark,
)


class SecondDoorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.corridors = select_external_corridors()
        cls.example = cls.corridors[0]

    def test_outside_source_corridors_and_provenance(self):
        self.assertEqual(len(self.corridors), 4)
        self.assertEqual({c.source_map for c in self.corridors}, {"tiny", "dragonage"})
        self.assertTrue(all(len(c.coordinates) == 7 for c in self.corridors))
        self.assertTrue(all(c.source_path_length >= 6 for c in self.corridors))

    def test_new_route_requires_legal_key_action(self):
        x = run(Owner(self.example, "KEY"))
        self.assertEqual(x["status"], "NEW_ROUTE_FROM_KEY_AFFORDANCE")
        self.assertFalse(x["nominal_walk_only_certificate"]["goal_reachable"])
        self.assertTrue(x["safe_fixture_replay_verified"])
        self.assertIn("TAKE", x["suggested_steps"])
        self.assertIn("UNLOCK", x["suggested_steps"])
        self.assertTrue(x["no_claim_of_superiority"])
        self.assertEqual(len(x["suggested_steps"]),
                         x["classical_augmented_dijkstra_cost"])

    def test_repair_with_another_resource_is_separate_valid_route(self):
        x = run(Owner(self.example, "TOOL"))
        self.assertEqual(x["status"], "NEW_ROUTE_FROM_TOOL_AFFORDANCE")
        self.assertIn("REPAIR", x["suggested_steps"])
        self.assertEqual(x["suggested_steps"].count("TAKE"), 1)
        self.assertTrue(x["safe_fixture_replay_verified"])

    def test_existing_detour_requires_no_new_physical_power(self):
        x = run(Owner(self.example, "DETOUR"))
        self.assertEqual(x["status"], "ALTERNATE_EXISTING_ROUTE")
        self.assertTrue(x["nominal_walk_only_certificate"]["goal_reachable"])
        self.assertNotIn("UNLOCK", x["suggested_steps"])
        self.assertNotIn("REPAIR", x["suggested_steps"])
        self.assertTrue(x["safe_fixture_replay_verified"])

    def test_denied_permission_not_rationalized_away(self):
        x = run(Owner(self.example, "DENIED"))
        self.assertEqual(x["status"], "HOLD_PERMISSION_DENIED")
        self.assertFalse(x["safe_fixture_replay_verified"])
        self.assertEqual(x["suggested_steps"], [])
        self.assertIsNone(x["classical_augmented_dijkstra_cost"])

    def test_unknown_permission_is_not_implied_consent(self):
        x = run(Owner(self.example, "UNKNOWN"))
        self.assertEqual(x["status"], "HOLD_ASK_FOR_AUTHORIZATION")
        self.assertFalse(x["safe_fixture_replay_verified"])
        self.assertNotIn("UNLOCK", x["suggested_steps"])

    def test_unsafe_route_never_allowed(self):
        x = run(Owner(self.example, "HAZARD"))
        self.assertEqual(x["status"], "HOLD_HAZARD_BLOCKED")
        self.assertEqual(x["suggested_steps"], [])

    def test_genuine_finite_scope_impossibility_retained(self):
        x = run(Owner(self.example, "ABSENT"))
        self.assertEqual(x["status"],
                         "CERTIFIED_NO_ROUTE_WITHIN_FINITE_AUTHORIZED_OPERATORS")
        self.assertTrue(x["bounded_search_exhausted"])
        self.assertFalse(x["nominal_walk_only_certificate"]["goal_reachable"])
        self.assertFalse(x["safe_fixture_replay_verified"])
        self.assertIsNone(x["classical_augmented_dijkstra_cost"])

    def test_resource_budget_stop_is_not_ontological_no_route(self):
        x = run(Owner(self.example, "KEY"), max_expansions=2)
        self.assertEqual(x["status"],
                         "HOLD_SEARCH_BUDGET_EXHAUSTED_NOT_IMPOSSIBLE")
        self.assertFalse(x["bounded_search_exhausted"])
        self.assertEqual(x["suggested_steps"], [])
        self.assertIsNotNone(x["classical_augmented_dijkstra_cost"])

    def test_exact_reference_replay_rejects_fake_crossing(self):
        owner = Owner(self.example, "KEY")
        self.assertIsNone(owner.verify_path((
            "MOVE:1", "MOVE:2", "MOVE:3", "MOVE:4", "MOVE:5", "MOVE:6"
        )))
        legal = bounded_search(owner)
        self.assertIsNotNone(owner.verify_path(legal["steps"]))

    def test_independent_reference_policies_agree_for_every_fixture(self):
        for corridor in self.corridors:
            for variant in VARIANTS:
                owner = Owner(corridor, variant)
                b = bounded_search(owner)
                classical = classical_dijkstra(owner)
                self.assertEqual(b["steps"] is None, classical["steps"] is None)
                if b["steps"] is not None:
                    self.assertEqual(len(b["steps"]), classical["cost"])
                    self.assertIsNotNone(owner.verify_path(b["steps"]))
                self.assertLess(b["discovered_states"], 1000)

    def test_forged_source_receipt_even_if_rehashed_is_rejected(self):
        owner = Owner(self.example, "UNKNOWN")
        observed = owner.observe("gate_permission")
        altered = deepcopy(observed)
        altered["value"] = "GRANTED"
        altered["sha256"] = seal({k: v for k, v in altered.items() if k != "sha256"})
        self.assertFalse(owner.verify(altered))
        self.assertTrue(owner.verify(observed))

    def test_laundering_external_source_provenance_fails(self):
        owner = Owner(self.example, "KEY")
        proof = owner.observe("resource_present")
        tampered = deepcopy(proof)
        tampered["source"] = "SOME_OTHER_OWNER"
        tampered["sha256"] = seal({k: v for k, v in tampered.items() if k != "sha256"})
        self.assertFalse(owner.verify(tampered))

    def test_native_motif003_actually_called(self):
        x = motif003_aperture(Owner(self.example, "KEY"))
        self.assertEqual(x["native"], "MOTIF003_REAL_EXECUTION")
        self.assertGreater(len(x["first_legal_choices"]), 0)
        self.assertTrue(x["selection_is_advisory_not_truth"])
        self.assertEqual(len(x["module_sha256"]), 64)

    def test_false_operator_never_appears_as_legal(self):
        owner = Owner(self.example, "DENIED")
        walk = owner.initial
        for _ in range(3):
            ops = dict(owner.symbolic_actions(walk))
            walk = ops["MOVE:" + str(walk.position + 1)]
        self.assertEqual(walk.position, 3)
        self.assertNotIn("UNLOCK", dict(owner.symbolic_actions(walk)))
        self.assertNotIn("REPAIR", dict(owner.symbolic_actions(walk)))

    def test_no_executable_external_actions(self):
        x = run(Owner(self.example, "KEY"))
        self.assertEqual(x["external_actions_executed"], 0)
        self.assertFalse(x["signed_source_identity"])
        self.assertEqual(x["authority"], "SYNTHETIC_RESEARCH_ONLY")
        self.assertEqual(x["original_source_origin_count"], 1)

    def test_fixed_benchmark_full_family(self):
        out = benchmark()
        self.assertEqual(out["cases"], 28)
        self.assertEqual(out["external_corridors"], 4)
        self.assertEqual(out["authorized_simulated_goals"], 12)
        self.assertEqual(out["scope_reopening_successes"], 8)
        self.assertEqual(out["existing_alternate_routes"], 4)
        self.assertEqual(out["source_confirmed_holds"], 12)
        self.assertEqual(out["formally_scoped_no_route"], 4)
        self.assertTrue(out["exact_classical_equal_cost_for_all_solutions"])


if __name__ == "__main__":
    unittest.main()
