"""Developer-authored synthetic heldout; independent classical truth table ties."""
from __future__ import annotations
import json
import random
from demo import SCOPE,scenario,raw_events
from instrument_lab import TraceCase, instrument_from_data


def heldout(seed=2026110612):
    rng=random.Random(seed)
    cases=[]
    for i in range(260):
        a,b=(i%4)//2,(i%4)%2
        raw=raw_events(a,b,rng) if i<240 else None
        cases.append(TraceCase.make(f'heldout-{i}',('sprout','bud'),('sprout','branch'),
                      {'appearance':'same-bud','season':'synthetic-spring'},bool(a^b),raw,
                      f'claimed:heldout:{i//4}',SCOPE))
    return cases


def classical_truth_table(train,test):
    """Independent direct event-counter/lookup baseline. Knows a,b and [0,8)."""
    def pair(c):
        if c.events is None:return None
        return (sum(e.channel=='a' and 0<=e.tick<8 for e in c.events)%2,
                sum(e.channel=='b' and 0<=e.tick<8 for e in c.events)%2)
    table={}
    for c in train:
        sig=pair(c)
        if sig in table and table[sig]!=c.expected:raise AssertionError('training table conflict')
        table[sig]=c.expected
    good=bad=unknown=0
    for c in test:
        sig=pair(c)
        if sig is None or sig not in table:unknown+=1
        elif table[sig]==c.expected:good+=1
        else:bad+=1
    return {'total':len(test),'correct':good,'wrong':bad,'abstentions':unknown}


def best_atomic(train,test):
    """Select strongest single derived measurement on development only."""
    options=[p for p in train._candidates() if len(p.atoms)==1]
    # Break train ties without ever examining heldout.
    best=max(options,key=lambda p:(train.score(p,train.development)['correct'],-p.cost(train.catalog)))
    return {'selected':best.data(),'scores':train.score(best,test)}


def run():
    lab=scenario()
    selected=lab.propose(work_budget=1000)
    assert selected['status']=='PENCIL_INSTRUMENT_PROPOSED'
    cases=heldout()
    measured=lab.evaluate_heldout(selected,cases)
    baseline=classical_truth_table(lab.development,cases)
    atomic=best_atomic(lab,cases)
    return {'experiment':'GEOM-012 raw-event program synthesis against classical baseline',
            'developer_authored_synthetic':True,'seed':2026110612,
            'development_cases':len(lab.development),'heldout_cases':len(cases),
            'proposed_instrument':selected['instrument'],
            'heldout':measured,'classical_direct_count_truth_table':baseline,
            'best_single_predicate':atomic,
            'visible_only_false_correct':sum(not c.expected for c in cases),
            'parity_with_classical':measured['scores']==baseline,
            'limits':'The generator uses a prescribed XOR-of-event-count-parity law. A conventional classical program search can tie. No real sensor was invented or accessed.',
            'state':'PENCIL','authority':'NONE'}

if __name__=='__main__':
    print(json.dumps(run(),indent=2,sort_keys=True))
