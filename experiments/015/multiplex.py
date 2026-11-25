"""MOTIF-015: bounded, simultaneous, counterfactual inquiry (synthetic only).

An avenue can be an answer computation, a question, or a check. The planner
chooses a *portfolio* by its joint decision value, not by summing per-avenue
information gain. A separate resolver supplies actual observations after
planning; no real-world authority is granted by selecting an avenue.
"""
from __future__ import annotations

from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from itertools import combinations
from typing import Callable, Dict, Mapping, Sequence, Tuple


@dataclass(frozen=True)
class Hypothesis:
    name: str
    answer: str
    weight: float = 1.0


@dataclass(frozen=True)
class Avenue:
    name: str
    kind: str  # ANSWER, ASK, or VERIFY; all are proposals, not external actions
    cost: float
    predicted: Mapping[str, str]  # hypothesis name -> possible observation
    origin: str
    prompt: str = ""
    human: bool = False
    allowed: bool = True


@dataclass(frozen=True)
class Plan:
    selected: Tuple[str, ...]
    status: str
    tentative_answer: str | None
    tentative_confidence: float
    baseline_accuracy: float
    expected_accuracy: float
    total_cost: float
    net_gain: float


def _normalized(hypotheses: Sequence[Hypothesis]) -> Dict[str, float]:
    if not hypotheses or len({h.name for h in hypotheses}) != len(hypotheses):
        raise ValueError("Need nonempty, uniquely named hypotheses")
    if any(h.weight < 0 for h in hypotheses):
        raise ValueError("Weights cannot be negative")
    total = sum(h.weight for h in hypotheses)
    if total <= 0:
        raise ValueError("Posterior must have positive mass")
    return {h.name: h.weight / total for h in hypotheses}


def best_answer(hypotheses: Sequence[Hypothesis]) -> tuple[str, float]:
    weights = _normalized(hypotheses)
    by_answer: Dict[str, float] = defaultdict(float)
    for h in hypotheses:
        by_answer[h.answer] += weights[h.name]
    return sorted(by_answer.items(), key=lambda item: (-item[1], item[0]))[0]


def expected_decision_accuracy(
    hypotheses: Sequence[Hypothesis], batch: Sequence[Avenue]
) -> float:
    """Exact expected MAP-answer accuracy over all joint observation signatures.

    No naive conditional-independence multiplication: each hypothetical world
    defines the *joint* signals, including perfectly redundant avenues.
    """
    weights = _normalized(hypotheses)
    groups: Dict[tuple[str, ...], Dict[str, float]] = defaultdict(lambda: defaultdict(float))
    for h in hypotheses:
        signature = tuple(a.predicted[h.name] for a in batch)
        groups[signature][h.answer] += weights[h.name]
    return sum(max(answer_mass.values()) for answer_mass in groups.values())


