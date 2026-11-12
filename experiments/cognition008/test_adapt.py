"""COGNITION-008 action grammar falsifiers using invented source-only inputs.

These tests do NOT replace original-game testing in CI.
"""
import ast
from pathlib import Path
import unittest
from unittest.mock import patch

from adapt import proposer,native_motif_hypothetical_programs,public_free_graph_hypothesis

BASE=["collect","craft_gadget","approach_workbench","select_old_item",
      "place","nop","give_up"]


def observation(count=1):
    return {"inventory":{"slots":[{"item":"unfamiliar_thing","count":count}],
                         "selectedItem":"old_item"},
            "failedAction":"craft_gadget","player":{"pos":[3,3],"facing":"north"},
            "map":{"3,4":"workbench"}}


class RecoveryGrammarTests(unittest.TestCase):
    def test_new_affordance_is_from_allowed_actions_not_hidden_truth(self):
        names=BASE+["select_unfamiliar_thing"]
        prefix=[{"action":"approach_workbench","success":True},
                {"action":"craft_gadget","success":False}]
        candidates=proposer(names,BASE,observation(),prefix)
        self.assertTrue(candidates)
        self.assertEqual(candidates[0]["actions"],
                         ["select_unfamiliar_thing","collect","craft_gadget"])
        self.assertTrue(all(c["status"]=="PENCIL_UNTESTED" for c in candidates))
        self.assertTrue(all(set(c["actions"]).issubset(names) for c in candidates))

    def test_absent_inventory_blocks_direct_select(self):
        names=BASE+["select_unfamiliar_thing"]
        candidates=proposer(names,BASE,observation(0),[
            {"action":"craft_gadget","success":False}])
        self.assertEqual(candidates,[])

    def test_no_novel_action_no_adaptation_victory_invented(self):
        candidates=proposer(BASE,BASE,observation(),[
            {"action":"craft_gadget","success":False}])
        self.assertEqual(candidates,[])

    def test_missing_original_failed_action_refuses(self):
        d=observation()
        d["failedAction"]="inaccessible_action"
        self.assertEqual(proposer(BASE+["select_unfamiliar_thing"],BASE,d,[]),[])

    def test_new_object_collection_program_does_not_need_inventory_advance(self):
        names=BASE+["approach_unfamiliar_thing","select_unfamiliar_thing"]
        candidates=proposer(names,BASE,observation(0),[
            {"action":"approach_workbench","success":True},
            {"action":"craft_gadget","success":False}])
        self.assertTrue(candidates)
        a=[c["actions"] for c in candidates]
        self.assertIn(["approach_unfamiliar_thing","collect",
                       "select_unfamiliar_thing","approach_workbench",
                       "collect","craft_gadget"],a)

    def test_observed_evidence_grammar_not_hardcoded_to_specific_novelty(self):
        source=Path(__file__).with_name("adapt.py").read_text()
        # Grammar is domain neutral. The task label may be hardcoded in the
        # outer benchmark harness, but the proposer must not be.
        tree=ast.parse(source)
        fun=next(n for n in tree.body if isinstance(n,ast.FunctionDef)
                 and n.name=="proposer")
        strings=[x.value for x in ast.walk(fun) if isinstance(x,ast.Constant)
                 and isinstance(x.value,str)]
        body=" ".join(strings).lower()
        for prohibited in ("bucket","fire","water","on_fire","pogo_stick"):
            self.assertNotIn(prohibited,body)

    def test_real_native_motif003_research_option_count(self):
        names=BASE+["select_unfamiliar_thing"]
        options=proposer(names,BASE,observation(),[
            {"action":"craft_gadget","success":False}])
        self.assertEqual(native_motif_hypothetical_programs(options),len(options))
        self.assertEqual(native_motif_hypothetical_programs([]),0)

    def test_original_free_graph_hypothesis_native_validation(self):
        names=BASE+["select_unfamiliar_thing"]
        history=[{"action":"craft_gadget","success":False}]
        proposal=proposer(names,BASE,observation(),history)[0]
        graph=public_free_graph_hypothesis(history,observation(),proposal)
        self.assertTrue(graph["native_validated"])
        self.assertEqual(graph["unresolved_links"],2)
        self.assertFalse(graph["owner_admission"])


if __name__=="__main__":
    unittest.main()
