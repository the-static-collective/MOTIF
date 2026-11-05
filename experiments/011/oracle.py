"""MOTIF-011: independent, synthetic oracle with models outside the grammar.

Only benchmark.py and tests import this file. skeptic.py never learns which
mechanism generated the snapshots. This is a procedural counterexample lab,
NOT physical evidence, a safety-tested intervention system or an LLM.

A third relation may be visible but absent from the learner's two-control
grammar, truly hidden, or duplicated by a perfect confounding proxy. A
separate fixture flips labels to mimic noisy/unstable observations. The
simulator cannot distinguish hidden causes from measurement noise by itself.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

FAMILIES = ("clean_two", "visible_third", "hidden_third",
            "noisy_flip", "ambiguous_proxy", "restricted_clean")
SEEDS = (11, 23, 37, 41, 59)
SPLITS = ("train", "validation", "local_review", "test")
VERSION = "motif-011-synthetic-skeptic-v1"
CONTROL_PAIRS = ((False, False), (False, True), (True, False), (True, True))


@dataclass(frozen=True)
class PublicControls:
    first_port: str
    second_port: str


@dataclass(frozen=True)
class World:
    family: str
    seed: int
    controls: PublicControls
    third_relation: str
    proxy_relation: str
    nuisance_relation: str
    # Evaluator only: NEVER pass this object to the learner.


@dataclass(frozen=True)
class Observation:
    before: frozenset[tuple[str, ...]]
    observed_after: frozenset[tuple[str, ...]]
    roles: tuple[str, str]
    provenance: str = "SYNTHETIC_INTERVENTION"


def make_world(family: str, seed: int) -> World:
    if family not in FAMILIES or type(seed) is not int or seed < 0:
        raise ValueError("Unknown synthetic world")
    def token(slot: str) -> str:
        return "q" + sha256(f"{VERSION}:{family}:{seed}:{slot}".encode()
                            ).hexdigest()[:24]
    return World(family, seed,
                 PublicControls(token("a"), token("b")),
                 token("third"), token("proxy"), token("nuisance"))


def observed_case(spec: World, first: bool, second: bool,
                  third: bool, repeat: int, split_name: str,
                  sequence: int) -> Observation:
    """A fresh graph, with label determined by the evaluator-only mechanism.

    The third bit is deliberately NOT part of the public intervention schema.
    In invisible cases it is omitted from the before graph entirely.
    """
    if any(type(x) is not bool for x in (first, second, third)):
        raise ValueError("Experiment flags must be Boolean")
    if split_name not in SPLITS or repeat not in (0, 1):
        raise ValueError("Unregistered observation slot")
    actor = f"{spec.seed}_{split_name}_{sequence}_actor"
    target = f"{spec.seed}_{split_name}_{sequence}_target"
    facts = {("role_actor", actor), ("role_target", target),
             ("pending", target)}
    if first:
        facts.add((spec.controls.first_port, actor))
    if second:
        facts.add((spec.controls.second_port, target))
    # A nuisance feature always duplicates the *known first port*.
    # It cannot resolve a two-port contradiction by itself.
    if first:
        facts.add((spec.nuisance_relation, actor))
    if spec.family in ("visible_third", "ambiguous_proxy") and third:
        facts.add((spec.third_relation, actor))
        if spec.family == "ambiguous_proxy":
            facts.add((spec.proxy_relation, target))
    if spec.family in ("visible_third", "ambiguous_proxy"):
        effect = bool(first ^ second ^ third)
    elif spec.family == "hidden_third":
        effect = bool(first ^ second ^ (repeat == 1))
    elif spec.family == "noisy_flip":
        # Deliberately periodic synthetic label-flip fixture, NOT evidence
        # that the learner can detect real stochastic noise.
        effect = bool(first ^ second ^ (repeat == 1))
    else:
        effect = bool(first ^ second)
    before = frozenset(facts)
    after = (frozenset((facts - {("pending", target)}) |
                       {("achieved", target)}) if effect else before)
    return Observation(before, after, (actor, target))


def episodes(spec: World, split_name: str) -> tuple[Observation, ...]:
    """Complete balanced factorial splits, 16 source snapshots per split.

    Eight (A,B,C) cells are repeated twice with new entity identities.
    The serial identities and evaluation splits do not overlap.
    """
    if split_name not in SPLITS:
        raise ValueError("Unknown split")
    output = []
    for a,b in CONTROL_PAIRS:
        for c in (False, True):
            for rep in (0, 1):
                index = len(output)
                output.append(observed_case(spec, a,b,c,rep,split_name,index))
    return tuple(output)


def safe_policy_fixture(spec: World):
    """Synthetic governance policy for a cost-constrained experiment.

    Only the diagonal control settings are admissible. The off-diagonal
    settings are prohibited even if they promise high information gain.
    """
    return {
        "allowed": frozenset(((False, False), (True, True))),
        "costs": {pair: 1 if pair[0] == pair[1] else 5
                  for pair in CONTROL_PAIRS},
        "budget": 2,
        "reason": "SYNTHETIC_LOCAL_POLICY_FIXTURE"
    }
