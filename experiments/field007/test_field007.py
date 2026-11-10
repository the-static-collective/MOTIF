import unittest
from copy import deepcopy
import numpy as np
from field007 import (TASKS,SEEDS,POLICIES,BUDGET,CHECKPOINTS,BOOTSTRAP,
  source_data,split_ids,ArchivedOwner,geom_next,committee,proposed_query,
  run,seal,score_model)
from lineage import Lineage

class TestField007(unittest.TestCase):
 def test_independently_archived_source_data(self):
  for name in TASKS:
   X,y=source_data(name)
   self.assertEqual(X.shape[0],len(y))
   self.assertEqual(set(y),{0,1})
   self.assertEqual(X.ndim,2)
 def test_no_split_overlap(self):
  for name in TASKS:
   n=len(source_data(name)[1])
   for seed in SEEDS:
    a,b,c=split_ids(n,name,seed)
    self.assertEqual(len(set(a)|set(b)|set(c)),n)
    self.assertFalse(set(a)&set(b) or set(a)&set(c) or set(b)&set(c))
 def test_source_query_gate(self):
  o=ArchivedOwner('digits_3_8',211)
  i=o.pool[0]
  with self.assertRaises(ValueError):o.query(o.test[0])
  p=o.query(i)
  self.assertTrue(o.verify(p))
  with self.assertRaises(ValueError):o.query(i)
 def test_rehashed_forgery_rejected(self):
  o=ArchivedOwner('digits_3_8',211)
  p=o.query(o.pool[0]);forged=deepcopy(p)
  forged['label']=1-forged['label'];forged['sha256']=seal({k:v for k,v in forged.items() if k!='sha256'})
  self.assertFalse(o.verify(forged))
  forged=deepcopy(p);forged['query_number']=123
  forged['sha256']=seal({k:v for k,v in forged.items() if k!='sha256'})
  self.assertFalse(o.verify(forged))
 def test_heldout_gate(self):
  o=ArchivedOwner('breast_cancer',223)
  with self.assertRaises(ValueError):o.freeze()
  with self.assertRaises(ValueError):o.score({},None)
 def test_test_scaling_matches_unlabeled_pool(self):
  from sklearn.preprocessing import StandardScaler
  from sklearn.svm import SVC
  o=ArchivedOwner('digits_3_8',211)
  p=o.visible();ids=list(p); scaler=StandardScaler().fit(np.asarray([p[i] for i in ids]))
  assert len(set(o._y[list(o.pool)]))==2
  train=scaler.transform(o.X[list(o.pool)])
  model=SVC(C=2.,kernel='rbf').fit(train,o._y[list(o.pool)])
  for row in o.pool[:BUDGET]:o.query(row)
  o.freeze()
  expected=model.predict(scaler.transform(o.X[list(o.test)]))
  observed=o.score({'ref':model},scaler)['ref']
  self.assertEqual(observed['correct'],int((expected==o._y[list(o.test)]).sum()))
  self.assertGreater(observed['balanced_accuracy'],0.8)
 def test_lineage_alternate_survives(self):
  o=ArchivedOwner('digits_3_8',211);p=o.query(o.pool[0]);l=Lineage();l.observation('root',p,o)
  l.claim('true',[['root']]);l.claim('false',[['root']])
  l.resolve('true','OBSERVED_MATCH');l.resolve('false','REFUTED_LOCAL_PREDICTION')
  l.claim('alternative',[['true'],['false']],claim_kind='ALTERNATIVE_LOCAL_JUSTIFICATION')
  self.assertTrue(l.supported('alternative'));self.assertFalse(l.supported('false'))
 def test_unknown_task_seed_policy(self):
  for args in [('not',211,'geometry'),('digits_3_8',99,'geometry'),('digits_3_8',211,'oops')]:
   with self.assertRaises(ValueError):run(*args)
 def test_geometry_independent_of_labels(self):
  X={0:np.array([0.,0.]),1:np.array([1.,0.]),2:np.array([10.,0.])}
  self.assertEqual(geom_next([1,2],[0],X),2)
 def test_query_proposal_before_answer(self):
  p=run('digits_3_8',211,'raw_margin',True)
  self.assertEqual(p['source_queries'],BUDGET)
  self.assertEqual(len(p['query_proof']),BUDGET)
  self.assertTrue(p['frozen_before_scoring'])
  for i,event in enumerate(p['query_proof'],1):
   self.assertEqual(event['prequery']['observations_before'],i-1)
   self.assertEqual(event['prequery']['row_id'],event['source_receipt']['row_id'])
  self.assertEqual([s['labels'] for s in p['snapshots']],list(CHECKPOINTS))
 def test_same_bootstrap_for_all_methods(self):
  a=run('digits_3_8',211,'random')
  b=run('digits_3_8',211,'geometry')
  self.assertEqual(a['acquired_row_ids'][:BOOTSTRAP],b['acquired_row_ids'][:BOOTSTRAP])
 def test_source_receipt_changes_by_row(self):
  p=run('digits_3_8',223,'geometry')
  self.assertEqual(len(set(p['source_receipt_sha256s'])),BUDGET)
 def test_same_label_budget_on_new_family(self):
  p=run('breast_cancer',211,'geometry')
  self.assertEqual(p['query_budget'],50)
  self.assertEqual(len(p['snapshots']),3)
  self.assertEqual(p['snapshots'][-1]['labels'],50)

if __name__=='__main__':unittest.main()
