"""RING-012 post-freeze evaluation of ambiguity as a default data type.

No forced single interpretation. Each source case can legitimately have
zero, one or several author-admissible graphs. The benchmark scores whether
the returned *set of perspectives* covers EVERY admitted reading, how much
spurious interpretation volume it carries, whether unbound text was held,
and whether it spuriously narrows to a lone operative-root reading.

This is NOT a guarantee of coverage for real human language: source text,
multi-meaning ground truth and ontology were authored for the test.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import itertools
import json
from pathlib import Path

import lattice,calibration
import binder,benchmark,corpus,search

SCHEMA="motif.ring012.postfreeze-ambiguity-native-trial.v1"
METHODS=("open_perspective_lattice","single_derived_binder",
         "single_word_bayes","single_bigram_bayes",
         "uncalibrated_method_union","all_24_possible_graphs","always_hold")

class HOLD(ValueError):
    pass


def frozen_verified(policy):
    lattice.validate_policy(policy)
    if (policy.get("source_train_dev_only_used_for_calibration") is not True
            or policy.get("novel_world_module_imported_during_selection") is not False
            or policy.get("test_meanings_consulted_to_select_policy") is not False):
        raise HOLD("Novel language scores must not control the selected policy")
    # Recompute from original train/dev source, not from heldout world.
    original=calibration.calibrate()
    if original!=policy:
        raise HOLD("Rehashed frozen source-calibrated policy was forged")
    source_frozen=search.run()
    train,program=benchmark.verify_frozen(source_frozen)
    return lattice.Sources(train,program)


def methods(case,source,policy):
    text,event,carrier=case["text"],case["observed_event"],case["carrier"]
    meta=lattice.combine(text,event,carrier,source,policy)
    out={"open_perspective_lattice":meta}
    # No baseline may claim authority, even on apparent utterance directives.
    raw=meta["source_methods"]
    for method,name in (
        ("derived_binder","single_derived_binder"),
        ("word_bayes","single_word_bayes"),
        ("bigram_bayes","single_bigram_bayes"),
    ):
        candidate=raw.get(method,{}).get("semantic_roles")
        world=[] if candidate is None else [
            corpus.frame(*(candidate[r] for r in corpus.RELATIONS),
                         carrier,event)]
        out[name]={
            "supported_worlds":world,
            "other_unmodeled_readings_remain_possible":True,
            "status":"BASELINE_ONE_SOURCE_HYPOTHESIS" if world else "HOLD",
            "external_action_executed":False,"authority":"NONE",
        }
    collected=[]
    for name in ("single_derived_binder","single_word_bayes","single_bigram_bayes"):
        collected.extend(out[name]["supported_worlds"])
    union={lattice.digest(x):x for x in collected}
    out["uncalibrated_method_union"]={
        "supported_worlds":list(union.values()),
        "other_unmodeled_readings_remain_possible":True,
        "status":"UNWEIGHTED_SOURCE_METHOD_UNION",
        "external_action_executed":False,"authority":"NONE",
    }
    _,bound=lattice.novelty_fraction(
        text,event,set(source.lexicon))
    allworld=[
        corpus.frame(force,scope,polarity,carrier,event)
        for force,scope,polarity in itertools.product(
            *[corpus.VALUES[relation] for relation in corpus.RELATIONS])
    ] if bound else []
    out["all_24_possible_graphs"]={
        "supported_worlds":allworld,
        "other_unmodeled_readings_remain_possible":True,
        "status":"UNINFORMATIVE_BOUNDED_ONTOLOGY_CONTROL",
        "external_action_executed":False,"authority":"NONE",
    }
    out["always_hold"]={
        "supported_worlds":[],
        "other_unmodeled_readings_remain_possible":True,
        "status":"HOLD",
        "external_action_executed":False,"authority":"NONE",
    }
    return out


def grade(case,output):
    truth=set(lattice.digest(x) for x in case["admissible_graphs"])
    worlds=output.get("supported_worlds",[])
    observed=set(lattice.digest(x) for x in worlds)
    all_valid=truth.issubset(observed)
    wrong_root=False
    if len(worlds)==1:
        m=corpus.graph_map(worlds[0])
        wrong_root=(m[("EVENT","REQUESTED_BY_ROOT")] is True and
                    not any(corpus.graph_map(x)[
                        ("EVENT","REQUESTED_BY_ROOT")] is True
                            for x in case["admissible_graphs"]))
    return {
        "all_readings_retained":bool(all_valid),
        "missing_reading_count":len(truth-observed),
        "excess_reading_count":len(observed-truth),
        "candidate_graphs":len(worlds),
        "multiple_readings_preserved":len(worlds)>1,
        "unsupported_single_root_action":bool(wrong_root),
        "unbound_held":case["reading_count"]!=0 or len(worlds)==0,
    }


def test(policy):
    source=frozen_verified(policy)
    # Only after checking the source-derived policy do we import the
    # experimenter's authored multiple-ground-truth test language.
    import world
    trials=[]
    for family,seed in (
        ("KNOWN_SHAPES_NEW_SOURCE_EVENTS",2026111211),
        ("OPEN_READING_CRYPTOGRAMMAR",2026111212),
    ):
        public=world.generate(family,seed=seed,rounds=4)
        world.validate(public)
        outcomes={}
        for method in METHODS:
            outcomes[method]={
                "cases":0,"complete_author_reading_coverage":0,
                "missing_authored_readings":0,
                "excess_proposed_readings":0,
                "concrete_readings_total":0,
                "multi_world_outputs":0,
                "false_single_root_action":0,
                "correct_unbound_holds":0,
                "author_ambiguous_cases_with_at_least_two_candidates":0,
                "author_ambiguous_cases_total":0,
            }
        witnesses=[]
        for case in public["cases"]:
            tested=methods(case,source,policy)
            outcome={}
            for method,prediction in tested.items():
                assert prediction["other_unmodeled_readings_remain_possible"] is True
                assert prediction["authority"]=="NONE"
                assert prediction["external_action_executed"] is False
                measures=grade(case,prediction)
                totals=outcomes[method]
                totals["cases"]+=1
                totals["complete_author_reading_coverage"]+=int(
                    measures["all_readings_retained"])
                totals["missing_authored_readings"]+=measures["missing_reading_count"]
                totals["excess_proposed_readings"]+=measures["excess_reading_count"]
                totals["concrete_readings_total"]+=measures["candidate_graphs"]
                totals["multi_world_outputs"]+=int(measures["multiple_readings_preserved"])
                totals["false_single_root_action"]+=int(
                    measures["unsupported_single_root_action"])
                totals["correct_unbound_holds"]+=int(
                    case["reading_count"]==0 and measures["unbound_held"])
                totals["author_ambiguous_cases_total"]+=int(case["reading_count"]>1)
                totals["author_ambiguous_cases_with_at_least_two_candidates"]+=int(
                    case["reading_count"]>1 and measures["multiple_readings_preserved"])
                outcome[method]=measures
            lattice_output=tested["open_perspective_lattice"]
            witnesses.append({
                "source_sha256":sha256(case["text"].encode()).hexdigest(),
                "carrier":case["carrier"],
                "authored_reading_count":case["reading_count"],
                "authored_reading_hashes":[lattice.digest(x)
                    for x in case["admissible_graphs"]],
                "model_source_claims":lattice_output["source_methods"],
                "retained_source_disagreement":lattice_output["source_disagreements"],
                "source_conditional_invariants":lattice_output.get(
                    "conditional_invariants_within_modeled_worlds",{}),
                "optional_discriminator":lattice_output.get(
                    "optional_discriminator_question_kind"),
                "ambiguity_does_not_force_an_interruption":not lattice_output.get(
                    "auto_interrupt_user_for_ambiguity",False),
                "open_world_always":lattice_output[
                    "other_unmodeled_readings_remain_possible"],
                "author_meanings_do_not_authenticate_real_events":True,
                "predictions":outcome,
            })
        for name in METHODS:
            o=outcomes[name]
            o["average_concrete_graphs"]=round(
                o["concrete_readings_total"]/max(1,o["cases"]),4)
        trials.append({
            "family":family,
            "packet_sha256":public["receipt_sha256"],
            "cases":len(public["cases"]),
            "author_tag_distribution":{
                kind:sum(x["author_tag"]==kind for x in public["cases"])
                for kind in ("UNIQUE","AMBIGUOUS","UNBOUND")},
            "scores":outcomes,
            "case_witnesses":witnesses,
            "labels_read_only_after_policy_frozen":True,
            "source_ontology_predefined_by_author":True,
            "no_private_cryptic_manuscript_text_used":True,
        })
    totals={}
    for name in METHODS:
        keys=[k for k in trials[0]["scores"][name]
              if k!="average_concrete_graphs"]
        totals[name]={k:sum(x["scores"][name][k] for x in trials)
                      for k in keys}
        totals[name]["average_concrete_graphs"]=round(
            totals[name]["concrete_readings_total"]/
            totals[name]["cases"],4)
    result={
        "schema":SCHEMA,
        "status":"MULTI_READING_OPEN_WORLD_LATTICE_TESTED_POST_FREEZE",
        "source_policy_sha256":policy["receipt_sha256"],
        "training_method_lineage_sha256":policy["source_011_frozen_receipt_sha256"],
        "test_packets":trials,
        "combined":totals,
        "meaning_is_set_valued_and_not_forced_to_one":True,
        "all_interpretations_remain_open_world":True,
        "witnessed_source_methods_share_correlated_training":True,
        "authored_semantic_ambiguity_not_real_world_interpretation":True,
        "source_carrier_authenticity_not_claimed":True,
        "no_generated_language_hypothesis_can_authorize_an_action":True,
        "external_actions_executed":False,
        "new_executable_methods_installed":0,
        "authority":"NONE",
    }
    result["receipt_sha256"]=lattice.digest(result)
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--policy",required=True,type=Path)
    p.add_argument("--out",type=Path)
    args=p.parse_args()
    try:
        doc=test(json.loads(args.policy.read_text()))
        if args.out:
            args.out.parent.mkdir(parents=True,exist_ok=True)
            args.out.write_text(json.dumps(doc,sort_keys=True,indent=2)+"\n")
        print(json.dumps({
            "status":doc["status"],
            "case_count":sum(g["cases"] for g in doc["test_packets"]),
            "scores":doc["combined"],
            "receipt":doc["receipt_sha256"],
        },sort_keys=True))
    except (HOLD,lattice.HOLD,binder.HOLD,ValueError) as exc:
        print(json.dumps({"status":"HOLD","reason":str(exc)}))
        raise SystemExit(2)


if __name__=="__main__":
    main()
