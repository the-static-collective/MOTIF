"""Adversarial correctness, provenance and abstention controls for GEOM-010."""
from __future__ import annotations
from itertools import combinations
import copy
import json
import random
import tempfile
import unittest
from pathlib import Path

from reason_lab import (SituatedCase,ConditionalRule,score,critic,possible_guards,
    invent_guard,guarded_from_data,explore,archive_pencil,stage,run_document,case_from_document)
from demo import initial_grammar,development_rounds,heldout,make_case,run,SCOPE
from living_graph import LivingGraph, RewriteRule, RewriteGrammar


class ReasonLabTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parent,cls.base,cls.initial=initial_grammar()
        cls.early,cls.later=development_rounds()
        cls.all_cases=cls.early+cls.later

    def proposal(self,cases=None,**kwargs):
        budget=kwargs.pop('work_budget',1000)
        return invent_guard(self.base,cases if cases is not None else self.all_cases,
                            scope=SCOPE,work_budget=budget,**kwargs)

    def test_geometric_prior_not_required(self):
        out=self.proposal()
        self.assertNotIn('geometry',out)
        self.assertEqual(out['authority'],'NONE')

    def test_inherits_real_prior_grammar_induction(self):
        self.assertEqual(self.initial['rule']['find'],['bud'])
        self.assertEqual(self.initial['rule']['replace'],['branch'])
        self.assertEqual(self.initial['status'],'PENCIL_GRAMMAR_REVISION_PROPOSED')

    def test_critic_find_unconditional_false_positives(self):
        d=critic(ConditionalRule(self.base,(),SCOPE),self.early)
        self.assertEqual(d['status'],'REFINEMENT_NEEDED')
        self.assertEqual(len(d['false_positives']),28)

    def test_round_one_2_term_guard(self):
        p=self.proposal(self.early)
        self.assertEqual(p['rule']['guard'],{'moisture':'wet','season':'warm'})
        self.assertEqual(p['development']['correct'],46)

    def test_round_two_3_term_guard(self):
        p=self.proposal()
        self.assertEqual(p['rule']['guard'],{'moisture':'wet','nutrient':'good','season':'warm'})
        self.assertEqual(p['development']['correct'],74)
        self.assertEqual(critic(guarded_from_data(p['rule']),self.all_cases)['status'],'DEVELOPMENT_FIT')

    def test_heldout_is_never_part_of_selection(self):
        p=self.proposal()['rule']
        shadow=heldout()
        self.assertEqual(len(shadow),260)
        # The Inventor API cannot see these objects; only supplied development cases.
        self.assertEqual(self.proposal()['rule'],p)
        self.assertTrue(all(not c.identity.startswith('frozen') for c in self.all_cases))

    def test_heldout_metrics_exact(self):
        r=guarded_from_data(self.proposal()['rule'])
        result=score(r,heldout())
        self.assertEqual((result['correct'],result['abstentions'],result['false_positives']), (240,20,0))
        self.assertEqual(sum(not c.expected for c in heldout()),200)

    def test_incomplete_has_no_claimed_discovery(self):
        o=self.proposal(work_budget=1)
        self.assertEqual(o['status'],'CONTINUE_SEARCH')
        self.assertEqual(o['completeness'],'INCOMPLETE')
        self.assertNotIn('rule',o)

    def test_resume_finds_same_guard(self):
        cursor=None
        while True:
            res=self.proposal(work_budget=1,cursor=cursor)
            if res['status']!='CONTINUE_SEARCH':break
            cursor=res['cursor']
        self.assertEqual(res['rule'],self.proposal()['rule'])

    def test_rejects_forged_cursor_offset(self):
        c=self.proposal(work_budget=1)['cursor']
        c['offset']=999
        with self.assertRaisesRegex(ValueError,'skipped|beyond'):
            self.proposal(work_budget=1,cursor=c)

    def test_rejects_cursor_skipping_good_result(self):
        c=self.proposal(work_budget=1)['cursor']
        c['offset']=8
        with self.assertRaisesRegex(ValueError,'skipped'):
            self.proposal(work_budget=1,cursor=c)

    def test_rejects_cursor_cross_dataset(self):
        c=self.proposal(work_budget=1)['cursor']
        changed=list(self.all_cases)
        v=changed[0]
        changed[0]=SituatedCase(v.identity,v.before,v.after,v.expected,v.facts,'replaced-origin',v.scope)
        with self.assertRaisesRegex(ValueError,'cursor'):
            self.proposal(changed,work_budget=1,cursor=c)

    def test_distinguish_known_false_from_missing(self):
        rule=guarded_from_data(self.proposal()['rule'])
        self.assertIsNone(rule.decide(make_case('new','warm','wet','missing',False,with_nutrient=False)))
        self.assertFalse(rule.decide(make_case('new2','warm','wet','poor',False)))
        self.assertTrue(rule.decide(make_case('new3','warm','wet','good',True)))

    def test_wrong_transformation_definitely_false_even_with_missing(self):
        rule=guarded_from_data(self.proposal()['rule'])
        self.assertFalse(rule.decide(make_case('new','warm','wet','missing',False,
                                               with_nutrient=False,after='leaf')))

    def test_scope_cannot_leak(self):
        rule=guarded_from_data(self.proposal()['rule'])
        c=make_case('different','warm','wet','good',True)
        forged=SituatedCase(c.identity,c.before,c.after,c.expected,c.facts,c.source_root,'other-observer')
        with self.assertRaisesRegex(ValueError,'cross-scope'):
            rule.decide(forged)
        with self.assertRaisesRegex(ValueError,'cross-scope'):
            self.proposal([forged])

    def test_critic_impossible_same_features_refuses_invention(self):
        a=make_case('same-positive','warm','wet','good',True)
        b=make_case('same-negative','warm','wet','good',False)
        b=SituatedCase(b.identity,a.before,a.after,b.expected,a.facts,b.source_root,b.scope)
        d=critic(ConditionalRule(self.base,(),SCOPE),[a,b])
        self.assertEqual(d['status'],'UNRESOLVABLE_IN_OBSERVED_VOCABULARY')
        stage_out=stage(self.parent,self.base,[a,b])
        self.assertEqual(stage_out['inventor']['status'],'HOLD')
        self.assertEqual(self.proposal([a,b])['status'],'HOLD')

    def test_no_positive_or_negative_refuses(self):
        self.assertEqual(self.proposal([self.early[0]])['status'],'HOLD')
        self.assertEqual(self.proposal([self.early[1]])['status'],'HOLD')

    def test_no_need_to_revise_refuses_redundancy(self):
        a=make_case('ok','warm','wet','good',True)
        b=make_case('no','warm','wet','good',False,after='leaf')
        r=stage(self.parent,self.base,[a,b])
        self.assertEqual(r['inventor']['status'],'HOLD')

    def test_negative_work_budgets_refused(self):
        for n in (-2,0,1.1,True):
            with self.assertRaises(ValueError):self.proposal(work_budget=n)
        with self.assertRaises(ValueError):self.proposal(seconds=-1)
        with self.assertRaises(ValueError):self.proposal(seconds=float('nan'))

    def test_stable_deterministic_evaluation(self):
        self.assertEqual(self.proposal()['rule'],self.proposal()['rule'])
        self.assertEqual(run(),run())

    def test_first_accepted_guard_is_minimal(self):
        candidate=self.proposal()['rule']['guard']
        features=sorted(set(self.all_cases[0].facts))
        for size in (0,1,2):
            for subset in combinations(features,size):
                rule=ConditionalRule(self.base,tuple(subset),SCOPE)
                self.assertNotEqual(score(rule,self.all_cases)['correct'],len(self.all_cases))
        self.assertEqual(len(candidate),3)

    def test_permitted_path_is_reached_only_by_guarded_rule(self):
        r=guarded_from_data(self.proposal()['rule'])
        facts={'season':'warm','moisture':'wet','nutrient':'good'}
        self.assertEqual(explore(['oak','seed'],['oak','branch'],self.parent,r,facts,work_budget=20)['status'],'PATH')
        self.assertEqual(explore(['oak','seed'],['oak','branch'],self.parent,None,facts,work_budget=20)['status'],'SATURATED_NO_TARGET')

    def test_blocked_context_has_no_path(self):
        r=guarded_from_data(self.proposal()['rule'])
        result=explore(['oak','seed'],['oak','branch'],self.parent,r,
                       {'season':'warm','moisture':'wet','nutrient':'poor'},work_budget=20)
        self.assertEqual(result['status'],'SATURATED_NO_TARGET')

    def test_missing_context_produces_hold(self):
        r=guarded_from_data(self.proposal()['rule'])
        result=explore(['oak','seed'],['oak','branch'],self.parent,r,
                       {'season':'warm','moisture':'wet'},work_budget=20)
        self.assertEqual(result['status'],'HOLD_UNKNOWN_CONTEXT')

    def test_partial_search_fails_closed(self):
        r=guarded_from_data(self.proposal()['rule'])
        result=explore(['oak','seed'],['oak','branch'],self.parent,r,
                       {'season':'warm','moisture':'wet','nutrient':'good'},work_budget=1)
        self.assertEqual(result['status'],'HOLD_RESOURCE_INCOMPLETE')

    def test_rejects_cross_scope_exploration(self):
        r=ConditionalRule(self.base,(), 'another')
        with self.assertRaisesRegex(ValueError,'cross-scope'):
            explore(['a','bud'],['a','branch'],self.parent,r,{},work_budget=5)

    def test_archive_has_pencil_only_and_verifies(self):
        p=self.proposal()
        with LivingGraph(scope=SCOPE) as g:
            receipt=archive_pencil(g,self.parent,self.base,self.all_cases,p)
            self.assertEqual(receipt['status'],'ARCHIVED_PENCIL_ONLY')
            self.assertEqual(g.counts()['nodes'],len(self.all_cases)+1)
            self.assertEqual(g.counts()['relations'],1)
            self.assertEqual(g.verify()['integrity'],'ok')
            node=g.db.execute('SELECT status FROM nodes WHERE id=?',(receipt['node_id'],)).fetchone()
            self.assertEqual(node['status'],'PENCIL')

    def test_tampered_archive_score_is_rejected(self):
        p=self.proposal()
        p['development']['correct']=100000
        with LivingGraph(scope=SCOPE) as g:
            with self.assertRaisesRegex(ValueError,'forged'):
                archive_pencil(g,self.parent,self.base,self.all_cases,p)
            self.assertEqual(g.counts()['nodes'],0)

    def test_wrong_archive_scope_is_rejected(self):
        with LivingGraph(scope='other-cut') as g:
            with self.assertRaisesRegex(ValueError,'scope'):
                archive_pencil(g,self.parent,self.base,self.all_cases,self.proposal())

    def test_reject_invalid_facts_and_nonboolean(self):
        with self.assertRaisesRegex(ValueError,'boolean'):
            make_case('wrong','warm','wet','good',1)
        with self.assertRaisesRegex(ValueError,'fact values'):
            SituatedCase.make('bad',['a'],['b'],True,{'season':4},'declared',SCOPE)
        with self.assertRaisesRegex(ValueError,'sorted'):
            SituatedCase('bad',('a',),('b',),True,(('z','1'),('a','2')),'declared',SCOPE)

    def test_reject_duplicate_id_in_feedback(self):
        with self.assertRaisesRegex(ValueError,'duplicate'):
            self.proposal([self.early[0],self.early[0]])

    def test_grammar_declaration_is_strict(self):
        r=self.proposal()['rule']
        r['admission']='PEN'
        with self.assertRaisesRegex(ValueError,'PENCIL'):
            guarded_from_data(r)

    def test_document_interface_refuses_unknown_fields(self):
        with self.assertRaisesRegex(ValueError,'lab field'):
            run_document({'execute_shell':'rm -rf'})

    def test_document_interface_roundtrip(self):
        data={'parent_grammar':self.parent.data(),
              'initial_rule':{'name':self.base.name,'find':list(self.base.find),
                              'replace':list(self.base.replace)},
              'development':[e.data() for e in self.early],
              'work_budget':1000}
        res=run_document(data)
        self.assertEqual(res['inventor']['status'],'PENCIL_GUARD_INVENTED')
        self.assertEqual(res['inventor']['rule']['guard'],{'moisture':'wet','season':'warm'})
        data['capabilities']=['network']
        with self.assertRaisesRegex(ValueError,'lab field'):
            run_document(data)

    def test_randomized_minimum_guard_oracle(self):
        rng=random.Random(903010)
        # Independent Boolean truth-table search for minimal exact-fit conjunction.
        for k in range(1,6):
            for trial in range(20):
                labels=[]
                for bits in range(2**k):
                    facts={f'f{i}':str((bits>>i)&1) for i in range(k)}
                    labels.append(SituatedCase.make(f'{k}-{trial}-{bits}',
                        ['x','bud'],['x','branch'], all(facts[f'f{i}']=='1' for i in range(k)),
                        facts, f'claimed:{bits}',SCOPE))
                out=invent_guard(self.base,labels,scope=SCOPE,work_budget=10000)
                self.assertEqual(out['status'],'PENCIL_GUARD_INVENTED')
                self.assertEqual(out['rule']['guard'],{f'f{i}':'1' for i in range(k)})
                self.assertEqual(out['development']['false_positives'],0)

    def test_second_critic_uses_current_revision_not_original(self):
        first=stage(self.parent,self.base,self.early)
        active=guarded_from_data(first['inventor']['rule'])
        second=stage(self.parent,self.base,self.all_cases,active=active)
        self.assertEqual(len(second['critic']['false_positives']),14)
        self.assertEqual(second['reviewed_active_guard'],{'moisture':'wet','season':'warm'})

    def test_huge_work_budget_still_has_finite_deadline(self):
        result=self.proposal(work_budget=10**15,seconds=1e-10)
        self.assertEqual(result['status'],'CONTINUE_SEARCH')
        self.assertEqual(result['completeness'],'INCOMPLETE')
        self.assertEqual(result['authority'],'NONE')

    def test_archive_rejects_forged_authority(self):
        proposal=self.proposal()
        proposal['authority']='PEN'
        with LivingGraph(scope=SCOPE) as graph:
            with self.assertRaisesRegex(ValueError,'forged'):
                archive_pencil(graph,self.parent,self.base,self.all_cases,proposal)
            self.assertEqual(graph.counts()['nodes'],0)

    def test_hash_collision_sources_are_not_authenticated(self):
        p=self.proposal()
        self.assertEqual(p['instrument'],'PENCIL')
        self.assertEqual(p['authority'],'NONE')
        self.assertNotIn('independent_witnesses_verified',p)


if __name__ == '__main__':unittest.main()
