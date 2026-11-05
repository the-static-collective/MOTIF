"""MOTIF-007 — The Smallest Key (finite, hypothetical intervention search).

Find the least-cost *declared* series of interventions that opens a specific
actor-relative opportunity without silently sacrificing another actor's.
Reality, legality, permission, outcome and value are NOT learned here. All
transitions are invented, inert, and limited to one explicit finite world.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from heapq import heappop, heappush
import json

TASK_TO_TOOL = {"well": "kit", "bike": "kit"}
SCOPES = ("physical", "admitted", "visible")
KINDS = ("loan", "teach", "inform", "mint", "grant")
Key = tuple[str, str]


@dataclass(frozen=True)
class World:
    skills: frozenset[Key]
    custody: frozenset[Key]          # (actor, asset_id); exclusive
    assets: frozenset[Key]           # (asset_id, tool_kind)
    access: frozenset[Key]           # declared world permission, not legal consent
    known: frozenset[Key]            # actor knows this opportunity is available

    def __post_init__(self) -> None:
        assets = dict(self.assets)
        if len(assets) != len(self.assets):
            raise ValueError("asset identifiers must be unique")
        held = [asset_id for _, asset_id in self.custody]
        if len(set(held)) != len(held) or any(x not in assets for x in held):
            raise ValueError("custody must reference exclusively held known assets")
        if any(task not in TASK_TO_TOOL for _, task in
               self.skills | self.access | self.known):
            raise ValueError("unknown task in world")
        if any(kind not in TASK_TO_TOOL.values() for kind in assets.values()):
            raise ValueError("unknown asset kind")


@dataclass(frozen=True)
class Intervention:
    id: str
    kind: str
    source: str
    recipient: str
    subject: str
    cost: int
    admitted: bool = True          # supplied toy gate, never real-world authority
    tool_kind: str = ""             # only used for mint

    def __post_init__(self) -> None:
        if not self.id or self.kind not in KINDS or not self.source or not self.recipient:
            raise ValueError("invalid intervention identity or kind")
        if not self.subject or type(self.cost) is not int or self.cost <= 0:
            raise ValueError("intervention cost must be a positive integer")


@dataclass(frozen=True)
class Goal:
    task: str
    scope: str = "visible"
    actor: str | None = None
    protect_existing: bool = True

    def __post_init__(self) -> None:
        if self.task not in TASK_TO_TOOL or self.scope not in SCOPES:
            raise ValueError("unknown declared goal")


def options(world: World) -> dict[str, frozenset[Key]]:
    """Deduplicate capability identity by (actor,task), NOT number of tools or paths."""
    available_kinds = {
        actor: frozenset(dict(world.assets)[asset_id]
                         for holder, asset_id in world.custody if holder == actor)
        for actor, _ in world.skills | world.access | world.known
    }
    physical = frozenset(
        (actor, task) for actor, task in world.skills
        if TASK_TO_TOOL[task] in available_kinds.get(actor, frozenset())
    )
    admitted = physical & world.access
    visible = admitted & world.known
    return {"physical": physical, "admitted": admitted, "visible": visible}


def simulate(world: World, intervention: Intervention) -> World | None:
    """A pure model transition. A toy HOLD/REFUSE means no attempted mutation."""
    a = intervention
    if not a.admitted:
        return None
    if a.kind == "loan":
        if a.source == a.recipient or (a.source, a.subject) not in world.custody:
            return None
        return replace(world, custody=frozenset(
            (holder, asset) for holder, asset in world.custody
            if asset != a.subject
        ) | {(a.recipient, a.subject)})
    if a.kind == "teach":
        if (a.source, a.subject) not in world.skills or (
            a.recipient, a.subject
        ) in world.skills or a.source == a.recipient:
            return None
        # Learning a skill does not prove knowledge of site admission.
        return replace(world, skills=world.skills | {(a.recipient, a.subject)})
    if a.kind == "inform":
        if (a.source, a.subject) not in world.known or (
            a.recipient, a.subject
        ) in world.known or a.source == a.recipient:
            return None
        return replace(world, known=world.known | {(a.recipient, a.subject)})
    if a.kind == "mint":
        if (a.subject in dict(world.assets)
                or a.tool_kind not in TASK_TO_TOOL.values()):
            return None
        return replace(world,
                       assets=world.assets | {(a.subject, a.tool_kind)},
                       custody=world.custody | {(a.recipient, a.subject)})
    if a.kind == "grant":
        if a.subject not in TASK_TO_TOOL or (
            a.recipient, a.subject
        ) in world.access:
            return None
        return replace(world, access=world.access | {(a.recipient, a.subject)})
    raise AssertionError("validated kind was not handled")


def reached(world: World, goal: Goal) -> bool:
    return any(task == goal.task and (goal.actor is None or actor == goal.actor)
               for actor, task in options(world)[goal.scope])


def _losses(original: dict[str, frozenset[Key]],
            future: dict[str, frozenset[Key]]) -> dict[str, frozenset[Key]]:
    return {scope: original[scope] - future[scope] for scope in SCOPES}


def _keys(rows: frozenset[Key]) -> list[str]:
    return [actor + ":" + task for actor, task in sorted(rows)]


def _delta(original: dict[str, frozenset[Key]],
           future: dict[str, frozenset[Key]]) -> dict[str, dict[str, list[str]]]:
    return {scope: {
        "gained": _keys(future[scope] - original[scope]),
        "lost": _keys(original[scope] - future[scope]),
    } for scope in SCOPES}


def find_smallest_key(
    initial: World, interventions: tuple[Intervention, ...], goal: Goal,
    budget: int, max_steps: int = 3, max_states: int = 500
) -> dict[str, object]:
    """Bounded exhaustive uniform-cost search of only modeled, admitted moves.

    Returns HOLD rather than an optimality claim when the declared world search
    is truncated. Protect-existing is checked at EVERY intermediate cut.
    """
    if type(budget) is not int or budget < 0 or max_steps < 0 or max_states < 1:
        raise ValueError("invalid search bounds")
    if len({a.id for a in interventions}) != len(interventions):
        raise ValueError("duplicate intervention identities")
    original = options(initial)
    meta = {"schema": "motif.smallest-key/v0",
            "goal": {"task": goal.task, "scope": goal.scope, "actor": goal.actor,
                     "protect_existing": goal.protect_existing},
            "budget": budget, "max_steps": max_steps,
            "simulated_only": True}
    if reached(initial, goal):
        return {**meta, "status": "ALREADY_REACHABLE", "cost": 0,
                "actions": [], "opportunity_delta": _delta(original, original),
                "explored_states": 1, "truncated": False}

    frontier: list[tuple[int, int, tuple[str, ...], World]] = [
        (0, 0, (), initial)
    ]
    best_for_state: dict[World, tuple[int, int, tuple[str, ...]]] = {
        initial: (0, 0, ())
    }
    explored = 0
    candidates: list[tuple[int, int, tuple[str, ...], World]] = []
    truncated = False
    ordered = tuple(sorted(interventions, key=lambda a: a.id))
    while frontier:
        cost, steps, path, world = heappop(frontier)
        if (cost, steps, path) != best_for_state.get(world):
            continue
        explored += 1
        if explored > max_states:
            truncated = True
            break
        if reached(world, goal):
            candidates.append((cost, steps, path, world))
            continue
        if steps >= max_steps:
            continue
        for action in ordered:
            if not action.admitted or cost + action.cost > budget:
                continue
            after = simulate(world, action)
            if after is None or after == world:
                continue
            after_options = options(after)
            if goal.protect_existing:
                losses = _losses(original, after_options)
                # Protect both physical control and admitted/visible options.
                if any(losses[scope] for scope in SCOPES):
                    continue
            candidate = (cost + action.cost, steps + 1,
                         path + (action.id,))
            prior = best_for_state.get(after)
            if prior is None or candidate < prior:
                best_for_state[after] = candidate
                heappush(frontier, (*candidate, after))
    if truncated:
        return {**meta, "status": "HOLD_TRUNCATED", "actions": [],
                "cost": None, "opportunity_delta": None,
                "explored_states": explored, "truncated": True}
    if not candidates:
        return {**meta, "status": "ABSTAIN_NO_PATH", "actions": [],
                "cost": None, "opportunity_delta": None,
                "explored_states": explored, "truncated": False}
    # Explicit optimization: minimum declared cost; next fewer steps;
    # next more distinct visible options; finally stable ID ordering.
    winner = min(candidates, key=lambda x: (
        x[0], x[1], -len(options(x[3])["visible"] - original["visible"]), x[2]))
    cost, steps, path, world = winner
    final = options(world)
    return {**meta, "status": "PROPOSED_SYNTHETIC",
            "actions": list(path), "cost": cost, "steps": steps,
            "opportunity_delta": _delta(original, final),
            "explored_states": explored, "truncated": False}


def fixture() -> tuple[World, tuple[Intervention, ...]]:
    """Two actors: a quick loan opens a door but shuts Ben's existing door."""
    world = World(
        skills=frozenset({("ada", "well"), ("ben", "bike")}),
        custody=frozenset({("ben", "kit-1")}),
        assets=frozenset({("kit-1", "kit")}),
        access=frozenset({("ada", "well"), ("ben", "well"), ("ben", "bike")}),
        known=frozenset({("ada", "well"), ("ben", "bike")}),
    )
    actions = (
        Intervention("loan-kit", "loan", "ben", "ada", "kit-1", 1),
        Intervention("teach-ben-well", "teach", "ada", "ben", "well", 2),
        Intervention("tell-ben-well", "inform", "ada", "ben", "well", 1),
        Intervention("make-spare-kit", "mint", "maker", "ada", "kit-2", 4,
                     tool_kind="kit"),
        Intervention("blocked-gift", "mint", "maker", "ada", "kit-3", 1,
                     admitted=False, tool_kind="kit"),
    )
    return world, actions


def run_demo() -> dict[str, object]:
    world, actions = fixture()
    protected = find_smallest_key(
        world, actions, Goal("well", protect_existing=True), budget=4)
    unprotected = find_smallest_key(
        world, actions, Goal("well", protect_existing=False), budget=4)
    return {"experiment": "MOTIF-007", "world": "invented cooperative workshop",
            "baseline_opportunities": {
                scope: _keys(rows) for scope, rows in options(world).items()},
            "protected_plan": protected, "unprotected_plan": unprotected,
            "interpretation_limit": (
                "Declared finite search over supplied toy interventions; "
                "the model does not learn permission, ethical value, or causality. "
                "No plan was executed and no person was contacted."
            )}


if __name__ == "__main__":
    print(json.dumps(run_demo(), indent=2))
