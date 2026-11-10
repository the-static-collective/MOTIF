"""Adversarial contracts for bounded source-code synthesis from graph behavior."""
from __future__ import annotations

from dataclasses import replace
from hashlib import sha256
from pathlib import Path
from shutil import copy2
from tempfile import TemporaryDirectory
from unittest.mock import patch
import ast
import inspect
import json
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'languagegrowth001'))
from languagegrowth import trials, path_three_reference, diagnose
from operatorinvention import (Program,OperatorRefusal,grammar,PROGRAMS,EDGE_ATOMS,
    discover,heldout,target,build_child,run_child,pins,demonstration)


class OperatorInventionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.train=trials('train',36)
        cls.validation=trials('validation',24)
        cls.test=trials('test',30)
        cls.ood=trials('ood',25)
        cls.four=discover(cls.train,cls.validation)
        cls.triangle=discover(cls.train,cls.validation,task='triangles')

    def test_old_grammar_failure_is_observed_not_assumed(self):
        diagnosis=diagnose(self.train)
        self.assertEqual(diagnosis['status'],'HOLD_FINITE_GRAMMAR_FALSIFIED')
        self.assertLessEqual(diagnosis['inspections'],8)

    def test_finite_grammar_is_generated_from_typed_primitives(self):
        self.assertGreater(len(PROGRAMS),20)
        self.assertLess(len(PROGRAMS),100)
        self.assertEqual(len(EDGE_ATOMS),6)
        self.assertTrue(all(isinstance(p,Program) for p in PROGRAMS))
        self.assertFalse(any('COUNT_XY' in p.name() for p in PROGRAMS))

    def test_actual_two_loop_program_discovered(self):
        p=self.four.program
        self.assertEqual(self.four.status,'I_EXECUTABLE_OPERATOR_VALIDATED')
        self.assertEqual(p.binders,('x','y'))
        self.assertEqual(set(p.atoms),{('a','x'),('b','y'),('x','y')})
        self.assertFalse(p.distinct)

    def test_second_task_discovers_distinct_simpler_loop(self):
        p=self.triangle.program
        self.assertEqual(self.triangle.status,'I_EXECUTABLE_OPERATOR_VALIDATED')
        self.assertEqual(p.binders,('x',))
        self.assertEqual(set(p.atoms),{('a','x'),('b','x')})
        self.assertNotEqual(p,self.four.program)

    def test_second_task_replays_ood_worlds(self):
        result=heldout(self.triangle,self.ood)
        self.assertEqual(result['matched'],len(self.ood))
        self.assertEqual(result['status'],'F_LOCAL_FINITE_REPLAY')

    def test_active_selection_uses_three_interventions(self):
        self.assertEqual(self.four.interventions,3)
        self.assertEqual(len([e for e in self.four.receipts if e.get('operation')=='EXECUTE_OBSERVED_GRAPH_PROBE']),3)

    def test_hidden_test_and_ood_not_present_in_learning_api(self):
        arguments=inspect.signature(discover).parameters
        self.assertNotIn('test',arguments)
        self.assertNotIn('ood',arguments)
        self.assertFalse({e.key for e in self.train}&{e.key for e in self.ood})

    def test_no_outcome_peeking_before_intervention_choice(self):
        import operatorinvention as module
        observed=[]
        original=module.target
        def record(event,task):
            observed.append(event.key)
            return original(event,task)
        with patch.object(module,'target',side_effect=record):
            d=discover(self.train,self.validation,budget=3)
        sampled=[r['probe'] for r in d.receipts if r.get('operation')=='EXECUTE_OBSERVED_GRAPH_PROBE']
        self.assertEqual(observed[:len(sampled)],sampled)
        self.assertFalse({e.key for e in self.validation}&set(observed[:len(sampled)]))

    def test_validation_is_frozen_no_retune(self):
        import operatorinvention as module
        original=module.target
        modified={e.key for e in self.validation}
        def corrupt(e,task):
            return original(e,task)+(1 if e.key in modified else 0)
        with patch.object(module,'target',side_effect=corrupt):
            d=discover(self.train,self.validation)
        self.assertEqual(d.status,'HOLD_VALIDATION_COUNTEREXAMPLE')
        self.assertIsNone(d.program)

    def test_thirty_hidden_cases(self):
        r=heldout(self.four,self.test)
        self.assertEqual((r['matched'],r['cases']),(30,30))
        self.assertEqual(r['strong_baseline_matches'],30)

    def test_larger_worlds_are_heldout(self):
        r=heldout(self.four,self.ood)
        self.assertEqual((r['matched'],r['cases']),(25,25))
        self.assertTrue(any(len(e.probe.graph.vertices)>12 for e in self.ood))

    def test_source_implementation_matches_classical_reference(self):
        for e in self.test+self.ood:
            self.assertEqual(self.four.program.interpret(e.probe),
                             path_three_reference(e.probe.graph,e.probe.a,e.probe.b))

    def test_compiler_emits_parseable_natural_python(self):
        source=self.four.program.emit_source()
        self.assertIn('for x in vertices:',source)
        self.assertIn('for y in vertices:',source)
        self.assertIn('count += 1',source)
        self.assertNotIn('eval(',source)
        self.assertNotIn('path_three_reference',source)
        self.assertNotIn('COUNT_XY',source)
        self.assertIsInstance(ast.parse(source),ast.Module)

    def test_generated_python_and_interpreter_agree_on_unseen_worlds(self):
        namespace={}
        exec(self.four.program.emit_source(),namespace)
        for e in self.test[:12]+self.ood[:12]:
            g=e.probe.graph
            self.assertEqual(namespace['constructed_operator'](g,e.probe.a,e.probe.b),
                             self.four.program.interpret(e.probe))

    def test_compiled_triangle_operator_matches_interpreter(self):
        namespace={}
        exec(self.triangle.program.emit_source(),namespace)
        for e in self.test[:10]:
            p=e.probe
            self.assertEqual(namespace['constructed_operator'](p.graph,p.a,p.b),
                             self.triangle.program.interpret(p))

    def test_no_two_binder_language_abstains(self):
        d=discover(self.train,self.validation,candidates=grammar(allow_two_binders=False))
        self.assertFalse(d.usable)
        self.assertIn('HOLD',d.status)

    def test_short_budget_cannot_forge_unique_claim(self):
        d=discover(self.train,self.validation,budget=1)
        self.assertFalse(d.usable)
        self.assertIn('HOLD',d.status)

    def test_wrong_oracle_has_no_explanation(self):
        import operatorinvention as module
        original=module.target
        def wrong(e,task):
            # Large offset is not representable by 3 atomic edge predicates.
            return original(e,task)+101
        with patch.object(module,'target',side_effect=wrong):
            result=discover(self.train,self.validation,budget=4)
        self.assertEqual(result.status,'HOLD_NO_PROGRAM_FITS_EVIDENCE')

    def test_illformed_programs_are_refused(self):
        invalid=[
            (('z',),(('a','x'),),False),
            (('x',),(('a','y'),),False),
            (('x',),(),False),
            (('x',),(('a','x'),('a','x')),False),
            (('x',),(('x','a'),),False),
            (('x',),(('a','x'),),True),
            (('x','y'),(('a','x'),),False),
        ]
        for args in invalid:
            with self.subTest(args=args),self.assertRaises(OperatorRefusal):Program(*args)

    def test_empty_and_duplicate_splits_are_refused(self):
        with self.assertRaises(OperatorRefusal):discover((),self.validation)
        with self.assertRaises(OperatorRefusal):discover(self.train,self.train)
        with self.assertRaises(OperatorRefusal):discover(self.train[:1]*2,self.validation)

    def test_bad_budget_and_bad_mode_refused(self):
        for b in (-1,0,37,True):
            with self.subTest(b=b),self.assertRaises(OperatorRefusal):
                discover(self.train,self.validation,budget=b)
        with self.assertRaises(OperatorRefusal):discover(self.train,self.validation,task='run_shell')
        with self.assertRaises(OperatorRefusal):discover(self.train,self.validation,selection='omniscient')

    def test_empty_program_pool_holds(self):
        with self.assertRaises(OperatorRefusal):discover(self.train,self.validation,candidates=())

    def test_output_does_not_claim_universal_proof(self):
        r=heldout(self.four,self.test)
        self.assertFalse(r['general_math_claim'])
        self.assertEqual(self.four.status,'I_EXECUTABLE_OPERATOR_VALIDATED')

    def test_both_syntax_and_behavior_verified_before_child_export(self):
        with TemporaryDirectory() as tmp:
            counterfeit=replace(self.four,program=self.triangle.program)
            with self.assertRaises(OperatorRefusal):build_child(ROOT,Path(tmp),counterfeit)

    def test_not_allow_other_task_to_build_four_cycle_child(self):
        with TemporaryDirectory() as tmp:
            with self.assertRaises(OperatorRefusal):build_child(ROOT,Path(tmp),self.triangle)

    def test_generated_child_is_real_separate_process(self):
        with TemporaryDirectory() as tmp:
            child=build_child(ROOT,Path(tmp),self.four)
            r=run_child(child,ROOT)
            self.assertEqual(r['status'],'F_LOCAL_INDEPENDENT_CHILD_CHECK')
            self.assertEqual(r['repository_edits'],0)
            self.assertEqual(r['real_world_actions'],0)
            self.assertIn('def constructed_operator',child.read_text())

    def test_child_runs_different_heldout_graph(self):
        with TemporaryDirectory() as tmp:
            child=build_child(ROOT,Path(tmp),self.four)
            self.assertEqual(run_child(child,ROOT,11)['status'],'F_LOCAL_INDEPENDENT_CHILD_CHECK')

    def test_child_refuses_invalid_index(self):
        with TemporaryDirectory() as tmp:
            child=build_child(ROOT,Path(tmp),self.four)
            self.assertEqual(run_child(child,ROOT,31)['status'],'HOLD_BAD_INDEX')

    def test_child_cannot_overwrite(self):
        with TemporaryDirectory() as tmp:
            build_child(ROOT,Path(tmp),self.four)
            with self.assertRaises(FileExistsError):build_child(ROOT,Path(tmp),self.four)

    def test_child_tampering_refused(self):
        with TemporaryDirectory() as tmp:
            child=build_child(ROOT,Path(tmp),self.four)
            child.write_text(child.read_text()+'\n# edited\n')
            self.assertEqual(run_child(child,ROOT)['status'],'HOLD_CHILD_TAMPER')

    def test_source_drift_detected_before_child_import(self):
        with TemporaryDirectory() as tmp:
            child=build_child(ROOT,Path(tmp)/'child',self.four)
            copyroot=Path(tmp)/'source'
            for rel,_ in pins(ROOT):
                f=copyroot/rel;f.parent.mkdir(parents=True,exist_ok=True)
                copy2(ROOT/rel,f)
            (copyroot/'mathal001'/'nunumathal.py').write_text('raise RuntimeError("changed")\n')
            r=run_child(child,copyroot)
            self.assertEqual(r['status'],'HOLD_SOURCE_DRIFT')

    def test_source_pins_fail_on_symlink(self):
        with TemporaryDirectory() as tmp:
            fake=Path(tmp)
            for rel,_ in pins(ROOT):
                f=fake/rel;f.parent.mkdir(parents=True,exist_ok=True)
                copy2(ROOT/rel,f)
            link=fake/'operatorinvention001'/'operatorinvention.py'
            link.unlink();link.symlink_to(ROOT/'operatorinvention001'/'operatorinvention.py')
            with self.assertRaises(OperatorRefusal):pins(fake)

    def test_duplicate_graph_inputs_do_not_hide_failing_holdout(self):
        wrong=replace(self.four,status='HOLD_UNVERIFIED')
        self.assertEqual(heldout(wrong,self.test)['status'],'HOLD_UNVERIFIED_MODEL_OR_CASES')

    def test_vertex_relabel_invariance(self):
        from nunumathal import Graph
        from contractfrontier import Probe
        old=self.ood[0].probe
        mapping={v:'relabel_'+v for v in old.graph.vertices}
        graph=Graph.build(mapping.values(),((mapping[a],mapping[b]) for a,b in old.graph.edges))
        altered=Probe('ood:relabelled',graph,mapping[old.a],mapping[old.b],'ood')
        self.assertEqual(self.four.program.interpret(old),self.four.program.interpret(altered))

    def test_replay_deterministic(self):
        same=discover(self.train,self.validation)
        self.assertEqual(self.four,same)
        self.assertEqual(same.training_digest,self.four.training_digest)

    def test_demo_connects_question_to_executable_result(self):
        result=demonstration()
        self.assertEqual(result['old_grammar_diagnosis'],'HOLD_FINITE_GRAMMAR_FALSIFIED')
        self.assertEqual(result['child']['status'],'F_LOCAL_INDEPENDENT_CHILD_CHECK')
        self.assertEqual(result['external_actions'],0)
        self.assertEqual(result['status'],'I_EXECUTABLE_OPERATOR_VALIDATED')

if __name__=='__main__':unittest.main()
