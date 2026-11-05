"""MOTIF-019F: classical STRIPS planning as composable, reviewable methods.

Actual BFS, uniform-cost search (Dijkstra), and A* with admissible h_max
delete-relaxed heuristic. Plans are computed at invocation time from action
schemas and facts, never written as fixed route lookup tables.

All actions are synthetic predictions, not permission to execute.
"""
from __future__ import annotations
from collections import deque
from dataclasses import dataclass, replace
from hashlib import sha256
import heapq
import itertools
import json
from math import inf, isfinite
from typing import FrozenSet, Iterable, Sequence

FactSet = FrozenSet[str]


@dataclass(frozen=True)
class Operator:
    name: str
    pre: FactSet
    add: FactSet
    delete: FactSet = frozenset()
    cost: float = 1.0

    def __post_init__(self):
        if not self.name or not isfinite(self.cost) or self.cost <= 0:
            raise ValueError("Operators require name and finite positive cost")
        if self.add & self.delete:
            raise ValueError("Add/delete lists must not overlap")

    def possible(self, state: FactSet) -> bool:
        return self.pre <= state

    def apply(self, state: FactSet) -> FactSet:
        if not self.possible(state):
            raise ValueError("Action preconditions not satisfied")
        return frozenset((state - self.delete) | self.add)


@dataclass(frozen=True)
class Task:
    facts: FactSet
    goal: FactSet
    operators: tuple[Operator, ...]
    version: int = 0

    def __post_init__(self):
        if len({o.name for o in self.operators}) != len(self.operators):
            raise ValueError("Duplicate operator name")
        if not self.goal:
            raise ValueError("Task goal must not be empty")
        if len(self.operators) > 60 or len(self.facts | self.goal | frozenset(
             f for o in self.operators for f in (o.pre | o.add | o.delete))) > 24:
            raise ValueError("Tiny bounded research tasks only")

    def replace_guard(self, name: str, extra_pre: str) -> "Task":
        if name not in {o.name for o in self.operators}:
            raise ValueError("Unknown action")
        return replace(self, operators=tuple(
            replace(op, pre=op.pre | {extra_pre}) if op.name == name else op
            for op in self.operators
        ), version=self.version + 1)


@dataclass(frozen=True)
class PlanResult:
    status: str
    algorithm: str
    actions: tuple[str, ...]
    cost: float
    expanded: int
    generated: int
    goal_met: bool
    model_version: int
    method_source: str = "CLASSICAL_STRIPS"
    external_effects: bool = False


@dataclass(frozen=True)
class MethodCartridge:
    name: str
    algorithm: str
    heuristic: str
    action_model_hash: str
    model_version: int
    measured_plan_cost: float
    search_expansions: int
    reference_ucs_cost: float
    status: str = "HOLD_FOR_LOCAL_REVIEW"
    external_effects: bool = False


@dataclass(frozen=True)
class MethodFoundry:
    chosen: MethodCartridge | None
    candidates: tuple[MethodCartridge, ...]
    reference: PlanResult
    planning_attempts: tuple[PlanResult, ...]


def hmax(task: Task, state: FactSet) -> float:
    """Admissible delete-relaxation lower bound for additive positive costs.

    One subgoal's cheapest relaxed justification is a lower bound. Taking
    the maximum across goal facts remains a lower bound on sequential cost.
    """
    possible_facts = set(task.goal | state)
    for op in task.operators:
        possible_facts.update(op.pre | op.add)
    distance = {f: (0.0 if f in state else inf) for f in possible_facts}
    for _ in range(len(possible_facts) + 1):
        changed = False
        for op in task.operators:
            prerequisites = [distance.get(p, inf) for p in op.pre]
            if any(not isfinite(v) for v in prerequisites):
                continue
            price = op.cost + (max(prerequisites) if prerequisites else 0.)
            for fact in op.add:
                if price < distance[fact] - 1e-12:
                    distance[fact] = price
                    changed = True
        if not changed:
            break
    return max(distance.get(g, inf) for g in task.goal)


def verify_plan(task: Task, steps: Sequence[str]) -> tuple[bool, float]:
    """Independently replay an alleged method on its declared action model."""
    state = task.facts
    ops = {op.name: op for op in task.operators}
    total = 0.0
    try:
        for name in steps:
            state = ops[name].apply(state)
            total += ops[name].cost
    except (ValueError, KeyError):
        return False, total
    return task.goal <= state, total


