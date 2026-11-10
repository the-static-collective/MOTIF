"""LEGIT-027: test which *part* of MOTIF's graph meta-policy transfers.

The graph-specific LEAF_FIRST source gate has no meaning in other domains.
Only the adopted COUNT_DIVERSITY priority scorer plus STATIC ordering is
ported as a typed rule. Each target domain still supplies training data
to rank *its own* candidate questions. This is cross-domain transfer
of a scoring principle, NOT zero-shot transfer of frozen graph question
orders or discovery of new general mathematics.
"""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
from pathlib import Path
from time import process_time_ns
import json
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from tasks import (DOMAINS,TRAIN_SEEDS,FUTURE_SEEDS,Hold,questions,world,
                   observe,independent_observe,oracle_nonidentical)

PRIOR_META_PATH=HERE.parent/"legit026"/"generated"/"selected_meta_cartridge.json"
GRAPH_FREEZE="ba8a947652ff39559278e6d339923e4abed408434b7d6894db62f8f3bb9550e1"
STATUS="RESEARCH_HOLD_CROSS_DOMAIN_GENERALIZATION_NOT_ESTABLISHED"


def prior_graph_rule():
    archive=json.loads(PRIOR_META_PATH.read_text(encoding="utf-8"))
    entry=archive["typed_rewrite"]["selected_and_adopted_program"]
    if archive["experiment"]!="MOTIF-LEGIT-026" or entry!=[
            "LEAF_FIRST","COUNT_DIVERSITY","STATIC"] or (
            archive["training"]["frozen_all_five_policies_sha256"]!=GRAPH_FREEZE):
        raise Hold("prior verified graph policy changed: do not silently adapt")
    return {
        "origin":"LEGIT026_FROZEN_TRAINING_CROSSVALIDATED_GRAPH_PROGRAM",
        "source_meta":entry,
        "source_frozen_sha256":GRAPH_FREEZE,
        "transferred_rule":"COUNT_DIVERSITY",
        "transferred_update":"STATIC",
        "graph_specific_LEAF_FIRST_gate_not_transferred":True,
        "target_domain_candidate_grammar_still_engineer_authored":True,
        "target_domain_training_observations_used_for_order_selection":True,
        "not_zero_shot_frozen_graph_question_order":True,
    }


def observations(domain,cases):
    return tuple({
        "case_id":case["case_id"],
        "case":case,
        "answers":{question:observe(domain,case,question)
                   for question in questions(domain)}
    } for case in cases)


def train_plan(domain,training_rows):
    """All candidate source observations come from target TRAINING only."""
    universe=questions(domain)
    if not training_rows:
        raise Hold("no training evidence")
    sample_labels=[r["case_id"] for r in training_rows]
    if len(sample_labels)!=len(set(sample_labels)):
        raise Hold("duplicate training problem")

    def count_diversity(question):
        return len({val for r in training_rows for val in r["answers"][question]})
    def coverage(question,subset):
        return sum(r["answers"][question][0]!=r["answers"][question][1]
                   for r in subset)

    static_diversity=tuple(sorted(universe,key=lambda q:(
        -count_diversity(q),universe.index(q))))
    static_gain=tuple(sorted(universe,key=lambda q:(
        -coverage(q,training_rows),universe.index(q))))
    remaining=list(universe)
    unresolved=list(training_rows)
    greedy=[]
    while remaining:
        winner=min(remaining,key=lambda q:(
            -coverage(q,unresolved),universe.index(q)))
        greedy.append(winner)
        remaining.remove(winner)
        unresolved=[r for r in unresolved if
                    r["answers"][winner][0]==r["answers"][winner][1]]

    # Domain-informed control, fixed before looking at any data.
    if domain==DOMAINS[0]:
        # For integer polynomials, high-modulus nonzero x supplies many
        # possible unequal residues; still no guarantee for every case.
        preferred=((2,11),(-2,11),(3,11),(-3,11),(2,7),(-2,7))
    else:
        # For inequality countermodels, sample central lattice points
        # before corners. This is hand-specified conventional heuristic.
        preferred=((2,2),(3,3),(2,3),(3,2),(1,2),(2,1))
    conventional=tuple(q for q in preferred if q in universe)+tuple(
        q for q in universe if q not in preferred)
    plans={
        "LEGIT026_GRAPH_SCORER_TRANSFERRED":static_diversity,
        "TARGET_CLASSICAL_STATIC_GAIN":static_gain,
        "TARGET_CLASSICAL_RESIDUAL_GREEDY":tuple(greedy),
        "TARGET_DOMAIN_HEURISTIC":conventional,
        "CANONICAL_FIXED":universe,
    }
    if any(len(plan)!=len(universe) or set(plan)!=set(universe)
           for plan in plans.values()):
        raise Hold("different query access across methods")
    frozen={name:[list(q) for q in plan] for name,plan in plans.items()}
    digest=sha256(json.dumps(frozen,sort_keys=True,
                separators=(",",":")).encode()).hexdigest()
    return plans,{
        "training_case_ids":sample_labels,
        "training_question_observations":[{
            "case_id":r["case_id"],
            "by_question":[{"question":list(q),"values":list(r["answers"][q])}
                           for q in universe]
        } for r in training_rows],
        "source_question_count":len(universe),
        "graph_transfer_uses_count_diversity_not_leaf_gate":True,
        "matched_source_question_grammars":True,
        "frozen_all_order_sha256":digest,
        "frozen_orders":frozen,
        "heldout_cases_not_opened_during_training":True,
    }


