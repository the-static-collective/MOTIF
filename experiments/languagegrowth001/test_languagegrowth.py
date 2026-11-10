"""LANGUAGE-GROWTH-001 adversarial controls for finite operator extension."""
from dataclasses import replace
from hashlib import sha256
from pathlib import Path
from shutil import copy2
from tempfile import TemporaryDirectory
from unittest.mock import patch
from itertools import combinations
import inspect
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'mathal001'))
sys.path.insert(0,str(ROOT/'contractfrontier002'))
from nunumathal import Graph
from contractfrontier import Probe,adjacent
from languagegrowth import (
    Experiment,Query,LanguageRefusal,PATCHES,ORIGINAL_GRAMMAR,
    count_four_cycles,path_three_reference,measured_outcome,trials,
    programs_for_patch,diagnose,grow,predict,test,ablation,
    emit_fir,pins,build_child,run_child,demonstrate,ROOT as SOURCE_ROOT
)

class LanguageGrowthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.train=trials('train')
        cls.validation=trials('validation')
        cls.test=trials('test',30)
        cls.ood=trials('ood',30)
        cls.discovery=grow(cls.train,cls.validation)

    def test_real_nunumathal_graphs_drive_experiment(self):
        self.assertTrue(all(isinstance(e.probe.graph,Graph) for e in self.train))
        self.assertEqual(self.discovery.status,'I_PATCH_VALIDATED')

    def test_base_grammar_is_real_previous_237_programs(self):
        self.assertEqual(len(ORIGINAL_GRAMMAR),237)
        self.assertTrue(all('COUNT_XY' not in m.text() for m in ORIGINAL_GRAMMAR))

    def test_diagnostic_falsifies_finite_grammar_with_actual_readings(self):
        d=diagnose(self.train)
        self.assertEqual(d['status'],'HOLD_FINITE_GRAMMAR_FALSIFIED')
        self.assertEqual(d['remaining'],0)
        self.assertEqual(d['inspections'],2)
        self.assertFalse(not d['not_a_universal_impossibility_proof'])

    def test_not_every_missing_answer_is_a_grammar_gap(self):
        zeros=tuple(x for x in self.train if measured_outcome(x)==0)
        self.assertGreaterEqual(len(zeros),4)
        d=diagnose(zeros,budget=4)
        self.assertEqual(d['status'],'I_OLD_GRAMMAR_NOT_FALSIFIED')
        r=grow(zeros,self.validation,budget=4)
        self.assertEqual(r.status,'HOLD_NO_PROVEN_LANGUAGE_GAP')

    def test_expansion_is_selected_not_given(self):
        self.assertEqual(len(PATCHES),3)
        self.assertEqual(self.discovery.operator,'COUNT_BINDING_PAIRS')
        self.assertEqual(self.discovery.formula.aggregator,'COUNT_XY')
        self.assertNotEqual(self.discovery.formula.aggregator,'COUNT_X')

    def test_program_is_synthesized_edge_join_without_square_primitive(self):
        q=self.discovery.formula
        self.assertEqual(q.atoms,(('a','x'),('b','y'),('x','y')))
        self.assertEqual((q.coefficient,q.intercept),(1,0))
        self.assertNotIn('four_cycle',q.text())
        self.assertNotIn('square',q.text())

    def test_active_evidence_is_bounded_and_minimal(self):
        self.assertEqual(self.discovery.observations,3)
        self.assertLess(self.discovery.observations,len(self.train))
        self.assertEqual(self.discovery.receipts[-2]['action'],
                         'STOP_OBSERVATIONAL_EQUIVALENCE_ON_TRAIN_POOL')

    def test_grammar_is_actually_changed_not_just_policy_weights(self):
        q=self.discovery.formula
        self.assertTrue(q.aggregator not in {m.feature.kind for m in ORIGINAL_GRAMMAR
                                            if m.feature is not None})
        self.assertEqual(q.evaluate(self.test[0].probe),predict(self.discovery,self.test[0]))

    def test_heldout_unseen_experiments(self):
        r=test(self.discovery,self.test)
        self.assertEqual((r['matched'],r['cases']),(30,30))
        self.assertEqual(r['status'],'F_LOCAL_FINITE_REPLAY')
        self.assertFalse(r['unrestricted_correctness_claim'])

    def test_larger_ood_experiments(self):
        self.assertTrue(all(len(e.probe.graph.vertices)>=11 for e in self.ood))
        r=test(self.discovery,self.ood)
        self.assertEqual((r['matched'],r['cases']),(30,30))
        self.assertEqual(r['independent_algorithm_matches_outcome'],30)

    def test_independent_classical_path_count_matches_four_cycle_counter(self):
        for e in self.test+self.ood:
            self.assertEqual(measured_outcome(e),
                             path_three_reference(e.probe.graph,e.probe.a,e.probe.b))

    def test_exact_four_cycle_counter_on_square(self):
        g=Graph.build('abcd',[('a','b'),('b','c'),('c','d'),('a','d')])
        self.assertEqual(count_four_cycles(g),1)

    def test_exact_four_cycle_counter_on_k4(self):
        g=Graph.build('abcd',combinations('abcd',2))
        self.assertEqual(count_four_cycles(g),3)

    def test_no_spurious_cycle_from_wedge(self):
        g=Graph.build('abcd',[('a','b'),('b','c'),('b','d')])
        self.assertEqual(count_four_cycles(g),0)

    def test_count_x_underestimates_when_multiple_second_bindings(self):
        g=Graph.build('abxuv',[('a','x'),('x','u'),('x','v'),('u','b'),('v','b')])
        p=Probe('test:fork',g,'a','b','test')
        self.assertEqual(self.discovery.formula.evaluate(p),2)
        q=Query((('a','x'),('b','y'),('x','y')),'COUNT_X')
        self.assertEqual(q.evaluate(p),1)

    def test_each_licensed_patch_is_generated_from_generic_atoms(self):
        for p in PATCHES:
            grammar=programs_for_patch(p)
            self.assertTrue(grammar)
            self.assertTrue(all(1<=len(q.atoms)<=3 for q in grammar))

    def test_no_count_pair_operator_means_no_valid_extension(self):
        out=ablation(self.train,self.validation)
        self.assertEqual(out['COUNT_BINDING_PAIRS']['status'],'HOLD_NO_SUPPORTED_OPERATOR')
        self.assertEqual(out['COUNT_OTHER_BINDING']['selected'],'COUNT_BINDING_PAIRS')

    def test_low_budget_refuses_false_discovery(self):
        r=grow(self.train,self.validation,budget=2)
        self.assertEqual(r.status,'HOLD_VALIDATION_COUNTEREXAMPLE')
        self.assertIsNone(r.formula)

    def test_budget_three_is_sufficient_on_this_fixture(self):
        r=grow(self.train,self.validation,budget=3)
        self.assertEqual(r.status,'I_PATCH_VALIDATED')
        self.assertEqual(r.formula,self.discovery.formula)

    def test_missing_other_two_patches_does_not_prevent_growth(self):
        r=grow(self.train,self.validation,allowed_patches=('COUNT_BINDING_PAIRS',))
        self.assertEqual(r.status,'I_PATCH_VALIDATED')
        self.assertEqual(r.operator,'COUNT_BINDING_PAIRS')

    def test_unsupported_patch_identifier_is_refused(self):
        with self.assertRaises(LanguageRefusal):programs_for_patch('SHELL_EXECUTE')
        with self.assertRaises(LanguageRefusal):grow(self.train,self.validation,allowed_patches=('SHELL_EXECUTE',))

    def test_invalid_query_expressions_are_refused(self):
        for atoms,aggregation in [((('x','a'),),'COUNT_X'),
                                  ((('a','b'),),'COUNT_X'),
                                  ((('a','x'),),'COUNT_XY'),
                                  ((('a','x'),),'READ_FILE')]:
            with self.assertRaises(LanguageRefusal):Query(atoms,aggregation)

    def test_invalid_coefficient_and_intercept_refused(self):
        with self.assertRaises(LanguageRefusal):Query((('a','x'),),'COUNT_X',2,0)
        with self.assertRaises(LanguageRefusal):Query((('a','x'),),'COUNT_X',1,42)

    def test_train_validation_key_leak_refused(self):
        with self.assertRaises(LanguageRefusal):grow(self.train,self.train)
        with self.assertRaises(LanguageRefusal):grow(self.train[:1]*5,self.validation)

    def test_missing_or_illegal_budget_refused(self):
        with self.assertRaises(LanguageRefusal):grow(self.train,self.validation,budget=0)
        with self.assertRaises(LanguageRefusal):grow(self.train,self.validation,budget=37)
        with self.assertRaises(LanguageRefusal):diagnose(self.train,0)
        with self.assertRaises(LanguageRefusal):grow(self.train,self.validation,selection='oracle')

    def test_no_test_truth_is_accepted_by_learner_signature(self):
        sig=inspect.signature(grow)
        self.assertNotIn('test',sig.parameters)
        self.assertNotIn('ood',sig.parameters)
        self.assertEqual(self.discovery,grow(self.train,self.validation))

    def test_outcomes_are_only_read_after_selection(self):
        import languagegrowth as m
        seen=[]
        origin=m.measured_outcome
        def watch(e):
            seen.append(e.key)
            return origin(e)
        with patch.object(m,'measured_outcome',side_effect=watch):
            r=m.grow(self.train,self.validation,budget=3)
        self.assertEqual(seen[:r.observations],[x['probe'] for x in r.receipts if 'probe' in x])
        self.assertFalse(set(e.key for e in self.validation)&set(seen[:r.observations]))

    def test_type_correct_forged_measurement_fails_independent_replay(self):
        e=self.test[0]
        original=measured_outcome(e)
        fake=original+1
        self.assertNotEqual(predict(self.discovery,e),fake)
        self.assertEqual(predict(self.discovery,e),original)

    def test_finite_fir_admission_never_promotes_universality(self):
        r=emit_fir(self.discovery,test(self.discovery,self.test))
        self.assertEqual((r['local_role'],r['universal_role']),('F_LOCAL','I'))
        self.assertTrue(any(x.get('operation')=='admit' for x in r['receipts']))

    def test_failed_model_does_not_get_local_admission(self):
        d=replace(self.discovery,status='HOLD')
        r=emit_fir(d,{'status':'HOLD','evidence_digest':'bad'})
        self.assertEqual(r['local_role'],'I')
        with self.assertRaises(LanguageRefusal):predict(d,self.test[0])

    def test_sources_are_pinned_to_actual_bytes(self):
        checks=pins(ROOT)
        self.assertEqual(len(checks),6)
        for rel,digest in checks:
            self.assertEqual(sha256((ROOT/rel).read_bytes()).hexdigest(),digest)

    def test_generated_child_runs_read_only_in_separate_process(self):
        with TemporaryDirectory() as td:
            child=build_child(ROOT,Path(td),self.discovery)
            r=run_child(child,ROOT,0)
            self.assertEqual(r['status'],'F_LOCAL_CHILD_REPLAY')
            self.assertEqual(r['external_actions'],0)
            self.assertEqual(r['source_edits'],0)

    def test_generated_child_cannot_overwrite_itself(self):
        with TemporaryDirectory() as td:
            build_child(ROOT,Path(td),self.discovery)
            with self.assertRaises(FileExistsError):build_child(ROOT,Path(td),self.discovery)

    def test_tampered_child_is_refused(self):
        with TemporaryDirectory() as td:
            child=build_child(ROOT,Path(td),self.discovery)
            child.write_text(child.read_text()+'\n# attacker\n')
            self.assertEqual(run_child(child,ROOT)['status'],'HOLD_CHILD_TAMPER')

    def test_missing_and_linked_child_are_refused(self):
        with TemporaryDirectory() as td:
            child=Path(td)/'fake.py'
            self.assertEqual(run_child(child,ROOT)['status'],'HOLD_CHILD_MISSING_OR_LINKED')
            child.symlink_to(ROOT/'languagegrowth001'/'languagegrowth.py')
            self.assertEqual(run_child(child,ROOT)['status'],'HOLD_CHILD_MISSING_OR_LINKED')

    def test_changed_source_file_is_refused_before_import(self):
        with TemporaryDirectory() as td:
            child=build_child(ROOT,Path(td)/'child',self.discovery)
            copy=Path(td)/'copy'
            for rel,_ in pins(ROOT):
                dest=copy/rel;dest.parent.mkdir(parents=True,exist_ok=True)
                copy2(ROOT/rel,dest)
            (copy/'featurefrontier001'/'featurefrontier.py').write_text('raise RuntimeError("tampered")')
            self.assertEqual(run_child(child,copy)['status'],'HOLD_SOURCE_DRIFT')

    def test_source_symlinks_are_refused(self):
        with TemporaryDirectory() as td:
            copy=Path(td)
            for rel,_ in pins(ROOT):
                dest=copy/rel;dest.parent.mkdir(parents=True,exist_ok=True)
                copy2(ROOT/rel,dest)
            f=copy/'languagegrowth001'/'languagegrowth.py'
            f.unlink();f.symlink_to(ROOT/'languagegrowth001'/'languagegrowth.py')
            with self.assertRaises(LanguageRefusal):pins(copy)

    def test_forged_formula_cannot_be_exported(self):
        fake=replace(self.discovery,formula=Query((('a','x'),),'COUNT_X'))
        with TemporaryDirectory() as td,self.assertRaises(LanguageRefusal):
            build_child(ROOT,Path(td),fake)

    def test_bad_child_index_refused(self):
        with TemporaryDirectory() as td:
            child=build_child(ROOT,Path(td),self.discovery)
            self.assertEqual(run_child(child,ROOT,-1)['status'],'HOLD_INVALID_INDEX')

    def test_vertex_relabeling_does_not_affect_prediction(self):
        e=self.ood[0];p=e.probe
        mapping={v:'z'+v for v in p.graph.vertices}
        g=Graph.build(mapping.values(),[(mapping[a],mapping[b]) for a,b in p.graph.edges])
        p2=Probe('ood:renamed',g,mapping[p.a],mapping[p.b],'ood')
        self.assertEqual(self.discovery.formula.evaluate(p),self.discovery.formula.evaluate(p2))

    def test_demo_is_reproducible_and_proposal_only(self):
        a=demonstrate();b=demonstrate()
        self.assertEqual(a,b)
        self.assertEqual(a['child']['status'],'F_LOCAL_CHILD_REPLAY')
        self.assertFalse(a['general_algorithm_invention'])
        self.assertEqual(a['real_world_actions'],0)

if __name__=='__main__':unittest.main()
