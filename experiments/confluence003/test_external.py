"""Independent-source falsifiers, no benchmark labels passed into A*."""
from __future__ import annotations

from dataclasses import replace
import copy
import unittest

from source import (GridOwner, parse_map, Grid, Scene, UPSTREAM_COMMIT,
                    verified_root, load_map_and_scenarios, deterministic_cohort,
                    dijkstra, astar, check_route, digest)
from cross import (native_modules, ProofService, source_verified_affordance,
                   native_route_macro, options_mask, fixed_three_option_cells)
from trial import run_trial, MODES


class IndependentSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.modules = native_modules()
        cls.proof = ProofService(cls.modules)
        cls.grid = {}
        cls.cohort = {}
        for name in ("tiny", "dragonage"):
            g, source_rows = load_map_and_scenarios(name)
            cls.grid[name] = g
            cls.cohort[name] = deterministic_cohort(name, source_rows)

    def test_independent_data_pinned_not_embedded(self):
        self.assertEqual(verified_root(), UPSTREAM_COMMIT)
        self.assertEqual(self.grid["tiny"].height, 21)
        self.assertEqual(self.grid["tiny"].width, 30)
        self.assertEqual(self.grid["dragonage"].height, 49)
        self.assertEqual(self.grid["dragonage"].width, 49)
        self.assertTrue(all(len(v) == 8 for v in self.cohort.values()))
        for subset in self.cohort.values():
            self.assertEqual(sorted(set(s.bucket for s in subset)), [0, 2, 4, 6])

    def test_pub_oracle_matches_two_competitive_classical_methods(self):
        for name in self.grid:
            grid = self.grid[name]
            for scene in self.cohort[name][:4]:
                a = astar(grid, scene.start, scene.goal)
                d = dijkstra(grid, scene.start, scene.goal)
                self.assertIsNotNone(a)
                self.assertIsNotNone(d)
                self.assertAlmostEqual(a[1], d[1], places=7)
                self.assertLess(abs(a[1] - scene.oracle_length), 0.0001)
                self.assertAlmostEqual(a[1], check_route(grid, a[0]), places=7)

    def test_native003_affordance_from_external_grid(self):
        grid = self.grid["tiny"]
        scene = self.cohort["tiny"][2]
        report = source_verified_affordance(grid, scene.start)
        self.assertEqual(report["module"], "ORIGINAL_MOTIF_003")
        self.assertGreater(report["local_options"], 0)
        self.assertTrue(report["ranking_is_not_path_optimality"])

    def test_route_macro_native_006_reuses_exact_source_edges(self):
        grid = self.grid["dragonage"]
        scene = next(s for s in self.cohort["dragonage"]
                     if len(astar(grid, s.start, s.goal)[0]) > 3)
        path = astar(grid, scene.start, scene.goal)[0]
        proof = native_route_macro(grid, path, self.modules)
        self.assertEqual(proof["status"], "NATIVE_TWO_STEP_CERTIFIED")
        self.assertTrue(proof["permission_guard"])
        self.assertTrue(proof["edge_guard"])
        self.assertEqual(proof["replayed_primitive_steps"], 2)
        self.assertEqual(native_route_macro(grid, path[:2], self.modules)["status"],
                         "HOLD_NOT_TWO_VERIFIED_EDGES")

    def test_external_complete_task_adapters(self):
        for name in self.grid:
            grid = self.grid[name]
            scene = next(s for s in self.cohort[name]
                         if len(astar(grid, s.start, s.goal)[0]) >= 3
                         and len(tuple(grid.neighbors(s.start))) > 1)
            report = run_trial(grid, scene, self.modules, self.proof)
            self.assertEqual(report["source_origin_count"], 1)
            self.assertTrue(report["native_003"])
            self.assertTrue(report["native_006"])
            self.assertTrue(report["native_proof001"])
            self.assertTrue(report["controlled_fault_injection"])
            self.assertTrue(report["native_008"])
            self.assertEqual(report["reentry_new_development_questions"], 0)
            self.assertTrue(report["proof_identity_not_authenticated"])
            self.assertEqual(report["authority"],
                             "NO_EXTERNAL_ACTIONS_OR_REAL_WORLD_SAFETY_CLAIM")

    def test_all_real_native_ablations_preserve_classical_route(self):
        g = self.grid["tiny"]
        scene = next(s for s in self.cohort["tiny"]
                     if len(astar(g, s.start, s.goal)[0]) >= 3
                     and len(tuple(g.neighbors(s.start))) > 1)
        cases = {mode: run_trial(g, scene, self.modules, self.proof, mode)
                 for mode in MODES}
        base = cases["FULL"]
        for x in cases.values():
            self.assertEqual(x["pre_change_astar_cost"], base["pre_change_astar_cost"])
            self.assertEqual(x["post_change_astar_cost"], base["post_change_astar_cost"])
        self.assertFalse(cases["NO_003"]["native_003"])
        self.assertFalse(cases["NO_006"]["native_006"])
        self.assertFalse(cases["NO_FIELD"]["native_008"])
        self.assertFalse(cases["NO_PROOF"]["native_proof001"])

    def test_false_published_length_rejected(self):
        g, scene = self.grid["tiny"], self.cohort["tiny"][1]
        wrong = replace(scene, oracle_length=scene.oracle_length+1)
        with self.assertRaises(RuntimeError):
            run_trial(g, wrong, self.modules, self.proof)

    def test_owner_preserves_history_after_controlled_change(self):
        g = self.grid["tiny"]
        scene = next(s for s in self.cohort["tiny"]
                     if len(astar(g, s.start, s.goal)[0]) >= 2)
        cell = astar(g, scene.start, scene.goal)[0][1]
        owner = GridOwner(g)
        old = owner.observe(cell)
        self.assertTrue(old["answer"])
        owner.shift_block(cell)
        new = owner.observe(cell)
        self.assertFalse(new["answer"])
        self.assertTrue(owner.verify(old))
        self.assertTrue(owner.verify(new))
        self.assertTrue(owner.check())
        self.assertNotEqual(old["sha256"], new["sha256"])

    def test_forged_rehashed_source_origin_fails(self):
        owner = GridOwner(self.grid["tiny"])
        item = owner.observe(self.cohort["tiny"][0].start)
        fake = copy.deepcopy(item)
        fake["origin"] = "IMAGINARY_SECOND_INDEPENDENT_WITNESS"
        fake["sha256"] = digest({k: v for k, v in fake.items() if k != "sha256"})
        self.assertFalse(owner.verify(fake))
        self.assertTrue(owner.verify(item))

    def test_finite_3bit_proof_cannot_overclaim_grid_route(self):
        x = self.proof.verify_update(5, 2, 7)
        self.assertEqual(x["status"], "NATIVE_SCOPED_SET_PROOF")
        self.assertEqual(x["scope"], "ONLY_THREE_LOCAL_DIRECTION_OPTIONS")
        self.assertTrue(x["NO_GLOBAL_ROUTE_OR_PHYSICAL_SAFETY_PROOF"])
        with self.assertRaises(RuntimeError):
            self.proof.verify_update(5, 2, 6)

    def test_unsupported_format_holds(self):
        with self.assertRaises(ValueError):
            parse_map("other", "type octile\nheight 1\nwidth 2\nmap\n.W\n")
        with self.assertRaises(ValueError):
            parse_map("other", "type wrong\nheight 1\nwidth 1\nmap\n.\n")
        with self.assertRaises(ValueError):
            run_trial(self.grid["tiny"], self.cohort["tiny"][0],
                      self.modules, self.proof, "AUTO_INSTALL_APP")


if __name__ == "__main__":
    unittest.main()
