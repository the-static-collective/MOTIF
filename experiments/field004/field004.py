"""FIELD-004: investigate whether source-witnessed relational apertures outperform
original FIELD-003 single-axis CART, and competitive same-label classical models.

Finite retrospective science. All choices made by training-only CV before test
labels are scored. No new causal law or nonclassical learning algorithm claimed.
"""
from __future__ import annotations
import hashlib, json, sys, subprocess
from collections import Counter
from pathlib import Path
from itertools import combinations

import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin, clone
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'field003'))
import field003 as previous

SCHEMA='motif.field004.v1'
DEV_SEEDS=(11,23,37,53,67,79,83) # includes already inspected seed 83
AUDIT_SEEDS=(97,101,107)  # design frozen before audit scoring; public-data proxy, not blind
SEEDS=DEV_SEEDS+AUDIT_SEEDS
MODES=('active','random')
DATASETS=('iris','wine')


def digest(obj):
    return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()


class RelationGrammar(BaseEstimator, TransformerMixin):
    """Train-fold-only feature/relationship selection; no test-label leakage.
    Grammar contains signed differences/sums and 2-way products, not invented math.
    """
    def __init__(self, kind='signed',top=6):
        self.kind=kind;self.top=top
    def fit(self,X,y=None):
        a=np.asarray(X,dtype=float)
        if a.ndim!=2 or not np.isfinite(a).all():raise ValueError('invalid features')
        if y is None or len(np.unique(y))<2:
            indices=list(range(min(a.shape[1],self.top)))
        else:
            # Only training-fold labels determine selected axes; no tuning/test.
            indices=previous.hypotheses([tuple(row) for row in a],list(map(int,y)),a.shape[1])[:self.top]
        self.indices_=tuple(indices)
        return self
    def transform(self,X):
        a=np.asarray(X,dtype=float)
        columns=[a]
        for i,j in combinations(self.indices_,2):
            columns.append((a[:,i]-a[:,j])[:,None])
            columns.append((a[:,i]+a[:,j])[:,None])
            if self.kind=='interactions':
                columns.append((a[:,i]*a[:,j])[:,None])
        return np.concatenate(columns,axis=1)


def candidates(seed):
    """Frozen finite candidate menu. A matched classical portfolio is NOT weak CART."""
    classical={
        'raw_dt3':DecisionTreeClassifier(max_depth=3,min_samples_leaf=3,random_state=seed),
        'raw_dt5':DecisionTreeClassifier(max_depth=5,min_samples_leaf=2,random_state=seed),
        'raw_rf':RandomForestClassifier(n_estimators=90,min_samples_leaf=2,max_features='sqrt',random_state=seed,n_jobs=1),
        'raw_extratrees':ExtraTreesClassifier(n_estimators=90,min_samples_leaf=2,random_state=seed,n_jobs=1),
        'raw_linear_svm':SVC(kernel='linear',C=1.0),
        'raw_rbf_svm':SVC(kernel='rbf',C=2.0,gamma='scale'),
        'raw_logistic':LogisticRegression(C=1.0,max_iter=2000),
        'raw_knn5':KNeighborsClassifier(n_neighbors=5,weights='distance'),
    }
    motif={
      'relation_signed_dt3':Pipeline([('relations',RelationGrammar('signed')),('fit',DecisionTreeClassifier(max_depth=3,min_samples_leaf=3,random_state=seed))]),
      'relation_signed_dt4':Pipeline([('relations',RelationGrammar('signed')),('fit',DecisionTreeClassifier(max_depth=4,min_samples_leaf=2,random_state=seed))]),
      'relation_signed_rf':Pipeline([('relations',RelationGrammar('signed')),('fit',RandomForestClassifier(n_estimators=90,min_samples_leaf=2,random_state=seed,n_jobs=1))]),
      'relation_signed_extratrees':Pipeline([('relations',RelationGrammar('signed')),('fit',ExtraTreesClassifier(n_estimators=90,min_samples_leaf=2,random_state=seed,n_jobs=1))]),
      'relation_interaction_dt3':Pipeline([('relations',RelationGrammar('interactions')),('fit',DecisionTreeClassifier(max_depth=3,min_samples_leaf=3,random_state=seed))]),
      'relation_interaction_rbf':Pipeline([('relations',RelationGrammar('interactions')),('fit',SVC(kernel='rbf',C=2.0,gamma='scale'))]),
      'relation_signed_rbf':Pipeline([('relations',RelationGrammar('signed')),('fit',SVC(kernel='rbf',C=2.0,gamma='scale'))]),
    }
    return classical,motif


