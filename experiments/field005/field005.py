"""FIELD-005 — RELATIONAL INQUIRY DIVIDEND.

Source-pinned historical archived labels, prospectively chosen queries, and
fixed policies compared using same label budgets. Pure offline learning study.
No physical measurement, causal proof, general AGI, or live experiment.
"""
from __future__ import annotations
import hashlib, json, sys, math, argparse
from dataclasses import dataclass
from pathlib import Path
from collections import Counter
import numpy as np
from sklearn.base import clone
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.pipeline import Pipeline

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent/'field003'))
sys.path.insert(0, str(HERE.parent/'field004'))
import field003 as f3
from field004 import RelationGrammar

SCHEMA = 'motif.field005.v1'
POLICIES = ('random','geometry','raw_margin','raw_committee','relation_frontier')
DATASETS = ('iris','wine')
DEVELOPMENT_SEEDS = (11,23,131)   # 131 was inspected during implementation; never counted as audit
AUDIT_SEEDS = (137,139,149)   # not inspected before policy and comparison protocol freeze
BUDGETS = {'iris':60,'wine':75}
CHECKPOINTS = {'iris':(12,25,40,60), 'wine':(12,25,40,75)}
REFIT_INTERVAL=3
WARMUP=12


def digest(obj):
    return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()

def standardize(pool):
    """Fit once to training-pool UNLABELED features; not tune/test features."""
    x=np.array(list(pool.values()), dtype=float)
    mu=x.mean(axis=0); st=np.maximum(x.std(axis=0),1e-9)
    return {i:(np.asarray(v,dtype=float)-mu)/st for i,v in pool.items()}, mu, st

def min_distance(query, known, X):
    if not known:return 0.
    d=[float(np.dot(X[query]-X[k], X[query]-X[k])) for k in known]
    return min(d)

def pool_neighbors(X):
    """Unsupervised density; absent from labels/test split."""
    ids=sorted(X)
    a=np.asarray([X[i] for i in ids])
    d=np.sum((a[:,None,:]-a[None,:,:])**2,axis=2)
    np.fill_diagonal(d,np.inf)
    d.sort(axis=1)
    density={i:1.0/(1.0+float(np.sqrt(d[k,:min(5,len(ids)-1)]).mean())) for k,i in enumerate(ids)}
    return density

def fit_acquisition_models(acquired,y,policy,seed):
    """Only verified acquired labels reach this function."""
    if len(set(y))<2:return None
    raw=SVC(kernel='rbf',C=2.0,gamma='scale').fit(acquired,y)
    if policy=='raw_margin':return {'raw':raw}
    if policy=='raw_committee':
        rf=RandomForestClassifier(n_estimators=45,min_samples_leaf=2,random_state=seed,n_jobs=1).fit(acquired,y)
        return {'raw':raw,'forest':rf}
    if policy=='relation_frontier':
        # Grammar chosen using only the acquired labels and inherited FIELD-004 code.
        signed=Pipeline([('relations',RelationGrammar('signed',top=6)),('classifier',SVC(kernel='rbf',C=2.0,gamma='scale'))]).fit(acquired,y)
        interaction=Pipeline([('relations',RelationGrammar('interactions',top=6)),('classifier',SVC(kernel='rbf',C=2.0,gamma='scale'))]).fit(acquired,y)
        return {'raw':raw,'signed':signed,'interaction':interaction}
    return None

