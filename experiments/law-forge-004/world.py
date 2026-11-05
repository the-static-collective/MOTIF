"""LAW-FORGE-004 hidden synthetic worlds (evaluator-owned).

The learner in machine.py imports no world definition. Training queries are
resettable, read-only membership observations; independent review/test
mechanisms can disagree and must not be silently treated as ground truth.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from random import Random

from machine import Observation, valid_word, words

FAMILIES = (
    "parity", "any_on",
    "ends_01", "ends_001", "contains_101",
    "ends_0001", "prime_count", "phase_shift"
)


@dataclass(frozen=True)
class World:
    family: str
    seed: int = 0
    opaque_input: str = "channel_q"

    def __post_init__(self):
        if self.family not in FAMILIES or type(self.seed) is not int or (
            self.seed < 0
        ) or not isinstance(self.opaque_input, str) or (
            not self.opaque_input
        ):
            raise ValueError("Unsupported evaluator-only mechanism")

    def measure(self, word, phase="inquiry"):
        word = valid_word(word)
        if phase not in ("inquiry", "review", "test", "transfer"):
            raise ValueError("Evaluation-only partition not permitted")
        if self.family == "parity":
            result = sum(word) % 2
        elif self.family == "any_on":
            result = int(any(word))
        elif self.family == "ends_01":
            result = int(word[-2:] == (0, 1))
        elif self.family == "ends_001":
            result = int(word[-3:] == (0, 0, 1))
        elif self.family == "contains_101":
            result = int(any(word[i:i+3] == (1, 0, 1)
                             for i in range(len(word)-2)))
        elif self.family == "ends_0001":
            result = int(word[-4:] == (0, 0, 0, 1))
        elif self.family == "prime_count":
            result = int(sum(word) in (2, 3, 5, 7, 11))
        else:
            # Training appears to be "ends with 01"; review + test
            # respond according to a different unannounced mechanism.
            result = int(word[-2:] == (0, 1))
            if phase != "inquiry":
                result = int(word[-2:] == (1, 0))
        return Observation(word, result)

    def base(self):
        return tuple(self.measure(w) for w in words(4))

    def execute_batch(self, batch):
        """Only the evaluator may run the proposed membership batch."""
        from machine import MembershipBatch
        if not isinstance(batch, MembershipBatch):
            raise ValueError("Typed local membership batch required")
        # Strictly round trip the proposal before synthetic evaluation.
        checked = MembershipBatch.from_word_batch(batch.words, batch.packet())
        return tuple(self.measure(w, "inquiry") for w in checked.words)

    def partition(self, phase):
        if phase not in ("review", "test", "transfer"):
            raise ValueError("Independent evaluator evidence only")
        salt = {"review": 109, "test": 277, "transfer": 431}[phase]
        rnd = Random(self.seed * 29791 + salt)
        cases = set()
        # Include all targeted small-pattern endings under long prefixes.
        for length in (8, 9, 10, 11):
            for p in product((0, 1), repeat=4):
                for q in product((0, 1), repeat=3):
                    prefix = (0,) * (length - 7)
                    cases.add(prefix + p + q)
            for _ in range(96):
                cases.add(tuple(rnd.randrange(2) for _ in range(length)))
        # Do not expose this independent evidence to model synthesis.
        return tuple(self.measure(w, phase) for w in sorted(cases))
