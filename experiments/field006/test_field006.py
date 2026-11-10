"""FIELD-006 adversarial tests. No actual external-world actions."""
import copy
import json
import sys
import unittest
from pathlib import Path
import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parent))
import field006 as e
from field006 import f3, old, Lineage, seal, check_receipt


class TruthMaintenanceTests(unittest.TestCase):
    def test_independent_support_survives_refutation(self):
        owner=f3.Owner('iris',11)
        l=Lineage()
        ids=owner.pool[:2]
        for j,k in enumerate(ids):
            l.observation('fact'+str(j),owner.query(k),owner)
        l.claim('wrong',[['fact0']])
        l.claim('right',[['fact1']])
        l.claim('a_second_order_conclusion',[['wrong'],['right']],claim_kind='ALTERNATIVE_LOCAL_JUSTIFICATION')
        l.resolve('wrong','REFUTED_LOCAL_PREDICTION')
        l.resolve('right','OBSERVED_MATCH')
        self.assertTrue(l.supported('a_second_order_conclusion'))
        self.assertFalse(l.supported('wrong'))
        l.claim('depends_on_false',[['wrong']],claim_kind='DEPENDENT_CONCLUSION')
        self.assertEqual(l.derived_status('depends_on_false'),'HOLD_NO_SURVIVING_SUPPORT')
        self.assertTrue(check_receipt(l.receipt()))

    def test_pencil_alone_is_not_fact(self):
        o=f3.Owner('iris',11);l=Lineage()
        l.observation('f',o.query(o.pool[0]),o)
        l.claim('hypothesis',[['f']])
        self.assertFalse(l.supported('hypothesis'))
        l.claim('conclusion',[['hypothesis']],claim_kind='INFERRED')
        self.assertFalse(l.supported('conclusion'))

    def test_forged_rehashed_archived_label_refused(self):
        o=f3.Owner('wine',11)
        r=o.query(o.pool[0]);f={**r,'observed_class':(r['observed_class']+1)%3}
        f['content_sha256']=f3.sha({k:v for k,v in f.items() if k!='content_sha256'})
        with self.assertRaises(ValueError):Lineage().observation('f',f,o)

    def test_cycle_or_orphan_refused(self):
        o=f3.Owner('iris',23);l=Lineage()
        l.observation('f',o.query(o.pool[0]),o)
        with self.assertRaises(ValueError):l.claim('bad',[['no_such_node']])
        l.claim('h',[['f']])
        with self.assertRaises(ValueError):l.claim('broken',[[]])
        broken=copy.deepcopy(l.receipt())
        broken['record']['nodes']['h']['alternatives']=[['h']]
        broken['sha256']=seal(broken['record'])
        self.assertFalse(check_receipt(broken))

    def test_structural_reentry_detects_mutation(self):
        o=f3.Owner('iris',11);l=Lineage();l.observation('f',o.query(o.pool[0]),o)
        receipt=l.receipt();self.assertTrue(check_receipt(receipt))
        modified=copy.deepcopy(receipt);modified['record']['nodes']['f']['payload_sha256']='a'*64
        self.assertFalse(check_receipt(modified))

    def test_twice_or_unlicensed_resolution_rejected(self):
        o=f3.Owner('iris',11);l=Lineage();l.observation('f',o.query(o.pool[0]),o)
        with self.assertRaises(ValueError):l.resolve('f','OBSERVED_MATCH')
        l.claim('a',[['f']]);l.resolve('a','OBSERVED_MATCH')
        with self.assertRaises(ValueError):l.resolve('a','REFUTED_LOCAL_PREDICTION')


