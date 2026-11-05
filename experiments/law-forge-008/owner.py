"""LAW-FORGE-008 evaluator-owned large synthetic sources.

This file alone knows hidden mechanisms and test labels. The learner sees an
opaque twelve-channel source contract, typed initial observations, and a
finite allowed query catalog with declared synthetic cost and consequence
weight. At most 24 query cost units, on a 4096-setting domain.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from random import Random

from learner import (
    SourceContract, Observation, Question, controls,
    consequence_weight, question_cost, WIDTH, DOMAIN
)

FAMILIES = (
    "identity_bit", "pair_and", "pair_or", "pair_xor",
    "triple_and", "triple_or", "triple_majority",
    "triple_xor", "twelve_parity", "phase_shift", "hidden_context"
)


@dataclass(frozen=True)
class World:
    family: str
    seed: int = 0
    source_epoch: str = "epoch-1"

    def __post_init__(self):
        if self.family not in FAMILIES or type(self.seed) is not int or (
            self.seed < 0
        ) or not isinstance(self.source_epoch, str) or not self.source_epoch:
            raise ValueError("Undeclared source-owned synthetic world")

    @property
    def contract(self):
        # Neither this source ID nor its query catalog reveals the hidden
        # family, target features, or labels.
        return SourceContract("synthetic-twelve-channel-laboratory",
                              self.source_epoch, f"source-instance-{self.seed}")

    @property
    def hidden_indices(self):
        rng = Random(711 + self.seed * 891)
        return tuple(sorted(rng.sample(range(WIDTH), 3)))

    def outcome(self, x, phase="train"):
        x = controls(x)
        if phase not in ("train", "review", "test", "transfer"):
            raise ValueError("Only evaluator-owned source partitions")
        a, b, c = (x[i] for i in self.hidden_indices)
        if self.family == "identity_bit":
            return a
        if self.family == "pair_and":
            return a & b
        if self.family == "pair_or":
            return a | b
        if self.family == "pair_xor":
            return a ^ b
        if self.family == "triple_and":
            return a & b & c
        if self.family == "triple_or":
            return a | b | c
        if self.family == "triple_majority":
            return int(a + b + c >= 2)
        if self.family == "triple_xor":
            return a ^ b ^ c
        if self.family == "twelve_parity":
            return sum(x) % 2
        if self.family == "phase_shift":
            return (a ^ b) if phase == "train" else (a & b)
        if self.family == "hidden_context":
            original = a | b | c
            return original ^ int(
                phase != "train" and x[0] == 1 and x[1] == 1)
        raise AssertionError("Hidden evaluator family not represented")

    def observe(self, x, phase="train"):
        return Observation(controls(x), self.outcome(x, phase),
                           self.contract.id)

    def partitions(self):
        rng = Random(1447 + self.seed * 1559)
        controls_all = list(product((0, 1), repeat=WIDTH))
        rng.shuffle(controls_all)
        # Anchor cases are a specified source observation protocol, not
        # privileged hidden mechanism hints.
        anchors = [tuple([0]*WIDTH), tuple([1]*WIDTH)]
        anchors.extend(controls_all[:2])
        used = set(anchors)
        remaining = [x for x in controls_all if x not in used]
        return {
            "initial": tuple(anchors),
            "catalog": tuple(remaining[:160]),
            "review": tuple(remaining[160:352]),
            "test": tuple(remaining[352:672])
        }

    def initial(self):
        return tuple(self.observe(x, "train")
                     for x in self.partitions()["initial"])

    def query_catalog(self):
        return tuple(Question(x, question_cost(x), consequence_weight(x))
                     for x in self.partitions()["catalog"])

    def execute(self, offered):
        """This evaluator alone dispatches bounded membership questions."""
        if not isinstance(offered, Question):
            raise ValueError("Source must receive a typed question")
        checked = Question.from_packet(offered.packet())
        if checked not in self.query_catalog():
            raise ValueError("Unknown, relabeled or unapproved source query")
        return self.observe(checked.x, "train")

    def independent(self, phase):
        if phase not in ("review", "test", "transfer"):
            raise ValueError("Only evaluator-owned independent evidence")
        key = "review" if phase == "review" else "test"
        return tuple(self.observe(x, phase)
                     for x in self.partitions()[key])

    def destination(self):
        return World(self.family, self.seed + 101, self.source_epoch)
