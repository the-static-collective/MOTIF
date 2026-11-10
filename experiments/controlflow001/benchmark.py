"""Frozen finite-control-flow controls; train/test outcomes separated by API."""
from __future__ import annotations
import json
from controlflow import trials
from controlflow import discover, diagnose, audit, grammar, OLD_PROGRAMS


def benchmark() -> dict:
    train=trials('train',36)
    valid=trials('validation',24)
    model=discover(train,valid)
    test=audit(model,trials('test',24))
    ood=audit(model,trials('ood',20))
    no_growth=discover(train,valid,max_depth=2)
    no_distinct=discover(train,valid,allow_distinct=False)
    random_three=[discover(train,valid,budget=3,selection='random',seed=i) for i in range(12)]
    random_eight=[discover(train,valid,budget=8,selection='random',seed=i) for i in range(12)]
    return {'experiment':'CONTROL-FLOW-GROWTH-001',
            'scope':'finite human-authored recursive FOR syntax; synthetic graphs',
            'initial_operator_grammar':len(OLD_PROGRAMS),
            'initial_failure':diagnose(train)['status'],
            'candidate_recursive_programs':len(grammar(3)),
            'active_new_family_interventions':model.probes,
            'prior_failure_probes':diagnose(train)['inspected'],
            'learned_ast':model.program.signature(),
            'validation':'F_LOCAL_REPLAY' if model.usable else model.status,
            'hidden_test':test,'larger_ood':ood,
            'no_third_loop':no_growth.status,
            'without_distinctness':no_distinct.status,
            'random_three_probe_validated':{'of':12,'successes':sum(x.usable for x in random_three)},
            'random_eight_probe_validated':{'of':12,'successes':sum(x.usable for x in random_eight)},
            'strong_handwritten_dfs_ties_generated':test['strong_classical_correct']==test['cases']
                 and ood['strong_classical_correct']==ood['cases'],
            'general_python_invention':False,'external_actions':0}

if __name__=='__main__':
    print(json.dumps(benchmark(),indent=2,sort_keys=True))
