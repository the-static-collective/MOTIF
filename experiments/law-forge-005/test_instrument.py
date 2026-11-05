"""LAW-FORGE-005 adversarial tests: ternary is a hypothesis, never a premise."""
import unittest

from instrument import (Query, Readout, Sensor, SensorModel, discover,
                        fit, generate_sensor_language, independent_review,
                        remaining_probes, score)
from world import FAMILIES, World
from trial import benchmark, counterfactual_transfer, inquiry, trial


class WorldBreakerTests(unittest.TestCase):
    def test_finite_source_owned_grammar_has_rival_ontologies(self):
        programs = generate_sensor_language()
        self.assertEqual(len(programs), 20)
        self.assertIn(Sensor("BIT", (0,)), programs)
        self.assertIn(Sensor("COUNT2", (0, 2)), programs)
        self.assertIn(Sensor("PAIR", (0, 2)), programs)
        self.assertIn(Sensor("REACH2"), programs)
        self.assertIn(Sensor("PATHCOUNT"), programs)
        self.assertIn(Sensor("RAW4"), programs)

    def test_trinary_is_categorical_not_more_than_two_raw_bits(self):
        world = World("one_neighbor")
        ternary = Sensor("COUNT2", (0, 2))
        pair = Sensor("PAIR", (0, 2))
        values = {world.reading(ternary, g)
                  for g in ((0, 0, 0, 0), (1, 0, 0, 0),
                            (1, 0, 1, 0), (0, 0, 1, 0))}
        self.assertEqual(values, {0, 1, 2})
        self.assertEqual(ternary.source_reads, pair.source_reads)
        self.assertEqual(ternary.cardinality, 3)
        self.assertEqual(pair.cardinality, 4)
        self.assertLess(score(ternary, "symbolic_capacity"),
                        score(pair, "symbolic_capacity"))
        self.assertGreater(score(ternary, "binary_encoded"),
                           score(pair, "binary_encoded"))

    def test_trinary_can_be_a_supported_compact_model(self):
        outcome = trial(World("one_neighbor", 3))
        self.assertEqual(outcome["sensor_program"]["operation"], "COUNT2")
        self.assertEqual(outcome["sensor_program"]["edges"], [0, 2])
        self.assertTrue(outcome["review"]["status"].startswith("ELIGIBLE"))
        self.assertEqual(outcome["heldout_incorrect"], 0)
        self.assertEqual(outcome["sensor_cardinality"], 3)

    def test_ternary_is_not_privileged_when_binary_encoding_ties(self):
        ternary = trial(World("one_neighbor", 3))
        binary_coded = trial(World("one_neighbor", 3),
                             capacity="binary_encoded")
        self.assertEqual(ternary["sensor_program"]["operation"], "COUNT2")
        self.assertEqual(binary_coded["sensor_program"]["operation"], "PAIR")
        self.assertEqual(binary_coded["heldout_covered"],
                         ternary["heldout_covered"])

    def test_binary_sensor_wins_on_identity_oriented_world(self):
        row = trial(World("first_neighbor_only", 3))
        self.assertEqual(row["sensor_program"]["operation"], "PAIR")
        self.assertEqual(row["sensor_program"]["edges"], [0, 2])
        self.assertEqual(row["heldout_incorrect"], 0)

    def test_relational_probe_can_be_more_compact_than_raw_four_bits(self):
        row = trial(World("any_route", 3))
        self.assertEqual(row["sensor_program"]["operation"], "REACH2")
        self.assertEqual(row["sensor_source_reads"], 4)
        self.assertEqual(row["sensor_cardinality"], 2)
        self.assertEqual(row["heldout_incorrect"], 0)

    def test_trinary_path_count_sufficient_for_one_and_two_paths(self):
        for family in ("one_route", "two_routes"):
            with self.subTest(family=family):
                row = trial(World(family, 3))
                self.assertEqual(row["sensor_program"]["operation"],
                                 "PATHCOUNT")
                self.assertEqual(row["sensor_cardinality"], 3)
                self.assertEqual(row["heldout_incorrect"], 0)

    def test_identity_of_first_route_requires_binary_pair(self):
        row = trial(World("first_route_only", 3))
        self.assertEqual(row["sensor_program"]["operation"], "PATHPAIR")
        self.assertEqual(row["heldout_incorrect"], 0)

    def test_strong_raw_binary_fallback_beats_unsupported_assumptions(self):
        row = trial(World("edge_parity", 3))
        self.assertEqual(row["sensor_program"]["operation"], "RAW4")
        self.assertEqual(row["heldout_incorrect"], 0)
        self.assertEqual(trial(World("edge_parity", 3),
                              method="ternary")["heldout_covered"], 0)

    def test_full_portfolio_does_not_improve_on_complete_raw_bit_accuracy(self):
        for family in FAMILIES:
            with self.subTest(family=family):
                full = trial(World(family, 5), "all")
                binary = trial(World(family, 5), "binary")
                raw = trial(World(family, 5), "full_raw")
                self.assertEqual(full["review"], binary["review"])
                self.assertEqual(full["review"], raw["review"])
                self.assertEqual(full["heldout_covered"], raw["heldout_covered"])

    def test_hidden_context_and_distribution_shift_fail_review(self):
        for family in ("phase_shift", "unseen_context"):
            with self.subTest(family=family):
                row = trial(World(family, 5))
                self.assertEqual(row["review"]["status"],
                                 "HOLD_INDEPENDENT_FALSIFIER")
                self.assertGreater(row["review"]["failures"], 0)
                self.assertEqual(row["heldout_covered"], 0)

    def test_budget_and_typed_synthetic_query_boundary(self):
        world = World("any_route")
        initial = world.initial()
        self.assertEqual(len(initial), 8)
        controls = tuple((a, b, c, 0)
                         for a in (0, 1) for b in (0, 1) for c in (0, 1))
        self.assertEqual(len(remaining_probes(controls, 8)), 8)
        self.assertEqual(remaining_probes(controls, 7), ())
        self.assertEqual(inquiry(world, budget=7)[2], "HOLD_UNFUNDED_QUERY")
        self.assertEqual(trial(world, budget=7)["heldout_covered"], 0)
        query = Query((1, 1, 1, 1))
        self.assertEqual(Query.from_packet(query.packet()), query)

    def test_sensor_program_packets_reject_privilege_and_bad_edges(self):
        sensor = Sensor("COUNT2", (0, 2))
        packet = sensor.packet()
        self.assertEqual(Sensor.from_packet(packet), sensor)
        malicious = (
            {"authority": "INTERNET"},
            {"real_world_authority": True},
            {"endpoint": "https://invalid.example"},
            {"operation": "EXEC"},
            {"edges": [0, 0]},
            {"edges": [4, 5]},
        )
        for diff in malicious:
            with self.subTest(diff=diff), self.assertRaises(ValueError):
                Sensor.from_packet({**packet, **diff})
        probe = Query((1, 0, 1, 0)).packet()
        for change in ({"authority": "PHYSICAL_ACTUATION"},
                       {"url": "https://invalid.example"},
                       {"controls": [1, 0, True, 0]}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                Query.from_packet({**probe, **change})

    def test_prediction_cartridge_rejects_tampering(self):
        model, _, _ = inquiry(World("one_route", 3))
        assert isinstance(model, SensorModel)
        packet = model.packet()
        self.assertEqual(SensorModel.from_packet(packet), model)
        corruption = (
            {"id": "sensor-model-" + "0" * 20},
            {"authority": "EXEC"},
            {"real_world_authority": True},
            {"status": "APPROVED"},
            {"source_digest": "bad"},
            {"mapping": [[3, 1]]},
            {"mapping": [[0, True]]},
            {"mapping": [[0, 1], [0, 0]]},
        )
        for diff in corruption:
            with self.subTest(diff=diff), self.assertRaises(ValueError):
                SensorModel.from_packet({**packet, **diff})

    def test_untrusted_source_readout_cannot_be_promoted(self):
        original = World("one_route").initial()[0]
        with self.assertRaises(ValueError):
            Readout(original.token, original.readings, 1,
                    provenance="REAL_PHYSICAL_SENSOR")
        with self.assertRaises(ValueError):
            Readout(original.token, original.readings, True)
        with self.assertRaises(ValueError):
            Readout(original.token, original.readings[:-1], original.outcome)
        with self.assertRaises(ValueError):
            discover([{"observation": original}])

    def test_review_is_not_fooled_by_replay(self):
        world = World("one_neighbor")
        model, _, _ = inquiry(world)
        review = world.partition("review")
        self.assertTrue(independent_review(model, review)["status"]
                        .startswith("ELIGIBLE"))
        self.assertEqual(
            independent_review(model, review[:16] * 2)["status"],
            "HOLD_DISTINCT_REVIEW_COVERAGE")
        self.assertEqual(independent_review(model, review[:15])["status"],
                         "HOLD_INSUFFICIENT_REVIEW")

    def test_transfer_requires_different_local_review(self):
        cases = counterfactual_transfer()
        self.assertTrue(cases["same_rule_renamed"]["status"]
                        .startswith("ELIGIBLE"))
        self.assertEqual(cases["different_rule"]["status"],
                         "HOLD_INDEPENDENT_FALSIFIER")

    def test_fixed_benchmark_does_not_grant_trinary_authority(self):
        r = benchmark()
        self.assertEqual(r["frozen_trinary_promotion"], "NO_TERNARY_PRIVILEGE")
        self.assertEqual(r["evaluation"]["all"]["worlds"], 50)
        self.assertEqual(r["evaluation"]["all"]["review_eligible"], 40)
        self.assertEqual(r["evaluation"]["all"]["held"], 10)
        self.assertEqual(r["evaluation"]["all"]["heldout_incorrect"], 0)
        self.assertEqual(r["evaluation"]["all"]["review_eligible"],
                         r["evaluation"]["binary"]["review_eligible"])
        self.assertEqual(r["evaluation"]["all"]["review_eligible"],
                         r["evaluation"]["full_raw"]["review_eligible"])
        self.assertEqual(r["evaluation"]["all"]["ternary_proposals"], 15)
        self.assertEqual(r["binary_encoding_ablation"]["ternary_proposals"], 0)
        self.assertEqual(r["external_actions"], 0)
        self.assertFalse(r["real_world_authority"])


if __name__ == "__main__":
    unittest.main()
