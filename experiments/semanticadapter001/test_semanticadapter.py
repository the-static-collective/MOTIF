"""Behavioral and hostile controls for SEMANTIC-ADAPTER-001.

All cases use the existing synthetic simulator, never real-world actions.
"""
from __future__ import annotations
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from shutil import copy2
import inspect
import json
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
for d in ('selfmirror001','adapterinvention001','assemblylab001','003'):
    sys.path.insert(0,str(ROOT/d))
from selfmirror import Policy, Move, preview_motif003
from adapterinvention import Adapter, AdapterRefusal, SEARCH
import semanticadapter as sem
from semanticadapter import (Probe,SemanticRefusal,InferredBridge,
    probes,observe,invent,check,target_contract,utility,independent_actions,
    independent_frontier,adversarial_shift,preview_policy,demonstration,
    build_child,run_child,pins,source_digest)


class SemanticAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.training=probes('train')
        cls.validation=probes('validation')
        cls.test=probes('test')
        cls.ood=probes('ood')
        cls.bridge=invent(cls.training,cls.validation)

    def test_declared_executable_worlds_are_repeatable(self):
        self.assertEqual(probes('train'),probes('train'))
        self.assertEqual(observe(self.test[0]),observe(self.test[0]))

    def test_splits_do_not_reuse_world_names_or_scenes(self):
        a=self.training;b=self.validation;c=self.test
        self.assertFalse({x.name for x in a}&{x.name for x in b})
        self.assertFalse({x.scene for x in b}&{x.scene for x in c})

    def test_behavior_not_target_Move_examples_is_input_to_invention(self):
        self.assertEqual(tuple(inspect.signature(invent).parameters),('training','validation'))
        self.assertTrue(all(isinstance(p,Probe) for p in self.training))
        self.assertFalse(any(hasattr(p,'expected') for p in self.training))

    def test_candidate_search_real_grammar_and_unique_answer(self):
        self.assertEqual(self.bridge.formula_tests,sum(len(v) for v in SEARCH.values()))
        self.assertEqual(tuple(e.op for e in self.bridge.adapter.formulas),
                         ('join_repr','field','length','field','field'))

    def test_local_holdout_reproduces_contract(self):
        result=check(self.bridge,self.test)
        self.assertEqual(result['probe_worlds'],36)
        self.assertEqual(result['correct_outputs'],result['actions'])
        self.assertEqual(result['refused_worlds'],0)
        self.assertEqual(result['status'],'F_LOCAL_FINITE_REPLAY')
        self.assertFalse(result['general_semantics_proved'])

    def test_source_probe_matches_real_MOTIF003_behavior(self):
        from affordance import analyze_first_moves
        from assembly import _possibilities
        p=self.test[0]
        actual=analyze_first_moves(p.scene,{},_possibilities,utility(p.utility_kind),
                                   horizon=p.horizon,max_worlds=p.max_worlds)
        self.assertEqual(tuple(actual),observe(p))

    def test_independent_reachability_is_not_using_003_frontier_function(self):
        p=self.test[0]
        row=observe(p)[0]
        computed=independent_frontier(row['future'],2,1000)
        self.assertEqual(computed,(row['reachable_after_first_move'],row['truncated']))

    def test_exact_novel_action_set_inference(self):
        p=self.test[0]
        teach=next(x for x in observe(p) if x['operator']=='teach')
        before=set(independent_actions(p.scene))
        after=set(independent_actions(teach['future']))
        self.assertEqual(set(teach['new_affordances']),after-before)
        self.assertEqual(target_contract(p,teach)[2],len(after-before))

    def test_interventions_change_utility_and_keep_rule_semantics(self):
        a,b=self.test[0],self.test[1]
        r1=next(x for x in observe(a) if x['operator']=='teach')
        r2=next(x for x in observe(b) if x['operator']=='teach')
        self.assertNotEqual(r1['immediate_delta'],r2['immediate_delta'])
        self.assertEqual(r1['reachable_after_first_move'],r2['reachable_after_first_move'])

    def test_small_frontier_budget_produces_truncated_bool_probes(self):
        values=[r['truncated'] for p in self.training for r in observe(p)]
        self.assertTrue(any(values))
        self.assertTrue(any(not b for b in values))

    def test_pure_false_truncation_mapping_is_distinguished(self):
        self.assertEqual(self.bridge.adapter.formulas[-1].op,'field')
        self.assertEqual(self.bridge.adapter.formulas[-1].args,('truncated',))

    def test_result_is_real_selfmirror_Move_class(self):
        p=self.test[0]
        moves=self.bridge.convert(p)
        self.assertTrue(all(isinstance(m,Move) for m in moves))
        self.assertEqual(len(moves),len(observe(p)))

    def test_downstream_policy_choice_matches_strong_manual_baseline(self):
        matched=0
        for p in self.test:
            rows=observe(p)
            if any(r['truncated'] for r in rows):
                continue
            moves=self.bridge.convert(p,rows)
            for policy in (Policy(0,0),Policy(2,1)):
                proposed=moves[policy.choose(moves)].name
                self.assertEqual(proposed,preview_motif003(list(rows),policy)['selection'])
                matched+=1
        self.assertGreater(matched,10)

    def test_preview_with_truncated_frontier_holds_instead_of_guess(self):
        p=next(p for p in self.test if any(r['truncated'] for r in observe(p)))
        result=preview_policy(self.bridge,p,Policy(2,1))
        self.assertEqual(result['status'],'HOLD_INCOMPLETE_FRONTIER')
        self.assertIsNone(result['choice'])

    def test_source_mismatch_is_refused_with_actual_trace(self):
        p=self.test[0]
        wrong=dict(observe(p)[0],future=frozenset({('state','fake')}))
        with self.assertRaisesRegex(SemanticRefusal,'HOLD_INVALID_ACTION_TRACE'):
            target_contract(p,wrong)

    def test_type_preserving_immediate_reach_swap_refused(self):
        p=self.test[0]
        row=observe(p)[0]
        self.assertNotEqual(row['immediate_delta'],row['reachable_after_first_move'])
        result=adversarial_shift(self.bridge,p,row)
        self.assertTrue(result['typed_only_accepts'])
        self.assertEqual(result['semantic_gate'],'HOLD_SEMANTIC_DRIFT')

    def test_wrong_new_affordance_identity_refused_even_if_length_same(self):
        p=self.test[0]
        row=next(r for r in observe(p) if r['new_affordances'])
        changed=dict(row,new_affordances=(('false','action'),)+row['new_affordances'][1:])
        with self.assertRaisesRegex(SemanticRefusal,'HOLD_SEMANTIC_DRIFT'):
            self.bridge.convert(p,(changed,))

    def test_wrong_new_skill_receipt_refused(self):
        p=self.test[0]
        row=next(r for r in observe(p) if r['operator']=='teach')
        changed=dict(row,new_skill_facts=())
        with self.assertRaisesRegex(SemanticRefusal,'HOLD_SEMANTIC_DRIFT'):
            self.bridge.convert(p,(changed,))

    def test_misleading_name_or_roles_refused(self):
        p=self.test[0]
        row=observe(p)[0]
        for key,value in (('operator','unknown'),('roles',('not','the','same'))):
            with self.subTest(key=key):
                changed=dict(row,**{key:value})
                with self.assertRaises(SemanticRefusal):
                    self.bridge.convert(p,(changed,))

    def test_false_truncation_refused_even_same_schema(self):
        p=next(p for p in self.test if any(r['truncated'] for r in observe(p)))
        row=next(r for r in observe(p) if r['truncated'])
        with self.assertRaisesRegex(SemanticRefusal,'HOLD_SEMANTIC_DRIFT'):
            self.bridge.convert(p,(dict(row,truncated=False),))

    def test_missing_source_field_refused(self):
        p=self.test[0]
        changed=dict(observe(p)[0])
        changed.pop('immediate_delta')
        with self.assertRaises(SemanticRefusal):
            self.bridge.convert(p,(changed,))

    def test_duplicate_action_ids_refused(self):
        p=self.test[0]
        row=observe(p)[0]
        with self.assertRaises(AdapterRefusal):
            self.bridge.convert(p,(row,row.copy()))

    def test_insufficient_or_repeated_probes_refused(self):
        with self.assertRaisesRegex(SemanticRefusal,'HOLD_TOO_FEW'):
            invent(self.training[:2],self.validation)
        with self.assertRaisesRegex(SemanticRefusal,'HOLD_LEAKED_PROBES'):
            invent(self.training,self.training)

    def test_unknown_utility_or_split_cannot_run(self):
        with self.assertRaises(SemanticRefusal):probes('user')
        with self.assertRaises(SemanticRefusal):utility('shell')
        with self.assertRaises(SemanticRefusal):Probe('x',frozenset(), 'hack')

    def test_poorly_separated_probe_family_causes_abstention(self):
        # All worlds use one fixed utility and only one state; there is no
        # information to distinguish some interchangeable expressions.
        with self.assertRaisesRegex(SemanticRefusal,'HOLD_AMBIGUOUS_SEMANTIC_MAPPING'):
            invent(tuple(replace(p, scene=self.training[0].scene,
                                 utility_kind='base',max_worlds=1000) for p in self.training),
                   tuple(replace(p, scene=self.validation[0].scene,
                                 utility_kind='base',max_worlds=1000) for p in self.validation))

    def test_learned_adapter_does_not_claim_proof_of_general_semantics(self):
        self.assertEqual(self.bridge.status,'I_SYNTHESIZED_BEHAVIORAL_CONTRACT')
        self.assertNotIn('FACT',self.bridge.status)

    def test_semantic_checks_depend_on_declared_simulator_not_external_truth(self):
        # An agreed-but-wrong executable world is still internally consistent.
        # This test deliberately does not claim detection of a common-mode bug.
        p=self.test[0]
        self.assertTrue(target_contract(p,observe(p)[0]))
        self.assertEqual(preview_policy(self.bridge,p,Policy(2,1))['external_actions'],0)

    def test_source_pins_include_upstream_and_downstream(self):
        records=pins(ROOT)
        files={p for p,_ in records}
        self.assertIn('003/affordance.py',files)
        self.assertIn('selfmirror001/selfmirror.py',files)
        self.assertIn('semanticadapter001/semanticadapter.py',files)
        self.assertGreaterEqual(len(records),7)

    def test_reject_missing_or_linked_source_at_pin_time(self):
        with TemporaryDirectory() as d:
            root=Path(d)
            for rel,_ in pins(ROOT):
                path=root/rel
                path.parent.mkdir(parents=True,exist_ok=True)
                copy2(ROOT/rel,path)
            (root/'003'/'affordance.py').unlink()
            with self.assertRaises(SemanticRefusal):pins(root)
            (root/'003'/'affordance.py').symlink_to(ROOT/'003'/'affordance.py')
            with self.assertRaises(SemanticRefusal):pins(root)

    def test_generated_child_runs_real_policy_in_separate_process(self):
        with TemporaryDirectory() as d:
            child=build_child(ROOT,Path(d),self.bridge)
            result=run_child(child,ROOT,0)
            self.assertEqual(result['status'],'I_VERIFIED_LOCAL_PROPOSAL')
            self.assertEqual(result['source_hashes_verified'],len(pins(ROOT)))
            self.assertTrue(result['choice'])
            self.assertEqual(result['external_actions'],0)
            self.assertEqual(result['automatic_code_edits'],0)

    def test_generated_child_source_is_fixed_not_user_python(self):
        with TemporaryDirectory() as d:
            child=build_child(ROOT,Path(d),self.bridge)
            text=child.read_text()
            self.assertNotIn('eval(',text)
            self.assertNotIn('exec(',text)
            self.assertNotIn('requests',text)
            with self.assertRaises(FileExistsError):build_child(ROOT,Path(d),self.bridge)

    def test_generated_child_tampering_refused(self):
        with TemporaryDirectory() as d:
            child=build_child(ROOT,Path(d),self.bridge)
            with child.open('a') as f:f.write('#changed\n')
            self.assertEqual(run_child(child,ROOT,0)['status'],'HOLD_CHILD_DIGEST_DRIFT')

    def test_generated_child_pin_catches_source_drift_before_import(self):
        with TemporaryDirectory() as d:
            child=build_child(ROOT,Path(d),self.bridge)
            with TemporaryDirectory() as copy_root:
                root=Path(copy_root)
                for rel,_ in pins(ROOT):
                    out=root/rel
                    out.parent.mkdir(parents=True,exist_ok=True)
                    copy2(ROOT/rel,out)
                (root/'003'/'affordance.py').write_text('raise RuntimeError("poisoned")\n')
                result=run_child(child,root,0)
                self.assertEqual(result['status'],'HOLD_SOURCE_DRIFT')

    def test_invalid_probe_index_refused(self):
        with TemporaryDirectory() as d:
            child=build_child(ROOT,Path(d),self.bridge)
            self.assertEqual(run_child(child,ROOT,999)['status'],'HOLD_INVALID_PROBE_INDEX')

    def test_replay_deterministic_and_outputs_expected_structure(self):
        one=demonstration()
        two=demonstration()
        self.assertEqual(one,two)
        self.assertEqual(one['experiment'],'SEMANTIC-ADAPTER-001')
        self.assertFalse(one['general_algorithm_invention'])

    def test_benchmark_exposes_fixed_typed_baseline_limitation(self):
        p=self.test[0]
        row=observe(p)[0]
        shifted=dict(row,immediate_delta=row['reachable_after_first_move'],
                     reachable_after_first_move=row['immediate_delta'])
        self.assertIsInstance(self.bridge.adapter.transform([shifted])[0],Move)
        with self.assertRaises(SemanticRefusal):target_contract(p,shifted)


if __name__=='__main__':unittest.main()
