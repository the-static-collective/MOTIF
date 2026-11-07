"""RING-011 graph evidence: voice/scope invention, source limits and failures.

Every test result is checked against case-level reported typed semantic
graphs. Source carrier NEVER constitutes independent corroboration. No raw
private book content is present in the experimental text or evidence.

The first two suites were inspected during code repair; they are explicitly
marked as regression datasets. The later suite was generated after repair
and is still authored by the same developer, not independent human speech.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import corpus,binder,benchmark

SCHEMA="motif.ring011.carrier-scope-measured-hypergraph.v1"

class HOLD(ValueError):
    pass


def digest(x):
    return corpus.digest(x)


def verify(frozen,report):
    benchmark.verify_frozen(frozen)
    if (not isinstance(report,dict)
            or report.get("schema")!=benchmark.SCHEMA
            or report.get("status")!="NESTED_VOICE_BINDER_FROZEN_AND_FALSIFIED"
            or report.get("receipt_sha256")!=digest({
                k:v for k,v in report.items() if k!="receipt_sha256"})
            or report.get("frozen_program_sha256")!=frozen["receipt_sha256"]
            or report.get("source_derived_program_sha256")!=frozen[
                "winning_program"]["receipt_sha256"]
            or report.get("outside_actions_executed") is not False
            or report.get("authority")!="NONE"
            or report.get("new_cartridge_or_external_tool_admissions")!=0
            or report.get("corpus_inspired_by_private_editing_structure_not_private_quotes") is not True
            or report.get("original_two_test_families_are_now_debugging_regressions") is not True
            or report.get("third_family_created_after_post_falsifier_source_fix") is not True):
        raise HOLD("Corrupt source binding or invented experimental authority")
    suites=report.get("test_packets")
    if not isinstance(suites,list) or len(suites)!=3:
        raise HOLD("Need exactly three source scenario packets")
    seen=set()
    totals={}
    for i,suite in enumerate(suites):
        source=suite.get("author_created_source_sha256")
        if (type(source) is not str or len(source)!=64 or source in seen
                or suite.get("labels_not_seen_by_algorithm_search") is not True
                or suite.get("private_manuscript_contents_not_in_test") is not True
                or suite.get("source_events_and_carriers_externally_supplied") is not True
                or suite.get("is_fresh_to_repaired_algorithm") is not (i==2)
                or suite.get("first_two_families_used_to_identify_previous_model_defect") is not (i!=2)):
            raise HOLD("Misclassified/duplicate synthetic source and its trial role")
        seen.add(source)
        population=suite.get("comparisons")
        if not isinstance(population,dict) or set(population)!={
            "source_induced_scope_binder","same_data_word_bayes",
            "same_data_bigram_bayes","always_hold"}:
            raise HOLD("Missing strong source-matched comparator")
        for name,method in population.items():
            metrics=method.get("metrics")
            rows=method.get("per_case")
            if (not isinstance(rows,list) or len(rows)!=suite.get("case_count")
                    or not isinstance(metrics,dict) or metrics.get("cases")!=len(rows)
                    or sum(x["exact"] for x in rows)!=metrics["exact_graphs"]
                    or sum(x["false_root_action_promotion"] for x in rows)
                       !=metrics["false_root_action_promotion"]
                    or sum(x["abstained"] for x in rows)!=metrics["abstained"]
                    or sum(not x["exact"] and not x["abstained"] for x in rows)
                       !=metrics["wrong_decisive"]):
                raise HOLD("Individual event-graph source receipts disagree with counts")
            for item in rows:
                if (not isinstance(item.get("target"),dict)
                        or item["target"].get("CARRIER") not in corpus.CARRIERS
                        or item["target"].get("EVIDENCE_STATUS")!=corpus.EPISTEMIC[
                            item["target"]["CARRIER"]]):
                    raise HOLD("Source-carrier truth was fabricated or dropped")
                predicted=item.get("predicted")
                if predicted is not None and (
                        predicted.get("CARRIER")!=item["target"]["CARRIER"]
                        or predicted.get("EVIDENCE_STATUS")!=
                        corpus.EPISTEMIC[item["target"]["CARRIER"]]):
                    raise HOLD("Learned model promoted or replaced document provenance")
            aggregate=totals.setdefault(name,{k:0 for k in metrics})
            for key in aggregate:
                aggregate[key]+=metrics[key]
    if totals!=report.get("combined"):
        raise HOLD("Cross-suite aggregate changed from the per-case observations")
    unbound=report.get("unbound_cryptic_diagnostics")
    if (not isinstance(unbound,list) or len(unbound)!=6
            or any(x.get("status")!="HOLD" or x.get("hallucinated_event_graph") is not False
                   for x in unbound)):
        raise HOLD("Ungrounded cryptic speech must never fabricate a graph")
    return suites


def build(frozen,report):
    groups=verify(frozen,report)
    program=frozen["winning_program"]
    source="train:"+frozen["source_train_sha256"]
    dev="dev:"+frozen["source_dev_sha256"]
    learned="binder:"+program["receipt_sha256"]
    vertices=[
        {"id":source,"type":"AUTHOR_CONTRASTED_GRAPH_MEANINGS",
         "external_event_and_carrier_metadata_required":True},
        {"id":dev,"type":"AUTHOR_MODEL_SELECTION_EXAMPLES"},
        {"id":learned,"type":"SOURCE_DERIVED_CLAUSE_BINDER",
         "rewrite_instances":program["source_induced_edge_rewrites"],
         "context_rule_instances":program["source_induced_relation_count"],
         "polarity_insertion_instances":program[
             "source_derived_polarity_insertion_count"],
         "runtime_is_predefined":True},
    ]
    checks=[]
    for suite in groups:
        name="trial:"+suite["author_created_source_sha256"]
        checks.append(name)
        vertices.append({
            "id":name,"type":"AUTHOR_CREATED_GRAPH_LANGUAGE_CHALLENGE",
            "family":suite["family"],
            "regression_from_previous_observed_failures":
                suite["first_two_families_used_to_identify_previous_model_defect"],
            "independent_human_ground_truth":False,
        })
    scores=report["combined"]["source_induced_scope_binder"]
    classical=report["combined"]["same_data_bigram_bayes"]
    edges=[
        {
            "id":"generated:contrast-graphs-to-nested-voice-hypothesis",
            "kind":"SUPERVISED_SOURCE_CONTRAST_COMPOSED_TYPED_RELATIONS",
            "tails":[source,dev],
            "heads":[learned,
                     "capability:typed_source_nested_scope_containment",
                     "method:source_local_polarity_insertion",
                     "open_question:discover_new_relation_kinds_without_labeled_ontology"],
            "derived_relational_rewrites":program["source_induced_edge_rewrites"],
            "learned_lexical_structural_rules":program["source_induced_relation_count"],
            "observed_prior_test_failure_prompted_developer_repair":True,
            "base_new_semantic_opcode_discovered":False,
        },
        {
            "id":"observed:cryptic-scope-versus-classical-and-provenance",
            "kind":"AUTHOR_SYNTHETIC_TYPED_GRAPH_OUTCOMES_AND_FALSE_CLEARANCE_RISK",
            "tails":[learned,source,dev,*checks],
            "heads":["outcome:correct_nested_graph_interpretations",
                     "outcome:incorrect_root_action_promotions",
                     "outcome:incorrect_nested_voice_and_polarity",
                     "outcome:provenance_carrier_never_authenticates_event",
                     "outcome:unbound_cryptic_speech_remains_unresolved"],
            "total_cases":scores["cases"],
            "source_derived_binder_metrics":scores,
            "same_data_bigram_bayes_metrics":classical,
            "difference_in_exact_graphs_vs_bigram":scores["exact_graphs"]-
                classical["exact_graphs"],
            "false_root_action_readings":scores["false_root_action_promotion"],
            "unbound_cryptic_holds":len(report["unbound_cryptic_diagnostics"]),
            "independent_real_world_semantic_ability_proven":False,
            "private_manuscript_text_published":False,
            "runtime_promoted_to_authority":False,
        },
    ]
    outcome={
        "schema":SCHEMA,
        "frozen_program_sha256":frozen["receipt_sha256"],
        "observed_source_sha256":report["receipt_sha256"],
        "vertices":vertices,"hyperedges":edges,
        "hard_carrier_evidence_classes_preserved":True,
        "two_debugging_families_not_independent_clean_tests":True,
        "original_book_quotes_or_personal_details_included":False,
        "real_world_semantic_ontology_independently_invented":False,
        "new_executable_methods_installed":0,
        "external_action_executed":False,
        "authority":"NONE",
    }
    outcome["receipt_sha256"]=digest(outcome)
    return outcome


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--frozen",required=True,type=Path)
    p.add_argument("--benchmark",required=True,type=Path)
    p.add_argument("--out",type=Path)
    args=p.parse_args()
    try:
        out=build(json.loads(args.frozen.read_text()),
                  json.loads(args.benchmark.read_text()))
        if args.out:
            args.out.parent.mkdir(parents=True,exist_ok=True)
            args.out.write_text(json.dumps(out,sort_keys=True,indent=2)+"\n")
        measured=out["hyperedges"][1]
        print(json.dumps({
            "schema":out["schema"],
            "relational_rules":out["hyperedges"][0]["learned_lexical_structural_rules"],
            "graph_rewrites":out["hyperedges"][0]["derived_relational_rewrites"],
            "exact":measured["source_derived_binder_metrics"]["exact_graphs"],
            "wrong":measured["source_derived_binder_metrics"]["wrong_decisive"],
            "false_root_action":measured["false_root_action_readings"],
            "held_unbound":measured["unbound_cryptic_holds"],
            "receipt":out["receipt_sha256"],
        },sort_keys=True))
    except (HOLD,benchmark.HOLD,binder.HOLD,ValueError) as exc:
        print(json.dumps({"status":"HOLD","reason":str(exc)}))
        raise SystemExit(2)


if __name__=="__main__":
    main()
