"""Adversarial tests for graph-edit induction, source-event binding and authority."""
from __future__ import annotations

import ast
from copy import deepcopy
from pathlib import Path
import unittest

import world,induce,search


class RelationGraphTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.training=world.generate("train",seed=2026111001,repeats=6)
        cls.program=induce.construct(cls.training,min_support=3,
                                     max_cue=2,max_gap=12,purity=0.9)

    def test_source_minimal_pairs_are_distinct_graphs_same_event(self):
        world.check(self.training,split="train")
        self.assertEqual(len(self.training["pairs"]),60)
        for pair in self.training["pairs"]:
            self.assertEqual(pair["a"]["observed_event"],
                             pair["b"]["observed_event"])
            self.assertNotEqual(pair["a"]["semantic_graph"],
                                pair["b"]["semantic_graph"])

    def test_graph_delta_operator_is_derived_not_wired_to_phrase(self):
        a=world.graph(("DIRECTIVE","ROOT","POS"))
        b=world.graph(("MENTION","QUOTED","POS"))
        changes=induce.differences(a,b)
        self.assertEqual(len(changes),2)
        self.assertTrue(all(x["opcode"]=="REPLACE_TYPED_EDGE"
                            for x in changes))
        self.assertEqual({x["source"][1] for x in changes},
                         {"FORCE","SCOPE"})
        self.assertGreater(self.program["derived_transition_count"],3)
        self.assertGreater(self.program["derived_cue_count"],4)

    def test_event_bindings_abstract_instead_of_memorizing_names(self):
        ctx={"speaker":"mara","agent":"sol","verb":"carry","patient":"parcel"}
        out=induce.abstract("Mara asks Sol to carry parcel",ctx)
        self.assertEqual(out,["<speaker>","asks","<agent>","to",
                              "<verb>","<patient>"])
        new={"speaker":"zevi","agent":"lynx","verb":"unfurl","patient":"kite"}
        self.assertEqual(induce.abstract("zevi asks lynx to unfurl kite",new),out)

    def test_unknown_source_entities_do_not_get_silently_invented(self):
        ctx={"speaker":"mara","agent":"sol","verb":"carry","patient":"parcel"}
        for text in ("carry parcel", "purple elbow of the spoon",
                     "mara asks someone to carry parcel",
                     "mara describes the event without saying the word carry twice carry"):
            got=induce.parse(self.program,text,ctx)
            self.assertEqual(got["status"],"HOLD")

    def test_source_hypotheses_have_no_effect_authority(self):
        ctx={"speaker":"mara","agent":"sol","verb":"carry","patient":"parcel"}
        for text in ("mara asks sol to carry parcel",
                     "mara says sol did not carry parcel",
                     "mara quotes sol saying carry parcel"):
            result=induce.parse(self.program,text,ctx)
            self.assertIn(result["status"],(
                "HOLD","NONAUTHORITATIVE_TYPED_GRAPH_HYPOTHESIS"))
            if result["semantic_graph"] is not None:
                self.assertEqual(result["external_action_authority"],"NONE")
                self.assertEqual(len(result["semantic_graph"]["edges"]),3)

    def test_changed_but_rehashed_program_cannot_add_new_executable_opcode(self):
        p=deepcopy(self.program)
        p["source_derived_contextual_cue_operators"][0]["opcode"]="EXECUTE_SHELL"
        p["receipt_sha256"]=world.digest({
            k:v for k,v in p.items() if k!="receipt_sha256"})
        with self.assertRaisesRegex(induce.HOLD,"Unapproved"):
            induce.validate(p)

    def test_undeclared_semantic_relation_is_refused(self):
        p=deepcopy(self.program)
        p["source_derived_transition_operator_instances"][0]["relation"]="PRIVATE_FILES"
        p["receipt_sha256"]=world.digest({
            k:v for k,v in p.items() if k!="receipt_sha256"})
        with self.assertRaisesRegex(induce.HOLD,"Unreviewed"):
            induce.validate(p)

    def test_program_selector_has_no_holdout_import(self):
        sources=(Path(search.__file__).read_text(),
                 Path(induce.__file__).read_text())
        modules=[]
        for source in sources:
            for node in ast.walk(ast.parse(source)):
                if isinstance(node,ast.Import):
                    modules.extend(a.name for a in node.names)
                elif isinstance(node,ast.ImportFrom):
                    modules.append(node.module)
        self.assertNotIn("novel",modules)
        self.assertNotIn("benchmark",modules)

    def test_weird_or_invented_language_is_uncertain_without_event_evidence(self):
        ctx={"speaker":"mara","agent":"sol","verb":"carry","patient":"parcel"}
        nonsense=(
            "does the pebble of thunder want its own name",
            "unfurl the sideways clocks of our unfamiliar drift",
            "an orbit in the cup folds the room on itself",
            "smashon lol the lattice forgot its speaker",
        )
        for phrase in nonsense:
            self.assertIsNone(induce.parse(self.program,phrase,ctx)[
                "semantic_graph"])

    def test_real_world_graph_knowledge_not_inferred_from_synthetic_labels(self):
        self.assertTrue(self.program["observed_event_context_required"])
        self.assertTrue(self.program["speaker_agent_action_patient_not_inferred_from_free_text"])
        self.assertFalse(self.program["new_base_computational_primitive_invented"])
        self.assertEqual(self.program["execution_authority"],"NONE")


if __name__=="__main__":
    unittest.main()
