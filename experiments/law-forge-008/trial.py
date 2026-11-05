"""LAW-FORGE-008: compare bounded question-selection against classical peers.

No method sees heldout labels before independently reviewing its frozen desk.
The same approved source catalog, unit costs, initial records, maximum budget
and independent evidence are used for every method. A risk-weighted question
policy is a *declared classical heuristic*, not a newly invented algorithm.
"""
from __future__ import annotations

import json
from learner import (
    MAX_QUERIES, DOMAIN, Question, PredictionDesk, SourceContract,
    choose_question, consequence_weight, make_desk, review, rule_library
)
from owner import FAMILIES, World

METHODS = (
    "motif_consequence", "classical_entropy", "classical_fixed",
    "classical_tree", "lookup_only"
)


def inquiry(world, method="motif_consequence", budget=MAX_QUERIES):
    if method not in METHODS:
        raise ValueError("Only frozen inquiry methods")
    if type(budget) is not int or not 0 <= budget <= MAX_QUERIES:
        raise ValueError("Inquiry budget must be an integer between 0 and 24")
    history = list(world.initial())
    catalog = world.query_catalog()
    spent = 0
    proposals = []
    seen = set()
    strategy = (
        "classical_fixed" if method in ("classical_tree", "lookup_only")
        else method
    )
    while spent < budget:
        remaining = budget - spent
        question = choose_question(
            ((row.x, row.y) for row in history),
            catalog, strategy, remaining, seen
        )
        if question is None:
            break
        # Source owner must revalidate its own read-only query catalog.
        checked = Question.from_packet(question.packet())
        returned = world.execute(checked)
        history.append(returned)
        proposals.append(question)
        spent += question.unit_cost
        seen.add(question.x)
    frozen = make_desk(world.contract, tuple(history), method)
    return frozen, tuple(proposals), spent


def trial(world, method="motif_consequence", budget=MAX_QUERIES):
    desk, queries, cost = inquiry(world, method, budget)
    reviewer = review(desk, world.contract, world.independent("review"))
    eligible = reviewer["status"].startswith("ELIGIBLE")
    test = world.independent("test")
    covered = wrong = weighted_covered = weighted_wrong = 0
    if eligible:
        for row in test:
            prediction = desk.predict(row.x, world.contract)
            if prediction["value"] is None:
                continue
            weight = consequence_weight(row.x)
            covered += 1
            weighted_covered += weight
            if prediction["value"] != row.y:
                wrong += 1
                weighted_wrong += weight
    # Different source epochs invalidate a learned lookup/hypothesis desk;
    # semantic similarity is not a license to cross an ownership boundary.
    changed = SourceContract(
        world.contract.source, "different-epoch", world.contract.challenge_id
    )
    stale_probe = desk.predict(tuple([0]*12), changed)
    return {
        "family": world.family,  # evaluator-only scoring metadata
        "seed": world.seed,
        "method": method,
        "source_contract_id": world.contract.id,
        "domain_configurations": DOMAIN,
        "hypothesis_language_size": len(rule_library()),
        "initial_observations": len(world.initial()),
        "source_questions_proposed": len(queries),
        "source_question_cost": cost,
        "question_proposals": [p.packet() for p in queries],
        "exact_lookup_cells": len(desk.snapshot),
        "surviving_hypotheses": len(desk.candidates),
        "independent_review": reviewer,
        "test_total": len(test),
        "test_covered": covered,
        "test_wrong": wrong,
        "test_weighted_covered": weighted_covered,
        "test_weighted_wrong": weighted_wrong,
        "test_weighted_abstention_cost": sum(
            consequence_weight(row.x) for row in test
        ) - weighted_covered,
        "stale_contract_status": stale_probe["status"],
        "no_automatic_admission": True,
        "external_actions": 0
    }


def summarize(rows):
    eligible = [row for row in rows if row["independent_review"]["status"]
                .startswith("ELIGIBLE")]
    return {
        "worlds": len(rows),
        "review_eligible": len(eligible),
        "held": len(rows) - len(eligible),
        "questions_issued": sum(row["source_questions_proposed"] for row in rows),
        "inquiry_cost": sum(row["source_question_cost"] for row in rows),
        "test_covered": sum(row["test_covered"] for row in rows),
        "test_wrong": sum(row["test_wrong"] for row in rows),
        "test_weighted_covered": sum(
            row["test_weighted_covered"] for row in rows),
        "weighted_cost_of_abstention": sum(
            row["test_weighted_abstention_cost"] for row in rows),
        "mean_lookup_cells_per_world": round(
            sum(row["exact_lookup_cells"] for row in rows) / len(rows), 3)
    }


def benchmark():
    development = [World(f, seed) for f in FAMILIES for seed in (0, 1)]
    evaluation = [World(f, seed) for f in FAMILIES for seed in (2, 3, 4, 5, 6)]
    dev = {method: summarize([trial(w, method) for w in development])
           for method in METHODS}
    # Freeze judgment based ONLY on development outcomes. The query policy
    # requires a meaningful source-risk-weighted improvement over a strong
    # classical active version-space learner, not just the fixed baseline.
    a, b = dev["motif_consequence"], dev["classical_entropy"]
    gain = a["test_weighted_covered"] - b["test_weighted_covered"]
    promote = (
        a["review_eligible"] >= b["review_eligible"] and
        a["test_wrong"] <= b["test_wrong"] and
        a["inquiry_cost"] <= b["inquiry_cost"] and
        gain >= max(32, b["test_weighted_covered"] // 10)
    )
    return {
        "schema": "motif.law-forge.unknown-world-benchmark.v1",
        "frozen_development_policy": {
            "promotion_requires": ">=10_percent_weighted_coverage_gain_vs_entropy_with_no_worse_review_error_or_cost_and_at_least_32_units",
            "maximum_synthetic_query_cost": MAX_QUERIES,
            "minimum_independent_review_covered": 16,
            "all_question_actions": "SYNTHETIC_OWNER_ONLY",
            "no_automatic_promotion": True
        },
        "development": dev,
        "frozen_method_decision": (
            "PROPOSE_FOR_HUMAN_REVIEW_ONLY" if promote
            else "NO_METHOD_PROMOTION"),
        "evaluation": {
            method: summarize([trial(w, method) for w in evaluation])
            for method in METHODS
        },
        "representative": {
            f: trial(World(f, 3), "motif_consequence") for f in (
                "pair_xor", "triple_and", "triple_majority",
                "twelve_parity", "phase_shift", "hidden_context")
        },
        "nonclaims": [
            "a general-purpose newly invented active-learning algorithm",
            "probabilistic calibration or physical-world correctness",
            "out-of-family generalization or independent new-world science",
            "risk values inferred from source outcome rather than declared tags",
            "native integration into ALEX, GRAFT, Dogram or Question Machine",
            "unrestricted live query execution, source authentication or consent",
            "theoretical savings beyond this restricted simulated source"
        ],
        "external_actions": 0,
        "automatic_method_promotion": False,
        "real_world_authority": False
    }


if __name__ == "__main__":
    print(json.dumps(benchmark(), indent=2, sort_keys=True))
