"""FIELD-003: one witnessed biological/chemical record -> frozen, bounded probe composition.

Offline research on independently collected UCI Iris/Wine data mirrored by sklearn.
All hypotheses remain predictive; no causal/physical intervention claims.
Only the OWNER interface can reveal a label. The learner sees unlabeled measurements.
"""
from __future__ import annotations
import csv
import hashlib
import json
import math
from pathlib import Path
from dataclasses import dataclass

HERE = Path(__file__).resolve().parent
SCHEMA = 'motif.field003.v1'
DATASETS = {
 'iris': {'file':'iris.csv','rows':150,'cols':4,
          'sha256':'f13ffa8fdd56fd8e6c8d16d4081a3fbd3114bcd0aae4256c43205169cd9d1449',
          'source':'https://archive.ics.uci.edu/dataset/53/iris', 'target':2},
 'wine': {'file':'wine_data.csv','rows':178,'cols':13,'sha256':'10e8a802908b34f86e5da8ce962f3c806694bc98450a18f61851af59f324bede',
          'source':'https://archive.ics.uci.edu/dataset/109/wine','target':2},
}
SEEDS = [11,23,37]
BUDGETS = {'iris':60,'wine':75}

def canonical(data):
 return json.dumps(data,sort_keys=True,separators=(',',':'),allow_nan=False)
def sha(data):
 return hashlib.sha256(canonical(data).encode()).hexdigest()

def load(name):
 spec=DATASETS[name]
 raw=(HERE/spec['file']).read_bytes()
 if hashlib.sha256(raw).hexdigest()!=spec['sha256']:
  raise ValueError('DATASET_SOURCE_HASH_CHANGED')
 contents=list(csv.reader(raw.decode().splitlines()))
 if tuple(map(int,contents[0][:2]))!=(spec['rows'],spec['cols']):
  raise ValueError('DATASET_HEADER_CHANGED')
 values=[(tuple(float(v) for v in row[:-1]),int(row[-1])) for row in contents[1:] if row]
 if len(values)!=spec['rows'] or any(len(x)!=spec['cols'] for x,_ in values):
  raise ValueError('DATASET_DIMENSIONS_CHANGED')
 if any(not all(math.isfinite(x) for x in xx) or lab not in (0,1,2) for xx,lab in values):
  raise ValueError('UNEXPECTED_VALUE')
 return values


def partition(n,name,seed):
 """Partition using row IDs only, not class or features: 60% pool, 20% tune, 20% test."""
 ranks=sorted(range(n),key=lambda i:sha([SCHEMA,'split',name,seed,i]))
 train=int(.6*n); tune=int(.2*n)
 return sorted(ranks[:train]),sorted(ranks[train:train+tune]),sorted(ranks[train+tune:])

class Owner:
 """Separate source-owner simulator: reads fixed, historical labelled rows.

 This is NOT a live botanist or physical experiment. It is an offline sealed-label query API.
 """
 def __init__(self,name,seed):
  self.name=name;self.spec=DATASETS[name];self.rows=load(name)
  self.pool,self.tune,self.test=partition(len(self.rows),name,seed)
  self.seen=set();self.query_count=0
  self.revision=self.spec['sha256']
 def public_pool(self):
  return {i:self.rows[i][0] for i in self.pool}
 def query(self,i):
  if i not in self.pool or i in self.seen:raise ValueError('UNAUTHORIZED_OR_DUPLICATE_LABEL_REQUEST')
  self.seen.add(i);self.query_count+=1
  event={'schema':SCHEMA,'dataset':self.name,'source_revision':self.revision,
         'row_id':i,'measurements':list(self.rows[i][0]),
         'observed_class':self.rows[i][1], 'source_kind':'ARCHIVED_DATASET_LABEL'}
  return {**event,'content_sha256':sha(event)}
 def verify(self,receipt):
  if not isinstance(receipt,dict):return False
  payload={k:v for k,v in receipt.items() if k!='content_sha256'}
  try:
   i=payload['row_id'];value=self.rows[i]
   return (receipt['content_sha256']==sha(payload)
       and 0<=i<len(self.rows) and payload['measurements']==list(value[0])
       and payload['observed_class']==value[1]
       and payload['source_revision']==self.revision
       and payload['dataset']==self.name
       and payload['schema']==SCHEMA
       and payload['source_kind']=='ARCHIVED_DATASET_LABEL')
  except (KeyError,IndexError,TypeError,ValueError):return False

def gini(labels):
 if not labels:return 0.
 p=sum(labels)/len(labels)
 return 2*p*(1-p)

@dataclass(frozen=True)
class Node:
 pred: int
 index: int=-1
 boundary: float=0.
 left:object=None
 right:object=None

