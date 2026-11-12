"""Hidden synthetic world generator for LAW-FORGE-001.

The learning module forge.py never imports this file. World mechanism names
and withheld labels are evaluator-only. These are not physical laws.
"""
from __future__ import annotations

from dataclasses import dataclass
from forge import Observation, Probe

FAMILIES = ("instant", "edge_first", "edge_second",
            "steady_first", "steady_second", "latent_shift", "xor_memory")


@dataclass(frozen=True)
class World:
    family: str
    seed: int = 0
    port_names: tuple[str, str] = ("opaque_left", "opaque_right")

    def __post_init__(self):
        if self.family not in FAMILIES or type(self.seed) is not int:
            raise ValueError("Unknown finite synthetic mechanism")
        if (len(self.port_names) != 2 or
                self.port_names[0] == self.port_names[1]):
            raise ValueError("Port names must be two distinct labels")

    def measure(self, probe: Probe) -> Observation:
        """A separately owned simulated actuator produces a new observation."""
        if not isinstance(probe, Probe):
            raise ValueError("Only local probe packets accepted")
        a, b = probe.controls
        pa, pb = probe.history[-1]
        if self.family == "instant":
            gate = 1
        elif self.family in ("edge_first", "latent_shift"):
            gate = 1 - pa
        elif self.family == "edge_second":
            gate = 1 - pb
        elif self.family == "steady_first":
            gate = pa
        elif self.family == "steady_second":
            gate = pb
        elif self.family == "xor_memory":
            gate = pa ^ pb
        else:
            raise AssertionError("Unreachable finite world")
        result = a & b & gate
        if self.family == "latent_shift" and len(probe.history) >= 2:
            # The first two sections cannot identify this hidden dependence.
            # New two-tick local-review experiments CAN refute the model.
            if probe.history[-2][0] == 1 and a == 1 and b == 1:
                result = 1 - result
        return Observation(probe, result)

    def initial_observations(self):
        """Natural histories perfectly confound previous first/second ports."""
        return tuple(self.measure(Probe(((p, p),), (a, b)))
                     for p in (0, 1) for a in (0, 1) for b in (0, 1))

    def partition(self, phase: str):
        """Independent 16-cell full coverage, never called by the learner."""
        if phase not in ("review", "test", "transfer"):
            raise ValueError("Unknown evaluation-only partition")
        offset = {"review": 0, "test": 1, "transfer": 2}[phase]
        rows = []
        for pa in (0, 1):
            for pb in (0, 1):
                for a in (0, 1):
                    for b in (0, 1):
                        # Older history differs between partitions and seeds;
                        # the current/previous 16-cell factorial remains exact.
                        oa = (a + pa + self.seed + offset) % 2
                        ob = (b + pb + offset) % 2
                        p = Probe(((oa, ob), (pa, pb)), (a, b))
                        rows.append(self.measure(p))
        return tuple(rows)
