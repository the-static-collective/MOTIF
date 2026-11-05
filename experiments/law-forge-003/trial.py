"""LAW-FORGE-003: separate evaluator loop + strong classical fold comparator.

The scientist in foundry.py never imports world.py or observes truth labels
other than requested, typed synthetic inquiry results. Review and test labels
are evaluator-owned partitions. Each method sees identical initial inputs.
"""
from __future__ import annotations
import json
from foundry import Operator, Query, possibilities, propose, review
from world import FAMILIES, World

METHODS = ("nand_adaptive", "nand_fixed", "table_fixed")


def identify(world, method="nand_adaptive", budget=1):
    if method not in METHODS:
        raise ValueError("Unknown frozen method")
    if type(budget) is not int or budget not in (0, 1):
        raise ValueError("At most one synthetic query")
    rows = list(world.initial_observations())
    algorithm = "classical" if method == "table_fixed" else "nand"
    candidates = possibilities(rows, algorithm)
    probes = []
    for _ in range(budget):
        if len(candidates) <= 1:
            break
        if method == "nand_adaptive":
            suggestion = propose(candidates, rows, remaining_cost=3)
        else:
            suggestion = Query((1, 1), 0.0, 3)
        if suggestion is None:
            break
        # The evaluator—not the model—authorizes one local oracle lookup.
        request = Query.from_packet(suggestion.packet())
        rows.append(world.measure(request.inputs, "inquiry"))
        probes.append(suggestion)
        candidates = possibilities(rows, algorithm)
    selected = candidates[0] if len(candidates) == 1 else None
    status = ("OPERATOR_PROPOSED" if selected is not None else
              "HOLD_UNIDENTIFIED_OPERATOR")
    return selected, tuple(probes), status


def trial(world, method="nand_adaptive", budget=1):
    selected, probes, status = identify(world, method, budget)
    reviewer = review(selected, world.partition("review"))
    eligible = reviewer["status"].startswith("ELIGIBLE")
    # No test labels used for selecting, changing or reviewing a circuit.
    unseen = world.partition("test")
    covered = len(unseen) if eligible else 0
    correct = (sum(selected.predict(case.inputs) == case.outcome for case in unseen)
               if eligible else 0)
    transfer = None
    if eligible:
        destination = World(world.family, world.seed + 100,
                            renamed_ports=("renamed_alpha", "renamed_beta"))
        transfer = review(selected, destination.partition("transfer"))
    return {
        "family": world.family,  # evaluator scoring metadata only
        "seed": world.seed,
        "method": method,
        "status": status,
        "probe_packets": [p.packet() for p in probes],
        "declared_probe_cost": sum(p.cost for p in probes),
        "source_operator_packet": selected.packet() if selected else None,
        "circuit_gates": (len(selected.circuit.gates)
                          if selected and selected.circuit else None),
        "review": reviewer,
        "test_cases_withheld": len(unseen),
        "test_covered": covered,
        "test_correct": correct,
        "test_incorrect": covered - correct,
        "transfer_review": transfer,
        "external_operations": 0,
        "automatic_admission": False
    }


def transfer_falsification():
    source, _, _ = identify(World("parity_fold", 2))
    assert isinstance(source, Operator) and source.circuit is not None
    return {
        "revalidated_equivalent": review(
            source, World("parity_fold", 100).partition("transfer")),
        "rejected_different_rule": review(
            source, World("any_on_fold", 100).partition("transfer"))
    }


def summary(rows):
    eligible = [r for r in rows if r["review"]["status"].startswith("ELIGIBLE")]
    return {
        "worlds": len(rows),
        "review_eligible": len(eligible),
        "held": len(rows) - len(eligible),
        "operator_proposals": sum(r["source_operator_packet"] is not None
                                  for r in rows),
        "local_synthetic_queries": sum(len(r["probe_packets"]) for r in rows),
        "query_cost_units": sum(r["declared_probe_cost"] for r in rows),
        "test_covered": sum(r["test_covered"] for r in rows),
        "test_incorrect": sum(r["test_incorrect"] for r in rows)
    }


def benchmark():
    # Mechanism families are authored by the evaluator; seed splits are
    # not independent problem domains. Development policy frozen below.
    dev_worlds = [World(f, s) for f in FAMILIES for s in (0, 1)]
    held_worlds = [World(f, s) for f in FAMILIES
                   for s in (2, 3, 4, 5, 6)]
    dev = {m: summary([trial(w, m) for w in dev_worlds]) for m in METHODS}
    # A tie with the stronger classical truth-table fold is not promotion.
    propose_new_method = (
        dev["nand_adaptive"]["review_eligible"] >=
        dev["table_fixed"]["review_eligible"] + 2 and
        dev["nand_adaptive"]["test_incorrect"] <=
        dev["table_fixed"]["test_incorrect"] and
        dev["nand_adaptive"]["query_cost_units"] <=
        dev["table_fixed"]["query_cost_units"])
    return {
        "schema": "motif.law-forge.operator-foundry-benchmark.v1",
        "scope": "finite_NAND_synthesis_and_handcrafted_synthetic_worlds",
        "development": dev,
        "frozen_method_decision": (
            "PROPOSE_NAND_METHOD_FOR_HUMAN_REVIEW" if propose_new_method
            else "NO_METHOD_PROMOTION"),
        "evaluation": {
            m: summary([trial(w, m) for w in held_worlds]) for m in METHODS
        },
        "xor_operator": trial(World("parity_fold", 2)),
        "or_operator": trial(World("any_on_fold", 2)),
        "and_operator": trial(World("all_on_fold", 2)),
        "hidden_width_refusal": trial(World("hidden_width", 2)),
        "phase_shift_refusal": trial(World("phase_shift", 2)),
        "negative_transfer": transfer_falsification(),
        "next_question": ("Can a frozen NAND-only operator language identify a "
                          "previously unseen, non-fold relational process without "
                          "silently expanding the evaluator's teaching grammar?"),
        "nonclaims": [
            "invention of NAND or XOR as new mathematical primitives",
            "unbounded programming-language synthesis",
            "general-domain scientific or causal discovery",
            "advantage over classical truth-table folding",
            "GRAFT integration, external probes or live self-modification"
        ],
        "external_operations": 0,
        "automatic_admission": False,
        "real_world_authority": False
    }


if __name__ == "__main__":
    print(json.dumps(benchmark(), indent=2, sort_keys=True))
