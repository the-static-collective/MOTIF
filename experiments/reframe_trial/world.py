"""Shared synthetic vocabulary and an owner-side outcome evaluator."""
from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "006"))
from composition import Call, F, Trace, Verb, World


# "bike" is the native 002/006 type tag for a synthetic resource slot.
# The scenario names change the framing, while the grammar is shared.
STEPS = (
    ("inspect", (), "examined"),
    ("release", ("examined", "reusable", "release_allowed"), "freed"),
    ("align", ("freed", "interface_fits"), "aligned"),
    ("couple", ("aligned", "join_allowed"), "coupled"),
    ("deliver", ("coupled", "delivery_allowed"), "delivered"),
    ("use_alternative", ("alternative_available", "delivery_allowed"), "delivered"),
)
COSTS = {name: 1 for name, _, _ in STEPS} | {"use_alternative": 9}
PRIMITIVES = {
    name: Verb(
        name,
        ("bike",),
        frozenset(F(requirement, "?0") for requirement in requirements),
        frozenset({F(effect, "?0")}),
        frozenset(),
        0,
    )
    for name, requirements, effect in STEPS
}
GOAL_VALUE = 14


@dataclass(frozen=True)
class Belief:
    facts: World
    weight: Fraction


@dataclass(frozen=True)
class Case:
    id: str
    family: str
    asset: str
    beliefs: tuple[Belief, ...]
    observable: tuple[str, ...]
    truth: World


def case(family, label, actual, *, release_allowed=True, alternative=True,
         interface_unknown=True, distractors=2):
    asset = f"{family}:{label}"
    facts = {F("bike", asset), F("join_allowed", asset),
             F("delivery_allowed", asset)}
    if release_allowed:
        facts.add(F("release_allowed", asset))
    if alternative:
        facts.add(F("alternative_available", asset))
    for i in range(distractors):
        facts.add(F("bike", f"{asset}:decoy:{i}"))

    unknown = {"cosmetic_mark": Fraction(1, 2), "reusable": Fraction(3, 4)}
    if interface_unknown:
        unknown["interface_fits"] = Fraction(3, 4)
    else:
        facts.add(F("interface_fits", asset))
    observable = tuple(sorted(unknown))
    beliefs = []
    for choices in product((False, True), repeat=len(observable)):
        possible = set(facts)
        weight = Fraction(1)
        for name, present in zip(observable, choices, strict=True):
            weight *= unknown[name] if present else 1 - unknown[name]
            if present:
                possible.add(F(name, asset))
        beliefs.append(Belief(frozenset(possible), weight))

    if set(actual) - set(observable):
        raise ValueError("Owner truth contains an undeclared observation")
    truth = frozenset(facts | {F(name, asset) for name in actual})
    return Case(asset, family, asset, tuple(beliefs), observable, truth)


def witness(before, primitive_calls, goal):
    """Owner-side stepwise evaluator, independent of native macro replay."""
    known = set(before)
    spent = 0
    for call in primitive_calls:
        if call.operator not in COSTS or len(call.roles) != 1:
            raise ValueError("Unknown primitive or malformed binding")
        subject, = call.roles
        if ("bike", subject) not in known:
            raise ValueError("Undeclared resource")
        _, requirements, effect = next(row for row in STEPS if row[0] == call.operator)
        if any((name, subject) not in known for name in requirements):
            raise ValueError("Owner refused primitive: " + call.operator)
        new_fact = (effect, subject)
        if new_fact in known:
            raise ValueError("Duplicate effect")
        known.add(new_fact)
        spent += COSTS[call.operator]
    return frozenset(known), spent, goal in known


def demo_traces(family, phase):
    """Generate two source-separated, synthetic demonstrations per phase."""
    recipe = ("inspect", "release") if phase == 1 else ("align", "couple")
    traces = []
    for i in range(2):
        demo = case(family, f"demo-{phase}-{i}", ("reusable", "interface_fits"))
        before = demo.truth
        if phase == 2:
            before |= {F("examined", demo.asset), F("freed", demo.asset)}
        calls = tuple(Call(name, (demo.asset,)) for name in recipe)
        after, _, _ = witness(before, calls, F("delivered", demo.asset))
        traces.append(Trace(before, calls, after))
    return traces


def cohort():
    """The pilot author supplied every task and outcome law."""
    return (
        case("tabletop", "surface-label", ("reusable",), interface_unknown=False),
        case("tabletop", "looks-reusable", (), interface_unknown=False),
        case("handoff", "parallel-route", ("reusable", "interface_fits")),
        case("handoff", "interface-changed", ("reusable",)),
        case("handoff", "approval-denied", ("reusable", "interface_fits"),
             release_allowed=False),
        case("interactive", "joint-probe", ("reusable", "interface_fits")),
        case("interactive", "wrong-mechanism", ("interface_fits",)),
        case("interactive", "no-authorized-route", (), release_allowed=False,
             alternative=False),
    )
