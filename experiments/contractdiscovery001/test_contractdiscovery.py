"""Hostile finite-model controls for autonomous experimental contract discovery."""
from dataclasses import replace
from fractions import Fraction
from pathlib import Path
from shutil import copy2
from tempfile import TemporaryDirectory
from unittest.mock import patch
from zipfile import ZipFile
import json
import subprocess
import sys
import unittest

from contractdiscovery import (
    CHANNELS, PERMUTATION, ContractRefusal, Discovery, MissingPortAdapter,
    Trial, _path, apply, independently_measure, independent_statistics,
    primitive, nullspace, measure, row_reduce, rank, trials, discover,
    check_relation, test_heldout, exhaustive_classical_control, fir_record,
    pins, build_child, run_child, demonstration,
)
from nunumathal import Graph, perform, statistics

ROOT=Path(__file__).resolve().parents[1]


class SourceAndProbeTests(unittest.TestCase):
    def test_real_upstream_nunumathal_graph_and_statistics(self):
        graph=_path('source_')
        self.assertIsInstance(graph,Graph)
        self.assertEqual(statistics(graph),(3,2,1,0,0))
        original=graph
        actual=perform(graph,'subdivide','source_d',edge=('source_a','source_b'))
        self.assertEqual(statistics(actual.target),(4,3,1,0,0))
        self.assertEqual(graph,original)

    def test_trial_keys_splits_independent(self):
        datasets=[trials(x) for x in ('train','validation','test','ood')]
        self.assertEqual(tuple(map(len,datasets)),(20,15,35,48))
        keys=[{x.key for x in dataset} for dataset in datasets]
        for i in range(4):
            for j in range(i):
                self.assertFalse(keys[i]&keys[j])

    def test_deletion_is_unseen_in_training_but_in_ood(self):
        train={x.operation for x in trials('train')}
        ood={x.operation for x in trials('ood')}
        self.assertEqual(train,{'isolated','leaf','subdivide','add_edge'})
        self.assertIn('remove_edge',ood)
        self.assertIn('remove_isolate',ood)
        self.assertTrue({'remove_edge','remove_isolate'}<=ood-train)

    def test_original_perform_is_used_for_addition_and_subdivision(self):
        examples=trials('train')
        for x in examples:
            if x.operation in {'isolated','leaf','subdivide'}:
                self.assertEqual(len(apply(x).vertices),len(x.source.vertices)+1)

    def test_all_interventions_preserve_input_graph(self):
        for case in trials('train')+trials('ood'):
            before=case.source
            new=apply(case)
            self.assertEqual(before,case.source)
            self.assertIsInstance(new,Graph)

    def test_inverse_operations_are_genuine(self):
        for case in trials('ood'):
            if case.operation=='remove_edge':
                self.assertEqual(len(apply(case).edges),len(case.source.edges)-1)
            if case.operation=='remove_isolate':
                self.assertEqual(len(apply(case).vertices),len(case.source.vertices)-1)

    def test_bad_intervention_rejected(self):
        with self.assertRaises(ContractRefusal):Trial('x',_path('a_'),'shell',())
        with self.assertRaises(ContractRefusal):apply(Trial('x',_path('a_'),'add_edge',('a_a','a_b')))
        with self.assertRaises(ContractRefusal):apply(Trial('x',_path('a_'),'remove_edge',('a_a','a_c')))
        with self.assertRaises(ContractRefusal):apply(Trial('x',_path('a_'),'remove_isolate',('a_a',)))
        with self.assertRaises(ContractRefusal):apply(Trial('x',_path('a_'),'leaf',('a_d',)))
        with self.assertRaises(ContractRefusal):trials('private_external_url')

    def test_opaque_encoding_is_permutation_not_named_semantics(self):
        case=trials('train')[0]
        before=statistics(case.source)
        after=statistics(apply(case))
        self.assertEqual(measure(case),tuple((b-a) for i in PERMUTATION
                                                   for a,b in [(before[i],after[i])]))
        self.assertEqual(CHANNELS,('u0','u1','u2','u3','u4'))

    def test_encoding_refuses_invalid_permutation(self):
        with self.assertRaises(ContractRefusal): measure(trials('train')[0],(0,1,2,3,3))
        with self.assertRaises(ContractRefusal): measure(trials('train')[0],(0,1,2,3))

    def test_independent_graph_oracle_recomputes_all_split_readouts(self):
        for split in ('train','validation','test','ood'):
            for case in trials(split):
                self.assertEqual(independently_measure(case),measure(case))
                self.assertEqual(independent_statistics(case.source),statistics(case.source))


class MathematicalDiscoveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.discovery=discover(trials('train'),trials('validation'))

    def test_sequential_experiment_orients_and_asks_another_question(self):
        self.assertEqual(self.discovery.status,'I_UNIQUE_FINITE_LINEAR_CONTRACT')
        self.assertGreaterEqual(self.discovery.inspections,8)
        self.assertTrue(all(e['action']=='EXECUTE_LOCAL_GRAPH_PROBE'
                            for e in self.discovery.receipts[:-1]))
        self.assertEqual(self.discovery.receipts[-1]['action'],'CHECK_FINITE_LINEAR_CONTRACT')
        self.assertEqual(self.discovery.inspections,8)

    def test_discovery_not_given_true_equation_or_target_labels(self):
        import inspect
        from contractdiscovery import discover as learner
        self.assertNotIn('coefficients',inspect.signature(learner).parameters)
        self.assertNotIn('labels',inspect.signature(learner).parameters)
        self.assertNotIn('expected',inspect.signature(learner).parameters)
        self.assertEqual(set(CHANNELS),{f'u{x}' for x in range(5)})

    def test_exact_nontrivial_rank_and_unique_primitive_relation(self):
        self.assertEqual(self.discovery.rank,4)
        self.assertEqual(self.discovery.alternatives,1)
        self.assertEqual(self.discovery.relation,(0,1,1,-1,-1))
        self.assertEqual(sum(v != 0 for v in self.discovery.relation),4)
        self.assertEqual(self.discovery.informative_inspections,4)

    def test_nonidentifiable_pure_original_three_operation_training_refuses(self):
        only=tuple(x for x in trials('train') if x.operation in {'isolated','leaf','subdivide'})
        answer=discover(only,trials('validation'),min_probe_count=3)
        self.assertEqual(answer.status,'HOLD_UNIDENTIFIABLE_CONTRACT')
        self.assertIsNone(answer.relation)
        self.assertLess(answer.rank,4)
        self.assertGreater(answer.alternatives,1)

    def test_repeated_facts_do_not_manufacture_new_rank(self):
        row=measure(trials('train')[0])
        self.assertEqual(rank([row]*100),1)
        self.assertEqual(len(nullspace([row]*100)),4)

    def test_too_low_budget_holds_and_never_builds_relation(self):
        ans=discover(trials('train'),trials('validation'),max_probes=2,min_probe_count=8)
        self.assertEqual(ans.status,'HOLD_INSUFFICIENT_PROBE_BUDGET')
        self.assertIsNone(ans.relation)
        self.assertEqual(ans.inspections,2)

    def test_no_deceptive_early_admission_with_insufficient_probes(self):
        ans=discover(trials('train'),trials('validation'),max_probes=4,min_probe_count=100)
        self.assertIsNone(ans.relation)
        self.assertEqual(ans.status,'HOLD_INSUFFICIENT_PROBE_BUDGET')

    def test_duplicated_or_leaked_splits_refuse(self):
        train=trials('train')
        with self.assertRaisesRegex(ContractRefusal,'HOLD_LEAKED'):
            discover(train,train)
        with self.assertRaisesRegex(ContractRefusal,'HOLD_LEAKED'):
            discover(train[:1]+train[:1],trials('validation'))
        with self.assertRaisesRegex(ContractRefusal,'HOLD_LEAKED'):
            discover((),trials('validation'))

    def test_exact_arithmetic_and_primitive_normalization(self):
        self.assertEqual(primitive((Fraction(-1,2),Fraction(1,2),0,0,0)),(1,-1,0,0,0))
        self.assertEqual(primitive((2,4,0,0,0)),(1,2,0,0,0))
        with self.assertRaises(ContractRefusal): primitive((0,0,0,0,0))
        with self.assertRaises(ContractRefusal): row_reduce(((1,2,3),))

    def test_classical_independent_exhaustive_search_same_result(self):
        readings=(measure(t) for t in trials('train'))
        self.assertEqual(exhaustive_classical_control(readings),(self.discovery.relation,))

    def test_validation_shift_refuses_instead_of_refitting(self):
        from contractdiscovery import measure as honest
        def corrupted(trial, permutation=PERMUTATION):
            x=honest(trial,permutation)
            return (x[0],x[1]+1,*x[2:]) if trial.key.startswith('validation') else x
        with patch('contractdiscovery.measure',side_effect=corrupted):
            answer=discover(trials('train'),trials('validation'))
        self.assertEqual(answer.status,'HOLD_VALIDATION_COUNTEREXAMPLE')
        self.assertIsNone(answer.relation)

    def test_source_training_poison_can_make_relation_unidentifiable(self):
        from contractdiscovery import measure as honest
        def corrupted(trial, permutation=PERMUTATION):
            x=honest(trial,permutation)
            return (x[0],x[1]+1,*x[2:]) if trial.key=='train:0:4' else x
        with patch('contractdiscovery.measure',side_effect=corrupted):
            result=discover(trials('train'),trials('validation'),min_probe_count=20)
        self.assertIn(result.status,{'HOLD_UNIDENTIFIABLE_CONTRACT','HOLD_VALIDATION_COUNTEREXAMPLE'})
        self.assertIsNone(result.relation)

    def test_validated_contract_survives_heldout_new_graphs(self):
        result=test_heldout(self.discovery,trials('test'))
        self.assertEqual(result['worlds'],35)
        self.assertEqual(result['independently_recomputed'],35)
        self.assertEqual(result['relations_hold'],35)
        self.assertEqual(result['status'],'F_LOCAL_EXACT_HOLDOUT')
        self.assertFalse(result['generalization_proved'])

    def test_ood_unseen_operations_survive(self):
        result=test_heldout(self.discovery,trials('ood'))
        self.assertEqual(result['worlds'],48)
        self.assertEqual(result['independently_recomputed'],48)
        self.assertEqual(result['status'],'F_LOCAL_EXACT_HOLDOUT')

    def test_graph_mechanism_not_inferred_from_same_opaque_delta(self):
        p=_path('t_')
        leaf=Trial('leaf',p,'leaf',('t_d','t_a'))
        sub=Trial('sub',p,'subdivide',('t_d','t_a','t_b'))
        self.assertEqual(measure(leaf),measure(sub))
        self.assertNotEqual(apply(leaf).edges,apply(sub).edges)

    def test_type_correct_attack_refuses_nonzero_coordinate(self):
        original=measure(trials('test')[0])
        position=next(i for i,c in enumerate(self.discovery.relation) if c)
        forged=list(original)
        forged[position]+=1
        self.assertTrue(check_relation(self.discovery,original))
        self.assertFalse(check_relation(self.discovery,tuple(forged)))

    def test_unused_channel_corruption_remains_invisible(self):
        original=measure(trials('test')[0]); forged=list(original)
        zero=next(i for i,c in enumerate(self.discovery.relation) if c==0)
        forged[zero]+=999
        self.assertTrue(check_relation(self.discovery,tuple(forged)))
        self.assertNotEqual(original,tuple(forged))

    def test_boolean_and_wrong_length_cannot_pass_as_counts(self):
        original=measure(trials('test')[0]); bad=list(original)
        bad[0]=True
        with self.assertRaises(ContractRefusal):check_relation(self.discovery,tuple(bad))
        with self.assertRaises(ContractRefusal):check_relation(self.discovery,(1,2,3))

    def test_fir_distinguishes_finite_receipt_from_universal_proof(self):
        local=fir_record(self.discovery,test_heldout(self.discovery,trials('test')))
        self.assertEqual(local['local_status'],'F_LOCAL_OBSERVATION')
        self.assertEqual(local['universal_status'],'I_ONLY')
        self.assertEqual([x['operation'] for x in local['receipts']],['propose','propose','admit'])
        self.assertEqual(local['receipts'][-1]['kind'],'finite_computation')
        self.assertTrue(local['receipts'][-1]['scope'].startswith('test:'))


class MissingPortChildTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract=discover(trials('train'),trials('validation'))

    def test_four_channels_can_be_derived_and_fifth_must_hold(self):
        possible=[c for c,v in zip(CHANNELS,self.contract.relation) if v]
        impossible=[c for c,v in zip(CHANNELS,self.contract.relation) if not v]
        self.assertEqual(len(possible),4)
        self.assertEqual(len(impossible),1)
        with self.assertRaisesRegex(ContractRefusal,'NOT_IDENTIFIABLE'):
            MissingPortAdapter(self.contract,impossible[0])
        for missing in possible:
            MissingPortAdapter(self.contract,missing)

    def test_all_four_port_reconstructions_are_correct_on_finite_test(self):
        for case in trials('test'):
            full=measure(case)
            for hidden,coeff in zip(CHANNELS,self.contract.relation):
                if coeff==0:
                    continue
                available={k:full[i] for i,k in enumerate(CHANNELS) if k!=hidden}
                actual=MissingPortAdapter(self.contract,hidden).reconstruct(available)
                self.assertEqual(actual['value'],full[CHANNELS.index(hidden)])
                self.assertEqual(actual['external_actions'],0)

    def test_missing_and_foreign_input_ports_are_rejected(self):
        adapter=MissingPortAdapter(self.contract,'u1')
        with self.assertRaisesRegex(ContractRefusal,'HOLD_TYPED'):
            adapter.reconstruct({'u0':1,'u2':2,'u3':3})
        with self.assertRaisesRegex(ContractRefusal,'HOLD_TYPED'):
            adapter.reconstruct({'u0':1,'u2':2,'u3':3,'u4':4,'eval':'danger'})
        with self.assertRaisesRegex(ContractRefusal,'HOLD_TYPED'):
            adapter.reconstruct({'u0':True,'u2':2,'u3':3,'u4':4})

    def test_refuses_fractional_reconstruction(self):
        forged=replace(self.contract,relation=(2,1,0,0,0))
        adapter=MissingPortAdapter(forged,'u0')
        with self.assertRaisesRegex(ContractRefusal,'NONINTEGER'):
            adapter.reconstruct({'u1':1,'u2':0,'u3':0,'u4':0})

    def test_parent_refuses_forged_discovery_before_build(self):
        fake=replace(self.contract,relation=(1,1,1,1,1))
        with TemporaryDirectory() as path:
            with self.assertRaisesRegex(ContractRefusal,'UNVERIFIED'):
                build_child(ROOT,Path(path),fake)

    def test_generated_child_executes_in_separate_process(self):
        name=next(x for x,c in zip(CHANNELS,self.contract.relation) if c)
        with TemporaryDirectory() as folder:
            child=build_child(ROOT,Path(folder),self.contract)
            result=run_child(child,ROOT,name)
            self.assertEqual(result['status'],'F_LOCAL_REPLAY')
            self.assertEqual(result['derived'],result['observed'])
            self.assertTrue(result['independent_instrument_agrees'])
            self.assertEqual(result['external_actions'],0)

    def test_generated_child_holds_nonidentifiable_port(self):
        name=next(x for x,c in zip(CHANNELS,self.contract.relation) if not c)
        with TemporaryDirectory() as folder:
            child=build_child(ROOT,Path(folder),self.contract)
            self.assertEqual(run_child(child,ROOT,name)['status'],
                             'HOLD_PORT_NOT_IDENTIFIABLE_FROM_CONTRACT')

    def test_child_misses_no_original_source_modified(self):
        hashes_before=pins(ROOT)
        with TemporaryDirectory() as folder:
            child=build_child(ROOT,Path(folder),self.contract)
            self.assertEqual(run_child(child,ROOT,'u1')['status'],'F_LOCAL_REPLAY')
        self.assertEqual(pins(ROOT),hashes_before)

    def test_tampered_child_is_refused(self):
        with TemporaryDirectory() as folder:
            child=build_child(ROOT,Path(folder),self.contract)
            child.write_text(child.read_text()+'\n# hacked\n')
            self.assertEqual(run_child(child,ROOT,'u1')['status'],'HOLD_CHILD_TAMPER')

    def test_upstream_source_drift_is_refused_before_import(self):
        with TemporaryDirectory() as folder:
            temp=Path(folder)
            child=build_child(ROOT,temp,self.contract)
            clean=ROOT/'mathal001'/'nunumathal.py'
            # Copy only the hashed source to another directory; avoid touching root.
            checkout=temp/'checkout'
            for rel,_ in pins(ROOT):
                destination=checkout/rel
                destination.parent.mkdir(parents=True,exist_ok=True)
                copy2(ROOT/rel,destination)
            target=checkout/'mathal001'/'nunumathal.py'
            target.write_text('raise RuntimeError("tampered")\n')
            result=run_child(child,checkout,'u1')
            self.assertEqual(result['status'],'HOLD_SOURCE_DRIFT')

    def test_child_rejects_out_of_bounds_test_index(self):
        with TemporaryDirectory() as folder:
            child=build_child(ROOT,Path(folder),self.contract)
            self.assertEqual(run_child(child,ROOT,'u1',999)['status'],'HOLD_CHILD_INDEX')

    def test_existing_child_is_not_overwritten(self):
        with TemporaryDirectory() as folder:
            build_child(ROOT,Path(folder),self.contract)
            with self.assertRaises(FileExistsError):
                build_child(ROOT,Path(folder),self.contract)

    def test_generated_child_is_deterministic(self):
        with TemporaryDirectory() as a, TemporaryDirectory() as b:
            child1=build_child(ROOT,Path(a),self.contract)
            child2=build_child(ROOT,Path(b),self.contract)
            self.assertEqual(child1.read_bytes(),child2.read_bytes())

    def test_demo_exhibits_discovery_and_adversarial_holds(self):
        d=demonstration(ROOT)
        self.assertTrue(d['classical_brute_force_agrees'])
        self.assertEqual(d['rank'],4)
        self.assertEqual(d['test']['reconstructed_ports_correct'],140)
        self.assertEqual(d['ood_unseen_operations']['reconstructed_ports_correct'],192)
        self.assertEqual(d['underidentified_child']['status'],'HOLD_PORT_NOT_IDENTIFIABLE_FROM_CONTRACT')
        self.assertFalse(d['unrestricted_contract_discovery'])
        self.assertEqual(d['external_actions'],0)


if __name__=='__main__':
    unittest.main()
