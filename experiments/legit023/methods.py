"""LEGIT-023: executable, source-attributed classical research methods.

This is a small, honest portfolio, not a claim to contain every state-of-the-art
solver. Graph non-isomorphism and a *homomorphism-count witness* are distinct
goals. An isomorphism solver cannot silently stand in for the latter.
"""
from __future__ import annotations

from collections import Counter
from functools import lru_cache

# A method's verification contract matters more than its name. The planned
# interfaces are deliberately NOT returned as executable capabilities.
EXECUTABLE = (
    {"id": "tree_hom_dynamic_programming", "domain": "exact graph-hom counts",
     "status": "EXECUTABLE", "proof_obligation": "match independent enumerator"},
    {"id": "constraint_backtracking_hom", "domain": "exact graph-hom counts",
     "status": "EXECUTABLE", "proof_obligation": "match independent enumerator"},
    {"id": "training_optimal_probe_order_dp", "domain": "small finite research planning",
     "status": "EXECUTABLE", "proof_obligation": "frozen training-only source order"},
    {"id": "joint_one_dimensional_WL", "domain": "graph non-isomorphism",
     "status": "EXECUTABLE", "proof_obligation": "unequal exact color histograms"},
    {"id": "networkx_VF2pp", "domain": "graph isomorphism decision",
     "status": "EXECUTABLE_IF_NETWORKX_PRESENT", "proof_obligation": "library decision"},
)
FUTURE_ADAPTERS = (
    {"id": "SymPy_exact_symbolics", "status": "NOT_INTEGRATED"},
    {"id": "Z3_SMT", "status": "NOT_INTEGRATED"},
    {"id": "cvc5_SyGuS_synthesis", "status": "NOT_INTEGRATED"},
    {"id": "OR_Tools_CP_SAT", "status": "NOT_INTEGRATED"},
    {"id": "Lean4_mathlib_formal_proofs", "status": "NOT_INTEGRATED"},
    {"id": "nauty_Traces_canonical_labeling", "status": "NOT_INTEGRATED"},
)


def _adjacency(graph):
    """Expected graph: (vertex_count, tuple of simple undirected edges)."""
    n, edges = graph
    if not isinstance(n, int) or n < 0:
        raise ValueError("invalid vertex count")
    adjacent = [set() for _ in range(n)]
    for u, v in edges:
        if not (0 <= u < n and 0 <= v < n) or u == v:
            raise ValueError("graph must be simple and loopless")
        adjacent[u].add(v)
        adjacent[v].add(u)
    return tuple(tuple(sorted(x)) for x in adjacent)


def tree_hom_count(source, target):
    """Exact hom(F,G) for forest F, by sum/product message passing.

    Returns None if F contains a cycle. Neighbor summation permits repeated
    target vertices for nonadjacent source vertices (hom, NOT embeddings).
    Disconnected forest counts multiply; isolated vertices have n choices.
    """
    src = _adjacency(source)
    dst = _adjacency(target)
    n = len(src)
    parent = {}
    roots = []
    visit_order = []
    for root in range(n):
        if root in parent:
            continue
        parent[root] = -1
        roots.append(root)
        stack = [root]
        while stack:
            u = stack.pop()
            visit_order.append(u)
            for v in src[u]:
                if v == parent[u]:
                    continue
                if v in parent:
                    return None
                parent[v] = u
                stack.append(v)
    # Messages at each node, indexed by image in target graph.
    messages = {}
    for u in reversed(visit_order):
        children = [v for v in src[u] if parent.get(v) == u]
        messages[u] = tuple(
            _product(sum(messages[child][w] for w in dst[x])
                     for child in children)
            for x in range(len(dst)))
    return _product(sum(messages[root]) for root in roots)


def _product(values):
    p = 1
    for v in values:
        p *= v
    return p


def constrained_hom_count(source, target):
    """Exact hom(F,G) by degree-ordered CSP backtracking and edge pruning.

    Source mappings are NOT injective. Every source edge must map to an edge.
    This is independent of the exhaustive vertex-assignment oracle in 021/022.
    """
    src = _adjacency(source)
    dst = tuple(set(x) for x in _adjacency(target))
    order = sorted(range(len(src)), key=lambda v: (-len(src[v]), v))
    assignment = {}
    def visit(depth):
        if depth == len(order):
            return 1
        u = order[depth]
        subtotal = 0
        for x in range(len(dst)):
            if all(x in dst[assignment[v]]
                   for v in src[u] if v in assignment):
                assignment[u] = x
                subtotal += visit(depth + 1)
                del assignment[u]
        return subtotal
    return visit(0)


