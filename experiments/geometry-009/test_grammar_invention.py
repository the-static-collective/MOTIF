"""GEOM-009 controls: grammar induction, provenance, forks, and resource honesty."""
from __future__ import annotations

import itertools
import random
import tempfile
import unittest
from pathlib import Path

from living_graph import LivingGraph, RewriteGrammar, RewriteRule
from grammar_invention import (Example, candidate_patterns, predicts, score,
    propose_revision, compare_fork, preserve_proposal, run_document, rule_from_proposal)
from demo import scenario


class GrammarInventionTests(unittest.TestCase):
    def setUp(self):
        self.parent, self.train, self.heldout = scenario()

    def propose(self, **kwargs):
        return propose_revision(self.parent,self.train,self.heldout,candidate_budget=1000,**kwargs)

    def test_can_identify_new_atomic_rewrite_not_in_original_grammar(self):
        res=self.propose()
        self.assertEqual(res['status'],'PENCIL_GRAMMAR_REVISION_PROPOSED')
        self.assertEqual(res['rule']['find'],['bud'])
        self.assertEqual(res['rule']['replace'],['branch'])
        self.assertNotEqual(res['parent_fingerprint'],res['proposed_fingerprint'])
        self.assertEqual(res['training']['correct'],4)
        self.assertEqual(res['heldout']['correct'],4)
        self.assertEqual(len(res['existing_grammar_gap']['unexplained_positive_cases']),3)

    def test_parent_grammar_without_gap_refuses_redundant_discovery(self):
        r=self.propose()['rule']
        enriched=RewriteGrammar(self.parent.scope,self.parent.rules+(rule_from_proposal(r),))
        res=propose_revision(enriched,self.train,self.heldout,candidate_budget=100)
        self.assertEqual(res['status'],'HOLD')
        self.assertIn('already explains',res['reason'])

    def test_isolated_fork_reaches_new_targets(self):
        res=self.propose()
        fork=compare_fork(self.parent,res['rule'],[('oak','seed'),('pine','seed')],
                          [('oak','branch'),('pine','branch')],work_budget=100)
        a=fork['comparison']['parent']; b=fork['comparison']['revised']
        self.assertEqual(a['target_hits'],0)
        self.assertEqual(b['target_hits'],2)
        self.assertEqual(a['growth_status'],'SATURATED_FOR_CURRENT_GRAMMAR')
        self.assertEqual(b['growth_status'],'SATURATED_FOR_CURRENT_GRAMMAR')
        self.assertEqual(a['integrity']['foreign_key_errors'],0)

    def test_proposal_preserved_as_pencil_with_witnesses(self):
        res=self.propose()
        with LivingGraph(scope=self.parent.scope) as graph:
            receipt=preserve_proposal(graph,self.parent,res,self.train,self.heldout)
            self.assertEqual(receipt['status'],'PENCIL_REVISION_ARCHIVED')
            self.assertEqual(graph.counts()['nodes'],9)
            self.assertEqual(graph.counts()['relations'],1)
            row=graph.db.execute('SELECT status,kind FROM nodes WHERE id=?',(receipt['node_id'],)).fetchone()
            self.assertEqual((row['status'],row['kind']),('PENCIL','reason_grammar_candidate'))
            self.assertEqual(graph.verify()['integrity'],'ok')

    def test_archive_rejects_forged_heldout_score(self):
        r=self.propose()
        r['heldout']['correct']=9999
        with LivingGraph(scope=self.parent.scope) as g:
            with self.assertRaisesRegex(ValueError,'mismatch'):
                preserve_proposal(g,self.parent,r,self.train,self.heldout)
            self.assertEqual(g.counts()['nodes'],0)

    def test_archive_rejects_forged_rule(self):
        r=self.propose()
        r['rule']['replace']=['nonsense']
        with LivingGraph(scope=self.parent.scope) as g:
            with self.assertRaisesRegex(ValueError,'mismatch'):
                preserve_proposal(g,self.parent,r,self.train,self.heldout)

    def test_scope_cannot_be_crossed(self):
        r=self.propose()
        with LivingGraph(scope='another:observer') as graph:
            with self.assertRaisesRegex(ValueError,'scope mismatch'):
                preserve_proposal(graph,self.parent,r,self.train,self.heldout)

    def test_existing_graph_grammar_cannot_be_rebound(self):
        proposed=self.propose()['rule']
        with LivingGraph(scope=self.parent.scope) as graph:
            graph.seed(['oak','seed'])
            graph.grow(self.parent,work_budget=3)
            with self.assertRaisesRegex(ValueError,'cannot silently replace'):
                graph.grow(RewriteGrammar(self.parent.scope,
                            self.parent.rules+(rule_from_proposal(proposed),)),work_budget=3)

    def test_distinct_claimed_origins_gate(self):
        collapsed=[Example(x.identity,x.before,x.after,x.expected,'same-root') for x in self.train]
        r=propose_revision(self.parent,collapsed,self.heldout,candidate_budget=100)
        self.assertEqual(r['status'],'HOLD')
        self.assertIn('source roots',r['reason'])

    def test_two_claimed_roots_not_authenticated(self):
        result=self.propose()
        self.assertEqual(result['authority'],'NONE')
        self.assertEqual(result['instrument'],'PENCIL')
        self.assertEqual(result['claimed_positive_roots'],3)

    def test_heldout_labels_do_not_influence_candidate_selection(self):
        false_held=[Example(e.identity,e.before,e.after,not e.expected,e.source_root)
                    for e in self.heldout]
        self.assertEqual(self.propose()['rule'],
            propose_revision(self.parent,self.train,false_held,candidate_budget=1000)['rule'])

    def test_incomplete_search_does_not_claim_global_success(self):
        r=propose_revision(self.parent,self.train,self.heldout,candidate_budget=1)
        self.assertEqual(r['status'],'CONTINUE_SEARCH')
        self.assertEqual(r['completeness'],'INCOMPLETE')
        done=propose_revision(self.parent,self.train,self.heldout,candidate_budget=1,
                              cursor=r['next_cursor'])
        self.assertEqual(done['status'],'PENCIL_GRAMMAR_REVISION_PROPOSED')
        self.assertEqual(done['rule'],self.propose()['rule'])

    def test_cursor_rejects_cross_domain_replay(self):
        r=propose_revision(self.parent,self.train,self.heldout,candidate_budget=1)
        modified=[Example(x.identity,x.before,x.after,x.expected,
                  'changed-root' if x.identity=='oak' else x.source_root) for x in self.train]
        with self.assertRaisesRegex(ValueError,'continuation cursor'):
            propose_revision(self.parent,modified,self.heldout,candidate_budget=100,
                             cursor=r['next_cursor'])

    def test_cursor_rejects_forged_candidate(self):
        r=propose_revision(self.parent,self.train,self.heldout,candidate_budget=1)
        r['next_cursor']['best_pair']=[['garbage'],['branch']]
        with self.assertRaises(ValueError):
            propose_revision(self.parent,self.train,self.heldout,candidate_budget=100,
                             cursor=r['next_cursor'])

    def test_negative_cases_block_overgeneralization(self):
        positive=[Example('a',('a','bud'),('a','branch'),True,'s1'),
                  Example('b',('b','bud'),('b','branch'),True,'s2')]
        negatives=[Example('c',('c','bud'),('c','branch'),False,'s3')]
        result=propose_revision(self.parent,positive+negatives,self.heldout,candidate_budget=200)
        self.assertEqual(result['status'],'HOLD')

    def test_wrong_scope_graph_fork_is_rejected(self):
        with self.assertRaises(ValueError):
            compare_fork(self.parent,self.propose()['rule'],[],[('a',)],work_budget=10)

    def test_duplicate_rule_fork_is_rejected(self):
        with self.assertRaisesRegex(ValueError,'duplicates'):
            compare_fork(self.parent,{'name':'duplicate','find':['seed'],'replace':['bud']},
                         [('a','seed')],[('a','bud')],work_budget=10)

    def test_partial_fork_does_not_treat_absence_as_falsity(self):
        r=self.propose()
        out=compare_fork(self.parent,r['rule'],[('a','seed')],[('a','branch')],work_budget=1)
        for branch in ('parent','revised'):
            self.assertFalse(out['comparison'][branch]['unobserved_targets_are_negative'])

    def test_insertion_and_deletion_cases_supported(self):
        insertion=Example('i',('a',),('a','b'),True,'s1')
        deletion=Example('d',('a','b'),('a',),True,'s2')
        self.assertIn(((),('b',)),list(candidate_patterns(insertion.before,insertion.after)))
        self.assertIn((('b',),()),list(candidate_patterns(deletion.before,deletion.after)))

    def test_malicious_top_level_field_refused(self):
        with self.assertRaisesRegex(ValueError,'unknown or missing'):
            run_document({'execute_shell':'rm -rf /'})

    def test_nonboolean_labels_rejected(self):
        with self.assertRaisesRegex(ValueError,'expected must be bool'):
            Example('x',('a',),('b',),1,'r')

    def test_invalid_budgets_refused(self):
        for val in (0,-2,True,0.1):
            with self.assertRaises(ValueError):
                propose_revision(self.parent,self.train,self.heldout,candidate_budget=val)

    def test_empty_positive_cases_refused(self):
        cases=[Example('n',('a',),('b',),False,'r')]
        self.assertEqual(propose_revision(self.parent,cases,self.heldout,candidate_budget=100)['status'],'HOLD')

    def test_independent_small_exhaustive_pattern_oracle(self):
        rng=random.Random(20261106)
        vocabulary=('a','b','c')
        for _ in range(120):
            before=tuple(rng.choice(vocabulary) for _ in range(rng.randrange(0,5)))
            after=tuple(rng.choice(vocabulary) for _ in range(rng.randrange(0,5)))
            if before==after:continue
            patterns=set(candidate_patterns(before,after))
            oracle=set()
            for m in range(len(before)+1):
                for n in range(len(after)+1):
                    for f in itertools.product(vocabulary,repeat=m):
                        for repl in itertools.product(vocabulary,repeat=n):
                            if f==repl:continue
                            rule=RewriteRule('oracle',f,repl)
                            if any(x==after for _,x in rule.outcomes(before)):
                                oracle.add((f,repl))
            # Candidate pattern must match independent exhaustive transition oracle.
            self.assertEqual(patterns,oracle,(before,after))


if __name__=='__main__':
    unittest.main()
