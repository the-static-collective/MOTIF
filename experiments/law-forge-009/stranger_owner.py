"""LAW-FORGE-009 evaluator-owned STRANGER challenge worlds.

This is physically source-separated from the researcher cartridge. We author
the challenges ourselves: independent code packaging does NOT mean independent
human provenance. Stranger mechanisms deliberately exceed the frozen 008
650-program grammar (mux, threshold, nested XOR, changing source).
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from itertools import product
from random import Random
from learner import (
    WIDTH, DOMAIN, SourceContract, Observation, Question,
    controls, question_cost, consequence_weight,
)

FAMILIES = (
    "single_bit", "two_bit_xor", "three_bit_or",
    "conditional_mux", "four_bit_parity", "four_bit_threshold",
    "xor_of_two_pairs", "four_way_conjunction",
    "drifting_pair_xor", "hidden_exception",
)


@lru_cache(maxsize=128)
def partitions(seed):
    rng = Random(seed * 9181 + 2901)
    all_x = list(product((0, 1), repeat=WIDTH))
    rng.shuffle(all_x)
    anchors = (tuple([0] * WIDTH), tuple([1] * WIDTH))
    rest = [x for x in all_x if x not in anchors]
    initial = anchors + tuple(rest[:2])
    return {
        "initial": initial,
        "catalog": tuple(rest[2:130]),
        "review": tuple(rest[130:322]),
        "test": tuple(rest[322:578]),
    }


@dataclass(frozen=True)
class Stranger:
    family: str
    seed: int = 0
    revision: str = "stranger-epoch-1"

    def __post_init__(self):
        if (self.family not in FAMILIES or type(self.seed) is not int
                or self.seed < 0 or not isinstance(self.revision, str)
                or not self.revision):
            raise ValueError("Only source-owned declared stranger worlds")

    @property
    def contract(self):
        # Family label is never included in capability contract.
        return SourceContract("synthetic-stranger-owner",
                              self.revision, f"challenge-{self.seed}")

    @property
    def important_channels(self):
        return tuple(sorted(Random(6513 + self.seed * 2077)
                            .sample(range(WIDTH), 4)))

    def outcome(self, x, phase="inquiry"):
        x = controls(x)
        if phase not in ("inquiry", "review", "test", "transfer"):
            raise ValueError("Only declared source phases")
        a, b, c, d = (x[i] for i in self.important_channels)
        if self.family == "single_bit":
            return a
        if self.family == "two_bit_xor":
            return a ^ b
        if self.family == "three_bit_or":
            return int(a or b or c)
        if self.family == "conditional_mux":
            return b if a else c
        if self.family == "four_bit_parity":
            return a ^ b ^ c ^ d
        if self.family == "four_bit_threshold":
            return int(a + b + c + d >= 3)
        if self.family == "xor_of_two_pairs":
            return (a & b) ^ (c & d)
        if self.family == "four_way_conjunction":
            return a & b & c & d
        if self.family == "drifting_pair_xor":
            return a ^ b if phase == "inquiry" else a & b
        if self.family == "hidden_exception":
            base = int(a or b or c)
            return base ^ int(phase != "inquiry" and x[0] and x[1])
        raise AssertionError("Unrecognized evaluator-only rule")

    def observe(self, x, phase="inquiry"):
        return Observation(controls(x), self.outcome(x, phase),
                           self.contract.id)

    def initial(self):
        return tuple(self.observe(x) for x in partitions(self.seed)["initial"])

    def catalog(self):
        return tuple(Question(x, question_cost(x), consequence_weight(x))
                     for x in partitions(self.seed)["catalog"])

    def execute(self, card):
        if not isinstance(card, Question):
            raise ValueError("Source-owner query card required")
        checked = Question.from_packet(card.packet())
        if checked not in self.catalog():
            raise ValueError("Probe not in current source-owned catalog")
        return self.observe(card.x)

    def independent(self, phase):
        if phase not in ("review", "test"):
            raise ValueError("Independent source partition only")
        return tuple(self.observe(x, phase)
                     for x in partitions(self.seed)[phase])

    def matching_new_epoch(self):
        return Stranger(self.family, self.seed, revision="stranger-epoch-2")
