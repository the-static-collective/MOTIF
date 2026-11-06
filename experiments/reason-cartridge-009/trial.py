"""Bounded two-family grammar invention experiment with strong classical control.

No claim of general-purpose new operators: the invented macro is a new
recursive expression shape over existing binary Boolean AND/OR primitives.
"""
from __future__ import annotations

from itertools import combinations
from pathlib import Path
import json

from grammar import HOLD,Grammar,discovery,validate,interpret,digest,LEVELS
from receiver import Receiver
from source import (Case,SourceOwner,INITIAL,HOLDOUT,FAMILIES,
                    lessons,heldout,future,bfs)


def invention(family,max_calls=24):
    if family not in FAMILIES:raise HOLD("Unrecognized source family")
    owner=SourceOwner(family,max_queries=max_calls)
    raw=discovery(family,lessons(family),owner,max_cost=11,max_calls=max_calls)
    method=validate(raw)
    reviewer=Receiver(raw)
    review=reviewer.preview(heldout(family))
    if review["all_32_feature_states_match"]:
        reviewer.admit("ADMIT_READ_ONLY",review["review_digest"])
    return raw,reviewer,review,owner


def fixed_family_accuracy(family):
    """Full-domain classical baselines for *fixed old DSL* vs invented AST."""
    count_old=0
    count_008=0
    for a,b in combinations(tuple(combinations(range(5),2)),2):
        hits=sum(
            (all(bool(m&(1<<i)) for i in a)
              or all(bool(m&(1<<i)) for i in b))==bfs(Case(m,family))
            for m in range(32)
        )
        count_old=max(count_old,hits)
    for triple in combinations(range(5),3):
        for pair in combinations(range(5),2):
            hits=sum(
                (all(bool(m&(1<<i)) for i in triple)
                 or all(bool(m&(1<<i)) for i in pair))==bfs(Case(m,family))
                for m in range(32)
            )
            count_008=max(count_008,hits)
    return {"fixed_007_best_correct":count_old,
            "fixed_008_best_correct":count_008,
            "classical_exact_BFS_correct":32}


def cost_model(source_calls,portfolio):
    """ALL hypothetical units; no measured compute, money or resource savings."""
    if type(source_calls) is not int or type(portfolio) is not int or portfolio<1:
        raise HOLD("Invalid declared reasoning budget")
    # The enumerator's complete search space is charged, regardless of the
    # actual first success. Prevent 'free' failed hypotheses.
    whole=Grammar()
    program_evaluations=len(whole.expressions)
    source_lookup=1.5
    query_cost=source_calls*source_lookup
    certification=len(HOLDOUT)*source_lookup
    search_cost=program_evaluations*.005
    inference=portfolio*.25
    compiled=round(query_cost+certification+search_cost+inference,6)
    classical=round(portfolio*source_lookup,6)
    return {"model":"ILLUSTRATIVE_NOT_MEASURED",
            "oracle_calls":source_calls,
            "candidate_signature_search_cost":round(search_cost,6),
            "candidate_semantics_enumerated":program_evaluations,
            "teacher_challenge_cost":round(query_cost,6),
            "independent_holdout_certification_cost":round(certification,6),
            "compiled_inference_cost":round(inference,6),
            "compiled_total":compiled,"direct_BFS_total":classical,
            "winner":"COMPILED_GRAMMAR" if compiled<classical else "DIRECT_BFS",
            "imputed_nontransferable_savings":
                round(max(0,classical-compiled),6),
            "real_money":False}


