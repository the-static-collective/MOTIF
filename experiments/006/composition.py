"""MOTIF-006 — The composite verb.

Induce reusable, typed, role-relative macro-operators from repeated synthetic
action traces. A macro compresses *planning representation*, not real execution.
Every primitive transition is replayed against independently pinned sources and
all preconditions are checked again (including fictional 'permits' relations).
No neural weights, autonomous tool building, consent proof, or external actions.
Python 3.10+ standard library.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, replace
from hashlib import sha256
from itertools import product
from pathlib import Path
from typing import Union
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "002"))
from motif002 import F, Verb, World, Fact, induce, lessons, scene, explore, \
                     declared_entities, ground, utility


class Inapplicable(ValueError):
    """A proposed synthetic transformation is not admitted into this field."""


@dataclass(frozen=True)
class Call:
    operator: str
    roles: tuple[str, ...]


@dataclass(frozen=True)
class Trace:
    before: World
    calls: tuple[Call, ...]
    observed_after: World
    provenance: str = "SYNTHETIC_TRACE"


@dataclass(frozen=True)
class Macro:
    id: str
    role_types: tuple[str, ...]
    calls: tuple[Call, ...]           # Internally abstract, e.g. ?0, ?1.
    requires: World
    adds: World
    removes: World
    pins: tuple[tuple[str, str], ...]
    demonstrations: int
    depth: int
    status: str = "CANDIDATE_ONLY"


Operator = Union[Verb, Macro]


def signature(op: Operator) -> str:
    """Fingerprint actual operator semantics; IDs alone cannot pin a source."""
    if isinstance(op, Verb):
        obj = ("primitive", op.role_types, sorted(op.requires),
               sorted(op.adds), sorted(op.removes))
    else:
        obj = ("composite", op.role_types,
               [(call.operator, call.roles) for call in op.calls],
               sorted(op.requires), sorted(op.adds), sorted(op.removes),
               op.pins)
    return sha256(json.dumps(obj, separators=(",", ":")).encode()).hexdigest()


def assert_types(world: World, role_types: tuple[str, ...],
                 role_values: tuple[str, ...]):
    known = declared_entities(world)
    if len(role_types) != len(role_values):
        raise Inapplicable("Wrong number of typed roles")
    for kind, name in zip(role_types, role_values):
        if known.get(name) != kind:
            raise Inapplicable("Undeclared or mismatched role type")


def checked_apply(world: World, operator: str, roles: tuple[str, ...],
                  catalog: dict[str, Operator], ancestors=frozenset()) -> World:
    """Deterministic replay ONLY; recursively rechecks all primitive guards."""
    if operator not in catalog:
        raise Inapplicable("Operator unavailable in pinned catalog")
    if operator in ancestors:
        raise Inapplicable("Recursive dependency cycle")
    op = catalog[operator]
    assert_types(world, op.role_types, roles)
    if isinstance(op, Verb):
        required = {ground(f, roles) for f in op.requires}
        if not required.issubset(world):
            raise Inapplicable("Primitive preconditions (incl. simulated permissions) absent")
        following = frozenset((world - {ground(f, roles) for f in op.removes}) |
                              {ground(f, roles) for f in op.adds})
        if following == world:
            raise Inapplicable("No-op cannot count as successful edit")
        return following
    if op.status != "CANDIDATE_ONLY":
        raise Inapplicable("Unrecognized macro status")
    for dep_id, expected in op.pins:
        dep = catalog.get(dep_id)
        if dep is None or signature(dep) != expected:
            raise Inapplicable("Source operator changed since candidate induction")
    # No authority exists in a macro envelope: inspect every component.
    current = world
    for call in op.calls:
        bindings = tuple(roles[int(token[1:])] for token in call.roles)
        current = checked_apply(current, call.operator, bindings, catalog,
                                ancestors | {operator})
    # Independently compare the advertised net effect with the checked replay.
    advertised = frozenset((world - {ground(f, roles) for f in op.removes}) |
                           {ground(f, roles) for f in op.adds})
    if advertised != current:
        raise Inapplicable("Macro claims effects not reproduced by source replay")
    return current


def replay(world: World, calls: tuple[Call, ...],
           catalog: dict[str, Operator]) -> World:
    current = world
    for call in calls:
        current = checked_apply(current, call.operator, call.roles, catalog)
    return current


def compile_trace(trace: Trace, catalog: dict[str, Operator],
                  max_expanded_steps=8) -> Macro:
    """Compile one verified synthetic trace into a candidate macro.

    All identifiers are abstracted in first-role-appearance order, preserving
    cross-step shared roles and aliasing. Primitive rules are regressed into a
    source-checkable outer precondition and net graph delta.
    """
    if trace.provenance != "SYNTHETIC_TRACE" or len(trace.calls) < 2:
        raise ValueError("Only multi-step synthetic traces can be compiled")
    if replay(trace.before, trace.calls, catalog) != trace.observed_after:
        raise ValueError("Independent synthetic outcome disagrees with replay")

    known = declared_entities(trace.before)
    abstract: dict[str, str] = {}
    role_types = []
    norm_calls = []
    dependencies = {}
    expanded_steps = 0
    for call in trace.calls:
        op = catalog[call.operator]
        expanded_steps += op.depth if isinstance(op, Macro) else 1
        if expanded_steps > max_expanded_steps:
            raise ValueError("Expanded program exceeds declared budget")
        assert_types(trace.before, op.role_types, call.roles)
        values = []
        for value in call.roles:
            if value not in abstract:
                abstract[value] = f"?{len(abstract)}"
                role_types.append(known[value])
            values.append(abstract[value])
        norm_calls.append(Call(call.operator, tuple(values)))
        dependencies[call.operator] = signature(op)
    required: set[Fact] = set()
    adds: set[Fact] = set()
    removes: set[Fact] = set()
    for call in norm_calls:
        op = catalog[call.operator]
        # Ground operator's internal ?slots into the macro's abstract ?slots.
        needs = {ground(f, call.roles) for f in op.requires}
        a = {ground(f, call.roles) for f in op.adds}
        d = {ground(f, call.roles) for f in op.removes}
        required |= needs - adds
        adds -= d
        removes -= a
        adds |= a
        removes |= d
    # A macro is not an atomic physical action; this summary is checked on
    # every replay and every underlying primitive is independently admitted.
    spec = (tuple(role_types),
            tuple((c.operator, c.roles) for c in norm_calls),
            tuple(sorted(required)), tuple(sorted(adds)), tuple(sorted(removes)),
            tuple(sorted(dependencies.items())))
    identifier = "macro-" + sha256(json.dumps(
        spec, separators=(",", ":")).encode()).hexdigest()[:16]
    return Macro(identifier, tuple(role_types), tuple(norm_calls),
                 frozenset(required), frozenset(adds), frozenset(removes),
                 tuple(sorted(dependencies.items())), 1, expanded_steps)


def induce_macros(traces: list[Trace], catalog: dict[str, Operator],
                  min_support=2, max_expanded_steps=8) -> dict[str, Macro]:
    """Count independently valid trace instances; do not trust claimed effects."""
    if min_support < 2:
        raise ValueError("Need at least two synthetic demonstrations")
    groups = defaultdict(list)
    for trace in traces:
        candidate = compile_trace(trace, catalog, max_expanded_steps)
        groups[candidate.id].append(candidate)
    return {key: replace(candidates[0], demonstrations=len(candidates))
            for key, candidates in sorted(groups.items())
            if len(candidates) >= min_support}


def available_macros(world: World, catalog: dict[str, Operator],
                     macro_ids: tuple[str, ...], max_groundings=500):
    """Enumerate hypothetical candidates; all replay subguards are tested."""
    if max_groundings < 1:
        raise ValueError("Grounding budget must be positive")
    known = declared_entities(world)
    tested = 0
    for name in sorted(macro_ids):
        op = catalog.get(name)
        if not isinstance(op, Macro):
            continue
        buckets = [tuple(sorted(key for key, kind in known.items() if kind == typ))
                   for typ in op.role_types]
        for roles in product(*buckets):
            if len(set(roles)) != len(roles):
                continue  # A single macro variable cannot denote two roles.
            tested += 1
            if tested > max_groundings:
                raise ValueError("Macro grounding cap reached; do not claim completeness")
            try:
                future = checked_apply(world, name, tuple(roles), catalog)
            except Inapplicable:
                continue
            yield Call(name, tuple(roles)), future


def rename_world(world: World, mapping: dict[str, str]) -> World:
    """Synthetic identifier-renaming only. Preserve predicates/constants."""
    return frozenset(tuple([f[0]] + [mapping.get(x, x) for x in f[1:]])
                     for f in world)


def rename_trace(trace: Trace, mapping: dict[str, str]) -> Trace:
    return Trace(rename_world(trace.before, mapping),
                 tuple(Call(x.operator, tuple(mapping.get(v, v) for v in x.roles))
                       for x in trace.calls),
                 rename_world(trace.observed_after, mapping),
                 trace.provenance)


def root_trace(verbs: dict[str, Verb]) -> Trace:
    world = scene()
    plan = explore(world, verbs)
    calls = tuple(Call(op, tuple(roles)) for op, roles in plan["path"])
    if len(calls) != 3:
        raise ValueError("Existing 002 fixture must yield a three-step trace")
    return Trace(world, calls, replay(world, calls, verbs))


def training_traces(verbs: dict[str, Verb], count=3) -> list[Trace]:
    """Renamed copies of one synthetic planner demonstration, not field data."""
    seed = root_trace(verbs)
    return [rename_trace(seed, {"Jo": f"Owner_{i}", "Mira": f"Helper_{i}",
                                "bike1": f"bikeA_{i}", "bike2": f"bikeB_{i}"})
            for i in range(count)]


def bind_prefix(prefix: tuple[Call, ...]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(role for call in prefix for role in call.roles))


def two_level_training(verbs: dict[str, Verb]):
    """Learn macro A then use A as a constituent of macro B.

    Neither operator's body is hard-coded: it is abstracted from traces
    produced by the original MOTIF-002 planner.
    """
    first = training_traces(verbs)
    partial = [Trace(t.before, t.calls[:2],
                     replay(t.before, t.calls[:2], verbs)) for t in first]
    level1 = induce_macros(partial, verbs, min_support=2)
    if len(level1) != 1:
        raise ValueError("Expected a unique training macro, not a forced selection")
    macro1 = next(iter(level1.values()))
    second_catalog = dict(verbs, **level1)
    nested = [
        Trace(t.before,
              (Call(macro1.id, bind_prefix(t.calls[:2])), t.calls[2]),
              t.observed_after)
        for t in first
    ]
    level2 = induce_macros(nested, second_catalog, min_support=2)
    if len(level2) != 1:
        raise ValueError("Failed to induct nested macros")
    return first, macro1, next(iter(level2.values()))


def run_demo() -> dict:
    verbs = induce(lessons())
    seed, macro1, macro2 = two_level_training(verbs)
    catalog: dict[str, Operator] = dict(verbs)
    catalog[macro1.id] = macro1
    catalog[macro2.id] = macro2
    unseen = rename_trace(root_trace(verbs),
                          {"Jo":"UnknownOwner", "Mira":"UnknownHelper",
                           "bike1":"unseen_A", "bike2":"unseen_B"})
    final = checked_apply(unseen.before, macro2.id,
                          bind_prefix(unseen.calls), catalog)
    primitive = replay(unseen.before, unseen.calls, verbs)
    blocked_world = frozenset(f for f in unseen.before if f[0] != "permits")
    try:
        checked_apply(blocked_world, macro2.id, bind_prefix(unseen.calls), catalog)
        blocked = False
    except Inapplicable:
        blocked = True
    return {
        "experiment": "MOTIF-006", "scope": "synthetic graph simulation ONLY",
        "training_traces": len(seed), "two_level_macros": 2,
        "first_macro": {"id": macro1.id, "expanded_steps": macro1.depth,
                        "support": macro1.demonstrations},
        "nested_macro": {"id": macro2.id, "expanded_steps": macro2.depth,
                         "support": macro2.demonstrations},
        "holdout_new_entity_ids": True,
        "macro_equals_primitive_replay": final == primitive,
        "simulated_goal_utility": utility(final, unseen.before),
        "single_macro_invocation": 1,
        "underlying_primitive_transitions": macro2.depth,
        "missing_permission_fixture_blocks": blocked,
        "original_world_unchanged": F("usable", "unseen_A") not in unseen.before
    }


if __name__ == "__main__":
    print(json.dumps(run_demo(), indent=2))
