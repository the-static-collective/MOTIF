"""LEGIT-023 replay: let tested classical methods compete on Atlas tasks.

Goal A: graph non-isomorphism -> direct VF2++ and 1-WL are legitimate.
Goal B: find a *source graph* with distinct hom counts -> a direct
non-isomorphism decision is NOT an admissible answer. Separate scoreboards.
No heldout response is used in policy selection.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from time import process_time_ns
import json
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "legit022"))
from atlas import cohort, HOLD
from trial import prior_apertures, training_priority
from graph_inventor import grammar, reference_count, characterize
from methods import (EXECUTABLE, FUTURE_ADAPTERS, hom_count,
                     optimal_training_order, joint_wl_separation,
                     vf2pp_decision)

STATUS = "RESEARCH_HOLD_METHOD_PORTFOLIO_NOT_RECURSIVE_COMPOUNDING"


def frozen_policies(train):
    patterns = tuple(grammar())
    priors, prior_receipt = prior_apertures()
    optimal_questions = optimal_training_order(
        train, patterns, reference_count, model="unit")
    optimal_assignments = optimal_training_order(
        train, patterns, reference_count, model="assignments")
    policies = {
        "CANONICAL_CONNECTED": patterns,
        "LEGIT021_PRIOR_APERTURES": tuple(priors) + tuple(
            p for p in patterns if p not in priors),
        "LEGIT022_GREEDY_TRAINED": training_priority(train, patterns),
        "CLASSICAL_DP_OPTIMAL_TRAINING_QUESTIONS": optimal_questions["order"],
        "CLASSICAL_DP_OPTIMAL_TRAINING_ASSIGNMENTS": optimal_assignments["order"],
    }
    for order in policies.values():
        if len(order) != len(patterns) or set(order) != set(patterns):
            raise HOLD("Mismatched question grammar")
    serial = {name: [[p[0], [list(e) for e in p[1]]] for p in order]
              for name, order in policies.items()}
    stamp = sha256(json.dumps(serial, sort_keys=True,
                              separators=(",", ":")).encode()).hexdigest()
    return policies, {
        "sha256_frozen_before_heldout": stamp,
        "full_source_orders": serial,
        "prior_source": prior_receipt,
        "training_dp_unit": {k: v for k, v in optimal_questions.items()
                             if k != "order"},
        "training_dp_assignments": {
            k: v for k, v in optimal_assignments.items() if k != "order"},
        "policies_only_read_training_cases": True,
    }


def examine_pair(pair, ordered):
    answers = []
    for source in ordered:
        two = tuple(hom_count(source, target) for target in pair.graphs)
        oracle = tuple(reference_count(source, target)
                       for target in pair.graphs)
        if tuple(x["value"] for x in two) != oracle:
            raise HOLD("New exact backend disagrees with independent enumerator")
        answers.append({
            "probe": characterize(source),
            "hom_counts": list(oracle),
            "exact_backend": [x["method"] for x in two],
            "independently_checked": True,
            "separates": oracle[0] != oracle[1],
        })
        if answers[-1]["separates"]:
            break
    return {"atlas_ids": list(pair.atlas_ids),
            "hom_witness_found": bool(answers and answers[-1]["separates"]),
            "questions": len(answers),
            "receipt": answers}


def noniso_goal(pair):
    # This algorithm sees the same graph structures as all other methods.
    # It is a different objective and is intentionally NOT counted as a
    # homomorphism-question solution.
    wl = joint_wl_separation(*pair.graphs)
    iso = vf2pp_decision(*pair.graphs)
    if iso["isomorphic"]:
        raise HOLD("Atlas matched non-isomorphic carriers unexpectedly match")
    return {"atlas_ids": list(pair.atlas_ids),
            "direct_VF2pp": iso,
            "joint_exact_1WL": wl,
            "hom_witness_claimed_from_iso": False}


def run():
    train, heldout, source = cohort()
    policies, freeze = frozen_policies(train)
    evaluated = {}
    for name, probes in policies.items():
        start = process_time_ns()
        rows = [examine_pair(pair, probes) for pair in heldout]
        cpu_ms = round((process_time_ns() - start) / 1_000_000, 6)
        evaluated[name] = {
            "heldout_cases": len(rows),
            "solved_hom_witness_cases": sum(x["hom_witness_found"] for x in rows),
            "total_source_questions": sum(x["questions"] for x in rows),
            "cpu_ms_including_independent_per_question_cross_checks": cpu_ms,
            "cpu_not_comparable_to_022_uncached_performance_measurements": True,
            "per_case_evidence": rows,
        }
    result_baseline = [noniso_goal(pair) for pair in heldout]
    return {
        "experiment": "MOTIF-LEGIT-023",
        "title": "THE SHOULDERS OF GIANTS REPERTOIRE",
        "status": STATUS,
        "external_source": source,
        "train_cases": len(train),
        "heldout_cases": len(heldout),
        "available_executable_methods": list(EXECUTABLE),
        "candidate_not_integrated_methods": list(FUTURE_ADAPTERS),
        "freeze": freeze,
        "task_A_direct_graph_nonisomorphism": {
            "goal": "decide if graph pairs are isomorphic",
            "VF2pp_nonisomorphic": sum(
                not x["direct_VF2pp"]["isomorphic"] for x in result_baseline),
            "joint_1WL_certifies_nonisomorphism": sum(
                x["joint_exact_1WL"]["conclusion"]
                == "CERTIFIED_NONISOMORPHIC_BY_INVARIANT"
                for x in result_baseline),
            "cases": result_baseline,
            "not_interchangeable_with_task_B": True,
        },
        "task_B_find_separating_hom_source": {
            "goal": "construct a specific source graph F and independently "
                    "verified unequal hom(F,G1) and hom(F,G2)",
            "same_candidate_source_grammar_across_arms": True,
            "selected_using_training_only": True,
            "cases_by_policy": evaluated,
            "not_interchangeable_with_task_A": True,
        },
        "not_demonstrated": [
            "historically novel mathematical theorem",
            "recursive autonomous self-improvement",
            "state-of-the-art superiority across all mathematical tasks",
            "independently blinded challenge",
            "end-to-end human engineering cost",
        ],
    }


if __name__ == "__main__":
    if sys.argv[1:] != ["--emit"]:
        raise SystemExit("Usage: python experiments/legit023/shoulders.py --emit")
    print(json.dumps(run(), indent=2, sort_keys=True))
