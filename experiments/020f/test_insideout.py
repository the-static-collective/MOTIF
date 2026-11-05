"""MOTIF-020F: real read-only PlanZ contract and counterfactual omission tests."""
import unittest
from dataclasses import replace

from demo import fixture, scenario
from insideout import CounterfactualOpportunity, InsideOutBox, scope_only
from planz import PlanPointer, read_planz_snapshot


class PlanZOmissionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.snapshot = read_planz_snapshot()

    def plan(self, opportunities=None, *, parallel=1, horizon=3, budget=2):
        return InsideOutBox(
            self.snapshot, fixture() if opportunities is None else opportunities,
            max_parallel=parallel, horizon=horizon,
            attention_budget=budget,
            cognition_cost_per_tick=0.05,
        ).analyze()

    def test_native_validator_and_frozen_index_are_real(self):
        s = self.snapshot
        self.assertEqual(s.git_blob, "49e70c0caeaf0bca430338829b69d51c8c617385")
        self.assertEqual(s.planz_validator_git_blob, "a6fb92b5242519fa1c72b88cf1d34eb6770063ea")
        self.assertEqual(s.edition, "ATTENTION-2026-10-28-005")
        self.assertGreater(len(s.plans), 8)
        self.assertEqual(s.authority, "INDEX_ONLY")
        self.assertEqual(s.temporal_fact, "NONE_IN_ATTENTION_INDEX")

    def test_real_source_cannot_be_converted_into_authority_or_deadline(self):
        for pointer in self.snapshot.plans:
            self.assertFalse(pointer.execution_allowed)
            self.assertEqual(pointer.field_outcome, "NOT_VERIFIED")
            self.assertEqual(pointer.third_party_approval, "NOT_ESTABLISHED")
            self.assertTrue(pointer.blocked_by)
        held = scope_only(self.snapshot)
        self.assertEqual(held["status"], "HOLD_NO_VERIFIED_INACTION_VALUATION")
        self.assertTrue(held["all_external_actions_blocked"])

    def test_one_tick_delay_really_destroys_reachable_welfare(self):
        r = self.plan()
        self.assertEqual(r.first_batch, ("SHELF-001",))
        self.assertEqual(r.status, "COUNTERFACTUAL_REVIEW_ONLY")
        self.assertAlmostEqual(r.optimal_modeled_value, 14)
        self.assertAlmostEqual(r.one_tick_wait_modeled_value, 8)
        self.assertAlmostEqual(r.cost_of_waiting_one_tick, 6)
        self.assertAlmostEqual(r.cost_of_deliberation_one_tick, 6.05)
        self.assertIn("SHELF-001", r.plans_expiring_if_wait)
        self.assertFalse(r.real_deadlines_verified)
        self.assertFalse(r.external_execution_allowed)

    def test_opportunity_cost_is_not_only_compute_cost(self):
        r = self.plan()
        self.assertGreater(r.cost_of_waiting_one_tick, 100 * 0.05)
        self.assertGreater(r.cost_of_deliberation_one_tick, r.cost_of_waiting_one_tick)
        self.assertEqual(r.model_name, "FINITE_HORIZON_CLASSICAL_DP")

    def test_finite_horizon_dp_beats_myopic_but_not_optimal_classical(self):
        r = self.plan()
        self.assertAlmostEqual(r.baseline_myopic_value, 8)
        self.assertAlmostEqual(r.optimal_modeled_value, 14)
        self.assertEqual([x.plans for x in r.sequence][:2],
                         [("SHELF-001",), ("GARDEN-TABLE-001",)])

    def test_permanent_omission_is_distinct_from_delay(self):
        r = self.plan()
        lost = dict(r.foregone_by_permanent_omission)
        self.assertAlmostEqual(lost["SHELF-001"], 6)
        self.assertAlmostEqual(lost["GARDEN-TABLE-001"], 8)
        self.assertAlmostEqual(r.cost_of_waiting_one_tick, 6)

    def test_unapproved_real_plan_has_no_executable_output(self):
        answer = scenario()
        self.assertEqual(answer["real_world"]["status"],
                         "HOLD_NO_VERIFIED_INACTION_VALUATION")
        self.assertFalse(answer["dispatched"])
        for source in answer["source_pointers"]:
            self.assertEqual(source["source_deadline"], "UNKNOWN_NOT_IN_PUBLIC_INDEX")
            self.assertFalse(source["source_execution_allowed"])
        self.assertEqual(answer["strong_classical_comparator"]["value"], 14)

    def test_zero_temporal_assumptions_does_not_invent_urgency(self):
        r = self.plan(())
        self.assertEqual(r.status, "HOLD_NO_TEMPORAL_ASSUMPTIONS")
        self.assertEqual(r.cost_of_waiting_one_tick, 0)
        self.assertEqual(r.optimal_modeled_value, 0)
        self.assertEqual(r.first_batch, ())

    def test_actor_level_loss_not_erased_by_aggregate_reward(self):
        base = fixture()
        danger = replace(base[0], actor_effects=(("recipient", 20), ("helper", -2)))
        r = self.plan((danger,base[1]))
        self.assertNotIn("SHELF-001", r.first_batch)
        self.assertAlmostEqual(r.optimal_modeled_value, 8)
        self.assertAlmostEqual(dict(r.foregone_by_permanent_omission)["SHELF-001"], 0)

    def test_parallelism_can_save_two_simultaneously_expiring_options(self):
        a, b = fixture()
        b = replace(b, last_start_tick=0)
        serial = self.plan((a,b),parallel=1)
        parallel = self.plan((a,b),parallel=2)
        self.assertAlmostEqual(serial.optimal_modeled_value, 8)
        self.assertAlmostEqual(parallel.optimal_modeled_value, 14)
        self.assertEqual(parallel.first_batch, ("GARDEN-TABLE-001", "SHELF-001"))
        self.assertAlmostEqual(parallel.cost_of_waiting_one_tick, 14)

    def test_zero_gain_should_not_force_work(self):
        a = replace(fixture()[0], reward_if_successful=0, effort_cost=3)
        r = self.plan((a,))
        self.assertEqual(r.first_batch, ())
        self.assertEqual(r.optimal_modeled_value, 0)

    def test_slow_decay_is_not_falsely_called_deadline(self):
        a,b = fixture()
        b = replace(b, value_decay_per_tick=1)
        r = self.plan((a,b))
        self.assertAlmostEqual(r.optimal_modeled_value, 13)
        self.assertAlmostEqual(r.cost_of_waiting_one_tick, 6)
        self.assertEqual(r.plans_expiring_if_wait, ("SHELF-001",))

    def test_all_hypothetical_inputs_must_be_explicit_and_finite(self):
        with self.assertRaises(ValueError):
            CounterfactualOpportunity("SHELF-001", 6, 0, probability=2)
        with self.assertRaises(ValueError):
            CounterfactualOpportunity("SHELF-001", 6, 0, assumed_clearance="REAL_APPROVED")
        with self.assertRaises(ValueError):
            CounterfactualOpportunity("SHELF-001", float("inf"), 0)
        with self.assertRaises(ValueError):
            self.plan((fixture()[0], fixture()[0]))
        with self.assertRaises(KeyError):
            self.plan((CounterfactualOpportunity("DOES-NOT-EXIST", 9, 0),))

    def test_planZ_pointer_refuses_authority_promotion(self):
        original = self.snapshot.get("SHELF-001")
        with self.assertRaises(ValueError):
            replace(original, execution_allowed=True)
        with self.assertRaises(ValueError):
            replace(original, third_party_approval="ESTABLISHED")
        with self.assertRaises(ValueError):
            replace(original, blocked_by=())
        self.assertTrue(original.source.startswith("https://github.com/"))

    def test_time_zero_expired_option_is_not_a_proven_real_emergency(self):
        r = self.plan()
        self.assertEqual(r.assumed_world,"DECLARED_SYNTHETIC_SCENARIO_NOT_PLANZ_FACTS")
        self.assertTrue(r.simulation_only)
        self.assertFalse(r.real_deadlines_verified)
        self.assertFalse(r.real_costs_verified)


if __name__ == "__main__":
    unittest.main()
