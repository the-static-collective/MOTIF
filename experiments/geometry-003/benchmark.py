"""Deterministic frozen synthetic triangle fixtures and matched classical controls."""
import json
from fractions import Fraction as F
from random import Random
from time import perf_counter
from pathlib import Path
from synthesis import point, oracles, learn, apply, certificates, evaluate


HERE = Path(__file__).parent


def examples(seed=127, count=48):
    rng=Random(seed)
    out=[]
    while len(out)<count:
        vals=[(rng.randrange(-15,16),rng.randrange(-15,16)) for _ in range(3)]
        if len(set(vals))!=3:
            continue
        a,b,c=[point(*xy) for xy in vals]
        if abs((b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x)) < 8:
            continue
        if (a,b,c) not in out:
            out.append((a,b,c))
    return out


def encode(p):
    return [str(p.x),str(p.y)]


def benchmark():
    cases=examples()
    train=cases[:8]
    test=cases[8:]
    t0=perf_counter(); learned=learn(train); synth_s=perf_counter()-t0
    assert learned['status']=='PROPOSE_ONLY',learned
    mistakes=0
    certificate_failures=0
    for abc in test:
        found=apply(learned,abc)
        teacher=oracles(abc)
        if found['status'] != 'PROPOSE_ONLY' or any(found['points'].get(k)!=v for k,v in teacher.items()):
            mistakes+=1
        if found['status']=='PROPOSE_ONLY' and not all(found['witnesses'].values()):
            certificate_failures+=1
    # Exact closed-form classical control uses the same triangles and correct
    # rational arithmetic. It is not a strawman: both methods should tie.
    baseline_errors=sum(not all(certificates(x,oracles(x)).values()) for x in test)
    no_perp=learn(train,allow_perpendicular=False)
    no_mid=learn(train,allow_midpoint=False)
    return {
        'experiment':'MOTIF-GEOM-003',
        'setting':'exact rational Euclidean triangles; deterministic synthetic development',
        'training_triangles':len(train),
        'heldout_synthetic_triangles':len(test),
        'enumerated_initial_programs':learned['candidate_programs'],
        'enumerated_secondary_compositions':learned['secondary_compositions'],
        'matching_programs_by_role':learned['matches'],
        'method_signatures':{k:p.signature() for k,p in learned['programs'].items()},
        'synthesis_seconds_local':round(synth_s,4),
        'learned_macro_heldout_errors':mistakes,
        'direct_classical_oracle_heldout_errors':baseline_errors,
        'exact_instance_invariant_failures':certificate_failures,
        'ablations':{
            'without_perpendicular':no_perp['status'],
            'without_midpoint':no_mid['status'],
        },
        'universal_formal_proof':False,
        'authority':'HOLD: mathematical synthetic construction; no external action'
    }


if __name__=='__main__':
    print(json.dumps(benchmark(),indent=2))
