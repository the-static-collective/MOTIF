"""Adversarial and reproducibility tests for FIELD-003."""
import copy
import json
from pathlib import Path
import unittest
from field003 import (DATASETS,BUDGETS,SEEDS,Owner,load,partition,run,experiment,sha,
                      verify_packet,fit_tree,classify,engineer_features,normalize,xscale,
                      next_request)

class Field003Test(unittest.TestCase):
 def test_source_pins_and_class_labels(self):
  for name,metadata in DATASETS.items():
   rows=load(name)
   self.assertEqual(len(rows),metadata['rows'])
   self.assertEqual(set(y for _,y in rows),{0,1,2})
 def test_split_disjoint_and_row_id_only(self):
  for name,metadata in DATASETS.items():
   for seed in SEEDS:
    p,t,e=partition(metadata['rows'],name,seed)
    self.assertFalse((set(p)&set(t)) or (set(t)&set(e)) or (set(p)&set(e)))
    self.assertEqual(len(set(p+t+e)),metadata['rows'])
 def test_one_starting_fact_and_no_duplicate_queries(self):
  owner=Owner('iris',11)
  fact=owner.query(owner.pool[0]);self.assertTrue(owner.verify(fact))
  self.assertEqual(owner.query_count,1)
  with self.assertRaises(ValueError):owner.query(owner.pool[0])
  with self.assertRaises(ValueError):owner.query(owner.test[0])
 def test_provenance_tamper_and_source_revision(self):
  owner=Owner('wine',11);proof=owner.query(owner.pool[0])
  self.assertTrue(owner.verify(proof))
  for change in ('observed_class','row_id','source_revision','measurements'):
   p=copy.deepcopy(proof)
   if change=='observed_class':p[change]=1-p[change] if p[change] in (0,1) else 0
   elif change=='row_id':p[change]=owner.pool[1]
   elif change=='source_revision':p[change]='forged'
   else:p[change][0]+=1.0
   self.assertFalse(owner.verify(p))
   p['content_sha256']=sha({k:v for k,v in p.items() if k!='content_sha256'})
   self.assertFalse(owner.verify(p))
 def test_composition_is_actual_two_feature_operator(self):
  X,desc=engineer_features([(1.,2.,3.)],3,(0,2))
  self.assertEqual(X[0],(1.,2.,3.,-2.,4.))
  self.assertEqual(desc[-2:],['z0-z2','z0+z2'])
 def test_probe_choice_does_not_require_owner_labels(self):
  o=Owner('iris',11);public=o.public_pool();mu,std=xscale(public)
  X=[normalize(public[k],mu,std) for k in sorted(public)[:12]]
  tree=fit_tree(X,[i%2 for i in range(12)],max_depth=1)
  choice=next_request(public,sorted(public)[:12],tree,None,(),mu,std)
  self.assertIn(choice,public)
  self.assertNotIn(choice,sorted(public)[:12])
  self.assertEqual(o.query_count,0)
 def test_tree_exact_tiny_known_function(self):
  X=[(0,0),(0,1),(1,0),(1,1)]*4
  y=[0,0,0,1]*4
  tree=fit_tree(X,y,max_depth=2,minleaf=2)
  self.assertEqual([classify(tree,x) for x in X],y)
 def test_independent_reentry_recovers_packet_and_denies_forgery(self):
  p=run('wine',11,20,'active')['proof']
  p=json.loads(json.dumps(p))
  self.assertTrue(verify_packet(p))
  q=copy.deepcopy(p);q['receipts'][0]['observed_class']=2 if q['receipts'][0]['observed_class']!=2 else 0
  q['receipts'][0]['content_sha256']=sha({k:v for k,v in q['receipts'][0].items() if k!='content_sha256'})
  q['packet_sha256']=sha({k:v for k,v in q.items() if k!='packet_sha256'})
  self.assertFalse(verify_packet(q))
  q=copy.deepcopy(p);q['probe_traces'][1]['row_id']=q['probe_traces'][0]['row_id']
  q['packet_sha256']=sha({k:v for k,v in q.items() if k!='packet_sha256'})
  self.assertFalse(verify_packet(q))
 def test_no_test_or_tune_label_queries(self):
  for name in DATASETS:
   r=run(name,11,20,'active')['proof'];o=Owner(name,11)
   queried={e['row_id'] for e in r['receipts']}
   self.assertEqual(len(queried),20)
   self.assertTrue(queried <= set(o.pool))
   self.assertFalse(queried & set(o.test+o.tune))
   self.assertTrue(all(s['before_observation'] for s in r['probe_traces']))
   self.assertTrue(all(s['source_queries_before']==k for k,s in enumerate(r['probe_traces'])))
 def test_full_receipt_exact_reproduction(self):
  data=experiment()
  expected=json.loads((Path(__file__).parent/'experiment-results.json').read_text())
  self.assertEqual(data,expected)

if __name__=='__main__':unittest.main()
