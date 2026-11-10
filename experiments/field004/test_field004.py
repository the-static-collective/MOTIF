"""FIELD-004 adversarial, fairness, leakage and reproducibility tests."""
import copy
import json
from pathlib import Path
import unittest
import numpy as np
from field004 import (AUDIT_SEEDS,DEV_SEEDS,DATASETS,MODES,SEEDS,
  RelationGrammar,run,replay_frozen_queries,choose_by_cv,candidates,
  classify_score,features_for,labels_for,compact_report,digest,previous)
from verify import check_summary,case_locus

class Field004(unittest.TestCase):
 def test_source_pin_and_no_test_label_requests(self):
  for dataset in DATASETS:
   owner,pub,mu,std,recs=replay_frozen_queries(dataset,11,'active')
   assert all(owner.verify(r) for r in recs)
   assert len(recs)==previous.BUDGETS[dataset]
   assert len(set(r['row_id'] for r in recs))==len(recs)
   assert not(set(owner.seen)&set(owner.test+owner.tune))

 def test_original_field003_query_sequence_unchanged(self):
  # Original FIELD-003 packet is produced by unchanged source and exact same budget.
  o,p,mu,std,recs=replay_frozen_queries('iris',11,'active')
  baseline=previous.run('iris',11,previous.BUDGETS['iris'],'active')['proof']
  self.assertEqual([r['row_id'] for r in recs],
                   [r['row_id'] for r in baseline['receipts']])
  self.assertEqual([r['content_sha256'] for r in recs],
                   [r['content_sha256'] for r in baseline['receipts']])

 def test_fold_local_relation_grammar(self):
  X=np.array([[0.,1.,2.],[1.,0.,2.],[0.,2.,1.],[2.,1.,0.],[3.,0.,1.],[3.,2.,0.]])
  y=np.array([0,0,0,1,1,1])
  f=RelationGrammar('interactions',top=2).fit(X,y)
  transformed=f.transform(X)
  self.assertEqual(transformed.shape,(6,6))
  i,j=f.indices_
  self.assertTrue(np.allclose(transformed[:,-3],X[:,i]-X[:,j]))
  self.assertTrue(np.allclose(transformed[:,-2],X[:,i]+X[:,j]))
  self.assertTrue(np.allclose(transformed[:,-1],X[:,i]*X[:,j]))

 def test_no_nan_relation(self):
  with self.assertRaises(ValueError):RelationGrammar().fit(np.array([[float('nan'),1]]),[0])

 def test_raw_classical_is_strong_portfolio(self):
  raw,rel=candidates(11)
  self.assertGreaterEqual(len(raw),8)
  self.assertGreaterEqual(len(rel),7)
  self.assertTrue(any('rf' in k for k in raw))
  self.assertTrue(any('svm' in k for k in raw))
  self.assertTrue(any('interaction' in k for k in rel))

 def test_choices_depend_only_on_acquired_labels(self):
  owner,pub,mu,std,receipt=replay_frozen_queries('iris',11,'active')
  ids=[r['row_id'] for r in receipt]
  X=features_for(ids,owner,mu,std)
  y=np.array([int(r['observed_class']==2) for r in receipt])
  c,_=candidates(11)
  a,s=choose_by_cv(c,X,y,11)
  # Results of training-only selection cannot change if unobserved labels mutate.
  for i in owner.tune+owner.test:
   xx,target=owner.rows[i];owner.rows[i]=(xx,(target+1)%3)
  b,t=choose_by_cv(c,X,y,11)
  self.assertEqual((a,s),(b,t))

 def test_case_freeze_receipts_independent_of_scoring(self):
  r=run('iris',11,'active')
  f=r['frozen']
  self.assertEqual(f['sha256'],digest({k:v for k,v in f.items() if k!='sha256'}))
  x=copy.deepcopy(r)
  x['scores']['test']['composed_relation_cv']['correct']=-1
  self.assertEqual(r['frozen'],x['frozen'])

 def test_one_full_case_reentry_exact_against_committed(self):
  obj=json.loads((Path(__file__).parent/'experiment-results.json').read_text())
  row=next(v for v in obj['cases'] if v['dataset']=='iris' and v['seed']==11 and v['mode']=='active')
  self.assertEqual(row,case_locus(run('iris',11,'active')))

 def test_summary_conservation_and_cohort_scope(self):
  obj=json.loads((Path(__file__).parent/'experiment-results.json').read_text())
  self.assertTrue(check_summary(obj))
  self.assertFalse(set(DEV_SEEDS)&set(AUDIT_SEEDS))
  self.assertEqual(len(SEEDS),10)
  self.assertEqual(len(obj['cases']),40)

 def test_random_and_active_equal_label_budgets(self):
  for mode in MODES:
   r=run('iris',11,mode)
   self.assertEqual(r['label_queries'],previous.BUDGETS['iris'])
   self.assertEqual(len(r['frozen']['trained_row_ids']),previous.BUDGETS['iris'])

if __name__=='__main__':unittest.main()
