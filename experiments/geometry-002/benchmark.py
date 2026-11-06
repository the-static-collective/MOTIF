"""Fixed development benchmark; reproducible, NOT an independent blind holdout."""
from __future__ import annotations
import json
import random
from math import hypot
from pathlib import Path
from discover import discover,point_set

FAMILIES=('triangular','square','oblique')
SEEDS=(770,771,772,773,774,775,776,777,778,779,780,781)
NEGATIVE_SEEDS=tuple(range(220,244))

def synthetic(family,seed,noise=0.015,outliers=2):
    rng=random.Random(seed)
    scale=1.0+(.1*(seed%4))
    world=point_set(family,scale,23+(seed%4)*11,(1.2,-.5))
    withheld={(0,0),(1,0),(-1,1)}
    actual=[v for k,v in world.items() if k not in withheld]
    rng.shuffle(actual)
    observed=[(x+rng.gauss(0,noise*scale),
               y+rng.gauss(0,noise*scale)) for x,y in actual]
    observed += [(rng.uniform(-3,4),rng.uniform(-4,3)) for _ in range(outliers)]
    return observed,[world[k] for k in withheld]


def negative(seed):
    rng=random.Random(seed)
    if seed%3==0:
        return [(rng.uniform(-3,3),rng.uniform(-3,3)) for _ in range(22)]
    if seed%3==1:
        return [(i*.35+rng.gauss(0,.025),
                 i*.8+rng.gauss(0,.025)) for i in range(22)]
    # Unrelated concentric ring, not a periodic 2D field.
    from math import pi,cos,sin
    return [(rng.uniform(1.6,2.0)*cos(2*pi*i/22),
             rng.uniform(1.6,2.0)*sin(2*pi*i/22)) for i in range(22)]


def measure_recovery(report, missing, scale):
    if report['status']!='PROPOSE_ONLY':
        return 0,0
    holes=report['holes']
    successes=sum(any(hypot(p['xy'][0]-x,p['xy'][1]-y)<.2*scale
                      for p in holes) for x,y in missing)
    false=sum(not any(hypot(p['xy'][0]-x,p['xy'][1]-y)<.2*scale
                      for x,y in missing) for p in holes)
    return successes,false


def run():
    results=[]
    for f in FAMILIES:
        for seed in SEEDS:
            obs,missing=synthetic(f,seed)
            proposal=discover(obs)
            ablated=discover(obs,refine=False)
            recovered,false=measure_recovery(proposal,missing,1+(.1*(seed%4)))
            results.append({
                'regime':f,'seed':seed,'status':proposal['status'],
                'family_correct':proposal.get('rule',{}).get('family')==f,
                'recovered_masked':recovered,'proposed_false_holes':false,
                'ablation_status':ablated['status'],
                'refined_coverage':proposal.get('coverage',0),
                'ablated_coverage':ablated.get('coverage',0),
                'refined_rmse':proposal.get('normalized_rmse'),
                'ablated_rmse':ablated.get('normalized_rmse'),
            })
    negatives=[]
    for seed in NEGATIVE_SEEDS:
        r=discover(negative(seed))
        negatives.append({'seed':seed,'case':('random','collinear','nonperiodic_ring')[seed%3],
                          'status':r['status']})
    models=[r for r in results if r['status']=='PROPOSE_ONLY']
    ablated=[r for r in results if r['ablation_status']=='PROPOSE_ONLY']
    summary={
        'design':'fixed development suite: 3 geometry families × 12 seeds; 24 nonlattice controls',
        'tested_worlds':len(results),
        'held_model_rejections':len(results)-len(models),
        'proposed_models':len(models),
        'family_correct':sum(r['family_correct'] for r in results),
        'masked_centers_total':3*len(results),
        'masked_centers_recovered':sum(r['recovered_masked'] for r in results),
        'extra_hole_proposals':sum(r['proposed_false_holes'] for r in results),
        'ablation_without_least_squares_proposals':len(ablated),
        'refined_mean_normalized_rmse':round(sum(r['refined_rmse'] for r in models)/max(1,len(models)),5),
        'ablation_mean_normalized_rmse':round(sum(r['ablated_rmse'] for r in ablated)/max(1,len(ablated)),5),
        'negative_controls':len(negatives),
        'negative_controls_held':sum(r['status']=='HOLD' for r in negatives),
        'negative_false_accepts':sum(r['status']!='HOLD' for r in negatives),
        'results':results,
        'negative_results':negatives,
        'interpretation':'finite classical robust fitting; this does not identify unknown physical laws or authenticate evidence',
    }
    return summary

if __name__=='__main__':
    result=run()
    Path(__file__).with_name('benchmark-results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('results','negative_results')},indent=2))