def classify(tree,x):
 while tree.index>=0:
  tree=tree.left if x[tree.index]<=tree.boundary else tree.right
 return tree.pred

def depth(tree):
 return 0 if tree.index<0 else 1+max(depth(tree.left),depth(tree.right))

def used_features(tree):
 if tree.index<0:return []
 return [tree.index]+used_features(tree.left)+used_features(tree.right)

def describe(tree,names):
 if tree.index<0:return {'predict':tree.pred}
 return {'if':f'{names[tree.index]} <= {tree.boundary:.5g}',
         'then':describe(tree.left,names),'else':describe(tree.right,names)}

def fit_tree(X,y,max_depth=1,minleaf=3):
 """Standard deterministic CART/Gini, no discovered new algorithm."""
 if not X or len(X)!=len(y):raise ValueError('empty/inconsistent labeled examples')
 def grow(ids,level):
  votes=sum(y[i] for i in ids); pred=int(2*votes>len(ids))
  if level>=max_depth or len(ids)<2*minleaf or votes in (0,len(ids)):
   return Node(pred)
  impurity=gini([y[i] for i in ids]); winner=None
  for col in range(len(X[0])):
   order=sorted(ids,key=lambda i:(X[i][col],i))
   ones=0;total=sum(y[i] for i in ids)
   for k in range(1,len(order)):
    ones+=y[order[k-1]]
    if k<minleaf or len(order)-k<minleaf: continue
    a,b=X[order[k-1]][col],X[order[k]][col]
    if a==b:continue
    nleft=k;nright=len(order)-k
    weighted=(nleft*gini([1]*ones+[0]*(nleft-ones))+nright*gini([1]*(total-ones)+[0]*(nright-total+ones)))/len(order)
    gain=impurity-weighted
    if gain>1e-10:
     key=(-round(gain,12),col,(a+b)/2)
     if winner is None or key<winner[0]: winner=(key,col,(a+b)/2,order[:k],order[k:])
  if winner is None:return Node(pred)
  _,j,t,left,right=winner
  return Node(pred,j,t,grow(left,level+1),grow(right,level+1))
 return grow(list(range(len(y))),0)

def xscale(public):
 """Unlabeled pool-only scaling; never computed with tune/test rows."""
 k=len(next(iter(public.values())))
 vals=[ [v[j] for v in public.values()] for j in range(k)]
 mu=[sum(v)/len(v) for v in vals]
 std=[max(math.sqrt(sum((x-mu[j])**2 for x in vals[j])/len(vals[j])),1e-9) for j in range(k)]
 return mu,std

def normalize(x,mu,std):return tuple((v-mu[i])/std[i] for i,v in enumerate(x))

def hypotheses(X,y,k):
 """Rank primitive single measurements by observed training Gini, no holdout."""
 scored=[]
 for j in range(k):
  t=fit_tree([(x[j],) for x in X],y,max_depth=1)
  err=sum(classify(t,(x[j],))!=v for x,v in zip(X,y))
  scored.append((err,j))
 return [j for _,j in sorted(scored)[:min(6,k)]]

def engineer_features(rows,source_k,chosen=()):
 """Evolved, bounded DSL: z_i - z_j and z_i + z_j for a ranked subset.

 The operators and search procedure were authored before labels were queried.
 """
 desc=[f'z{i}' for i in range(source_k)]
 added=[]
 for pos,i in enumerate(chosen):
  for j in chosen[pos+1:]:
   for sign in ('-','+'):
    desc.append(f'z{i}{sign}z{j}');added.append((i,j,sign))
 return [tuple(x)+tuple((x[i]-x[j] if sign=='-' else x[i]+x[j]) for i,j,sign in added) for x in rows],desc

def farthest_next(public,labeled_ids):
 """Pool-only geometric coverage; cannot inspect source labels."""
 available=[i for i in sorted(public) if i not in labeled_ids]
 if not labeled_ids:return available[0]
 return max(available,key=lambda i:(
  min(sum((public[i][j]-public[k][j])**2 for j in range(len(public[i]))) for k in labeled_ids),-i))

def next_request(public,chosen,stump,composition,features,mu,std):
 candidates=[i for i in sorted(public) if i not in chosen]
 if len(chosen)<12 or stump is None:return farthest_next(public,chosen)
 def score(i):
  x=public[i]; grow_x=normalize(x,mu,std)
  comp_x=engineer_features([grow_x],len(x),features)[0][0]
  pa=classify(stump,grow_x)
  pb=classify(composition,comp_x) if composition else pa
  # First seek disagreements, then small tree split margin on the original observed features.
  boundaries=[]
  def collect(t):
   if t.index>=0:
    boundaries.append(abs(comp_x[t.index]-t.boundary))
    collect(t.left);collect(t.right)
  if composition:collect(composition)
  else:collect(stump)
  margin=min(boundaries) if boundaries else 1000
  # tie-break reproducible and labels are never used to score unqueried candidates.
  return (int(pa!=pb),-margin,-i)
 return max(candidates,key=score)