def score_query(policy, unqueried, acquired, xmap, density, models):
    """No access to oracle labels. All scores derived from unlabeled pool + trained models.

    The relational method seeks a candidate where alternate evidence-derived
    relations disagree, then seeks uncertainty and coverage. Classical
    uncertainty/committee methods get access to the same unlabeled pool.
    """
    if policy=='random':raise ValueError('random queries use independent rank')
    # geometry-only bootstrap and geometry comparison
    if models is None or policy=='geometry':
        return max(unqueried,key=lambda i:(min_distance(i,acquired,xmap),density[i],-i))
    xx=np.asarray([xmap[i] for i in unqueried])
    svm=models['raw']
    raw_margin=np.abs(svm.decision_function(xx))
    raw_pred=svm.predict(xx)
    # Candidate order always explicit; no hidden oracle inspection.
    if policy=='raw_margin':
        return max(range(len(unqueried)),key=lambda j:(-float(raw_margin[j]),
                   math.log1p(min_distance(unqueried[j],acquired,xmap)), -unqueried[j]))
    if policy=='raw_committee':
        forest_pred=models['forest'].predict(xx)
        return max(range(len(unqueried)),key=lambda j:(int(raw_pred[j]!=forest_pred[j]),
                  -float(raw_margin[j]), math.log1p(min_distance(unqueried[j],acquired,xmap)),-unqueried[j]))
    if policy=='relation_frontier':
        p1=models['signed'].predict(xx)
        p2=models['interaction'].predict(xx)
        m1=np.abs(models['signed'].decision_function(xx))
        m2=np.abs(models['interaction'].decision_function(xx))
        # Each uncertain relation proposal or prediction disagreement defines
        # a future question. Maximize distinct disagreement, then minimum
        # relational margin, with geometric novelty as tie-breaker.
        return max(range(len(unqueried)), key=lambda j:(
           int(p1[j]!=p2[j])+int(p1[j]!=raw_pred[j])+int(p2[j]!=raw_pred[j]),
           -float(min(m1[j],m2[j])),
           math.log1p(min_distance(unqueried[j],acquired,xmap)),
           density[unqueried[j]], -unqueried[j]))
    raise ValueError('unsupported policy')

def select_query(policy,known,xmap,seed,fit=None,density=None):
    available=sorted(set(xmap)-set(known))
    if not available:raise ValueError('budget exhausted')
    if policy=='random':
        return min(available,key=lambda i:(digest(['field005-random',seed,i]),i))
    if density is None:density=pool_neighbors(xmap)
    choice=score_query(policy,available,known,xmap,density,fit)
    return available[choice] if isinstance(choice,int) and (fit is not None and policy not in ('geometry',)) else choice


def raw_estimators(seed):
    return {
        'rbf_svc':SVC(C=2.0,gamma='scale',kernel='rbf'),
        'linear_svc':SVC(C=1.0,kernel='linear'),
        'rf':RandomForestClassifier(n_estimators=60,min_samples_leaf=2,random_state=seed,n_jobs=1),
        'extra_trees':ExtraTreesClassifier(n_estimators=60,min_samples_leaf=2,random_state=seed,n_jobs=1),
        'logistic':LogisticRegression(C=1.0,max_iter=1500)
    }

def relational_estimators(seed):
    return {
        'signed_svm':Pipeline([('relations',RelationGrammar('signed',top=6)),('fit',SVC(C=2.0,gamma='scale',kernel='rbf'))]),
        'interaction_svm':Pipeline([('relations',RelationGrammar('interactions',top=6)),('fit',SVC(C=2.0,gamma='scale',kernel='rbf'))]),
        'interaction_forest':Pipeline([('relations',RelationGrammar('interactions',top=6)),('fit',RandomForestClassifier(n_estimators=60,min_samples_leaf=2,random_state=seed,n_jobs=1))]),
    }

def select_model(models,X,y,seed):
    counts=Counter(y);folds=min(4,min(counts.values()))
    if folds < 2:raise ValueError('insufficient class coverage')
    cv=StratifiedKFold(n_splits=folds,shuffle=True,random_state=seed)
    scores={name:round(float(np.mean(cross_val_score(mod,X,y,cv=cv,scoring='balanced_accuracy'))),6) for name,mod in models.items()}
    selected=max(models,key=lambda name:(scores[name],-list(models).index(name)))
    return selected,scores,clone(models[selected]).fit(X,y)

def predicted_score(model,X,y):
    pred=model.predict(X)
    return {'correct':int(np.sum(pred==y)),'total':len(y),
            'accuracy':round(float(np.mean(pred==y)),6)}

