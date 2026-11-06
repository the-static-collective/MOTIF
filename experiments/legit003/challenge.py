"""LEGIT-003: independently frozen synthetic adversarial transfer set.

Source cases have an unseen simulated assignment of the latent target. The
countermodel compiler sees *only* aggregate proxy counts and permitted small
truth anchors, never the hidden latent values. These are authored synthetic
cases, NOT independently sourced empirical research.
"""
from __future__ import annotations

from hashlib import sha256
from itertools import product
from random import Random

from countermodel import SCHEMA

SEED = "LEGIT003-countermodels-2026-11-06-frozen-v1"
N_CASES = 128


def _seed(index):
    return int(sha256(f"{SEED}:{index}".encode()).hexdigest()[:16],16)


def challenge(index):
    if type(index) is not int or not 0<=index<N_CASES:
        raise ValueError("Invalid frozen case number")
    rng = Random(_seed(index))
    n_groups = rng.randint(1,4)
    observations = []
    anchors = []
    hidden = {}
    for g in range(n_groups):
        group = f"g{g}"
        pos, neg = rng.randint(0,4), rng.randint(0,4)
        if pos+neg==0:
            neg=1
        observations.append({"group":group,
                             "proxy_positive":pos,
                             "proxy_negative":neg,
                             "source_id":"SIMULATOR"})
        for proxy,n in (("positive",pos),("negative",neg)):
            true = rng.randint(0,n)
            hidden[(group,proxy)] = true
            if index % 3 == 0 or rng.random() < .6:
                known_true = rng.randint(0,true)
                known_false = rng.randint(0,n-true)
                anchors.append({"group":group,"proxy":proxy,
                                "known_latent_true":known_true,
                                "known_latent_false":known_false,
                                "origin":"SIMULATOR_TRUTH"})
    task = {"schema":SCHEMA,"id":f"Synthetic_{index:03d}",
            "scope":"SYNTHETIC_ONLY",
            "question":"Does the negative reading entail that this hidden quality is absent?",
            "latent_target":"HIDDEN_PROPERTY",
            "observed_proxy":"READING",
            "observations":observations,
            "anchors":anchors,
            "sources":[{"id":"SIMULATOR","url":"synthetic://sealed-challenge-v1",
                        "provenance":"SYNTHETIC_SIMULATOR"}]}
    return task, hidden


def brute_force_reference(task):
    """An independent tiny classical enumerator; no compiler imports.

    Enumerate EVERY possible binary target assignment within each stratum
    (max 4 persons/cell) and discard those contradicting certified synthetic
    label counts. Derive exact possible target-count extremes from enumeration.
    """
    anchor_map = {(a["group"],a["proxy"]):a for a in task["anchors"]}
    bounds = {}
    for row in task["observations"]:
        for proxy, n in (("positive",row["proxy_positive"]),
                         ("negative",row["proxy_negative"])):
            a = anchor_map.get((row["group"],proxy),{})
            true_required = a.get("known_latent_true",0)
            false_required = a.get("known_latent_false",0)
            assignments = [sum(bits) for bits in product((False,True),repeat=n)
                           if sum(bits)>=true_required and
                              n-sum(bits)>=false_required]
            if not assignments:
                raise ValueError("Inconsistent independent source constraints")
            bounds[(row["group"],proxy)] = (min(assignments),max(assignments))
    return bounds


def report():
    from countermodel import compile_countermodels
    from bridge import demonstrate
    breakdown = {"AMBIGUOUS":0,"ENTAILED_ABSENCE":0,
                 "FALSIFIED_ABSENCE":0,"NO_NEGATIVE_CASES":0}
    synthetics_checked = 0
    for i in range(N_CASES):
        task, truth = challenge(i)
        result = compile_countermodels(task)
        check = brute_force_reference(task)
        for cell in result["cells"]:
            key = cell["group"],cell["proxy"]
            exact = check[key]
            if (cell["min_target_true"],cell["max_target_true"])!=exact:
                raise AssertionError("Countermodel compiler disagrees with independent enumeration")
            if not exact[0]<=truth[key]<=exact[1]:
                raise AssertionError("True simulated target excluded from advertised interval")
        if result["negative_proxy_observed"]==0:
            label="NO_NEGATIVE_CASES"
        elif result["negative_proxy_latent_true_bounds"][1]==0:
            label="ENTAILED_ABSENCE"
        elif result["negative_proxy_latent_true_bounds"][0]>0:
            label="FALSIFIED_ABSENCE"
        else:
            label="AMBIGUOUS"
        breakdown[label]+=1
        synthetics_checked+=1

    original = demonstrate()
    receptor = original["compiler_receipt"]
    if (receptor["negative_proxy_latent_true_bounds"] != [0,250] or
            receptor["all_latent_true_bounds"] != [0,353] or
            receptor["total_observed"] != 353):
        raise AssertionError("Unexpected public-cohort completion: inspect source")
    return {"experiment":"MOTIF-LEGIT-003",
            "registered_synthetic_cases":N_CASES,
            "registered_seed":SEED,
            "synthetic_cases_checked_against_independent_brute_force":synthetics_checked,
            "synthetic_breakdown":breakdown,
            "strong_classical_control":"EXACT_TIE",
            "classical_superiority_claim":False,
            "external_unseen_real_world_generalization":False,
            "public_neuro_cohort_latent_bounds":receptor["all_latent_true_bounds"],
            "public_negative_proxy_latent_bounds":receptor["negative_proxy_latent_true_bounds"],
            "public_verdict":receptor["verdict"],
            "scope":"RESEARCH_HOLD",
            "real_world_authority":False}

if __name__=="__main__":
    import json
    print(json.dumps(report(),sort_keys=True,indent=2))
