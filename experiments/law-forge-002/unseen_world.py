"""Evaluator-owned worlds for LAW-FORGE-002.

The learner's constructor.py has no import of this file. Names, mechanisms,
partition assignments and ground truth stay in the evaluator.
"""
from __future__ import annotations
from dataclasses import dataclass

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "law-forge-001"))
from forge import Probe, Observation

FAMILIES = ("xor_memory", "or_memory", "instant",
            "two_tick_hidden", "distribution_shift")
PRIOR_PAIRS = ((0, 0), (0, 1), (1, 0))


@dataclass(frozen=True)
class World:
    family: str
    seed: int = 0
    renamed_ports: tuple[str, str] = ("epsilon", "zeta")

    def __post_init__(self):
        if self.family not in FAMILIES or type(self.seed) is not int:
            raise ValueError("Unknown evaluator world family")
        if (len(self.renamed_ports) != 2 or
                self.renamed_ports[0] == self.renamed_ports[1]):
            raise ValueError("Two distinct opaque port labels required")

    def measure(self, probe, phase="inquiry"):
        if not isinstance(probe, Probe):
            raise ValueError("Local typed probe required")
        if phase not in ("inquiry", "review", "test", "transfer"):
            raise ValueError("Unsupported simulator partition")
        a, b = probe.controls
        pa, pb = probe.history[-1]
        if self.family == "instant":
            gate = 1
        elif self.family == "or_memory":
            gate = pa | pb
        else:
            gate = pa ^ pb
        if self.family == "two_tick_hidden" and len(probe.history) > 1:
            # The actual synthetic mechanism has an additional two-tick term.
            gate ^= probe.history[-2][0]
        if self.family == "distribution_shift" and phase != "inquiry":
            # Deliberately altered simulator mechanism, not normal IID noise.
            gate = pa | pb
        return Observation(probe, a & b & gate)

    def initial_observations(self):
        # These three history states confound XOR and OR, and disprove the
        # old individual-lag grammar on (1,1) for those two families.
        return tuple(self.measure(Probe(((pa, pb),), (a, b)))
                     for pa, pb in PRIOR_PAIRS
                     for a in (0, 1) for b in (0, 1))

    def partition(self, phase):
        if phase not in ("review", "test", "transfer"):
            raise ValueError("Only evaluator-owned held-out partitions")
        offset = {"review": 11, "test": 17, "transfer": 23}[phase]
        examples = []
        for pa in (0, 1):
            for pb in (0, 1):
                for a in (0, 1):
                    for b in (0, 1):
                        older_a = (pa + a + self.seed + offset) % 2
                        older_b = (pb + b + offset) % 2
                        probe = Probe(((older_a, older_b), (pa, pb)), (a, b))
                        examples.append(self.measure(probe, phase))
        return tuple(examples)