def run(name,seed,policy,budget=None):
    if policy not in POLICIES or name not in DATASETS:raise ValueError('unsupported case')
    budget=BUDGETS[name] if budget is None else int(budget)
    if not 1<=budget<=BUDGETS[name]:raise ValueError('bad budget')
    owner=f3.Owner(name,seed);pool=owner.public_pool()
    xmap,mu,std=standardize(pool);density=pool_neighbors(xmap)
    selected=[];receipts=[];events=[];models=None
    acquired_y=[];checkpoints=[];checkpoint_fits=[];last_refit=-1
    for step in range(budget):
        if (policy not in ('random','geometry') and step>=WARMUP
                and len(set(acquired_y))==2 and (models is None or step-last_refit>=REFIT_INTERVAL)):
            models=fit_acquisition_models(np.asarray([xmap[i] for i in selected]),
                                          np.asarray(acquired_y),policy,seed)
            last_refit=step
        choice=select_query(policy,selected,xmap,seed,models,density)
        proposal={'query':step+1,'row_id':choice,'policy':policy,'source_queries_before':owner.query_count,
                  'acquired_before_sha256':digest(selected),
                  'query_status':'PROPOSED_BEFORE_LABEL',
                  'relation_model_count':len(models or {})}
        # Preserve the particular question MOTIF proposed, including what
        # its current evidence-derived relations predict *before* the answer.
        hypotheses={}
        if models:
            point=np.asarray([xmap[choice]])
            for label,trained in models.items():
                hypotheses[label]={'pred':int(trained.predict(point)[0]),
                                   'uncertainty_margin':round(float(abs(trained.decision_function(point)[0])),6)
                                   if hasattr(trained,'decision_function') else None}
                if hasattr(trained,'named_steps'):
                    hypotheses[label]['selected_source_axes']=list(trained.named_steps['relations'].indices_)
        proposal['pre_query_hypotheses']=hypotheses
        receipt=owner.query(choice)
        if not owner.verify(receipt):raise AssertionError('owner receipt mismatch')
        assert proposal['row_id']==receipt['row_id']
        selected.append(choice);receipts.append(receipt)
        acquired_y.append(int(receipt['observed_class']==2))
        events.append({**proposal,'source_receipt_sha256':receipt['content_sha256']})
        if step+1 in CHECKPOINTS[name]:
            checkpoint_x=np.asarray([xmap[i] for i in selected]); checkpoint_y=np.asarray(acquired_y)
            snapshot={'query_count':step+1,'labels_positive':sum(acquired_y),
                      'source_receipts_sha256':digest([r['content_sha256'] for r in receipts]),
                      'trained_id_sequence_sha256':digest(selected)}
            if len(set(acquired_y))==2 and min(Counter(acquired_y).values())>=2:
                cn,cc,cm=select_model(raw_estimators(seed),checkpoint_x,checkpoint_y,seed)
                rn,rc,rm=select_model(relational_estimators(seed),checkpoint_x,checkpoint_y,seed)
                snapshot['raw_selected']=cn;snapshot['relational_selected']=rn
                snapshot['raw_cv']=cc;snapshot['relational_cv']=rc
                checkpoint_fits.append((step+1,cm,rm))
            else:
                snapshot['status']='HOLD_INSUFFICIENT_CLASS_DIVERSITY'
            checkpoints.append(snapshot)
    assert owner.query_count==budget and len(set(selected))==budget
    assert not(set(selected)&set(owner.test+owner.tune))
    X=np.asarray([xmap[i] for i in selected]);y=np.asarray(acquired_y)
    # Reuse the frozen last-checkpoint selection; don't recompute/choose
    # from a second fitting run after observation. This also saves CPU.
    if checkpoint_fits and checkpoint_fits[-1][0]==budget:
        raw_name=checkpoints[-1]['raw_selected'];rel_name=checkpoints[-1]['relational_selected']
        raw_cv=checkpoints[-1]['raw_cv'];rel_cv=checkpoints[-1]['relational_cv']
        _,raw,rel=checkpoint_fits[-1]
    else:
        raw_name,raw_cv,raw=select_model(raw_estimators(seed),X,y,seed)
        rel_name,rel_cv,rel=select_model(relational_estimators(seed),X,y,seed)
    model_proof={'dataset':name,'seed':seed,'policy':policy,'budget':budget,
         'source_sha256':owner.revision,
         'data_scope':'only train-pool unlabeled measurements and queried training labels',
         'ids_ordered':selected,'source_receipts_sha256':[r['content_sha256'] for r in receipts],
         'queried_positive':int(sum(y)),
         'raw_classical_cv':raw_cv,'relational_cv':rel_cv,
         'selected_raw':raw_name,'selected_relational':rel_name,
         'events':events,'checkpoints':checkpoints,
         'audit_role':'exploratory' if seed in DEVELOPMENT_SEEDS else 'frozen_seed_audit',
         'schema':SCHEMA}
    model_proof['frozen_sha256']=digest(model_proof)
    # Evaluation data first accessed *after* selections and proof freeze.
    # The tuning slice is reported but never used for model selection.
    def eval_part(ids):
        arr=np.asarray([f3.normalize(owner.rows[i][0],mu,std) for i in ids])
        truth=np.asarray([int(owner.rows[i][1]==2) for i in ids])
        return {'raw':predicted_score(raw,arr,truth),'relational':predicted_score(rel,arr,truth)}
    tune=eval_part(owner.tune);test=eval_part(owner.test)
    test_curve=[]
    for count,mraw,mrel in checkpoint_fits:
        xx=np.asarray([f3.normalize(owner.rows[i][0],mu,std) for i in owner.test])
        truth=np.asarray([int(owner.rows[i][1]==2) for i in owner.test])
        test_curve.append({'query_count':count,'raw':predicted_score(mraw,xx,truth),
                           'relational':predicted_score(mrel,xx,truth)})
    return {'proof':model_proof,'tuning':tune, 'test':test, 'test_learning_curve':test_curve}

