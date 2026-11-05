"""MOTIF-010 evaluator: controlled scientific inquiry versus matched baselines.

ONLY this evaluator imports oracle.py. scientist.py never sees the hidden
family, labels for unperformed interventions, or independently held-out
evaluation results. Every proposed action is freshly executed inside the
synthetic simulator; there is no fixed pool of pre-generated labeled questions.

60 synthetic worlds = 6 mechanisms x 10 seeds. Every method starts with the
SAME two confounded natural observations and gets exactly two further
observations. Readout is a separate four-setting truth table.

Protocols are development-locked, not externally preregistered scientific
claims, and no such action corresponds to any real-world authorization.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from random import Random
from statistics import mean
import json

from oracle import (FAMILIES, SEEDS, world, natural_observations,
                    natural_case, intervene, test_world)
from scientist import (OPTIONS, candidate_cartridges, validated_result,
                       consensus, propose_intervention,
                       explanation_report)
from cartridge import (CartridgeBay, HOLD, export_cartridge,
                       validate_cartridge)

VERSION = "scientist-controlled-interventions-v1"
STEPS = 2
METHODS = ("scientist", "random", "fixed_diagnostic", "passive_natural")
EVALUATION_CONTROLS = OPTIONS


def control_order(family: str, seed: int):
    rng = Random(int.from_bytes(sha256(
        f"010:random:{family}:{seed}".encode()).digest()[:8], "big"))
    return rng.sample(list(OPTIONS), STEPS)


def evaluate_method(spec, method: str):
    if method not in METHODS:
        raise ValueError("Unknown controlled evaluator method")
    observed = list(natural_observations(spec))
    current = candidate_cartridges(observed, spec.controls)
    initial_candidates = len(current)
    queried = []
    events = []
    if method == "random":
        choices = control_order(spec.family, spec.seed)
    elif method == "fixed_diagnostic":
        # A competent classical experimental-design baseline, not MOTIF.
        choices = [(False, True), (True, False)]
    elif method == "passive_natural":
        choices = [(False, False), (True, True)]
    else:
        choices = None
    for step in range(STEPS):
        before = len(current)
        if method == "scientist":
            proposal = propose_intervention(current, queried)
            if proposal is None:
                raise AssertionError("No informative synthetic intervention within budget")
            controls = (proposal.first, proposal.second)
            proposed_gain = proposal.information_gain_bits
            vote_counts = [proposal.predicted_votes.count(False),
                           proposal.predicted_votes.count(True)]
        else:
            controls = choices[step]
            proposed_gain = None
            vote_counts = None
        # Crucial separation: a fresh world outcome is generated ONLY here,
        # after the scientist has selected the controlled settings.
        if method == "passive_natural":
            case = natural_case(spec, controls[0], 20_000 + step)
        else:
            case = intervene(spec, *controls, serial=20_000 + step)
        observed.append(case)
        queried.append(controls)
        current = candidate_cartridges(observed, spec.controls)
        events.append({
            "step": step + 1,
            "method": method,
            "controlled_port_settings": list(controls),
            "question_expected_information_bits": proposed_gain,
            "hypothesis_votes_before_observation": vote_counts,
            "observed_change": validated_result(case),
            "hypotheses_before": before,
            "hypotheses_after": len(current),
            "answer_exposed_before_proposal": False,
            "synthetic_world_only": True,
        })
    # Held-out, freshly generated test environments created *after* selection.
    test = test_world(spec, serial=40_000)
    total = len(test)
    asserted = 0
    correct = 0
    for settings, case in zip(EVALUATION_CONTROLS, test):
        prediction = consensus(current, *settings)
        if prediction is not None:
            asserted += 1
            correct += prediction == validated_result(case)
    return {
        "method": method,
        "initial_natural_observations": 2,
        "additional_observations": STEPS,
        "oracle_calls_after_initial": STEPS,
        "initial_explanations": initial_candidates,
        "remaining_explanations": len(current),
        "unique_model_identified": len(current) == 1,
        "source_tree_cartridge_ids": [card.id for card in current],
        "heldout_world_settings": total,
        "heldout_coverage": round(asserted / total, 4),
        "heldout_accuracy_when_covered": round(correct / asserted, 4) if asserted else None,
        "wrong_covered_predictions": asserted - correct,
        "events": events,
        "_final_cartridges": current,  # evaluator-only; removed from JSON receipt
    }


def cartridge_review_example():
    """One independently checked inferred tree may be locally admitted for
    prediction, never for acting. All 8 review observations are NEW and are
    NOT supplied to the version-space selector or its two-query budget.
    """
    spec = world("exclusive", 11)
    source = list(natural_observations(spec))
    source += [
        intervene(spec, False, True, 50_000),
        intervene(spec, True, False, 50_001),
    ]
    model = candidate_cartridges(source, spec.controls)
    if len(model) != 1:
        raise AssertionError("Expected diagnostic completion")
    candidate = model[0]
    raw = export_cartridge(candidate)
    restored = validate_cartridge(raw)
    bay = CartridgeBay()
    ticket = bay.offer(raw)
    held_by_default = ticket not in bay.admitted
    local = [intervene(spec, a, b, 60_000 + i*4 + 2*int(a) + int(b))
             for i in range(2) for a,b in OPTIONS]
    decision = bay.review(ticket, "ADMIT_PREDICT_ONLY",
                          "LOCAL_SYNTHETIC_STEWARD",
                          local_observations=local, min_balanced=0.65)
    # Includes 00, where both Boolean source predicates are absent.
    negative_before = local[0].before
    safe_negative_prediction = bay.predict_admitted(ticket, negative_before,
                                                    local[0].roles)
    bay.revoke(ticket, "LOCAL_SYNTHETIC_STEWARD")
    did_hold_after_revocation = False
    try:
        bay.predict_admitted(ticket, negative_before, local[0].roles)
    except HOLD:
        did_hold_after_revocation = True
    return {
        "cartridge_id": candidate.id,
        "semantic_roundtrip": restored == candidate,
        "local_hold_first": held_by_default,
        "separate_local_review_samples": len(local),
        "local_review_balanced": round(decision["local_score"], 4),
        "local_admission_type": decision["decision"],
        "prediction_allowed_with_absent_false_ports":
            safe_negative_prediction["hypothesis"] is False,
        "revoke_blocks_predict": did_hold_after_revocation,
        "checksum_authenticates_origin": False,
        "real_world_authority": False,
    }


def benchmark():
    rows = []
    for family in FAMILIES:
        for seed in SEEDS:
            spec = world(family, seed)
            outcomes = {
                name: evaluate_method(spec, name)
                for name in METHODS
            }
            cleaned = {}
            for name, evidence in outcomes.items():
                cleaned[name] = {key: val for key,val in evidence.items()
                                 if not key.startswith("_")}
            rows.append({"family": family, "seed": seed,
                         "methods": cleaned})
    return {
        "experiment": "MOTIF-010",
        "summary": aggregate(rows),
        "review": cartridge_review_example(),
        "worlds": rows
    }


def aggregate(rows):
    result = {
        "version": VERSION,
        "scope": "INDEPENDENT_SYNTHETIC_DO_SIMULATOR",
        "worlds": len(rows),
        "families": list(FAMILIES),
        "seeds": list(SEEDS),
        "starting_natural_observations_per_world": 2,
        "manipulations_or_new_observations_per_method": STEPS,
        "unperformed_outcomes_visible_to_scientist": False,
        "oracle_rule_imported_by_scientist": False,
        "user_world_or_real_identity_available": False,
        "candidate_cartridge_grammar": "ALL_16_TWO_INPUT_BOOLEAN_TREES",
        "classical_diagnostic_baseline_included": True,
        "real_world_actions": 0,
    }
    for method in METHODS:
        m = [x["methods"][method] for x in rows]
        result[method] = {
            "worlds": len(m),
            "worlds_exactly_identified": sum(x["unique_model_identified"] for x in m),
            "mean_heldout_coverage": round(mean(x["heldout_coverage"] for x in m), 4),
            "total_incorrect_covered_predictions": sum(
                x["wrong_covered_predictions"] for x in m),
            "mean_remaining_explanations": round(mean(
                x["remaining_explanations"] for x in m), 4),
            "query_budget_matched": all(
                x["additional_observations"] == STEPS for x in m),
        }
    result["scientist_minus_random_coverage"] = round(
        result["scientist"]["mean_heldout_coverage"] -
        result["random"]["mean_heldout_coverage"], 4)
    result["scientist_minus_fixed_diagnostic_coverage"] = round(
        result["scientist"]["mean_heldout_coverage"] -
        result["fixed_diagnostic"]["mean_heldout_coverage"], 4)
    return result


if __name__ == "__main__":
    print(json.dumps(benchmark(), indent=2, sort_keys=True))
