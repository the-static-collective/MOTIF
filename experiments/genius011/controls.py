"""GENIUS-011 explicitly POSTHOC observational confounding falsifier.

Added after the first synthetically frozen six-seed run was inspected.
This diagnostic is not a fresh preregistered/blind test and cannot be
quietly folded into the original confirmed result.
"""
from __future__ import annotations

import json
import random
from discovery import (Trial, THREADS, make_world, question_synthesis,
                       analyze, public_trials, fisher_two_sided)


def confounded_survey(seed: int, q) -> tuple[Trial, ...]:
    """Make X and outcome Y both depend on latent Z, with NO X -> Y effect."""
    rng=random.Random(seed*3119 + int(q.digest[:8],16))
    rows=[]
    for thread in THREADS:
        for i in range(160):
            z = rng.random() < 0.5
            x = z if rng.random() < .94 else not z
            y = z if rng.random() < .94 else not z
            uid=f"synthetic://observational/{seed}/{q.digest}/{thread}/{i}"
            share = i % 37 != 0
            rows.append(Trial(q.signature,thread,bool(x),bool(y),
                              uid,uid,share,
                              "NEVER_SHARE_PRIVATE_CONTROL_NOTE",
                              "OBSERVATIONAL_NOT_RANDOMIZED"))
    return tuple(rows)


def audit_survey(seed: int) -> dict:
    w=make_world(seed,"CONFOUNDED")
    queries=question_synthesis(w.strands)["candidates"]
    cases=[]
    for q in queries:
        data=public_trials(confounded_survey(seed,q))
        arms=[]
        for thread in THREADS:
            rows=[x for x in data if x.thread==thread]
            high=[x for x in rows if x.treated]
            low=[x for x in rows if not x.treated]
            gap=sum(x.success for x in high)/len(high) - (
                sum(x.success for x in low)/len(low))
            p=fisher_two_sided(sum(x.success for x in low),len(low),
                               sum(x.success for x in high),len(high))
            arms.append({"thread":thread,"observational_difference":round(gap,6),
                         "observational_p_value":format(p, ".6e"),
                         "not_a_causal_or_randomized_conclusion":True})
        forbidden=analyze(q,data,purported_randomization_attested=True)
        assert forbidden["status"]=="HOLD_OBSERVATIONAL_DATA_NOT_AN_INTERVENTION"
        cases.append({
            "generated_signature":q.signature,
            "survey_results":arms,
            "intervention_gate_status":forbidden["status"],
            "survey_private_notes_not_exported":True,
        })
    return {
        "status":"POSTHOC_OBSERVATIONAL_CONFOUNDING_NOT_INDEPENDENT_BLIND",
        "seed":seed,"generated_candidates":len(queries),
        "candidate_checks":cases,
        "underlying_true_intervention_effect":"NONE_IN_SYNTHETIC_WORLD",
        "no_external_action":True,
    }


if __name__=="__main__":
    print(json.dumps(audit_survey(11031),indent=2,sort_keys=True))
