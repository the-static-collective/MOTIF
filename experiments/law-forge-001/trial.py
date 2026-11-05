"""Reproducible bounded trial + matched fixed classical diagnostic control.

Evaluator owns the hidden oracle; scientist in forge.py sees only observations.
No real-world commands, API requests, dynamic code execution or permissions.
"""
from __future__ import annotations

import json
from forge import (Probe, hypotheses, choose, propose, independent_review,
                   synthesis_record)
from oracle import World, FAMILIES

FIXED_DIAGNOSTICS = (
    Probe(((0, 1),), (1, 1)),
    Probe(((1, 0),), (1, 1)),
)


def run_trial(world: World, method: str = "adaptive", budget: int = 2):
    if method not in ("adaptive", "fixed"):
        raise ValueError("Unknown predeclared inquiry method")
    if type(budget) is not int or not (0 <= budget <= 2):
        raise ValueError("Finite two-probe budget only")
    training = world.initial_observations()
    evidence = list(training)
    probes = []
    for _ in range(budget):
        models = hypotheses(evidence)
        if choose(models) is not None or len(models) < 2:
            break
        if method == "adaptive":
            packet = propose(models, evidence, budget - len(probes))
        else:
            packet = next((p for p in FIXED_DIAGNOSTICS
                           if p not in {r.probe for r in evidence}), None)
        if packet is None:
            break
        # Only the EVALUATOR, not the learner, dispatches this local simulation.
        evidence.append(world.measure(Probe.from_packet(packet.packet())))
        probes.append(packet)
    models = hypotheses(evidence)
    selected = choose(models)
    reviewed = independent_review(selected, world.partition("review"))
    eligible = reviewed["status"] == "ELIGIBLE_PREDICT_ONLY_PENDING_HUMAN_REVIEW"
    test = world.partition("test")  # never fed into inquiry, fitting, or review
    correct = (sum(selected.predict(o.probe) == o.outcome for o in test)
               if eligible else 0)
    coverage = len(test) if eligible else 0
    # A separate renamed world is not admitted by possession of a cartridge.
    transfer = None
    if eligible:
        destination = World(world.family, world.seed + 101,
                            port_names=("unnamed_input_17", "unnamed_input_29"))
        transfer = independent_review(selected, destination.partition("transfer"))
    return {
        "family": world.family,  # evaluator-only score label
        "seed": world.seed,
        "method": method,
        "budget": budget,
        "inquiries_used": len(probes),
        "remaining_hypotheses": len(models),
        "review": reviewed,
        "test_covered": coverage,
        "test_correct": correct,
        "test_incorrect": coverage - correct,
        "transfer": transfer,
        "receipt": synthesis_record(training, probes, selected, reviewed)
    }


def negative_transfer():
    """Passing a source review never waives destination-world validation."""
    from forge import fit
    source = World("edge_first", 2)
    learned = run_trial(source)
    # Reconstruct strictly from the same *observable* source experiment,
    # without consulting world family as a model input.
    data = list(source.initial_observations())
    for packet in learned["receipt"]["probe_packets"]:
        data.append(source.measure(Probe.from_packet(packet)))
    candidate = choose(hypotheses(data))
    return {
        "matching_new_world": independent_review(
            candidate, World("edge_first", 900).partition("transfer")),
        "changed_hidden_rule": independent_review(
            candidate, World("edge_second", 900).partition("transfer")),
    }


def benchmark():
    # Development worlds and final-test worlds are disjoint by seed.
    development = [World(f, s) for f in FAMILIES for s in (0, 1, 2)]
    evaluation = [World(f, s) for f in FAMILIES for s in (3, 4, 5, 6, 7)]
    dev = {m: [run_trial(w, m) for w in development]
           for m in ("adaptive", "fixed")}
    # Predeclared cautious rule: method promotion requires >=2 more
    # independently admitted correct worlds without extra wrong predictions.
    def score(trials):
        return {
            "worlds": len(trials),
            "review_eligible": sum(
                t["review"]["status"].startswith("ELIGIBLE") for t in trials),
            "held": sum(
                not t["review"]["status"].startswith("ELIGIBLE") for t in trials),
            "test_covered": sum(t["test_covered"] for t in trials),
            "test_incorrect": sum(t["test_incorrect"] for t in trials),
            "probes_used": sum(t["inquiries_used"] for t in trials)
        }
    a = score(dev["adaptive"])
    f = score(dev["fixed"])
    improve = a["review_eligible"] >= f["review_eligible"] + 2 and (
        a["test_incorrect"] <= f["test_incorrect"])
    method_decision = "PROPOSE_ADAPTIVE_FOR_REVIEW" if improve else (
        "NO_METHOD_PROMOTION")
    result = {
        "schema": "motif.law-forge.benchmark.v1",
        "scope": "synthetic_finite_7_family_generator",
        "development": {m: score(rows) for m, rows in dev.items()},
        "frozen_method_decision": method_decision,
        "evaluation": {m: score([run_trial(w, m) for w in evaluation])
                       for m in ("adaptive", "fixed")},
        "negative_transfer": negative_transfer(),
        "sample_experiment": run_trial(World("edge_first", 3)),
        "sample_refusal": run_trial(World("latent_shift", 3)),
        "not_demonstrated": [
            "unrestricted new vocabulary invention",
            "real-world causal-law discovery",
            "GRAFT integration or external instrument construction",
            "autonomous method promotion or execution",
            "performance advantage over a fixed classical diagnostic"
        ],
        "external_calls": 0,
        "real_world_authority": False
    }
    return result


if __name__ == "__main__":
    print(json.dumps(benchmark(), indent=2, sort_keys=True))
