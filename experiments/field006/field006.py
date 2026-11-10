"""FIELD-006 — The Counterexample Question / truth-maintenance frontier.

Finite, archived-data active-learning experiment. Model predictions are fallible,
conditional local claims, never causal laws or authentic real-world observations.
All sources are SHA-pinned original FIELD-003 Iris and Wine historical snapshots.
"""
from __future__ import annotations
import argparse
import json
import math
import sys
from collections import Counter
from pathlib import Path

import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier
from sklearn.tree import DecisionTreeClassifier

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'field005'))
import field005 as old
from field005 import f3, RelationGrammar
from lineage import Lineage, seal, check_receipt

SCHEMA='motif.field006.v1'
POLICIES=('counterexample_relational','counterexample_raw','raw_margin','raw_committee','relation_frontier','geometry')
SEEDS_DEV=(11,23)
SEEDS_AUDIT=(157,163,167)
DATASETS=('iris','wine')
CHECKPOINTS=(25,40)
BOOTSTRAP=12
REFIT_EVERY=3


def committee(policy, X, y, seed):
    """Six members for raw and relational arms; all members see same labels.
    Rankings depend only on their previously acquired labels and pool features.
    """
    raw=[
      ('rbf2',SVC(C=2.,kernel='rbf')),
      ('rbf05',SVC(C=.5,kernel='rbf')),
      ('forest',RandomForestClassifier(n_estimators=45,min_samples_leaf=2,random_state=seed,n_jobs=1)),
      ('extra',ExtraTreesClassifier(n_estimators=45,min_samples_leaf=2,random_state=seed,n_jobs=1)),
      ('linear',LogisticRegression(max_iter=1000)),
      ('tree',DecisionTreeClassifier(max_depth=3,min_samples_leaf=2,random_state=seed))]
    mixed=[raw[0],raw[2],
       ('signed_rbf',Pipeline([('rel',RelationGrammar('signed',6)),('fit',SVC(C=2.,kernel='rbf'))])),
       ('interaction_rbf',Pipeline([('rel',RelationGrammar('interactions',6)),('fit',SVC(C=2.,kernel='rbf'))])),
       ('signed_tree',Pipeline([('rel',RelationGrammar('signed',6)),('fit',DecisionTreeClassifier(max_depth=3,min_samples_leaf=2,random_state=seed))])),
       ('interaction_tree',Pipeline([('rel',RelationGrammar('interactions',6)),('fit',DecisionTreeClassifier(max_depth=3,min_samples_leaf=2,random_state=seed))]))]
    selected=mixed if policy=='counterexample_relational' else raw
    return {name:model.fit(X,y) for name,model in selected}


def choose_counterexample(available, selected, X, density, models, experience, policy):
    """A pre-query, entropy/minimum-opposition objective, no oracle outcomes.

    Model weights use only prospective, previously witnessed local prediction
    outcomes. Their feedback is adaptively sampled and is not a calibrated
    estimate of each model's true generalization accuracy.
    """
    Xnew=np.asarray([X[i] for i in available])
    votes={key:mod.predict(Xnew).astype(int) for key,mod in models.items()}
    weights={key:(2+experience[key][0])/(4+sum(experience[key])) for key in models}
    chosen=None;winner=None
    for j,rid in enumerate(available):
        wtrue=sum(weights[key] for key,v in votes.items() if v[j]==1)
        wfalse=sum(weights[key] for key,v in votes.items() if v[j]==0)
        minority=min(wtrue,wfalse)
        p=wtrue/(wtrue+wfalse)
        entropy=-sum(q*math.log2(q) for q in (p,1-p) if q>0)
        # Evidence aimed at refuting a high-support conflicting explanation.
        # Do NOT count agreement as independent verification of any mechanism.
        rel_conflict=int(policy=='counterexample_relational' and (
            any(votes[k][j] != votes['rbf2'][j] for k in votes if k in
                ('signed_rbf','interaction_rbf','signed_tree','interaction_tree'))))
        novelty=min(old.min_distance(rid,selected,X),100.)
        score=(rel_conflict,round(entropy,10),round(minority,10),
               density[rid],math.log1p(novelty),-rid)
        if winner is None or score>winner:
            chosen=rid;winner=score
    packet={'selection_score':[float(v) for v in winner],
            'model_weights':{k:round(float(v),6) for k,v in weights.items()},
            'votes':{k:int(v[available.index(chosen)]) for k,v in votes.items()},
            'version_space_members':list(models),
            'status':'PROPOSED_BEFORE_SOURCE_QUERY'}
    return chosen,packet


