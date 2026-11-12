"""Post-hoc paired uncertainty audit of preregistered error-dividend outcomes.

This file was added AFTER the initial 160-seed trial. It must not silently
replace the preregistered primary scores. Seeded paired bootstrap evaluates
whether the small differences between policies are sampling noise.
"""
import json,random
from statistics import mean
from error_dividend import HELDOUT,episode,REGIMES

def paired_interval(a,b,iterations=2000):
    delta=[x-y for x,y in zip(a,b)]
    n=len(delta)
    rng=random.Random(20261112)
    draws=[]
    for _ in range(iterations):
        sample=[delta[rng.randrange(n)] for _ in range(n)]
        draws.append(mean(sample))
    draws.sort()
    return {"mean_delta":round(mean(delta),6),
            "lower_95_percentile":round(draws[int(.025*iterations)],6),
            "upper_95_percentile":round(draws[int(.975*iterations)-1],6),
            "straddles_zero":draws[int(.025*iterations)]<=0<=draws[int(.975*iterations)-1],
            "n_paired_seeds":n}

def summarize():
    rows=[]
    for regime in REGIMES:
        for budget in (1,2,3):
            runs={policy:[episode(seed,regime,policy,budget) for seed in HELDOUT]
                  for policy in ("challenge_favorite","classical_ig","uniform_random","no_probe")}
            for comparator in ("classical_ig","uniform_random","no_probe"):
                analysis=paired_interval(
                    [r["net_utility"] for r in runs["challenge_favorite"]],
                    [r["net_utility"] for r in runs[comparator]])
                rows.append({"regime":regime,"budget":budget,
                             "contrast":"challenge_favorite - "+comparator,**analysis})
    return {"kind":"EXPLORATORY_POSTHOC_BOOTSTRAP","not_preregistered":True,
            "bootstrap_iterations":2000,"analyses":rows}

if __name__=="__main__":
    print(json.dumps(summarize(),sort_keys=True,indent=2))
