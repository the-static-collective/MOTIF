"""NUNUMATHAL-001: hostile comparisons of *computed finite graph* crossings.

Graph changes are synthetic and exactly reproducible; cross-domain mechanism
identity is never inferred from the printed index or even a matching signature.
"""
from __future__ import annotations
from dataclasses import dataclass


class GraphRefusal(ValueError):
    pass


@dataclass(frozen=True)
class Graph:
    vertices: frozenset[str]
    edges: frozenset[tuple[str, str]]

    def __post_init__(self):
        if not all(isinstance(v, str) and v for v in self.vertices):
            raise GraphRefusal("vertices must be named")
        for a, b in self.edges:
            if a >= b or a not in self.vertices or b not in self.vertices:
                raise GraphRefusal("edges must be ordered, loopless, and within carrier")

    @classmethod
    def build(cls, vertices, edges):
        pairs = []
        for e in edges:
            if len(e) != 2 or not all(isinstance(v, str) for v in e):
                raise GraphRefusal("edge must have exactly two named endpoints")
            pairs.append(tuple(sorted(e)))
        return cls(frozenset(vertices), frozenset(pairs))

    def components(self) -> int:
        unseen = set(self.vertices)
        count = 0
        while unseen:
            count += 1
            pool = [unseen.pop()]
            while pool:
                v = pool.pop()
                neighbors = {b if a == v else a for a, b in self.edges if v in (a, b)}
                incoming = neighbors & unseen
                pool.extend(incoming)
                unseen.difference_update(incoming)
        return count

    def isolates(self) -> int:
        incident = {x for edge in self.edges for x in edge}
        return len(self.vertices - incident)


def statistics(graph: Graph) -> tuple[int, int, int, int, int]:
    c = graph.components()
    return len(graph.vertices), len(graph.edges), c, graph.isolates(), len(graph.edges)-len(graph.vertices)+c


@dataclass(frozen=True)
class GraphMathal:
    name: str
    source: Graph
    target: Graph
    rule: str
    parameter: str
    delta: tuple[int, int, int, int, int]
    receipt: tuple[str, ...]

    @property
    def numerical_index(self):
        return len(self.source.vertices), len(self.target.vertices)


def perform(graph: Graph, rule: str, new_vertex: str, edge: tuple[str,str] | None = None,
            anchor: str = "") -> GraphMathal:
    """Replay three explicit synthetic graph rewrites, with strict preconditions."""
    if not isinstance(new_vertex, str) or not new_vertex or new_vertex in graph.vertices:
        raise GraphRefusal("new vertex must be fresh")
    if rule not in {"isolated", "leaf", "subdivide"}:
        raise GraphRefusal("unknown synthetic rule")
    edges = set(graph.edges)
    info = []
    if rule == "leaf":
        if anchor not in graph.vertices:
            raise GraphRefusal("leaf anchor missing")
        edges.add(tuple(sorted((anchor, new_vertex))))
        info.append(f"anchor:{anchor}")
    elif rule == "subdivide":
        if edge is None:
            raise GraphRefusal("subdivision edge required")
        chosen = tuple(sorted(edge))
        if chosen not in edges:
            raise GraphRefusal("subdivision edge not present")
        edges.remove(chosen)
        edges.add(tuple(sorted((chosen[0],new_vertex))))
        edges.add(tuple(sorted((new_vertex, chosen[1]))))
        info.append(f"subdivided:{chosen[0]}:{chosen[1]}")
    target = Graph.build(graph.vertices | {new_vertex}, edges)
    before, after = statistics(graph), statistics(target)
    delta = tuple(y - x for x, y in zip(before, after))
    return GraphMathal(f"{rule}@{new_vertex}", graph, target, rule, new_vertex,
                       delta, (f"simulation:{rule}", *info, f"before:{before}", f"after:{after}"))


def compare(a: GraphMathal, b: GraphMathal) -> dict:
    """Nominate second-order relation; remove numerical indices before comparison."""
    equal_index = a.numerical_index == b.numerical_index
    surviving = a.delta == b.delta  # already discards absolute index
    return {
        "second_order_status": "I",  # proposed common mechanism only
        "same_index": equal_index,
        "same_index_status": "F" if equal_index else "NOT_SAME",
        "numeral_removed_signature_match": surviving,
        "equal_rule_label": a.rule == b.rule,
        "invariants": {"left": a.delta, "right": b.delta,
                       "coordinates": ("vertices", "edges", "components", "isolates", "cycle_rank")},
        "refusal": "A matching index or invariant vector does not establish shared mechanism.",
        "needs_independent_warrant": True,
    }
