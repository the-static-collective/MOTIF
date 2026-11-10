"""FIELD-007: source-domain transfer of counterexample-selecting active learning.

The original FIELD-006 lineage and FIELD-004 relation composer are reused.
The classifier and query languages are classical; original datasets are public,
not source-owner-operated blind experiments. No external-world actions.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter

import numpy as np
from sklearn.datasets import load_digits, load_breast_cancer
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.pipeline import Pipeline

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'field004'))
sys.path.insert(0,str(HERE.parent/'field006'))
from field004 import RelationGrammar
from lineage import Lineage, seal, check_receipt

SCHEMA='motif.field007.v1'
SEEDS=(211,223,227)
POLICIES=('random','geometry','raw_margin','raw_committee','counterexample_relational')
TASKS=('digits_3_8','breast_cancer')
BUDGET=50
CHECKPOINTS=(20,35,50)
BOOTSTRAP=12
REFIT_EVERY=3
SOURCES={
 'digits_3_8': {'revision':'41ea7cf6db2effc93950bc713ba9451755ed1787e71a9bd29032198c86a451e9',
               'origin':'UCI Optical Recognition of Handwritten Digits, sklearn 1.8.0 load_digits(), filtered classes 3 and 8',
               'n':357,'features':64},
 'breast_cancer': {'revision':'25e2eb7b7a8745b1bde5ba18bc4969983d2e2f403291ecd5bde4a29ef30c3859',
               'origin':'UCI Wisconsin Diagnostic Breast Cancer, sklearn 1.8.0 load_breast_cancer()',
               'n':569,'features':30},
}


def _sha_bytes(X,y):
 return hashlib.sha256(np.asarray(X,dtype='<f8').tobytes()+np.asarray(y,dtype='<i8').tobytes()).hexdigest()


def source_data(task):
 if task=='digits_3_8':
  ds=load_digits();mask=np.isin(ds.target,[3,8]);X=np.asarray(ds.data[mask],dtype=float);y=np.asarray(ds.target[mask]==8,dtype=int)
 elif task=='breast_cancer':
  ds=load_breast_cancer();X=np.asarray(ds.data,dtype=float);y=np.asarray(ds.target,dtype=int)
 else: raise ValueError('UNAUTHORIZED_SOURCE')
 spec=SOURCES[task]
 if X.shape!=(spec['n'],spec['features']) or _sha_bytes(X,y)!=spec['revision']:
  raise ValueError('SOURCE_REVISION_DRIFT')
 return X,y


def split_ids(n,task,seed):
 """Hash-ranked row ID only, no label-, feature- or target-guided selection."""
 keys=sorted(range(n),key=lambda i:seal(['FIELD007_SPLIT',task,seed,i]))
 a=int(n*.6);b=int(n*.2)
 return tuple(keys[:a]),tuple(keys[a:a+b]),tuple(keys[a+b:])


class ArchivedOwner:
 """Source-held labels are simulated locally; not a real privacy barrier."""
 def __init__(self,task,seed):
  if seed not in SEEDS:raise ValueError('UNDECLARED_SPLIT_SEED')
  self.task=task;self.X,self._y=source_data(task)
  self.pool,self.tune,self.test=split_ids(len(self.X),task,seed)
  self.revision=SOURCES[task]['revision'];self.used=set();self.frozen=False
  self.queries=0;self.score_calls=0;self._issued={}
 def visible(self):
  return {i:self.X[i].copy() for i in self.pool}
 def query(self,row):
  if self.frozen or row not in self.pool or row in self.used:
   raise ValueError('UNAUTHORIZED_SOURCE_LABEL_QUERY')
  self.used.add(row);self.queries+=1
  payload={'kind':'SOURCE_ARCHIVE_OBSERVATION','schema':SCHEMA,'source':self.task,
           'revision':self.revision,'row_id':int(row),
           'label':int(self._y[row]),'query_number':self.queries}
  receipt={**payload,'sha256':seal(payload)}
  self._issued[row]=receipt
  return receipt
 def verify(self,receipt):
  if not isinstance(receipt,dict):return False
  try:
   payload={k:v for k,v in receipt.items() if k!='sha256'}
   i=payload['row_id']
   return (receipt['sha256']==seal(payload) and payload=={
            'kind':'SOURCE_ARCHIVE_OBSERVATION','schema':SCHEMA,'source':self.task,
            'revision':self.revision,'row_id':i,
            'label':int(self._y[i]),'query_number':payload['query_number']}
           and i in self.pool and i in self._issued and receipt==self._issued[i])
  except (KeyError,IndexError,TypeError,ValueError):return False
 def freeze(self):
  if self.queries!=BUDGET:raise ValueError('CAN_NOT_SCORE_BEFORE_BUDGET')
  self.frozen=True
 def score(self,models,scaler):
  if not self.frozen:raise ValueError('TEST_LEAK_ATTEMPT')
  self.score_calls+=1
  X=scaler.transform(self.X[list(self.test)]);y=self._y[list(self.test)]
  return {name:score_model(model,X,y) for name,model in models.items()}


def score_model(model,X,y):
 p=np.asarray(model.predict(X),dtype=int);y=np.asarray(y,dtype=int)
 sens0=np.mean(p[y==0]==0) if np.any(y==0) else 0.
 sens1=np.mean(p[y==1]==1) if np.any(y==1) else 0.
 return {'correct':int(np.sum(p==y)),'n':len(y),'balanced_accuracy':round(float((sens0+sens1)/2),6),
         'accuracy':round(float(np.mean(p==y)),6),
         'by_class':{'0':int(np.sum((p==0)&(y==0))),'1':int(np.sum((p==1)&(y==1)))},
         'class_counts':{'0':int(np.sum(y==0)),'1':int(np.sum(y==1))}}


def finite_scale(X):
 scaler=StandardScaler().fit(X)
 return scaler


def dist_sq(X,a,b):
 delta=X[a]-X[b];return float(delta@delta)


def geom_next(avail,seen,X):
 if not seen:return min(avail)
 return max(avail,key=lambda i:(min(dist_sq(X,i,k) for k in seen),-i))


def committee(policy,X,y,seed):
 raw={
  'raw_svm':SVC(C=2.,kernel='rbf'),
  'raw_logistic':LogisticRegression(max_iter=2000),
  'raw_forest':RandomForestClassifier(n_estimators=45,min_samples_leaf=2,random_state=seed,n_jobs=1),
 }
 if policy=='counterexample_relational':
  raw.update({
   'rel_signed_svm':Pipeline([('relations',RelationGrammar('signed',6)),('classifier',SVC(C=2.,kernel='rbf'))]),
   'rel_product_svm':Pipeline([('relations',RelationGrammar('interactions',6)),('classifier',SVC(C=2.,kernel='rbf'))]),
   'rel_signed_tree':Pipeline([('relations',RelationGrammar('signed',6)),('classifier',DecisionTreeClassifier(max_depth=3,min_samples_leaf=2,random_state=seed))]),
  })
 return {k:v.fit(X,y) for k,v in raw.items()}


def proposed_query(policy,available,seen,X,seed,models,experience,step):
 if step<BOOTSTRAP or (models is None and policy!='random'):
  return geom_next(available,seen,X),{'committee_votes':{},'status':'PROPOSED_BEFORE_LABEL'}
 if policy=='random':
  row=min(available,key=lambda i:seal(['FIELD007_RANDOM',seed,i]))
  return row,{'committee_votes':{},'status':'PROPOSED_BEFORE_LABEL'}
 if policy=='geometry':
  return geom_next(available,seen,X),{'committee_votes':{},'status':'PROPOSED_BEFORE_LABEL'}
 raw= models['raw_svm']
 xnew=np.asarray([X[i] for i in available])
 margin=np.abs(raw.decision_function(xnew))
 if policy=='raw_margin':
  j=min(range(len(available)),key=lambda j:(margin[j],available[j]));return available[j],{'committee_votes':{'raw_svm':int(raw.predict(xnew[j:j+1])[0])},'status':'PROPOSED_BEFORE_LABEL'}
 votes={name:mod.predict(xnew).astype(int) for name,mod in models.items()}
 weights={name:(2+experience.get(name,[0,0])[0])/(4+sum(experience.get(name,[0,0]))) for name in models}
 total=sum(weights.values())
 best=None;idx=None
 for j,row in enumerate(available):
  yes=sum(weights[k] for k,v in votes.items() if v[j]==1)
  no=total-yes
  entropy= -sum(p*math.log2(p) for p in [yes/total,no/total] if p>0)
  conflict=int(any(v[j]!=votes['raw_svm'][j] for k,v in votes.items() if k.startswith('rel_')))
  if policy=='counterexample_relational':
   score=(round(min(yes,no)/total,9),conflict,round(entropy,9),-float(margin[j]),-row)
  else:
   score=(round(entropy,9),-float(margin[j]),-row)
  if best is None or score>best:idx=j;best=score
 assert idx is not None
 return available[idx],{'committee_votes':{k:int(v[idx]) for k,v in votes.items()},
                        'weights':{k:round(weights[k],6) for k in weights},
                        'selection_key':[float(s) for s in best],
                        'status':'PROPOSED_BEFORE_LABEL'}


def final_models(X,y,seed):
 """Same fixed final predictors independent of query policy; no test selection."""
 return {
  'raw_rbf':SVC(C=2.,kernel='rbf').fit(X,y),
  'signed_relation_rbf':Pipeline([('relations',RelationGrammar('signed',6)),('model',SVC(C=2.,kernel='rbf'))]).fit(X,y),
  'raw_forest':RandomForestClassifier(n_estimators=100,min_samples_leaf=2,random_state=seed,n_jobs=1).fit(X,y),
 }


def run(task,seed,policy,verbose=False):
 if task not in TASKS or seed not in SEEDS or policy not in POLICIES:raise ValueError('NOT_IN_PREREGISTERED_PROTOCOL')
 start=perf_counter()
 owner=ArchivedOwner(task,seed)
 public=owner.visible();ids=list(public)
 scaler=finite_scale(np.asarray([public[i] for i in ids]))
 scaled=scaler.transform(np.asarray([public[i] for i in ids]))
 X={idx:scaled[j] for j,idx in enumerate(ids)}
 chosen=[];labs=[];evidence=[];ledger=Lineage()
 models=None;last_fit=-1;experience={};refuted=0;survivors=0
 snapshots=[];source_events=[];fits=0;bootstrap_oneclass=0
 for step in range(BUDGET):
  available=sorted(set(X)-set(chosen))
  # Common first 12 source questions. After that an unfit committee (one class)
  # is handled with extra geometry-only observations and declared in the receipt.
  if step>=BOOTSTRAP and policy in ('raw_margin','raw_committee','counterexample_relational') and len(set(labs))>1 and (models is None or step-last_fit>=REFIT_EVERY):
   train=np.asarray([X[i] for i in chosen]);y=np.asarray(labs)
   models=committee(policy,train,y,seed)
   fits+=len(models);last_fit=step
   for key in models:experience.setdefault(key,[0,0])
  if step>=BOOTSTRAP and len(set(labs))<2:bootstrap_oneclass+=1
  row,proposal=proposed_query(policy,available,chosen,X,seed,models,experience,step)
  # Commit BEFORE reading this row's archived label.
  before={'schema':SCHEMA,'source':task,'seed':seed,'policy':policy,'step':step+1,
          'row_id':int(row),'observations_before':owner.queries,
          'source_revision':owner.revision,'observed_ancestry_sha256':seal([r['sha256'] for r in evidence]),
          'hypothesis':proposal,'status':'PROPOSED_BEFORE_SOURCE_QUERY'}
  before_sha=seal(before)
  # Register local claims only with previously witnessed supports, not the
  # new label being queried. These remain hypothetical until adjudication.
  claims=[]
  for key,pred in proposal['committee_votes'].items():
   claim_id=f'prediction:{step+1}:{key}'
   ledger.claim(claim_id,[['fact:'+str(i) for i in range(1,step+1)]])
   claims.append((claim_id,key,int(pred)))
  observed=owner.query(row)
  if not owner.verify(observed):raise ValueError('ARCHIVE_RECHECK_FAILED')
  ledger.observation('fact:'+str(step+1),observed,owner)
  correct=[];updates=[]
  for claim_id,key,pred in claims:
   match=pred==observed['label']
   ledger.resolve(claim_id,'OBSERVED_MATCH' if match else 'REFUTED_LOCAL_PREDICTION')
   experience[key][0 if match else 1]+=1
   if match:correct.append(claim_id)
   else:refuted+=1
   updates.append({'model':key,'predicted':pred,'verdict':ledger.nodes[claim_id]['verdict']})
  if correct:
   ledger.claim('surviving:'+str(step+1),[[id] for id in correct],claim_kind='ALTERNATIVE_LOCAL_JUSTIFICATION')
   assert ledger.supported('surviving:'+str(step+1))
   survivors+=1
  chosen.append(row);labs.append(observed['label']);evidence.append(observed)
  source_events.append({'prequery_sha256':before_sha,'prequery':before,'source_receipt':observed,
                        'refutations':updates})
  if step+1 in CHECKPOINTS:
   if len(set(labs))==2:
    fm=final_models(np.asarray([X[i] for i in chosen]),np.asarray(labs),seed)
    fits+=len(fm)
    snapshots.append((step+1,fm,seal([r['sha256'] for r in evidence])))
   else:
    snapshots.append((step+1,None,seal([r['sha256'] for r in evidence])))
 assert owner.queries==BUDGET and len(set(chosen))==BUDGET
 assert not set(chosen)&set(owner.test) and not set(chosen)&set(owner.tune)
 owner.freeze()
 # After query policy, all models, and evidence ancestry are frozen, score
 # unseen heldout labels ONCE per checkpoint; no acquisition after this point.
 scores=[]
 for q,mod,digest in snapshots:
  outcome=owner.score(mod,scaler) if mod is not None else {'HOLD_NO_TWO_CLASSES':None}
  scores.append({'labels':q,'models':outcome,'evidence_sha256':digest})
 lineage=ledger.receipt()
 assert check_receipt(lineage)
 packet={'schema':SCHEMA,'source':task,'seed':seed,'policy':policy,'archive_revision':owner.revision,
         'query_budget':BUDGET,'test_size':len(owner.test),'source_queries':owner.queries,
         'acquired_row_ids':chosen,'prequery_sha256s':[e['prequery_sha256'] for e in source_events],
         'source_receipt_sha256s':[e['source_receipt']['sha256'] for e in source_events],
         'snapshots':scores,'local_refutations':refuted,'surviving_local_alternatives':survivors,
         'committee_model_fits':fits,'bootstrap_oneclass_overflow':bootstrap_oneclass,
         'lineage_sha256':lineage['sha256'],'frozen_before_scoring':True,
         'wall_seconds':round(perf_counter()-start,3),
         'epistemic_status':'HISTORICAL_OFFLINE_RESEARCH_HOLD'}
 packet['packet_sha256']=seal({k:v for k,v in packet.items() if k!='wall_seconds'})
 if verbose:
  packet['query_proof']=source_events
  packet['lineage_proof']=lineage
 return packet


def summarize(packets):
 summary={}
 for task in TASKS:
  for policy in POLICIES:
   cases=[p for p in packets if p['source']==task and p['policy']==policy]
   if not cases:continue
   out={'cases':len(cases),'fits':sum(x['committee_model_fits'] for x in cases),
        'seconds':round(sum(x['wall_seconds'] for x in cases),3)}
   for checkpoint in CHECKPOINTS:
    for model in ['raw_rbf','signed_relation_rbf','raw_forest']:
     vals=[next(z for z in c['snapshots'] if z['labels']==checkpoint)['models'].get(model) for c in cases]
     if all(v is not None for v in vals):
      out[f'{model}_q{checkpoint}']={'balanced_accuracy_mean':round(sum(v['balanced_accuracy'] for v in vals)/len(vals),6),
                        'correct_total':sum(v['correct'] for v in vals),'predictions_total':sum(v['n'] for v in vals)}
   summary.setdefault(task,{})[policy]=out
 # Primary: compare per-domain mean raw RBF at 50 to best classical acquisition.
 verdict={};advantages=[]
 for task in TASKS:
  rows=summary[task]; own=rows['counterexample_relational']['raw_rbf_q50']['balanced_accuracy_mean']
  choices={p:rows[p]['raw_rbf_q50']['balanced_accuracy_mean'] for p in POLICIES[:-1]}
  strongest=max(choices,key=lambda p:choices[p]); gap=round(own-choices[strongest],6)
  verdict[task]={'motif':own,'best_classical_policy':strongest,'best_classical':choices[strongest],
                 'balanced_accuracy_gap':gap};advantages.append(gap)
 result={'predeclared_primary_success':all(x>0 for x in advantages) and sum(advantages)/len(advantages)>=0.02,
         'per_domain':verdict,'mean_domain_gap':round(sum(advantages)/len(advantages),6),
         'warning':'Repeated historical holdouts, not blinded independent patient/handwriting units'}
 return summary,result


def main():
 p=argparse.ArgumentParser();p.add_argument('--task',choices=TASKS);p.add_argument('--seed',type=int,choices=SEEDS);p.add_argument('--policy',choices=POLICIES);p.add_argument('--verbose',action='store_true');args=p.parse_args()
 if not (args.task and args.seed is not None and args.policy):p.error('--task, --seed, --policy all required')
 print(json.dumps(run(args.task,args.seed,args.policy,args.verbose),sort_keys=True,indent=2))

if __name__=='__main__':main()
