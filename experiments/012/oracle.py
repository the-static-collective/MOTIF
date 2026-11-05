"""MOTIF-012 independent synthetic causal-counterfactual oracle.

This file is for the EVALUATOR only; cartographer.py never imports it.

Two opaque visible predicates C and P are *perfectly correlated* in natural
observations. Six deliberately related hidden mechanisms agree on that
observational data, but can disagree when an isolated synthetic intervention
sets C and P independently. Some evaluation worlds hide a third contextual
input or flip intervention outcomes using a deterministic hash.

No real-world causal conclusion, sensor, human experiment or actuator.
"""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256

VERSION = "causal-cartographer-v1"
FAMILIES = ("cause_c", "cause_p", "joint", "either", "latent", "noisy_c")
SEEDS = (11, 23, 37, 41, 59, 67)
PAIRS = ((False, False), (False, True), (True, False), (True, True))
SPLITS = ("train", "validation", "local_review", "test", "intervention")


@dataclass(frozen=True)
class Controls:
    first_port: str
    second_port: str


@dataclass(frozen=True)
class World:
    family: str
    seed: int
    controls: Controls
    candidate_c: str
    candidate_p: str
    nuisance: str


@dataclass(frozen=True)
class Observation:
    before: frozenset[tuple[str, ...]]
    observed_after: frozenset[tuple[str, ...]]
    roles: tuple[str, str]
    provenance: str


def new_world(family: str, seed: int) -> World:
    if family not in FAMILIES or type(seed) is not int or seed < 0:
        raise ValueError("Unknown world")
    def name(slot):
        return "q" + sha256(f"{VERSION}:{family}:{seed}:{slot}".encode()
                            ).hexdigest()[:24]
    return World(family, seed, Controls(name("actor"), name("target")),
                 name("C"), name("P"), name("nuisance"))


def _effect(spec: World, c: bool, p: bool, context: bool,
            split: str, sequence: int) -> bool:
    if spec.family == "cause_c":
        return c
    if spec.family == "cause_p":
        return p
    if spec.family == "joint":
        return c and p
    if spec.family == "either":
        return c or p
    if spec.family == "latent":
        return context
    if spec.family == "noisy_c":
        noise = sha256(
            f"{VERSION}:noise:{spec.seed}:{split}:{sequence}".encode()
        ).digest()[0] < 64  # 25% deterministic intervention flip fixture
        return c ^ noise
    raise ValueError("Unexpected causal family")


def case(spec: World, a: bool, b: bool, c: bool, p: bool,
         context: bool, split: str, sequence: int) -> Observation:
    if split not in SPLITS or type(sequence) is not int or sequence < 0:
        raise ValueError("Invalid observation split/serial")
    if any(type(x) is not bool for x in (a,b,c,p,context)):
        raise ValueError("All synthetic intervention settings must be Boolean")
    actor = f"e12_{spec.seed}_{split}_{sequence}_actor"
    target = f"e12_{spec.seed}_{split}_{sequence}_target"
    before = {("role_actor",actor),("role_target",target),("pending",target)}
    if a:
        before.add((spec.controls.first_port,actor))
        before.add((spec.nuisance,actor))
    if b:
        before.add((spec.controls.second_port,target))
    if c:
        before.add((spec.candidate_c,actor))
    if p:
        before.add((spec.candidate_p,target))
    # The baseline XOR(A,B) is a known, separately specified prior. The
    # challenge is which of C/P produces the additional outcome residual.
    if split in ("train","validation"):
        # All six worlds must be observationally equivalent in the natural
        # regime, including the family with noisy *intervention* results.
        outcome = a ^ b ^ c
    else:
        outcome = a ^ b ^ _effect(spec,c,p,context,split,sequence)
    frozen = frozenset(before)
    after = (frozenset((before-{("pending",target)})|{("achieved",target)})
             if outcome else frozen)
    provenance = ("SYNTHETIC_NATURAL" if split in ("train","validation")
                  else "SYNTHETIC_INTERVENTION")
    return Observation(frozen,after,(actor,target),provenance)


def natural(spec: World, split: str):
    if split not in ("train","validation"):
        raise ValueError("Only natural observation splits")
    result=[]
    for a,b in PAIRS:
        for common in (False,True):
            for rep in (0,1):
                result.append(case(spec,a,b,common,common,common,
                                   split,len(result)))
    return tuple(result)


def intervene(spec: World, c: bool, p: bool, sequence: int,
              context: bool = False) -> Observation:
    """Fresh simulator transition, executed only AFTER question selection."""
    return case(spec,False,False,c,p,context,"intervention",sequence)


def independent_suite(spec: World, split: str):
    """Factorial evidence that randomizes C/P separately from hidden context.

    Local-review and test suites are disjoint, and are never accessible to
    the scientific question-selection routine.
    """
    if split not in ("local_review","test"):
        raise ValueError("Unregistered evaluator-only split")
    out=[]
    for c,p in PAIRS:
        for context in (False,True):
            for repeat in (0,1):
                out.append(case(spec,False,False,c,p,context,split,len(out)))
    return tuple(out)


def declared_policy():
    """Toy policy: optimal discriminatory probes are disallowed."""
    return {
        "allowed": frozenset(((False,False),(True,True))),
        "costs": {pair:(4 if pair[0]!=pair[1] else 1) for pair in PAIRS},
        "budget":3,
        "real_world_authority":False,
    }
