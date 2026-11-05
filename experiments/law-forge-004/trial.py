"""Evaluator for LAW-FORGE-004, with independently separated review/test labels.

The research engine only receives typed observations and proposes a batch.
This evaluator alone executes local synthetic membership queries. No agent,
external API, source edit, credential, or real-world side effect is authorized.
"""
from __future__ import annotations

import json
from machine import (FoldModel, StateProgram, evidence_id, evidence_table,
                     fold_candidates, infer, independent_review,
                     missing_queries)
from world import FAMILIES, World

METHODS = ("scalar_only", "stateful_upgrade", "classical_gated",
           "classical_full")


def learn(world: World, method="stateful_upgrade", budget=224):
    if method not in METHODS:
        raise ValueError("Only predeclared research methods")
    if type(budget) is not int or budget < 0 or budget > 224:
        raise ValueError("Synthetic membership budget capped at 224")
    initial = world.base()
    scalar = fold_candidates(initial)
    if method != "classical_full" and len(scalar) == 1:
        return scalar[0], (), "RETAIN_SINGLE_BIT_FOLD", "FOLD"
    if method == "scalar_only":
        return None, (), "HOLD_SCALAR_GRAMMAR_INADEQUATE", "NONE"
    proposal = missing_queries(initial)
    if proposal.cost > budget:
        return None, (), "HOLD_MEMBERSHIP_BUDGET", "NONE"
    # A full bounded membership protocol, not adaptive one-query optimality.
    # The evaluator is the only actor able to answer its requested samples.
    actual = world.execute_batch(proposal)
    decision = infer(initial + actual)
    if decision.machine is None:
        return None, (proposal,), decision.status, "NONE"
    return decision.machine, (proposal,), decision.status, "STATE_MACHINE"


def trial(world: World, method="stateful_upgrade", budget=224):
    candidate, batches, state, kind = learn(world, method, budget)
    review_rows = world.partition("review")
    decision = independent_review(candidate, review_rows)
    eligible = decision["status"].startswith("ELIGIBLE")
    # Separate withheld test, never consulted while fitting or reviewing.
    unseen = world.partition("test")
    covered = len(unseen) if eligible else 0
    correct = (sum(candidate.predict(row.word) == row.result
                   for row in unseen) if eligible else 0)
    transfer = None
    if eligible:
        destination = World(world.family, world.seed + 101,
                            opaque_input="renamed_port_17")
        transfer = independent_review(candidate, destination.partition("transfer"))
    return {
        "family": world.family,  # evaluator scoring metadata only
        "seed": world.seed,
        "method": method,
        "status": state,
        "representation": kind,
        "states_inferred": candidate.state_count if isinstance(candidate, StateProgram) else (
            1 if isinstance(candidate, FoldModel) else 0),
        "stateful_operator_packet": (candidate.packet()
                                      if isinstance(candidate, StateProgram) else None),
        "requested_synthetic_batches": [b.packet() for b in batches],
        "total_synthetic_queries": 31 + sum(b.cost for b in batches),
        "review": decision,
        "heldout_total": len(unseen),
        "heldout_covered": covered,
        "heldout_correct": correct,
        "heldout_incorrect": covered - correct,
        "destination_review": transfer,
        "external_operations": 0,
        "automatic_admission": False,
        "real_world_authority": False
    }


def negative_transfer():
    from_source, _, _, _ = learn(World("ends_01", 0))
    assert isinstance(from_source, StateProgram)
    return {
        "same_machine_new_identity": independent_review(
            from_source, World("ends_01", 100, opaque_input="renamed")
            .partition("transfer")),
        "different_hidden_machine": independent_review(
            from_source, World("ends_001", 100, opaque_input="renamed")
            .partition("transfer")),
        "nonstationary_destination": independent_review(
            from_source, World("phase_shift", 100).partition("transfer"))
    }


def aggregate(rows):
    eligible = [x for x in rows if x["review"]["status"].startswith("ELIGIBLE")]
    return {
        "worlds": len(rows),
        "review_eligible": len(eligible),
        "held": len(rows) - len(eligible),
        "new_stateful_operator_proposals": sum(
            x["stateful_operator_packet"] is not None for x in rows),
        "membership_queries": sum(x["total_synthetic_queries"] for x in rows),
        "heldout_covered": sum(x["heldout_covered"] for x in rows),
        "heldout_incorrect": sum(x["heldout_incorrect"] for x in rows)
    }


def benchmark():
    # Seeds vary independent review/test sequence generation; all family
    # mechanisms are hand-authored, not independent external domains.
    dev = [World(f, s) for f in FAMILIES for s in (0, 1)]
    evaluation = [World(f, s) for f in FAMILIES for s in (2, 3, 4, 5, 6)]
    development_results = {
        m: aggregate([trial(w, m) for w in dev]) for m in METHODS
    }
    # Strong classical gated comparator shares the efficient change-of-grammar
    # protocol; report a tie rather than relabeling generic inference as novelty.
    a = development_results["stateful_upgrade"]
    b = development_results["classical_gated"]
    promote = (a["review_eligible"] >= b["review_eligible"] + 2
               and a["heldout_incorrect"] <= b["heldout_incorrect"]
               and a["membership_queries"] <= b["membership_queries"])
    return {
        "schema": "motif.law-forge.grammar-breaker-benchmark.v1",
        "synthetic_membership_horizon": 7,
        "maximum_inferred_states": 4,
        "development": development_results,
        "frozen_method_decision": (
            "PROPOSE_PROTOCOL_FOR_HUMAN_REVIEW" if promote
            else "NO_METHOD_PROMOTION"),
        "evaluation": {
            m: aggregate([trial(w, m) for w in evaluation]) for m in METHODS
        },
        "example_two_state_parity": trial(World("parity", 2)),
        "example_three_state_history": trial(World("ends_01", 2)),
        "example_four_state_history": trial(World("ends_001", 2)),
        "example_four_state_pattern": trial(World("contains_101", 2)),
        "refused_five_state_world": trial(World("ends_0001", 2)),
        "refused_nonstationary_world": trial(World("phase_shift", 2)),
        "negative_transfer": negative_transfer(),
        "nonclaims": [
            "unrestricted invention of computational primitives",
            "out-of-family scientific generalization",
            "superiority over classical finite-state inference",
            "real-world causal discovery",
            "GRAFT adapter construction or live autonomous code execution",
            "independently authenticated evidence or authority"
        ],
        "external_operations": 0,
        "automatic_admission": False,
        "real_world_authority": False
    }


if __name__ == "__main__":
    print(json.dumps(benchmark(), sort_keys=True, indent=2))