def prepare_training():
    graph_origin=prior_graph_rule()
    plans={}
    audit={"graph_rule":graph_origin,"domains":{}}
    for domain in DOMAINS:
        cases=[]
        provenance=[]
        for seed in TRAIN_SEEDS:
            current,origin=world(domain,seed)
            cases.extend(current)
            provenance.append(origin)
        orders,receipt=train_plan(domain,observations(domain,cases))
        plans[domain]=orders
        audit["domains"][domain]={
            "training_worlds":provenance, "frozen_selection":receipt}
    hash_input={domain:audit["domains"][domain]["frozen_selection"][
        "frozen_all_order_sha256"] for domain in DOMAINS}
    audit["combined_frozen_sha256"]=sha256(json.dumps(
        hash_input,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    audit["future_world_function_not_called"]=True
    return plans,audit


def replay(domain,cases,plans):
    """Independently verify every attempted question, including negatives."""
    baseline=questions(domain)[:2]
    choices={"NO_ESCAPE_OLD_TWO_QUESTIONS":baseline,**plans}
    results={}
    for name,plan in choices.items():
        start=process_time_ns()
        receipts=[]
        for case in cases:
            if not oracle_nonidentical(domain,case):
                raise Hold("challenge does not possess a counterexample")
            trace=[]
            for question in plan:
                observed=observe(domain,case,question)
                independently=independent_observe(domain,case,question)
                if observed!=independently:
                    raise Hold("candidate question failed independent oracle")
                witness=(observed[0]!=observed[1])
                trace.append({
                    "question":list(question),
                    "observed_pair":list(observed),
                    "independent_verification":True,
                    "is_valid_counterexample":witness,
                })
                if witness:
                    break
            receipts.append({
                "case_id":case["case_id"],
                "verdict":"EXACT_COUNTEREXAMPLE" if trace[-1][
                    "is_valid_counterexample"] else "ABSTAIN",
                "questions":len(trace),
                "full_question_receipts":trace,
            })
        results[name]={
            "solved":sum(r["verdict"]=="EXACT_COUNTEREXAMPLE"
                         for r in receipts),
            "cases":len(cases),
            "questions":sum(r["questions"] for r in receipts),
            "cpu_ms_including_verification":round(
                (process_time_ns()-start)/1e6,5),
            "all_attempted_question_receipts":receipts,
        }
    return results


def run():
    start=process_time_ns()
    plans,audit=prepare_training()
    # Future worlds are first opened only AFTER the complete order is
    # frozen. Separate seed list is a registered protocol, not hidden.
    result={}
    provenance={}
    for domain in DOMAINS:
        domains={}
        for seed in FUTURE_SEEDS:
            cases,origin=world(domain,seed)
            domains["seed_%d"%seed]=replay(domain,cases,plans[domain])
            provenance["%s_seed_%d"%(domain,seed)]=origin
        result[domain]=domains
    summaries={}
    for domain,worlds in result.items():
        summaries[domain]={}
        for method in next(iter(worlds.values())):
            byworld=[arms[method] for arms in worlds.values()]
            summaries[domain][method]={
                "cases":sum(x["cases"] for x in byworld),
                "solved":sum(x["solved"] for x in byworld),
                "questions":sum(x["questions"] for x in byworld),
                "cpu_ms":round(sum(x["cpu_ms_including_verification"]
                                   for x in byworld),5),
            }
    return {
        "experiment":"MOTIF-LEGIT-027",
        "title":"QUESTION TRANSFER — WILL A GRAPH-LEARNED RESEARCH RULE GENERALIZE?",
        "status":STATUS,
        "graph_origin":prior_graph_rule(),
        "two_new_different_goal_contracts":list(DOMAINS),
        "transfer_scope":"question_priority_scoring_rule_not_specific_questions",
        "training_and_freeze":audit,
        "future_world_provenance":provenance,
        "future_evidence":result,
        "aggregate_results":summaries,
        "resource_limitations":[
            "No external independently blinded tasks",
            "Both future world generators engineer-authored and conditioned on old-probe failure",
            "Target-domain training data used to instantiate ALL source priorities",
            "Only scoring rule transferred, not graph-only structural gate",
            "Not a proof of cross-domain general mathematical superiority",
            "No formal theorem discovery or autonomous creation of new algorithm",
            "Policy success defined by exact counterexample construction, not equivalence proof",
            "Human engineering, corpus design and verifier costs not included in CPU totals",
            "Only two future fixed seeds per domain; not statistically robust",
        ],
        "total_cpu_ms_including_training_and_evaluation":round(
            (process_time_ns()-start)/1e6,5),
    }


if __name__=="__main__":
    if sys.argv[1:]!=["--emit"]:
        raise SystemExit("Usage: python experiments/legit027/transfer.py --emit")
    print(json.dumps(run(),indent=2,sort_keys=True))
