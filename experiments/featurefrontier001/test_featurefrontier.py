"""Executable controls for bounded relational feature synthesis and refusal."""
from __future__ import annotations
from dataclasses import replace
from hashlib import sha256
from pathlib import Path
from shutil import copy2
from tempfile import TemporaryDirectory
from unittest.mock import patch
import inspect
import json
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'contractfrontier002'))
sys.path.insert(0,str(ROOT/'mathal001'))
from nunumathal import Graph
from contractfrontier import Probe,observed_outcome,coarse_counterexample,features
from featurefrontier import (
    PROGRAMS,ATOM_TYPES,Feature,Expression,FeatureRefusal,
    pool,path_probe,discover,infer,heldout,ablate,anti_corruption,
    build_child,run_child,pins,demonstration,fir_receipt
)

class FeatureFrontierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.train=pool('train')
        cls.validation=pool('validation')
        cls.test=pool('test',20)
        cls.ood=pool('ood',20)
        cls.d=discover(cls.train,cls.validation)

    def test_actual_source_uses_real_nunumathal_graphs(self):
        self.assertIsInstance(self.train[0].graph,Graph)
        self.assertEqual(self.d.status,'I_VALIDATED_SYNTHESIZED_FEATURES')

    def test_grammar_is_generated_not_named_oracle_features(self):
        self.assertEqual(len(PROGRAMS),237)
        self.assertTrue(all(m.feature is None or m.feature.kind in ('count','edge_closure') for m in PROGRAMS))
        self.assertEqual(len(ATOM_TYPES),6)
        self.assertFalse(any('common_neighbors' in m.text() or 'connected' in m.text() for m in PROGRAMS))

    def test_learned_triangle_feature_is_a_two_atom_relational_join(self):
        self.assertEqual(self.d.triangle.feature.kind,'count')
        self.assertEqual(self.d.triangle.feature.atoms,(('a','x'),('b','x')))
        self.assertEqual((self.d.triangle.coefficient,self.d.triangle.intercept),(1,0))

    def test_learned_component_feature_is_transitive_closure(self):
        f=self.d.components.feature
        self.assertEqual((f.kind,f.depth),('edge_closure',0))
        self.assertEqual((self.d.components.coefficient,self.d.components.intercept),(1,-1))

    def test_used_only_five_interventions(self):
        self.assertEqual(self.d.inspections,5)
        self.assertEqual(len([r for r in self.d.receipts if 'probe' in r]),5)
        self.assertGreater(self.d.remaining_hypotheses[0],1)
        self.assertEqual(self.d.remaining_hypotheses[1],1)

    def test_train_splits_unreused(self):
        self.assertFalse(set(x.key for x in self.train)&set(x.key for x in self.validation))
        self.assertFalse(set(x.key for x in self.test)&set(x.key for x in self.ood))
        self.assertEqual(self.train,pool('train'))

    def test_independent_validation_result_has_digest(self):
        self.assertEqual(self.d.receipts[-1]['action'],'VALIDATE_FROZEN_DISCOVERED_PROGRAMS')
        self.assertEqual(self.d.receipts[-1]['status'],'F_LOCAL_EXACT_REPLAY')
        self.assertEqual(len(self.d.valid_digest),24)

    def test_heldout_synthetic_replay(self):
        result=heldout(self.d,self.test)
        self.assertEqual((result['matched'],result['cases']),(len(self.test),len(self.test)))
        self.assertEqual(result['status'],'F_LOCAL_REPLAY')
        self.assertFalse(result['general_claim'])

    def test_ood_larger_graph_replay(self):
        result=heldout(self.d,self.ood)
        self.assertEqual(result['matched'],len(self.ood))
        self.assertTrue(any(len(p.graph.vertices)>20 for p in self.ood))

    def test_direct_benchmarks_tie_strong_known_formula(self):
        for p in self.test:
            direct=(features(p)['common_neighbors'],features(p)['connected']-1)
            self.assertEqual(direct,infer(self.d,p))
            self.assertEqual(direct,observed_outcome(p))

    def test_two_common_neighbors_counted_once_each(self):
        g=Graph.build('abcde',[('a','c'),('b','c'),('a','d'),('b','d'),('d','e')])
        p=Probe('test:two',g,'a','b','test')
        self.assertEqual(infer(self.d,p),(2,0))

    def test_adding_bridge_removes_component(self):
        p=path_probe('test',8,True)
        self.assertEqual(infer(self.d,p),(0,-1))

    def test_long_connected_path_requires_closure(self):
        p=path_probe('ood',23)
        self.assertEqual(self.d.components.feature.evaluate(p.graph,p.a,p.b),1)
        self.assertEqual(Feature('edge_closure',depth=5).evaluate(p.graph,p.a,p.b),0)
        self.assertEqual(infer(self.d,p),(0,0))

    def test_coarse_graph_statistics_insufficient(self):
        result=coarse_counterexample()
        self.assertTrue(result['genuine_counterexample'])
        self.assertTrue(result['equal_coarse_statistics'])

    def test_relabeling_graph_vertices_preserves_law(self):
        p=self.ood[4]
        rename={v:'zz_'+v for v in p.graph.vertices}
        g=Graph.build(rename.values(),[(rename[a],rename[b]) for a,b in p.graph.edges])
        q=Probe('ood:renamed',g,rename[p.a],rename[p.b],'ood')
        self.assertEqual(infer(self.d,p),infer(self.d,q))

    def test_refit_without_join_fails_to_find_law(self):
        out=ablate(self.train,self.validation,remove_join=True)
        self.assertLess(out['programs'],len(PROGRAMS))
        self.assertEqual(out['status'],'HOLD_NO_RELATIONAL_EXPLANATION')

    def test_refit_without_closure_does_not_pass_validation(self):
        out=ablate(self.train,self.validation,remove_closure=True)
        self.assertEqual(out['status'],'HOLD_VALIDATION_COUNTEREXAMPLE')

    def test_active_training_never_looks_at_heldout(self):
        signature=inspect.signature(discover)
        self.assertNotIn('test',signature.parameters)
        self.assertNotIn('ood',signature.parameters)
        altered=tuple(replace(p,key=p.key+'changed') for p in self.test)
        self.assertEqual(self.d,discover(self.train,self.validation))
        self.assertNotEqual(heldout(self.d,self.test)['digest'],heldout(self.d,altered)['digest'])

    def test_probe_readout_only_after_selection(self):
        import featurefrontier
        seen=[]
        origin=featurefrontier.observed_outcome
        def record(p):
            seen.append(p.key)
            return origin(p)
        with patch.object(featurefrontier,'observed_outcome',side_effect=record):
            result=discover(self.train,self.validation,budget=3)
        self.assertGreaterEqual(len(seen),3)
        self.assertEqual(seen[:3],[r['probe'] for r in result.receipts if 'probe' in r])
        self.assertTrue(all(p.key not in seen[:3] for p in self.validation))

    def test_invalid_splits_and_duplicate_keys_refused(self):
        with self.assertRaises(FeatureRefusal):discover(self.train,self.train)
        with self.assertRaises(FeatureRefusal):discover(self.train[:1]*2,self.validation)
        with self.assertRaises(FeatureRefusal):discover((),self.validation)

    def test_invalid_budget_refused(self):
        for n in (0,len(self.train)+1):
            with self.assertRaises(FeatureRefusal):discover(self.train,self.validation,budget=n)
        with self.assertRaises(FeatureRefusal):discover(self.train,self.validation,select='oracle')

    def test_incomplete_budget_abstains(self):
        result=discover(self.train,self.validation,budget=1)
        self.assertFalse(result.usable)

    def test_invalid_feature_grammar_refused(self):
        with self.assertRaises(FeatureRefusal):Feature('count',(('a','b'),))
        with self.assertRaises(FeatureRefusal):Feature('count',(('x','a'),))
        with self.assertRaises(FeatureRefusal):Feature('edge_closure',depth=17)
        with self.assertRaises(FeatureRefusal):Feature('exec')

    def test_invalid_program_grammar_refused(self):
        with self.assertRaises(FeatureRefusal):Expression(None,1,0)
        with self.assertRaises(FeatureRefusal):Expression(None,0,4)
        with self.assertRaises(FeatureRefusal):Expression(Feature('edge_closure'),10,0)

    def test_no_unverified_model_inference(self):
        fake=replace(self.d,status='I_UNTESTED')
        with self.assertRaises(FeatureRefusal):infer(fake,self.test[0])
        self.assertEqual(heldout(fake,self.test)['status'],'HOLD_NO_VALIDATED_FEATURES')

    def test_compositional_program_detects_tampered_outcome_if_replayed(self):
        out=anti_corruption(self.d,self.test[0])
        self.assertTrue(out['detected_by_independent_replay'])
        self.assertFalse(out['trusted_source_authenticity_proved'])

    def test_fir_separates_finite_arithmetic_from_general_truth(self):
        r=fir_receipt(self.d,heldout(self.d,self.test))
        self.assertEqual(r['finite_role'],'F_LOCAL')
        self.assertEqual(r['universal_role'],'I')
        self.assertTrue(any(x.get('operation')=='admit' for x in r['receipts']))

    def test_fir_wont_admit_failure(self):
        r=fir_receipt(replace(self.d,status='I_UNTESTED'),{'status':'HOLD','digest':'none'})
        self.assertEqual(r['finite_role'],'I')

    def test_pins_are_repo_source_bytes(self):
        checks=pins(ROOT)
        self.assertEqual(len(checks),5)
        for path,actual in checks:
            self.assertEqual(sha256((ROOT/path).read_bytes()).hexdigest(),actual)

    def test_generated_child_executes_frozen_programs(self):
        with TemporaryDirectory() as td:
            child=build_child(ROOT,Path(td),self.d)
            result=run_child(child,ROOT)
            self.assertEqual(result['status'],'F_LOCAL_CHILD_REPLAY')
            self.assertEqual(result['real_actions'],0)
            self.assertEqual(result['source_changes'],0)
            self.assertEqual(len(result['programs']),2)

    def test_child_cannot_overwrite(self):
        with TemporaryDirectory() as td:
            build_child(ROOT,Path(td),self.d)
            with self.assertRaises(FileExistsError):build_child(ROOT,Path(td),self.d)

    def test_child_tampering_refused(self):
        with TemporaryDirectory() as td:
            child=build_child(ROOT,Path(td),self.d)
            child.write_text(child.read_text()+'\n# changed\n')
            self.assertEqual(run_child(child,ROOT)['status'],'HOLD_CHILD_TAMPER')

    def test_child_rejects_invalid_index(self):
        with TemporaryDirectory() as td:
            child=build_child(ROOT,Path(td),self.d)
            self.assertEqual(run_child(child,ROOT,-7)['status'],'HOLD_INDEX')

    def test_child_detects_source_drift_before_import(self):
        with TemporaryDirectory() as td:
            child=build_child(ROOT,Path(td)/'child',self.d)
            copy_root=Path(td)/'copy'
            for rel,checksum in pins(ROOT):
                f=copy_root/rel;f.parent.mkdir(parents=True,exist_ok=True)
                copy2(ROOT/rel,f)
            (copy_root/'mathal001'/'nunumathal.py').write_text('# tampered\n')
            self.assertEqual(run_child(child,copy_root)['status'],'HOLD_SOURCE_DRIFT')

    def test_symlink_source_refused(self):
        with TemporaryDirectory() as td:
            fake=Path(td)
            for rel,_ in pins(ROOT):
                f=fake/rel;f.parent.mkdir(parents=True,exist_ok=True)
                copy2(ROOT/rel,f)
            link=fake/'contractfrontier002'/'contractfrontier.py'
            link.unlink();link.symlink_to(ROOT/'contractfrontier002'/'contractfrontier.py')
            with self.assertRaises(FeatureRefusal):pins(fake)

    def test_forged_model_not_exportable(self):
        with TemporaryDirectory() as td:
            counterfeit=replace(self.d,triangle=Expression(None,0,0))
            with self.assertRaises(FeatureRefusal):build_child(ROOT,Path(td),counterfeit)

    def test_deterministic_candidate_and_evidence_order(self):
        other=discover(self.train,self.validation)
        self.assertEqual(other,self.d)

    def test_demo_runs_and_reports_next_question(self):
        r=demonstration()
        self.assertEqual(r['child']['status'],'F_LOCAL_CHILD_REPLAY')
        self.assertEqual(r['FIR']['universal_role'],'I')
        self.assertEqual(r['inferred_laws'][0],self.d.triangle.text())
        self.assertEqual(r['real_world_actions'],0)
        self.assertIn('language itself grow',r['next_question'])

if __name__=='__main__':unittest.main()
