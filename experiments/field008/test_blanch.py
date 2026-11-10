import copy
import json
import unittest
from pathlib import Path
from unittest.mock import patch
import blanch as b
from grounding import BlanchLedger


class FieldEightTests(unittest.TestCase):
    def test_corpus_pin_and_sizes(self):
        self.assertEqual(len(b.atlas()),1253)
        self.assertEqual(len(b.source_catalog(6).ids),156)
        self.assertEqual(len(b.audit_ids(7)),96)
        self.assertEqual(b.corpus_digest(b.atlas()),b.ATLAS_SHA256)

    def test_hypothetical_source_agreement_all_probes(self):
        for n in (6,7):
            ids=b.source_catalog(n).ids if n==6 else b.audit_ids(7)
            for i in ids:
                for p in b.catalog(n):
                    self.assertEqual(b.from_graph(b.atlas()[i],p),
                                     b.owner_answer(b.atlas()[i],p),(i,p.key))

    def test_forged_rehashed_source_rejected(self):
        o=b.Owner(100)
        root=o.root()
        self.assertTrue(o.verify(root))
        p=o.ask('degree:1')
        self.assertTrue(o.verify(p))
        forged=copy.deepcopy(p);forged['answer']+=1
        forged['sha256']=b.sha({k:v for k,v in forged.items() if k!='sha256'})
        self.assertFalse(o.verify(forged))
        stale=copy.deepcopy(p);stale['source_revision']='stale';stale['sha256']=b.sha({k:v for k,v in stale.items() if k!='sha256'})
        self.assertFalse(o.verify(stale))
        fake=copy.deepcopy(p);fake['probe']='invented:1';fake['sha256']=b.sha({k:v for k,v in fake.items() if k!='sha256'})
        self.assertFalse(o.verify(fake))
        with self.assertRaises(ValueError):o.ask('degree:1')
        with self.assertRaises(ValueError):o.ask('owner_secret')

    def test_starting_fact_no_hidden_graph_id(self):
        o=b.Owner(97);packet=o.root()
        self.assertNotIn('graph_id',packet)
        self.assertNotIn('world_id',packet)
        self.assertNotIn('97',str(packet))
        self.assertEqual(o.history,[])

    def test_all_branched_predictions_are_pencil(self):
        c=b.source_catalog(6)
        o=b.Owner(100); root=o.root()
        s=b.choices_after(root,[],c)
        q=b.propose('blanch',s,set(),c)
        self.assertIsNotNone(q)
        self.assertTrue(all(row['status']=='PENCIL_BLANCHED_NOT_FACT' for row in q['blanched_branches']))
        self.assertEqual({x for row in q['blanched_branches'] for x in row['source_root_origins']},{'one_atlas_corpus'})
        self.assertEqual(len(o.history),0)  # Proposing does not query.
        self.assertGreaterEqual(q['query_depth'],1)
        self.assertTrue(all(len(row['trace'])>=q['query_depth'] for row in q['blanched_branches']))

    def test_evidence_lineage_retractions_keep_true_alternatives(self):
        for policy in ('near','entropy','gini','blanch','value_control'):
            result=b.run_case(100,policy,full_trace=True)
            self.assertTrue(result['packet_sha256'])
            self.assertLessEqual(result['extra_queries'],4)
            self.assertNotIn('SOURCE_OBSERVATION',str([x['proposal']['blanched_branches'] for x in result['proof_steps']]))
            for step in result['proof_steps']:
                self.assertIn(100,step['retained_alternative_worlds'])
                self.assertFalse(set(step['retracted_conditional_worlds']) & set(step['retained_alternative_worlds']))
                self.assertEqual(step['proposal']['source_query_count_before']+1,
                                 step['verified_source']['source_query_sequence'])
                pkt=step['proposal']; self.assertEqual(pkt['proposal_sha256'],b.sha({k:v for k,v in pkt.items() if k!='proposal_sha256'}))

    def test_attribute_resolution_is_not_graph_identification(self):
        # Structural properties may all be determined while alternative
        # original graph structures legitimately survive.
        x=[b.run_case(i,'blanch') for i in b.audit_ids(7)]
        self.assertTrue(any(r['properties_resolved']==5 and not r['unique_identified'] for r in x))

    def test_grounding_deduplicates_common_origin_and_preserves_or(self):
        class FakeOwner:
            def verify(self,r):return r.get('kind')=='fake' and r.get('valid') is True
        l=BlanchLedger();own=FakeOwner()
        for k,origin in [('a','one'),('b','one'),('c','two')]:
            l.ink(k,{'kind':'fake','valid':True,'provenance_origin':origin},own)
        x=l.blanch('h1',[['a','b']])
        self.assertEqual(x['independent_origin_count'],1)
        x=l.blanch('h2',[['a','c']])
        self.assertEqual(x['independent_origin_count'],2)
        l.claim('bad',[['a']],claim_kind='LOCAL_PREDICTION')
        l.claim('good',[['c']],claim_kind='LOCAL_PREDICTION')
        l.resolve('bad','REFUTED_LOCAL_PREDICTION')
        l.resolve('good','OBSERVED_MATCH')
        status=l.blanch('child',[['bad'],['good']])
        self.assertEqual(status['state'],'PENCIL_CONDITIONAL')
        self.assertEqual(status['independent_origin_count'],1)
        self.assertNotEqual(status['state'],'INK')

    def test_strong_classical_value_control_ties(self):
        for n in (6,7):
            ids=b.source_catalog(n).ids[:12]
            for i in ids:
                a=b.run_case(i,'blanch');b0=b.run_case(i,'value_control')
                for key in ('remaining_models','unique_identified','properties_resolved','extra_queries'):
                    self.assertEqual(a[key],b0[key])

    def test_report_reproduction(self):
        path=Path(__file__).resolve().parent/'experiment-results.json'
        actual=b.benchmark()
        self.assertEqual(actual,json.loads(path.read_text()))
        sums={(x['n'],x['policy']):x for x in actual['summary']}
        self.assertFalse(actual['primary_strict_beats_classical_6'])
        self.assertEqual(sums[(7,'blanch')]['total_resolved_attributes'],480)
        self.assertEqual(sums[(7,'blanch')]['unique'],sums[(7,'value_control')]['unique'])


if __name__=='__main__':unittest.main()
