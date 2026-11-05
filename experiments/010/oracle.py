"""MOTIF-010 independent synthetic intervention oracle.

SCIENTIST must never import this module. The evaluator uses the oracle to
apply explicit do(port_a=x,port_b=y) manipulations to newly constructed
synthetic graph worlds. No real action is possible.

The natural observation regime always has a == b. Therefore natural before /
after observations cannot distinguish several rival causal mechanisms. The
experimenter is allowed to manipulate two declared graph ports independently.

This establishes causation ONLY inside a deliberately programmed simulator.
"""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256

Fact = tuple[str, ...]
World = frozenset[Fact]
FAMILIES = ("source_a", "source_b", "both", "either", "exclusive", "equal")
SEEDS = (11, 23, 37, 41, 59, 67, 71, 83, 97, 101)
PROTOCOL = "synthetic-interventions-v1"


@dataclass(frozen=True)
class Observation:
    before: World
    observed_after: World
    roles: tuple[str, str]
    provenance: str
    # No oracle mechanism or answer bit is provided here.


@dataclass(frozen=True)
class PublicControls:
    first_port: str
    second_port: str
    # Types and allowed manipulation range are publicly exposed;
    # the function mapping settings to an outcome remains hidden.


@dataclass(frozen=True)
class SyntheticWorld:
    family: str
    seed: int
    controls: PublicControls
    # Evaluator-only record. Do not pass this object to the scientist.


def world(family: str, seed: int) -> SyntheticWorld:
    if family not in FAMILIES or type(seed) is not int or seed < 0:
        raise ValueError("Unknown synthetic hidden-rule world")
    def relation(port):
        return "q" + sha256(
            f"010:{PROTOCOL}:{family}:{seed}:{port}".encode()
        ).hexdigest()[:24]
    return SyntheticWorld(family, seed,
        PublicControls(relation("port0"), relation("port1")))


def _hidden_rule(family: str, first: bool, second: bool) -> bool:
    """This function is accessible only inside oracle/evaluator code."""
    if family == "source_a":
        return first
    if family == "source_b":
        return second
    if family == "both":
        return first and second
    if family == "either":
        return first or second
    if family == "exclusive":
        return first != second
    if family == "equal":
        return first == second
    raise ValueError("Unrecognized synthetic rule")


def _construct(spec: SyntheticWorld, first: bool, second: bool,
               serial: int, provenance: str) -> Observation:
    if type(first) is not bool or type(second) is not bool:
        raise ValueError("Controls must be explicit Boolean settings")
    if type(serial) is not int or serial < 0:
        raise ValueError("Invalid synthetic event serial")
    prefix = f"w{spec.seed}_{serial}_"
    actor, target = prefix + "actor", prefix + "target"
    facts = {
        ("role_actor", actor), ("role_target", target), ("pending", target),
    }
    if first:
        facts.add((spec.controls.first_port, actor))
    if second:
        facts.add((spec.controls.second_port, target))
    if _hidden_rule(spec.family, first, second):
        after = frozenset((facts - {("pending", target)}) | {("achieved", target)})
    else:
        after = frozenset(facts)
    return Observation(frozenset(facts), after, (actor, target), provenance)


def natural_observations(spec: SyntheticWorld) -> tuple[Observation, Observation]:
    """Exactly two unmanipulated but confounded observations.

    This is not a random sample: both input settings are equal by design.
    The two cases are identical across repeated calls for reproducibility.
    """
    return (_construct(spec, False, False, 1000, "SYNTHETIC_NATURAL"),
            _construct(spec, True, True, 1001, "SYNTHETIC_NATURAL"))


def intervene(spec: SyntheticWorld, first: bool, second: bool,
              serial: int) -> Observation:
    """An *on-demand* simulator operation, not a cached example lookup.

    Both controls are set explicitly (do-operator on a toy graph). This
    produces fresh entity identities and a newly computed observed outcome.
    An equal setting is still a controlled setting, albeit uninformative.
    """
    return _construct(spec, first, second, serial, "SYNTHETIC_INTERVENTION")


def test_world(spec: SyntheticWorld, serial=7000) -> tuple[Observation, ...]:
    """Evaluator-only complete two-control truth table for final scoring."""
    return tuple(intervene(spec, a, b, serial + 2*int(a) + int(b))
                 for a in (False, True) for b in (False, True))
