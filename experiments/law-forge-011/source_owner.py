"""LAW-FORGE-011 source-owner simulator: unfamiliar signed Boolean phenomena.

The source owner, not the learner, controls hidden mechanisms and membership
queries. Entirely synthetic and still authored by our research process, not
independently created or authenticated. Input partition identities are frozen
per seed and do not reveal any labels.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from hashlib import sha256
from itertools import product
from pathlib import Path
from random import Random
import sys

sys.path.append(str(Path(__file__).resolve().parents[1] / "law-forge-008"))
from learner import (WIDTH, SourceContract, Observation, Question,
                     controls, question_cost, consequence_weight)

FAMILIES = (
    "bit", "xor2", "or3", "and3",
    "signed_exception", "two_signed_exceptions", "conditional_mux",
    "three_bit_majority", "four_bit_parity", "four_bit_threshold",
    "training_review_shift", "hidden_context_shift"
)


@lru_cache(maxsize=128)
def split(seed):
    rng = Random(93613 + seed*19333)
    cells = list(product((0,1), repeat=WIDTH))
    rng.shuffle(cells)
    anchors = (tuple([0]*WIDTH), tuple([1]*WIDTH))
    rest = [x for x in cells if x not in anchors]
    return {
        "initial": anchors + tuple(rest[:2]),
        "catalog": tuple(rest[2:162]),
        "review": tuple(rest[162:354]),
        "test": tuple(rest[354:610])
    }


@dataclass(frozen=True)
class UnknownOwner:
    family: str
    seed: int = 0
    epoch: str = "signed-source-r1"

    def __post_init__(self):
        if (self.family not in FAMILIES or
                type(self.seed) is not int or self.seed < 0 or
                not isinstance(self.epoch, str) or not self.epoch):
            raise ValueError("Invalid synthetic source owner")

    @property
    def contract(self):
        opaque = sha256(
            f"signed-owner-v1:{self.family}:{self.seed}".encode()
        ).hexdigest()[:24]
        return SourceContract("synthetic-independent-signed-source",
                              self.epoch, f"signed-challenge-{opaque}")

    @property
    def positions(self):
        return tuple(sorted(Random(1807 + self.seed*1093)
                            .sample(range(WIDTH), 5)))

    def truth(self, state, phase="train"):
        state = controls(state)
        if phase not in ("train", "review", "test"):
            raise ValueError("Only source-owned sampling phases")
        a,b,c,d,e = (state[i] for i in self.positions)
        if self.family == "bit":
            return a
        if self.family == "xor2":
            return a ^ b
        if self.family == "or3":
            return int(a or b or c)
        if self.family == "and3":
            return a & b & c
        if self.family == "signed_exception":
            return a ^ (b & (1-c))
        if self.family == "two_signed_exceptions":
            return a ^ int((b & (1-c)) or (d & (1-e)))
        if self.family == "conditional_mux":
            return b if a else c
        if self.family == "three_bit_majority":
            return int(a+b+c >= 2)
        if self.family == "four_bit_parity":
            return a ^ b ^ c ^ d
        if self.family == "four_bit_threshold":
            return int(a+b+c+d >= 3)
        if self.family == "training_review_shift":
            return a if phase == "train" else (a ^ b)
        if self.family == "hidden_context_shift":
            return a ^ int(phase != "train" and b and (1-c))
        raise AssertionError("Undeclared hidden owner family")

    def read(self, state, phase="train"):
        return Observation(controls(state), self.truth(state, phase),
                           self.contract.id)

    def initial(self):
        return tuple(self.read(x) for x in split(self.seed)["initial"])

    def catalog(self):
        return tuple(Question(x, question_cost(x), consequence_weight(x))
                     for x in split(self.seed)["catalog"])

    def execute(self, request):
        if not isinstance(request, Question):
            raise ValueError("Typed source query card required")
        card = Question.from_packet(request.packet())
        if card not in self.catalog():
            raise ValueError("Unapproved question, cost or source controls")
        return self.read(card.x)

    def independent(self, phase):
        if phase not in ("review", "test"):
            raise ValueError("No unknown source partition")
        return tuple(self.read(x, phase) for x in split(self.seed)[phase])

    def changed_epoch(self):
        return UnknownOwner(self.family, self.seed, "signed-source-r2")
