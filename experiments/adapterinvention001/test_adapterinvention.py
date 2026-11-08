"""Hostile and independently held-out controls for limited adapter synthesis."""
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
from shutil import copy2
import json
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'selfmirror001'))
from selfmirror import Move,Policy,preview_motif003
from adapterinvention import (Adapter,AdapterRefusal,Expression,Example,OUTPUTS,
    SEARCH,check,create_child,demonstration,digest,invent,missing_port_report,
    run_child,trusted_fixture,validate_row)


class AdapterInventionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.training=trusted_fixture('train',64)
        cls.validation=trusted_fixture('validation',64)
        cls.test=trusted_fixture('test',100)
        cls.adapter=invent(cls.training,cls.validation)

    def test_synthesis_is_reproducible_and_bounded(self):
        self.assertEqual(self.adapter,invent(self.training,self.validation))
        self.assertLessEqual(self.adapter.examined,40)
        self.assertGreater(self.adapter.examined,0)
        self.assertEqual(len(self.adapter.formulas),5)

    def test_derived_rules_are_not_supplied_as_the_answer(self):
        # The grammar contains alternatives. The learned mapping is not passed to invent().
        self.assertGreater(len(SEARCH['name']),1)
        self.assertGreater(len(SEARCH['affordances']),1)
        self.assertGreater(len(SEARCH['truncated']),1)
        self.assertEqual(tuple(x.op for x in self.adapter.formulas),
                         ('join_repr','field','length','field','field'))

    def test_hidden_examples_are_only_used_after_freeze(self):
        r=check(self.adapter,self.test)
        self.assertEqual(r['tested'],100)
        self.assertEqual(r['matched'],100)
        self.assertEqual(r['failed'],())
        self.assertEqual(r['status'],'F_LOCAL_CONTRACT_REPLAY')
        self.assertFalse(r['generalization_claim'])

    def test_training_and_validation_are_distinct(self):
        self.assertEqual(len({digest(x) for x in
            (self.training,self.validation,self.test,trusted_fixture('ood'))}),4)
        self.assertFalse(set(x.key for x in self.training) & set(x.key for x in self.validation))
        self.assertFalse(set(x.key for x in self.test) & set(x.key for x in self.training))

    def test_fewer_than_declared_examples_holds(self):
        with self.assertRaisesRegex(AdapterRefusal,'SUPERVISION'):
            invent(self.training[:11],self.validation)
        with self.assertRaisesRegex(AdapterRefusal,'SUPERVISION'):
            invent(self.training,self.validation[:11])

    def test_reused_examples_are_refused(self):
        with self.assertRaisesRegex(AdapterRefusal,'LEAKED_SPLIT'):
            invent(self.training,self.training)
        with self.assertRaisesRegex(AdapterRefusal,'LEAKED_SPLIT'):
            invent(self.training[:1]*12,self.validation)

    def test_supervision_error_refuses_adapter_not_best_guess(self):
        corrupted=tuple(replace(e,expected=(e.expected[0]+'Z',)+e.expected[1:])
                        for e in self.validation)
        with self.assertRaisesRegex(AdapterRefusal,'NO_UNIQUE_ADAPTER:name'):
            invent(self.training,corrupted)

    def test_ambiguous_constant_false_input_refuses(self):
        base=tuple(replace(e,row={**e.row,'truncated':False},
                           expected=e.expected[:-1]+(False,)) for e in self.training)
        valid=tuple(replace(e,row={**e.row,'truncated':False},
                            expected=e.expected[:-1]+(False,)) for e in self.validation)
        with self.assertRaisesRegex(AdapterRefusal,'NO_UNIQUE_ADAPTER:truncated'):
            invent(base,valid)

    def test_absent_source_field_refused(self):
        row=dict(self.test[0].row)
        del row['new_affordances']
        with self.assertRaisesRegex(AdapterRefusal,'SOURCE_SCHEMA'):
            self.adapter.transform([row])

    def test_wrong_source_types_refused(self):
        row=dict(self.test[0].row)
        for field,value in [('roles','not-tuple'),('immediate_delta',False),
                            ('reachable_after_first_move',-1),('truncated',0),
                            ('new_skill_facts',[]),('operator','')]:
            bad=dict(row,**{field:value})
            with self.subTest(field=field),self.assertRaisesRegex(AdapterRefusal,'SOURCE_SCHEMA'):
                self.adapter.transform([bad])

    def test_empty_or_invalid_batch_holds(self):
        with self.assertRaisesRegex(AdapterRefusal,'EMPTY_SOURCE'):
            self.adapter.transform([])
        with self.assertRaisesRegex(AdapterRefusal,'SOURCE_SCHEMA'):
            self.adapter.transform(['not-a-row'])

    def test_aliasing_names_are_refused_not_counted_twice(self):
        row=dict(self.test[0].row,truncated=False)
        with self.assertRaisesRegex(AdapterRefusal,'ALIASING_ACTION_IDENTITIES'):
            self.adapter.transform([row,row.copy()])

    def test_joined_identity_distinguishes_same_operator_different_roles(self):
        a=dict(self.test[0].row,operator='repair',roles=('worker','bike'),truncated=False)
        b=dict(a,roles=('worker','house'))
        moves=self.adapter.transform([a,b])
        self.assertNotEqual(moves[0].name,moves[1].name)
        self.assertEqual({m.name for m in moves},{"repair:('worker', 'bike')","repair:('worker', 'house')"})

    def test_truncated_frontier_survives_adapter(self):
        x=dict(self.test[0].row,truncated=True)
        move=self.adapter.transform([x])[0]
        self.assertTrue(move.truncated)
        with self.assertRaises(ValueError):Policy(2,1).choose((move,))

    def test_real_selfmirror_policy_receives_typed_moves(self):
        data=[dict(e.row,truncated=False) for e in self.test[:5]]
        # Disambiguate the deliberately reusable action names.
        for i,row in enumerate(data):row['roles']=('worker',f'bike{i}')
        moves=self.adapter.transform(data)
        self.assertTrue(all(isinstance(m,Move) for m in moves))
        selected=moves[Policy(2,1).choose(moves)].name
        hand=preview_motif003(data,Policy(2,1))
        self.assertEqual(hand['selection'],selected)
        self.assertEqual(hand['status'],'I')

    def test_real_context_gate_accepts_generated_move(self):
        sys.path.insert(0,str(ROOT/'contextgate001'))
        from contextgate import train_gate,generate
        gate=train_gate(generate('train',240),12,.5)
        rows=[dict(e.row,truncated=False) for e in self.test[:3]]
        for i,row in enumerate(rows):row['roles']=('worker',f'b{i}')
        result=gate.choose('amber',self.adapter.transform(rows))
        self.assertEqual(result.status,'I_PROPOSAL_ONLY')
        self.assertIn(result.selected,{f"{r['operator']}:{r['roles']!r}" for r in rows})

    def test_grammar_rejects_unlisted_expression_or_injected_code(self):
        for op,args in [('exec',('code',)),('field',('__class__',)),
                        ('length',('operator',)),('join_repr',('operator','__dict__'))]:
            with self.assertRaises(AdapterRefusal):Expression(op,args)

    def test_runtime_rejects_foreign_formula(self):
        other=replace(self.adapter,formulas=(Expression('field',('operator',)),)+self.adapter.formulas[1:])
        self.assertNotEqual(check(other,self.test)['status'],'F_LOCAL_CONTRACT_REPLAY')
        with self.assertRaises(AdapterRefusal):
            replace(self.adapter,formulas=(Expression('field',('roles',)),)+self.adapter.formulas[1:])

    def test_split_perturbation_does_not_retune_frozen_adapter(self):
        bad=tuple(replace(e,expected=(e.expected[0]+'X',)+e.expected[1:]) for e in self.test)
        self.assertNotEqual(check(self.adapter,bad)['matched'],len(bad))
        self.assertEqual(self.adapter,invent(self.training,self.validation))

    def test_typed_source_and_target_are_explicit(self):
        report=missing_port_report()
        self.assertEqual(report['direct_connection'],'HOLD_INCOMPATIBLE_PORTS')
        self.assertIn('Move',report['target'])
        self.assertEqual(report['pre_existing_manual_bridge'],'selfmirror.preview_motif003')

    def test_child_is_generated_in_requested_directory(self):
        with TemporaryDirectory() as tmp:
            child=create_child(ROOT,Path(tmp),self.adapter)
            self.assertTrue(child.is_file())
            self.assertNotIn('eval(',child.read_text())
            self.assertNotIn('subprocess.run',child.read_text())
            with self.assertRaises(FileExistsError):create_child(ROOT,Path(tmp),self.adapter)

    def test_child_executes_real_policy_in_independent_interpreter(self):
        with TemporaryDirectory() as tmp:
            child=create_child(ROOT,Path(tmp),self.adapter)
            batch=[dict(e.row,truncated=False) for e in self.test[:4]]
            for i,row in enumerate(batch):row['roles']=('worker',f'device{i}')
            result=run_child(child,ROOT,batch)
            self.assertEqual(result['status'],'I_VALIDATED_ADAPTER_OUTPUT')
            self.assertEqual(result['external_actions'],0)
            self.assertEqual(result['code_edits'],0)
            expected=self.adapter.transform(batch)
            self.assertEqual(result['choice'],expected[Policy(2,1).choose(expected)].name)

    def test_child_holds_when_a_move_is_truncated(self):
        with TemporaryDirectory() as tmp:
            child=create_child(ROOT,Path(tmp),self.adapter)
            result=run_child(child,ROOT,[dict(self.test[0].row,truncated=True)])
            self.assertEqual(result['status'],'HOLD_INCOMPLETE_FRONTIER')
            self.assertIsNone(result['choice'])

    def test_child_refuses_schema_drift(self):
        with TemporaryDirectory() as tmp:
            child=create_child(ROOT,Path(tmp),self.adapter)
            result=run_child(child,ROOT,[{'operator':'A'}])
            self.assertEqual(result['status'],'HOLD_INVALID_INPUT_OR_ADAPTER')

    def test_child_detects_upstream_source_drift(self):
        with TemporaryDirectory() as temp:
            tmp=Path(temp)
            (tmp/'selfmirror001').mkdir()
            source=ROOT/'selfmirror001'/'selfmirror.py'
            copy2(source,tmp/'selfmirror001'/'selfmirror.py')
            # child uses trusted installed adapterinvention module from root;
            # source check happens BEFORE any real downstream import.
            child=create_child(ROOT,tmp/'child',self.adapter)
            (tmp/'selfmirror001'/'selfmirror.py').write_text('raise RuntimeError("altered")')
            r=run_child(child,tmp,[self.test[0].row])
            self.assertEqual(r['status'],'HOLD_UPSTREAM_SOURCE_DRIFT')

    def test_generated_child_tamper_detected_before_launch(self):
        with TemporaryDirectory() as tmp:
            child=create_child(ROOT,Path(tmp),self.adapter)
            with child.open('a',encoding='utf8') as out:
                out.write('\n# changed since emission\n')
            result=run_child(child,ROOT,[self.test[0].row])
            self.assertEqual(result['status'],'HOLD_GENERATED_CHILD_DRIFT')

    def test_generated_child_receipt_missing_is_a_hold(self):
        with TemporaryDirectory() as tmp:
            child=create_child(ROOT,Path(tmp),self.adapter)
            child.with_suffix('.sha256').unlink()
            result=run_child(child,ROOT,[self.test[0].row])
            self.assertEqual(result['status'],'HOLD_GENERATED_CHILD_DRIFT')

    def test_upstream_adapter_code_is_pinned_as_well(self):
        with TemporaryDirectory() as temp:
            tmp=Path(temp)
            for name in ('selfmirror001','adapterinvention001'):
                (tmp/name).mkdir()
                source=ROOT/name/('selfmirror.py' if name=='selfmirror001' else 'adapterinvention.py')
                copy2(source,tmp/name/source.name)
            child=create_child(ROOT,tmp/'child',self.adapter)
            (tmp/'adapterinvention001'/'adapterinvention.py').write_text('raise RuntimeError("altered")')
            r=run_child(child,tmp,[self.test[0].row])
            self.assertEqual(r['status'],'HOLD_UPSTREAM_SOURCE_DRIFT')

    def test_semantic_shift_is_a_documented_failure(self):
        original=next(e for e in self.test if e.row['immediate_delta']>=0
                      and e.row['immediate_delta']!=e.row['reachable_after_first_move'])
        swapped=dict(original.row,immediate_delta=original.row['reachable_after_first_move'],
                     reachable_after_first_move=original.row['immediate_delta'])
        move=self.adapter.transform([swapped])[0]
        self.assertNotEqual(move.immediate,original.expected[1])
        self.assertNotEqual(move.reach,original.expected[3])

    def test_child_missing_link_or_refused_source(self):
        with TemporaryDirectory() as tmp:
            missing=Path(tmp)/'missing.py'
            self.assertEqual(run_child(missing,ROOT,[self.test[0].row])['status'],
                             'HOLD_CHILD_MISSING_OR_LINKED')
            link=Path(tmp)/'alias.py'
            link.symlink_to(ROOT/'adapterinvention001'/'adapterinvention.py')
            self.assertEqual(run_child(link,ROOT,[self.test[0].row])['status'],
                             'HOLD_CHILD_MISSING_OR_LINKED')

    def test_generated_code_is_deterministic(self):
        with TemporaryDirectory() as a,TemporaryDirectory() as b:
            x=create_child(ROOT,Path(a),self.adapter)
            y=create_child(ROOT,Path(b),self.adapter)
            self.assertEqual(x.read_bytes(),y.read_bytes())

    def test_end_to_end_question_to_verified_code_and_new_question(self):
        result=demonstration(ROOT)
        self.assertEqual(result['experiment'],'ADAPTER-INVENTION-001')
        self.assertEqual(result['finite_test']['matched'],100)
        self.assertEqual(result['generated_child']['status'],'I_VALIDATED_ADAPTER_OUTPUT')
        self.assertIn('less supervision',result['next_question'])
        self.assertEqual(result['automatic_repo_writes'],0)

    def test_actual_motif003_graph_frontier_when_checkout_available(self):
        if not (ROOT/'003'/'affordance.py').exists():
            self.skipTest('real MOTIF-003 only in full GitHub checkout')
        sys.path.insert(0,str(ROOT/'003'))
        sys.path.insert(0,str(ROOT/'assemblylab001'))
        from affordance import analyze_first_moves
        from assembly import _possibilities,_utility
        scene=frozenset({('need','repair'),('resource','scrap')})
        rows=analyze_first_moves(scene,{},_possibilities,_utility,horizon=3)
        adapted=self.adapter.transform(rows)
        self.assertEqual(len(adapted),2)
        self.assertEqual({m.name for m in adapted},
                         {f"{r['operator']}:{tuple(r['roles'])!r}" for r in rows})
        for policy in (Policy(0,0),Policy(2,1)):
            self.assertEqual(adapted[policy.choose(adapted)].name,
                             preview_motif003(rows,policy)['selection'])


if __name__=='__main__':unittest.main()
