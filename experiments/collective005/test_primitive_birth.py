"""COLLECTIVE-005: missing-primitive formation, original data, fair classical."""
from __future__ import annotations
from copy import deepcopy
import json
import os
import sys
import unittest
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
sys.path.insert(0,str(HERE.parent/"collective004"))
sys.path.insert(0,str(HERE.parent/"collective003"))

from primitive_birth import (
    HOLD, GRAMMAR, emit_ast, generate_python, execute_generated,
    independent_permutation_count, networkx_reference,
    old_question_fingerprint, invent_question, classical_fair_reference,
    SimulatedAtlasSourceOwner, research_packet, verify_packet, reenter,
    digest, _typecheck,
)
from external_atlas import source_module,carrier,ATLAS_DATA_SHA256
from national_treasure_frontier import build_node,verify_node
from atlas_trial import run,original_source_proof


class PrimitiveBirthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root=Path(os.environ["ATLAS_ROOT"]).resolve()
        cls.cases=Path(os.environ["NT_CASE_ROOT"]).resolve()
        cls.box=Path(os.environ["NT_BOX_ROOT"]).resolve()
        cls.module=source_module(cls.root)
        cls.train,cls.heldout,cls.protocol=cls.module.cohort()
        cls.provenance=original_source_proof(cls.module,cls.protocol)
        cls.nt=build_node("same-state-different-world",cls.cases,cls.box)
        verify_node(cls.nt,cls.cases,cls.box)
        cls.report=run(cls.root,cls.cases,cls.box)

        cls.train_failed=[t for t in cls.train if
            old_question_fingerprint(tuple(carrier(g) for g in t.graphs))[
                "previous_two_question_grammars_saturated"
            ]]
        cls.test_failed=[t for t in cls.heldout if
            old_question_fingerprint(tuple(carrier(g) for g in t.graphs))[
                "previous_two_question_grammars_saturated"
            ]]

    def test_external_source_bytes_and_train_heldout_are_distinct(self):
        self.assertEqual(self.protocol["atlas_data_sha256"],ATLAS_DATA_SHA256)
        self.assertTrue(self.protocol["original_carrier_authorship_independent_of_MOTIF"])
        self.assertEqual((len(self.train),len(self.heldout)),(14,28))
        self.assertEqual(len(self.train_failed),1)
        self.assertEqual(len(self.test_failed),2)
        self.assertEqual(tuple(self.train_failed[0].atlas_ids),(769,770))
        self.assertEqual({tuple(x.atlas_ids) for x in self.test_failed},
                         {(482,483),(552,553)})

    def test_both_prior_question_languages_provably_insufficient(self):
        for task in self.train_failed+self.test_failed:
            worlds=tuple(carrier(g) for g in task.graphs)
            result=old_question_fingerprint(worlds)
            self.assertEqual(result["old_measurements"][0],
                             result["old_measurements"][1])
            self.assertEqual(result["degree_pair_existence_signatures"][0],
                             result["degree_pair_existence_signatures"][1])
            self.assertTrue(result["previous_two_question_grammars_saturated"])

    def test_raw_atoms_gradually_build_new_question_not_prelisted_path4(self):
        self.assertNotIn("PATH4",GRAMMAR["base_atoms"])
        self.assertNotIn("DEGREE_PAIR",GRAMMAR["base_atoms"])
        self.assertEqual(GRAMMAR["base_atoms"],
                         ["BIND_VERTEX","ADJACENT","ALL_DISTINCT","COUNT"])
        self.assertFalse(GRAMMAR["unrestricted_primitive_invention"])
        ast=emit_ast(4)
        self.assertEqual(ast["bind_vertices"],
                         ["v0","v1","v2","v3","v4"])
        self.assertEqual(ast["adjacency_constraints"],
                         [["v0","v1"],["v1","v2"],["v2","v3"],["v3","v4"]])
        src=generate_python(ast)
        self.assertIn("for v4 in range(n):",src)
        self.assertEqual(src.count("for v"),5)
        self.assertNotIn("nx.",src)
        self.assertNotIn("degree",src)

    def test_training_seeks_minimal_new_primitive_with_failed_attempts(self):
        worlds=tuple(carrier(g) for g in self.train_failed[0].graphs)
        attempt=invent_question(worlds,max_edges=3)
        self.assertEqual(attempt["status"],
                         "HOLD_NO_SEPARATING_COMPOSITION_WITHIN_BUDGET")
        self.assertEqual([x["depth"] for x in attempt["search_history"]],[1,2,3])
        self.assertTrue(all(not x["separates"]
                            for x in attempt["search_history"]))
        success=invent_question(worlds)
        self.assertEqual(success["status"],
                         "COMPOSED_NEW_QUESTION_PRIMITIVE_REVIEW_ONLY")
        self.assertEqual(len(success["search_history"]),4)
        self.assertEqual(success["selected_ast"],emit_ast(4))
        self.assertEqual(success["selected_predictions"],[76,73])
        self.assertEqual(classical_fair_reference(worlds),emit_ast(4))

    def test_frozen_new_primitive_resolves_both_external_heldout_holds(self):
        self.assertEqual(self.report["heldout"]["all_pairs"],28)
        self.assertEqual(self.report["heldout"]["previously_resolved"],26)
        self.assertEqual(self.report["heldout"]["previously_unsolved"],2)
        self.assertEqual(self.report["heldout"]["frozen_new_primitive_newly_resolved"],2)
        self.assertEqual(self.report["heldout"]["honest_holds"],0)
        self.assertEqual(self.report["heldout"]["realized_world_observations_correct"],4)
        self.assertEqual(self.report["heldout"]["new_source_owner_calls"],4)
        self.assertEqual(self.report["heldout"]["classical_same_grammar_ties"],2)
        self.assertEqual(self.report["training_generated_ast"],emit_ast(4))
        self.assertTrue(self.report["question_ast_frozen_before_any_heldout_evaluation"])
        predictions={tuple(x["pair_ids"]):x["source_counts_by_candidate"]
                     for x in self.report["heldout_pair_records"]
                     if x["status"]=="FROZEN_COMPOSED_PRIMITIVE_SEPARATES"}
        self.assertEqual(predictions,{(482,483):[25,22],(552,553):[21,18]})

    def test_three_separate_methods_agree_on_unseen_heldout(self):
        ast=self.report["training_generated_ast"]
        for task in self.test_failed:
            worlds=tuple(carrier(g) for g in task.graphs)
            for g in worlds:
                a=execute_generated(ast,g)
                self.assertEqual(a,independent_permutation_count(ast,g))
                self.assertEqual(a,networkx_reference(ast,g))
            self.assertEqual(classical_fair_reference(worlds),ast)

    def test_original_nat_question_remains_unanswered(self):
        self.assertTrue(verify_node(self.nt,self.cases,self.box))
        self.assertEqual(self.nt["world_claim_verified"],False)
        self.assertNotIn("answer",self.nt["original_question_receipt"])
        self.assertTrue(self.report["source_NT_mystery_remains_unanswered"])
        self.assertFalse(self.report["automatic_admission"])

    def test_new_source_observation_contains_proof_and_reentries_without_questions(self):
        task=self.test_failed[0]
        worlds=tuple(carrier(g) for g in task.graphs)
        owner=SimulatedAtlasSourceOwner(worlds[0],list(task.atlas_ids))
        packet=research_packet(self.nt,worlds,owner,
                               source_atlas_proof=self.provenance)
        self.assertEqual(packet["new_program_ast"],emit_ast(4))
        self.assertEqual(packet["source_questions_asked"],1)
        self.assertEqual(packet["remaining_possible_world_indices"],[0])
        self.assertTrue(verify_packet(packet,self.nt,owner,
                                      source_atlas_proof=self.provenance))
        first_count=owner.questions
        recovered=reenter(json.loads(json.dumps(packet)),self.nt,owner,
                          source_atlas_proof=self.provenance)
        self.assertEqual(recovered["new_discovery_questions"],0)
        self.assertEqual(owner.questions,first_count)

    def test_rehashed_forged_external_source_observation_fail_closed(self):
        task=self.test_failed[0]
        worlds=tuple(carrier(g) for g in task.graphs)
        owner=SimulatedAtlasSourceOwner(worlds[0],list(task.atlas_ids))
        packet=research_packet(self.nt,worlds,owner,
                               source_atlas_proof=self.provenance)
        bad=deepcopy(packet)
        bad["source_owned_observation"]["measured_count"]+=1
        bad["source_owned_observation"]["integrity_digest"]=digest({
            k:v for k,v in bad["source_owned_observation"].items()
            if k!="integrity_digest"
        })
        bad["integrity_digest"]=digest({
            k:v for k,v in bad.items() if k!="integrity_digest"
        })
        with self.assertRaises(HOLD):
            verify_packet(bad,self.nt,owner,source_atlas_proof=self.provenance)

    def test_owner_revision_invalidates_reentry(self):
        task=self.test_failed[0]
        worlds=tuple(carrier(g) for g in task.graphs)
        old=SimulatedAtlasSourceOwner(worlds[0],list(task.atlas_ids),revision=1)
        packet=research_packet(self.nt,worlds,old,
                               source_atlas_proof=self.provenance)
        new=SimulatedAtlasSourceOwner(worlds[0],list(task.atlas_ids),revision=2)
        with self.assertRaises(HOLD):
            reenter(packet,self.nt,new,source_atlas_proof=self.provenance)

    def test_no_new_claim_without_source_and_unavailable_grammar(self):
        task=self.test_failed[0]
        worlds=tuple(carrier(g) for g in task.graphs)
        source=SimulatedAtlasSourceOwner(worlds[0],list(task.atlas_ids))
        declined=research_packet(self.nt,worlds,source,
                                 source_atlas_proof=self.provenance,
                                 max_edges=3)
        self.assertIn("HOLD_",declined["status"])
        self.assertEqual(declined["source_questions_asked"],0)
        self.assertEqual(source.questions,0)
        with self.assertRaises(HOLD):
            emit_ast(0)
        with self.assertRaises(HOLD):
            emit_ast(5)
        invalid=deepcopy(emit_ast(4))
        invalid["adjacency_constraints"][0]=["v0","v3"]
        with self.assertRaises(HOLD):
            _typecheck(invalid)

    def test_not_changing_grammar_after_unseen_data(self):
        self.assertTrue(self.report["question_ast_frozen_before_any_heldout_evaluation"])
        self.assertTrue(self.report["raw_graph_primitives_and_search_bounds_human_authored"])
        self.assertTrue(self.report["new_math_or_unrestricted_program_invention_not_established"])
        self.assertTrue(self.report["source_owner_is_local_simulated_not_real_independent_agent"])
        self.assertTrue(self.report["original_atlas_authorship_independent_but_experiment_not_blinded"])
        self.assertEqual(self.report["external_authority"],"NONE")


if __name__=="__main__":
    unittest.main()
