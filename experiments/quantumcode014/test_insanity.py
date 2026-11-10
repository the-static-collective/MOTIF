"""QC-014: falsify 'repeat => insanity' with task-specific feedback."""
import unittest
from dataclasses import replace
from insanity import (
    Snapshot,Observation,StagnationGuard,assess,diagnose_craft,
    inspect_qc011_replay,PROGRESS,NO_PROGRESS,UNRESOLVED,
)
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"quantumcode011"))
from game_replay import Episode,GameState,Replay


def snap(step,wood=1,pick=0,pos=(5,5),facing=(1,0),
         health=9,drink=8,achievements=()):
    return Snapshot(
        tuple(sorted((("wood",wood),("wood_pickaxe",pick),
                      ("health",health),("drink",drink)))),
        tuple(achievements),pos,facing,step)


def event(step,action="make_wood_pickaxe",before=None,after=None):
    return Observation(action,before or snap(step),
                       after or snap(step+1),
                       "synthetic:test-step-%d"%step)


class InsanityMonitorTests(unittest.TestCase):
    def test_three_identical_failed_crafts_trigger_once(self):
        guard=StagnationGuard(3)
        result=[guard.observe(event(i)) for i in range(6)]
        self.assertIsNone(result[0])
        self.assertIsNone(result[1])
        self.assertEqual(result[2].failures,3)
        self.assertTrue(guard.should_hold("make_wood_pickaxe"))
        self.assertEqual(sum(x is not None for x in result),1)

    def test_survival_drain_does_not_count_as_crafting_progress(self):
        x=event(0,before=snap(0,health=9,drink=8),
                after=snap(1,health=8,drink=7))
        y=assess(x)
        self.assertEqual(y.verdict,NO_PROGRESS)
        self.assertEqual(y.effect_basis,"CRAFT_OUTPUT_OR_ACHIEVEMENT")

    def test_actual_crafted_item_is_progress(self):
        x=event(0,after=snap(1,pick=1,wood=0))
        self.assertEqual(assess(x).verdict,PROGRESS)

    def test_craft_achievement_is_progress_even_with_zero_item_delta(self):
        x=event(0,after=snap(1,achievements=(
            "achievement:make_wood_pickaxe",)))
        self.assertEqual(assess(x).verdict,PROGRESS)

    def test_progress_resets_failed_consecutive_counter(self):
        guard=StagnationGuard(3)
        guard.observe(event(0))
        guard.observe(event(1,after=snap(2,pick=1)))
        self.assertIsNone(guard.observe(event(2)))
        self.assertEqual(guard.failed_counts["make_wood_pickaxe"],1)

    def test_two_failed_attempts_do_not_trigger(self):
        guard=StagnationGuard(3)
        for i in range(2):self.assertIsNone(guard.observe(event(i)))
        self.assertFalse(guard.held)

    def test_successful_move_with_new_position_is_not_an_infinite_loop(self):
        guard=StagnationGuard(3)
        for i in range(30):
            x=event(i,"move_right",
                    snap(i,pos=(i,2)),snap(i+1,pos=(i+1,2)))
            self.assertIsNone(guard.observe(x))
        self.assertFalse(guard.alerts)

    def test_orientation_without_movement_is_valid_progress(self):
        g=StagnationGuard(3)
        x=event(0,"move_up",
                snap(0,facing=(1,0)),snap(1,facing=(0,-1)))
        self.assertEqual(assess(x).verdict,PROGRESS)
        self.assertIsNone(g.observe(x))

    def test_unknown_facing_is_not_construed_as_failed_movement(self):
        x=event(0,"move_right",
                snap(0,facing=None),snap(1,facing=None))
        self.assertEqual(assess(x).verdict,UNRESOLVED)

    def test_three_blocked_moves_with_unchanged_facing_trigger(self):
        g=StagnationGuard(3)
        for i in range(3):
            result=g.observe(event(i,"move_right",snap(i),snap(i+1)))
        self.assertIsNotNone(result)
        self.assertEqual(result.action,"move_right")

    def test_combat_mechanics_hidden_by_inventory_are_unresolved(self):
        g=StagnationGuard(3)
        for i in range(20):
            alert=g.observe(event(i,"do"))
            self.assertIsNone(alert)
        self.assertFalse(g.held)
        self.assertEqual(g.ignored_unresolved,20)

    def test_rest_with_delayed_effect_is_not_false_stall(self):
        g=StagnationGuard(3)
        for i in range(12):
            self.assertIsNone(g.observe(event(i,"sleep")))
        self.assertFalse(g.held)

    def test_do_with_actual_inventory_gain_is_progress(self):
        x=event(0,"do",snap(0,wood=1),snap(1,wood=2))
        self.assertEqual(assess(x).verdict,PROGRESS)

    def test_undefined_game_actions_not_called_repeated_failure(self):
        g=StagnationGuard(3)
        for i in range(9):
            self.assertIsNone(g.observe(event(i,"unknown_action")))
        self.assertEqual(g.ignored_unresolved,9)

    def test_intervening_meaningful_probe_breaks_consecutive_failure(self):
        g=StagnationGuard(3)
        g.observe(event(0))
        g.observe(event(1,"move_right",
                        snap(1,pos=(4,4)),snap(2,pos=(5,4))))
        self.assertIsNone(g.observe(event(2)))
        self.assertEqual(g.failed_counts["make_wood_pickaxe"],1)

    def test_an_unresolved_intervening_action_breaks_sequence(self):
        g=StagnationGuard(3)
        g.observe(event(0))
        g.observe(event(1,"do"))
        self.assertIsNone(g.observe(event(2)))
        self.assertEqual(g.failed_counts["make_wood_pickaxe"],1)

    def test_loop_holds_no_outbound_effects(self):
        g=StagnationGuard(3)
        for i in range(3):out=g.observe(event(i))
        self.assertFalse(out.actual_cause_confirmed)
        self.assertEqual(out.status,"STOP_RETRY_AND_INSPECT")
        self.assertIn("required resource",out.proposed_next_question)

    def test_cannot_unblock_action_without_new_observation(self):
        g=StagnationGuard(3)
        for i in range(3):g.observe(event(i))
        with self.assertRaises(ValueError):
            g.release_after_new_evidence("make_wood_pickaxe","")
        self.assertTrue(g.should_hold("make_wood_pickaxe"))

    def test_sourced_new_evidence_may_reopen_a_craft_probe(self):
        g=StagnationGuard(3)
        for i in range(3):g.observe(event(i))
        g.release_after_new_evidence("make_wood_pickaxe",
                                     "crafter-game-table-observed")
        self.assertFalse(g.should_hold("make_wood_pickaxe"))
        self.assertIsNone(g.observe(event(4)))

    def test_known_recipe_identifies_absent_nearby_table(self):
        d=diagnose_craft(
            "make_wood_pickaxe",{"wood":1},{"table":False},
            {"uses":{"wood":1},"nearby":["table"]})
        self.assertEqual(d.missing_utilities,("table",))
        self.assertEqual(d.explanation,"MISSING_NEARBY_CRAFTING_UTILITY")
        self.assertFalse(d.current_action_allowed)

    def test_material_shortage_has_priority_over_utility(self):
        d=diagnose_craft(
            "make_wood_pickaxe",{"wood":0},{"table":False},
            {"uses":{"wood":1},"nearby":["table"]})
        self.assertEqual(d.explanation,"MISSING_GAME_RECIPE_INPUT")
        self.assertEqual(d.missing_resources,(("wood",1),))

    def test_unknown_material_not_invented(self):
        d=diagnose_craft(
            "make_wood_pickaxe",{"wood":1},{"table":None},
            {"uses":{"wood":1},"nearby":["table"]})
        self.assertEqual(d.unknown_utilities,("table",))
        self.assertEqual(d.explanation,"CANNOT_VERIFY_REQUIRED_NEARBY_UTILITY")

    def test_fully_satisfied_preconditions_require_deeper_probe(self):
        d=diagnose_craft(
            "make_wood_pickaxe",{"wood":1},{"table":True},
            {"uses":{"wood":1},"nearby":["table"]})
        self.assertEqual(d.explanation,
                         "PRECONDITIONS_APPEAR_MET__INVESTIGATE_OTHER_CAUSE")
        self.assertEqual(d.automatic_external_effects,0)

    def test_recipe_lacks_source_is_rejected(self):
        with self.assertRaises(ValueError):
            diagnose_craft("make_wood_pickaxe",{}, {},None)

    def test_other_domain_route_not_grafted_to_crafting(self):
        with self.assertRaises(ValueError):
            diagnose_craft("walk_somewhere",{}, {},
                           {"uses":{},"nearby":[]})

    def test_bad_threshold_config_rejected(self):
        with self.assertRaises(ValueError):
            StagnationGuard(threshold=1)
        with self.assertRaises(ValueError):
            StagnationGuard(threshold=50)

    def test_time_broken_event_rejected(self):
        with self.assertRaises(ValueError):
            Observation("make_wood_pickaxe",snap(3),snap(2),"fixture")

    def test_without_evidence_event_rejected(self):
        with self.assertRaises(ValueError):
            Observation("make_wood_pickaxe",snap(1),snap(2),"")

    def test_a_snapshot_cannot_have_duplicate_inventory_keys(self):
        with self.assertRaises(ValueError):
            Snapshot((("wood",1),("wood",2)),(),(0,0),step=0)

    def test_actual_qc011_shape_can_be_audited_without_running_the_game(self):
        def state(t):
            return GameState(
                (("wood",1),("wood_pickaxe",0),("health",9)),(),
                (),"GAME_TILE:5,5",t)
        eps=tuple(Episode(
            "synthetic:"+str(i),"OTHER_GAME","SYNTHETIC_FIXTURE",
            "fixture:repeated-craft","SYNTHETIC",i,i+1,
            "make_wood_pickaxe",state(i),state(i+1),
            "INCONCLUSIVE","synthetic repeated attempt","OBSERVED",
            ("SYNTHETIC_GAME",)) for i in range(161))
        replay=Replay("OTHER_GAME",eps,"synthetic-replay",True)
        replay.validate()
        audit=inspect_qc011_replay(replay.episodes)
        self.assertEqual(audit["audited_steps"],161)
        self.assertEqual(len(audit["alerts"]),1)
        self.assertEqual(audit["alerts"][0]["step"],3)
        self.assertEqual(audit["effectful_actions"],0)

    def test_a_replay_without_facing_does_not_diagnose_walking(self):
        def state(t,x):
            return GameState((("wood",1),),(),(),
                             "GAME_TILE:%d,4"%x,t)
        eps=[]
        for i in range(15):
            eps.append(Episode(
                "walk:"+str(i),"OTHER_GAME","SYNTHETIC_FIXTURE",
                "fixture:walking","SYNTHETIC",i,i+1,
                "move_right",state(i,i),state(i+1,i+1),
                "SUCCESS","move in game","OBSERVED",("SYNTHETIC_GAME",)))
        audit=inspect_qc011_replay(eps)
        self.assertEqual(len(audit["alerts"]),0)


if __name__=="__main__":
    unittest.main()
