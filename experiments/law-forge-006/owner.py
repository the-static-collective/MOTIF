"""Evaluator-owned six-link graph source.

The learner inventor.py cannot import this module. A source contract exposes
low-level link READ only; it does not donate a reachability/path sensor.
Graph and hidden rule labels stay on the evaluator's side.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from itertools import product

from inventor import EDGE_COUNT, GraphQuery, Witness, edges, Proposal


LINKS = (
    ("S", "R0"), ("R0", "T"),
    ("S", "R1"), ("R1", "T"),
    ("S", "R2"), ("R2", "T"),
)
FAMILIES = (
    "any_three_paths", "first_two_paths", "last_path",
    "cross_pair_paths", "edge_or", "middle_edge", "first_path",
    "at_least_two_paths", "exactly_one_path", "edge_parity",
    "three_edge_joint", "phase_shift", "hidden_context"
)


def owner_contract():
    return {"schema": "motif.law-forge.source-capability.v1",
            "source": "LOCAL_SYNTHETIC_SIX_LINK_GRAPH",
            "edge_count": EDGE_COUNT, "links": [list(pair) for pair in LINKS],
            "read_capabilities": ["READ_ONE_SYNTHETIC_LINK"],
            "allow_synthetic_graph_queries": True,
            "allow_real_network": False, "allow_graph_writes": False,
            "instrument_vocabulary": ["AND", "OR", "READ_ONE_SYNTHETIC_LINK"],
            "max_conjunction_width": 2, "max_disjunction_terms": 3,
            "automatic_admission": False}


@dataclass(frozen=True)
class World:
    family: str
    seed: int = 0
    role_names: tuple[str, ...] = ("S", "R0", "R1", "R2", "T")

    def __post_init__(self):
        if (self.family not in FAMILIES or type(self.seed) is not int or
                self.seed < 0 or not isinstance(self.role_names, tuple) or
                len(self.role_names) != 5 or
                len(set(self.role_names)) != 5):
            raise ValueError("Only declared synthetic source worlds")

    def actual(self, state, phase):
        x = edges(state)
        p = (x[0] & x[1], x[2] & x[3], x[4] & x[5])
        if self.family == "any_three_paths":
            result = int(any(p))
        elif self.family == "first_two_paths":
            result = int(p[0] or p[1])
        elif self.family == "last_path":
            result = p[2]
        elif self.family == "cross_pair_paths":
            result = int((x[0] & x[3]) or (x[2] & x[5]))
        elif self.family == "edge_or":
            result = int(x[0] or x[5])
        elif self.family == "middle_edge":
            result = x[3]
        elif self.family == "first_path":
            result = p[0]
        elif self.family == "at_least_two_paths":
            result = int(sum(p) >= 2)
        elif self.family == "exactly_one_path":
            result = int(sum(p) == 1)
        elif self.family == "edge_parity":
            result = sum(x) % 2
        elif self.family == "three_edge_joint":
            result = x[0] & x[2] & x[4]
        elif self.family == "phase_shift":
            result = int(any(p)) if phase == "inquiry" else int(p[0] or p[1])
        else:
            result = int(any(p)) ^ int(
                phase != "inquiry" and x == (1, 1, 1, 1, 1, 1))
        return result

    def measure(self, graph, phase="inquiry"):
        graph = edges(graph)
        if phase not in ("inquiry", "review", "test", "transfer"):
            raise ValueError("Only recognized synthetic partitions")
        token = sha256(
            f"{phase}|{self.seed}|{self.role_names}|{graph}".encode()
        ).hexdigest()[:32]
        return Witness(graph, self.actual(graph, phase), token)

    def initial(self):
        # One link is always absent in initial encounters, so the 3rd path
        # is initially unavailable. An owner-approved new query batch is
        # required to distinguish new relational affordances.
        return tuple(self.measure((a, b, c, d, 0, e))
                     for a, b, c, d, e in product((0, 1), repeat=5))

    def execute(self, queries):
        replies = []
        for query in queries:
            if not isinstance(query, GraphQuery):
                raise ValueError("Only strict local graph queries can execute")
            checked = GraphQuery.from_packet(query.packet())
            replies.append(self.measure(checked.controls, "inquiry"))
        return tuple(replies)

    def independent(self, phase):
        if phase not in ("review", "test", "transfer"):
            raise ValueError("Only evaluator-owned independent partitions")
        return tuple(self.measure(x, phase)
                     for x in product((0, 1), repeat=EDGE_COUNT))

    def conformance(self, packet, phase="review"):
        """Source owner validates an invented AST, without admitting it.

        This is a local, source-owned compiler/conformance gate, NOT the
        independent GRAFT repository's admission or actual deployment.
        """
        if phase not in ("review", "transfer"):
            raise ValueError("Conformance is not a training-query oracle")
        candidate = Proposal.from_packet(packet)
        if candidate.sensor.referenced_links and max(
            candidate.sensor.referenced_links
        ) >= len(LINKS):
            raise ValueError("Instrument requests undeclared link")
        failures = sum(candidate.sensor.predict(row.inputs) != row.result
                       for row in self.independent(phase))
        return {"schema": "motif.law-forge.owner-conformance.v1",
                "source": owner_contract()["source"],
                "model_id": candidate.id,
                "status": ("PROPOSE_ONLY_REVIEW_PASSED" if failures == 0
                           else "HOLD_SOURCE_CONFORMANCE_FAILURE"),
                "failures": failures, "automatic_admission": False,
                "real_world_authority": False}
