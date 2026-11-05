"""MOTIF-011 evaluator and audit.

Six distinct *procedurally related synthetic* world families × five seeds.
Each world has four strictly separate 16-snapshot partitions:
  train → candidate concepts
  validation → reject spurious concepts
  local_review → explicit prediction-only admission
  test → evaluator-only final score

The learner in skeptic.py never imports this oracle. Raw world state, hidden
mechanism, withheld labels and safety authority are NOT sent to cartridges.
This is not preregistered evidence of general physical causal discovery.
"""
from __future__ import annotations

from collections import Counter,defaultdict
from dataclasses import dataclass
from pathlib import Path
from statistics import mean
import json

from oracle import (FAMILIES, SEEDS, make_world, episodes,
                    safe_policy_fixture, CONTROL_PAIRS)
from skeptic import (Assessment, HOLD, assess, controls_present,
                    validated_result, LocalConceptBay,
                    candidate_cartridges, safe_experiment,
                    export_extension, decode_extension)

VERSION = "skeptical-scientist-v1"
SPLIT_COUNTS = {"train":16,"validation":16,"local_review":16,"test":16}


def forcing_baseline(training, testing, controls):
    """A deliberately naive all-world *forced* two-port baseline.

    It predicts by per-input majority (ties -> False) even when identical
    visible inputs had contradictory training outcomes. It never abstains.
    This is NOT a strong noise-aware Bayesian or probabilistic comparator.
    """
    grouped = defaultdict(list)
    for row in training:
        grouped[controls_present(row,controls)].append(validated_result(row))
    lookup = {key:sum(vals)>len(vals)/2 for key, vals in grouped.items()}
    if len(lookup)!=4:
        raise ValueError("Forcing baseline lacks all input settings")
    observed = [validated_result(x) for x in testing]
    guesses = [lookup[controls_present(x,controls)] for x in testing]
    return {"coverage":1.0,
            "accuracy":round(sum(a==b for a,b in zip(observed,guesses))/
                             len(observed),4),
            "wrong":sum(a!=b for a,b in zip(observed,guesses)),
            "never_abstains":True}


def evaluate(family: str, seed: int) -> dict:
    spec = make_world(family,seed)
    train, validation, local, test = (
        episodes(spec,part) for part in SPLIT_COUNTS)
    assessment = assess(train, validation, spec.controls)
    raw_world_test = tuple(x.before for x in test)
    bay=LocalConceptBay()
    admitted = False
    held_before_review = None
    receipt = None
    extension_packet_roundtrip = None

    if assessment.status == "PROPOSE_EXTENSION":
        raw = export_extension(assessment.extension)
        extension_packet_roundtrip = (
            decode_extension(raw)==assessment.extension)
        ticket=bay.offer_packet(raw)
        held_before_review=ticket not in bay.admitted
        local_receipt=bay.review(ticket,"ADMIT_PREDICT_ONLY",
                                  "LOCAL_SYNTHETIC_REVIEWER", local,
                                  spec.controls)
        admitted = ticket in bay.admitted
        receipt = {
            "id": ticket,
            "local_decision": local_receipt.decision,
            "local_training_examples":len(local),
            "portable_router_roundtrip":extension_packet_roundtrip,
            "source_tree_ids":[assessment.extension.when_absent.id,
                               assessment.extension.when_present.id],
            "third_relation_predicate":assessment.extension.relation,
            "third_role":assessment.extension.role_index,
        }
        predictions=[bay.predict(ticket,x,spec.controls) for x in test]
    elif assessment.status=="TWO_PORT_CONSISTENT":
        predictions=[assessment.predict_two_port(x,spec.controls) for x in test]
    else:
        predictions=[None for _ in test]
    observed=[validated_result(x) for x in test]
    included=sum(x is not None for x in predictions)
    wrong=sum(p is not None and p!=true
              for p,true in zip(predictions,observed))
    status=assessment.status
    return {
        "family":family,"seed":seed,
        "train":len(train),"validation":len(validation),
        "local_review":len(local),"heldout_test":len(test),
        "status":status,"contradictory_control_settings":len(assessment.contradictions),
        "scars":[{"controls":list(x.controls),
                  "observed_outcomes":list(x.observed_outcomes),
                  "synthetic_provenance":x.provenance}
                 for x in assessment.contradictions],
        "new_concept_candidates":assessment.extension_candidates,
        "proposed_extension":assessment.extension.metadata()
                              if assessment.extension else None,
        "held_before_local_review":held_before_review,
        "explicit_local_admission":admitted,
        "extension_receipt":receipt,
        "heldout_coverage":round(included/len(test),4),
        "heldout_wrong_when_covered":wrong,
        "heldout_correct_when_covered":included-wrong,
        "heldout_accuracy_when_covered":
            round((included-wrong)/included,4) if included else None,
        "naive_forced_baseline":forcing_baseline(train,test,spec.controls),
        "heldout_original_graphs_unchanged":tuple(x.before for x in test)==raw_world_test,
        "real_world_authority":False,
    }