def replay_frozen_queries(name,seed,mode='active'):
    """Exact FIELD003 query policy replay, STOP before its heldout scoring.

    Original query trace SHA is independently pinned by FIELD-003's artifact.
    """
    o=previous.Owner(name,seed)
    pub=o.public_pool();mu,std=previous.xscale(pub)
    chosen=[];receipts=[];grew=False
    stump=composition=None;features=()
    for t in range(previous.BUDGETS[name]):
        if mode=='random':
            available=[i for i in pub if i not in chosen]
            choice=min(available,key=lambda i:previous.sha(['passive',name,seed,i]))
        else:
            choice=previous.next_request(pub,chosen,stump,composition,features,mu,std)
        r=o.query(choice)
        if not o.verify(r):raise ValueError('invalid historical receipt')
        chosen.append(choice);receipts.append(r)
        stump,composition,features,_=previous._fit_from_receipts(receipts,pub,mu,std,grew)
        if not grew and len(receipts)>=18:
            yy=[int(r['observed_class']==2) for r in receipts]
            X=[previous.normalize(pub[r['row_id']],mu,std) for r in receipts]
            bad=sum(previous.classify(stump,x)!=v for x,v in zip(X,yy))
            if bad>=3 and len(set(yy))==2:
                grew=True
                stump,composition,features,_=previous._fit_from_receipts(receipts,pub,mu,std,grew)
    if o.query_count!=previous.BUDGETS[name]:raise AssertionError('wrong budget')
    return o,pub,mu,std,receipts


def choose_by_cv(models,X,y,seed):
    """Classical CV selection on acquired-label training only, identical folds.
    Ties prefer simpler dictionaries' insertion order. No tuning/test labels.
    """
    labels=Counter(map(int,y))
    folds=min(4,min(labels.values()))
    if folds<2:raise ValueError('insufficient class diversity')
    cv=StratifiedKFold(n_splits=folds,shuffle=True,random_state=seed)
    scores={}
    for key,model in models.items():
        fold_scores=cross_val_score(model,X,y,cv=cv,scoring='balanced_accuracy',n_jobs=1)
        scores[key]=round(float(np.mean(fold_scores)),6)
    winner=max(models,key=lambda name:(scores[name],-list(models).index(name)))
    return winner,scores


def classify_score(model,X,y):
    pred=model.predict(X)
    truth=np.asarray(y)
    return {'correct':int((pred==truth).sum()),'total':len(truth),
            'accuracy':round(float(np.mean(pred==truth)),6),
            'positive_correct':int(((pred==1)&(truth==1)).sum()),
            'positive_total':int((truth==1).sum()),
            'negative_correct':int(((pred==0)&(truth==0)).sum()),
            'negative_total':int((truth==0).sum())}


def features_for(ids,o,mu,std):
    return np.asarray([previous.normalize(o.rows[i][0],mu,std) for i in ids],dtype=float)

def labels_for(ids,o):
    return np.asarray([int(o.rows[i][1]==2) for i in ids],dtype=int)


def run(name,seed,mode='active'):
    owner,pub,mu,std,receipts=replay_frozen_queries(name,seed,mode)
    selected=[r['row_id'] for r in receipts]
    X=features_for(selected,owner,mu,std)
    y=np.array([int(r['observed_class']==2) for r in receipts],dtype=int)
    classical,relation=candidates(seed)
    picked_raw,raw_cv=choose_by_cv(classical,X,y,seed)
    picked_relation,relation_cv=choose_by_cv(relation,X,y,seed)
    # Same train budget; raw portfolio and relation portfolio get same CV folds.
    raw=classical[picked_raw].fit(X,y)
    evolved=relation[picked_relation].fit(X,y)
    matched_raw_ablation=clone(evolved.named_steps['fit']).fit(X,y)
    cart=previous.fit_tree([tuple(x) for x in X],list(map(int,y)),max_depth=3)
    # freeze all chosen methods and source evidence BEFORE holdout scoring
    frozen={'schema':SCHEMA,'dataset':name,'seed':seed,'mode':mode,
            'source_sha256':owner.revision,'trained_row_ids':selected,
            'receipt_sha256':[r['content_sha256'] for r in receipts],
            'preexisting_label_budget':len(receipts),
            'cv_scoring':'4fold_stratified_balanced_accuracy_train_only',
            'selected_raw':picked_raw,'selected_relational':picked_relation,
            'cohort':'preexisting_exploratory' if seed in DEV_SEEDS else 'new_seed_frozen_audit',
            'raw_cv':raw_cv,'relational_cv':relation_cv,
            'relation_axes':list(evolved.named_steps['relations'].indices_),
            'relation_kind':evolved.named_steps['relations'].kind,
            'no_tune_or_test_labels_used_in_model_selection':True}
    frozen['sha256']=digest(frozen)
    # Not used for fitting, CV selection or model selection: final report only.
    scores={}
    for part in ('tune','test'):
        ids=getattr(owner,part)
        xx=features_for(ids,owner,mu,std);yy=labels_for(ids,owner)
        cartpred=np.asarray([previous.classify(cart,tuple(v)) for v in xx])
        scores[part]={
         'original_cart_depth3':{'correct':int((cartpred==yy).sum()),'total':len(yy),'accuracy':round(float(np.mean(cartpred==yy)),6)},
         'matched_raw_classical_cv':classify_score(raw,xx,yy),
         'composed_relation_cv':classify_score(evolved,xx,yy),
         'selected_estimator_raw_ablation':classify_score(matched_raw_ablation,xx,yy),
        }
    assert set(selected).isdisjoint(set(owner.test+owner.tune))
    return {'frozen':frozen,'scores':scores,'label_queries':owner.query_count}


