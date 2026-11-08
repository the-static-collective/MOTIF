"""RING-012 evidence graph: do not transform uncertainty into certainty.

All source methods share supervised training, and their votes are explicitly
NOT independent witnesses. Preserve:
  - synthetic admissible-interpretation coverage;
  - excessive candidate breadth;
  - excluded readings;
  - unresolved source events;
  - conflicting partial perspectives;
  - erroneous single root-action interpretations;
  - document-carrier evidence class (never event authentication).

A semantic ambiguity graph is not permission to act or proof that any
author-suggested interpretation corresponds to a real person or event.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import lattice,calibration

SCHEMA="motif.ring012.measured-ambiguity-evidence-hypergraph.v1"

class HOLD(ValueError):
    pass


def digest(value):
    return lattice.digest(value)


def verify(policy,report):
    lattice.validate_policy(policy)
    if (not isinstance(report,dict)
            or report.get("schema")!=
            "motif.ring012.postfreeze-ambiguity-native-trial.v1"
            or report.get("status")!=
            "MULTI_READING_OPEN_WORLD_LATTICE_TESTED_POST_FREEZE"
            or report.get("receipt_sha256")!=digest({
                k:v for k,v in report.items() if k!="receipt_sha256"})
            or report.get("source_policy_sha256")!=policy["receipt_sha256"]
            or report.get("meaning_is_set_valued_and_not_forced_to_one") is not True
            or report.get("all_interpretations_remain_open_world") is not True
            or report.get("witnessed_source_methods_share_correlated_training") is not True
            or report.get("authored_semantic_ambiguity_not_real_world_interpretation") is not True
            or report.get("source_carrier_authenticity_not_claimed") is not True
            or report.get("no_generated_language_hypothesis_can_authorize_an_action") is not True
            or report.get("new_executable_methods_installed")!=0
            or report.get("external_actions_executed") is not False
            or report.get("authority")!="NONE"):
        raise HOLD("Misrepresented, modified or unauthorized ambiguity evidence")
    packs=report.get("test_packets")
    if not isinstance(packs,list) or len(packs)!=2:
        raise HOLD("Expected two distinct author language worlds")
    source_ids=set()
    sums={}
    for pack in packs:
        sid=pack.get("packet_sha256")
        if (type(sid) is not str or len(sid)!=64 or sid in source_ids
                or pack.get("labels_read_only_after_policy_frozen") is not True
                or pack.get("no_private_cryptic_manuscript_text_used") is not True
                or pack.get("source_ontology_predefined_by_author") is not True
                or pack.get("cases")!=60):
            raise HOLD("Duplicate or under-scoped source packet")
        source_ids.add(sid)
        witnesses=pack.get("case_witnesses")
        counts=pack.get("author_tag_distribution")
        if (not isinstance(witnesses,list) or len(witnesses)!=pack["cases"]
                or counts!={"UNIQUE":24,"AMBIGUOUS":24,"UNBOUND":12}):
            raise HOLD("Author truth-set cardinality not tracked")
        scores=pack.get("scores")
        expect={
            "open_perspective_lattice","single_derived_binder",
            "single_word_bayes","single_bigram_bayes",
            "uncalibrated_method_union","all_24_possible_graphs","always_hold",
        }
        if not isinstance(scores,dict) or set(scores)!=expect:
            raise HOLD("Missing single-decision or full-ignorance controls")
        for name in expect:
            rows=[w.get("predictions",{}).get(name) for w in witnesses]
            if any(not isinstance(row,dict) for row in rows):
                raise HOLD("Missing case-level source error witness")
            m=scores[name]
            derived={
                "cases":len(rows),
                "complete_author_reading_coverage":sum(x[
                    "all_readings_retained"] for x in rows),
                "missing_authored_readings":sum(x["missing_reading_count"] for x in rows),
                "excess_proposed_readings":sum(x["excess_reading_count"] for x in rows),
                "concrete_readings_total":sum(x["candidate_graphs"] for x in rows),
                "multi_world_outputs":sum(x["multiple_readings_preserved"] for x in rows),
                "false_single_root_action":sum(x["unsupported_single_root_action"] for x in rows),
                "correct_unbound_holds":sum(
                    w["authored_reading_count"]==0 and row["unbound_held"]
                    for w,row in zip(witnesses,rows)),
                "author_ambiguous_cases_with_at_least_two_candidates":sum(
                    w["authored_reading_count"]>=2 and row["multiple_readings_preserved"]
                    for w,row in zip(witnesses,rows)),
                "author_ambiguous_cases_total":sum(
                    w["authored_reading_count"]>=2 for w in witnesses),
                "average_concrete_graphs":round(
                    sum(x["candidate_graphs"] for x in rows)/max(1,len(rows)),4),
            }
            if derived!=m:
                raise HOLD("Evidence receipts suppress or fabricate case errors")
            agg=sums.setdefault(name,{k:0 for k in m
                                       if k!="average_concrete_graphs"})
            for key in agg:
                agg[key]+=m[key]
        for witness in witnesses:
            if (witness.get("carrier") not in lattice.corpus.CARRIERS
                    or witness.get("open_world_always") is not True
                    or witness.get("ambiguity_does_not_force_an_interruption") is not True
                    or not isinstance(witness.get("source_conditional_invariants"),dict)
                    or witness.get("optional_discriminator") not in (
                        None,"WHO_IF_ANY_REQUESTED_THIS_EVENT",
                        "WHICH_SCOPE_OWNS_THE_EVENT",
                        "IS_THIS_DIRECT_SPEECH_OR_REPORTED_SPEECH",
                        "DOES_NEGATION_APPLY_TO_THIS_EVENT")
                    or witness.get("author_meanings_do_not_authenticate_real_events") is not True
                    or type(witness.get("source_sha256")) is not str
                    or len(witness["source_sha256"])!=64
                    or len(witness.get("authored_reading_hashes",[]))!=witness[
                        "authored_reading_count"]):
                raise HOLD("Source meaning provenance or possibility misrepresented")
    for name,m in sums.items():
        m["average_concrete_graphs"]=round(m["concrete_readings_total"]/
                                           m["cases"],4)
    if sums!=report.get("combined"):
        raise HOLD("Cross-world aggregate differs from individual source witnesses")
    return packs


def build(policy,report):
    packs=verify(policy,report)
    source="train:"+policy["source_train_sha256"]
    dev="dev:"+policy["original_dev_source_sha256"]
    frozen="policy:"+policy["receipt_sha256"]
    methods=["method:"+x for x in lattice.METHODS]
    vertices=[
        {"id":source,"type":"SINGLE_AUTHOR_LABELLED_LANGUAGE_EVIDENCE"},
        {"id":dev,"type":"AUTHOR_CHOSEN_UNCERTAINTY_CALIBRATION_SOURCE"},
        {"id":frozen,"type":"OPEN_WORLD_SET_VALUED_REASONING_POLICY",
         "source_methods_share_training":True,
         "not_a_calibrated_human_language_probability":True},
    ]+[{"id":name,"type":"CORRELATED_NONAUTHORITATIVE_METHOD"}
       for name in methods]
    packet_refs=[]
    for pack in packs:
        k="trial:"+pack["packet_sha256"]
        packet_refs.append(k)
        vertices.append({
            "id":k,"type":"AUTHOR_CREATED_SET_VALUED_LANGUAGE_CHALLENGE",
            "admissible_readings_not_authenticated_historical_truth":True,
            "counts":pack["author_tag_distribution"],
        })
    m=report["combined"]["open_perspective_lattice"]
    conditional_cases=sum(
        bool(x["source_conditional_invariants"])
        for p in packs for x in p["case_witnesses"])
    discriminator_cases=sum(
        x["optional_discriminator"] is not None
        for p in packs for x in p["case_witnesses"])
    union=report["combined"]["uncalibrated_method_union"]
    full=report["combined"]["all_24_possible_graphs"]
    edges=[
        {
            "id":"derived:three-dependent-methods-to-open-perspective-lattice",
            "kind":"CALIBRATED_CONDITIONAL_HYPOTHESIS_SETS",
            "tails":[source,dev,*methods],
            "heads":[frozen,
                     "outcome:competing_interpretations_retained",
                     "limitation:unmodeled_interpretations_always_possible"],
            "calibration_candidates_tested":policy["calibration_candidates_executed"],
            "original_methods_have_correlated_errors":True,
            "new_mathematical_operator_invented":False,
        },
        {
            "id":"observed:ambiguous-meaning-coverage-versus-volume",
            "kind":"MEASURED_SYNTHETIC_MULTIPLE_ADMISSIBLE_PERSPECTIVES",
            "tails":[source,dev,frozen,*packet_refs],
            "heads":["outcome:all_author_readings_retained",
                     "cost:excess_hypothesized_worlds",
                     "risk:excluded_true_author_readings",
                     "risk:false_single_directive_root",
                     "frontier:independent_human_ambiguity_judgments",
                     "benefit:conditional_invariants_without_forced_disambiguation"],
            "conditional_invariant_case_count":conditional_cases,
            "optional_discriminator_case_count":discriminator_cases,
            "automatic_ambiguity_interruption_count":0,
            "total_test_cases":m["cases"],
            "authored_admissible_reading_coverage":m[
                "complete_author_reading_coverage"],
            "authored_readings_excluded":m["missing_authored_readings"],
            "extra_hypothesized_readings":m["excess_proposed_readings"],
            "mean_concrete_world_count":m["average_concrete_graphs"],
            "false_single_directive_root_readings":m[
                "false_single_root_action"],
            "unbound_cryptic_holds":m["correct_unbound_holds"],
            "unweighted_method_union":union,
            "uninformative_full_ontology":full,
            "source_ground_truth_is_human_independent":False,
            "document_carrier_is_not_event_proof":True,
            "the_program_does_not_execute_requests":True,
        },
    ]
    graph={
        "schema":SCHEMA,
        "source_calibrated_policy_sha256":policy["receipt_sha256"],
        "source_postfreeze_trial_sha256":report["receipt_sha256"],
        "vertices":vertices,"hyperedges":edges,
        "ambiguity_is_primary_output_not_defect_to_erase":True,
        "open_world_other_always_preserved":True,
        "correlated_source_agreement_does_not_establish_truth":True,
        "no_private_how_to_live_source_passages_in_repo":True,
        "independent_real_world_language_competence_demonstrated":False,
        "automatic_new_cartridge_admissions":0,
        "external_action_executed":False,"authority":"NONE",
    }
    graph["receipt_sha256"]=digest(graph)
    return graph


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--policy",required=True,type=Path)
    p.add_argument("--trial",required=True,type=Path)
    p.add_argument("--out",type=Path)
    args=p.parse_args()
    try:
        result=build(json.loads(args.policy.read_text()),
                     json.loads(args.trial.read_text()))
        if args.out:
            args.out.parent.mkdir(parents=True,exist_ok=True)
            args.out.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
        edge=result["hyperedges"][1]
        print(json.dumps({
            "schema":result["schema"],
            "author_readings_covered":edge["authored_admissible_reading_coverage"],
            "excess_worlds":edge["extra_hypothesized_readings"],
            "false_single_directives":edge["false_single_directive_root_readings"],
            "receipt_sha256":result["receipt_sha256"],
        },sort_keys=True))
    except (HOLD,lattice.HOLD,ValueError) as exc:
        print(json.dumps({"status":"HOLD","reason":str(exc)}))
        raise SystemExit(2)


if __name__=="__main__":
    main()
