"""MOTIF-002: experimental discovery of unnamed graph transformations.

Learns reusable symbolic graph edits from synthetic before/after pairs, with
neither action labels nor hand-specified action roles. A tiny controlled test,
not causal identification, a neural model, a real consent system, or an agent.
Python 3.10+, standard library only.
"""
from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from hashlib import sha256
from itertools import product
import json
from typing import FrozenSet

Fact = tuple[str, ...]
World = FrozenSet[Fact]
TYPES = frozenset({"person", "bike"})  # Explicit domain ontology; not learned.


def F(relation: str, *args: str) -> Fact:
    return (relation, *args)


@dataclass(frozen=True)
class Transition:
    before: World
    after: World
    provenance: str = "SYNTHETIC"


@dataclass(frozen=True)
class Verb:
    id: str
    role_types: tuple[str, ...]
    requires: World
    adds: World
    removes: World
    demonstrations: int

    def data(self) -> dict:
        return dict(id=self.id, role_types=self.role_types,
                    requires=sorted(self.requires), adds=sorted(self.adds),
                    removes=sorted(self.removes),
                    demonstrations=self.demonstrations)


def declared_entities(world: World) -> dict[str, str]:
    """Read only explicitly typed entities; remaining tokens are constants."""
    result = {}
    for fact in sorted(world):
        if len(fact) == 2 and fact[0] in TYPES:
            if fact[1] in result and result[fact[1]] != fact[0]:
                raise ValueError("Ambiguous type declaration")
            result[fact[1]] = fact[0]
    return result


def normalized(episode: Transition) -> tuple:
    if episode.provenance != "SYNTHETIC":
        raise ValueError("MOTIF-002 trains only on declared synthetic fixtures")
    before, after = episode.before, episode.after
    adds, removes = after - before, before - after
    if not adds and not removes:
        return ()
    types = declared_entities(before | after)
    changed = sorted(adds | removes)
    touched = []
    for fact in changed:
        for item in fact[1:]:
            if item in types and item not in touched:
                touched.append(item)
    if len(touched) != 1:
        # Current experiment is intentionally limited to one changed entity.
        return ()

    # Select a bounded local field, then infer roles from its topology.
    neighborhood, reached = set(), set(touched)
    for _ in range(2):
        frontier = set(reached)
        for fact in sorted(before):
            if any(item in frontier for item in fact[1:] if item in types):
                neighborhood.add(fact)
                reached.update(item for item in fact[1:] if item in types)

    roles = touched[:]
    # Traverse predicate names and edge positions, never entity spellings.
    for _ in range(len(reached)):
        for fact in sorted(neighborhood):
            if not any(item in roles for item in fact[1:]):
                continue
            for item in fact[1:]:
                if item in types and item not in roles:
                    roles.append(item)
    if set(roles) != reached:
        return ()
    mapping = {item: f"?{i}" for i, item in enumerate(roles)}

    def norm(facts):
        return frozenset(tuple(mapping.get(token, token) for token in fact)
                         for fact in facts)

    return (tuple(types[item] for item in roles), norm(neighborhood),
            norm(adds), norm(removes))


def induce(episodes: list[Transition], min_support: int = 2) -> dict[str, Verb]:
    """Discover graph-rewrite *schemas*, not their names or their causes.

    A schema groups identical normalized edit signatures and intersects the
    context seen before each change. Simulated permission is a hard gate:
    absent permission patterns can never be inferred from a successful edit.
    """
    grouped = defaultdict(list)
    for episode in episodes:
        row = normalized(episode)
        if row:
            role_types, context, adds, removes = row
            grouped[(role_types, adds, removes)].append(context)
    result = {}
    for (role_types, adds, removes), contexts in grouped.items():
        if len(contexts) < min_support:
            continue
        requires = frozenset.intersection(*contexts)
        # Synthetic permission has to be an explicit *required* fact.
        if not any(f[0] == "permits" for f in requires):
            continue
        signature = json.dumps([role_types, sorted(requires),
                                sorted(adds), sorted(removes)], separators=(",", ":"))
        name = "verb-" + sha256(signature.encode()).hexdigest()[:12]
        result[name] = Verb(name, role_types, requires, adds,
                            removes, len(contexts))
    return result


def ground(fact: Fact, roles: tuple[str, ...]) -> Fact:
    return tuple(roles[int(token[1:])] if token.startswith("?")
                 and token[1:].isdigit() else token for token in fact)


