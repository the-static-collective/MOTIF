"""Frozen synthetic raw-trace demo; no real instrumentation or outside reads."""
from __future__ import annotations
import json
import random
from instrument_lab import Capability, Event, InstrumentLab, TraceCase

SCOPE='synthetic:observer-a@cut-12:decoder-A'
WINDOWS=((0,4),(0,8),(4,8))
BUDGET=3.


def raw_events(a:int,b:int,rng:random.Random):
    """Only raw time-tagged events; no Boolean A/B sensor values are supplied."""
    items=[]
    for channel,parity in [('a',a),('b',b)]:
        count=parity+2*rng.randrange(3)
        items.extend(Event(rng.randrange(8),channel) for _ in range(count))
    items.extend(Event(rng.randrange(8),'noise') for _ in range(rng.randrange(6)))
    # A forbidden (and very cheap) perfect-answer channel is deliberately present.
    # Its content must never enter an instrument candidate.
    if a ^ b:items.append(Event(rng.randrange(8),'answer-leak'))
    if a ^ b:items.append(Event(rng.randrange(8),'unavailable-leak'))
    rng.shuffle(items)
    return items


def sample_cases(seed:int,roots:tuple[str,...],reps:int,*,prefix:str,missing:int=0):
    rng=random.Random(seed)
    out=[]
    for root in roots:
        for rep in range(reps):
            for a,b in ((0,0),(0,1),(1,0),(1,1)):
                identity=f'{prefix}-{root}-{rep}-{a}{b}'
                raw=raw_events(a,b,rng)
                out.append(TraceCase.make(identity,('sprout','bud'),('sprout','branch'),
                    {'appearance':'same-bud','season':'synthetic-spring'},bool(a^b),raw,
                    f'claimed:{prefix}:{root}',SCOPE))
    if missing:
        for i in range(len(out)-missing,len(out)):
            o=out[i]
            out[i]=TraceCase.make(o.identity,o.before,o.after,dict(o.visible),o.expected,
                                  None,o.source_root,o.scope)
    return out


def scenario():
    development=sample_cases(2026110601,('oak','birch','pine','cedar','ash','elm'),4,prefix='development')
    capabilities=[Capability('a',1.,True,True,SCOPE),
                  Capability('b',1.,True,True,SCOPE),
                  Capability('noise',0.25,True,True,SCOPE),
                  Capability('answer-leak',0.001,False,True,SCOPE),
                  Capability('unavailable-leak',0.001,True,False,SCOPE)]
    lab=InstrumentLab(development,capabilities,WINDOWS,scope=SCOPE,budget=BUDGET)
    return lab


def run():
    lab=scenario()
    diagnosis=lab.diagnose()
    first=lab.propose(work_budget=7)
    assert first['status']=='CONTINUE_SEARCH',first
    found=lab.propose(work_budget=1000,cursor=first['cursor'])
    assert found['status']=='PENCIL_INSTRUMENT_PROPOSED',found
    plan=lab.validate_proposal(found)
    assert plan.operator=='XOR' and len(plan.atoms)==2,plan
    assert {(x.channel,x.start,x.end,x.transform) for x in plan.atoms}=={
        ('a',0,8,'ODD'),('b',0,8,'ODD')},plan
    return {'experiment':'MOTIF GEOM-012 synthetic instrument synthesis',
            'development_cases':len(lab.development),'diagnosis':diagnosis,
            'first_search_slice':first,'invented_procedure':found,
            'independence':'declared roots are not authenticated',
            'observation':'replayed existing synthetic event traces; no live measurement or physical instrument',
            'status':'PENCIL_ONLY','authority':'NONE'}

if __name__=='__main__':
    print(json.dumps(run(),indent=2,sort_keys=True))
