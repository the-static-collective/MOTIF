"""QC-005 independent foreign graph hosts and classical oracles.

Graphs come from the third-party NetworkX 3.6.1 package, not from MOTIF's
training fixture generator. Graph *families* are external implementations;
the three tasks and this harness remain researcher-selected and public.
This is a test of out-of-training-graph transfer, NOT a sealed blind exam.
"""
from __future__ import annotations

from hashlib import sha256
import json
import networkx as nx

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "quantumcode002"))
from structural import Graph, edge


class UnsupportedDomain(ValueError):
    pass


def topology(native: nx.Graph) -> Graph:
    """Explicit, lossy topology-only adapter; never silently flatten DiGraph."""
    if native.is_directed() or native.is_multigraph():
        raise UnsupportedDomain("Directed and multiedge structures require new types")
    if nx.number_of_selfloops(native):
        raise UnsupportedDomain("Self loops unsupported by simple-graph grammar")
    return Graph.of(native.nodes, native.edges)


def normalize_native(source: nx.Graph) -> nx.Graph:
    if source.is_directed() or source.is_multigraph():
        raise UnsupportedDomain("This is an undirected simple-graph test")
    if nx.number_of_selfloops(source):
        raise UnsupportedDomain("Self-loop graph outside the declared grammar")
    # Map arbitrary foreign objects (integer, person names, tuple grid cells)
    # to neutral labels; neither source names nor node attributes reach MOTIF.
    nodes = sorted(source.nodes, key=lambda x: (type(x).__name__, repr(x)))
    mapping = {node: f"foreign-{i:04d}" for i, node in enumerate(nodes)}
    result = nx.Graph()
    result.add_nodes_from(mapping.values())
    result.add_edges_from((mapping[a], mapping[b]) for a, b in source.edges)
    return result


def hosts():
    """Independent library topologies, never passed to discovery or review."""
    fixed = (
        ("karate_1977", nx.karate_club_graph()),
        ("florentine_families", nx.florentine_families_graph()),
        ("davis_women_bipartite", nx.davis_southern_women_graph()),
        ("grid_7x8", nx.grid_2d_graph(7, 8)),
        ("barbell_8_5", nx.barbell_graph(8, 5)),
        ("regular_degree_3", nx.random_regular_graph(3, 30, seed=20261107)),
        ("small_world_48", nx.watts_strogatz_graph(48, 4, .23, seed=20261107)),
        ("random_48", nx.gnp_random_graph(48, .11, seed=20261107)),
        ("wheel_17", nx.wheel_graph(17)),
        ("lollipop_9_7", nx.lollipop_graph(9, 7)),
        ("long_path_26", nx.path_graph(26)),
        ("odd_cycle_27", nx.cycle_graph(27)),
    )
    return tuple((name, normalize_native(g)) for name, g in fixed)


def native_signature(graph: nx.Graph):
    return sha256(json.dumps(
        {"nodes": sorted(graph.nodes),
         "edges": sorted(edge(a, b) for a, b in graph.edges)},
        separators=(",", ":"), sort_keys=True).encode()).hexdigest()


def oracle(question: str, graph: nx.Graph, target: tuple[str, str]) -> bool:
    """Separate independent classical NetworkX + exhaustive simple path truth."""
    a, b = target
    if not graph.has_edge(a, b):
        raise ValueError("Existing source edge required")
    cut = graph.copy()
    cut.remove_edge(a, b)
    if question == "alternate_path":
        return nx.has_path(cut, a, b)
    if question == "triangle":
        return len(set(graph.neighbors(a)) & set(graph.neighbors(b))) > 0
    if question == "square":
        # Independent length-three *simple* path check, not TC or JOIN AST.
        return any(x != b and x != a and y not in (a, b, x)
                   and cut.has_edge(y, b)
                   for x in cut.neighbors(a)
                   for y in cut.neighbors(x))
    raise UnsupportedDomain("Unknown task has no externally established semantics")


def expected_graph(question: str, graph: nx.Graph, target: tuple[str, str]) -> Graph:
    """Foreign oracle produces an independent before/after graph witness."""
    a, b = target
    condition = oracle(question, graph, target)
    result = graph.copy()
    if condition:
        result.remove_edge(a, b)
    n0, n1 = "foreign-new-0", "foreign-new-1"
    if n0 in result or n1 in result:
        raise ValueError("Oracle fresh-name collision")
    result.add_edges_from(((a, n0), (n0, n1), (n1, b)))
    return topology(result)


def count_external():
    return tuple({"name": name, "nodes": len(graph.nodes),
                  "edges": len(graph.edges), "sha256": native_signature(graph)}
                 for name, graph in hosts())
