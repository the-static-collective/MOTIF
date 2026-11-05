"""LAW-FORGE-006: independent source-owner experiment and classical controls.

The learner sees only six low-level READ_LINK bits per approved experiment
and one simulator-provided outcome. Source owner generates questions and
reviews; it never grants a real-world action or project admission.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
from math import log2

from inventor import (
    Instrument, Proposal, Witness, evidence_digest, fit_old_four_edge,
    fit_full_raw, query_missing, review, synthesize
)
from owner import World, FAMILIES, owner_contract


METHODS = ("inventor", "old_four_link", "full_six_link")


@dataclass(frozen=True)
class Classical:
    method: str
    mapping: tuple[tuple[tuple[int, ...], int], ...]

    def predict(self, inputs):
        key = inputs[:4] if self.method == "old_four_link" else inputs
        return next((v for k, v in self.mapping if k == key), None)


def inspect_source(world: World, method="inventor", budget=32):
    if method not in METHODS:
        raise ValueError("Predeclared methods only")
    if type(budget) is not int or not 0 <= budget <= 32:
        raise ValueError("Bounded source probe budget 0..32 only")
    natural = world.initial()
    # The old source has only four edge channels, but no prebuilt derived
    # sensors are available to any method. All methods get equal evidence.
    queries = query_missing(natural, budget)
    if len(queries) != 32:
        return None, (), natural, "HOLD_PROBE_BUDGET"
    measured = world.execute(queries)
    evidence = natural + measured
    if method == "inventor":
        candidate = synthesize(evidence)
        status = ("PROPOSE_DERIVED_SENSOR" if candidate else
                  "HOLD_NO_ALLOWED_COMPOSITION")
    else:
        mapping = (fit_old_four_edge(evidence)
                   if method == "old_four_link" else fit_full_raw(evidence))
        candidate = (Classical(method, tuple(sorted(mapping.items())))
                     if mapping is not None else None)
        status = ("CLASSICAL_MODEL_PROPOSED" if candidate else
                  "HOLD_ORIGINAL_OBSERVATION_LANGUAGE")
    return candidate, queries, evidence, status


def gate(candidate, rows):
    """Same independent evaluator review for every method."""
    if candidate is None:
        return {"status": "HOLD_NO_SUPPORTED_MODEL", "contradictions": None}
    if isinstance(candidate, Proposal):
        return review(candidate, rows)
    if len(rows) < 64 or len({r.inputs for r in rows}) != 64:
        return {"status": "HOLD_REVIEW_COVERAGE", "contradictions": None}
    wrong = sum(candidate.predict(x.inputs) != x.result for x in rows)
    return {"status": ("ELIGIBLE_PREDICT_ONLY_PENDING_HUMAN_REVIEW"
                       if wrong == 0 else "HOLD_INDEPENDENT_FALSIFIER"),
            "contradictions": wrong}


def trial(world: World, method="inventor", budget=32):
    model, requests, evidence, status = inspect_source(world, method, budget)
    verified = gate(model, world.independent("review"))
    admitted_for_testing = verified["status"].startswith("ELIGIBLE")
    withheld = world.independent("test")
    score = sum(model.sensor.predict(x.inputs) == x.result
                if isinstance(model, Proposal) else
                model.predict(x.inputs) == x.result
                for x in withheld) if admitted_for_testing else 0
    transfer = None
    source_gate = None
    if admitted_for_testing:
        recipient = World(world.family, world.seed + 101,
                          role_names=("origin", "relay_a", "relay_b",
                                      "relay_c", "terminal"))
        transfer = gate(model, recipient.independent("transfer"))
        if isinstance(model, Proposal):
            source_gate = recipient.conformance(model.packet(), "transfer")
    else:
        if isinstance(model, Proposal):
            source_gate = world.conformance(model.packet(), "review")
    instrument = model.sensor if isinstance(model, Proposal) else None
    return {
        "world_family": world.family,  # evaluator-only scoring metadata
        "seed": world.seed,
        "method": method,
        "selection": status,
        "synthetic_graph_queries": len(requests),
        "source_observations": len(evidence),
        "source_evidence_digest": evidence_digest(evidence),
        "derived_instrument": model.packet() if isinstance(model, Proposal) else None,
        "derived_sensor_clauses": (instrument.program()["clauses"]
                                   if instrument else None),
        "required_source_links": (list(instrument.referenced_links)
                                   if instrument else None),
        "review": verified,
        "withheld_total": len(withheld),
        "withheld_covered": len(withheld) if admitted_for_testing else 0,
        "withheld_correct": score,
        "withheld_wrong": len(withheld) - score if admitted_for_testing else 0,
        "new_destination_review": transfer,
        "owner_compiler_review": source_gate,
        "authority": "SYNTHETIC_PREDICTION_ONLY",
        "automatic_source_integration": False,
        "external_actions": 0
    }


def negative_transfer():
    model, _, _, _ = inspect_source(World("any_three_paths", 0))
    if not isinstance(model, Proposal):
        raise AssertionError("The source model was not synthesized")
    return {
        "matching_renamed_source": World("any_three_paths", 100).conformance(
            model.packet(), "transfer"),
        "changed_rule": World("first_two_paths", 100).conformance(
            model.packet(), "transfer"),
        "unmeasured_hidden_context": World("hidden_context", 100).conformance(
            model.packet(), "transfer")
    }


def summary(rows):
    good = [r for r in rows if r["review"]["status"].startswith("ELIGIBLE")]
    return {
        "worlds": len(rows),
        "review_eligible": len(good),
        "held": len(rows) - len(good),
        "program_proposals": sum(r["derived_instrument"] is not None for r in rows),
        "source_queries": sum(r["synthetic_graph_queries"] for r in rows),
        "withheld_covered": sum(r["withheld_covered"] for r in rows),
        "withheld_wrong": sum(r["withheld_wrong"] for r in rows),
        "mean_source_link_reads_per_eligible_instrument": (
            round(sum(len(r["required_source_links"] or ()) for r in good) /
                  len(good), 4) if good and all(
                      r["required_source_links"] is not None for r in good
                  ) else None)
    }


def benchmark():
    developmental = [World(f, seed) for f in FAMILIES for seed in (0, 1)]
    final = [World(f, seed) for f in FAMILIES for seed in (2, 3, 4, 5, 6)]
    dev = {m: summary([trial(world, m) for world in developmental])
           for m in METHODS}
    outputs = {m: summary([trial(world, m) for world in final])
               for m in METHODS}
    # The raw six-link table is the complete-input upper-bound comparator.
    # Rule says NO new algorithm promotion when it doesn't beat raw accuracy.
    promote_method = (dev["inventor"]["review_eligible"] >=
                      dev["full_six_link"]["review_eligible"] + 2 and
                      dev["inventor"]["withheld_wrong"] <=
                      dev["full_six_link"]["withheld_wrong"])
    return {
        "schema": "motif.law-forge.instrument-invention-trial.v1",
        "source_capability_contract": owner_contract(),
        "development": dev,
        "final_evaluation": outputs,
        "frozen_method_decision": (
            "PROPOSE_METHOD_FOR_HUMAN_REVIEW" if promote_method
            else "NO_METHOD_PROMOTION"),
        "demonstrations": {f: trial(World(f, 3)) for f in (
            "any_three_paths", "last_path", "first_path",
            "at_least_two_paths", "phase_shift", "hidden_context")},
        "counterfactual_source_compilation": negative_transfer(),
        "unproven": [
            "unrestricted autonomous instrument invention",
            "unknown graph topologies or arbitrary graph arity",
            "advantages over the complete raw six-link truth table",
            "native ALEX persistence or GRAFT admission",
            "physical probe access, true energy costs or real-world causality"
        ],
        "external_actions": 0,
        "automatic_integration": False
    }


if __name__ == "__main__":
    print(json.dumps(benchmark(), indent=2, sort_keys=True))