def find_plan(task: Task, algorithm: str = "UCS",
              *, max_expanded: int = 4000) -> PlanResult:
    """Bounded graph search, including a genuinely cost-optimal classical control.

    BFS minimizes action count only; UCS minimizes total positive action cost;
    A* uses admissible hmax, hence also minimizes model cost if not truncated.
    """
    if algorithm not in {"BFS", "UCS", "ASTAR_HMAX"} or not 1 <= max_expanded <= 50000:
        raise ValueError("Unsupported classical method or expansion limit")
    initial = task.facts
    ops = tuple(sorted(task.operators, key=lambda o: o.name))
    if task.goal <= initial:
        return PlanResult("PLAN", algorithm, (), 0.0, 0, 1, True, task.version)
    counter = itertools.count()
    expanded = 0
    generated = 1
    q = deque([(initial, (), 0.)]) if algorithm == "BFS" else None
    frontier = []
    if algorithm != "BFS":
        heuristic = hmax(task, initial) if algorithm == "ASTAR_HMAX" else 0.
        heapq.heappush(frontier, (heuristic, next(counter), 0., initial, ()))
    best_depth = {initial: 0}
    best_cost = {initial: 0.0}
    while (q if algorithm == "BFS" else frontier):
        if expanded >= max_expanded:
            return PlanResult("HOLD_SEARCH_LIMIT", algorithm, (), inf,
                              expanded, generated, False, task.version)
        if algorithm == "BFS":
            state, steps, price = q.popleft()
        else:
            _, _, price, state, steps = heapq.heappop(frontier)
            if price > best_cost.get(state, inf) + 1e-12:
                continue
        expanded += 1
        if task.goal <= state:
            return PlanResult("PLAN", algorithm, steps, price, expanded,
                              generated, True, task.version)
        for op in ops:
            if not op.possible(state):
                continue
            next_state = op.apply(state)
            next_steps = steps + (op.name,)
            next_cost = price + op.cost
            if algorithm == "BFS":
                if len(next_steps) >= best_depth.get(next_state, inf):
                    continue
                best_depth[next_state] = len(next_steps)
                q.append((next_state, next_steps, next_cost))
                generated += 1
            else:
                if next_cost >= best_cost.get(next_state, inf) - 1e-12:
                    continue
                best_cost[next_state] = next_cost
                heuristic = hmax(task, next_state) if algorithm == "ASTAR_HMAX" else 0.
                if not isfinite(heuristic):
                    continue
                heapq.heappush(frontier, (
                    next_cost + heuristic, next(counter), next_cost,
                    next_state, next_steps,
                ))
                generated += 1
    return PlanResult("HOLD_NO_PLAN", algorithm, (), inf, expanded,
                      generated, False, task.version)


def _model_hash(task: Task) -> str:
    payload = [
        (o.name, sorted(o.pre), sorted(o.add), sorted(o.delete), o.cost)
        for o in sorted(task.operators, key=lambda op: op.name)
    ]
    return sha256(json.dumps(payload).encode()).hexdigest()


def develop_methods(task: Task, *, budget_expansions: int = 4000) -> MethodFoundry:
    """Develop bounded strategy cartridges at runtime from a typed grammar.

    Each candidate's plan is replayed and compared to a UCS reference. A
    discovered shortcut in a KNOWN model can be retained as a method proposal.
    This changes no outside-world code or execution authority.
    """
    if not 1 <= budget_expansions <= 50000:
        raise ValueError("Invalid compute budget")
    attempts = tuple(find_plan(task, algorithm, max_expanded=budget_expansions)
                     for algorithm in ("BFS", "UCS", "ASTAR_HMAX"))
    reference = attempts[1]
    method_cartridges = []
    if reference.status != "PLAN":
        return MethodFoundry(None, (), reference, attempts)
    for result in attempts:
        valid, replay_cost = verify_plan(task, result.actions)
        if result.status != "PLAN" or not valid or abs(replay_cost-result.cost) > 1e-8:
            continue
        optimal = abs(result.cost - reference.cost) <= 1e-8
        method_cartridges.append(MethodCartridge(
            name="SYNTHESIZED_" + result.algorithm + "_V" + str(task.version),
            algorithm=result.algorithm,
            heuristic="H_MAX" if result.algorithm == "ASTAR_HMAX" else "ZERO",
            action_model_hash=_model_hash(task),
            model_version=task.version,
            measured_plan_cost=result.cost,
            search_expansions=result.expanded,
            reference_ucs_cost=reference.cost,
            status=("HOLD_OPTIMAL_MODEL_ONLY_REVIEW" if optimal
                    else "REFUSE_MORE_COSTLY_THAN_UCS"),
        ))
    eligible = [m for m in method_cartridges
                if m.status == "HOLD_OPTIMAL_MODEL_ONLY_REVIEW"]
    # Measuring expansions is a weak proxy; hmax preprocessing cost is NOT
    # included. No wallclock speedup claimed without separate profiling.
    chosen = min(eligible, key=lambda m: (m.search_expansions, m.algorithm)) if eligible else None
    return MethodFoundry(chosen, tuple(method_cartridges), reference, attempts)