def choose(
    hypotheses: Sequence[Hypothesis],
    avenues: Sequence[Avenue],
    *,
    budget: float = 2.0,
    max_parallel: int = 3,
    cost_penalty: float = 0.01,
    answer_threshold: float = 0.8,
    max_human: int = 2,
) -> Plan:
    """Choose the best *joint* portfolio under hard constraints and costs.

    Enumerates portfolios exactly; intentionally capped at twelve avenues for
    a small falsifiable experiment, not suitable for large action spaces.
    """
    if len(avenues) > 12 or max_parallel < 0 or budget < 0 or cost_penalty < 0:
        raise ValueError("Invalid portfolio limit")
    if len({a.name for a in avenues}) != len(avenues):
        raise ValueError("Avenue names must be distinct")
    if any(a.kind not in {"ANSWER", "ASK", "VERIFY"} or a.cost < 0 for a in avenues):
        raise ValueError("Invalid avenue")
    weights = _normalized(hypotheses)
    for a in avenues:
        if set(a.predicted) != set(weights):
            raise ValueError("Avenue outcomes must cover all named hypotheses")
    answer, confidence = best_answer(hypotheses)
    baseline = expected_decision_accuracy(hypotheses, ())
    best_batch: tuple[Avenue, ...] = ()
    best_value = baseline
    best_accuracy = baseline
    # Exact same source / exact same predicted report is one available avenue,
    # even when presented under different names. Retain the first declaration.
    seen_claims: set[tuple[str, tuple[tuple[str, str], ...]]] = set()
    eligible = []
    for avenue in avenues:
        claim = (avenue.origin, tuple(sorted(avenue.predicted.items())))
        if avenue.allowed and claim not in seen_claims:
            seen_claims.add(claim)
            eligible.append(avenue)
    eligible.sort(key=lambda avenue: avenue.name)
    for size in range(1, min(len(eligible), max_parallel) + 1):
        for batch in combinations(eligible, size):
            cost = sum(a.cost for a in batch)
            if cost > budget + 1e-12 or sum(a.human for a in batch) > max_human:
                continue
            # An identical request from the same source is not another witness.
            if len({(a.origin, tuple(sorted(a.predicted.items()))) for a in batch}) != len(batch):
                continue
            accuracy = expected_decision_accuracy(hypotheses, batch)
            value = accuracy - cost_penalty * cost
            if value > best_value + 1e-12 or (
                abs(value - best_value) <= 1e-12
                and best_batch
                and (cost, tuple(a.name for a in batch))
                < (sum(a.cost for a in best_batch), tuple(a.name for a in best_batch))
            ):
                best_value, best_batch, best_accuracy = value, batch, accuracy
    has_answer = confidence >= answer_threshold
    if best_batch:
        status = "ANSWER_AND_EXPLORE" if has_answer else "MULTI_INQUIRY"
    else:
        status = "ANSWER" if has_answer else "HOLD"
    return Plan(
        selected=tuple(a.name for a in best_batch),
        status=status,
        tentative_answer=answer if has_answer else None,
        tentative_confidence=confidence,
        baseline_accuracy=baseline,
        expected_accuracy=best_accuracy,
        total_cost=sum(a.cost for a in best_batch),
        net_gain=best_value - baseline,
    )


def execute_synthetic(
    plan: Plan,
    avenues: Sequence[Avenue],
    resolver: Callable[[Avenue], str],
) -> dict[str, str]:
    """Run selected synthetic probes concurrently; preserve proposal ordering.

    `resolver` is an injected simulator callback, never an authenticated human
    answer or external-actuator bridge. Production adapters require separate
    permission, idempotency, timeouts, and evidence custody.
    """
    index = {a.name: a for a in avenues}
    if not plan.selected:
        return {}
    if any(not index[n].allowed for n in plan.selected):
        raise ValueError("Blocked avenue cannot execute")
    with ThreadPoolExecutor(max_workers=len(plan.selected)) as pool:
        futures = {pool.submit(resolver, index[name]): name for name in plan.selected}
        observations: dict[str, str] = {}
        for future in as_completed(futures):
            observations[futures[future]] = future.result()
    return {name: observations[name] for name in plan.selected}


def revise(
    hypotheses: Sequence[Hypothesis],
    avenues: Sequence[Avenue],
    observations: Mapping[str, str],
) -> tuple[str, tuple[Hypothesis, ...]]:
    """Only accept a consistent observation; contradiction => HOLD, not invention.

    This is noiseless version-space filtering, not a calibrated Bayesian
    witness model; later work must connect 014W's uncertain source model.
    """
    index = {a.name: a for a in avenues}
    if any(name not in index for name in observations):
        raise ValueError("Unknown observation source")
    remaining = tuple(
        h for h in hypotheses
        if all(index[name].predicted[h.name] == value for name, value in observations.items())
    )
    if not remaining:
        return "HOLD_MODEL_FALSIFIED", tuple(hypotheses)
    return "UPDATED", remaining

