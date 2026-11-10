"""Hostile and independent finite controls for CONTRACT-FRONTIER-002.

These tests establish performance only on declared simple-graph fixtures.
They are not a proof checker or evidence of unrestricted semantic invention.
"""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from shutil import copy2
import json
import sys
import unittest

from contractfrontier import (
    ROOT, Graph, Trial, Probe, Expr, FrontierRefusal, FEATURES, PROGRAMS,
    adjacent, connected, count_triangles, alternate_triangles, features,
    observed_outcome, _graphs, choose_probe, entropy, digest,
    discover, audit, infer, sabotage_readout, coarse_counterexample,
    fir_receipts, source_pins, build_child, run_child, demonstration,
)


class ContractFrontierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.train=_graphs('train',120)
        cls.validation=_graphs('validation',60)
        cls.test=_graphs('test',100)
        cls.ood=_graphs('ood',100)
        cls.learned=discover(cls.train,cls.validation)

    def test_finite_candidate_grammar_is_not_fitted_answer(self):
        self.assertEqual(len(PROGRAMS),313)
        self.assertEqual(len({x.terms for x in PROGRAMS}),len(PROGRAMS))
        self.assertIn(Expr((('common_neighbors',1),)),PROGRAMS)
        self.assertIn(Expr((('connected',1),('one',-1))),PROGRAMS)
        self.assertTrue(all(len(p.terms)<=2 for p in PROGRAMS))

    def test_invalid_grammar_and_input_hold(self):
        for invalid in (((('not-a-feature',1),),), ((('one',3),),),
                        ((('one',1),('one',-1)),),
                        ((('one',1),('connected',1),('edges',1)),)):
            with self.assertRaises(FrontierRefusal):
                Expr(invalid[0])
        self.assertRaises(FrontierRefusal,Probe,'bad',Graph.build(['a'],[]),'a','a','train')

    def test_hold_on_preexisting_edge_or_bad_source(self):
        g=Graph.build(['a','b'], [('a','b')])
        with self.assertRaisesRegex(FrontierRefusal,'EDGE_ALREADY'):
            Probe('bad',g,'a','b','train')
        with self.assertRaises(FrontierRefusal):
            Probe('bad',g,'a','absent','train')

    def test_isolated_vs_connected_endpoint_preconditions(self):
        g=Graph.build(list('abc'),[('a','b')])
        self.assertTrue(connected(g,'a','b'))
        self.assertFalse(connected(g,'a','c'))
        self.assertEqual(adjacent(g,'a'),frozenset({'b'}))

    def test_triangle_count_two_independent_methods(self):
        g=Graph.build(list('abcde'),[('a','b'),('b','c'),('a','c'),('c','d')])
        self.assertEqual(count_triangles(g),1)
        self.assertEqual(alternate_triangles(g),1)
        self.assertEqual(count_triangles(Graph.build(list('abc'),[])),0)

    def test_true_graph_port_connected_and_triangle_values(self):
        g=Graph.build(list('abcd'), [('a','c'),('b','c')])
        p=Probe('train:known',g,'a','b','train')
        self.assertEqual(observed_outcome(p),(1,0))
        self.assertEqual(features(p)['common_neighbors'],1)
        self.assertEqual(features(p)['connected'],1)
        # A disconnected edge creates no triangle and reduces components.
        p2=Probe('train:disc',g,'a','d','train')
        self.assertEqual(observed_outcome(p2),(0,-1))

    def test_targets_are_measured_through_original_graph_cartridge(self):
        p=self.train[2]
        self.assertEqual(p.trial().operation,'add_edge')
        self.assertEqual(p.trial().source,p.graph)
        import contractdiscovery
        after=contractdiscovery.apply(p.trial())
        self.assertEqual(len(after.edges),len(p.graph.edges)+1)

    def test_splits_are_disjoint_and_deterministic(self):
        self.assertEqual(self.train,_graphs('train',120))
        self.assertEqual(len({p.key for p in self.train+self.validation+self.test+self.ood}),380)
        self.assertEqual(len({digest((p.key,observed_outcome(p)) for p in group)
                              for group in (self.train,self.validation,self.test,self.ood)}),4)

    def test_ood_graphs_are_larger_and_have_distinct_vertices(self):
        self.assertTrue(all(len(p.graph.vertices)>=11 for p in self.ood))
        self.assertTrue(all(len(p.graph.vertices)<=9 for p in self.train))
        self.assertFalse(set().union(*(p.graph.vertices for p in self.train)) &
                         set().union(*(p.graph.vertices for p in self.ood)))

    def test_training_pool_contains_connected_and_disconnected_arms(self):
        self.assertTrue(any(connected(p.graph,p.a,p.b) for p in self.train))
        self.assertTrue(any(not connected(p.graph,p.a,p.b) for p in self.train))
        self.assertTrue(any(features(p)['common_neighbors']>1 for p in self.train))

    def test_information_gain_is_nonnegative_and_chooses_pool_member(self):
        self.assertEqual(entropy({0:5}),0.)
        self.assertAlmostEqual(entropy({0:2,1:2}),1.)
        selected=choose_probe(self.train[:10],(PROGRAMS,PROGRAMS))
        self.assertIn(selected,self.train[:10])

    def test_probe_picker_cannot_see_oracle_outcome(self):
        # This ensures active selection is prequential, not test-label leakage.
        with patch('contractfrontier.observed_outcome',side_effect=RuntimeError('oracle forbidden')):
            choice=choose_probe(self.train[:16],(PROGRAMS,PROGRAMS))
        self.assertIn(choice,self.train[:16])

    def test_active_discovery_builds_two_distinct_math_relations(self):
        self.assertTrue(self.learned.usable)
        self.assertEqual(self.learned.inspected,3)
        self.assertEqual(self.learned.triangle,Expr((('common_neighbors',1),)))
        self.assertEqual(self.learned.components,Expr((('connected',1),('one',-1))))
        self.assertEqual(self.learned.remaining,(1,1))

    def test_active_receipts_show_numerical_version_space_reduction(self):
        rows=[r for r in self.learned.receipts if r.get('action')=='EXECUTE_ADD_EDGE']
        self.assertEqual(len(rows),self.learned.inspected)
        self.assertTrue(any(r['models_before']!=r['models_after'] for r in rows))
        self.assertTrue(all(r['external_actions']==0 for r in rows))
        self.assertEqual(self.learned.receipts[-1]['action'],'VALIDATE_EXACT_OUTCOMES')

    def test_frozen_holdout_and_ood_are_independently_recomputed(self):
        a,b=audit(self.learned,self.test),audit(self.learned,self.ood)
        for r in (a,b):
            self.assertEqual((r['cases'],r['correct'],r['instrument_crosscheck']),(100,100,100))
            self.assertEqual(r['status'],'F_LOCAL_EXACT_TEST')
            self.assertFalse(r['generalization_proved'])

    def test_inferred_values_need_no_outcome_lookup(self):
        with patch('contractfrontier.observed_outcome',side_effect=RuntimeError('oracle forbidden')):
            result=infer(self.learned,self.test[3])
        self.assertEqual(result['status'],'I_MODEL_PREDICTION')
        self.assertEqual(result['external_actions'],0)

    def test_abi_is_two_separately_typed_numerical_ports(self):
        prediction=infer(self.learned,self.test[0])
        self.assertEqual(set(prediction),{'delta_triangles','delta_components','status','train_digest','external_actions'})
        self.assertTrue(all(type(prediction[k])==int for k in ('delta_triangles','delta_components')))

    def test_insufficient_budget_abstains(self):
        result=discover(self.train,self.validation,budget=1)
        self.assertFalse(result.usable)
        self.assertEqual(result.status,'HOLD_UNIDENTIFIABLE_AT_BUDGET')
        with self.assertRaisesRegex(FrontierRefusal,'NO_VALIDATED'):
            infer(result,self.test[0])

    def test_no_common_neighbor_feature_fails_to_identify_triangle_law(self):
        without=tuple(p for p in PROGRAMS if all(name!='common_neighbors' for name,_ in p.terms))
        result=discover(self.train,self.validation,programs=without,budget=12)
        self.assertFalse(result.usable)
        self.assertIn(result.status,{'HOLD_NO_SUPPORTED_HYPOTHESIS',
                                    'HOLD_UNIDENTIFIABLE_AT_BUDGET',
                                    'HOLD_VALIDATION_COUNTEREXAMPLE'})

    def test_sensor_corruption_in_validation_causes_hold(self):
        original=observed_outcome
        def changed(p):
            a,b=original(p)
            return (a+1,b) if p.split=='validation' else (a,b)
        with patch('contractfrontier.observed_outcome',side_effect=changed):
            result=discover(self.train,self.validation)
        self.assertEqual(result.status,'HOLD_VALIDATION_COUNTEREXAMPLE')

    def test_hypothesis_forgery_fails_child_gate(self):
        with TemporaryDirectory() as tmp:
            fake=replace(self.learned,triangle=Expr(()))
            with self.assertRaisesRegex(FrontierRefusal,'UNAUTHENTICATED'):
                build_child(ROOT,Path(tmp),fake)

    def test_train_validation_overlap_refused(self):
        with self.assertRaisesRegex(FrontierRefusal,'BAD_DISCOVERY'):
            discover(self.train,self.train)
        with self.assertRaises(FrontierRefusal):
            discover(self.train,self.validation,budget=999)
        with self.assertRaises(FrontierRefusal):
            discover(self.train,self.validation,selection='answer-key')

    def test_false_claim_does_not_become_mathal_fact(self):
        report=fir_receipts(self.learned,audit(self.learned,self.test))
        self.assertEqual(report['local_status'],'F_LOCAL')
        self.assertEqual(report['general_status'],'I_ONLY')
        self.assertEqual(sum(x['operation']=='admit' for x in report['receipts']),1)
        self.assertIn('finite_computation',str(report['receipts']))

    def test_failed_audit_not_promoted_to_fact(self):
        fail={'status':'HOLD_HIDDEN_REGRESSION','digest':'synthetic'}
        self.assertEqual(fir_receipts(self.learned,fail)['local_status'],'I')

    def test_coarse_graph_measurements_cannot_predict_triangles(self):
        r=coarse_counterexample()
        self.assertTrue(all(r[x] for x in ('equal_coarse_statistics','equal_endpoint_degrees',
                                          'equal_connectivity','genuine_counterexample')))
        self.assertEqual(r['triangle_changes'],(1,0))

    def test_type_correct_observation_attack_detected_by_replay(self):
        self.assertTrue(all(sabotage_readout(self.learned,p)['detected_on_independent_replay']
                            for p in self.test[:20]))
        self.assertFalse(sabotage_readout(self.learned,self.test[0])['source_authenticity_verified'])

    def test_fixture_input_graphs_remain_immutable(self):
        before=self.test[0].graph
        result=infer(self.learned,self.test[0])
        self.assertEqual(before,self.test[0].graph)
        self.assertNotIn(tuple(sorted((self.test[0].a,self.test[0].b))),before.edges)
        self.assertEqual(result['external_actions'],0)

    def test_child_uses_real_pinned_upstream_code(self):
        checks=source_pins(ROOT)
        self.assertEqual(len(checks),4)
        for rel,sha in checks:
            from hashlib import sha256
            self.assertEqual(sha,sha256((ROOT/rel).read_bytes()).hexdigest())

    def test_generated_child_runs_independent_process(self):
        with TemporaryDirectory() as tmp:
            child=build_child(ROOT,Path(tmp),self.learned)
            result=run_child(child,ROOT,index=4)
            self.assertEqual(result['status'],'F_LOCAL_CHILD_REPLAY')
            self.assertEqual(result['predictions'],result['observed'])
            self.assertEqual((result['external_actions'],result['repo_edits']),(0,0))

    def test_child_refuses_tampering_and_does_not_overwrite(self):
        with TemporaryDirectory() as tmp:
            child=build_child(ROOT,Path(tmp),self.learned)
            with self.assertRaises(FileExistsError):
                build_child(ROOT,Path(tmp),self.learned)
            child.write_text(child.read_text()+'\n# unauthorized change')
            self.assertEqual(run_child(child,ROOT)['status'],'HOLD_CHILD_TAMPER_OR_MISSING')

    def test_child_wrong_index_and_pin_drift_hold(self):
        with TemporaryDirectory() as tmp:
            child=build_child(ROOT,Path(tmp),self.learned)
            self.assertEqual(run_child(child,ROOT,index=100)['status'],'HOLD_INDEX')
            # A copied source may be changed without ever modifying the original.
            with TemporaryDirectory() as checkout:
                fake_root=Path(checkout)
                for rel,_ in source_pins(ROOT):
                    dst=fake_root/rel;dst.parent.mkdir(parents=True,exist_ok=True)
                    copy2(ROOT/rel,dst)
                (fake_root/'mathal001'/'nunumathal.py').write_text('raise RuntimeError("tampered")')
                self.assertEqual(run_child(child,fake_root)['status'],'HOLD_SOURCE_DRIFT')

    def test_demo_executes_next_questions_and_child(self):
        response=demonstration()
        self.assertEqual(response['status'],'I_FINITE_CONTRACTS_VALIDATED')
        self.assertEqual(response['observed_training_probes'],3)
        self.assertEqual(response['child']['status'],'F_LOCAL_CHILD_REPLAY')
        self.assertFalse(response['self_modified_live_code'])
        self.assertFalse(response['generalization_proved'])
        self.assertEqual(response['real_world_actions'],0)

    def test_random_baseline_is_not_privileged(self):
        models=discover(self.train,self.validation,budget=8,selection='random',seed=4)
        self.assertTrue(all(x.get('selection')=='random' for x in models.receipts if 'selection' in x))
        self.assertGreaterEqual(models.inspected,self.learned.inspected)


if __name__=='__main__':
    unittest.main()
