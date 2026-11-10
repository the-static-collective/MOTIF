"""MOTIF-GENIUS-001: small, inspectable discovery-operator prototypes.

These algorithms are modern educational analogies inspired by historical
research practices, not reconstructions of private cognitive processes.
No claim of novel mathematics, historical attribution, or learned routing.
"""
from __future__ import annotations

from itertools import combinations


def clock_offset_receipt(send_a: float, observed_b: float, return_a: float,
                         *, symmetric_path: bool | None = None) -> dict:
    """Operationally estimate B's clock offset, conditionally on equal path times.

    If the outbound/return light or signal path is not independently known
    symmetric, a measured RTT does not establish the one-way delay.
    """
    if return_a <= send_a:
        raise ValueError("Return time must follow departure")
    midpoint = (send_a + return_a) / 2
    receipt = {
        "operator": "OPERATIONAL_REDEFINITION",
        "observations": {"send_a": send_a, "observed_b": observed_b,
                         "return_a": return_a},
        "round_trip": return_a - send_a,
        "assumption": "equal outbound and return travel times",
        "naive_offset": observed_b - send_a,
        "conditional_offset": observed_b - midpoint,
        "question": "Is the signal path symmetric, independently of the clocks?",
        "status": "CONDITIONAL" if symmetric_path is True else "HOLD",
    }
    if symmetric_path is not True:
        receipt["reason"] = "one-way offset not identifiable from these three readings alone"
    return receipt


def partition_numbers(max_n: int) -> list[int]:
    """Exact coin-change dynamic programming for integer partitions."""
    if max_n < 0:
        raise ValueError("max_n must be nonnegative")
    count = [0] * (max_n + 1)
    count[0] = 1
    for part in range(1, max_n + 1):
        for n in range(part, max_n + 1):
            count[n] += count[n - part]
    return count


def mine_modular_congruences(sequence: list[int], moduli: tuple[int, ...],
                             train_end: int, min_support: int = 10) -> list[dict]:
    """Mine finite modular conjectures and separately test future indices.

    Caller supplies data whose values are independent of candidate selection.
    This is not an infinite proof or necessarily historically novel mathematics.
    """
    if not 0 < train_end < len(sequence):
        raise ValueError("Need disjoint nonempty train and test ranges")
    if min_support < 2:
        raise ValueError("min_support must be >=2")
    results = []
    for m in sorted(set(moduli)):
        if m < 2:
            raise ValueError("moduli must be >=2")
        for residue in range(m):
            train_indices = [n for n in range(train_end) if n % m == residue]
            if len(train_indices) < min_support:
                continue
            if not all(sequence[n] % m == 0 for n in train_indices):
                continue
            test_indices = [n for n in range(train_end, len(sequence)) if n % m == residue]
            if len(test_indices) < min_support:
                continue
            counterexamples = [n for n in test_indices if sequence[n] % m != 0]
            results.append({
                "operator": "CONJECTURE_THEN_FALSIFY",
                "conjecture": f"a({m}k+{residue}) is divisible by {m}",
                "modulus": m, "residue": residue,
                "train_support": len(train_indices),
                "test_support": len(test_indices),
                "test_counterexamples": counterexamples,
                "status": "FINITE_TEST_PASS_NOT_PROOF" if not counterexamples else "FALSIFIED",
                "question": "Can a general proof or an external counterexample be found?",
            })
    return results


def exact_min_cut(nodes: tuple[str, ...], edges: tuple[tuple[str, str, int], ...],
                  source: str, sink: str) -> dict:
    """Exact small directed-graph min cut by exhaustive partition enumeration."""
    if len(nodes) != len(set(nodes)) or source not in nodes or sink not in nodes or source == sink:
        raise ValueError("Need distinct valid source/sink and unique vertices")
    if len(nodes) > 12:
        raise ValueError("Only small graphs: <=12 vertices")
    for u, v, w in edges:
        if u not in nodes or v not in nodes or type(w) is not int or w < 0:
            raise ValueError("Edges must have valid nodes and nonnegative integer capacities")
    interior = sorted(set(nodes) - {source, sink})
    best, best_side, checked = None, None, 0
    for size in range(len(interior) + 1):
        for choice in combinations(interior, size):
            side = {source, *choice}
            capacity = sum(w for u, v, w in edges if u in side and v not in side)
            checked += 1
            if best is None or capacity < best:
                best, best_side = capacity, sorted(side)
    return {"capacity": best, "source_side": best_side, "cuts_checked": checked,
            "status": "EXACT_FINITE", "operator": "STRUCTURAL_ANALOGY"}


def transfer_min_cut(nodes: tuple[str, ...], edges: tuple[tuple[str, str, int], ...],
                     source: str, sink: str,
                     mapping: dict[str, str],
                     target_nodes: tuple[str, ...],
                     target_edges: tuple[tuple[str, str, int], ...]) -> dict:
    """Transfer only after checking a capacity-preserving graph mapping.

    Do not infer real physical equivalence merely from similar descriptions.
    """
    if set(mapping) != set(nodes) or set(mapping.values()) != set(target_nodes) or len(set(mapping.values())) != len(mapping):
        return {"status": "HOLD", "reason": "mapping not a vertex bijection"}
    expected_edges = sorted((mapping[u], mapping[v], w) for u, v, w in edges)
    if expected_edges != sorted(target_edges):
        return {"status": "HOLD", "reason": "edges or capacities fail preservation"}
    source_receipt = exact_min_cut(nodes, edges, source, sink)
    target_receipt = exact_min_cut(target_nodes, target_edges,
                                   mapping[source], mapping[sink])
    mapped_cut = sorted(mapping[node] for node in source_receipt["source_side"])
    mapped_capacity = sum(w for u, v, w in target_edges if u in mapped_cut and v not in mapped_cut)
    if mapped_capacity != target_receipt["capacity"]:
        return {"status": "HOLD", "reason": "independent cut verification failed"}
    return {
        "operator": "STRUCTURAL_ANALOGY",
        "status": "EXACT_FINITE",
        "source_cut": source_receipt,
        "target_cut": target_receipt,
        "mapped_source_side": mapped_cut,
        "capacity_preserved": True,
        "question": "Where does this analogy fail when real constraints are restored?",
    }


def next_question(problem_kind: str) -> dict:
    """Human-authored router, NOT a learned or autonomous policy."""
    questions = {
        "remote_clocks": ("OPERATIONAL_REDEFINITION", "Which measurement assumption makes the target identifiable?"),
        "integer_sequence": ("CONJECTURE_THEN_FALSIFY", "What finite pattern survives fresh data, and what would prove it?"),
        "cross_domain_network": ("STRUCTURAL_ANALOGY", "Which relations must be preserved for transfer to be valid?"),
    }
    if problem_kind not in questions:
        return {"status": "HOLD", "question": "What evidence type and success condition define this problem?"}
    operator, question = questions[problem_kind]
    return {"status": "HYPOTHESIS_ONLY", "operator": operator, "question": question}