def possibilities(world: World, verbs: dict[str, Verb]):
    """Yield synthetic counterfactuals, never outward actions."""
    types = declared_entities(world)
    for verb in sorted(verbs.values(), key=lambda v: v.id):
        buckets = [sorted(k for k, t in types.items() if t == kind)
                   for kind in verb.role_types]
        for roles in product(*buckets):
            if not {ground(f, roles) for f in verb.requires}.issubset(world):
                continue
            after = (world - {ground(f, roles) for f in verb.removes}) | {
                ground(f, roles) for f in verb.adds}
            if after != world:
                yield verb.id, roles, frozenset(after)


def utility(world: World, initial: World) -> int:
    """Declared synthetic objective. Never an inferred universal value."""
    return 10 * len({f for f in world - initial if f[0] == "usable"}) + \
           4 * len({f for f in world - initial if f[0] == "skill"})


def explore(initial: World, verbs: dict[str, Verb], steps: int = 3) -> dict:
    queue = deque([(initial, ())])
    visited = {initial}
    best_world, best_path = initial, ()
    explored = 0
    while queue:
        world, path = queue.popleft()
        explored += 1
        if (utility(world, initial), -len(path)) > (
                utility(best_world, initial), -len(best_path)):
            best_world, best_path = world, path
        if len(path) >= steps:
            continue
        for verb, roles, following in possibilities(world, verbs):
            if following not in visited:
                visited.add(following)
                queue.append((following, path + ((verb, roles),)))
    return dict(score=utility(best_world, initial), path=best_path,
                final=best_world, explored=explored, reachable=len(visited))


def demo(before: set[Fact], remove: set[Fact], add: set[Fact]) -> Transition:
    return Transition(frozenset(before), frozenset((before - remove) | add))


def lessons() -> list[Transition]:
    data = []
    for owner, helper, bike, flavor in [
        ("Ava", "Bo", "cycleA", "music"),
        ("Dee", "Em", "cycleB", "gardens"),
        ("Fin", "Gil", "cycleC", "weather"),
    ]:
        prior = {F("person", owner), F("person", helper), F("bike", bike),
                 F("owns", owner, bike), F("broken", bike),
                 F("skill", helper, "repair"), F("tool", helper, "wrench"),
                 F("permits", owner, helper, bike), F("likes", owner, flavor)}
        data.append(demo(prior, {F("broken", bike)}, {F("usable", bike)}))
    for teacher, novice, flavor in [
        ("Bo", "Ava", "tea"), ("Em", "Dee", "coffee"),
        ("Gil", "Fin", "soup")
    ]:
        prior = {F("person", teacher), F("person", novice),
                 F("skill", teacher, "repair"),
                 F("permits", novice, teacher, "teaching"),
                 F("likes", novice, flavor)}
        data.append(demo(prior, set(), {F("skill", novice, "repair")}))
    return data


def scene(permissions: bool = True, tools: bool = True) -> World:
    facts = {F("person", "Jo"), F("person", "Mira"),
             F("bike", "bike1"), F("bike", "bike2"),
             F("owns", "Jo", "bike1"), F("owns", "Jo", "bike2"),
             F("broken", "bike1"), F("broken", "bike2"),
             F("skill", "Mira", "repair")}
    if tools:
        facts |= {F("tool", "Jo", "wrench"), F("tool", "Mira", "wrench")}
    if permissions:
        facts |= {F("permits", "Jo", "Mira", "bike1"),
                  F("permits", "Jo", "Mira", "teaching"),
                  F("permits", "Jo", "Jo", "bike2")}
    return frozenset(facts)


def report() -> dict:
    verbs = induce(lessons())
    plan = explore(scene(), verbs)
    held = explore(scene(permissions=False), verbs)
    assert len(verbs) == 2, verbs
    assert len(plan["path"]) == 3, plan
    assert {F("usable", "bike1"), F("usable", "bike2"),
            F("skill", "Jo", "repair")}.issubset(plan["final"])
    assert not held["path"]
    return {"experiment": "MOTIF-002", "status": "synthetic, label-free symbolic induction",
            "training_pairs": len(lessons()), "learned_verbs": [v.data() for v in verbs.values()],
            "counterfactual_plan": [{"anonymous_verb": v, "roles": r}
                                    for v, r in plan["path"]],
            "score": plan["score"], "states_explored": plan["explored"],
            "reachable_worlds": plan["reachable"],
            "permission_ablation": {"plan": held["path"],
                                    "reachable_worlds": held["reachable"]}}


if __name__ == "__main__":
    print(json.dumps(report(), indent=2))
