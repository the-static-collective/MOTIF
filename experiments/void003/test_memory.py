"""Pure, no-game cross-run tests before live third-party trial."""
from dataclasses import dataclass
import unittest
from memory import EpisodicMap,signature,waypoint_action

@dataclass(frozen=True)
class Cell:
    xy:tuple
    material:str
    object_present:bool=False

class Belief:
    def __init__(self,start,cells,face=(0,1)):
        self.start=start;self.cells=tuple(cells);self.facing=face
        self.grid={c.xy:c for c in cells}


def b(start=(0,0),end=5,target=True):
    cells=[Cell((x,0),"grass") for x in range(end)]
    if target: cells.append(Cell((end,0),"water"))
    return Belief(start,cells)

class MemoryTests(unittest.TestCase):
    def test_export_import_and_same_seed_reset(self):
        first=b();m=EpisodicMap(11,first);data=m.export()
        self.assertEqual(m.coordinates,EpisodicMap.admit(data,11,first).coordinates)
        with self.assertRaises(ValueError): EpisodicMap.admit(data,12,first)
        with self.assertRaises(ValueError): EpisodicMap.admit(data,11,b(target=False))
    def test_tamper_rejected(self):
        m=EpisodicMap(11,b());data=m.export();data["historical_cells"][0][1]="gold"
        with self.assertRaises(ValueError): EpisodicMap.admit(data,11,b())
    def test_full_path_towards_offscreen_remembered_water(self):
        reset=b(end=2,target=False);m=EpisodicMap(11,reset)
        m.remember(b(end=6,target=True))
        out=waypoint_action(reset,m,"game_drink_obtained")
        self.assertEqual(out["action"],"move_right")
        self.assertTrue(out["first_move_verified_in_current_sensor"])
    def test_stale_local_observation_cannot_override_now(self):
        reset=b(end=2,target=False);m=EpisodicMap(11,reset)
        m.remember(b(end=6,target=True))
        changed=Belief((0,0),[Cell((0,0),"grass"),Cell((1,0),"stone")])
        self.assertIsNone(waypoint_action(changed,m,"game_drink_obtained"))
    def test_memory_without_witnessed_resource_cannot_invent_target(self):
        reset=b(end=2,target=False);m=EpisodicMap(11,reset)
        self.assertIsNone(waypoint_action(reset,m,"game_drink_obtained"))
    def test_no_offscreen_step_forged_into_live_sensor(self):
        reset=Belief((0,0),[Cell((0,0),"grass")])
        m=EpisodicMap(11,reset)
        m.remember(b(end=6,target=True))
        self.assertIsNone(waypoint_action(reset,m,"game_drink_obtained"))
    def test_noncanonical_goal_refused(self):
        with self.assertRaises(ValueError):
            waypoint_action(b(),EpisodicMap(1,b()),"human_water")

if __name__=="__main__":unittest.main()
