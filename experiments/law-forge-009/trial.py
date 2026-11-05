"""LAW-FORGE-009 — Stranger challenge, preregistered classical comparison.

The classical entropy cartridge is executable and portable, but does not get
to win by decree. It competes with the inherited Gini/disagreement selector
from LAW-FORGE-008, fixed-order queries, a CART-like classifier, and exact
lookup. Equal query budgets, initial witnesses, catalog, independent review
and heldout tests. Model selection is frozen on development seeds only.
"""
from __future__ import annotations

import json

from entropy_cartridge import EntropyCartridge
from gap import diagnose, independent_core_check
from stranger_owner import FAMILIES, Stranger
from learner import (
    MAX_QUERIES, make_desk, choose_question, Question, review,
    consequence_weight
)

METHODS = ("shannon_entropy_cartridge", "classical_gini_008",
           "fixed_catalog", "classical_tree", "lookup_only")


def inquire(source, method="shannon_entropy_cartridge", budget=MAX_QUERIES):
    if method not in METHODS:
        raise ValueError("Only preregistered inquiry strategies")
    if type(budget) is not int or not 0 <= budget <= MAX_QUERIES:
        raise ValueError("Only nonnegative bounded source-owned inquiry")
    evidence = list(source.initial())
    owner_catalog = source.catalog()
    spent = 0
    issued = []
    cartridge = EntropyCartridge(source.contract, tuple(evidence))
    while spent < budget:
        remaining = budget - spent
        if method == "shannon_entropy_cartridge":
            proposal = cartridge.propose(owner_catalog, remaining)
            card = proposal.card if proposal else None
        else:
            strategy = ("classical_entropy"
                        if method == "classical_gini_008" else "classical_fixed")
            card = choose_question(
                ((w.x, w.y) for w in evidence),
                owner_catalog, strategy, remaining, tuple(q.x for q in issued)
            )
        if card is None:
            break
        checked = Question.from_packet(card.packet())
        answer = source.execute(checked)
        if method == "shannon_entropy_cartridge":
            cartridge = cartridge.ingest(proposal, answer, owner_catalog)
        evidence.append(answer)
        spent += card.unit_cost
        issued.append(card)
    pred_method = ("classical_tree" if method == "classical_tree"
                   else "lookup_only" if method == "lookup_only"
                   else "classical_entropy")
    frozen = make_desk(source.contract, tuple(evidence), pred_method)
    return frozen, cartridge, tuple(issued), spent


def trial(source, method="shannon_entropy_cartridge", budget=MAX_QUERIES):
    model, entropy_cartridge, questions, cost = inquire(source, method, budget)
    review_rows = source.independent("review")
    reviewed = review(model, source.contract, review_rows)
    eligible = reviewed["status"].startswith("ELIGIBLE")
    tested = source.independent("test")
    covered = errors = weighted = 0
    if eligible:
        for row in tested:
            response = model.predict(row.x, source.contract)
            if response["value"] is None:
                continue
            covered += 1
            weighted += consequence_weight(row.x)
            errors += response["value"] != row.y
    # Diagnoses derive solely from the *training* witnesses in the frozen
    # classical entropy cartridge, not reviewer labels or hidden rules.
    gap = diagnose(entropy_cartridge) if method == "shannon_entropy_cartridge" else None
    changed = source.matching_new_epoch().contract
    old = entropy_cartridge.predict(tuple([0]*12), changed)
    return {
        "family": source.family,  # evaluator-only scoring metadata
        "seed": source.seed,
        "method": method,
        "source_contract": source.contract.packet(),
        "initial_observations": len(source.initial()),
        "catalog_size": len(source.catalog()),
        "question_count": len(questions),
        "membership_cost": cost,
        "source_snapshot_cells": len(model.snapshot),
        "surviving_hypotheses": len(entropy_cartridge.survivor_indices)
        if method == "shannon_entropy_cartridge" else len(model.candidates),
        "review": reviewed,
        "heldout_total": len(tested),
        "heldout_covered": covered,
        "heldout_errors": errors,
        "heldout_weighted_covered": weighted,
        "grammar_gap": gap.packet() if gap else None,
        "grammar_gap_independently_checkable": (
            independent_core_check(entropy_cartridge, gap) if gap else None),
        "cartridge": entropy_cartridge.packet()
        if method == "shannon_entropy_cartridge" else None,
        "stale_contract_status": old["status"],
        "real_world_authority": False,
        "automatic_promotion": False
    }


def summarize(rows):
    eligible = [r for r in rows if r["review"]["status"].startswith("ELIGIBLE")]
    return {
        "worlds": len(rows),
        "review_eligible": len(eligible),
        "held": len(rows) - len(eligible),
        "source_query_count": sum(r["question_count"] for r in rows),
        "source_query_cost": sum(r["membership_cost"] for r in rows),
        "heldout_covered": sum(r["heldout_covered"] for r in rows),
        "heldout_errors": sum(r["heldout_errors"] for r in rows),
        "declared_weighted_covered": sum(
            r["heldout_weighted_covered"] for r in rows),
        "training_detected_grammar_gaps": sum(
            r["grammar_gap"] is not None for r in rows),
        "mean_witness_cells": round(
            sum(r["source_snapshot_cells"] for r in rows) / len(rows), 3)
    }


def benchmark():
    development = [Stranger(f, seed) for f in FAMILIES for seed in (0, 1)]
    evaluation = [Stranger(f, seed) for f in FAMILIES
                  for seed in (2, 3, 4, 5, 6)]
    dev = {name: summarize([trial(w, name) for w in development])
           for name in METHODS}
    a, b = dev["shannon_entropy_cartridge"], dev["classical_gini_008"]
    propose = (a["review_eligible"] >= b["review_eligible"] and
               a["heldout_errors"] <= b["heldout_errors"] and
               a["source_query_cost"] < b["source_query_cost"] and
               a["heldout_covered"] >= b["heldout_covered"])
    return {
        "schema": "motif.law-forge.stranger-entropy-benchmark.v1",
        "domain_size": 4096,
        "source_owned_query_budget": MAX_QUERIES,
        "rule_library_size": 650,
        "source_is_separately_packaged_not_independently_authored": True,
        "development": dev,
        "frozen_selection": "PROPOSE_FOR_HUMAN_REVIEW" if propose
        else "NO_METHOD_PROMOTION",
        "evaluation": {name: summarize([trial(w, name) for w in evaluation])
                       for name in METHODS},
        "examples": {family: trial(Stranger(family, 3))
                     for family in (
                         "two_bit_xor", "conditional_mux",
                         "four_bit_parity", "four_way_conjunction",
                         "drifting_pair_xor", "hidden_exception")},
        "nonclaims": [
            "new active learning mathematics",
            "uniform hypothesis prior represents real-world probability",
            "independently authored physical or historical source",
            "out-of-grammar truth recovered without source review",
            "unrestricted new language or hardware adapter invention",
            "native ALEX/GRAFT/Dogram/Question Machine runtime integration",
            "true physical cost or Bayesian calibration"
        ],
        "external_actions": 0,
        "real_world_authority": False,
        "automatic_promotion": False
    }


if __name__ == "__main__":
    print(json.dumps(benchmark(), indent=2, sort_keys=True))
