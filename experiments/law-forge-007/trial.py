"""LAW-FORGE-007 predeclared controls: raw classical lookup is first-class.

The hybrid *never* asserts better coverage than a complete classical table.
Its only additional value is a checked compact description where possible,
safe exception routing, strict source revision binding, and explicit HOLD.
"""
from __future__ import annotations

import json
from dataclasses import dataclass

from lookup import (Contract, LookupSkill, assimilate, compact_cost,
                    independent_review, normalized, snapshot_id)
from source import FAMILIES, Source

METHODS = ("assimilated_hybrid", "classical_full_lookup",
           "old_four_channel_only", "partial_unobserved")


@dataclass(frozen=True)
class OldProjection:
    contract: Contract
    mapping: tuple[tuple[tuple[int, ...], int], ...]

    def predict(self, inputs, contract):
        if contract.id != self.contract.id:
            return {"status": "HOLD_SOURCE_CONTRACT_CHANGED", "value": None}
        x = tuple(inputs[:4])
        return {"status": "SUPPORTED_SYNTHETIC_SNAPSHOT",
                "value": dict(self.mapping).get(x)}


def old_four(rows, contract):
    observed = normalized(contract, rows)
    table = {}
    for x, y in observed:
        key = x[:4]
        if key in table and table[key] != y:
            return None
        table[key] = y
    return OldProjection(contract, tuple(sorted(table.items())))


def make_model(source, method):
    if method not in METHODS:
        raise ValueError("Predeclared lookup skill/competitor required")
    contract = source.contract()
    if method == "partial_unobserved":
        rows = source.observations(partial=True)
    else:
        rows = source.observations()
    if method == "old_four_channel_only":
        return old_four(rows, contract), len(rows)
    if method == "classical_full_lookup":
        canonical = normalized(contract, rows)
        return LookupSkill(contract, canonical,
                           snapshot_id(contract, canonical)), len(rows)
    return assimilate(contract, rows), len(rows)


def review_model(model, contract, evidence):
    if model is None:
        return {"status": "HOLD_INADEQUATE_OLD_INTERFACE",
                "contradictions": None}
    if isinstance(model, LookupSkill):
        return independent_review(model, contract, evidence)
    known = tuple(evidence)
    if len({r.vector for r in known}) != 2 ** contract.width:
        return {"status": "HOLD_REVIEW_COVERAGE", "contradictions": None}
    contradictions = sum(model.predict(r.vector, contract)["value"] != r.outcome
                         for r in known)
    return {"status": ("ELIGIBLE_PREDICT_ONLY_PENDING_HUMAN_REVIEW"
                       if contradictions == 0 else "HOLD_INDEPENDENT_FALSIFIER"),
            "contradictions": contradictions}


def trial(source: Source, method="assimilated_hybrid"):
    model, cost = make_model(source, method)
    contract = source.contract()
    decision = review_model(model, contract, source.observations("review"))
    eligible = decision["status"].startswith("ELIGIBLE")
    withheld = source.observations("test")
    correct = sum(model.predict(r.vector, contract)["value"] == r.outcome
                  for r in withheld) if eligible else 0
    destination = None
    if eligible:
        dest = source.destination()
        destination = review_model(model, dest.contract(),
                                   dest.observations("transfer"))
    program_cost = None
    raw_cost = contract.width * (2 ** contract.width) + 2 ** contract.width
    if isinstance(model, LookupSkill):
        program_cost = (compact_cost(model.program, len(model.corrections))
                        if model.program else raw_cost)
    return {
        "family": source.hidden_family,  # evaluator metadata only
        "seed": source.seed, "method": method,
        "channels": contract.width,
        "model_status": ("HOLD_NO_MODEL" if model is None else
                         model.representation if isinstance(model, LookupSkill)
                         else "FOUR_CHANNEL_PROJECTION"),
        "complete_source_snapshot": (
            model.complete if isinstance(model, LookupSkill) else
            cost == 2 ** contract.width),
        "source_observations": cost,
        "compact_corrections": len(model.corrections)
        if isinstance(model, LookupSkill) else None,
        "declared_description_units": program_cost,
        "declared_full_raw_units": raw_cost,
        "source_contract": contract.packet(),
        "skill_cartridge": model.packet() if isinstance(model, LookupSkill) else None,
        "independent_review": decision,
        "test_covered": len(withheld) if eligible else 0,
        "test_correct": correct,
        "test_incorrect": len(withheld) - correct if eligible else 0,
        "destination_review": destination,
        "automatic_method_promotion": False,
        "real_world_authority": False,
        "external_operations": 0
    }


def summary(rows):
    accepted = [r for r in rows
                if r["independent_review"]["status"].startswith("ELIGIBLE")]
    models = [r for r in rows if r["skill_cartridge"] is not None]
    return {
        "worlds": len(rows),
        "review_eligible": len(accepted),
        "held": len(rows) - len(accepted),
        "lookup_cartridges": len(models),
        "compact_exact": sum(r["model_status"] == "COMPACT_EXACT" for r in rows),
        "compact_with_exceptions": sum(
            r["model_status"] == "COMPACT_WITH_EXCEPTIONS" for r in rows),
        "raw_lookup_used": sum(r["model_status"] == "RAW_LOOKUP" for r in rows),
        "training_source_observations": sum(r["source_observations"] for r in rows),
        "test_covered": sum(r["test_covered"] for r in rows),
        "test_incorrect": sum(r["test_incorrect"] for r in rows)
    }


def benchmark():
    dev = [Source(f, seed) for f in FAMILIES for seed in (0, 1)]
    evaluation = [Source(f, seed) for f in FAMILIES
                  for seed in (2, 3, 4, 5, 6)]
    developmental = {
        name: summary([trial(s, name) for s in dev]) for name in METHODS
    }
    final = {name: summary([trial(s, name) for s in evaluation])
             for name in METHODS}
    method_gain = (
        developmental["assimilated_hybrid"]["review_eligible"] >=
        developmental["classical_full_lookup"]["review_eligible"] + 2 and
        developmental["assimilated_hybrid"]["test_incorrect"] <=
        developmental["classical_full_lookup"]["test_incorrect"])
    return {
        "schema": "motif.law-forge.classical-lookup-assimilation.v1",
        "development": developmental,
        "evaluation": final,
        "frozen_method_decision": (
            "PROPOSE_FOR_HUMAN_REVIEW" if method_gain
            else "NO_METHOD_PROMOTION"),
        "examples": {
            f: trial(Source(f, 2)) for f in (
                "any_three_paths", "exactly_one_path",
                "edge_parity", "sparse_exception_six",
                "seven_parity", "seven_last_channel",
                "phase_shift", "seven_phase_shift")
        },
        "limitations": [
            "classical exact lookup plus bounded optional DNF compression",
            "full source domain sampled for admitted closed-domain models",
            "no proof of prediction on unseen source configurations",
            "no improvement over information-complete classical lookup",
            "six-link DNF grammar not transferred to seven-link contracts",
            "data SHA256 content checks are not real source signatures",
            "all mechanisms are synthetic and researcher-authored",
            "static description units are not actual energy or runtime cost"
        ],
        "no_automatic_admission": True, "real_world_authority": False,
        "external_operations": 0
    }


if __name__ == "__main__":
    print(json.dumps(benchmark(), indent=2, sort_keys=True))
