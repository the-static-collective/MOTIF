"""FIELD-001: bounded fact -> idea -> relation -> fact expansion.

Graph edit ideas are *not* facts until checked against an independent,
source-attributed graph corpus. The relation grammar and all graphs are finite.
No real-world actions, model training, or original mathematical discoveries.
"""
from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
import hashlib
import json
from itertools import combinations
from typing import Callable

import networkx as nx

N = 5
EDGES = tuple(combinations(range(N), 2))
SEED_EDGES = ((0, 1), (1, 2), (2, 3), (3, 4))  # P5, source verified below
SEED_MASK = sum(1 << EDGES.index(edge) for edge in SEED_EDGES)
SOURCE = "Read & Wilson, An Atlas of Graphs (1998); NetworkX graph_atlas_g"


def graph(mask: int, n: int = N) -> nx.Graph:
    pairs = tuple(combinations(range(n), 2))
    if not 0 <= mask < (1 << len(pairs)):
        raise ValueError("mask outside fixed graph universe")
    g = nx.Graph()
    g.add_nodes_from(range(n))
    g.add_edges_from(edge for i, edge in enumerate(pairs) if mask & (1 << i))
    return g


def description(g: nx.Graph) -> dict:
    """Properties are computed by NetworkX, not the proposal grammar."""
    n, m = g.number_of_nodes(), g.number_of_edges()
    c = nx.number_connected_components(g) if n else 0
    return {"n": n, "m": m, "components": c,
            "cycle_rank": m - n + c, "connected": bool(n and c == 1),
            "forest": nx.is_forest(g), "tree": nx.is_tree(g) if n else False}


