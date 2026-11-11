"""Bounded, common planner and decision-value query policy."""
from collections import defaultdict
from dataclasses import dataclass
from fractions import Fraction
from heapq import heappop, heappush
from itertools import combinations, count
from math import log2

from world import COSTS, GOAL_VALUE, PRIMITIVES
from composition import Call, F, Inapplicable, Macro, checked_apply, declared_entities


@dataclass
class Work:
    expanded_states: int = 0
    candidates_checked: int = 0
    primitive_guard_budget: int = 0


@dataclass(frozen=True)
class Plan:
    calls: tuple[Call, ...]
    cost: int

    @property
    def value(self):
        return GOAL_VALUE - self.cost


def primitive_calls(calls, catalog):
    for call in calls:
        op = catalog[call.operator]
        if isinstance(op, Macro):
            nested = tuple(Call(item.operator, tuple(
                call.roles[int(token[1:])] for token in item.roles))
                for item in op.calls)
            yield from primitive_calls(nested, catalog)
        else:
            yield call


def plan(initial, goal, library, work):
    """Dijkstra on primitive execution cost, then fewer planning calls."""
    catalog = PRIMITIVES | library
    choices = [(name, (subject,), COSTS[name], 1)
               for subject in declared_entities(initial)
               for name in PRIMITIVES]
    # Every induced operator in this pilot has one resource role.
    for name, op in sorted(library.items()):
        if op.role_types != ("bike",):
            raise ValueError("Pilot requires one resource role per macro")
        for subject in declared_entities(initial):
            roles = (subject,)
            expanded = tuple(primitive_calls((Call(name, roles),), catalog))
            cost = sum(COSTS[call.operator] for call in expanded)
            choices.append((name, roles, cost, len(expanded)))
    serial = count()
    queue = [(0, 0, next(serial), initial, ())]
    best = {initial: (0, 0)}
    while queue:
        cost, length, _, state, calls = heappop(queue)
        if best[state] != (cost, length):
            continue
        work.expanded_states += 1
        if goal in state:
            return Plan(calls, cost)
        for name, roles, edge_cost, guard_budget in choices:
            next_cost = cost + edge_cost
            if next_cost >= GOAL_VALUE:
                continue
            work.candidates_checked += 1
            # Charge all primitive guards, even if replay rejects the first one.
            work.primitive_guard_budget += guard_budget
            try:
                future = checked_apply(state, name, roles, catalog)
            except Inapplicable:
                continue
            rank = (next_cost, length + 1)
            if rank >= best.get(future, (GOAL_VALUE, 0)):
                continue
            best[future] = rank
            heappush(queue, (*rank, next(serial), future, calls + (Call(name, roles),)))
    return None


def questions(observable):
    # Every arm gets the same query vocabulary. A two-part check pays twice.
    return tuple(q for size in (1, 2) for q in combinations(observable, size))


def reading(facts, asset, question):
    return tuple(F(name, asset) in facts for name in question)


def split(beliefs, asset, question):
    groups = defaultdict(list)
    for belief in beliefs:
        groups[reading(belief.facts, asset, question)].append(belief)
    return dict(groups)


def value(solution):
    return solution.value if solution else 0


def decision(beliefs, asset, observable, library, policy, work):
    """Freeze a plan for each possible reply before seeing the owner's truth."""
    if policy not in {"fixed", "entropy", "decision"}:
        raise ValueError("Unknown query policy")
    cache = {}

    def best(group):
        common = frozenset.intersection(*(b.facts for b in group))
        if common not in cache:
            cache[common] = plan(common, F("delivered", asset), library, work)
        return cache[common]

    fallback = best(beliefs)
    chosen = ()
    contingent = {(): fallback}
    best_score = Fraction(value(fallback)) if policy == "decision" else 0
    expected = Fraction(value(fallback))
    for question in questions(observable):
        groups = split(beliefs, asset, question)
        if len(groups) < 2:
            continue
        mass = {key: sum(b.weight for b in group) for key, group in groups.items()}
        if policy == "fixed":
            candidate = {key: best(group) for key, group in groups.items()}
            return question, candidate, sum(mass[key] * value(route)
                                          for key, route in candidate.items()) - len(question)
        if policy == "entropy":
            score = -sum(float(p) * log2(float(p)) for p in mass.values()) / len(question)
            if score > best_score:
                chosen, best_score = question, score
            continue

        candidate = {key: best(group) for key, group in groups.items()}
        score = sum(mass[key] * value(route) for key, route in candidate.items()) - len(question)
        if score > best_score:
            chosen, contingent, best_score = question, candidate, score
            expected = score
    if policy == "entropy" and chosen:
        groups = split(beliefs, asset, chosen)
        contingent = {key: best(group) for key, group in groups.items()}
        expected = sum(sum(b.weight for b in group) * value(contingent[key])
                       for key, group in groups.items()) - len(chosen)
    return chosen, contingent, expected
