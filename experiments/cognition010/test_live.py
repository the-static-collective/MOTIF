"""COGNITION-010 source-only live learning/control falsifiers."""
import ast
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import unittest

from live import (TransitionMemory, programs_for_failure, public_signature,
                  safe_actions, MAX_ATTEMPTS, MAX_RECOVERY, POLICIES,run_case)


def sensor(selected="tree_tap",counts=None):
    if counts is None:counts={"axe":1}
    return {"inventory":{"selectedItem":selected,
            "slots":[{"item":k,"count":v} for k,v in counts.items()]},
            "player":{"pos":["3","9"],"facing":"north"}}


class LiveTests(unittest.TestCase):
    def test_prior_failed_action_remains_a_research_target(self):
        allowed=["select_axe","select_tree_tap","break_block","collect",
                 "move_forward","rotate_right","approach_oak_log","nop","give_up"]
        old=[x for x in allowed if x!="select_axe"]
        choices=programs_for_failure(allowed,old,sensor(),
                 "break_block",[])
        self.assertIn(["select_axe","break_block"],[x["actions"] for x in choices])
        self.assertTrue(all(x["actions"][-1]=="break_block" for x in choices))
        self.assertTrue(all(x["status"]=="PENCIL_UNVERIFIED" for x in choices))

    def test_can_investigate_obstacle_and_continue_task(self):
        names=["approach_fence","approach_oak_log","break_block","collect",
               "move_forward","move_left","move_right","nop"]
        candidate=programs_for_failure(names,[n for n in names if n!="approach_fence"],
                     sensor(counts={}),"approach_oak_log",[])
        self.assertIn(["approach_fence","break_block","approach_oak_log"],
                      [x["actions"] for x in candidate])

    def test_no_novel_action_names_still_has_active_retests(self):
        names=["approach_entity_103","trade_block","move_forward","move_backward",
               "move_left","move_right","rotate_left","rotate_right"]
        hypotheses=programs_for_failure(names,names,sensor(counts={}),"trade_block",
                     [{"action":"approach_entity_103","native_action_success":True}])
        self.assertTrue(hypotheses)
        self.assertIn(["move_forward","trade_block"],[x["actions"] for x in hypotheses])
        self.assertTrue(any(x["kind"]=="expanded-novel-motion-sequence"
                            for x in hypotheses))

    def test_no_give_up_or_nop_hypothesis(self):
        options=programs_for_failure(
             ["give_up","nop","move_forward","trade_block"],[],
             sensor(counts={}),"trade_block",[])
        self.assertTrue(options)
        self.assertTrue(all("give_up" not in x["actions"] and
                            "nop" not in x["actions"] for x in options))

    def test_separate_evaluator_bits_are_not_remembered(self):
        memory=TransitionMemory()
        x={"action":"break_block","native_action_success":True,
           "visible_inventory_delta":{"oak_log":1},
           "selected_item_before":"axe",
           "owner_goal":True,"owner_given_up":False}
        memory.observe(x,"break_block")
        self.assertNotIn("owner_goal",memory.actions[0])
        self.assertNotIn("owner_given_up",memory.actions[0])
        self.assertEqual(memory.summary()["source_bound_receipts"],1)
        self.assertEqual(memory.by_transition[("break_block","break_block","axe")]["passes"],1)
        self.assertEqual(memory.by_transition[("break_block","break_block","axe")]["inventory_effects"]["oak_log"],1)

    def test_memory_carries_program_attempts_across_resets(self):
        m=TransitionMemory()
        p={"actions":["select_axe","break_block"]}
        self.assertTrue(m.untried("break_block",p))
        m.tried("break_block",p)
        self.assertFalse(m.untried("break_block",p))
        self.assertEqual(m.summary()["tested_programs"],1)

    def test_goal_only_external_owner_and_recovery_not_local_repair(self):
        source=Path(__file__).with_name("live.py").read_text()
        self.assertIn('if chosen==blocked:',source)
        self.assertIn('in_resume=True',source)
        self.assertIn('main.stuck=False',source)
        self.assertIn('source_bound_model',source)
        self.assertIn('all_remaining_attempts_spent_if_unsolved',source)

    def test_unresolved_live_failure_consumes_all_ten_attempts(self):
        """A pure fake outcome source checks scheduler, NOT game competence."""
        class FakeEnv:
            agent_selection="agent_0"
            terminations={"agent_0":False}
            truncations={"agent_0":False}
            internal_state=SimpleNamespace(_goal_achieved=False,_given_up=False)
            def close(self):pass
        fake_actions=["craft_widget","move_forward","move_backward",
                      "move_left","move_right","rotate_left","rotate_right"]
        view=sensor(counts={})
        def step(env,name,mode,iteration,attempt,memory,failed):
            row={"action":name,"native_action_success":False,
                 "native_message":"synthetic stubborn failure",
                 "selected_item_before":"tree_tap",
                 "selected_item_after":"tree_tap",
                 "visible_inventory_delta":{},
                 "public_position_after":["3","9"]}
            memory.observe(row,failed)
            return row,view,False,False
        with patch("live.make",side_effect=lambda *_:FakeEnv()),\
             patch("live.main_actions",return_value=fake_actions),\
             patch("live.original_prefix",return_value=[
                {"action":"craft_widget","success":False,
                 "message":"independently mocked failure"}]),\
             patch("live.public_observe",return_value=view),\
             patch("live.execute_native_step",side_effect=step):
            actual=run_case("axe","classical_live")
        self.assertFalse(actual["native_owner_goal"])
        self.assertEqual(actual["attempts_used"],10)
        self.assertEqual(actual["total_post_failure_actions"],10*80)
        self.assertEqual(actual["stop_reason"],"ATTEMPT_RECOVERY_BUDGET_EXHAUSTED")
        self.assertTrue(actual["all_remaining_attempts_spent_if_unsolved"])
        self.assertTrue(all(x["post_failure_actions"]==80 for x in actual["attempts"]))

    def test_budgets_and_equal_baseline_controllers(self):
        self.assertEqual(MAX_ATTEMPTS,10)
        self.assertEqual(MAX_RECOVERY,80)
        self.assertEqual(set(POLICIES),{"classical_live","motif_live"})
        tree=ast.parse(Path(__file__).with_name("live.py").read_text())
        fn=next(x for x in tree.body if isinstance(x,ast.FunctionDef)
                and x.name=="programs_for_failure")
        text=" ".join(x.value for x in ast.walk(fn)
                     if isinstance(x,ast.Constant) and isinstance(x.value,str)).lower()
        for prohibited in ("water_bucket","fence_easy","on_fire","pogo_stick","dist_trade"):
            self.assertNotIn(prohibited,text)


if __name__=="__main__":
    unittest.main()