def run(output=None):
    cases={}
    for family in FAMILIES:
        raw,receiver,review,owner=invention(family)
        m=validate(raw)
        check={size:cost_model(owner.calls,size) for size in (1,32,64)}
        targets=future(family,64)
        predicted=[receiver.suggest(c)["prediction"] for c in targets]
        observed=[bfs(c) for c in targets]
        if predicted!=observed:
            raise HOLD("Renamed deployment family disagreed with source-owned BFS")
        cases[family]={
            "method":m,"raw_method":raw,
            "review":review,
            "owner":owner,
            "source_owned_future_correct":sum(p==o for p,o in zip(predicted,observed)),
            "source_owned_future_cases":len(targets),
            "fixed_family_baselines":fixed_family_accuracy(family),
            "costs":check,
        }
    first=cases["LONG_SHORT"]
    second=cases["BRIDGE"]
    if (first["method"]["program"]["binary_ast_nodes"]!=9
            or second["method"]["program"]["binary_ast_nodes"]!=11
            or second["fixed_family_baselines"]["fixed_008_best_correct"]>=32
            or second["fixed_family_baselines"]["fixed_007_best_correct"]>=32):
        raise HOLD("Independent cross-family grammar baseline no longer differentiates")
    result={
        "schema":"motif.reason.grammar-inventor-experiment.v1",
        "grammar_search":"GENERAL_BINARY_MONOTONE_AST_NOT_FIXED_EXTENSION_FAMILY",
        "source_revision":first["method"]["source_revision"],
        "source_blob":first["method"]["source_owner_blob"],
        "families":{},
        "two_nonisomorphic_source_graphs":True,
        "both_use_same_source_blind_grammar_algorithm":True,
        "independent_source_BFS_is_full_information_classical_baseline":True,
        "invented_mathematically_new_boolean_operator":False,
        "unbounded_program_invention":False,
        "real_world_authority":False,"external_execution":False,
    }
    for name,case in cases.items():
        method=case["method"]
        data={
            "initial_examples":len(INITIAL),
            "adaptive_queries_or_challenges":case["owner"].calls,
            "public_observations":len(method["public_observations"]),
            "grammar_tiers_refuted":[g["max_binary_ast_nodes"]
                                   for g in method["rejected_smaller_grammar_tiers"]],
            "exhaustive_smaller_program_refutations":
                method["rejected_smaller_grammar_tiers"][-1]["candidate_functions_refuted"],
            "found_expression_node_count":method["program"]["binary_ast_nodes"],
            "inferred_macro_shape":method["program"]["inferred_typed_macro_shape"],
            "learned_expression":method["program"]["ast"],
            "source_owner_challenge_passed_without_holdout":True,
            "sealed_holdout_cases":case["review"]["heldout_cases"],
            "sealed_holdout_errors":case["review"]["heldout_errors"],
            "post_synthesis_acquisition_errors":
                case["review"]["post_synthesis_acquisition_errors"],
            "read_only_admitted":case["review"]["all_32_feature_states_match"],
            "renamed_future_correct":case["source_owned_future_correct"],
            "renamed_future_cases":case["source_owned_future_cases"],
            "legacy_baselines":case["fixed_family_baselines"],
            "cost_one_task":case["costs"][1],
            "cost_thirty_two_tasks":case["costs"][32],
            "cost_sixty_four_tasks":case["costs"][64],
            "method_checksum":method["checksum_sha256"],
            "certification_checksum":case["review"]["review_digest"],
            "synthetic_source_only":True,
            "external_actions":False,
        }
        result["families"][name]=data
    if output:
        p=Path(output)
        p.mkdir(parents=True,exist_ok=True)
        for family,case in cases.items():
            (p/(family.lower()+"-method.json")).write_text(case["raw_method"])
            (p/(family.lower()+"-certification.json")).write_text(
                json.dumps(case["review"],indent=2,sort_keys=True)+"\n")
            (p/(family.lower()+"-oracle-trace.json")).write_text(
                json.dumps(case["owner"].history,indent=2,sort_keys=True)+"\n")
        (p/"benchmark.json").write_text(
            json.dumps(result,indent=2,sort_keys=True)+"\n")
    return result


if __name__=="__main__":
    import sys
    if len(sys.argv)>2:raise SystemExit("usage: python trial.py [evidence-directory]")
    print(json.dumps(run(sys.argv[1] if len(sys.argv)==2 else None),
                     sort_keys=True,indent=2))
