"""Deterministic geometry controls: correctness, abstentions and fair baselines."""
import unittest
from math import hypot

from geometry import (
    circle_intersections, edges, flower, from_xy, hex_distance, pathfind,
    propose_centers, rotate60, svg_flower, to_xy,
)


class FlowerTests(unittest.TestCase):
    def test_exact_counts_and_edge_invariants(self):
        for n in range(6):
            cells = flower(n)
            self.assertEqual(len(cells), 1 + 3 * n * (n + 1))
            self.assertEqual(len(set(cells)), len(cells))
            self.assertEqual(len(edges(cells)), 3 * n * (3 * n + 1))
            self.assertTrue(all(hex_distance(a, b) == 1 for a, b in edges(cells)))
        self.assertEqual(len(flower(2)), 19)
        with self.assertRaises(ValueError):
            flower(-1)

    def test_sixfold_symmetry_is_exact(self):
        for n in (1, 2, 4):
            cells = set(flower(n))
            self.assertEqual({rotate60(c) for c in cells}, cells)
            for c in cells:
                moved = c
                for _ in range(6):
                    moved = rotate60(moved)
                self.assertEqual(moved, c)

    def test_distance_and_intersections(self):
        a, b = to_xy((0, 0)), to_xy((1, 0))
        self.assertAlmostEqual(hypot(b[0] - a[0], b[1] - a[1]), 1.0)
        intersections = circle_intersections(a, b, 1.0)
        self.assertEqual(len(intersections), 2)
        self.assertEqual({from_xy(*p) for p in intersections},
                         {(0, 1), (1, -1)})
        self.assertEqual(circle_intersections((0, 0), (0, 0), 1), ())
        self.assertEqual(circle_intersections((0, 0), (3, 0), 1), ())
        self.assertEqual(circle_intersections((0, 0), (2, 0), 1),
                         ((1.0, 0.0),))

    def test_metric_calibration_is_a_real_gate(self):
        for c in flower(3):
            xy = to_xy(c, 17)
            self.assertEqual(from_xy(*xy, radius=17), c)
        self.assertIsNone(from_xy(0.21, 0.37))
        self.assertIsNone(from_xy(1.15, 0.0, radius=1.0))
        with self.assertRaises(ValueError):
            from_xy(0, 0, radius=0)

    def test_missing_circles_are_proposals_not_facts(self):
        full = set(flower(2))
        absent = {(0, 1), (1, -1)}
        observed = full - absent
        proposals = propose_centers(observed, max_ring=2)
        found = {tuple(p["center"]) for p in proposals}
        self.assertEqual(found, absent)
        self.assertTrue(all(p["status"] == "PROPOSAL_ONLY" for p in proposals))
        self.assertEqual(len(observed), 17)
        self.assertNotIn((0, 1), observed)

    def test_sparse_tangent_observations_still_propose_middle(self):
        proposal = propose_centers({(0, 1), (0, -1)}, max_ring=1)
        found = {tuple(p["center"]) for p in proposal}
        self.assertIn((0, 0), found)

    def test_cannot_claim_outside_declared_field(self):
        with self.assertRaises(ValueError):
            propose_centers({(3, 0)}, max_ring=2)
        self.assertEqual(propose_centers({(0, 0)}, max_ring=2), [])

    def test_hypothetical_circles_cannot_be_traversed(self):
        observed = set(flower(2)) - {(0, 0)}
        result = pathfind(observed, (1, 0), (0, 0))
        self.assertEqual(result["status"], "HOLD")
        self.assertEqual(result["path"], [])

    def test_hex_astar_equals_exact_classical_baseline(self):
        for n in (2, 4, 6):
            cells = set(flower(n))
            start, goal = (-n, 0), (n, 0)
            a = pathfind(cells, start, goal, geometry_heuristic=True)
            baseline = pathfind(cells, start, goal, geometry_heuristic=False)
            self.assertEqual(a["status"], "PATH")
            self.assertEqual(a["distance"], 2 * n)
            self.assertEqual(a["distance"], baseline["distance"])
            self.assertLessEqual(a["expanded"], baseline["expanded"])

    def test_blocked_paths_remain_optimal_or_held(self):
        cells = set(flower(3))
        scenarios = [
            dict(blocked={(0, 0)}),
            dict(blocked={(0, 0), (1, -1), (-1, 1)}),
            dict(missing_edges={((-3, 0), (-2, 0))}),
        ]
        for kwargs in scenarios:
            with self.subTest(kwargs=kwargs):
                a = pathfind(cells, (-3, 0), (3, 0),
                             geometry_heuristic=True, **kwargs)
                b = pathfind(cells, (-3, 0), (3, 0),
                             geometry_heuristic=False, **kwargs)
                self.assertEqual(a["status"], b["status"])
                self.assertEqual(a.get("distance"), b.get("distance"))
        held = pathfind(cells, (0, 0), (1, 0),
                        blocked=set(cells) - {(0, 0), (1, 0)},
                        missing_edges={((0, 0), (1, 0))})
        self.assertEqual(held["status"], "HOLD")

    def test_svg_marks_hypothesis_distinctly(self):
        svg = svg_flower({(0, 0), (1, 0)}, {(0, 1)})
        self.assertIn("<svg", svg)
        self.assertIn("stroke-dasharray", svg)
        self.assertEqual(svg.count("<circle"), 6)


if __name__ == "__main__":
    unittest.main()