def experiment(isolate=True):
    results=[]
    for name in DATASETS:
        for seed in SEEDS:
            for mode in MODES:
                if isolate:
                    p=subprocess.run([sys.executable,str(Path(__file__).resolve()),'--case',name,str(seed),mode],
                       capture_output=True,text=True,check=True,timeout=50)
                    results.append(json.loads(p.stdout))
                else:
                    results.append(run(name,seed,mode))
    summary={}
    for cohort,seeds in [('exploratory',DEV_SEEDS),('audit_frozen',AUDIT_SEEDS),('all',SEEDS)]:
        summary[cohort]={}
        for name in DATASETS:
            summary[cohort][name]={}
            for mode in MODES:
                rr=[r for r in results if r['frozen']['dataset']==name and r['frozen']['mode']==mode and r['frozen']['seed'] in seeds]
                scores={}
                for algo in ('original_cart_depth3','matched_raw_classical_cv','composed_relation_cv','selected_estimator_raw_ablation'):
                    scores[algo]={'correct':sum(x['scores']['test'][algo]['correct'] for x in rr),
                             'total':sum(x['scores']['test'][algo]['total'] for x in rr)}
                summary[cohort][name][mode]={'scores':scores,
                   'relational_selected':[x['frozen']['selected_relational'] for x in rr],
                   'raw_selected':[x['frozen']['selected_raw'] for x in rr]}
    return {'schema':SCHEMA,'research_status':'EXPLORATORY_HOLD_UNMERGED',
            'source_data':'original FIELD003 independently published iris/wine snapshots',
            'label_budget':previous.BUDGETS,'dev_seeds':DEV_SEEDS,'audit_seeds':AUDIT_SEEDS,'modes':MODES,
            'summary':summary,'cases':results,
            'limitations':['public, historically familiar benchmarks; not preregistered or blind',
                'each split overlaps others; do not infer significance from aggregated row counts',
                'all feature synthesis and candidate models are ordinary classical algorithms',
                'relationship features selected within each CV training fold',
                'labels limited to FIELD003 original acquisition budget',
                'CV selects within families; family comparison on heldout is post-hoc descriptive, not model selection',
                'seed 83 was inspected in development and is not part of the audit cohort',
                'CSV and source checksums verify bytes, not independent primary source authentication',
                'no real-world intervention and no new scientific causal findings']}

def compact_report(full):
    """Reproducible, source/choice-pinned case ledger; full evidence in CI artifact."""
    return {k:v for k,v in full.items() if k!='cases'} | {
      'cases':[{'frozen_sha256':r['frozen']['sha256'],
                'dataset':r['frozen']['dataset'],'seed':r['frozen']['seed'],
                'cohort':r['frozen']['cohort'],'mode':r['frozen']['mode'],
                'source_sha256':r['frozen']['source_sha256'],
                'training_id_sequence_sha256':digest(r['frozen']['trained_row_ids']),
                'source_receipts_sha256':digest(r['frozen']['receipt_sha256']),
                'label_queries':r['label_queries'],
                'cv_summaries':{'raw':r['frozen']['raw_cv'], 'relation':r['frozen']['relational_cv']},
                'selected_raw':r['frozen']['selected_raw'],
                'selected_relation':r['frozen']['selected_relational'],
                'selected_relation_axes':r['frozen']['relation_axes'],
                'tune_scores':r['scores']['tune'],'test_scores':r['scores']['test']}
               for r in full['cases']]}

if __name__=='__main__':
    if len(sys.argv)==5 and sys.argv[1]=='--case':
        print(json.dumps(run(sys.argv[2],int(sys.argv[3]),sys.argv[4]),sort_keys=True))
    else:
        print(json.dumps(compact_report(experiment()),sort_keys=True,indent=2))
