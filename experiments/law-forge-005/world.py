"""LAW-FORGE-005 sealed synthetic graph evaluator.

The learner never imports this module. It receives only the registered
instrument readouts and outcomes, never the raw graph or hidden family.
Three-valued readings are *constructed from topology*, not privileged truth.
"""
from __future__ import annotations
from dataclasses import dataclass
from itertools import product

from instrument import (Readout, Sensor, Query, bits4,
                        generate_sensor_language)

FAMILIES = (
    "first_edge",
    "one_neighbor",
    "first_neighbor_only",
    "any_route",
    "one_route",
    "two_routes",
    "first_route_only",
    "edge_parity",
    "phase_shift",
    "unseen_context",
)


@dataclass(frozen=True)
class World:
    family: str
    seed: int = 0
    role_names: tuple[str, str, str, str] = (
        "source", "bridge_alpha", "bridge_beta", "target"
    )

    def __post_init__(self):
        if self.family not in FAMILIES or type(self.seed) is not int or (
            self.seed < 0
        ) or (not isinstance(self.role_names, tuple)
               or len(self.role_names) != 4 or
               len(set(self.role_names)) != 4):
            raise ValueError("Only valid evaluator graph worlds")

    @staticmethod
    def reading(sensor, graph):
        e0, e1, e2, e3 = bits4(graph)
        paths = (e0 & e1, e2 & e3)
        if sensor.operation == "BIT":
            return graph[sensor.edges[0]]
        if sensor.operation == "PAIR":
            return tuple(graph[x] for x in sensor.edges)
        if sensor.operation == "COUNT2":
            return sum(graph[x] for x in sensor.edges)
        if sensor.operation == "REACH2":
            return int(any(paths))
        if sensor.operation == "PATHCOUNT":
            return sum(paths)
        if sensor.operation == "PATHPAIR":
            return paths
        if sensor.operation == "RAW4":
            return tuple(graph)
        raise ValueError("No source-owned sensor compiler for unknown expression")

    def rule(self, graph, phase):
        e0, e1, e2, e3 = graph
        r0, r1 = e0 & e1, e2 & e3
        if self.family == "first_edge":
            return e0
        if self.family == "one_neighbor":
            return int(e0 + e2 == 1)
        if self.family == "first_neighbor_only":
            return int(e0 == 1 and e2 == 0)
        if self.family == "any_route":
            return int(r0 or r1)
        if self.family == "one_route":
            return int(r0 + r1 == 1)
        if self.family == "two_routes":
            return int(r0 + r1 == 2)
        if self.family == "first_route_only":
            return int(r0 == 1 and r1 == 0)
        if self.family == "edge_parity":
            return sum(graph) % 2
        if self.family == "phase_shift":
            return int(r0 or r1) if phase == "inquiry" else int(
                e0 == 1 and e2 == 0)
        if self.family == "unseen_context":
            return int(r0 or r1) ^ int(
                phase != "inquiry" and graph == (1, 1, 1, 1))
        raise AssertionError("Unknown evaluator family")

    def measure(self, graph, phase="inquiry", copy_index=0):
        """Read-only evaluator executes a typed synthetic request."""
        graph = bits4(graph)
        if phase not in ("inquiry", "review", "test", "transfer") or (
            type(copy_index) is not int or copy_index < 0
        ):
            raise ValueError("Only local simulator query partitions")
        token = f"{phase}:{copy_index}:{''.join(map(str, graph))}:{self.seed}"
        readings = tuple(
            (sensor, self.reading(sensor, graph))
            for sensor in generate_sensor_language()
        )
        return Readout(token, readings, self.rule(graph, phase))

    def initial(self):
        # Precisely eight predeclared initial graph experiments, no family hints.
        return tuple(self.measure((a, b, c, 0), "inquiry")
                     for a, b, c in product((0, 1), repeat=3))

    def execute(self, queries):
        # Source-owned execution, not a learner tool-use permission.
        result = []
        for request in queries:
            if not isinstance(request, Query):
                raise ValueError("Only typed synthetic graph probes")
            checked = Query.from_packet(request.packet())
            result.append(self.measure(checked.graph_controls, "inquiry"))
        return tuple(result)

    def partition(self, phase):
        if phase not in ("review", "test", "transfer"):
            raise ValueError("Only evaluator may supply review/test samples")
        # Replicated exhaustive 16 graph settings for 32 distinct tokens.
        # New opaque role labels/seed never change the hidden rule.
        controls = tuple(product((0, 1), repeat=4))
        return tuple(self.measure(g, phase, c)
                     for c in (0, 1) for g in controls)
