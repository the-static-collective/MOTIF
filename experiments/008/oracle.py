"""MOTIF-008 hidden-rule synthetic world generator.

Only the evaluation harness imports this module. The learner receives immutable
before/after relational observations with actor and target role bindings; it
never receives a family name, rule implementation, hidden flags or test labels.

This is not a physical simulator, secure sandbox, calibrated world model, or
a claim of actual action/consent. All examples and actions are SYNTHETIC.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from random import Random
from typing import FrozenSet

Fact = tuple[str, ...]
World = FrozenSet[Fact]

FAMILIES = ("direct", "forward_join", "reverse_join", "conjunction",
            "hybrid", "xor")
SUPPORTED = frozenset(FAMILIES) - {"xor"}
KEYS = ("direct", "forward", "reverse", "permit", "prepared", "noise1", "noise2")
COUNTS = {"train": 48, "validation": 24, "test": 80}
SPLIT_SEEDS = {"train": 300_000, "validation": 600_000, "test": 900_000}


@dataclass(frozen=True)
class Episode:
    before: World
    observed_after: World
    roles: tuple[str, str]
    provenance: str = "SYNTHETIC_ORACLE"
    # Only a public role binding, not the hidden attempted-action rule.


@dataclass(frozen=True)
class WorldSpec:
    family: str
    seed: int
    vocabulary: tuple[str, ...]
    # This entire object remains on the oracle/evaluator side.


@dataclass(frozen=True)
class Trial:
    family: str
    spec_seed: int
    train: tuple[Episode, ...]
    validation: tuple[Episode, ...]
    test: tuple[Episode, ...]


def spec_for(family: str, seed: int) -> WorldSpec:
    if family not in FAMILIES or not isinstance(seed, int) or seed < 0:
        raise ValueError("Unknown or invalid synthetic world")
    # A digest namespace per (family, seed) prevents accidental repeated
    # source predicate names among distinct worlds in this finite benchmark.
    # Earlier v1 sampling seven names from a shared 2000-name list did NOT
    # guarantee disjoint vocabulary, so this is an explicit method correction.
    namespace = sha256(f"spec:v2:{family}:{seed}".encode()).hexdigest()
    vocabulary = tuple("q" + sha256(
        f"{namespace}:{index}".encode()).hexdigest()[:24]
        for index in range(len(KEYS)))
    return WorldSpec(family, seed, vocabulary)


def hidden_rule(spec: WorldSpec, hidden_flags: dict[str, bool]) -> bool:
    """Private rule oracle, used only for generating labeled observations."""
    f = hidden_flags
    if spec.family == "direct":
        return f["direct"]
    if spec.family == "forward_join":
        return f["forward"]
    if spec.family == "reverse_join":
        return f["reverse"]
    if spec.family == "conjunction":
        return f["permit"] and f["prepared"]
    if spec.family == "hybrid":
        return f["forward"] and f["permit"]
    if spec.family == "xor":
        return f["permit"] != f["prepared"]
    raise ValueError("Unknown world family")


def make_episode(spec: WorldSpec, case_number: int,
                 flags: dict[str, bool] | None = None) -> Episode:
    if case_number < 0:
        raise ValueError("Case must be nonnegative")
    rng = Random(int.from_bytes(sha256(
        f"case:v1:{spec.family}:{spec.seed}:{case_number}".encode()
    ).digest()[:8], "big"))
    chosen = {key: bool(rng.getrandbits(1)) for key in KEYS}
    if flags is not None:
        if set(flags) != set(KEYS):
            raise ValueError("Intervention must specify every synthetic flag")
        chosen = dict(flags)
    # Names never overlap between cases or worlds, including the mediator IDs.
    prefix = f"d{spec.seed}_{case_number}_"
    actor, target = prefix + "agent", prefix + "object"
    other_actor, other_target = prefix + "decoy_agent", prefix + "decoy_object"
    p0, p1, p2, p3 = (prefix + f"intermediate_{i}" for i in range(4))
    d, f, r, permit, prepared, noise1, noise2 = spec.vocabulary
    facts = {
        ("role_actor", actor), ("role_target", target),
        ("pending", target),
        (d, actor, target if chosen["direct"] else other_target),
        (d, other_actor, target if not chosen["direct"] else other_target),
        (f, actor, p0), (f, p0 if chosen["forward"] else p1, target),
        (r, target, p2), (r, p2 if chosen["reverse"] else p3, actor),
        (permit, actor if chosen["permit"] else other_actor),
        (prepared, target if chosen["prepared"] else other_target),
        (noise1, actor if chosen["noise1"] else other_actor),
        (noise2, target if chosen["noise2"] else other_target),
    }
    # Both halves of each path always exist, independently of whether they
    # actually meet at the *same* intermediate node.
    good = hidden_rule(spec, chosen)
    after = frozenset(
        (facts - {("pending", target)}) | {("achieved", target)}
    ) if good else frozenset(facts)
    return Episode(frozenset(facts), after, (actor, target))


def split(spec: WorldSpec, name: str, count: int | None = None):
    if name not in COUNTS:
        raise ValueError("Unrecognized split")
    n = COUNTS[name] if count is None else count
    if not isinstance(n, int) or n < 1 or n > 2000:
        raise ValueError("Invalid world sample budget")
    return tuple(make_episode(spec, spec.seed * 1000000
                              + SPLIT_SEEDS[name] + i) for i in range(n))


def trial(family: str, seed: int, counts: dict[str, int] | None = None) -> Trial:
    spec = spec_for(family, seed)
    budget = COUNTS if counts is None else counts
    if set(budget) != set(COUNTS):
        raise ValueError("All split budgets must be explicit")
    return Trial(family, seed,
                 split(spec, "train", budget["train"]),
                 split(spec, "validation", budget["validation"]),
                 split(spec, "test", budget["test"]))


def paired_intervention(family: str, seed: int, case_number=710123):
    """Change only one source edge endpoint; hold other six flags fixed.

    A structural counterfactual in a PROGRAMMED oracle, not evidence that the
    learned model has discovered an intervention in the physical world.
    """
    if family not in ("forward_join", "reverse_join"):
        raise ValueError("This paired experiment is defined for join families")
    spec = spec_for(family, seed)
    fixed = {x: False for x in KEYS}
    label = "forward" if family == "forward_join" else "reverse"
    true_flags, false_flags = dict(fixed), dict(fixed)
    true_flags[label] = True
    success = make_episode(spec, case_number, true_flags)
    failure = make_episode(spec, case_number, false_flags)
    changed = success.before ^ failure.before
    if len(changed) != 2:
        raise AssertionError("Paired intervention did not rewire exactly one fact")
    if success.observed_after == success.before:
        raise AssertionError("Positive intervention did not change outcome")
    if failure.observed_after != failure.before:
        raise AssertionError("Negative intervention wrongly changed outcome")
    return success, failure