def _fit_from_receipts(receipts,public,mu,std,expanded):
 X=[normalize(public[r['row_id']],mu,std) for r in receipts]
 y=[int(r['observed_class']==2) for r in receipts]
 stump=fit_tree(X,y,1)
 use=hypotheses(X,y,len(mu)) if expanded else []
 Xc,names=engineer_features(X,len(mu),use)
 tree=fit_tree(Xc,y,2) if expanded else None
 return stump,tree,use,names

def evaluate(tree,ids,owner,mu,std,features=()):
 samples=[owner.rows[i] for i in ids]
 X=[normalize(x,mu,std) for x,y in samples]
 X=engineer_features(X,len(mu),features)[0]
 preds=[classify(tree,x) for x in X]
 ys=[int(y==2) for x,y in samples]
 return {'correct':sum(a==b for a,b in zip(preds,ys)),'total':len(ys),
         'accuracy':round(sum(a==b for a,b in zip(preds,ys))/len(ys),6),
         'false_positive':sum(a==1 and b==0 for a,b in zip(preds,ys)),
         'false_negative':sum(a==0 and b==1 for a,b in zip(preds,ys))}

def run(name,seed,budget,mode='active'):
 owner=Owner(name,seed); public=owner.public_pool();mu,std=xscale(public)
 selected=[];receipts=[];steps=[];checkpoints=[];checkpoint_models=[];grew=False;trigger=None
 stump=composition=None;features=();names=[f'z{i}' for i in range(len(mu))]
 for t in range(budget):
  # Strong random baseline still keeps one sealed starting fact, just samples random thereafter.
  if mode=='random':
   available=[i for i in public if i not in selected]
   choice=min(available,key=lambda i:sha(['passive',name,seed,i]))
  else:choice=next_request(public,selected,stump,composition,features,mu,std)
  proposed={'step':t,'row_id':choice,'policy':mode,'before_observation':True,
            'hypothesis_stage': 'COMPOSED' if grew else 'UNARY',
            'source_queries_before':owner.query_count}
  receipt=owner.query(choice)
  if not owner.verify(receipt):raise ValueError('INVALID_OWNER_RECEIPT')
  assert receipt['row_id']==proposed['row_id']
  steps.append({**proposed,'receipt_sha256':receipt['content_sha256']})
  selected.append(choice);receipts.append(receipt)
  stump,composition,features,names=_fit_from_receipts(receipts,public,mu,std,grew)
  # Explicit evidence-trigger for insufficiency of a single-threshold language.
  # This is TRAINING error; not a proof that a new grammar generalizes.
  if not grew and len(receipts)>=18:
   yy=[int(r['observed_class']==2) for r in receipts]
   X=[normalize(public[r['row_id']],mu,std) for r in receipts]
   mistakes=sum(classify(stump,x)!=truth for x,truth in zip(X,yy))
   if mistakes>=3 and len(set(yy))==2:
    grew=True;trigger={'at_source_queries':len(receipts),'stump_training_errors':mistakes,
                       'status':'PROPOSED_COMPOSITION_NOT_FACT'}
    stump,composition,features,names=_fit_from_receipts(receipts,public,mu,std,grew)
  # Fixed checkpoint schedule; no heldout labels or scores are inspected here.
  if len(receipts) in (20,40,budget):
   if not grew: checkpoint_model=stump; check_features=(); check_names=[f'z{i}' for i in range(len(mu))]
   else:checkpoint_model=composition;check_features=tuple(features);check_names=names
   checkpoint_models.append((len(receipts),checkpoint_model,check_features))
   checkpoints.append({'queries':len(receipts),'grammar':'COMPOSED' if grew else 'UNARY',
     'program':describe(checkpoint_model,check_names),
     'generated_features':[check_names[j] for j in set(used_features(checkpoint_model)) if j>=len(mu)]})
 assert owner.query_count==budget
 # Selection and model fit occurred without viewing the tuning or test labels.
 # Freeze model and proof packet before any graded inspection.
 if not grew:
  composition=stump;features=();names=[f'z{i}' for i in range(len(mu))]
 y=[int(r['observed_class']==2) for r in receipts]
 X=[normalize(public[r['row_id']],mu,std) for r in receipts]
 # A strong, independent classical depth-3 CART on exactly same labeled data, raw features only.
 cart=fit_tree(X,y,3)
 model={'stump':describe(stump,[f'z{i}' for i in range(len(mu))]),
        'composed':describe(composition,names),
        'classical_depth3':describe(cart,[f'z{i}' for i in range(len(mu))]),
        'synthesized_operators':[names[j] for j in sorted(set(used_features(composition))) if j>=len(mu)],
        'composition_tree_depth':depth(composition)}
 freeze={'schema':SCHEMA,'dataset':name,'source':DATASETS[name]['source'],
         'source_sha256':owner.revision,'seed':seed,'label_budget':budget,'mode':mode,
         'starting_fact':receipts[0],'probe_traces':steps,'receipts':receipts,
         'grammar_trigger':trigger,'checkpoints':checkpoints,'model':model}
 freeze['packet_sha256']=sha(freeze)
 # Only NOW score on heldout labels. Tuning set also graded, never used to select model.
 score={
  'stump':evaluate(stump,owner.test,owner,mu,std),
  'composed':evaluate(composition,owner.test,owner,mu,std,features),
  'classical_depth3':evaluate(cart,owner.test,owner,mu,std),
  'tune_stump':evaluate(stump,owner.tune,owner,mu,std),
  'tune_composed':evaluate(composition,owner.tune,owner,mu,std,features),
  'tune_classical_depth3':evaluate(cart,owner.tune,owner,mu,std),
 }
 score['learning_curve']=[{'queries':q,'test':evaluate(t,owner.test,owner,mu,std,feat)} for q,t,feat in checkpoint_models]
 assert len(owner.seen)==budget and set(owner.seen).isdisjoint(set(owner.tune+owner.test))
 return {'proof':freeze,'score':score,'pool_size':len(owner.pool),
         'tune_size':len(owner.tune),'test_size':len(owner.test)}

