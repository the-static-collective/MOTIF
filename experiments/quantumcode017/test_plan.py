"""QC-017: search, partial observation, source receipts and falsifiers."""
import unittest
from collections import deque
from dataclasses import replace

from plan import (
    Belief,SeenCell,Plan,observe,traverse,check_goals,plans_for_goals,
    next_action,DIRECTIONS,GOAL_RULES,MAX_ACTIONS,
)


def world(start=(0,0),facing=(0,1),targets=(),walls=(),radius=5):
    cells=[]
    for x in range(-radius,radius+1):
        for y in range(-radius,radius+1):
            material="grass"
            if (x,y) in walls:material="stone"
            for dest,kind in targets:
                if (x,y)==dest:material=kind
            cells.append(SeenCell((x,y),material,False,
                                  "source:local_sensor"))
    return Belief(start,facing,tuple(cells),"fixture:witnessed_tiles")


class ProbePlannerTests(unittest.TestCase):
    def test_it_generates_northward_route_not_a_script(self):
        b=world(targets=(((0,-3),"water"),))
        p=traverse(b,"game_drink_obtained")
        self.assertEqual(p.status,"PLAN_CANDIDATE")
        self.assertEqual(p.target,(0,-3))
        self.assertEqual(p.actions,
                         ("move_up","move_up","do"))

    def test_direction_rotates_with_target_and_origin(self):
        cases=[((0,3),"move_down"),((3,0),"move_right"),
               ((-3,0),"move_left"),((0,-3),"move_up")]
        for dest,first in cases:
            with self.subTest(dest=dest):
                p=traverse(world(targets=((dest,"water"),)),
                           "game_drink_obtained")
                self.assertEqual(p.actions[0],first)
                self.assertEqual(p.actions[-1],"do")
                self.assertEqual(p.target,dest)

    def test_obstacle_detour_is_inferred_from_observed_map(self):
        direct=traverse(world(targets=(((3,0),"water"),)),
                        "game_drink_obtained")
        blocked=traverse(world(
            targets=(((3,0),"water"),),
            walls=((1,0),(2,0))),
            "game_drink_obtained")
        self.assertEqual(direct.cost,3)
        self.assertEqual(blocked.status,"PLAN_CANDIDATE")
        self.assertGreater(blocked.cost,direct.cost)
        self.assertNotEqual(blocked.actions[0],"move_right")

    def test_orientation_is_part_of_state_not_an_illegal_teleport(self):
        b=world(start=(0,0),facing=(0,1),targets=(((1,0),"water"),))
        p=traverse(b,"game_drink_obtained")
        self.assertEqual(p.actions,("move_right","do"))
        self.assertEqual(p.cost,2)

    def test_already_facing_resource_goes_directly_to_interact(self):
        b=world(start=(0,0),facing=(0,-1),targets=(((0,-1),"water"),))
        p=traverse(b,"game_drink_obtained")
        self.assertEqual(p.actions,("do",))

    def test_no_observed_resource_is_hold_not_fictitious_exploration(self):
        p=traverse(world(),"game_drink_obtained")
        self.assertEqual(p.status,"HOLD_NO_OBSERVED_GOAL_RESOURCE")
        self.assertFalse(p.actions)
        self.assertIsNone(next_action(p))

    def test_blocked_goal_is_hold_not_walk_through_stone(self):
        b=world(targets=(((3,0),"water"),),
                walls=((2,0),(3,1),(3,-1),(4,0),
                       (2,1),(2,-1)))
        p=traverse(b,"game_drink_obtained")
        # A boundary path may still exist by going around the wall.
        # An actually inaccessible water tile has *all four* neighbors blocked.
        self.assertEqual(p.status,"HOLD_OBSERVED_NO_VERIFIED_PATH")
        self.assertEqual(p.actions,())

    def test_unknown_shortcut_is_not_admitted(self):
        cells=(SeenCell((0,0),"grass",False,"seen"),
               SeenCell((0,-2),"water",False,"seen"))
        b=Belief((0,0),(0,-1),cells,"only:two_seen_cells")
        p=traverse(b,"game_drink_obtained")
        self.assertEqual(p.status,"HOLD_OBSERVED_NO_VERIFIED_PATH")

    def test_sensor_object_presence_blocks_apparent_grass(self):
        cells=(SeenCell((0,0),"grass",False,"seen"),
               SeenCell((1,0),"grass",True,"seen"),
               SeenCell((2,0),"water",False,"seen"))
        b=Belief((0,0),(1,0),cells,"synthetic:obj")
        self.assertEqual(traverse(b,"game_drink_obtained").status,
                         "HOLD_OBSERVED_NO_VERIFIED_PATH")

    def test_one_cell_visibility_does_not_invent_target(self):
        b=Belief((0,0),(0,1),
                 (SeenCell((0,0),"grass",False,"seen"),),"source")
        self.assertEqual(traverse(b,"game_wood_obtained").cost,0)

    def test_independent_goal_uses_tree_not_water(self):
        b=world(targets=(((0,-3),"tree"),((1,0),"water")))
        water,wood=plans_for_goals(b,("game_drink_obtained",
                                      "game_wood_obtained"))
        self.assertEqual(water.target,(1,0))
        self.assertEqual(wood.target,(0,-3))
        self.assertEqual(water.cost,2)
        self.assertGreater(wood.cost,water.cost)

    def test_modified_observation_changes_plan_receipt_and_route(self):
        original=world(targets=(((3,0),"water"),))
        changed=world(targets=(((3,0),"water"),),
                      walls=((1,0),))
        a=traverse(original,"game_drink_obtained")
        b=traverse(changed,"game_drink_obtained")
        self.assertNotEqual(a.input_pin,b.input_pin)
        self.assertNotEqual(a.actions[0],b.actions[0])

    def test_goal_cannot_masquerade_as_real_world_materials(self):
        with self.assertRaises(ValueError):
            traverse(world(),"HUMAN_WATER")
        with self.assertRaises(ValueError):
            Belief((0,0),(0,1),world().cells,"source",
                   world="REAL_WORLD")

    def test_feedback_requires_actual_observed_resource_gain(self):
        b={"drink":3}
        a={"drink":4}
        result=check_goals(b,a,{},{},"game_drink_obtained")
        self.assertEqual(result,"WITNESSED_GAME_RESOURCE_GAIN")
        self.assertEqual(check_goals(b,b,{},{},"game_drink_obtained"),
                         "GOAL_NOT_YET_WITNESSED")

    def test_wood_achievement_can_be_witnessed_even_if_inventory_full(self):
        self.assertEqual(check_goals(
            {"wood":8},{"wood":8},{"collect_wood":0},{"collect_wood":1},
            "game_wood_obtained"),"WITNESSED_GAME_ACHIEVEMENT")

    def test_sensor_receipt_is_stable_and_order_independent(self):
        a=world(targets=(((0,-2),"water"),))
        b=replace(a,cells=tuple(reversed(a.cells)))
        self.assertEqual(a.pin,b.pin)
        self.assertEqual(traverse(a,"game_drink_obtained").actions,
                         traverse(b,"game_drink_obtained").actions)

    def test_bad_duplicate_cells_rejected(self):
        x=SeenCell((0,0),"grass",False,"fixture")
        with self.assertRaises(ValueError):
            Belief((0,0),(0,1),(x,x),"fixture")

    def test_unsafe_search_horizons_refused(self):
        with self.assertRaises(ValueError):
            traverse(world(),"game_wood_obtained",max_actions=1000)

    def test_missing_evidence_cannot_create_a_cell(self):
        with self.assertRaises(ValueError):
            SeenCell((0,0),"grass",False,"")

    def test_plans_reject_unbounded_goals(self):
        with self.assertRaises(ValueError):
            plans_for_goals(world(),("game_drink_obtained",)*9)

    def test_node_count_and_search_cost_are_bounded(self):
        p=traverse(world(targets=(((5,-5),"water"),)),
                   "game_drink_obtained")
        self.assertLessEqual(p.expanded_states,5000)
        self.assertLessEqual(p.cost,MAX_ACTIONS)

    def test_predicted_effect_is_not_automatically_verified(self):
        p=traverse(world(targets=(((0,-2),"water"),)),
                   "game_drink_obtained")
        self.assertTrue(p.predicted_but_unverified)
        self.assertFalse(p.real_world_authority)

    def test_untraversable_cell_cannot_be_approached_as_if_walkable(self):
        cells=(SeenCell((0,0),"grass",False,"witness"),
               SeenCell((0,-1),"lava",False,"witness"),
               SeenCell((0,-2),"water",False,"witness"))
        p=traverse(Belief((0,0),(0,-1),cells,"witness"),
                   "game_drink_obtained")
        self.assertEqual(p.status,"HOLD_OBSERVED_NO_VERIFIED_PATH")

if __name__=="__main__":
    unittest.main()
