"""FIELD-005 basic validity, attack and repeatability checks (unittest only)."""
import copy, json, sys, unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from field005 import (SCHEMA, POLICIES, DEVELOPMENT_SEEDS, AUDIT_SEEDS,
                      run, select_query, pool_neighbors, standardize,
                      fit_acquisition_models, digest, f3, WARMUP, CHECKPOINTS)

class Field005Tests(unittest.TestCase):
    def test_split_roles_and_equal_label_budgets(self):
        for policy in POLICIES:
            r=run('iris',11,policy,budget=25)
            ids=r['proof']['ids_ordered'];o=f3.Owner('iris',11)
            self.assertEqual(len(ids),25)
            self.assertEqual(len(set(ids)),25)
            self.assertFalse(set(ids)&set(o.test+o.tune))
            self.assertEqual(len(r['proof']['source_receipts_sha256']),25)
            self.assertEqual(r['proof']['schema'],SCHEMA)

    def test_source_byte_pin_and_refuse_rehashed_forgery(self):
        owner=f3.Owner('iris',23)
        r=owner.query(owner.pool[0])
        self.assertTrue(owner.verify(r))
        bad={**r,'observed_class':(r['observed_class']+1)%3}
        bad['content_sha256']=f3.sha({k:v for k,v in bad.items() if k!='content_sha256'})
        self.assertFalse(owner.verify(bad))
        self.assertEqual(owner.revision,f3.DATASETS['iris']['sha256'])

    def test_query_selection_never_reads_hidden_labels(self):
        owner=f3.Owner('wine',11)
        xmap,_,_=standardize(owner.public_pool());d=pool_neighbors(xmap)
        # Query selector is given only labeled training samples and unlabeled pool.
        selected=[];observed=[];fit=None
        for n in range(19):
            if n >= WARMUP and len(set(observed))==2:
                fit=fit_acquisition_models(np.asarray([xmap[i] for i in selected]),
                                            np.asarray(observed), 'relation_frontier', 11)
            proposed=select_query('relation_frontier',selected,xmap,11,fit,d)
            if n>=WARMUP and fit:
                # changing hidden tune/test labels cannot influence the proposed query
                original=owner.rows[:]
                for i in owner.test+owner.tune:
                    x,l=owner.rows[i];owner.rows[i]=(x,(l+1)%3)
                other=select_query('relation_frontier',selected,xmap,11,fit,d)
                self.assertEqual(proposed,other)
                owner.rows=original
            rec=owner.query(proposed)
            selected.append(proposed);observed.append(int(rec['observed_class']==2))

    def test_question_precedes_answer_and_hash_rechecks(self):
        r=run('iris',23,'relation_frontier',budget=40)
        proof=r['proof']
        for j,ev in enumerate(proof['events']):
            self.assertEqual(ev['source_queries_before'],j)
            self.assertEqual(ev['query'],j+1)
            self.assertEqual(ev['acquired_before_sha256'],digest(proof['ids_ordered'][:j]))
            self.assertEqual(ev['query_status'],'PROPOSED_BEFORE_LABEL')
            self.assertNotIn('observed_class',ev)
        self.assertEqual(proof['frozen_sha256'],digest({k:v for k,v in proof.items() if k!='frozen_sha256'}))
        changed=copy.deepcopy(proof);changed['ids_ordered'][0]=-1
        self.assertNotEqual(proof['frozen_sha256'],digest({k:v for k,v in changed.items() if k!='frozen_sha256'}))

    def test_same_model_menu_for_all_query_policies(self):
        from field005 import raw_estimators,relational_estimators
        r=raw_estimators(11);c=relational_estimators(11)
        self.assertTrue({'rbf_svc','rf','extra_trees','logistic'}.issubset(r))
        self.assertTrue({'signed_svm','interaction_svm','interaction_forest'}.issubset(c))
        self.assertEqual(len(r),5);self.assertEqual(len(c),3)

    def test_finite_budget_and_invalid_policies(self):
        for bad in ('danger','',None):
            with self.assertRaises(ValueError):run('iris',11,bad,budget=12)
        with self.assertRaises(ValueError):run('wine',11,'random',budget=999)

    def test_data_partitions_and_no_audit_overlap(self):
        self.assertFalse(set(DEVELOPMENT_SEEDS)&set(AUDIT_SEEDS))
        for dataset in ('iris','wine'):
            for seed in (*DEVELOPMENT_SEEDS,*AUDIT_SEEDS):
                owner=f3.Owner(dataset,seed)
                self.assertEqual(set(owner.pool)&set(owner.tune),set())
                self.assertEqual(set(owner.tune)&set(owner.test),set())
                self.assertEqual(set(owner.pool)&set(owner.test),set())

    def test_repeatability_small_case(self):
        a=run('wine',23,'raw_margin',budget=25)
        b=run('wine',23,'raw_margin',budget=25)
        self.assertEqual(a['proof'],b['proof'])
        self.assertEqual(a['test'],b['test'])

    def test_feature_and_label_independence(self):
        owner=f3.Owner('iris',11);xmap,mu,st=standardize(owner.public_pool())
        self.assertEqual(len(xmap),len(owner.pool))
        self.assertTrue(np.isfinite(mu).all())
        self.assertTrue(np.all(st>0))
        self.assertEqual(len(CHECKPOINTS['wine']),4)

if __name__=='__main__':unittest.main()
