"""COLLECTIVE-002: execute same-information question policies in synthetic worlds.

No blind independent evaluation, no real agents or model calls. The source
owner's hidden graph is only read by evaluator code AFTER a policy is run.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
for folder in ("thought-025", "thought-026", "thought-027",
               "thought-028", "collective001"):
    p = str(HERE.parent / folder)
    if p not in sys.path:
        sys.path.insert(0, p)
sys.path.insert(0, str(HERE))

from specimens import BY_KEY
from memory_benchmark import seeds, new_cases
from weave import investigate as old_investigate
from answer_weave import first_answer
from missing_link import (
    synthetic_owner, derive_questions, investigate, reenter,
    policy_order, exhaustive_classical_reference,
    reference_evaluator_only, evaluate_fixed_order, expected_cost,
)


def source_nodes():
    store = seeds()
    a = BY_KEY["cancel_or_add"]
    a_inputs = {k: v for (k, _), v in zip(a.fields, (3, 5))}
    a_run = old_investigate(a, store, mode="compose")
    a_packet = first_answer(a, store, a_run, a_inputs)

    b = new_cases()["toggle_equipment"]
    store.add_task(b)
    b_inputs = {k: v for (k, _), v in zip(b.fields, (4, 1))}
    b_run = old_investigate(b, store, mode="retrieved")
    b_packet = first_answer(b, store, b_run, b_inputs)
    return a_packet, b_packet, store.registry, a_run, b_run


def run(seeds=range(400, 432)):
    left, right, registry, a_run, b_run = source_nodes()
    first_owner = synthetic_owner(400)
    relevant = derive_questions(left, right, registry, first_owner.contract())
    motif_order = policy_order(relevant)
    strong_order, strong_expected = exhaustive_classical_reference(relevant)
    canonical_order = sorted(relevant, key=lambda q: q["pair"])

    methods = ("MOTIF_TYPED_RELEVANCE_P_OVER_COST",
               "CLASSICAL_EXACT_EXPECTED_OPTIMUM",
               "CLASSICAL_CANONICAL_RELEVANT")
    results = {name: {"cases": 0, "correct": 0, "total_questions": 0,
                      "total_query_cost": 0, "sample_wins": 0}
               for name in methods}
    receipt_example = None
    per_world = []
    for seed in seeds:
        # Each arm has the same hidden fixture, priors and costs.
        # The controller never reads its own owner's hidden truth.
        owner_a = synthetic_owner(seed)
        packet = investigate(left, right, registry, owner_a)
        back = reenter(json.loads(json.dumps(packet)), registry, owner_a)
        found = packet["status"] == "FOUND_VERIFIED_FINITE_LINK"
        hidden = reference_evaluator_only(owner_a, packet["candidate_questions"])
        assert found == hidden
        assert back["new_source_queries"] == 0
        baseline_arms = (
            (methods[0], {"found": found,
                          "queries": owner_a.query_count,
                          "query_cost_paid": packet["query_cost_paid"]}),
            (methods[1], evaluate_fixed_order(
                synthetic_owner(seed), relevant, strong_order)),
            (methods[2], evaluate_fixed_order(
                synthetic_owner(seed), relevant, canonical_order)),
        )
        row = {"seed": seed, "oracle_has_relevant_link": hidden}
        for name, arm in baseline_arms:
            assert arm["found"] == hidden
            record = results[name]
            record["cases"] += 1
            record["correct"] += 1
            record["total_questions"] += arm["queries"]
            record["total_query_cost"] += arm["query_cost_paid"]
            row[name] = {"questions": arm["queries"],
                         "query_cost": arm["query_cost_paid"]}
        per_world.append(row)
        if receipt_example is None:
            receipt_example = packet
    return {
        "schema": "motif.collective002.synthetic-benchmark.v1",
        "source_task_kinds": [left["task_key"], right["task_key"]],
        "source_task_owner_development_queries": {
            "left": a_run["development_queries"],
            "right": b_run["development_queries"],
        },
        "source_nodes_independently_verified_64_cases_each": True,
        "source_nodes_independently_authored_people": False,
        "candidate_questions_derived_from_masks": len(relevant),
        "candidate_question_pairs": [q["pair"] for q in relevant],
        "active_selection_uses_hidden_truth": False,
        "priors_calibrated_to_real_world": False,
        "expected_query_cost_motif": str(expected_cost(motif_order)),
        "expected_query_cost_classical_exact": str(strong_expected),
        "matched_expected_optimum": expected_cost(motif_order) == strong_expected,
        "results": results,
        "per_world": per_world,
        "example_complete_portable_proof_carrying_node": receipt_example,
        "no_real_agents_or_model_calls": True,
        "no_general_novel_algorithm_or_external_authority": True,
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
