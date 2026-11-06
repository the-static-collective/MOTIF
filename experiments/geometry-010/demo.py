"""GEOM-010: two criticism/revision rounds, then a sealed heldout inspection."""
from __future__ import annotations
import json
import random

from reason_lab import (SituatedCase, ConditionalRule, critic, score, invent_guard,
                        guarded_from_data, stage, explore, archive_pencil)
from living_graph import LivingGraph, RewriteGrammar, RewriteRule
from grammar_invention import Example, propose_revision, rule_from_proposal

SCOPE='synthetic:observer-alpha:t1:decoder-v1'


def initial_grammar():
    parent=RewriteGrammar(SCOPE,(
        RewriteRule('sprout',('seed',),('bud',)),
        RewriteRule('recede',('bud',),('seed',))))
    train=[Example(f'init-{n}',(n,'bud'),(n,'branch'),True,f'claimed:initial:{n}')
           for n in ('oak','pine','birch')]
    audit=[Example('audit-pos',('larch','bud'),('larch','branch'),True,'claimed:audit'),
           Example('audit-neg',('larch','bud'),('larch','leaf'),False,'claimed:audit')]
    proposed=propose_revision(parent,train,audit,candidate_budget=1000)
    assert proposed['status']=='PENCIL_GRAMMAR_REVISION_PROPOSED',proposed
    return parent,rule_from_proposal(proposed['rule']),proposed


def make_case(identity, seasonal, moisture, nutrient, expected, *, with_nutrient=True, after='branch', prefix='development'):
    facts={'season':seasonal,'moisture':moisture}
    if with_nutrient:
        facts['nutrient']=nutrient
    return SituatedCase.make(identity, [identity,'bud'],[identity,after],expected,
                             facts,f'claimed:{prefix}:{identity}',SCOPE)


def development_rounds():
    early=[]
    for i in range(14):
        early.append(make_case('early-good-'+str(i),'warm','wet','good',True))
        early.append(make_case('early-cold-'+str(i),'cold','wet','good',False))
        early.append(make_case('early-dry-'+str(i),'warm','dry','good',False))
    for i in range(4):
        early.append(make_case('early-leaf-'+str(i),'warm','wet','good',False,after='leaf'))
    later=[]
    for i in range(14):
        later.append(make_case('later-good-'+str(i),'warm','wet','good',True))
        later.append(make_case('later-poor-'+str(i),'warm','wet','poor',False))
    return early, later


def heldout(seed=20261106):
    """Generated only after the rule search; not supplied to any Inventor call."""
    rng=random.Random(seed)
    cases=[]
    kinds=[('warm','wet','good',True),('cold','wet','good',False),
           ('warm','dry','good',False),('warm','wet','poor',False)]
    for j,(season,moist,nutrient,expected) in enumerate(kinds):
        for i in range(60):
            label=f'frozen-{j}-{i}-{rng.getrandbits(56):014x}'
            cases.append(make_case(label,season,moist,nutrient,expected,prefix='heldout'))
    for i in range(20):
        label=f'unknown-{i}-{rng.getrandbits(56):014x}'
        cases.append(make_case(label,'warm','wet','missing',False,
                               with_nutrient=False,prefix='heldout-unknown'))
    return tuple(cases)


def run():
    parent,base,initial=initial_grammar()
    early,later=development_rounds()
    first=stage(parent,base,early,work_budget=1000)
    assert first['inventor']['status']=='PENCIL_GUARD_INVENTED',first
    first_rule=guarded_from_data(first['inventor']['rule'])
    all_development=early+later
    second=stage(parent,base,all_development,work_budget=1000,active=first_rule)
    assert second['inventor']['status']=='PENCIL_GUARD_INVENTED',second
    final_rule=guarded_from_data(second['inventor']['rule'])
    samples=heldout() # frozen; never supplied to invention or selection
    unguarded=ConditionalRule(base,(),SCOPE)
    scores={'unconditional':score(unguarded,samples),
            'round_one_guard':score(first_rule,samples),
            'round_two_guard':score(final_rule,samples),
            'always_false_baseline':{'correct':sum(not x.expected for x in samples),
                                     'total':len(samples)}}
    forking={}
    for kind,facts in [('permitted',{'season':'warm','moisture':'wet','nutrient':'good'}),
                       ('forbidden',{'season':'warm','moisture':'wet','nutrient':'poor'}),
                       ('unknown',{'season':'warm','moisture':'wet'})]:
        forking[kind]={
            'parent':explore(['oak','seed'],['oak','branch'],parent,None,facts,work_budget=20),
            'unconditional':explore(['oak','seed'],['oak','branch'],parent,unguarded,facts,work_budget=20),
            'revised':explore(['oak','seed'],['oak','branch'],parent,final_rule,facts,work_budget=20)}
    with LivingGraph(scope=SCOPE) as archive:
        receipt=archive_pencil(archive,parent,base,all_development,second['inventor'])
        counts=archive.counts()
        integrity=archive.verify()
    return {'experiment':'MOTIF GEOM-010: synthetic critic/inventor/explorer grammar revision',
            'scope':SCOPE,'initial_symbolic_rule':initial['rule'],
            'round_one':{'critic_false_positives':len(first['critic']['false_positives']),
                         'guard':first['inventor']['rule']['guard'],
                         'development':first['inventor']['development'],
                         'critic_after':first['critic_after']['status']},
            'round_two':{'critic_false_positives':len(second['critic']['false_positives']),
                         'guard':second['inventor']['rule']['guard'],
                         'development':second['inventor']['development'],
                         'critic_after':second['critic_after']['status']},
            'heldout_scores':scores,'heldout_seed':20261106,
            'counterfactual_graph_forks':forking,
            'archive':receipt,'archive_counts':counts,'integrity':integrity,
            'interpretation':'training/dev-driven classical conditional rule induction; no claims of unsupervised semantics',
            'authority':'NONE','instrument':'PENCIL'}

if __name__=='__main__':
    print(json.dumps(run(),sort_keys=True,indent=2))
