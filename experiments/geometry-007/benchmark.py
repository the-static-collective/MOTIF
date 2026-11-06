"""Frozen seeded smoke regime and matched no-layout classical partition baseline.

This is a deliberately elementary synthetic control, not independent real-world
validation or proof that multi-view representation improves accuracy.
"""
import json
import random
from math import log2
from contextual import Context, ContextualAtlas, Lens, Question


def baseline(worlds, questions):
    # Independent direct categorical partition information gain / cost.
    ranking=[]
    for q in questions:
        if not q.permitted:
            continue
        bins={}
        for world in worlds:
            bins[world[q.variable]]=bins.get(world[q.variable],0)+1
        if len(bins)<2:
            continue
        total=len(worlds)
        gain=-sum((size/total)*log2(size/total) for size in bins.values())
        ranking.append((-round(gain/q.cost,9),q.cost,q.id))
    return sorted(ranking)[0][2] if ranking else None


def run():
    rng=random.Random(20261106)
    checks=100; mismatches=[]; blind=0; held=0
    for i in range(checks):
        model_count=rng.randrange(2,6)
        # One visible constant, two potentially informative hidden coordinates.
        worlds=[]
        for j in range(model_count):
            worlds.append({'appearance':'SAME','hidden_a':str(j%2),
                           'hidden_b':str((j//2)%2)})
        # Deduplicate identical complete worlds explicitly.
        worlds=list({tuple(sorted(x.items())): x for x in worlds}.values())
        questions=[Question('q_a','hidden_a',rng.choice([1.,2.]),True),
                   Question('q_b','hidden_b',rng.choice([1.,3.]),True),
                   Question('untrusted','hidden_a',0.01,False)]
        contexts=[Context('all','same-typed-cut',('appearance','hidden_a','hidden_b'),
                          tuple(worlds),'fixture:predeclared')]
        atlas=ContextualAtlas(contexts,[Lens('fixed_visible',('appearance',),'HEX'),
                                        Lens('all',('appearance','hidden_a','hidden_b'),'NONE')],questions)
        left=atlas.next_question(('fixed_visible',))
        right=baseline(worlds,questions)
        selected=left.get('best',{}).get('question')
        if right!=selected:mismatches.append(i)
        if atlas.inspect(('fixed_visible',))['representation_blind']:
            blind+=1
        if left['status']=='HOLD':held+=1
        # Geometry MUST NEVER change conclusions or suggestion.
        no_coords=atlas.inspect(('fixed_visible',),display=False)
        with_coords=atlas.inspect(('fixed_visible',),display=True)
        with_coords['coordinates']={}
        assert no_coords==with_coords
    return {'cases':checks,'disagreement_with_matched_classical_partition_baseline':len(mismatches),
            'mismatch_case_ids':mismatches,'cases_where_fixed_view_hid_model_distinctions':blind,
            'cases_with_no_permitted_discriminator':held,'seed':20261106,
            'evaluation':'synthetic developer controls, not frozen independent data',
            'authority':'NONE'}

if __name__=='__main__':print(json.dumps(run(),sort_keys=True,indent=2))