class AtlasOracle:
    """Unmodified third-party Graph Atlas acts as a finite external corpus.

    This does NOT authenticate its historical authors or independently prove
    its correctness; the corpus and evaluator implementation are separate from
    the idea generator. Only a fixed n vertex slice is checked.
    """
    def __init__(self, n: int = N):
        self.n = n
        self.source_graphs = [(i, g) for i, g in enumerate(nx.graph_atlas_g())
                              if g.number_of_nodes() == n]
        self.dataset_sha256 = hashlib.sha256(json.dumps([
            {"id": i, "edges": sorted(tuple(sorted(e)) for e in g.edges())}
            for i, g in self.source_graphs], separators=(",", ":"))
            .encode()).hexdigest()
        self.queries = 0

    def observe(self, mask: int) -> dict:
        g = graph(mask, self.n)
        self.queries += 1
        matches = [i for i, candidate in self.source_graphs
                   if nx.is_isomorphic(g, candidate)]
        if len(matches) != 1:
            raise AssertionError("Atlas corpus did not give a unique graph type")
        data = {"source": SOURCE, "version": nx.__version__,
                "dataset_sha256": self.dataset_sha256,
                "atlas_id": matches[0], "properties": description(g),
                "edge_mask": mask, "n": self.n}
        data["receipt_sha256"] = hashlib.sha256(json.dumps(
            data, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        return data


def verify_receipt(receipt: dict, oracle: AtlasOracle) -> bool:
    """Recheck against source corpus, never trust a digest as authority."""
    try:
        payload = {k: v for k, v in receipt.items() if k != "receipt_sha256"}
        if hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"))
                          .encode()).hexdigest() != receipt["receipt_sha256"]:
            return False
        return oracle.observe(receipt["edge_mask"]) == receipt
    except (KeyError, TypeError, ValueError, AssertionError):
        return False


def expand(seed: int = SEED_MASK, depth: int = 3, n: int = N,
           observer: Callable[[int], dict] | None = None) -> dict:
    """Generate *ideas first*; only the observer can promote to facts.

    A source is never silently assumed, and all paths remain in provenance.
    An ordinary labeled-state cache avoids repeated external corpus queries.
    """
    if not 0 <= depth <= 4 or n != N:
        raise ValueError("FIELD-001 is deliberately bounded to five vertices and 0..4 rounds")
    if observer is None:
        raise ValueError("an observation source is required")
    original = observer(seed)
    facts = {seed: {"state": seed, "generation": 0, "evidence": original}}
    queue = deque([(seed, 0)])
    relations = []
    ideas = set()
    attempts = 0
    while queue:
        mask, generation = queue.popleft()
        if generation >= depth:
            continue
        for bit, edge in enumerate(EDGES):
            child = mask ^ (1 << bit)
            attempts += 1
            ideas.add(child)
            op = "REMOVE" if mask & (1 << bit) else "ADD"
            relations.append({"from": mask, "to": child, "operation": op,
                              "edge": edge, "parent_generation": generation,
                              "status": "hypothesis_until_observed"})
            if child not in facts:
                evidence = observer(child)
                facts[child] = {"state": child, "generation": generation + 1,
                                "evidence": evidence}
                queue.append((child, generation + 1))
    # A relation stays a proposed claim until both endpoints are observed.
    for relation in relations:
        relation["status"] = "both_endpoints_observed" if (
            relation["from"] in facts and relation["to"] in facts) else "HOLD"
    return {"seed": seed, "depth": depth, "facts": facts,
            "ideas": ideas, "relations": relations, "attempts": attempts}


def transition_rows(field: dict) -> list[dict]:
    """One row per observed directed proposal; includes repeated paths."""
    rows = []
    for relation in field["relations"]:
        before = field["facts"][relation["from"]]["evidence"]["properties"]
        after = field["facts"][relation["to"]]["evidence"]["properties"]
        rows.append({"operation": relation["operation"],
                     "parent_tree": before["tree"],
                     "parent_connected": before["connected"],
                     "parent_forest": before["forest"],
                     "delta_components": after["components"] - before["components"],
                     "delta_cycle_rank": after["cycle_rank"] - before["cycle_rank"],
                     "post_tree": after["tree"],
                     "post_connected": after["connected"]})
    return rows


CONDITIONS = ("all", "parent_tree", "parent_connected", "parent_forest")
TARGETS = ("delta_components", "delta_cycle_rank", "post_tree", "post_connected")


def condition_holds(row: dict, condition: str) -> bool:
    return condition == "all" or row[condition] is True


def mine_hypotheses(train_rows: list[dict], min_support: int = 4) -> list[dict]:
    """A tiny declared search grammar; no semantic invention is claimed."""
    proposals = []
    for op in ("ADD", "REMOVE"):
        for context in CONDITIONS:
            sub = [r for r in train_rows if r["operation"] == op and condition_holds(r, context)]
            if len(sub) < min_support:
                continue
            for target in TARGETS:
                values = set(r[target] for r in sub)
                if len(values) == 1:
                    proposals.append({"operation": op, "condition": context,
                                      "target": target, "predicted": next(iter(values)),
                                      "train_support": len(sub), "status": "HYPOTHESIS"})
    return proposals


def independent_atlas_rows(n: int = 6) -> list[dict]:
    """Holdout: *different-sized* original Atlas graphs, not seed descendants.

    This set is accessed only in the post-freeze evaluator. The graph edits
    are independent of the five-vertex training representation.
    """
    rows = []
    for atlas_id, source in enumerate(nx.graph_atlas_g()):
        if source.number_of_nodes() != n:
            continue
        before = description(source)
        for u, v in combinations(range(n), 2):
            after_g = source.copy()
            has = after_g.has_edge(u, v)
            if has:
                after_g.remove_edge(u, v)
            else:
                after_g.add_edge(u, v)
            after = description(after_g)
            rows.append({"operation": "REMOVE" if has else "ADD",
                         "parent_tree": before["tree"],
                         "parent_connected": before["connected"],
                         "parent_forest": before["forest"],
                         "delta_components": after["components"] - before["components"],
                         "delta_cycle_rank": after["cycle_rank"] - before["cycle_rank"],
                         "post_tree": after["tree"],
                         "post_connected": after["connected"],
                         "source_atlas_n": n, "source_atlas_id": atlas_id,
                         "edit_edge": (u, v)})
    return rows


def evaluate(hypotheses: list[dict], heldout: list[dict]) -> list[dict]:
    results = []
    for h in hypotheses:
        applicable = [r for r in heldout if r["operation"] == h["operation"]
                      and condition_holds(r, h["condition"])]
        failures = [r for r in applicable if r[h["target"]] != h["predicted"]]
        results.append({**h, "holdout_support": len(applicable),
                        "holdout_failures": len(failures),
                        "counterexample": None if not failures else {
                            "observed": failures[0][h["target"]],
                            "source_atlas_id": failures[0]["source_atlas_id"],
                            "edit_edge": failures[0]["edit_edge"],
                            "context": h["condition"], "operation": h["operation"]},
                        "status": ("FINITE_HOLDOUT_SUPPORTED" if applicable and not failures
                                   else "REFUTED" if failures else "HOLD_NO_COVERAGE")})
    return results


def frozen_digest(hypotheses: list[dict]) -> str:
    return hashlib.sha256(json.dumps(hypotheses, sort_keys=True,
                       separators=(",", ":")).encode()).hexdigest()


def ancestry(field: dict) -> list[dict]:
    """Return a connected 0 -> 1 -> ... -> depth lineage, not unrelated samples."""
    depth = field["depth"]
    if depth == 0:
        return []
    child = min(m for m, f in field["facts"].items() if f["generation"] == depth)
    chain = []
    while child != field["seed"]:
        gen = field["facts"][child]["generation"]
        relation = next(r for r in field["relations"] if r["to"] == child and
                        field["facts"][r["from"]]["generation"] == gen - 1)
        receipt = field["facts"][child]["evidence"]
        chain.append({"generation": gen, "from_state": relation["from"],
                      "to_state": child, "edit": relation["operation"],
                      "edge": relation["edge"], "atlas_id": receipt["atlas_id"],
                      "receipt_sha256": receipt["receipt_sha256"]})
        child = relation["from"]
    return list(reversed(chain))


def run(depth: int = 3) -> dict:
    oracle = AtlasOracle(n=N)
    field = expand(depth=depth, observer=oracle.observe)
    n_observations = oracle.queries
    train = transition_rows(field)
    # Train and freeze BOTH stages before looking at the six-node heldout data.
    stage1 = [row for row, relation in zip(train, field["relations"])
              if relation["parent_generation"] == 0]
    early_h = mine_hypotheses(stage1, min_support=3)
    late_h = mine_hypotheses(train, min_support=3)
    early_frozen = frozen_digest(early_h)
    late_frozen = frozen_digest(late_h)
    heldout = independent_atlas_rows(n=6)
    early = evaluate(early_h, heldout)
    late = evaluate(late_h, heldout)
    observed_by_depth = {str(d): sum(f["generation"] == d for f in field["facts"].values())
                         for d in range(depth + 1)}
    # Independent exhaustive classical reference; no graph oracle or MOTIF search.
    from math import comb
    classical_reachable = sum(comb(len(EDGES), i) for i in range(depth + 1))
    assert len(field["facts"]) == classical_reachable
    stage_summary = lambda rs: {"hypotheses_mined": len(rs),
             "finite_supported": sum(x["status"] == "FINITE_HOLDOUT_SUPPORTED" for x in rs),
             "refuted": sum(x["status"] == "REFUTED" for x in rs)}
    return {"experiment": "FIELD-001", "source": SOURCE,
            "networkx_version": nx.__version__, "dataset_sha256": oracle.dataset_sha256,
            "seed": {"mask": SEED_MASK, "edges": SEED_EDGES,
                     "atlas_id": field["facts"][SEED_MASK]["evidence"]["atlas_id"],
                     "receipt_sha256": field["facts"][SEED_MASK]["evidence"]["receipt_sha256"]},
            "depth": depth, "facts_total_including_seed": len(field["facts"]),
            "new_facts_observed": len(field["facts"]) - 1,
            "facts_by_generation": observed_by_depth,
            "distinct_atlas_graph_types": len({v["evidence"]["atlas_id"] for v in field["facts"].values()}),
            "proposed_ideas_distinct_including_seed": len(field["ideas"]),
            "relation_paths": len(field["relations"]),
            "naive_source_queries": field["attempts"] + 1,
            "cached_source_queries": n_observations,
            "query_reduction": round(1 - n_observations / (field["attempts"] + 1), 6),
            "hypothesis_grammar": {"conditions": CONDITIONS, "targets": TARGETS},
            "stage1": {"train_relations": len(stage1),
                       "frozen_sha256": early_frozen, **stage_summary(early),
                       "hypotheses": early},
            "stage3": {"train_relations": len(train),
                       "frozen_sha256": late_frozen, **stage_summary(late),
                       "hypotheses": late},
            "heldout_atlas_graphs": 156,
            "heldout_relation_cases": len(heldout),
            "example_chain": ancestry(field),
            "strong_classical_baseline": {
                "method": "Independent exhaustive Hamming-ball count, with identical labeled-state memoization",
                "reachable_labeled_states": classical_reachable,
                "equal_to_field": classical_reachable == len(field["facts"]),
                "query_count_with_same_cache": classical_reachable},
            "limitations": ["all graph edits, hypothesis conditions and targets are human-authored",
                            "finite 5-vertex source; 6-vertex holdout from the same historical graph corpus",
                            "Atlas package is not a live independent human referee",
                            "finite agreement does not establish a universal theorem",
                            "query reductions reflect classical memoization, not novel learning",
                            "no autonomous invention, new mathematics, or proven compounding intelligence"]}


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
