"""LAW-FORGE-008 adversarial tests: classical lookup + limited active learning."""
import inspect
import unittest

import learner
from learner import (
    DOMAIN, WIDTH, MAX_QUERIES, SourceContract, Observation, Question,
    controls, exact_lookup, fitted_indices, make_desk, choose_question,
    rule_library, consequence_weight, question_cost, review
)
from owner import FAMILIES, World
from trial import METHODS, benchmark, inquiry, trial


class UnknownWorldTests(unittest.TestCase):
    def test_prior_classical_vector_validator_is_actually_reused(self):
        self.assertIs(learner.prior_binary_vector.__module__,
                      learner.prior_binary_vector.__module__)
        self.assertEqual(WIDTH, 12)
        self.assertEqual(DOMAIN, 4096)
        self.assertEqual(controls(tuple([0]*12)), tuple([0]*12))
        with self.assertRaises(ValueError):
            controls(tuple([0]*13))
        with self.assertRaises(ValueError):
            controls(tuple([0]*11 + [True]))

    def test_rule_language_is_frozen_and_does_not_import_hidden_oracle(self):
        self.assertEqual(len(rule_library()), 650)
        self.assertNotIn("from owner import", inspect.getsource(learner))
        self.assertNotIn("import owner", inspect.getsource(learner))
        self.assertEqual(
            {rule.kind for rule in rule_library()},
            {"BIT", "AND2", "OR2", "XOR2", "AND3", "OR3"}
        )

    def test_original_classical_lookup_is_preserved_over_hypotheses(self):
        world = World("pair_and", 2)
        desk, questions, spent = inquiry(world, "motif_consequence")
        self.assertLess(len(desk.snapshot), DOMAIN)
        for witness in world.initial():
            response = desk.predict(witness.x, world.contract)
            self.assertEqual(response["status"], "LOOKUP_WITNESSED")
            self.assertEqual(response["value"], witness.y)
        self.assertLessEqual(spent, MAX_QUERIES)
        self.assertEqual(len(questions), len({q.x for q in questions}))

    def test_unseen_input_refused_by_strict_lookup_only_baseline(self):
        world = World("pair_and", 1)
        desk, _, _ = inquiry(world, "lookup_only")
        unseen = next(row for row in world.independent("test")
                      if row.x not in dict(desk.snapshot))
        result = desk.predict(unseen.x, world.contract)
        self.assertEqual(result["status"], "HOLD_UNOBSERVED")
        self.assertIsNone(result["value"])
        self.assertEqual(trial(world, "lookup_only")["test_covered"], 0)

    def test_question_cards_are_strictly_authorized_by_source(self):
        world = World("pair_or", 2)
        card = world.query_catalog()[0]
        self.assertEqual(Question.from_packet(card.packet()), card)
        self.assertEqual(world.execute(card).contract_id, world.contract.id)
        for diff in (
            {"authority": "INTERNET"},
            {"real_world_authority": True},
            {"callback": "https://invalid.example"},
            {"x": [0]*11 + [True]},
            {"consequence_weight": 17},
            {"unit_cost": 0}
        ):
            with self.subTest(diff=diff), self.assertRaises(ValueError):
                Question.from_packet({**card.packet(), **diff})

    def test_forged_source_cost_or_priority_cannot_be_executed(self):
        world = World("pair_or", 2)
        card = world.query_catalog()[0]
        changed_weight = 1 if card.consequence_weight == 5 else 5
        with self.assertRaises(ValueError):
            world.execute(Question(card.x, card.unit_cost, changed_weight))
        changed_cost = 1 if card.unit_cost == 2 else 2
        with self.assertRaises(ValueError):
            world.execute(Question(card.x, changed_cost, card.consequence_weight))

    def test_query_catalog_partitions_do_not_leak_evaluation_inputs(self):
        for seed in (0, 1, 2, 3, 4, 5, 6):
            with self.subTest(seed=seed):
                partitions = World("pair_xor", seed).partitions()
                sets = [set(partitions[key])
                        for key in ("initial", "catalog", "review", "test")]
                self.assertEqual(list(map(len, sets)), [4, 160, 192, 320])
                for i, first in enumerate(sets):
                    for other in sets[i+1:]:
                        self.assertTrue(first.isdisjoint(other))

    def test_source_epochs_and_foreign_records_do_not_cross(self):
        world = World("pair_and", 1)
        other = World("pair_and", 1, source_epoch="epoch-2")
        desk, _, _ = inquiry(world)
        self.assertEqual(desk.predict(tuple([0]*12), other.contract)["status"],
                         "HOLD_SOURCE_REVISION_CHANGED")
        with self.assertRaises(ValueError):
            exact_lookup(world.contract, other.initial())

    def test_two_same_cell_conflicting_outcomes_are_rejected(self):
        world = World("pair_and", 1)
        first = world.initial()[0]
        with self.assertRaises(ValueError):
            exact_lookup(world.contract, (
                first, Observation(first.x, 1-first.y, world.contract.id)
            ))
        with self.assertRaises(ValueError):
            Observation(first.x, True, world.contract.id)
        with self.assertRaises(ValueError):
            Observation(first.x, first.y, "0"*64, provenance="NETWORK")

    def test_version_space_is_classical_and_conservative(self):
        world = World("triple_and", 2)
        initial = world.initial()
        candidates = fitted_indices(tuple((o.x, o.y) for o in initial))
        self.assertGreater(len(candidates), 1)
        desk, questions, budget = inquiry(world, "classical_entropy")
        self.assertTrue(len(desk.candidates) <= len(candidates))
        for row in world.initial():
            self.assertEqual(desk.predict(row.x, world.contract)["value"],
                             row.y)
        self.assertLessEqual(budget, MAX_QUERIES)

    def test_predeclared_consequence_is_not_a_hidden_source_outcome(self):
        high = (1, 1) + (0,)*10
        low = (0, 1) + (0,)*10
        self.assertEqual(consequence_weight(high), 5)
        self.assertEqual(consequence_weight(low), 1)
        self.assertIn(question_cost(high), (1, 2))
        self.assertIn(question_cost(low), (1, 2))
        self.assertEqual(World("pair_and", 2).query_catalog()[0].provenance,
                         "SYNTHETIC_OWNER_QUESTION_CATALOG")

    def test_unfunded_query_budget_cannot_be_overdrawn(self):
        world = World("pair_and", 1)
        with self.assertRaises(ValueError):
            inquiry(world, budget=-1)
        with self.assertRaises(ValueError):
            inquiry(world, budget=25)
        with self.assertRaises(ValueError):
            inquiry(world, budget=True)
        desk, questions, cost = inquiry(world, budget=0)
        self.assertEqual((len(questions), cost), (0, 0))
        self.assertEqual(len(desk.snapshot), 4)

    def test_all_five_competitors_receive_same_initial_evidence(self):
        world = World("pair_and", 3)
        samples = []
        for method in METHODS:
            desk, questions, spent = inquiry(world, method)
            samples.append(tuple(sorted((row.x, desk.predict(row.x, world.contract)['value'])
                                        for row in world.initial())))
            self.assertLessEqual(spent, MAX_QUERIES)
        self.assertTrue(all(sample == samples[0] for sample in samples))

    def test_replayed_review_cannot_manufacture_independence(self):
        world = World("pair_and", 2)
        desk, _, _ = inquiry(world, "classical_entropy")
        review_rows = world.independent("review")
        copied = (review_rows[0],) * 192
        self.assertEqual(review(desk, world.contract, copied)["status"],
                         "HOLD_REVIEW_COVERAGE")

    def test_hidden_shift_cannot_claim_success_without_review(self):
        for family in ("phase_shift", "hidden_context"):
            with self.subTest(family=family):
                result = trial(World(family, 2), "classical_entropy")
                self.assertFalse(result["independent_review"]["status"]
                                 .startswith("ELIGIBLE"))
                self.assertEqual(result["test_covered"], 0)

    def test_outside_grammar_can_abstain_not_claim_theorem(self):
        world = World("twelve_parity", 2)
        desk, _, _ = inquiry(world, "motif_consequence")
        # A finite, declared hypothesis library need not fit unseen laws.
        self.assertIn(len(desk.candidates), range(len(rule_library()) + 1))
        result = trial(world, "motif_consequence")
        self.assertFalse(result["independent_review"]["status"]
                         .startswith("ELIGIBLE"))
        self.assertEqual(result["test_covered"], 0)

    def test_tree_baseline_is_real_executable_gini_classifier(self):
        world = World("identity_bit", 2)
        desk, questions, spent = inquiry(world, "classical_tree")
        self.assertIsNotNone(desk.tree)
        self.assertEqual(len(desk.candidates), 0)
        self.assertLessEqual(spent, MAX_QUERIES)
        known = dict(desk.snapshot)
        for x, y in known.items():
            self.assertEqual(desk.predict(x, world.contract)["value"], y)
        self.assertEqual(trial(world, "classical_tree")["external_actions"], 0)

    def test_observational_budget_under_one_percent_of_entire_domain(self):
        world = World("pair_or", 3)
        desk, queries, _ = inquiry(world, "classical_fixed")
        self.assertLessEqual(len(desk.snapshot), 4 + MAX_QUERIES)
        self.assertLess((4 + MAX_QUERIES) / DOMAIN, 0.01)
        self.assertEqual(trial(world)["domain_configurations"], 4096)

    def test_frozen_comparison_has_explicit_no_auto_promotion(self):
        receipt = benchmark()
        self.assertEqual(receipt["evaluation"]["motif_consequence"]["worlds"],
                         len(FAMILIES)*5)
        self.assertEqual(receipt["evaluation"]["classical_entropy"]["worlds"],
                         len(FAMILIES)*5)
        self.assertEqual(receipt["development"]["motif_consequence"]["worlds"],
                         len(FAMILIES)*2)
        self.assertEqual(receipt["automatic_method_promotion"], False)
        self.assertFalse(receipt["real_world_authority"])
        self.assertEqual(receipt["external_actions"], 0)
        self.assertIn(receipt["frozen_method_decision"],
                      ("NO_METHOD_PROMOTION", "PROPOSE_FOR_HUMAN_REVIEW_ONLY"))
        self.assertLess(receipt["evaluation"]["motif_consequence"]["inquiry_cost"],
                        MAX_QUERIES*len(FAMILIES)*5+1)


if __name__ == "__main__":
    unittest.main()
