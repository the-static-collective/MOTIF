"""Adversarial standard-library tests: LAW-FORGE-003 operator foundry."""
import unittest
from copy import deepcopy

from foundry import (
    Example, NandCircuit, Operator, Query, bits, gate_library,
    possibilities, propose, review
)
from world import World, FAMILIES
from trial import METHODS, benchmark, identify, trial, transfer_falsification


class OperatorFoundryTests(unittest.TestCase):
    def test_nand_is_the_only_executable_primitive(self):
        library = dict(gate_library())
        # No XOR, OR or AND special-case compiler opcode exists.
        self.assertIn((0, 1, 1, 0), library)
        self.assertIn((0, 1, 1, 1), library)
        self.assertIn((0, 0, 0, 1), library)
        self.assertEqual(len(library[(0, 1, 1, 0)].gates), 4)
        self.assertEqual(len(library[(0, 1, 1, 1)].gates), 3)
        self.assertEqual(len(library[(0, 0, 0, 1)].gates), 2)

    def test_actual_gate_netlist_executes_unseen_long_sequences(self):
        xor = dict(gate_library())[(0, 1, 1, 0)]
        self.assertEqual(xor.run((1, 0, 1, 1, 0, 1, 1, 1)), 0)
        self.assertEqual(xor.run((1, 0, 1, 1, 0, 1, 1)), 1)
        self.assertEqual(NandCircuit.from_data(xor.data()), xor)

    def test_initial_two_competing_operators_no_hidden_label(self):
        observations = World("parity_fold").initial_observations()
        candidates = possibilities(observations)
        self.assertEqual([c.signature for c in candidates],
                         [(0, 1, 1, 0), (0, 1, 1, 1)])
        # The exact family name is only inside evaluator world.py.
        self.assertEqual({len(c.circuit.gates) for c in candidates}, {3, 4})

    def test_probe_is_information_discriminating_not_prebaked_label(self):
        world = World("parity_fold")
        observations = world.initial_observations()
        options = possibilities(observations)
        query = propose(options, observations)
        self.assertIsNotNone(query)
        self.assertEqual(query.inputs, (1, 1))
        self.assertEqual(query.information_bits, 1.0)
        self.assertEqual(query.cost, 3)
        self.assertEqual(Query.from_packet(query.packet()).inputs, query.inputs)

    def test_local_budget_and_prohibition_halt(self):
        rows = World("parity_fold").initial_observations()
        options = possibilities(rows)
        self.assertIsNone(propose(options, rows, remaining_cost=2))
        self.assertIsNone(propose(options, rows, prohibited=((1, 1),)))
        with self.assertRaises(ValueError):
            propose(options, rows, remaining_cost=-1)
        self.assertEqual(trial(World("parity_fold"), budget=0)["test_covered"], 0)

    def test_xor_is_discovered_as_nand_operator_not_or(self):
        op, probes, status = identify(World("parity_fold", 2))
        self.assertEqual(status, "OPERATOR_PROPOSED")
        self.assertEqual(len(probes), 1)
        self.assertEqual(op.signature, (0, 1, 1, 0))
        self.assertEqual(len(op.circuit.gates), 4)
        self.assertEqual(op.predict((1, 0, 1, 0, 1)), 1)

    def test_or_and_construction_from_same_nand_primitive(self):
        for family, signature, count in (
            ("any_on_fold", (0, 1, 1, 1), 3),
            ("all_on_fold", (0, 0, 0, 1), 2)
        ):
            with self.subTest(family=family):
                op, _, _ = identify(World(family, 3))
                self.assertEqual(op.signature, signature)
                self.assertEqual(len(op.circuit.gates), count)

    def test_generated_operator_round_trip_and_checksum(self):
        op, _, _ = identify(World("parity_fold"))
        packet = op.packet()
        self.assertEqual(Operator.from_packet(packet), op)
        self.assertFalse(packet["real_world_authority"])
        self.assertEqual(packet["status"], "PROPOSAL_ONLY")
        self.assertEqual(packet["netlist"]["primitive"], "NAND")

    def test_adversarial_operator_cartridge_tampering_refused(self):
        packet = identify(World("parity_fold"))[0].packet()
        mutations = [
            {"authority": "EXTERNAL_ACTION"},
            {"real_world_authority": True},
            {"status": "AUTHORIZED"},
            {"callback_url": "https://example.invalid"},
            {"signature": [1, 1, 1, 1]},
            {"id": "operator-" + "0"*24},
            {"netlist": {"primitive": "PYTHON", "wires": 2,
                         "gates": [[0, 0]], "output_pin": 0}},
            {"netlist": {"primitive": "NAND", "wires": 2,
                         "gates": [[0, 7]], "output_pin": 0}},
        ]
        for diff in mutations:
            with self.subTest(diff=diff), self.assertRaises(ValueError):
                Operator.from_packet({**packet, **diff})

    def test_malformed_observations_and_queries_rejected(self):
        with self.assertRaises(ValueError):
            Example((0, 1), True)
        with self.assertRaises(ValueError):
            Example((0, 1), 1, provenance="REAL_THIRD_PARTY")
        with self.assertRaises(ValueError):
            possibilities([{"inputs": [0, 1], "outcome": 1}])
        packet = Query((1, 1), 1.0, 3).packet()
        for diff in ({"authority": "NETWORK"}, {"url": "https://x.invalid"},
                     {"inputs": [1, True]}, {"declared_cost": 0}):
            with self.subTest(diff=diff), self.assertRaises(ValueError):
                Query.from_packet({**packet, **diff})

    def test_all_three_true_fold_worlds_transfer_to_unseen_lengths(self):
        for f in FAMILIES[:3]:
            with self.subTest(family=f):
                row = trial(World(f, 3))
                self.assertTrue(row["review"]["status"].startswith("ELIGIBLE"))
                self.assertGreater(row["test_covered"], 32)
                self.assertEqual(row["test_incorrect"], 0)
                self.assertTrue(row["transfer_review"]["status"].startswith("ELIGIBLE"))

    def test_nonfold_and_shifting_worlds_do_not_get_falsely_admitted(self):
        for f in FAMILIES[3:]:
            with self.subTest(family=f):
                row = trial(World(f, 3))
                self.assertEqual(row["review"]["status"],
                                 "HOLD_INDEPENDENT_FALSIFIER")
                self.assertGreater(row["review"]["contradictions"], 0)
                self.assertEqual(row["test_covered"], 0)
                self.assertIsNone(row["transfer_review"])

    def test_no_forged_coverage_from_repeated_review_rows(self):
        model = identify(World("parity_fold"))[0]
        full = World("parity_fold").partition("review")
        self.assertEqual(review(model, full[:10])["status"],
                         "HOLD_INSUFFICIENT_REVIEW")
        self.assertEqual(review(model, full[:10] * 4)["status"],
                         "HOLD_REVIEW_COVERAGE")

    def test_destination_must_revalidate_not_inherit_permission(self):
        result = transfer_falsification()
        self.assertTrue(result["revalidated_equivalent"]["status"].startswith("ELIGIBLE"))
        self.assertEqual(result["rejected_different_rule"]["status"],
                         "HOLD_INDEPENDENT_FALSIFIER")

    def test_classical_table_is_a_strong_matched_control(self):
        for f in FAMILIES:
            with self.subTest(family=f):
                a = trial(World(f, 4), "nand_adaptive")
                b = trial(World(f, 4), "table_fixed")
                self.assertEqual(a["review"], b["review"])
                self.assertEqual(a["test_incorrect"], b["test_incorrect"])
                self.assertEqual(a["test_covered"], b["test_covered"])
                self.assertEqual(a["declared_probe_cost"], b["declared_probe_cost"])

    def test_method_decision_refuses_promotion_on_classical_tie(self):
        report = benchmark()
        self.assertEqual(report["frozen_method_decision"], "NO_METHOD_PROMOTION")
        evaluation = report["evaluation"]
        self.assertEqual(evaluation["nand_adaptive"], evaluation["nand_fixed"])
        self.assertEqual(evaluation["nand_adaptive"], evaluation["table_fixed"])
        self.assertEqual(evaluation["nand_adaptive"]["worlds"], 35)
        self.assertEqual(evaluation["nand_adaptive"]["review_eligible"], 15)
        self.assertEqual(evaluation["nand_adaptive"]["held"], 20)
        self.assertEqual(evaluation["nand_adaptive"]["test_incorrect"], 0)
        self.assertEqual(evaluation["nand_adaptive"]["local_synthetic_queries"], 35)
        self.assertEqual(report["external_operations"], 0)
        self.assertFalse(report["real_world_authority"])


if __name__ == "__main__":
    unittest.main()
