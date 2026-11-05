"""MOTIF-Q-001: choose the first useful question in a closed synthetic world.

A finite, declared hypothesis family predicts outcomes for sandbox trials.
Selection sees predictions and costs, NEVER the hidden mechanism. A separate
oracle simulates outcomes after selection. This is active query selection, not
causal discovery, real observation, authentication, or autonomous action.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations
import json

HYPOTHESES = ("part", "badge", "both", "either")


@dataclass(frozen=True)
class Trial:
    id: str
    part: bool
    badge: bool
    cost: int
    admitted: bool = True
    actor: str = "surrogate"


@dataclass(frozen=True)
class Observation:
    trial: Trial
    effect: bool
    provenance: str = "SYNTHETIC_ORACLE"


def predict(mechanism: str, trial: Trial) -> bool:
    """Candidate mechanism -> hypothetical outcome. No historical assertion."""
    if mechanism not in HYPOTHESES:
        raise ValueError("unknown synthetic mechanism")
    if mechanism == "part":
        return trial.part
    if mechanism == "badge":
        return trial.badge
    if mechanism == "both":
        return trial.part and trial.badge
    return trial.part or trial.badge


def compatible(observations: tuple[Observation, ...]) -> tuple[str, ...]:
    if any(event.provenance != "SYNTHETIC_ORACLE" for event in observations):
        raise ValueError("unverified observations cannot enter this toy experiment")
    return tuple(h for h in HYPOTHESES
                 if all(predict(h, event.trial) == event.effect
                        for event in observations))


def candidate_trials() -> tuple[Trial, ...]:
    return (
        Trial("a_part-surrogate", True, False, 1),
        Trial("b_badge-surrogate", False, True, 1),
        Trial("c_nuisance-repeat", True, True, 1),
        Trial("d_expensive-part", True, False, 4),
        Trial("e_refused-part", True, False, 0, admitted=False),
    )


def target_trial() -> Trial:
    # Different actor. Transfer of the common mechanism is a fixture assumption.
    return Trial("target-another-actor", True, False, 0, admitted=False,
                 actor="target")


def forecast(hypotheses: tuple[str, ...], target: Trial) -> str:
    if not hypotheses:
        return "ABSTAIN_MODEL_MISS"
    effects = {predict(h, target) for h in hypotheses}
    if len(effects) > 1:
        return "ABSTAIN"
    return "EFFECT_HYPOTHESIS" if True in effects else "NO_EFFECT_HYPOTHESIS"


def _target_resolved_count(
    hypotheses: tuple[str, ...], probe: Trial, target: Trial
) -> int:
    """Number of equiprobable hypothesis states whose probe branch is pure.

    This is a declared finite count, NOT empirical probability calibration.
    """
    groups: dict[bool, list[str]] = {}
    for h in hypotheses:
        groups.setdefault(predict(h, probe), []).append(h)
    return sum(len(group) for group in groups.values()
               if len({predict(h, target) for h in group}) == 1)


def select_question(
    hypotheses: tuple[str, ...], probes: tuple[Trial, ...],
    target: Trial, budget: int, asked: frozenset[str] = frozenset()
) -> Trial | None:
    """Greedy target-resolution per unit cost, with deterministic ties.

    Never inspects ground truth. Only allowed, unasked, affordable probes can
    be selected. It abstains rather than invent a distinguishing observation.
    """
    if budget < 0:
        raise ValueError("budget cannot be negative")
    if forecast(hypotheses, target) != "ABSTAIN":
        return None
    choices = []
    for probe in probes:
        if (not probe.admitted or probe.id in asked
                or probe.cost <= 0 or probe.cost > budget):
            continue
        score = _target_resolved_count(hypotheses, probe, target)
        if score > 0:
            choices.append((Fraction(score, probe.cost), score,
                            -probe.cost, probe.id, probe))
    if not choices:
        return None
    # Reproducible tie: highest gain/cost, then gain, then lower cost, then ID.
    choices.sort(key=lambda row: (-row[0], -row[1], -row[2], row[3]))
    return choices[0][-1]


def select_information_gain(
    hypotheses: tuple[str, ...], probes: tuple[Trial, ...],
    budget: int, asked: frozenset[str] = frozenset()
) -> Trial | None:
    """Strong ordinary baseline: finite hypothesis pair elimination per cost.

    This target-blind baseline uses the SAME declared hypotheses and trials.
    It does not see the oracle. No advantage is claimed if MOTIF ties it.
    """
    candidates = []
    for probe in probes:
        if (not probe.admitted or probe.id in asked or probe.cost <= 0
                or probe.cost > budget):
            continue
        eliminated_pairs = sum(
            predict(h1, probe) != predict(h2, probe)
            for index, h1 in enumerate(hypotheses)
            for h2 in hypotheses[index + 1:]
        )
        if eliminated_pairs:
            candidates.append((
                Fraction(eliminated_pairs, probe.cost),
                eliminated_pairs, -probe.cost, probe.id, probe
            ))
    if not candidates:
        return None
    candidates.sort(key=lambda row: (-row[0], -row[1], -row[2], row[3]))
    return candidates[0][-1]


def decide_with_oracle(
    hidden_mechanism: str, probes: tuple[Trial, ...] | None = None,
    target: Trial | None = None, budget: int = 1,
    policy: str = "active"
) -> dict[str, object]:
    """Simulation harness; hidden mechanism never enters the selector.

    Prior observations show both features -> effect and neither -> no effect.
    The target is a separate actor, not itself attempted by the learner.
    """
    if hidden_mechanism not in HYPOTHESES:
        raise ValueError("unknown oracle mechanism")
    if policy not in ("active", "info_gain", "fixed_nuisance"):
        raise ValueError("unknown declared policy")
    if budget < 0:
        raise ValueError("negative budget")
    probes = candidate_trials() if probes is None else probes
    target = target_trial() if target is None else target
    observations = (
        Observation(Trial("prior-both", True, True, 0), True),
        Observation(Trial("prior-neither", False, False, 0), False),
    )
    current = compatible(observations)
    prior = current
    asked: set[str] = set()
    remaining = budget
    receipts: list[dict[str, object]] = []
    while forecast(current, target) == "ABSTAIN":
        if policy == "active":
            chosen = select_question(current, probes, target, remaining,
                                     frozenset(asked))
        elif policy == "info_gain":
            chosen = select_information_gain(current, probes, remaining,
                                             frozenset(asked))
        else:
            chosen = next(
                (p for p in probes if p.id == "c_nuisance-repeat"
                 and p.admitted and p.cost <= remaining
                 and p.id not in asked), None
            )
        if chosen is None:
            break
        # This check is the simulator's last gate; refusal never becomes failure.
        if not chosen.admitted:
            raise AssertionError("denied trial reached execution")
        frozen_predictions = {h: predict(h, chosen) for h in current}
        asked.add(chosen.id)
        remaining -= chosen.cost
        observed = predict(hidden_mechanism, chosen)  # ORACLE ONLY HERE
        updated = tuple(h for h in current if frozen_predictions[h] == observed)
        receipts.append({
            "trial": chosen.id,
            "cost": chosen.cost,
            "actor": chosen.actor,
            "predictions_before": frozen_predictions,
            "synthetic_observation": observed,
            "hypotheses_before": list(current),
            "hypotheses_after": list(updated),
            "provenance": "SYNTHETIC_ORACLE",
            "effect_on_world": "NONE",
        })
        current = updated
    prediction = forecast(current, target)
    oracle_target = predict(hidden_mechanism, target)
    return {
        "schema": "motif.question-study/v0",
        "policy": policy,
        "initial_hypotheses": list(prior),
        "query_receipts": receipts,
        "remaining_budget": remaining,
        "remaining_hypotheses": list(current),
        "target_prediction": prediction,
        "evaluator_target_truth": oracle_target,
        "answered": prediction not in ("ABSTAIN", "ABSTAIN_MODEL_MISS"),
        "correct_if_answered": (
            (prediction == "EFFECT_HYPOTHESIS") == oracle_target
            if prediction not in ("ABSTAIN", "ABSTAIN_MODEL_MISS")
            else None
        ),
        "no_real_action": True,
    }


def dogram_probe_family(
    hypotheses: tuple[str, ...] | None = None,
    probes: tuple[Trial, ...] | None = None
) -> dict[str, object]:
    """Dogram-compatible finite probe vectors; NOT a Dogram receipt.

    Only projections over DECLARED hypotheses are exported. Withheld oracle
    identity, synthetic observations and permission-denied probes stay out.
    """
    hypotheses = HYPOTHESES if hypotheses is None else hypotheses
    probes = candidate_trials() if probes is None else probes
    valid = [p for p in probes if p.admitted and p.cost > 0]
    return {
        "schema": "motif.dogram-probe-family/v0",
        "states": list(hypotheses),
        "probes": {p.id: [int(predict(h, p)) for h in hypotheses]
                   for p in valid},
        "costs": {p.id: p.cost for p in valid},
        "target_labels": [int(predict(h, target_trial()))
                          for h in hypotheses],
        "excluded_trials": [p.id for p in probes if not p.admitted],
        "claim": "declared finite hypothesis partitions only; no evidence or authority",
    }


def run_demo() -> dict[str, object]:
    rows = [decide_with_oracle(h, policy=policy) for policy in
            ("active", "info_gain", "fixed_nuisance") for h in HYPOTHESES]
    stats = {
        policy: {
            "answered": sum(row["answered"] for row in rows
                            if row["policy"] == policy),
            "correct_answers": sum(row["correct_if_answered"] is True
                                   for row in rows if row["policy"] == policy),
            "total_cases": len(HYPOTHESES),
            "total_query_cost": sum(
                event["cost"] for row in rows if row["policy"] == policy
                for event in row["query_receipts"]),
        }
        for policy in ("active", "info_gain", "fixed_nuisance")
    }
    return {"experiment": "MOTIF-Q-001", "domain": "synthetic finite toy",
            "statistics": stats, "cases": rows,
            "dogram_probe_family": dogram_probe_family()}


if __name__ == "__main__":
    print(json.dumps(run_demo(), indent=2))
