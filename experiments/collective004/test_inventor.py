"""COLLECTIVE-004 adversarial proof and question-language growth tests."""
from __future__ import annotations
import copy
import json
import sys
import unittest
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
sys.path.insert(0,str(HERE.parent/"collective003"))
from question_inventor import (
    HOLD, AST_SCHEMA, base_worlds, extended_worlds, graph, degrees,
    old_measurements, candidate_programs, find_missing_question, emit_program,
    execute, independent_execute, classical_exhaustive_reference,
    SyntheticWorldOwner, investigate, verify_packet, reenter, permute_world,
    digest, run,
)
from national_treasure_frontier import verify_node, build_node


class InventNewQuestionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import os
        cls.case_root=Path(os.environ["NT_CASE_ROOT"]).resolve()
        cls.box_root=Path(os.environ["NT_BOX_ROOT"]).resolve()
        cls.nt=build_node("same-state-different-world",
                          cls.case_root,cls.box_root)
        verify_node(cls.nt,cls.case_root,cls.box_root)
        cls.worlds=base_worlds()
        cls.old=find_missing_question(cls.worlds,enable_extension=False)
        cls.new=find_missing_question(cls.worlds)
        cls.owner=SyntheticWorldOwner(cls.worlds[1],
                                       identifier="fixture:owner-B")
        cls.packet=investigate(cls.nt,cls.worlds,cls.owner)

    def test_actual_national_treasure_source_is_question_not_proof(self):
        self.assertTrue(verify_node(self.nt,self.case_root,self.box_root))
        self.assertNotIn("answer",self.nt["original_question_receipt"])
        self.assertIn("HOLD_",self.nt["motif_task_relevance_critic"]["status"])
        self.assertFalse(self.nt["world_claim_verified"])

    def test_old_menu_makes_both_worlds_strictly_indistinguishable(self):
        a,b=self.worlds
        self.assertNotEqual(a,b)
        self.assertEqual(degrees(a).count(2),2)
        self.assertEqual(sorted(degrees(a)),sorted(degrees(b)))
        self.assertEqual(old_measurements(a),old_measurements(b))
        self.assertEqual(self.old["status"],"HOLD_NO_ALLOWED_NEW_QUESTION")
        self.assertEqual(self.old["generated_candidates"],0)

    def test_expand_synthesizes_instead_of_handpick_from_old_menu(self):
        q=self.new
        self.assertEqual(q["status"],"QUESTION_GRAMMAR_EXPANDED_REVIEW_ONLY")
        self.assertEqual(q["generated_candidates"],6)
        self.assertEqual(len(q["catalog"]),6)
        self.assertEqual(q["selected_signatures"],[False,True])
        self.assertEqual(q["selected_program"],emit_program(2,2))
        self.assertTrue(q["new_question_from_composed_primitives"])
        self.assertTrue(q["old_language_saturated"])
        self.assertFalse(q["arbitrary_open_ended_grammar_invention"])

    def test_no_target_world_truth_used_in_question_synthesis(self):
        q=self.new
        self.assertIn("quantifier",q["selected_program"])
        self.assertEqual(q["selected_program"]["quantifier"],"EXISTS")
        self.assertEqual(q["selected_program"]["edge"],["u","v"])
        self.assertEqual(self.owner.questions_asked,1)
        swapped=find_missing_question(self.worlds[::-1])
        self.assertEqual(swapped["selected_program"],q["selected_program"])
        self.assertEqual(swapped["selected_signatures"],[True,False])

    def test_strong_classical_exhaustive_control_ties(self):
        classical=classical_exhaustive_reference(self.worlds)
        self.assertEqual(classical,self.new["selected_program"])
        self.assertEqual(execute(classical,self.worlds[0]),False)
        self.assertEqual(independent_execute(classical,self.worlds[1]),True)

    def test_carries_completely_real_source_observation_receipt(self):
        p=self.packet
        self.assertEqual(p["status"],"SCOPED_SYNTHETIC_WORLD_IDENTIFIED")
        self.assertEqual(p["remaining_possible_world_indices"],[1])
        self.assertEqual(p["source_owner_observation"]["typed_question_ast"],
                         p["invented_question"]["typed_program"])
        self.assertTrue(p["source_owner_observation"]["observed_boolean"])
        self.assertTrue(verify_packet(p,self.nt,self.owner))
        self.assertFalse(p["original_NT_question_unanswered_in_external_world"] is False)
        self.assertFalse(p["automatic_admission"])

    def test_saved_reentry_rechecks_without_new_owner_question(self):
        old_count=self.owner.questions_asked
        before=self.owner.rechecks
        receipt=reenter(json.loads(json.dumps(self.packet)),self.nt,self.owner)
        self.assertEqual(receipt["new_discovery_questions"],0)
        self.assertEqual(self.owner.questions_asked,old_count)
        self.assertGreater(self.owner.rechecks,before)
        self.assertEqual(receipt["answer_node"],self.packet)

    def test_source_owner_revision_revokes_previous_packet(self):
        changed=SyntheticWorldOwner(self.worlds[1],
                            identifier="fixture:owner-B",revision=2)
        with self.assertRaises(HOLD):
            reenter(self.packet,self.nt,changed)

    def test_rehashed_forged_observation_rejected_by_owner(self):
        p=copy.deepcopy(self.packet)
        p["source_owner_observation"]["observed_boolean"]=False
        p["source_owner_observation"]["integrity_digest"]=digest({
            k:v for k,v in p["source_owner_observation"].items()
            if k!="integrity_digest"})
        p["integrity_digest"]=digest({k:v for k,v in p.items()
                                       if k!="integrity_digest"})
        with self.assertRaises(HOLD):
            verify_packet(p,self.nt,self.owner)

    def test_rehashed_fake_invented_question_refused(self):
        p=copy.deepcopy(self.packet)
        p["invented_question"]["text"]="Are time machines proven real?"
        p["integrity_digest"]=digest({k:v for k,v in p.items()
                                       if k!="integrity_digest"})
        with self.assertRaises(HOLD):
            verify_packet(p,self.nt,self.owner)

    def test_invalid_or_missing_grammar_refuses_to_hallucinate(self):
        a,b=self.worlds
        self.assertEqual(find_missing_question((a,b),enable_extension=False)["status"],
                         "HOLD_NO_ALLOWED_NEW_QUESTION")
        with self.assertRaises(HOLD):
            execute({"schema":AST_SCHEMA,"quantifier":"EXISTS",
                    "edge":["u","v"],"endpoints":[]},a)
        with self.assertRaises(HOLD):
            emit_program(9,9)
        with self.assertRaises(HOLD):
            graph(6,[(0,1),(0,1)])

    def test_previous_menu_not_used_when_it_already_separates(self):
        a,_=self.worlds
        other=graph(6,[(0,1),(1,2),(2,3),(3,4),(4,5)])
        self.assertNotEqual(old_measurements(a),old_measurements(other))
        res=find_missing_question((a,other))
        self.assertEqual(res["status"],"HOLD_OLD_GRAMMAR_ALREADY_DISTINGUISHES")

    def test_generalizes_to_larger_manually_authored_fixture(self):
        a7,b7=extended_worlds()
        self.assertEqual(old_measurements(a7),old_measurements(b7))
        q=self.new["selected_program"]
        self.assertEqual([execute(q,g) for g in (a7,b7)],[False,True])
        self.assertEqual([independent_execute(q,g) for g in (a7,b7)],
                         [False,True])

    def test_1440_complete_relabelings_preserve_answer(self):
        from itertools import permutations
        selected=self.new["selected_program"]
        count=0
        for perm in permutations(range(6)):
            for idx,g in enumerate(self.worlds):
                translated=permute_world(g,perm)
                observed=execute(selected,translated)
                self.assertEqual(observed,self.new["selected_signatures"][idx])
                self.assertEqual(observed,independent_execute(selected,translated))
                count+=1
        self.assertEqual(count,1440)

    def test_frozen_full_benchmark_returns_structured_evidence(self):
        result=run(self.nt)
        self.assertEqual(result["first_grammar_status"],
                         "HOLD_NO_ALLOWED_NEW_QUESTION")
        self.assertTrue(result["classical_exhaustive_exact_tie"])
        self.assertEqual(result["heldout_vertex_relabeling_checks"],1440)
        self.assertEqual(result["larger_seven_node_invented_question_predictions"],
                         [False,True])
        self.assertEqual(result["reentry_new_source_questions"],0)
        self.assertFalse(result["world_claims_not_proven"] is False)


if __name__=="__main__":
    unittest.main()
