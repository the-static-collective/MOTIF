"""Frozen evaluator protocol for compositional constructor discovery.

No exploratory test labels ever enter model fitting. Matched fixed inquiry,
old-grammar-only and adaptive policies share initial evidence and budgets.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "law-forge-001"))
from forge import Probe, hypotheses as original_hypotheses, choose as original_choose
from forge import independent_review as original_review

from constructor import (synthesize, distinct, query, review, ConstructorModel)
from unseen_world import World, FAMILIES


def select(world: World, method="adaptive", budget=1):
    if method not in ("old_only", "adaptive", "fixed"):
        raise ValueError("Unknown preregistered method")
    if type(budget) is not int or budget not in (0, 1):
        raise ValueError("Only zero or one local probe permitted")
    natural = world.initial_observations()
    incumbent = original_choose(original_hypotheses(natural))
    if incumbent is not None:
        return incumbent, (), "INCUMBENT_SUFFICIENT"
    if method == "old_only":
        return None, (), "HOLD_OLD_GRAMMAR_FAILED"

    inquiry = list(natural)
    probes = []
    for _ in range(budget):
        candidates = synthesize(inquiry)
        options = candidates["proposals"]
        candidate = distinct(options)
        if candidate is not None:
            return candidate, tuple(probes), "CONSTRUCTOR_IDENTIFIED"
        if len(options) < 2:
            return None, tuple(probes), "HOLD_NO_REPRESENTATION"
        if method == "adaptive":
            probe = query(options, inquiry, budget=budget - len(probes))
        else:
            # Strong classical fixed discriminator for OR versus XOR.
            probe = Probe(((1, 1),), (1, 1))
            if probe in {o.probe for o in inquiry}:
                probe = None
        if probe is None:
            return None, tuple(probes), "HOLD_UNIDENTIFIABLE"
        # Explicit evaluator execution. The learner only proposed a packet.
        checked = Probe.from_packet(probe.packet())
        inquiry.append(world.measure(checked))
        probes.append(checked)

    options = synthesize(inquiry)["proposals"]
    candidate = distinct(options)
    return candidate, tuple(probes), ("CONSTRUCTOR_IDENTIFIED" if candidate is not None
                                      else "HOLD_UNIDENTIFIABLE")


def trial(world: World, method="adaptive", budget=1):
    selected, probes, state = select(world, method, budget)
    is_composite = isinstance(selected, ConstructorModel)
    verifier = review if is_composite or selected is None else original_review
    checked = verifier(selected, world.partition("review"))
    passed = checked["status"].startswith("ELIGIBLE")
    withheld = world.partition("test")
    correct = (sum(selected.predict(r.probe) == r.outcome for r in withheld)
               if passed else 0)
    transfer_status = None
    if passed:
        # Names have no identity-transfer authority; destination rechecks.
        destination = World(world.family, seed=world.seed + 100,
                            renamed_ports=("port_red", "port_violet"))
        transfer_status = verifier(selected, destination.partition("transfer"))
    return {
        "family": world.family,  # evaluator-owned scoring metadata
        "seed": world.seed,
        "method": method, "state": state,
        "probes": [p.packet() for p in probes],
        "new_constructor": (selected.packet() if is_composite else None),
        "incumbent_kept": selected is not None and not is_composite,
        "review": checked,
        "test_covered": 16 if passed else 0,
        "test_correct": correct,
        "test_incorrect": 16 - correct if passed else 0,
        "transfer_review": transfer_status,
        "real_world_authority": False,
        "automatic_method_promotion": False
    }


def negative_transfer():
    # A candidate may transfer to renamed *equivalent* worlds, but cannot
    # authorize its own use in a world governed by a different mechanism.
    from_source, _, _ = select(World("xor_memory", 1))
    if not isinstance(from_source, ConstructorModel):
        raise AssertionError("Source did not produce typed constructor")
    return {
        "equivalent_world": review(
            from_source, World("xor_memory", 900).partition("transfer")),
        "changed_rule": review(
            from_source, World("or_memory", 900).partition("transfer"))
    }


def summarized(records):
    eligible = [r for r in records if r["review"]["status"].startswith("ELIGIBLE")]
    return {
        "worlds": len(records),
        "review_eligible": len(eligible),
        "held": len(records) - len(eligible),
        "new_constructors": sum(r["new_constructor"] is not None for r in records),
        "synthetic_probes": sum(len(r["probes"]) for r in records),
        "test_covered": sum(r["test_covered"] for r in records),
        "test_incorrect": sum(r["test_incorrect"] for r in records)
    }


def benchmark():
    precommitted_methods = ("old_only", "fixed", "adaptive")
    development = [World(f, s) for f in FAMILIES for s in (0, 1)]
    evaluation = [World(f, s) for f in FAMILIES for s in (2, 3, 4, 5, 6)]
    dev = {m: summarized([trial(w, m) for w in development])
           for m in precommitted_methods}
    # Do NOT promote on a tie with a good fixed classical diagnostic.
    promote = (dev["adaptive"]["review_eligible"] >=
               dev["fixed"]["review_eligible"] + 2
               and dev["adaptive"]["test_incorrect"] <=
               dev["fixed"]["test_incorrect"])
    return {
        "schema": "motif.law-forge.meta-constructor-trial.v1",
        "description": "finite hand-authored two-port synthetic worlds",
        "development": dev,
        "frozen_method_decision": ("PROPOSE_ADAPTIVE_FOR_HUMAN_REVIEW" if promote
                                   else "NO_METHOD_PROMOTION"),
        "evaluation": {
            m: summarized([trial(w, m) for w in evaluation])
            for m in precommitted_methods
        },
        "synthetic_xor_example": trial(World("xor_memory", 2)),
        "synthetic_or_example": trial(World("or_memory", 2)),
        "held_hidden_two_tick_example": trial(World("two_tick_hidden", 2)),
        "held_shift_example": trial(World("distribution_shift", 2)),
        "negative_transfer": negative_transfer(),
        "separate_approval_required": True,
        "external_operations": 0,
        "real_world_authority": False,
        "nonclaims": [
            "invention of a new Boolean primitive",
            "unbounded feature-program synthesis",
            "open-domain causal science",
            "general intelligence or consciousness",
            "automatic GRAFT compilation or self-editing",
            "advantage over the fixed classical inquiry method"
        ]
    }


if __name__ == "__main__":
    print(json.dumps(benchmark(), sort_keys=True, indent=2))
