"""QC-004: anti-overclaim and source-integrity tests."""
import unittest
from dataclasses import replace

from gardener import (
    ATOMS, UNARY, BINARY, STATUS, MAX_AST_COST, Expr, grammar,
    relation, query, fixtures, discover, review, Garden, apply, replay,
    oracle_semantics, evaluator_graph, oracle_edit, evaluate, all_edges,
    infer_delta, labelled, separate, Graph, edge, equivalent_new, report,
    graft_from_library, apply_grafted,
)


class GrammarGardenerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = {}
        for task in ("alternate_path", "triangle", "square"):
            train, valid, test = fixtures(task)
            candidate = discover(train)
            certified = review(candidate, train, valid)
            cls.cases[task] = (train, valid, test, candidate, certified)

    def test_frozen_data_splits(self):
        for task, (train, valid, test, _, _) in self.cases.items():
            self.assertEqual((len(train),len(valid),len(test)),(6,4,8),task)
            self.assertEqual(len({r.evidence_id for r in train+valid+test}),18)

    def test_synthetic_episodes_have_no_action_cue_or_anchor(self):
        for train, valid, test, _, _ in self.cases.values():
            for r in train+valid+test:
                self.assertFalse(hasattr(r,"signal"))
                self.assertFalse(hasattr(r,"anchors"))
                self.assertFalse(hasattr(r,"action"))

    def test_grammar_is_generated_not_three_named_canned_templates(self):
        candidates=list(grammar(5))
        self.assertGreater(len(candidates),100)
        self.assertEqual({e.op for e in candidates if e.cost==1},set(ATOMS))
        self.assertTrue(any(x.op=="JOIN" and x.cost==5 for x in candidates))
        self.assertTrue(any(x.op=="TC" for x in candidates))
        self.assertTrue(all(x.well_typed() for x in candidates))

    def test_three_different_programs_are_found(self):
        programs=[x[3].program.code() for x in self.cases.values()]
        self.assertEqual(len(set(programs)),3)
        self.assertEqual(self.cases["alternate_path"][3].program.cost,2)
        self.assertEqual(self.cases["triangle"][3].program.cost,3)
        self.assertEqual(self.cases["square"][3].program.cost,5)

    def test_separate_feature_family_cost_ablation(self):
        for task, (train,_,_, candidate,_) in self.cases.items():
            limit=candidate.program.cost-1
            self.assertIsNone(discover(train,limit),task)

    def test_opposite_effects_per_identical_graph(self):
        for train, valid, test, _, _ in self.cases.values():
            for group in (train,valid,test):
                for i in range(0,len(group),2):
                    self.assertEqual(group[i].before,group[i+1].before)
                    self.assertNotEqual(infer_delta(group[i])[1],
                                        infer_delta(group[i+1])[1])

    def test_two_fresh_vertices_inferred_not_handed_as_actions(self):
        for train, _, _, _, _ in self.cases.values():
            for row in train:
                boundary, effect=infer_delta(row)
                self.assertEqual(len(boundary),2)
                self.assertEqual(effect.new_roles,2)

    def test_all_heldout_examples_correct_and_separately_validated(self):
        for task,(train,valid,test,candidate,model) in self.cases.items():
            self.assertIsNotNone(model,task)
            self.assertEqual(model.validation_count,4)
            self.assertEqual(evaluate(task,model,test),
                             {"total":8,"covered":8,"correct":8,"held":0,"wrong":0})

    def test_all_edges_not_just_targeted_examples(self):
        for task,(_,_,test,_,model) in self.cases.items():
            graphs=tuple(test[i].before for i in range(0,len(test),2))
            results=all_edges(task,model,graphs)
            self.assertEqual(len(results),4)
            for measured in results:
                self.assertEqual(measured["edges"],measured["correct"])

    def test_independent_oracle_is_not_learned_ast(self):
        for task,(_,_,test,_,model) in self.cases.items():
            graph=test[-1].before
            for target in graph.edges:
                result=apply(graph,target,model)
                self.assertIsNotNone(result)
                truth=oracle_edit(task,graph,target,"source_truth")
                self.assertTrue(equivalent_new(graph,truth,result.graph))

    def test_relabeling_invariance(self):
        for task,(_,_,_,_,model) in self.cases.items():
            graph, targets=evaluator_graph(task,f"fresh_{task}",34,
                                          chord=True,extra_tail=True)
            renaming={v:"opaque_"+v for v in graph.vertices}
            relocated=Graph.of(renaming.values(),
                               [(renaming[a],renaming[b]) for a,b in graph.edges])
            for a,b in targets:
                self.assertEqual(query(model.proposal.program,graph,(a,b)),
                                 query(model.proposal.program,relocated,
                                       (renaming[a],renaming[b])))

    def test_bridging_false_positive_is_not_a_triangle(self):
        graph,_=evaluator_graph("triangle","false_triangle",28)
        triangle_prog=self.cases["triangle"][4].proposal.program
        for target in graph.edges:
            self.assertEqual(query(triangle_prog,graph,target),
                             oracle_semantics("triangle",graph,target))

    def test_square_is_not_merely_generic_reachability(self):
        graph,targets=evaluator_graph("square","false_short",24)
        reach=self.cases["alternate_path"][4].proposal.program
        square=self.cases["square"][4].proposal.program
        self.assertTrue(query(reach,graph,targets[0]))
        self.assertTrue(query(reach,graph,targets[1]))
        self.assertTrue(query(square,graph,targets[0]))
        self.assertFalse(query(square,graph,targets[1]))

    def test_no_square_pattern_with_too_small_grammar(self):
        train,*_=fixtures("square")
        self.assertIsNone(discover(train,4))

    def test_individual_queries_do_not_reveal_hidden_actor_choice(self):
        for task,(_,_,test,_,model) in self.cases.items():
            graph=test[0].before
            self.assertGreater(len(graph.edges),10)
            # Several possible counterfactuals; no selection as actual act.
            possibilities=[apply(graph,e,model) for e in graph.edges]
            self.assertEqual(len(possibilities),len(graph.edges))
            self.assertTrue(all(x is not None for x in possibilities))

    def test_source_pinned_prediction_replays_exactly(self):
        for task,(_,_,test,_,model) in self.cases.items():
            row=test[0]
            target,_=infer_delta(row)
            outcome=apply(row.before,target,model)
            self.assertEqual(replay(row.before,outcome,model),outcome)

    def test_forged_prediction_is_refused(self):
        row=self.cases["triangle"][2][0]
        model=self.cases["triangle"][4]
        target,_=infer_delta(row)
        result=apply(row.before,target,model)
        forged=replace(result,evidence=replace(result.evidence,outcome="fake"))
        self.assertIsNone(replay(row.before,forged,model))

    def test_revoked_validation_signature_is_refused(self):
        row=self.cases["square"][2][0]
        model=self.cases["square"][4]
        target,_=infer_delta(row)
        result=apply(row.before,target,model)
        unpinned=replace(model,validation_hash="withdrawn")
        self.assertIsNone(replay(row.before,result,unpinned))

    def test_unauthorized_status_is_never_admitted(self):
        row=self.cases["triangle"][2][0]
        model=self.cases["triangle"][4]
        target,_=infer_delta(row)
        with self.assertRaises(ValueError):
            apply(row.before,target,replace(model,status="INSTALLED"))

    def test_fabricated_candidate_ast_is_refused(self):
        train,valid,_,candidate,_=self.cases["triangle"]
        other=self.cases["square"][3]
        fake=replace(candidate,program=other.program)
        with self.assertRaises(ValueError):
            review(fake,train,valid)

    def test_fabricated_evidence_hash_is_refused(self):
        train,valid,_,candidate,_=self.cases["triangle"]
        with self.assertRaises(ValueError):
            review(replace(candidate,evidence_hash="fake"),train,valid)

    def test_wrong_training_split_rejected(self):
        _, valid, _,_,_=self.cases["triangle"]
        with self.assertRaises(ValueError):
            discover(valid)

    def test_forged_provenance_rejected(self):
        train,*_=self.cases["triangle"]
        forged=replace(train[0],provenance="REAL_WITNESS")
        with self.assertRaises(ValueError):
            discover((forged,)+train[1:])

    def test_duplicate_evidence_rejected(self):
        train,*_=self.cases["triangle"]
        with self.assertRaises(ValueError):
            discover(train+(train[0],))

    def test_validation_overlap_rejected(self):
        train,valid,_,candidate,_=self.cases["triangle"]
        forged=replace(valid[0],evidence_id=train[0].evidence_id)
        with self.assertRaises(ValueError):
            review(candidate,train,(forged,)+valid[1:])

    def test_contradicted_validation_holds(self):
        train,valid,_,candidate,_=self.cases["triangle"]
        modified=(replace(valid[0],after=valid[1].after),)+valid[1:]
        self.assertIsNone(review(candidate,train,modified))

    def test_proposed_but_unvalidated_feature_not_usable(self):
        _,_,test,candidate,_=self.cases["triangle"]
        edge0=next(iter(test[0].before.edges))
        self.assertIsNone(apply(test[0].before,edge0,None))
        with self.assertRaises(Exception):
            apply(test[0].before,edge0,candidate)

    def test_outside_type_or_cost_ast_rejected(self):
        graph,_=evaluator_graph("triangle","invalid",26)
        target=next(iter(graph.edges))
        with self.assertRaises(ValueError):
            query(Expr("EXEC",Expr("E")),graph,target)
        with self.assertRaises(ValueError):
            query(Expr("JOIN",Expr("E")),graph,target)

    def test_garden_keeps_three_explicit_task_cartridges(self):
        garden=Garden()
        for task,(train,valid,test,_,model) in self.cases.items():
            garden=garden.keep(task,model,train,valid)
        self.assertEqual(len(garden.entries),3)
        self.assertIsNone(garden.use("unknown",self.cases["square"][2][0].before,
                                     next(iter(self.cases["square"][2][0].before.edges))))
        with self.assertRaises(ValueError):
            garden.keep("triangle",self.cases["triangle"][4],
                        self.cases["triangle"][0],self.cases["triangle"][1])
        with self.assertRaises(ValueError):
            garden.keep("fake",self.cases["triangle"][3],
                        self.cases["triangle"][0],self.cases["triangle"][1])

    def test_garden_is_not_mutated_by_retention(self):
        first=Garden()
        second=first.keep("triangle",self.cases["triangle"][4],
                          self.cases["triangle"][0],self.cases["triangle"][1])
        self.assertEqual(first.entries,())
        self.assertEqual(len(second.entries),1)

    def test_forged_reviewed_envelope_cannot_enter_garden(self):
        train, valid, _, _, certified=self.cases["triangle"]
        bad=replace(certified,validation_hash="spoofed")
        with self.assertRaises(ValueError):
            Garden().keep("triangle",bad,train,valid)
        bad2=replace(certified,proposal=replace(certified.proposal,evidence_hash="spoofed"))
        with self.assertRaises(ValueError):
            Garden().keep("triangle",bad2,train,valid)

    def test_prior_feature_is_reused_to_construct_another_program(self):
        ttrain,tvalid,_,_,donor=self.cases["triangle"]
        strain,svalid,stest,_,_=self.cases["square"]
        garden=Garden().keep("triangle",donor,ttrain,tvalid)
        graft=graft_from_library(garden,"triangle","square-from-triangle",
                                 strain,svalid)
        self.assertIsNotNone(graft)
        self.assertIn(donor.proposal.program.code(),graft.program.code())
        self.assertEqual(graft.program.cost,5)
        count=0
        for row in stest:
            target,_=infer_delta(row)
            result=apply_grafted(graft,donor,row.before,target)
            self.assertIsNotNone(result)
            count+=int(equivalent_new(row.before,row.after,result.graph))
        self.assertEqual(count,8)

    def test_library_graft_refuses_revoked_or_tampered_parent(self):
        ttrain,tvalid,_,_,donor=self.cases["triangle"]
        strain,svalid,stest,_,_=self.cases["square"]
        garden=Garden().keep("triangle",donor,ttrain,tvalid)
        graft=graft_from_library(garden,"triangle","square",strain,svalid)
        row=stest[0]
        target,_=infer_delta(row)
        self.assertIsNone(apply_grafted(graft,replace(donor,validation_hash="gone"),
                                         row.before,target))
        self.assertIsNone(apply_grafted(replace(graft,status="INSTALLED"),donor,
                                         row.before,target))
        self.assertIsNone(graft_from_library(Garden(),"triangle","square",strain,svalid))

    def test_grafted_feature_validation_does_not_tune_second_candidate(self):
        ttrain,tvalid,_,_,donor=self.cases["triangle"]
        strain,svalid,_,_,_=self.cases["square"]
        garden=Garden().keep("triangle",donor,ttrain,tvalid)
        fake_valid=(replace(svalid[0],after=svalid[1].after),)+svalid[1:]
        self.assertIsNone(graft_from_library(garden,"triangle","square",
                                              strain,fake_valid))

    def test_report_does_not_claim_compounding_or_quantum(self):
        x=report()
        self.assertEqual(x["reviewed_question_cartridges"],3)
        self.assertEqual(x["external_actions"],0)
        self.assertFalse(x["quantum_execution"])
        self.assertFalse(x["produced_executable_source"])
        self.assertTrue(all(r["reviewed"] for r in x["task_outcomes"].values()))
        self.assertTrue(x["task_outcomes"]["square"]["graft_from_triangle"]["validated"])
        self.assertEqual(x["task_outcomes"]["square"]["graft_from_triangle"]["heldout_correct"],8)


if __name__=="__main__":
    unittest.main()
