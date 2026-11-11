"""VOID-002: pure falsifiers plus native MOTIF-003 smoke."""
import unittest
from collections import Counter
from dataclasses import dataclass
from frontier import POLICIES, source_moves, potential_reveal, choose


@dataclass(frozen=True)
class Cell:
    xy: tuple
    material: str
    object_present: bool = False


class Belief:
    def __init__(self, start=(32, 32), walls=()):
        self.start = start
        cells = {}
        for x in range(start[0]-3, start[0]+4):
            for y in range(start[1]-3, start[1]+4):
                p = (x, y)
                cells[p] = Cell(p, "stone" if p in walls else "grass")
        self.grid = cells
        self.cells = tuple(cells.values())


class FrontierTests(unittest.TestCase):
    def test_declared_policies(self):
        self.assertEqual(POLICIES, ("classical_2ply", "motif003", "classical_1ply"))

    def test_observed_wall_blocks_candidate(self):
        b = Belief(walls={(33,32), (32,31), (32,33)})
        moves = source_moves(b, b.start)
        self.assertEqual([a for a, _ in moves], ["move_left"])
        seen = {c.xy for c in b.cells}
        for policy in POLICIES:
            self.assertEqual("move_left", choose(b, seen, Counter(), policy))

    def test_never_promote_future_sightlines_to_observed_facts(self):
        b = Belief()
        seen = {c.xy for c in b.cells}
        unknown = potential_reveal((33,32), seen)
        self.assertTrue(unknown.isdisjoint(seen))
        self.assertTrue(all(0 <= x < 64 and 0 <= y < 64 for x, y in unknown))

    def test_sensor_ledger_must_include_current_observation(self):
        with self.assertRaises(ValueError):
            choose(Belief(), set(), Counter(), "motif003")

    def test_unregistered_policy_refused(self):
        b = Belief()
        with self.assertRaises(ValueError):
            choose(b, {c.xy for c in b.cells}, Counter(), "unreviewed")

    def test_all_first_moves_use_same_visible_walkable_tiles(self):
        b = Belief(walls={(33,32), (32,31)})
        seen = {c.xy for c in b.cells}
        options = {a for a, _ in source_moves(b, b.start)}
        for policy in POLICIES:
            self.assertIn(choose(b, seen, Counter(), policy), options)


if __name__ == "__main__":
    unittest.main()