class Field006Tests(unittest.TestCase):
    def test_only_public_pool_in_scoring(self):
        o=f3.Owner('wine',11)
        X,_,_=old.standardize(o.public_pool());density=old.pool_neighbors(X)
        chosen=o.pool[:14];y=[int(o.rows[i][1]==2) for i in chosen]
        if len(set(y))<2:
            chosen=chosen+[i for i in o.pool if int(o.rows[i][1]==2)!=y[0]][:2]
            y=[int(o.rows[i][1]==2) for i in chosen]
        mods=e.committee('counterexample_relational',np.asarray([X[i] for i in chosen]),np.asarray(y),11)
        future=sorted(set(o.pool)-set(chosen))
        experience={k:[0,0] for k in mods}
        a,_=e.choose_counterexample(future,chosen,X,density,mods,experience,'counterexample_relational')
        hidden=copy.deepcopy(o.rows)
        for i in o.tune+o.test:
            f,z=o.rows[i];o.rows[i]=(f,(z+1)%3)
        b,_=e.choose_counterexample(future,chosen,X,density,mods,experience,'counterexample_relational')
        self.assertEqual(a,b)
        o.rows=hidden

    def test_equal_budget_original_source_and_proposal_before_label(self):
        for policy in ('counterexample_relational','counterexample_raw','raw_margin'):
            r=e.run('iris',11,policy,25)
            proof=r['proof'];o=f3.Owner('iris',11)
            self.assertEqual(proof['budget'],25)
            self.assertEqual(proof['source_rev'],o.revision)
            self.assertEqual(len(set(proof['selected_row_ids'])),25)
            self.assertFalse(set(proof['selected_row_ids']) & set(o.tune+o.test))
            for j,ev in enumerate(proof['events']):
                b=ev['before']
                self.assertEqual(b['query'],j+1)
                self.assertEqual(b['source_queries_before'],j)
                self.assertEqual(b['prior_observation_ids_sha256'],seal(proof['selected_row_ids'][:j]))
                self.assertNotIn('observed_class',b)
                self.assertEqual(b['sha256'],seal({k:v for k,v in b.items() if k!='sha256'}))
            self.assertEqual(proof['sha256'],seal({k:v for k,v in proof.items() if k!='sha256'}))

    def test_counterexample_ledger_has_discriminating_questions(self):
        r=e.run('wine',23,'counterexample_relational',25)
        self.assertGreater(r['proof']['discriminating_queries'],0)
        self.assertGreater(r['proof']['local_prediction_refutations'],0)
        self.assertGreater(r['proof']['surviving_local_alternatives'],0)
        self.assertEqual(r['proof']['status'],'RESEARCH_HOLD_SOURCE_RECORDS_NOT_NEW_PHYSICAL_FACTS')

    def test_determinism_and_ancestry_tampering(self):
        a=e.run('iris',23,'counterexample_relational',25)
        b=e.run('iris',23,'counterexample_relational',25)
        self.assertEqual(a['proof'],b['proof'])
        changed=copy.deepcopy(a['proof'])
        changed['events'][12]['before']['question']['status']='OBSERVED_FACT'
        self.assertNotEqual(changed['sha256'],seal({k:v for k,v in changed.items() if k!='sha256'}))

    def test_invalid_input_rejected(self):
        for bad in ('unrecognized','',None):
            with self.assertRaises(ValueError):e.run('iris',11,bad,25)
        with self.assertRaises(ValueError):e.run('iris',11,'geometry',41)

    def test_equal_sized_committees(self):
        o=f3.Owner('wine',11);public=o.public_pool()
        X,_,_=old.standardize(public)
        selected=o.pool[:12];yy=np.array([int(o.rows[i][1]==2) for i in selected])
        if len(set(yy))<2:
            selected=selected+[i for i in o.pool if int(o.rows[i][1]==2)!=yy[0]][:2]
            yy=np.array([int(o.rows[i][1]==2) for i in selected])
        Xtrain=np.asarray([X[i] for i in selected])
        self.assertEqual(len(e.committee('counterexample_raw',Xtrain,yy,11)),6)
        self.assertEqual(len(e.committee('counterexample_relational',Xtrain,yy,11)),6)

if __name__=='__main__':unittest.main()
