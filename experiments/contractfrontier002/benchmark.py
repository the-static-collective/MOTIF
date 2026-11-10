"""Fixed classical baselines for conditional/topological contract inference.

All learning methods get the identical developer-authored feature grammar and
training pool. Random sampling is a meaningful comparison; a handwritten
common-neighbor/reachability formula is a stronger oracle bound, not claimed
as an invention. No test labels enter any learner.
"""
from __future__ import annotations
import json
from contractfrontier import (
    PROGRAMS, _graphs, discover, audit, coarse_counterexample, observed_outcome,
    features, count_triangles, alternate_triangles, connected, adjacent,
)


def benchmark() -> dict:
    training=_graphs('train',120)
    validation=_graphs('validation',60)
    test=_graphs('test',100)
    ood=_graphs('ood',100)
    active=discover(training,validation,budget=8,selection='active')
    random_trials=[discover(training,validation,budget=8,selection='random',seed=j)
                   for j in range(30)]
    tight=[discover(training,validation,budget=3,selection='random',seed=j)
           for j in range(30)]
    # Manual algorithms are fair strong controls, not learned outcomes.
    manual_correct=sum(observed_outcome(p)==(
        len(adjacent(p.graph,p.a)&adjacent(p.graph,p.b)),
        int(connected(p.graph,p.a,p.b))-1) for p in test+ood)
    return {
        'experiment':'CONTRACT-FRONTIER-002',
        'hypothesis_programs':len(PROGRAMS),
        'active_training_interventions':active.inspected,
        'active_identified_both':active.usable,
        'active_test':audit(active,test),'active_ood':audit(active,ood),
        'random_eight_probe_30_seeds':{
            'identified':sum(r.usable for r in random_trials),
            'of':len(random_trials),
            'mean_probes':sum(r.inspected for r in random_trials)/len(random_trials),
            'best_probes':min(r.inspected for r in random_trials),
            'worst_probes':max(r.inspected for r in random_trials)},
        'random_three_probe_30_seeds':{'identified':sum(r.usable for r in tight),
                                     'of':len(tight)},
        'strong_handwritten_graph_algorithm':{'correct':manual_correct,
                                             'of':len(test)+len(ood)},
        'constant_zero_baseline':{'correct':sum(observed_outcome(p)==(0,0)
                                                 for p in test+ood),
                                  'of':len(test)+len(ood)},
        'coarse_statistics_ablation':coarse_counterexample(),
        'claims':{'novel_graph_mathematics':False,'unrestricted_contract_discovery':False,
                  'actual_live_self_improvement':False,'new_independent_evidence':False},
    }

if __name__=='__main__':
    print(json.dumps(benchmark(),indent=2,sort_keys=True))