def run(name,seed,policy,budget=40):
    if name not in DATASETS or policy not in POLICIES or budget not in CHECKPOINTS:
        raise ValueError('unsupported test protocol')
    owner=f3.Owner(name,seed)
    pool=owner.public_pool()
    X,mu,std=old.standardize(pool)
    density=old.pool_neighbors(X)
    chosen=[];labels=[];receipts=[];events=[];snapshots=[]
    lineage=Lineage();previous_models=None;last_fit=-1
    experience={}
    local_refutations=0;counterexample_queries=0;valid_alternatives=0
    checkpoint_models={}
    for step in range(budget):
        if policy.startswith('counterexample_') and step>=BOOTSTRAP and len(set(labels))==2 and (
                previous_models is None or step-last_fit>=REFIT_EVERY):
            previous_models=committee(policy,np.asarray([X[i] for i in chosen]),np.asarray(labels),seed)
            last_fit=step
            for model_name in previous_models: experience.setdefault(model_name,[0,0])
        if policy.startswith('counterexample_') and previous_models is not None:
            available=sorted(set(X)-set(chosen))
            row,question=choose_counterexample(available,chosen,X,density,previous_models,experience,policy)
            if len(set(question['votes'].values()))>1:counterexample_queries+=1
        else:
            fitted=None
            if policy in ('raw_margin','raw_committee','relation_frontier') and step>=BOOTSTRAP and len(set(labels))==2:
                if previous_models is None or step-last_fit>=REFIT_EVERY:
                    previous_models=old.fit_acquisition_models(np.asarray([X[i] for i in chosen]),np.asarray(labels),policy,seed)
                    last_fit=step
                fitted=previous_models
            row=old.select_query(policy,chosen,X,seed,fitted,density)
            question={'votes':{},'status':'PROPOSED_BEFORE_SOURCE_QUERY'}
        # Frozen pre-answer hypotheses, never label-dependent selection.
        before={'query':step+1,'selected':row,'source_queries_before':owner.query_count,
                'prior_observation_ids_sha256':seal(chosen),'question':question,
                'source_revision':owner.revision,'kind':'PRE_OBSERVATION_HYPOTHESIS'}
        before['sha256']=seal(before)
        obs=owner.query(row)
        if not owner.verify(obs): raise AssertionError('invalid original source record')
        source_key=f'fact:{step+1}'
        lineage.observation(source_key,obs,owner)
        verified_label=int(obs['observed_class']==2)
        updates=[]
        if question['votes']:
            survived=[]
            for model_key,pred in question['votes'].items():
                claim_id=f'predict:{step+1}:{model_key}'
                # Preregister a local prediction on the previously supported facts.
                supporting=[f'fact:{i}' for i in range(1,step+1)]
                lineage.claim(claim_id,[supporting])
                matched=int(pred==verified_label)
                lineage.resolve(claim_id,'OBSERVED_MATCH' if matched else 'REFUTED_LOCAL_PREDICTION')
                experience[model_key][0 if matched else 1]+=1
                if matched: survived.append(claim_id)
                else:local_refutations+=1
                updates.append({'model':model_key,'predicted':pred,'actual':verified_label,
                                'status':lineage.nodes[claim_id]['verdict']})
            # At least one alternative correct prediction remains independent
            # of a refuted one. No global model is accepted/rejected on one row.
            if survived:
                lineage.claim(f'local-survivors:{step+1}',[[s] for s in survived],
                              claim_kind='ALTERNATIVE_LOCAL_JUSTIFICATION')
                if lineage.supported(f'local-survivors:{step+1}'):
                    valid_alternatives+=1
        chosen.append(row);labels.append(verified_label);receipts.append(obs)
        events.append({'before':before,'source_receipt_sha256':obs['content_sha256'],
                       'source_row_id':row,'truth_maintenance_updates':updates})
        if step+1 in CHECKPOINTS:
            training=np.asarray([X[i] for i in chosen])
            y=np.asarray(labels)
            # Same strong model portfolios as FIELD-005, no tune/test labels.
            rn,rc,raw=old.select_model(old.raw_estimators(seed),training,y,seed)
            mn,mc,rel=old.select_model(old.relational_estimators(seed),training,y,seed)
            snapshots.append({'queries':step+1,'raw_selected':rn,'rel_selected':mn,
                              'raw_cv':rc,'rel_cv':mc,
                              'ids_sha256':seal(chosen),
                              'receipts_sha256':seal([r['content_sha256'] for r in receipts])})
            checkpoint_models[step+1]=(raw,rel)
    assert owner.query_count==budget and len(set(chosen))==budget
    assert not set(chosen)&set(owner.tune+owner.test)
    # Ledger freeze occurs before reading any heldout/tune labels.
    evidence={'schema':SCHEMA,'dataset':name,'seed':seed,'policy':policy,'budget':budget,
              'source_rev':owner.revision,'labels_scope':'training_pool_only',
              'selected_row_ids':chosen,'evidence_sha256':[r['content_sha256'] for r in receipts],
              'events':events,'snapshots':snapshots,
              'local_prediction_refutations':local_refutations,
              'discriminating_queries':counterexample_queries,
              'surviving_local_alternatives':valid_alternatives,
              'lineage_sha256':lineage.receipt()['sha256'],
              'status':'RESEARCH_HOLD_SOURCE_RECORDS_NOT_NEW_PHYSICAL_FACTS'}
    evidence['sha256']=seal(evidence)
    def score(ids):
        z=np.asarray([f3.normalize(owner.rows[i][0],mu,std) for i in ids])
        y=np.asarray([int(owner.rows[i][1]==2) for i in ids])
        return {str(n):{'raw':old.predicted_score(mraw,z,y),
                         'relational':old.predicted_score(mrel,z,y)}
                for n,(mraw,mrel) in checkpoint_models.items()}
    return {'proof':evidence,'test':score(owner.test),'tune':score(owner.tune)}


