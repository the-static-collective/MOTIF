"""LAW-FORGE-003 evaluator-only procedural worlds.

world.py is NEVER imported by foundry.py. The learner receives only
Example(inputs, outcome), not these family labels or hidden functions.
"""
from __future__ import annotations
from dataclasses import dataclass
from itertools import product
from random import Random
from foundry import Example, bits

FAMILIES = (
    "parity_fold", "any_on_fold", "all_on_fold",
    "exactly_one", "majority", "hidden_width", "phase_shift"
)


@dataclass(frozen=True)
class World:
    family: str
    seed: int = 0
    renamed_ports: tuple[str, str] = ("unnamed_input", "unnamed_output")

    def __post_init__(self):
        if self.family not in FAMILIES or type(self.seed) is not int or self.seed < 0:
            raise ValueError("Evaluator requires a known procedural family and seed")
        if (len(self.renamed_ports) != 2 or
                self.renamed_ports[0] == self.renamed_ports[1]):
            raise ValueError("Opaque port names must differ")

    def measure(self, sequence, phase="inquiry"):
        vals = bits(sequence)
        if phase not in ("inquiry", "review", "test", "transfer"):
            raise ValueError("Unknown synthetic evaluation partition")
        n = len(vals)
        if self.family == "parity_fold":
            outcome = sum(vals) % 2
        elif self.family == "any_on_fold":
            outcome = int(any(vals))
        elif self.family == "all_on_fold":
            outcome = int(all(vals))
        elif self.family == "exactly_one":
            outcome = int(sum(vals) == 1)
        elif self.family == "majority":
            outcome = int(sum(vals) > n / 2)
        elif self.family == "hidden_width":
            # The two-input truth table still matches parity. The simulator
            # has a separate higher-order interaction for longer sequences.
            outcome = (sum(vals) % 2) ^ int(
                n >= 4 and vals[0] == 1 and vals[-1] == 1)
        else:
            outcome = sum(vals) % 2
            if phase != "inquiry" and n >= 3 and vals[0] == 1:
                # Deliberate test phase shift, NOT IID sensor noise.
                outcome ^= 1
        return Example(vals, outcome)

    def initial_observations(self):
        # The 11 pair is deliberately omitted. For the fold worlds it
        # disambiguates XOR/OR, and for all_on it disambiguates AND/CONST0.
        # Longer training examples constrain actual left-fold behavior.
        cases = (
            (0, 0), (0, 1), (1, 0),
            (0, 0, 0), (0, 0, 1), (0, 1, 0), (1, 0, 0)
        )
        return tuple(self.measure(row) for row in cases)

    def partition(self, phase):
        if phase not in ("review", "test", "transfer"):
            raise ValueError("Independent evaluator-only partition required")
        phase_id = {"review": 11, "test": 29, "transfer": 47}[phase]
        random = Random(self.seed * 21401 + phase_id * 3109)
        # Complete small truth-table coverage and long-sequence stress.
        cases = set(product((0, 1), repeat=2))
        cases.update(product((0, 1), repeat=3))
        cases.update(product((0, 1), repeat=4))
        # Explicit independent counterexample for hidden-width mechanisms.
        cases.update((
            (1, 0, 0, 1, 0), (1, 0, 0, 0, 1),
            (1, 1, 0, 0, 1), (0, 1, 0, 0, 1),
            (1, 0, 0, 1, 0, 0, 0, 0), (1, 0, 1, 0, 0, 0, 0, 1),
            (0, 0, 0, 0, 0, 0, 0, 1), (1, 1, 1, 1, 1, 1, 1, 1)
        ))
        for n in (5, 6, 7, 8, 9, 10, 11):
            for _ in range(8):
                cases.add(tuple(random.randrange(2) for _ in range(n)))
        return tuple(self.measure(row, phase) for row in sorted(cases))