def cases(name,seed,policies=POLICIES,budget=None):
    return [run(name,seed,p,budget) for p in policies]

def summarize(rows):
    cohorts={'development':DEVELOPMENT_SEEDS,'audit':AUDIT_SEEDS}
    output={}
    for cohort,seeds in cohorts.items():
        output[cohort]={}
        for dataset in DATASETS:
            output[cohort][dataset]={}
            for policy in POLICIES:
                selected=[x for x in rows if x['proof']['dataset']==dataset and
                   x['proof']['seed'] in seeds and x['proof']['policy']==policy]
                if not selected:continue
                output[cohort][dataset][policy]={
                    'n_splits':len(selected),
                    'label_queries_per_split':selected[0]['proof']['budget'],
                    **{m:{'correct':sum(x['test'][m]['correct'] for x in selected),
                          'total':sum(x['test'][m]['total'] for x in selected)} for m in ('raw','relational')}
                }
    return output

def compact(rows):
    return {'schema':SCHEMA,'status':'RESEARCH_HOLD_UNMERGED','policies':POLICIES,
            'source_datasets':'UCI historical Iris/Wine data pinned by FIELD-003',
            'budget':BUDGETS,'development_seeds':DEVELOPMENT_SEEDS,'audit_seeds':AUDIT_SEEDS,
            'comparison':'same unlabeled training pool and equal distinct source-label budgets; identical raw and relational estimator selection menus',
            'summary':summarize(rows),
            'cases':[{'dataset':r['proof']['dataset'],'seed':r['proof']['seed'],
              'policy':r['proof']['policy'],'budget':r['proof']['budget'],
              'source_sha256':r['proof']['source_sha256'],
              'source_receipts_digest':digest(r['proof']['source_receipts_sha256']),
              'selected_ids_digest':digest(r['proof']['ids_ordered']),
              'frozen_sha256':r['proof']['frozen_sha256'],
              'selected_raw':r['proof']['selected_raw'],
              'selected_relation':r['proof']['selected_relational'],
              'raw_cv':r['proof']['raw_classical_cv'],
              'relation_cv':r['proof']['relational_cv'],
              'checkpoints':[{k:v for k,v in snap.items() if k not in ('raw_cv','relational_cv')} for snap in r['proof']['checkpoints']],
              'tuning':r['tuning'],'test':r['test'],
              'test_learning_curve':r['test_learning_curve']} for r in rows],
            'limitations':['public historical datasets, overlapping re-splits, not blinded or independent replications',
                           'all operators and acquisition heuristics classical and programmer supplied',
                           'label inquiries are recorded dataset lookups, not new physical measurements',
                           'holdout aggregate does not prove statistical significance',
                           'no online changes to model code or external execution authority']}

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--dataset',choices=DATASETS)
    parser.add_argument('--seed',type=int)
    parser.add_argument('--policy',choices=POLICIES)
    parser.add_argument('--budget',type=int)
    parser.add_argument('--run-all',action='store_true')
    args=parser.parse_args()
    if args.run_all:
        rows=[run(dataset,seed,policy) for dataset in DATASETS for seed in (*DEVELOPMENT_SEEDS,*AUDIT_SEEDS) for policy in POLICIES]
        print(json.dumps(compact(rows),indent=2,sort_keys=True))
    elif args.dataset and args.seed and args.policy:
        print(json.dumps(run(args.dataset,args.seed,args.policy,args.budget),indent=2,sort_keys=True))
    else:parser.error('specify --run-all or --dataset --seed --policy')
