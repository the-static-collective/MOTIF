"""Evaluate on data materialized ONLY after both development-stage selections.

Independent classical baseline computes unique-ID parity directly; its staged
selection does not invoke the GEOM-013 revision search or measure/score methods.
"""
from __future__ import annotations
from itertools import combinations
import json
from redesign import RecordedCase
from demo import examples, two_revisions


def independent_measure(case:RecordedCase, flags:tuple[bool,bool]):
    if case.records is None:return None
    bits=[]
    for ch,unique in zip(('a','b'),flags):
        selected=[e for e in case.records if e.channel==ch and 0<=e.tick<8]
        if unique:
            if any(e.event_id is None for e in selected):return None
            seen={}
            for e in selected:
                if e.event_id in seen and seen[e.event_id] != (e.channel,e.tick):return None
                seen[e.event_id]=(e.channel,e.tick)
            bits.append(len(seen)%2)
        else:
            bits.append(len(selected)%2)
    return bool(bits[0]^bits[1])


def independent_select(cases,active=(False,False)):
    # Exhaustive finite operator-subset search, independent from redesign.Lab.
    ranked=[]
    for flags in ((False,False),(True,False),(False,True),(True,True)):
        if any(a and not f for a,f in zip(active,flags)):continue
        if flags==active:continue
        correct=True
        for c in cases:
            v=independent_measure(c,flags)
            if v is None or v!=c.expected:
                correct=False;break
        if correct:ranked.append((sum(flags)-sum(active),flags))
    if not ranked:return None
    return min(ranked)[1]


def count_independent(cases,flags):
    correct=wrong=abstentions=0
    for c in cases:
        value=independent_measure(c,flags)
        if value is None:abstentions+=1
        elif value==c.expected:correct+=1
        else:wrong+=1
    return {'correct':correct,'wrong':wrong,'abstentions':abstentions,'total':len(cases)}


def run():
    baseline,first,second,p1,r1,p2,r2=two_revisions()
    classic1=independent_select(first.development)
    classic2=independent_select(second.development,classic1)
    assert classic1==r1.distinct and classic2==r2.distinct
    frozen=examples(2026110603,300,'heldout',duplicate_a=lambda i:i%3 in (0,1),
                    duplicate_b=lambda i:i%4 in (0,3),missing_traces=20,missing_ids=20)
    before=second.evaluation(baseline,frozen)
    after_first=second.evaluation(r1,frozen)
    after_second=second.heldout(r1,p2,frozen)['scores']
    classic=count_independent(frozen,classic2)
    assert (after_second['correct'],after_second['wrong'],after_second['abstentions'])==(
        classic['correct'],classic['wrong'],classic['abstentions'])
    return {'experiment':'GEOM-013 procedural redesign under synthetic duplicate-record shift',
            'development_first':len(first.development),
            'development_second_total':len(second.development),
            'heldout_cases':len(frozen), 'heldout_seed':2026110603,
            'parent':before,'after_first_revision':after_first,'after_second_revision':after_second,
            'matched_classical_learner':classic,
            'classical_selected_first':list(classic1),'classical_selected_final':list(classic2),
            'parallel_classical_match':(after_second['correct'],after_second['wrong'],after_second['abstentions'])==(
                 classic['correct'],classic['wrong'],classic['abstentions']),
            'interpretation':'Synthetic record IDs presumed valid. This is classical subset search with a heldout shift from clean source events to duplicated delivery records; matched classical baseline ties. No autonomous sensing or discovery of a new operator primitive.',
            'authority':'NONE','state':'PENCIL'}

if __name__=='__main__':
    print(json.dumps(run(),indent=2,sort_keys=True))
