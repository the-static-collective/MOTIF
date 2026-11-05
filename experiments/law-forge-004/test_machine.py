"""Adversarial offline tests for the LAW-FORGE-004 language-growth boundary."""
import unittest

from machine import (
    MembershipBatch, Observation, StateProgram, evidence_table,
    fold_candidates, infer, independent_review, missing_queries, words
)
from world import FAMILIES, World
from trial import aggregate, benchmark, learn, negative_transfer, trial


class GrammarBreakerTests(unittest.TestCase):
    def test_small_original_fold_remains_eligible_without_new_memory(self):
        for family in ("parity", "any_on"):
            with self.subTest(family=family):
                source = World(family, 0)
                old = fold_candidates(source.base())
                self.assertEqual(len(old), 1)
                model, batches, status, kind = learn(source)
                self.assertEqual(status, "RETAIN_SINGLE_BIT_FOLD")
                self.assertEqual(kind, "FOLD")
                self.assertEqual(len(batches), 0)
                self.assertEqual(trial(source)["total_synthetic_queries"], 31)

    def test_old_language_cannot_describe_three_and_four_state_history(self):
        for family in ("ends_01", "ends_001", "contains_101"):
            with self.subTest(family=family):
                self.assertEqual(fold_candidates(World(family).base()), ())

    def test_new_operator_is_inferred_from_discriminating_histories(self):
        expected = {"ends_01": 3, "ends_001": 4, "contains_101": 4}
        for family, count in expected.items():
            with self.subTest(family=family):
                machine, batches, status, kind = learn(World(family, 2))
                self.assertIsInstance(machine, StateProgram)
                self.assertEqual(machine.state_count, count)
                self.assertEqual(kind, "STATE_MACHINE")
                self.assertEqual(status, "PROPOSE_STATEFUL_OPERATOR")
                self.assertEqual(len(batches), 1)
                self.assertEqual(batches[0].cost, 224)
                self.assertEqual(trial(World(family, 2))["heldout_incorrect"], 0)

    def test_learned_machine_is_executable_not_just_a_label(self):
        model, _, _, _ = learn(World("ends_01", 0))
        self.assertEqual(model.predict((1, 1, 0, 1)), 1)
        self.assertEqual(model.predict((1, 1, 0, 0)), 0)
        self.assertEqual(len(model.trace((0, 0, 1, 0))), 5)
        self.assertEqual(StateProgram.from_packet(model.packet()), model)
        self.assertEqual(model.packet()["status"], "PROPOSAL_ONLY")

    def test_probe_batch_proposal_is_held_until_evaluator_executes(self):
        source = World("ends_01", 0)
        batch = missing_queries(source.base())
        self.assertEqual(batch.cost, 224)
        self.assertEqual(MembershipBatch.from_word_batch(batch.words,
                         batch.packet()), batch)
        self.assertEqual(len(source.execute_batch(batch)), 224)
        self.assertEqual(infer(source.base()).status,
                         "HOLD_INSUFFICIENT_MEMBERSHIP_EVIDENCE")

    def test_exceeding_budget_must_hold_and_never_call_oracle(self):
        model, batches, status, kind = learn(World("ends_01", 0), budget=223)
        self.assertIsNone(model)
        self.assertEqual(batches, ())
        self.assertEqual(status, "HOLD_MEMBERSHIP_BUDGET")
        self.assertEqual(trial(World("ends_01", 0), budget=0)
                         ["heldout_covered"], 0)

    def test_more_than_four_states_must_hold(self):
        source = World("ends_0001", 0)
        model, batches, status, kind = learn(source)
        self.assertIsNone(model)
        self.assertTrue(status.startswith("HOLD_"))
        self.assertEqual(trial(source)["heldout_covered"], 0)

    def test_prime_count_is_not_fraudulently_promoted(self):
        source = World("prime_count", 0)
        trial_result = trial(source)
        self.assertFalse(trial_result["review"]["status"].startswith("ELIGIBLE"))
        self.assertEqual(trial_result["heldout_covered"], 0)

    def test_nonstationary_world_can_fake_success_then_fail_review(self):
        result = trial(World("phase_shift", 0))
        self.assertEqual(result["status"], "PROPOSE_STATEFUL_OPERATOR")
        self.assertEqual(result["review"]["status"], "HOLD_INDEPENDENT_FALSIFIER")
        self.assertGreater(result["review"]["failures"], 0)
        self.assertEqual(result["heldout_covered"], 0)

    def test_missing_or_forged_witnesses_hold_or_error(self):
        world = World("ends_01")
        with self.assertRaises(ValueError):
            evidence_table([Observation((1, 0), 0),
                            Observation((1, 0), 1)])
        with self.assertRaises(ValueError):
            Observation((1, True), 0)
        with self.assertRaises(ValueError):
            Observation((0, 1), 1, provenance="LIVE_WEB")
        with self.assertRaises(ValueError):
            infer([{"word": (0, 1), "result": 1}])

    def test_schema_authority_and_hash_tamper_rejected(self):
        model, batches, _, _ = learn(World("ends_01"))
        packet = model.packet()
        corruptions = (
            {"status": "APPROVED"},
            {"authority": "REMOTE_CONTROL"},
            {"real_world_authority": True},
            {"endpoint": "https://invalid.test"},
            {"start_state": 1},
            {"state_count": 19},
            {"transitions": [[99, 99]]},
            {"id": "fsm-" + "0" * 24},
            {"outputs": [True] * model.state_count},
        )
        for extra in corruptions:
            with self.subTest(extra=extra), self.assertRaises(ValueError):
                StateProgram.from_packet({**packet, **extra})
        b = batches[0]
        for changed in (
            {"authority": "NETWORK"},
            {"real_world_authority": True},
            {"url": "https://invalid.test"},
            {"word_set_digest": "00"},
            {"count": 223},
        ):
            with self.subTest(changed=changed), self.assertRaises(ValueError):
                MembershipBatch.from_word_batch(
                    b.words, {**b.packet(), **changed})

    def test_review_requires_full_sample_and_multiple_lengths(self):
        machine, _, _, _ = learn(World("ends_01"))
        rows = World("ends_01").partition("review")
        self.assertEqual(independent_review(machine, rows[:40])["status"],
                         "HOLD_INSUFFICIENT_REVIEW")
        repeated = rows[:80] * 2
        self.assertEqual(independent_review(machine, repeated)["status"],
                         "HOLD_REVIEW_COVERAGE")

    def test_source_success_does_not_admit_destination(self):
        cases = negative_transfer()
        self.assertTrue(cases["same_machine_new_identity"]["status"]
                        .startswith("ELIGIBLE"))
        self.assertEqual(cases["different_hidden_machine"]["status"],
                         "HOLD_INDEPENDENT_FALSIFIER")
        self.assertEqual(cases["nonstationary_destination"]["status"],
                         "HOLD_INDEPENDENT_FALSIFIER")

    def test_all_eligible_cases_hold_zero_error_on_separate_data(self):
        for family in ("parity", "any_on", "ends_01",
                       "ends_001", "contains_101"):
            with self.subTest(family=family):
                r = trial(World(family, 5))
                self.assertTrue(r["review"]["status"].startswith("ELIGIBLE"))
                self.assertGreater(r["heldout_covered"], 300)
                self.assertEqual(r["heldout_incorrect"], 0)
                self.assertTrue(r["destination_review"]["status"]
                                .startswith("ELIGIBLE"))

    def test_classical_gated_control_is_equally_capable(self):
        for family in FAMILIES:
            with self.subTest(family=family):
                a = trial(World(family, 4), "stateful_upgrade")
                b = trial(World(family, 4), "classical_gated")
                self.assertEqual(a["review"], b["review"])
                self.assertEqual(a["heldout_covered"], b["heldout_covered"])
                self.assertEqual(a["total_synthetic_queries"],
                                 b["total_synthetic_queries"])

    def test_method_does_not_promote_on_baseline_tie(self):
        report = benchmark()
        self.assertEqual(report["frozen_method_decision"], "NO_METHOD_PROMOTION")
        results = report["evaluation"]
        self.assertEqual(results["stateful_upgrade"],
                         results["classical_gated"])
        self.assertEqual(results["stateful_upgrade"]["worlds"], 40)
        self.assertEqual(results["stateful_upgrade"]["review_eligible"], 25)
        self.assertEqual(results["stateful_upgrade"]["held"], 15)
        self.assertEqual(results["stateful_upgrade"]["heldout_incorrect"], 0)
        self.assertEqual(results["scalar_only"]["review_eligible"], 10)
        self.assertEqual(report["external_operations"], 0)
        self.assertFalse(report["real_world_authority"])


if __name__ == "__main__":
    unittest.main()
