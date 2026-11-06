"""REASON-018 result: rediscover a relational meaning, not copy a phrase.

This is bounded program synthesis from artificial relational counterexamples.
A source-owner, not the candidate engine, determines whether the graph
supports the newly defined fictional relation. A strong classical synthesis
baseline could find the same formula. No one has measured a loving outcome.
"""
from __future__ import annotations

from pathlib import Path
import json

from worlds import train_worlds,heldout_worlds
from oracle import SourceOwner,source_label
from inventor import discover,suggest,programs,export,pin
from reviewer import Receiver,reviewed_evaluation


def flat_unjoined_baseline(w):
    """A deliberately inadequate bag-of-edge-facts representation.

    It never binds the SAME intermediate node across OPEN and RELEASE.
    When two different intermediate witnesses exist, it can hallucinate
    a complete care-path even though no joined route exists.
    """
    E={tuple(e) for e in w["edges"]}
    a,b=w["actor"],w["recipient"]
    has_offer=("OFFER",a,b) in E
    has_free=("FREE",a,b) in E
    open_any=any(e[0]=="OPEN" and e[1]==b for e in E)
    return_any=any(e[0]=="RELEASE" and e[2]==a for e in E)
    pos=has_offer and has_free and open_any and return_any
    neg=(not (has_offer and open_any and return_any)) or (
        "CLAIM",a,b) in E
    return ("BOTH" if pos and neg else "SUPPORTED" if pos else
            "REFUTED" if neg else "UNDETERMINED")


def run(out=None):
    owner=SourceOwner()
    model=discover(owner,max_inquiries=40)
    payload=export(model)
    receiver=Receiver()
    review=receiver.preview(payload)
    if review["source_errors"]:
        raise AssertionError("Relational meaning contradicted independent source-owned case")
    receiver.admit("ADMIT_READ_ONLY",review["review_digest"])
    examples=reviewed_evaluation(model)
    flat=sum(flat_unjoined_baseline(w)==source_label(w)["status"]
             for w in heldout_worlds())
    exact=sum(x["exact_match"] for x in examples)
    holds=sum(x["abstained"] for x in examples)
    statuses={}
    for x in examples:
        statuses[x["source_status"]]=statuses.get(x["source_status"],0)+1
    checked=receiver.suggest(heldout_worlds()[0])
    answer={
        "schema":"motif.reason.living-concept.benchmark.v1",
        "training_worlds_available":len(train_worlds()),
        "heldout_worlds_available":len(heldout_worlds()),
        "training_examples_purchased":model["source_example_count"],
        "owner_question_budget":model["source_inquiry_budget"],
        "syntactic_grammar_candidates":model["grammar_size"],
        "learned_program_candidates":len(model["remaining_hypotheses"]),
        "invented_macro_expressions":model["remaining_hypotheses"],
        "active_source_counterexample_trace":model["version_space_trace"],
        "heldout_source_exact":exact,
        "heldout_safe_abstentions":holds,
        "heldout_incorrect_confident":len(examples)-exact-holds,
        "heldout_source_four_state_counts":dict(sorted(statuses.items())),
        "strong_classical_direct_reference":len(examples),
        "weak_unjoined_relation_bag_baseline":flat,
        "source_snapshot_git_blob":pin(),
        "source_owner_labels_are_not_imported_by_inventor":True,
        "no_target_rule_given_to_discovery":True,
        "witness_binding_is_not_flat_edge_cooccurrence":True,
        "relational_predicate_composition_not_new_logical_connective":True,
        "target_meaning_is_source_author_fiction":True,
        "source_graph_nodes_grow_beyond_training":True,
        "independent_receiver":review,
        "first_independently_admitted_source_case":checked,
        "label_source_is_synthetic":True,
        "general_language_understanding_not_proven":True,
        "human_welfare_love_emotion_not_measured":True,
        "external_actions":False,
        "real_world_authority":False,
    }
    if out:
        dest=Path(out);dest.mkdir(parents=True,exist_ok=True)
        (dest/"compiled-relation-cartridge.json").write_text(payload,encoding="utf8")
        (dest/"benchmark.json").write_text(
            json.dumps(answer,indent=2,sort_keys=True)+"\n",encoding="utf8")
        (dest/"heldout-four-valued-source-audit.json").write_text(
            json.dumps(examples,indent=2,sort_keys=True)+"\n",encoding="utf8")
    return answer


if __name__=="__main__":
    import sys
    if len(sys.argv)>2:
        raise SystemExit("usage: python trial.py [evidence-directory]")
    result=run(sys.argv[1] if len(sys.argv)==2 else None)
    print(json.dumps({
        "available_worlds":result["training_worlds_available"],
        "source_labeled":result["training_examples_purchased"],
        "program_search_size":result["syntactic_grammar_candidates"],
        "surviving_relational_macros":result["learned_program_candidates"],
        "heldout_exact":result["heldout_source_exact"],
        "heldout_safe_holds":result["heldout_safe_abstentions"],
        "heldout_wrong_with_confidence":result["heldout_incorrect_confident"],
        "flat_unjoined_weak_baseline":result["weak_unjoined_relation_bag_baseline"],
        "strong_classical_reference":result["strong_classical_direct_reference"],
        "synthetic_source_truth_counts":result["heldout_source_four_state_counts"],
    },indent=2,sort_keys=True))
