"""Frozen baselines. Never use held-out outcomes to choose a feature program."""
from __future__ import annotations
from featurefrontier import (PROGRAMS, pool, discover, heldout, ablate, infer)
from contractfrontier import observed_outcome, features
from statistics import mean
import json

def strong_handwritten(probes):
    return sum((features(p)['common_neighbors'],features(p)['connected']-1)
               == observed_outcome(p) for p in probes)

def run():
    train,valid=pool('train'),pool('validation')
    test,ood=pool('test',100),pool('ood',100)
    model=discover(train,valid)
    random_short=[];random_long=[]
    for seed in range(20):
        random_short.append(discover(train,valid,budget=model.inspections,select='random',seed=seed).usable)
        random_long.append(discover(train,valid,budget=12,select='random',seed=seed).usable)
    no_join=ablate(train,valid,remove_join=True)
    no_closure=ablate(train,valid,remove_closure=True)
    return {'experiment':'FEATURE-FRONTIER-001',
            'declared_grammar_size':len(PROGRAMS),'active_probes':model.inspections,
            'active_laws':[model.triangle.text(),model.components.text()],
            'active_test':heldout(model,test),'active_ood':heldout(model,ood),
            'random_budget_matched_successes':sum(random_short),
            'random_12_probe_successes':sum(random_long),'random_seeds':20,
            'strong_handwritten_classical':{'correct':strong_handwritten(test+ood),'of':len(test)+len(ood)},
            'naive_constant_zero':{'correct':sum(observed_outcome(p)==(0,0) for p in test+ood),'of':len(test)+len(ood)},
            'no_multiatom_join_refit':no_join,
            'no_transitive_closure_refit':no_closure,
            'claim':'bounded relational DSL with generic closure, not arbitrary invented math or historical novelty'}

if __name__=='__main__':
    print(json.dumps(run(),indent=2,sort_keys=True))