def batch(datasets=DATASETS,seeds=SEEDS_AUDIT,policies=POLICIES,budget=40):
    rows=[]
    for d in datasets:
        for s in seeds:
            for p in policies:
                r=run(d,s,p,budget)
                rows.append({'dataset':d,'seed':s,'policy':p,'budget':budget,
                             'proof_sha256':r['proof']['sha256'],
                             'source_rev':r['proof']['source_rev'],
                             'query_ids_sha256':seal(r['proof']['selected_row_ids']),
                             'refutations':r['proof']['local_prediction_refutations'],
                             'discriminating_queries':r['proof']['discriminating_queries'],
                             'surviving_local_alternatives':r['proof']['surviving_local_alternatives'],
                             'test':r['test']})
    summary={}
    for d in datasets:
        summary[d]={}
        for p in policies:
            selected=[r for r in rows if r['dataset']==d and r['policy']==p]
            if not selected:continue
            summary[d][p]={str(n):{family:{'correct':sum(r['test'][str(n)][family]['correct'] for r in selected),
                                           'total':sum(r['test'][str(n)][family]['total'] for r in selected)}
                                      for family in ('raw','relational')}
                                for n in CHECKPOINTS if n<=budget}
    packet={'experiment':'FIELD-006','schema':SCHEMA,'datasets':list(datasets),
            'seeds':list(seeds),'policies':list(policies),'budget':budget,
            'results':rows,'summary':summary,'limitations':[
                'well-known archived datasets reused from prior experiments',
                'overlapping repeated splits are correlated',
                'predeclared no test-label tuning; not prospectively blinded',
                'proof checksum is not source identity authentication',
                'falsifying a local prediction is not refuting a universal relation',
                'classical and relational methods are author-programmed, not autonomous invention',
                'different committee members incur different actual compute cost']}
    packet['sha256']=seal(packet)
    return packet


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--dataset',choices=DATASETS)
    p.add_argument('--seed',type=int)
    p.add_argument('--policy',choices=POLICIES)
    p.add_argument('--budget',type=int,choices=CHECKPOINTS,default=40)
    p.add_argument('--audit',action='store_true')
    a=p.parse_args()
    if a.audit:result=batch(budget=a.budget)
    elif a.dataset and a.seed and a.policy:result=run(a.dataset,a.seed,a.policy,a.budget)
    else:p.error('provide --audit OR --dataset, --seed and --policy')
    print(json.dumps(result,sort_keys=True,indent=2))
