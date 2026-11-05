"""Evaluator-owned unfamiliar source packs for LAW-FORGE-007.

The researcher lookup.py imports no evaluator/world rules. The source changes
the number of permitted binary channels between four/six/seven and may have
phase-sensitive hidden mechanisms. Contract revision is pinned per source.

These are developer-authored synthetic domains, not external independent data.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1] / "law-forge-006"))
from owner import World as SixLinkOwner

from lookup import Contract, Reading, vector

FAMILIES = (
    "any_three_paths", "first_two_paths", "last_path",
    "exactly_one_path", "edge_parity", "three_edge_joint",
    "phase_shift", "hidden_context",
    "sparse_exception_six",
    "seven_parity", "seven_last_channel",
    "seven_threshold", "seven_phase_shift",
)


@dataclass(frozen=True)
class Source:
    hidden_family: str
    seed: int = 0
    revision: str = "source-rev-1"

    def __post_init__(self):
        if (self.hidden_family not in FAMILIES or
                type(self.seed) is not int or self.seed < 0 or
                not isinstance(self.revision, str) or not self.revision):
            raise ValueError("Invalid synthetic source contract")

    @property
    def width(self):
        return 7 if self.hidden_family.startswith("seven_") else 6

    def contract(self):
        # The source does not expose the hidden mechanism's family name.
        return Contract(
            source="synthetic-unfamiliar-source-pack",
            revision=self.revision,
            channels=tuple(f"channel_{i}" for i in range(self.width))
        )

    def outcome(self, state, phase):
        state = vector(state, self.width)
        if self.width == 6:
            if self.hidden_family == "sparse_exception_six":
                old = SixLinkOwner("any_three_paths", self.seed)
                return old.actual(state, phase) ^ int(state == (1, 1, 1, 1, 1, 1))
            return SixLinkOwner(self.hidden_family, self.seed).actual(state, phase)
        if self.hidden_family == "seven_parity":
            return sum(state) % 2
        if self.hidden_family == "seven_last_channel":
            return state[-1]
        if self.hidden_family == "seven_threshold":
            return int(sum(state) >= 3)
        if self.hidden_family == "seven_phase_shift":
            return sum(state) % 2 if phase == "training" else int(
                sum(state) % 2 == 0)
        raise ValueError("Unrecognized seven-channel hidden source")

    def measure(self, bits, phase="training"):
        if phase not in ("training", "review", "test", "transfer"):
            raise ValueError("Only evaluator-owned sample phases")
        x = vector(bits, self.width)
        return Reading(x, self.outcome(x, phase), self.contract().id)

    def observations(self, phase="training", partial=False):
        if phase not in ("training", "review", "test", "transfer"):
            raise ValueError("No undeclared source phases")
        cases = product((0, 1), repeat=self.width)
        if partial:
            cases = (x for x in cases if x[-1] == 0)
        return tuple(self.measure(x, phase) for x in cases)

    def destination(self):
        return Source(self.hidden_family, self.seed + 101, self.revision)
