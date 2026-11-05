"""MOTIF-016: The Living Forest — bounded, adaptive research in synthetic worlds.

Select several complementary avenues now, but also look ahead to questions
that become available after answers. Every forecast is counterfactual until a
separate synthetic resolver returns an observation. No outside-world actions.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from itertools import combinations
from math import isfinite
from pathlib import Path
from typing import Callable, Mapping, Sequence
import sys

# Reuse the reviewed MOTIF-015 synthetic parallel dispatcher and hypothesis type.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "015"))
from multiplex import Avenue, Hypothesis, Plan as BatchPlan, best_answer, execute_synthetic  # noqa: E402


@dataclass(frozen=True)
class Road:
    name: str
    kind: str
    cost: float
    predicted: Mapping[str, str]  # declared world->possible signal, NOT an oracle read
    origin: str
    requires: tuple[tuple[str, str], ...] = ()
    allowed: bool = True
    human: bool = False
    prompt: str = ""


@dataclass(frozen=True)
class _Evaluation:
    selected: tuple[str, ...]
    score: float  # expected future decision accuracy less expected probe costs
    expected_accuracy: float
    expected_cost: float


@dataclass(frozen=True)
class Forecast:
    result: tuple[tuple[str, str], ...]
    probability: float
    hypothetical_survivors: tuple[str, ...]
    newly_available: tuple[str, ...]
    next_selected: tuple[str, ...]
    projected_accuracy: float


@dataclass(frozen=True)
class ForestPlan:
    revision: int
    status: str
    selected: tuple[str, ...]
    tentative_answer: str | None
    confidence: float
    current_accuracy: float
    expected_final_accuracy: float
    immediate_cost: float
    expected_total_cost: float
    objective: float
    forecasts: tuple[Forecast, ...]
    evaluated_states: int
    cache_hits: int


@dataclass(frozen=True)
class WitnessedStep:
    revision: int
    selected: tuple[str, ...]
    evidence: tuple[tuple[str, str, str], ...]  # road, origin, reported outcome
    pruned_hypotheses: tuple[str, ...]
    newly_available: tuple[str, ...]
    spent_total: float
    confidence: float
    status: str


class LivingForest:
    """Finite exact expectimax, not a trained model or an autonomous agent.

    A road can be unlocked by earlier evidence. Planning marginalizes over
    every hypothetical outcome and recursively chooses another portfolio.
    Lookup keys canonicalize observation order (transposition merging).
    """

    def __init__(
        self,
        hypotheses: Sequence[Hypothesis],
        roads: Sequence[Road],
        *,
        budget: float = 1.25,
        rounds: int = 2,
        max_parallel: int = 2,
        max_human: int = 2,
        cost_penalty: float = 0.01,
        answer_threshold: float = 0.8,
        stop_threshold: float = 0.999,
    ):
        if not hypotheses or len(hypotheses) > 64 or len({h.name for h in hypotheses}) != len(hypotheses):
            raise ValueError("Need 1..64 uniquely named hypotheses")
        if any(not isfinite(h.weight) or h.weight < 0 for h in hypotheses) or sum(h.weight for h in hypotheses) <= 0:
            raise ValueError("Hypothesis weights must be finite, nonnegative, and nonzero in total")
        if len(roads) > 12 or len({r.name for r in roads}) != len(roads):
            raise ValueError("Need at most 12 uniquely named roads")
        if not (0 <= budget and isfinite(budget) and 0 <= rounds <= 3 and 1 <= max_parallel <= 3
                and 0 <= max_human <= 12 and 0 <= cost_penalty and isfinite(cost_penalty)
                and 0 < answer_threshold <= stop_threshold <= 1):
            raise ValueError("Invalid finite search limits")
        self.hypotheses = tuple(hypotheses)
        self.names = tuple(h.name for h in hypotheses)
        self.weights = {h.name: h.weight for h in hypotheses}
        self.roads = {r.name: r for r in roads}
        for r in roads:
            if (r.kind not in {"ANSWER", "ASK", "VERIFY"} or not r.name or not r.origin
                    or not isfinite(r.cost) or r.cost < 0
                    or set(r.predicted) != set(self.names)
                    or any(not isinstance(v, str) for v in r.predicted.values())):
                raise ValueError("Malformed road or outcome model: " + r.name)
            if len(set(r.requires)) != len(r.requires):
                raise ValueError("Repeated prerequisite")
            for dependency, result in r.requires:
                if dependency == r.name or dependency not in self.roads:
                    raise ValueError("Unknown or self-referential prerequisite")
                if result not in self.roads[dependency].predicted.values():
                    raise ValueError("Impossible prerequisite result")
        self.budget = budget
        self.round_limit = rounds
        self.max_parallel = max_parallel
        self.max_human = max_human
        self.cost_penalty = cost_penalty
        self.answer_threshold = answer_threshold
        self.stop_threshold = stop_threshold
        self.live = self.names
        self.observed: dict[str, str] = {}
        self.spent = 0.0
        self.rounds_used = 0
        self.human_used = 0
        self.history: list[WitnessedStep] = []
        self.counterexamples: list[dict] = []
        self.state = "ACTIVE"
        self._cache_hits = 0

    def _posterior(self, living: Sequence[str]) -> tuple[Hypothesis, ...]:
        return tuple(Hypothesis(h, next(x.answer for x in self.hypotheses if x.name == h), self.weights[h])
                     for h in living)

    def _accuracy(self, living: Sequence[str]) -> float:
        return best_answer(self._posterior(living))[1]

    def _ready(self, observed: Mapping[str, str]) -> tuple[Road, ...]:
        # Canonical duplicate suppression. These are *declared* origins, not
        # authenticated independence or real evidence custody.
        eligible = [
            r for r in self.roads.values()
            if r.allowed and r.name not in observed
            and all(observed.get(name) == value for name, value in r.requires)
        ]
        seen = set()
        result = []
        for r in sorted(eligible, key=lambda item: (item.cost, item.name)):
            claim = (r.origin, tuple((name, r.predicted[name]) for name in sorted(self.names)))
            if claim not in seen:
                result.append(r)
                seen.add(claim)
        return tuple(sorted(result, key=lambda item: item.name))

    def _partitions(self, living: Sequence[str], batch: Sequence[Road]):
        pieces: dict[tuple[str, ...], list[str]] = defaultdict(list)
        for name in living:
            pieces[tuple(r.predicted[name] for r in batch)].append(name)
        denominator = sum(self.weights[h] for h in living)
        return tuple(
            (signature, tuple(members), sum(self.weights[n] for n in members) / denominator)
            for signature, members in sorted(pieces.items())
            if sum(self.weights[n] for n in members) > 0
        )

    def _search(
        self,
        living: tuple[str, ...],
        observed: Mapping[str, str],
        remaining: float,
        depth: int,
        human_left: int,
        memo: dict,
    ) -> _Evaluation:
        key = (living, tuple(sorted(observed.items())), round(remaining, 10), depth, human_left)
        if key in memo:
            self._cache_hits += 1
            return memo[key]
        accuracy = self._accuracy(living)
        best = _Evaluation((), accuracy, accuracy, 0.0)
        if depth == 0 or accuracy >= self.stop_threshold:
            memo[key] = best
            return best
        ready = self._ready(observed)
        for size in range(1, min(len(ready), self.max_parallel) + 1):
            for batch in combinations(ready, size):
                cost = sum(r.cost for r in batch)
                human = sum(r.human for r in batch)
                if cost > remaining + 1e-10 or human > human_left:
                    continue
                score = -self.cost_penalty * cost
                forecast_accuracy = 0.0
                forecast_cost = cost
                for signature, survivors, probability in self._partitions(living, batch):
                    next_observed = dict(observed)
                    next_observed.update(zip((r.name for r in batch), signature))
                    child = self._search(survivors, next_observed, remaining - cost,
                                         depth - 1, human_left - human, memo)
                    score += probability * child.score
                    forecast_accuracy += probability * child.expected_accuracy
                    forecast_cost += probability * child.expected_cost
                proposal = _Evaluation(tuple(r.name for r in batch), score,
                                       forecast_accuracy, forecast_cost)
                # Free to STOP; on equal utility prefer fewer queries/cost.
                if (proposal.score > best.score + 1e-12 or
                        (abs(proposal.score - best.score) <= 1e-12 and best.selected
                         and (proposal.expected_cost, proposal.selected)
                         < (best.expected_cost, best.selected))):
                    best = proposal
        memo[key] = best
        return best

    def plan(self) -> ForestPlan:
        if self.state == "HOLD_MODEL_FALSIFIED":
            return ForestPlan(len(self.history), self.state, (), None, 0,
                              0, 0, 0, 0, 0, (), 0, 0)
        current_answer, confidence = best_answer(self._posterior(self.live))
        available_budget = self.budget - self.spent
        self._cache_hits = 0
        memo: dict = {}
        answer = self._search(self.live, self.observed, available_budget,
                              self.round_limit - self.rounds_used,
                              self.max_human - self.human_used, memo)
        if answer.selected:
            status = "ANSWER_AND_EXPLORE" if confidence >= self.answer_threshold else "MULTI_INQUIRY"
        else:
            status = "ANSWER" if confidence >= self.answer_threshold else "HOLD"
        ready_now = {r.name for r in self._ready(self.observed)}
        batch = [self.roads[name] for name in answer.selected]
        immediate_cost = sum(r.cost for r in batch)
        forecasts = []
        for outcome, survivors, probability in self._partitions(self.live, batch) if batch else ():
            projected = dict(self.observed)
            projected.update(zip(answer.selected, outcome))
            after = self._search(survivors, projected, available_budget - immediate_cost,
                                 self.round_limit - self.rounds_used - 1,
                                 self.max_human - self.human_used - sum(r.human for r in batch), memo)
            forecasts.append(Forecast(
                tuple(zip(answer.selected, outcome)),
                probability,
                survivors,
                tuple(sorted({r.name for r in self._ready(projected)} - ready_now)),
                after.selected,
                after.expected_accuracy,
            ))
        return ForestPlan(
            revision=len(self.history), status=status, selected=answer.selected,
            tentative_answer=current_answer if confidence >= self.answer_threshold else None,
            confidence=confidence, current_accuracy=confidence,
            expected_final_accuracy=answer.expected_accuracy,
            immediate_cost=immediate_cost,
            expected_total_cost=answer.expected_cost,
            objective=answer.score,
            forecasts=tuple(forecasts),
            evaluated_states=len(memo), cache_hits=self._cache_hits,
        )

    def accept(self, plan: ForestPlan, observations: Mapping[str, str]) -> WitnessedStep:
        """Accept only results of the current selected portfolio, never forecasts."""
        if plan.revision != len(self.history) or plan.selected != self.plan().selected or not plan.selected:
            raise ValueError("Stale, empty, or unauthorized plan")
        if set(observations) != set(plan.selected):
            raise ValueError("Only complete observations for the selected portfolio are accepted")
        batch = [self.roads[name] for name in plan.selected]
        before = {r.name for r in self._ready(self.observed)}
        survivors = tuple(
            h for h in self.live
            if all(self.roads[name].predicted[h] == observations[name] for name in plan.selected)
        )
        cost = sum(r.cost for r in batch)
        self.spent += cost
        self.rounds_used += 1
        self.human_used += sum(r.human for r in batch)
        evidence = tuple((r.name, r.origin, observations[r.name]) for r in batch)
        if survivors:
            pruned = tuple(h for h in self.live if h not in survivors)
            self.live = survivors
            self.observed.update(observations)
            unlocked = tuple(sorted({r.name for r in self._ready(self.observed)} - before))
            confidence = self._accuracy(self.live)
            self.state = "ANSWER" if confidence >= self.stop_threshold else "ACTIVE"
        else:
            # A contradiction is a scar, not permission to invent a new cause
            # or silently reset/overwrite the previous posterior.
            pruned = ()
            unlocked = ()
            confidence = self._accuracy(self.live)
            self.counterexamples.append({
                "revision": len(self.history),
                "reported": evidence,
                "reason": "NO_EXISTING_HYPOTHESIS_PREDICTS_JOINT_RESULT",
            })
            self.state = "HOLD_MODEL_FALSIFIED"
        record = WitnessedStep(len(self.history), plan.selected, evidence,
                               pruned, unlocked, self.spent, confidence, self.state)
        self.history.append(record)
        return record

    def run_synthetic_round(self, resolver: Callable[[Road], str]) -> tuple[ForestPlan, WitnessedStep | None]:
        """Actually dispatch callbacks concurrently; no real actions or humans."""
        plan = self.plan()
        if not plan.selected:
            return plan, None
        avenues = [
            Avenue(r.name, r.kind, r.cost, r.predicted, r.origin,
                   r.prompt, r.human, r.allowed)
            for r in self.roads.values()
        ]
        batch = BatchPlan(plan.selected, plan.status, plan.tentative_answer,
                          plan.confidence, plan.current_accuracy,
                          plan.expected_final_accuracy, plan.immediate_cost,
                          plan.objective - plan.current_accuracy)
        found = execute_synthetic(batch, avenues,
                                  lambda a: resolver(self.roads[a.name]))
        return plan, self.accept(plan, found)
