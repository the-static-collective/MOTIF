"""Two honest feedback-driven measurement revisions; synthetic duplicate records."""
from __future__ import annotations

from importlib.util import spec_from_file_location, module_from_spec
from functools import lru_cache
from pathlib import Path
import json
import random
from redesign import RecordedCase, RecordedEvent, Revision, IdentifierAccess, RedesignLab
from instrument_lab import Capability, TraceCase, Event, instrument_from_data

SCOPE='synthetic:observer-a@cut-12:decoder-A'
WINDOWS=((0,4),(0,8),(4,8))
BUDGET=3.6


@lru_cache(maxsize=1)
def predecessor_instrument():
    """Use the actual GEOM-012 synthesizer, not a manually supplied XOR program."""
    path=Path(__file__).resolve().parent.parent/'geometry-012'/'demo.py'
    spec=spec_from_file_location('geom012_reference_demo',path)
    upstream=module_from_spec(spec)
    spec.loader.exec_module(upstream)
    lab=upstream.scenario()
    proposal=lab.propose(work_budget=1000)
    assert proposal['status']=='PENCIL_INSTRUMENT_PROPOSED',proposal
    instrument=lab.validate_proposal(proposal)
    assert instrument.operator=='XOR'
    assert {(a.channel,a.start,a.end,a.transform) for a in instrument.atoms}=={
        ('a',0,8,'ODD'),('b',0,8,'ODD')}
    return instrument


def capabilities():
    return [Capability('a',1.,True,True,SCOPE),
            Capability('b',1.,True,True,SCOPE),
            Capability('noise',0.1,True,True,SCOPE),
            Capability('answer-leak',0.001,False,True,SCOPE),
            Capability('unavailable-leak',0.001,True,False,SCOPE)]


def examples(seed:int,n:int,prefix:str,*,duplicate_a,duplicate_b,
             missing_traces:int=0,missing_ids:int=0):
    """Ground-truth label is produced from synthetic unique *original* events.

    Echo records carry the same identity as their original and can reverse raw
    parity. A source declaring equal identifiers is not independent evidence
    that they actually refer to the same physical event.
    """
    rng=random.Random(seed)
    cases=[]
    for i in range(n):
        a=i%2;b=(i//2)%2
        truth=bool(a^b)
        records=[]
        for ch,parity,duplicator in (('a',a,duplicate_a),('b',b,duplicate_b)):
            raw=[]
            for j in range(parity+2*rng.randint(1,3)):
                raw.append(RecordedEvent(rng.randrange(8),ch,f'{prefix}:{i}:{ch}:{j}'))
            records.extend(raw)
            if duplicator(i):records.append(rng.choice(raw))
        for j in range(rng.randint(0,4)):
            records.append(RecordedEvent(rng.randrange(8),'noise',f'{prefix}:{i}:noise:{j}'))
        if truth:
            records.append(RecordedEvent(0,'answer-leak',f'{prefix}:{i}:answer-leak'))
            records.append(RecordedEvent(0,'unavailable-leak',f'{prefix}:{i}:unavailable-leak'))
        rng.shuffle(records)
        if i >= n-missing_traces:
            records=None
        elif i>=n-missing_traces-missing_ids:
            idx=next(k for k,r in enumerate(records) if r.channel=='a')
            r=records[idx]
            records[idx]=RecordedEvent(r.tick,r.channel,None)
        case=RecordedCase.make(f'{prefix}-{i}',('sprout','bud'),('sprout','branch'),
            {'appearance':'same-bud','season':'synthetic-spring'},truth,records,
            f'claimed:{prefix}:source-{i%7}',SCOPE)
        cases.append(case)
    return cases


def scenario():
    parent=predecessor_instrument()
    access=IdentifierAccess(SCOPE,True,True,0.25)
    initial=Revision(parent,(False,)*len(parent.atoms))
    early=examples(2026110601,64,'round1',duplicate_a=lambda i:i%2==0,
                   duplicate_b=lambda i:False)
    later=examples(2026110602,64,'round2',duplicate_a=lambda i:i%3==0,
                   duplicate_b=lambda i:i%2==1)
    first=RedesignLab(parent,capabilities(),WINDOWS,access,early,budget=BUDGET)
    second=RedesignLab(parent,capabilities(),WINDOWS,access,early+later,budget=BUDGET)
    return initial,first,second


def two_revisions():
    active,first,second=scenario()
    p1=first.propose(active,work_budget=1)
    if p1['status']=='CONTINUE_SEARCH':
        p1=first.propose(active,work_budget=10,cursor=p1['cursor'])
    assert p1['status']=='PENCIL_INSTRUMENT_REDESIGN_PROPOSED',p1
    improved=first.validate_proposal(active,p1)
    p2=second.propose(improved,work_budget=10)
    assert p2['status']=='PENCIL_INSTRUMENT_REDESIGN_PROPOSED',p2
    final=second.validate_proposal(improved,p2)
    return active,first,second,p1,improved,p2,final


def run():
    active,first,second,p1,improved,p2,final=two_revisions()
    return {'experiment':'GEOM-013 self-redesigning measurement instrument',
            'parent':'GEOM-012 exact synthesized instrument',
            'first_critic':first.critic(active),
            'first_revision':p1,
            'second_critic':second.critic(improved),
            'second_revision':p2,
            'final_critic':second.critic(final),
            'summary':{'parent':active.data(),'first':improved.data(),'second':final.data(),
                       'inserted_steps':[s for s in final.recipe() if s['step']=='DISTINCT_BY_DECLARED_EVENT_ID']},
            'limitations':'Classical finite insertion search, synthetic declared record IDs and labels; no physical sensing, source authentication or autonomous experimentation.',
            'state':'PENCIL','authority':'NONE'}


if __name__=='__main__':
    print(json.dumps(run(),indent=2,sort_keys=True))
