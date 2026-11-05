"""Adversarial LAW-FORGE-006 tests: derived sensors are not supplied as a menu."""
import json
import tempfile
import unittest
from pathlib import Path

from inventor import (
    GraphQuery, Instrument, Proposal, Witness, evidence_digest, fit_old_four_edge,
    generated_programs, query_missing, review, synthesize
)
from owner import FAMILIES, World, owner_contract
from trial import benchmark, negative_transfer, inspect_source, trial
from bridge import DOGRAM_COMMIT, DOGRAM_REPO, dogram_specimens, emit, verify


class InstrumentInventorTests(unittest.TestCase):
    def test_old_observation_interface_is_insufficient_for_six_links(self):
        from pathlib import Path
        import sys
        sys.path.append(str(Path(__file__).resolve().parents[1] / "law-forge-005"))
        from instrument import bits4
        with self.assertRaises(ValueError):
            bits4((0, 0, 0, 0, 1, 1))
        self.assertEqual(owner_contract()["edge_count"], 6)
        self.assertEqual(owner_contract()["read_capabilities"],
                         ["READ_ONE_SYNTHETIC_LINK"])
        self.assertNotIn("REACH2", owner_contract()["instrument_vocabulary"])

    def test_search_language_contains_no_prebuilt_path_sensor(self):
        candidates = generated_programs()
        self.assertEqual(len(candidates), 1561)
        self.assertEqual(set(owner_contract()["instrument_vocabulary"]),
                         {"AND", "OR", "READ_ONE_SYNTHETIC_LINK"})
        self.assertEqual(candidates[0], Instrument(((0,),)))
        self.assertTrue(all(1 <= len(p.clauses) <= 3 for p in candidates))

    def test_instrument_is_synthesized_from_six_owned_edge_reads(self):
        model, probes, data, status = inspect_source(World("any_three_paths", 2))
        self.assertIsInstance(model, Proposal)
        self.assertEqual(status, "PROPOSE_DERIVED_SENSOR")
        self.assertEqual(len(probes), 32)
        self.assertEqual(len(data), 64)
        self.assertEqual(model.sensor.clauses,
                         ((0, 1), (2, 3), (4, 5)))
        self.assertEqual(model.sensor.referenced_links, (0, 1, 2, 3, 4, 5))
        self.assertEqual(model.sensor.predict((0, 0, 0, 0, 1, 1)), 1)
        self.assertEqual(model.sensor.predict((1, 0, 0, 0, 0, 0)), 0)

    def test_single_edge_and_cross_pairs_are_not_hardcoded(self):
        expected = {
            "last_path": ((4, 5),),
            "first_two_paths": ((0, 1), (2, 3)),
            "middle_edge": ((3,),),
            "edge_or": ((0,), (5,)),
            "cross_pair_paths": ((0, 3), (2, 5)),
        }
        for family, clauses in expected.items():
            with self.subTest(family=family):
                model, _, _, _ = inspect_source(World(family, 1))
                self.assertEqual(model.sensor.clauses, clauses)

    def test_old_four_edge_model_loses_new_3rd_path(self):
        baseline = trial(World("any_three_paths", 2), "old_four_link")
        invented = trial(World("any_three_paths", 2), "inventor")
        self.assertEqual(baseline["review"]["status"],
                         "HOLD_NO_SUPPORTED_MODEL")
        self.assertEqual(baseline["withheld_covered"], 0)
        self.assertEqual(invented["withheld_covered"], 64)
        self.assertEqual(invented["withheld_wrong"], 0)

    def test_strong_full_raw_baseline_recovers_nonmonotone_worlds(self):
        for family in ("at_least_two_paths", "exactly_one_path",
                       "edge_parity", "three_edge_joint"):
            with self.subTest(family=family):
                result = trial(World(family, 4), "inventor")
                self.assertEqual(result["review"]["status"],
                                 "HOLD_NO_SUPPORTED_MODEL")
                self.assertEqual(result["withheld_covered"], 0)
                raw = trial(World(family, 4), "full_six_link")
                self.assertEqual(raw["withheld_covered"], 64)
                self.assertEqual(raw["withheld_wrong"], 0)

    def test_hidden_context_and_shifted_rule_are_falsified(self):
        for family in ("phase_shift", "hidden_context"):
            with self.subTest(family=family):
                row = trial(World(family, 4))
                self.assertEqual(row["review"]["status"],
                                 "HOLD_INDEPENDENT_FALSIFIER")
                self.assertGreater(row["review"]["contradictions"], 0)
                self.assertEqual(row["withheld_covered"], 0)
                self.assertIsNone(row["new_destination_review"])

    def test_budget_31_cannot_fake_complete_instrument_inquiry(self):
        world = World("any_three_paths")
        queries = query_missing(world.initial(), 32)
        self.assertEqual(len(queries), 32)
        self.assertEqual(query_missing(world.initial(), 31), ())
        self.assertEqual(inspect_source(world, budget=31)[3],
                         "HOLD_PROBE_BUDGET")
        self.assertEqual(trial(world, budget=31)["withheld_covered"], 0)
        with self.assertRaises(ValueError):
            query_missing(world.initial(), True)

    def test_program_packet_is_data_only_and_hash_addressed(self):
        model, _, _, _ = inspect_source(World("any_three_paths"))
        packet = model.packet()
        self.assertEqual(Proposal.from_packet(packet), model)
        self.assertFalse(packet["real_world_authority"])
        self.assertEqual(packet["status"], "PROPOSE_ONLY")
        evil = (
            {"status": "AUTHORIZED"},
            {"authority": "NETWORK"},
            {"real_world_authority": True},
            {"url": "https://example.invalid"},
            {"id": "instrument-" + "0" * 24},
            {"source_digest": "unknown"},
            {"sensor": {"operator": "SHELL", "clauses": [[0]],
                        "atoms": "READ_ONE_SYNTHETIC_LINK",
                        "read_only": True}},
            {"sensor": {"operator": "OR_OF_AND", "clauses": [[0, 1, 2]],
                        "atoms": "READ_ONE_SYNTHETIC_LINK",
                        "read_only": True}},
        )
        for corrupted in evil:
            with self.subTest(corrupted=corrupted), self.assertRaises(ValueError):
                Proposal.from_packet({**packet, **corrupted})

    def test_query_packet_disallows_privileged_actuation(self):
        probe = GraphQuery((0, 0, 0, 0, 1, 1))
        self.assertEqual(GraphQuery.from_packet(probe.packet()), probe)
        for bad in (
            {"authority": "REMOTE_ACTUATION"},
            {"endpoint": "https://example.invalid"},
            {"controls": [1, 0, 0, 0, True, 1]},
        ):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                GraphQuery.from_packet({**probe.packet(), **bad})

    def test_duplicate_or_forged_observations_refused(self):
        source = World("any_three_paths")
        x = source.measure((1, 0, 0, 0, 1, 0))
        with self.assertRaises(ValueError):
            Witness(x.inputs, True, x.token)
        with self.assertRaises(ValueError):
            Witness(x.inputs, 1, x.token, provenance="REAL_WITNESS")
        with self.assertRaises(ValueError):
            synthesize([{"inputs": x.inputs, "result": 1}])
        with self.assertRaises(ValueError):
            synthesize([x, Witness(x.inputs, 1 - x.result, "another_token_test")])

    def test_independent_review_rejects_replayed_cases(self):
        world = World("any_three_paths")
        model, _, _, _ = inspect_source(world)
        rows = world.independent("review")
        self.assertTrue(review(model, rows)["status"].startswith("ELIGIBLE"))
        self.assertEqual(review(model, rows[:32] * 2)["status"],
                         "HOLD_REVIEW_COVERAGE")
        self.assertEqual(review(model, rows[:16])["status"],
                         "HOLD_INSUFFICIENT_REVIEW")

    def test_source_owned_conformance_does_not_admit_to_GRAFT(self):
        r = negative_transfer()
        self.assertEqual(r["matching_renamed_source"]["status"],
                         "PROPOSE_ONLY_REVIEW_PASSED")
        self.assertEqual(r["changed_rule"]["status"],
                         "HOLD_SOURCE_CONFORMANCE_FAILURE")
        self.assertEqual(r["unmeasured_hidden_context"]["status"],
                         "HOLD_SOURCE_CONFORMANCE_FAILURE")
        self.assertFalse(r["matching_renamed_source"]["automatic_admission"])

    def test_alex_graft_handoff_is_explicitly_unstored_unadmitted(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)
            emit(path)
            alex = json.loads((path / "alex-proposal.json").read_text())
            graft = json.loads((path / "graft-proposal.json").read_text())
            manifest = json.loads((path / "manifest.json").read_text())
            self.assertEqual(alex["status"], "PROPOSE_TO_ALEX_NOT_STORED")
            self.assertEqual(graft["status"], "PROPOSE_TO_GRAFT_NOT_IMPORTED")
            self.assertEqual(graft["graft_native_compile"], "NOT_ATTEMPTED")
            self.assertEqual(alex["witness_layer"]["count"], 64)
            self.assertEqual(manifest["dogram_commit"], DOGRAM_COMMIT)
            self.assertFalse(graft["automatic_admission"])

    def test_native_dogram_specimens_have_precise_graph_ablation(self):
        model, _, _, _ = inspect_source(World("any_three_paths"))
        specs = dogram_specimens(model)
        self.assertEqual(len(specs), 3)
        for i, specimen in enumerate(specs):
            with self.subTest(i=i):
                self.assertEqual(specimen["schema"], "dogram.specimen/v0")
                self.assertEqual(specimen["operator"], "ablate")
                self.assertEqual(specimen["operator_version"], 1)
                self.assertEqual(len(specimen["inputs"]["graph"]["edges"]), 2)
                self.assertEqual(specimen["inputs"]["requested_targets"],
                                 [["S", "T"]])

    def test_fake_native_receipt_is_not_accepted(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)
            emit(path)
            with self.assertRaises(FileNotFoundError):
                verify(path)
            for i in range(3):
                specimen = json.loads((path / f"dogram-{i}.json").read_text())
                fake = {
                    "schema": "dogram.receipt/v0",
                    "specimen_id": specimen["specimen_id"],
                    "status": "REFUSE",
                    "operator": "ablate", "operator_version": 1,
                    "result": None
                }
                (path / f"dogram-{i}.receipt.json").write_text(json.dumps(fake))
            with self.assertRaises(AssertionError):
                verify(path)

    def test_predeclared_benchmarks_and_method_refusal(self):
        data = benchmark()
        self.assertEqual(data["frozen_method_decision"], "NO_METHOD_PROMOTION")
        results = data["final_evaluation"]
        self.assertEqual(results["inventor"]["worlds"], 65)
        self.assertEqual(results["inventor"]["review_eligible"], 35)
        self.assertEqual(results["inventor"]["held"], 30)
        self.assertEqual(results["inventor"]["withheld_wrong"], 0)
        self.assertEqual(results["old_four_link"]["review_eligible"], 15)
        self.assertEqual(results["full_six_link"]["review_eligible"], 55)
        self.assertEqual(data["external_actions"], 0)
        self.assertFalse(data["automatic_integration"])


if __name__ == "__main__":
    unittest.main()