def hom_count(source, target):
    """Route a precise homomorphism-count task to an exact algorithm."""
    count = tree_hom_count(source, target)
    if count is not None:
        return {"value": count, "method": "tree_hom_dynamic_programming"}
    return {"value": constrained_hom_count(source, target),
            "method": "constraint_backtracking_hom"}


def joint_wl_separation(a, b):
    """Run exact joint 1-WL color refinement, without hash collisions.

    Unequal color histograms CERTIFY non-isomorphism. Equal histograms
    mean UNKNOWN, not isomorphic. Joint ranking makes colors comparable.
    """
    first = _adjacency(a)
    second = _adjacency(b)
    adjacent = first + tuple(
        tuple(x + len(first) for x in row) for row in second)
    left = len(first)
    colors = tuple(len(row) for row in adjacent)
    for round_number in range(len(adjacent) + 1):
        if Counter(colors[:left]) != Counter(colors[left:]):
            return {"conclusion": "CERTIFIED_NONISOMORPHIC_BY_INVARIANT",
                    "round": round_number}
        signatures = [
            (colors[v], tuple(sorted(colors[w] for w in row)))
            for v, row in enumerate(adjacent)]
        keys = {value: i for i, value in enumerate(sorted(set(signatures)))}
        updated = tuple(keys[x] for x in signatures)
        if updated == colors:
            break
        colors = updated
    return {"conclusion": "INCONCLUSIVE", "round": round_number}


def vf2pp_decision(a, b):
    """Direct graph-isomorphism decision, NEVER a hom-count witness."""
    import networkx as nx
    def graph(data):
        g = nx.Graph()
        g.add_nodes_from(range(data[0]))
        g.add_edges_from(data[1])
        return g
    return {"isomorphic": bool(nx.vf2pp_is_isomorphic(graph(a), graph(b))),
            "method": "networkx_VF2pp",
            "does_not_supply_homomorphism_source_witness": True}


def optimal_training_order(training, probes, counter, model="unit"):
    """Exact finite DP for training-weighted *nonadaptive* probe ordering.

    Minimize sum over distinguishable training pairs of cumulative probe
    costs until the first successful question. No heldout data is read.
    This optimizes only the supplied finite grammar and training distribution,
    not the global problem of mathematical discovery.
    """
    if model not in ("unit", "assignments"):
        raise ValueError("unknown training objective")
    probes = tuple(probes)
    masks = []
    for probe in probes:
        mask = 0
        for i, pair in enumerate(training):
            if counter(probe, pair.graphs[0]) != counter(probe, pair.graphs[1]):
                mask |= 1 << i
        masks.append(mask)
    possible = 0
    for mask in masks:
        possible |= mask
    costs = tuple(1 if model == "unit" else
                  (max(g[0] for pair in training for g in pair.graphs)
                   if training else 0) ** p[0]
                  for p in probes)
    @lru_cache(None)
    def solve(remaining):
        if not remaining:
            return (0, ())
        best = None
        for i, covered in enumerate(masks):
            next_mask = remaining & ~covered
            if next_mask == remaining:
                continue
            cost, tail = solve(next_mask)
            choice = (costs[i] * remaining.bit_count() + cost, (i,) + tail)
            if best is None or choice < best:
                best = choice
        if best is None:
            raise AssertionError("covered training tasks unexpectedly unsolved")
        return best
    optimum, prefix = solve(possible)
    ordered_indices = prefix + tuple(i for i in range(len(probes))
                                     if i not in prefix)
    if set(ordered_indices) != set(range(len(probes))):
        raise AssertionError("non-permutation portfolio")
    return {"order": tuple(probes[i] for i in ordered_indices),
            "training_objective": optimum,
            "training_coverable_pairs": possible.bit_count(),
            "training_pairs": len(training),
            "optimization": "exact_DP_finite_training_nonadaptive",
            "model": model,
            "heldout_influenced_selection": False}