def safety_audit():
    """Under an explicit fictional policy, high-information unsafe actions HOLD."""
    spec=make_world("restricted_clean",SEEDS[0])
    train=episodes(spec,"train")
    # Only A=B natural examples: same input ambiguity as MOTIF-010.
    inputs=(next(x for x in train if controls_present(x,spec.controls)==pair)
            for pair in ((False,False),(True,True)))
    hypotheses=candidate_cartridges(tuple(inputs),spec.controls)
    if len(hypotheses)!=4:
        raise ValueError("Expected four competing synthetic trees")
    policy=safe_policy_fixture(spec)
    unsafe=safe_experiment(hypotheses,
                           allowed=policy["allowed"],
                           costs=policy["costs"],
                           remaining_budget=policy["budget"])
    no_funds=safe_experiment(hypotheses,
                           allowed=CONTROL_PAIRS,
                           costs={pair:5 for pair in CONTROL_PAIRS},
                           remaining_budget=2)
    permitted=safe_experiment(hypotheses,
                           allowed=CONTROL_PAIRS,
                           costs={pair:(1 if pair==(False,True) else 2)
                                  for pair in CONTROL_PAIRS},
                           remaining_budget=2)
    return {
        "competing_hypotheses":len(hypotheses),
        "unsafe_informative_setting":"HOLD" if unsafe.settings is None else "ERROR",
        "forbidden_information_gain_does_not_override_policy":unsafe.status,
        "insufficient_budget":"HOLD" if no_funds.settings is None else "ERROR",
        "insufficient_budget_status":no_funds.status,
        "admissible_proposal_status":permitted.status,
        "admissible_proposal":list(permitted.settings) if permitted.settings else None,
        "admissible_proposal_cost":permitted.cost,
        "real_action_dispatched":False,
        "simulator_changes_performed":0,
    }


def summary(rows):
    names=FAMILIES
    classified=Counter(x["status"] for x in rows)
    count=len(rows)
    covered=sum(x["heldout_test"]*x["heldout_coverage"] for x in rows)
    total=sum(x["heldout_test"] for x in rows)
    wrong=sum(x["heldout_wrong_when_covered"] for x in rows)
    forced_wrong=sum(x["naive_forced_baseline"]["wrong"] for x in rows)
    family={}
    for name in names:
        values=[x for x in rows if x["family"]==name]
        family[name]={
            "worlds":len(values),
            "statuses":dict(sorted(Counter(x["status"] for x in values).items())),
            "mean_coverage":round(mean(x["heldout_coverage"] for x in values),4),
            "wrong_when_covered":sum(x["heldout_wrong_when_covered"] for x in values),
            "forced_baseline_accuracy":round(mean(
                x["naive_forced_baseline"]["accuracy"] for x in values),4),
        }
    return {
        "version":VERSION,
        "scope":"SYNTHETIC_GRAPH_EVIDENCE_ONLY",
        "worlds":count,
        "families":list(names),
        "seeds":list(SEEDS),
        "train_each":16,"validation_each":16,
        "local_review_each":16,"heldout_test_each":16,
        "total_heldout_predictions_possible":total,
        "source_train_val_test_separated":True,
        "candidate_grammar_complete":False,
        "unobserved_cause_can_be_identified":False,
        "provisional_new_concept_requires_explicit_local_review":True,
        "status_counts":dict(sorted(classified.items())),
        "skeptic_heldout_coverage":round(covered/total,4),
        "skeptic_wrong_where_covered":wrong,
        "forced_baseline_heldout_coverage":1.0,
        "forced_baseline_wrong_total":forced_wrong,
        "forced_baseline_accuracy":round(1-forced_wrong/total,4),
        "per_family":family,
        "real_world_actions":0,
    }


def benchmark():
    rows=[evaluate(fam,seed) for fam in FAMILIES for seed in SEEDS]
    return {
        "experiment":"MOTIF-011",
        "summary":summary(rows),
        "safety_audit":safety_audit(),
        "worlds":rows,
    }


def demo():
    out=[]
    for fam in ("clean_two","visible_third","hidden_third",
                "noisy_flip","ambiguous_proxy","restricted_clean"):
        row=evaluate(fam,SEEDS[0])
        out.append({
            "family":fam,"status":row["status"],
            "contradiction_count":row["contradictory_control_settings"],
            "concept_candidate_count":row["new_concept_candidates"],
            "coverage":row["heldout_coverage"],
            "wrong":row["heldout_wrong_when_covered"],
            "source_only_concept":row["proposed_extension"],
            "local_admission":row["explicit_local_admission"],
            "naive_forced_baseline_accuracy":row["naive_forced_baseline"]["accuracy"]
        })
    return {
        "experiment":"MOTIF-011","label":"SKEPTICAL_SCIENTIST_LAB",
        "cases":out,
        "unsafe_interventions":safety_audit(),
        "safety_boundary":"PROPOSE_ONLY; NO_REAL_ACTUATOR",
    }


if __name__=="__main__":
    print(json.dumps(benchmark(),sort_keys=True,indent=2))