def verify_packet(packet):
 try:
  if packet['packet_sha256']!=sha({k:v for k,v in packet.items() if k!='packet_sha256'}):return False
  owner=Owner(packet['dataset'],packet['seed'])
  if packet['source_sha256']!=owner.revision:return False
  for r in packet['receipts']:
   if not owner.verify(r):return False
  return packet==run(packet['dataset'],packet['seed'],packet['label_budget'],packet['mode'])['proof']
 except (KeyError,ValueError,TypeError):return False

def experiment():
 results=[]
 for name in ('iris','wine'):
  for seed in SEEDS:
   for mode in ('active','random'):
    results.append(run(name,seed,BUDGETS[name],mode))
 rows=[{'dataset':r['proof']['dataset'],'seed':r['proof']['seed'],
        'mode':r['proof']['mode'],'query_budget':r['proof']['label_budget'],
        'trigger':r['proof']['grammar_trigger'],'model':r['proof']['model'],
        'packet_sha256':r['proof']['packet_sha256'],
        'heldout':{k:v for k,v in r['score'].items() if not k.startswith('tune_')},
        'tuning':{k:v for k,v in r['score'].items() if k.startswith('tune_')},
        'learning_curve':r['score']['learning_curve']} for r in results]
 summary={}
 for name in ('iris','wine'):
  summary[name]={}
  for mode in ('active','random'):
   rr=[r for r in rows if r['dataset']==name and r['mode']==mode]
   summary[name][mode]={
      'grammar_triggered':sum(x['trigger'] is not None for x in rr),
      'nontrivial_composed_tree':sum(x['model']['composition_tree_depth']>1 for x in rr),
      'selected_generated_features':sum(bool(x['model']['synthesized_operators']) for x in rr),
      'scores':{algo: {'correct':sum(x['heldout'][algo]['correct'] for x in rr),
                       'total':sum(x['heldout'][algo]['total'] for x in rr)}
                for algo in ('stump','composed','classical_depth3')}
   }
 return {'experiment':'FIELD-003','protocol':SCHEMA,
         'evidence_scope':'fixed, retrospectively collected UCI biology and chemistry; offline sealed labels; NO physical interventions',
         'source_files':{name:{k:v for k,v in x.items() if k!='target'} for name,x in DATASETS.items()},
         'seeds':SEEDS,'per_case':rows,'summary':summary,
         'limitations':['Class is observed in the historical source, not a newly discovered physical fact',
          'Rules are predictive decision trees, not discovered causal laws',
          'Methods and threshold heuristics are human-authored classical algorithms',
          'Public, old benchmark datasets have potential prior exposure and selection bias',
          'No method was autonomously invented outside authored operator grammar',
          'A checksum detects drift but does not authenticate primary source authors']}

if __name__=='__main__':
 print(json.dumps(experiment(),indent=2,sort_keys=True))
