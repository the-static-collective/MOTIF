"""CONTROL-FLOW-GROWTH-001: precise empirical claims and hostile controls."""
from __future__ import annotations
from dataclasses import replace
from hashlib import sha256
from itertools import combinations
from pathlib import Path
from tempfile import TemporaryDirectory
from shutil import copy2
from unittest.mock import patch
import ast
import inspect
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'mathal001'))
sys.path.insert(0,str(ROOT/'languagegrowth001'))
sys.path.insert(0,str(ROOT/'contractfrontier002'))
from nunumathal import Graph
from contractfrontier import Probe
from languagegrowth import Experiment, trials
import controlflow
from controlflow import (ControlProgram,FlowRefusal,ForEach,IfEdges,Increment,
                         tree_for,grammar,cycle_count,outcome,strong_baseline,
                         discover,diagnose,audit,pins,build_child,run_child,demonstration)


class ControlFlowGrowthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.train=trials('train',36)
        cls.validation=trials('validation',24)
        cls.test=trials('test',24)
        cls.ood=trials('ood',20)
        cls.model=discover(cls.train,cls.validation)

    def test_genuine_parent_sources_used(self):
        self.assertEqual(self.model.status,'I_EXTENDED_LOOP_AST_VALIDATED')
        self.assertTrue(all(isinstance(x.probe.graph,Graph) for x in self.train))
        self.assertEqual(self.model.program.binders,('x','y','z'))

    def test_frozen_old_grammar_is_falsified_before_growth(self):
        report=diagnose(self.train)
        self.assertEqual(report['status'],'HOLD_OLD_CONTROL_GRAMMAR_FALSIFIED')
        self.assertEqual(report['old_grammar_count'],len(controlflow.OLD_PROGRAMS))
        self.assertLessEqual(report['inspected'],12)
        self.assertEqual(report['remaining'],0)

    def test_not_supplying_target_path_law_or_prebuilt_primitive(self):
        source=inspect.getsource(controlflow.grammar)
        self.assertIn('combinations',source)
        self.assertNotIn('path_three_reference',source)
        self.assertNotIn('strong_baseline',source)
        self.assertEqual(len(grammar(3)),52)
        self.assertTrue(any(x.distinct_all for x in grammar(3)))
        self.assertTrue(any(not x.distinct_all for x in grammar(3)))

    def test_grammar_depths_have_distinct_search_spaces(self):
        self.assertEqual(tuple(len(grammar(k)) for k in (1,2,3)),(6,18,52))
        self.assertTrue(all(len(p.binders)==3 and len(p.atoms)==4 for p in grammar(3)))

    def test_recursive_wrapper_depth_not_preassembled_triple_template(self):
        plan=self.model.program.loop_tree
        self.assertIsInstance(plan,ForEach)
        self.assertIsInstance(plan.body,ForEach)
        self.assertIsInstance(plan.body.body,ForEach)
        self.assertIsInstance(plan.body.body.body,IfEdges)
        self.assertIsInstance(plan.body.body.body.body,Increment)
        self.assertEqual([plan.binder,plan.body.binder,plan.body.body.binder],['x','y','z'])
        tree=tree_for(('x','y'),(('a','x'),('b','y'),('x','y')),True)
        self.assertIsInstance(tree.body.body,IfEdges)

    def test_emitted_python_has_three_actual_nested_loops(self):
        code=self.model.program.emit_source()
        parsed=ast.parse(code)
        fn=parsed.body[0]
        outer=next(n for n in fn.body if isinstance(n,ast.For))
        inner=outer.body[0]
        third=inner.body[0]
        self.assertTrue(all(isinstance(x,ast.For) for x in (outer,inner,third)))
        self.assertIsInstance(third.body[0],ast.If)
        self.assertNotIn('eval(',code)
        self.assertNotIn('import ',code)
        self.assertNotIn('exec(',code)

    def test_ast_interpreter_matches_emitted_python(self):
        namespace={}
        exec(self.model.program.emit_source(),namespace)
        child=namespace['discovered_operation']
        for case in self.test[:12]:
            p=case.probe
            self.assertEqual(child(p.graph,p.a,p.b),self.model.program.interpret(p))

    def test_five_cycle_instrument_matches_separate_dfs_algorithm(self):
        for case in self.test+self.ood:
            self.assertEqual(outcome(case),strong_baseline(case.probe))

    def test_complete_k5_add_edge_creates_six_five_cycles(self):
        edges=[pair for pair in combinations('abcde',2) if pair!=('a','b')]
        p=Probe('test:k5',Graph.build('abcde',edges),'a','b','test')
        c=Experiment('test:k5',p,'test')
        self.assertEqual(outcome(c),6)
        self.assertEqual(self.model.program.interpret(p),6)

    def test_long_path_new_edge_creates_one_five_cycle(self):
        g=Graph.build('abcde',[('a','c'),('c','d'),('d','e'),('e','b')])
        p=Probe('test:path5',g,'a','b','test')
        self.assertEqual(self.model.program.interpret(p),1)
        self.assertEqual(outcome(Experiment(p.key,p,'test')),1)

    def test_shorter_path_does_not_create_five_cycle(self):
        g=Graph.build('abcde',[('a','c'),('c','b')])
        p=Probe('test:short',g,'a','b','test')
        self.assertEqual(self.model.program.interpret(p),0)

    def test_repeated_vertices_are_not_allowed_in_simple_cycle(self):
        g=Graph.build('abcde',[('a','c'),('c','d'),('d','e'),('e','b'),('c','e')])
        p=Probe('test:partial',g,'a','b','test')
        self.assertEqual(self.model.program.interpret(p),outcome(Experiment(p.key,p,'test')))

    def test_active_training_reaches_finite_validated_ast(self):
        self.assertEqual(self.model.probes,3)
        self.assertEqual(self.model.remaining,1)
        self.assertEqual(self.model.total_candidates,52)
        self.assertEqual(self.model.program.distinct_all,True)

    def test_distinct_validation_unseen_graphs(self):
        result=audit(self.model,self.test)
        self.assertEqual(result['status'],'F_LOCAL_FINITE_REPLAY')
        self.assertEqual(result['AST_correct'],24)
        self.assertEqual(result['emitted_code_correct'],24)
        self.assertEqual(result['strong_classical_correct'],24)

    def test_larger_ood_graphs_all_match(self):
        result=audit(self.model,self.ood)
        self.assertEqual(result['cases'],20)
        self.assertEqual(result['AST_correct'],20)
        self.assertEqual(result['strong_classical_correct'],20)

    def test_depth_ablation_reports_hold(self):
        result=discover(self.train,self.validation,max_depth=2)
        self.assertEqual(result.status,'HOLD_MAX_LOOP_DEPTH_BELOW_NEEDED')
        self.assertIsNone(result.program)

    def test_undistinguished_repeated_walks_not_accepted(self):
        result=discover(self.train,self.validation,allow_distinct=False)
        self.assertFalse(result.usable)
        self.assertIn(result.status,{'HOLD_NO_COMPOSABLE_PROGRAM','HOLD_VALIDATION_COUNTEREXAMPLE'})

    def test_few_probes_fail_closed(self):
        with self.assertRaises(FlowRefusal):discover(self.train,self.validation,budget=2)

    def test_source_splits_are_disjoint(self):
        self.assertFalse({e.key for e in self.train}&{e.key for e in self.validation})
        self.assertFalse({e.key for e in self.test}&{e.key for e in self.ood})
        with self.assertRaises(FlowRefusal):discover(self.train,self.train)

    def test_source_result_does_not_use_heldout_in_discover_signature(self):
        sig=inspect.signature(discover)
        self.assertNotIn('test',sig.parameters)
        self.assertNotIn('ood',sig.parameters)

    def test_bad_budget_or_foreign_goal_refused(self):
        for kwargs in ({'budget':100}, {'max_depth':4}, {'budget':True},
                       {'max_depth':True}, {'allow_distinct':1}, {'selection':'oracle'}):
            with self.subTest(kwargs=kwargs),self.assertRaises(FlowRefusal):
                discover(self.train,self.validation,**kwargs)

    def test_typo_graph_outcome_preserves_hold_on_validation(self):
        original=controlflow.outcome
        def corrupted(case):
            return original(case)+(1 if case.split=='validation' else 0)
        with patch.object(controlflow,'outcome',side_effect=corrupted):
            result=discover(self.train,self.validation)
        self.assertEqual(result.status,'HOLD_VALIDATION_COUNTEREXAMPLE')
        self.assertIsNone(result.program)

    def test_ranking_uses_only_unlabeled_graph_probes_before_oracle(self):
        original=controlflow.outcome
        seen=[]
        def tracked(case):
            seen.append(case.key)
            return original(case)
        with patch.object(controlflow,'outcome',side_effect=tracked):
            d=discover(self.train,self.validation)
        selected=[r['case'] for r in d.receipts if r.get('action')=='RUN_SYNTHETIC_INTERVENTION']
        self.assertEqual(seen[:10],[r['probe'] for r in diagnose(self.train)['receipts']])
        self.assertEqual(seen[10:10+len(selected)],selected)
        self.assertEqual(len(selected),3)

    def test_original_graph_not_mutated(self):
        before=self.test[0].probe.graph
        audit(self.model,self.test[:1])
        self.assertEqual(before,self.test[0].probe.graph)

    def test_relabeling_preserves_operation(self):
        p=self.test[2].probe
        rename={v:'other:'+v for v in p.graph.vertices}
        g=Graph.build(rename.values(),[(rename[a],rename[b]) for a,b in p.graph.edges])
        copied=Probe('test:relabeled',g,rename[p.a],rename[p.b],'test')
        self.assertEqual(self.model.program.interpret(copied),self.model.program.interpret(p))

    def test_forged_discovery_cannot_build_child(self):
        counterfeit=replace(self.model,program=grammar(3)[0])
        with TemporaryDirectory() as folder,self.assertRaises(FlowRefusal):
            build_child(ROOT,Path(folder),counterfeit)

    def test_child_generated_and_verified_as_separate_interpreter(self):
        with TemporaryDirectory() as folder:
            path=build_child(ROOT,Path(folder),self.model)
            result=run_child(path,ROOT,index=4)
            self.assertEqual(result['status'],'F_LOCAL_CHILD_REPLAY')
            self.assertEqual(result['external_actions'],0)
            self.assertEqual(result['original_source_edits'],0)
            self.assertEqual(result['observed'],result['computed'])

    def test_generated_child_cannot_overwrite(self):
        with TemporaryDirectory() as folder:
            build_child(ROOT,Path(folder),self.model)
            with self.assertRaises(FileExistsError):build_child(ROOT,Path(folder),self.model)

    def test_child_tamper_fails_closed(self):
        with TemporaryDirectory() as folder:
            path=build_child(ROOT,Path(folder),self.model)
            path.write_text(path.read_text()+'\n# tamper')
            self.assertEqual(run_child(path,ROOT)['status'],'HOLD_MISSING_OR_TAMPERED_CHILD')

    def test_bad_index_child_holds(self):
        with TemporaryDirectory() as folder:
            child=build_child(ROOT,Path(folder),self.model)
            self.assertEqual(run_child(child,ROOT,-1)['status'],'HOLD_INVALID_TEST_INDEX')

    def test_source_pin_detects_modification(self):
        with TemporaryDirectory() as folder:
            child=build_child(ROOT,Path(folder)/'child',self.model)
            copy=Path(folder)/'copy'
            for relative,_ in pins(ROOT):
                target=copy/relative
                target.parent.mkdir(parents=True,exist_ok=True)
                copy2(ROOT/relative,target)
            (copy/'operatorinvention001'/'operatorinvention.py').write_text('# corrupted')
            self.assertEqual(run_child(child,copy)['status'],'HOLD_SOURCE_DRIFT')

    def test_symlink_sources_refused(self):
        with TemporaryDirectory() as folder:
            root=Path(folder)
            for relative,_ in pins(ROOT):
                target=root/relative;target.parent.mkdir(parents=True,exist_ok=True)
                copy2(ROOT/relative,target)
            victim=root/'controlflow001'/'controlflow.py'
            victim.unlink();victim.symlink_to(ROOT/'controlflow001'/'controlflow.py')
            with self.assertRaises(FlowRefusal):pins(root)

    def test_invalid_ast_and_foreign_control_rejected(self):
        good=self.model.program
        with self.assertRaises(FlowRefusal):ControlProgram(('z',),good.atoms[:2],False)
        with self.assertRaises(FlowRefusal):ControlProgram(('x','y','z'),(('a','x'),)*4,False)
        with self.assertRaises(FlowRefusal):grammar(0)
        with self.assertRaises(FlowRefusal):grammar(4)

    def test_canonical_alpha_equivalence_is_not_claimed_novel_operator(self):
        model=self.model.program
        self.assertEqual(controlflow._canonical(model.atoms,model.binders),model.atoms)
        self.assertFalse(audit(self.model,self.test)['unrestricted_algorithm_claim'])

    def test_results_are_reproducible_under_fixed_probe_fixtures(self):
        self.assertEqual(self.model,discover(self.train,self.validation))

    def test_demo_identifies_honest_next_question(self):
        r=demonstration()
        self.assertEqual(r['child']['status'],'F_LOCAL_CHILD_REPLAY')
        self.assertIn('computation need',r['next_question'])
        self.assertFalse(r['historical_novelty_claim'])
        self.assertEqual(r['real_world_actions'],0)


if __name__=='__main__':
    unittest.main()
