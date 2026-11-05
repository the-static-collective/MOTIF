"""LAW-FORGE-005 — controlled sensor-language comparison.

Trinary is a falsifiable instrument proposal, not a privileged ontology.
All methods receive the same common readout panel and outcome evidence.
That makes this a representation-selection experiment, NOT a real instrument
fabrication or computation/energy-cost benchmark.
"""
from __future__ import annotations

import json
from itertools import product
from instrument import (Sensor, SensorModel, discover, independent_review,
                        remaining_probes, score)
from world import FAMILIES, World

METHODS = ("all", "binary", "ternary", "full_raw")
CAPACITY_MODELS = ("symbolic_capacity", "binary_encoded")


def inquiry(world: World, method="all", capacity="symbolic_capacity", budget=8):
    if method not in METHODS or capacity not in CAPACITY_MODELS:
        raise ValueError("Predeclared sensor portfolio/capacity model required")
    if type(budget) is not int or budget < 0 or budget > 8:
        raise ValueError("Zero through eight synthetic graph queries")
    initial = world.initial()
    declared_controls = tuple((a, b, c, 0)
                              for a, b, c in product((0, 1), repeat=3))
    proposals = remaining_probes(declared_controls, budget)
    if len(proposals) != 8:
        return None, (), "HOLD_UNFUNDED_QUERY"
    # Only the evaluator possesses the program to execute these controls.
    measured = world.execute(proposals)
    candidate, status = discover(initial + measured, method, capacity)
    return candidate, proposals, status


def trial(world: World, method="all", capacity="symbolic_capacity", budget=8):
    candidate, proposals, state = inquiry(world, method, capacity, budget)
    reviewed = independent_review(candidate, world.partition("review"))
    eligible = reviewed["status"].startswith("ELIGIBLE")
    heldout = world.partition("test")
    correct = (sum(candidate.predict(row) == row.outcome for row in heldout)
               if eligible else 0)
    transfer = None
    if eligible:
        destination = World(world.family, world.seed + 100,
                            role_names=("origin17", "relay33", "relay56", "dest88"))
        transfer = independent_review(candidate, destination.partition("transfer"))
    choice = candidate.sensor if candidate is not None else None
    return {
        "family": world.family,  # evaluator metadata only
        "seed": world.seed,
        "method": method,
        "capacity": capacity,
        "status": state,
        "query_count": len(proposals),
        "sensor_program": choice.packet() if choice else None,
        "sensor_model": candidate.packet() if candidate else None,
        "sensor_source_reads": choice.source_reads if choice else None,
        "sensor_cardinality": choice.cardinality if choice else None,
        "symbolic_capacity_bits": (round(__import__("math").log2(choice.cardinality), 6)
                                   if choice else None),
        "declared_score": list(score(choice, capacity)) if choice else None,
        "review": reviewed,
        "heldout_covered": len(heldout) if eligible else 0,
        "heldout_correct": correct,
        "heldout_incorrect": (len(heldout) - correct) if eligible else 0,
        "destination_review": transfer,
        "external_actions": 0,
        "automatic_admission": False
    }


def counterfactual_transfer():
    source = World("any_route", 1)
    model, _, _ = inquiry(source)
    if model is None:
        raise AssertionError("Unable to construct the synthetic source sensor")
    return {
        "same_rule_renamed": independent_review(
            model, World("any_route", 100,
                         role_names=("n0", "n1", "n2", "n3")).partition("transfer")),
        "different_rule": independent_review(
            model, World("one_route", 100,
                         role_names=("n0", "n1", "n2", "n3")).partition("transfer"))
    }


def summarize(rows):
    admitted = [row for row in rows if row["review"]["status"].startswith("ELIGIBLE")]
    tri_selected = sum(row["sensor_program"] is not None and
                       row["sensor_program"]["operation"] in (
                           "COUNT2", "PATHCOUNT") for row in rows)
    return {
        "worlds": len(rows),
        "review_eligible": len(admitted),
        "held": len(rows) - len(admitted),
        "ternary_proposals": tri_selected,
        "membership_queries": sum(row["query_count"] for row in rows),
        "mean_source_reads_eligible": (
            round(sum(row["sensor_source_reads"] for row in admitted) /
                  len(admitted), 4) if admitted else None),
        "heldout_covered": sum(row["heldout_covered"] for row in rows),
        "heldout_incorrect": sum(row["heldout_incorrect"] for row in rows)
    }


def benchmark():
    development = [World(f, s) for f in FAMILIES for s in (0, 1)]
    evaluation = [World(f, s) for f in FAMILIES for s in (2, 3, 4, 5, 6)]
    dev = {m: summarize([trial(w, m) for w in development])
           for m in METHODS}
    final = {m: summarize([trial(w, m) for w in evaluation])
             for m in METHODS}
    # This is a user-supplied speculative thought. There is no reason to
    # privilege base-3 without a verified outcome benefit over binary.
    tri_wins = (dev["ternary"]["review_eligible"] >=
                dev["binary"]["review_eligible"] + 2
                and dev["ternary"]["heldout_incorrect"] <=
                dev["binary"]["heldout_incorrect"])
    return {
        "schema": "motif.law-forge.world-breaker.v1",
        "research_question": ("Does a proposed ternary categorical readout "
                              "ever justify itself against equally observable "
                              "binary and relational representations?"),
        "seven_four_edge_graphs_positive": 8,
        "world_families": len(FAMILIES),
        "development": dev,
        "frozen_trinary_promotion": ("PROPOSE_FOR_REVIEW" if tri_wins
                                     else "NO_TERNARY_PRIVILEGE"),
        "evaluation": final,
        "binary_encoding_ablation": summarize(
            [trial(w, "all", "binary_encoded") for w in evaluation]),
        "counterfactual_transfer": counterfactual_transfer(),
        "examples": {
            f: trial(World(f, 2)) for f in (
                "first_edge", "one_neighbor", "first_neighbor_only",
                "any_route", "one_route", "two_routes", "first_route_only",
                "edge_parity", "phase_shift", "unseen_context")
        },
        "limitations": [
            "Ternary is a speculative human hypothesis and only a finite coding option",
            "All candidate readouts are predeclared and exposed in a common panel",
            "No live physical instrument or arbitrary new ontology was invented",
            "Abstract capacity differs from real storage, power and measurement costs",
            "No improvement over complete binary/raw graph evidence is implied",
            "World families and synthetic source are researcher-authored",
            "Source checksum is not source authentication or execution permission"
        ],
        "external_actions": 0,
        "real_world_authority": False
    }


if __name__ == "__main__":
    print(json.dumps(benchmark(), indent=2, sort_keys=True))
