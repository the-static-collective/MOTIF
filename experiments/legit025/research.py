"""LEGIT-025: detect a real aperture blind spot; generate a new question;
construct and verify a five-vertex observational source; reuse it later.

EXPERIMENTAL SCOPE: finite graph homomorphism counts, project-authored
algorithm selection, external-origin carrier graphs from the Read/Wilson
1998 Atlas. The generator is classical graph enumeration, NOT a newly
invented algorithm or general LLM-driven mathematical self-improvement.

The source graph grammar in LEGIT-021 *already supported* five vertices!
The actual contribution here is blind-spot discovery, parent-child
construction receipts, source selection, out-of-cohort transfer and
independent validation with strong same-grammar comparators.
"""
from __future__ import annotations

from collections import defaultdict
from functools import lru_cache
from hashlib import sha256
from itertools import combinations
from pathlib import Path
import json
import sys
from time import process_time_ns

HERE = Path(__file__).resolve().parent
for name in ("legit021", "legit022", "legit023"):
    sys.path.insert(0, str(HERE.parent / name))
from atlas import _networkx, _carrier, HOLD
from graph_inventor import grammar, reference_count, characterize
from methods import hom_count

STATUS = "RESEARCH_HOLD_NO_AUTONOMOUS_RECURSIVE_IMPROVEMENT"
TRAIN_COUNT = 4
HOLDOUT_COUNT = 6


def _graph(pattern):
    import networkx as nx
    n, edges = pattern
    obj = nx.Graph()
    obj.add_nodes_from(range(n))
    obj.add_edges_from(edges)
    return obj


def _degree(graph):
    n, edges = graph
    deg = [0] * n
    for u, v in edges:
        deg[u] += 1
        deg[v] += 1
    return tuple(sorted(deg))


def _spectrum(graph, patterns):
    return tuple(hom_count(source, graph)["value"] for source in patterns)


@lru_cache(maxsize=1)
def find_blindspots():
    """A rule-based discovery of observationally indistinguishable carriers.

    Search *all* external 7-vertex carriers using only old <=4 source
    outcomes, never any 5-vertex probe answers. Hence the heldout subset
    is selected after seeing low-level outcomes, but before new ones;
    this is deliberately not an externally blind benchmark.
    """
    nx, fingerprint, byte_count = _networkx()
    atlas = nx.graph_atlas_g()
    if len(atlas) != 1253:
        raise HOLD("external source corpus size drift")
    old = grammar()
    if len(old) != 10 or max(p[0] for p in old) != 4:
        raise HOLD("old source grammar drift")
    groups = defaultdict(list)
    for atlas_id, nx_graph in enumerate(atlas):
        if len(nx_graph) != 7:
            continue
        target = _carrier(nx_graph)
        degree = _degree(target)
        signature = _spectrum(target, old)
        groups[(degree, signature)].append((atlas_id, target))
    collision_groups = [members for members in groups.values()
                        if len(members) > 1]
    # Refuse any ambiguous non-two-way cluster: the paired-study design
    # does not know how to choose it without an explicit new protocol.
    if any(len(group) != 2 for group in collision_groups):
        raise HOLD("unexpected >2 graph collision cluster")
    pairs = []
    for members in collision_groups:
        a, b = sorted(members)
        # Independent graph isomorphism is a DIFFERENT acceptance contract:
        # confirm only that these aren't literally the same graph.
        if nx.is_isomorphic(_graph(a[1]), _graph(b[1])):
            raise HOLD("claimed collision is actually graph-isomorphic")
        if _spectrum(a[1], old) != _spectrum(b[1], old):
            raise HOLD("old source grammar unexpectedly distinguishes")
        pairs.append((tuple([a[0], b[0]]), (a[1], b[1])))
    pairs.sort(key=lambda x: x[0])
    if len(pairs) != TRAIN_COUNT + HOLDOUT_COUNT:
        raise HOLD("the predeclared finite collision cohort changed")
    return (
        tuple(pairs[:TRAIN_COUNT]), tuple(pairs[TRAIN_COUNT:]),
        {
            "source": "Read/Wilson 1998 Graph Atlas via NetworkX 3.4.2",
            "external_graph_data_sha256": fingerprint,
            "atlas_data_byte_count": byte_count,
            "seven_vertex_graphs_inspected": 1044,
            "old_connected_source_patterns": len(old),
            "collisions_found_after_seeing_old_probe_answers": len(pairs),
            "new_five_vertex_answers_not_seen_in_challenge_selection": True,
            "predeclared_training_pair_ids":
                [list(p[0]) for p in pairs[:TRAIN_COUNT]],
            "predeclared_heldout_pair_ids":
                [list(p[0]) for p in pairs[TRAIN_COUNT:]],
            "pair_selection_and_experiment_engineer_authored": True,
            "source_dataset_is_public_not_hidden_from_engineer": True,
        }
    )


@lru_cache(maxsize=1)
def generate_extensions():
    """Author-specified compositional operator, not autonomous invention.

    Extend every connected four-node source by a new vertex, attached
    to any nonempty subset of the four old vertices. Deduplicate by
    exact graph isomorphism; the resulting 21 structures should equal
    the already-existing classical grammar(5) minus grammar(4).
    Keep parent+operation receipt for the first (lowest arity) recipe.
    """
    import networkx as nx
    parents = tuple(p for p in grammar() if p[0] == 4)
    if len(parents) != 6:
        raise HOLD("unexpected connected four-node source count")
    generated = []
    # Prefer one-edge extensions where possible: minimal operator complexity.
    for arity in (1, 2, 3, 4):
        for parent in parents:
            for chosen in combinations(range(4), arity):
                source = (5, tuple(sorted(parent[1] +
                    tuple((v, 4) for v in chosen))))
                if any(nx.is_isomorphic(_graph(source), _graph(entry["source"]))
                       for entry in generated):
                    continue
                generated.append({
                    "source": source,
                    "parent": parent,
                    "operator": "ADD_VERTEX_WITH_NEIGHBORS",
                    "new_vertex_neighbors": chosen,
                    "operator_arity": arity,
                })
    # Compare against LEGIT-021's *already implemented* five-vertex
    # classical search grammar, to avoid pretending this is new math.
    classical5 = tuple(p for p in grammar(5) if p[0] == 5)
    if len(generated) != 21 or len(classical5) != 21:
        raise HOLD("unexpected five-vertex connected graph count")
    for item in generated:
        if sum(nx.is_isomorphic(_graph(item["source"]), _graph(other))
               for other in classical5) != 1:
            raise HOLD("composed source not equivalent to classical grammar")
    # Stable names are assigned only after generating; no target answers
    # or 5-probe outcomes are inspected to select these names.
    nx_obj, _, _ = _networkx()
    atlas = nx_obj.graph_atlas_g()
    atlas_5 = [(i, g) for i, g in enumerate(atlas)
               if len(g) == 5 and nx_obj.is_connected(g)]
    for item in generated:
        matches = [i for i, graph in atlas_5
                   if nx.is_isomorphic(_graph(item["source"]), graph)]
        if len(matches) != 1:
            raise HOLD("five-node atlas ID ambiguity")
        item["atlas_source_id"] = matches[0]
    return tuple(sorted(generated, key=lambda x: x["atlas_source_id"]))


def _training_coverage(training, sources):
    covered = {}
    # All five-vertex patterns incur the same conservative 7**5
    # mapping budget per target. True CPU may vary by source structure.
    for item in sources:
        found = []
        for ids, pair in training:
            counts = _spectrum_pair(pair, item["source"])
            if counts[0] != counts[1]:
                found.append(ids)
        covered[item["atlas_source_id"]] = found
    return covered


def _spectrum_pair(pair, source):
    return [hom_count(source, g)["value"] for g in pair]


def make_plan(training):
    """Training-only plan and explicit method-construction cartridge.

    The leaf-first strategy is a constrained, interpretable search; the
    unconstrained classical greedy strategy receives all 21 same-grammar
    sources and identical training answers. Neither sees heldout 5-probe
    outcomes before the order is SHA-256 frozen.
    """
    sources = generate_extensions()
    by_id = {entry["atlas_source_id"]: entry for entry in sources}
    coverage = _training_coverage(training, sources)
    leaf = [s for s in sources if s["operator_arity"] == 1]
    # Use maximum training support; classic tie-breaking by Atlas ID.
    leaf_order = sorted(leaf, key=lambda s: (
        -len(coverage[s["atlas_source_id"]]), s["atlas_source_id"]))
    composite = leaf_order + [s for s in sources if s not in leaf_order]
    # Strong classical greedy considers EVERY connected 5-vertex source
    # in exactly the same fixed source grammar and training dataset.
    unresolved = {ids for ids, _ in training}
    remaining = list(sources)
    classical = []
    while remaining:
        next_item = min(remaining, key=lambda s: (
            -len(unresolved.intersection(coverage[s["atlas_source_id"]])),
            s["atlas_source_id"]))
        classical.append(next_item)
        remaining.remove(next_item)
        unresolved.difference_update(coverage[next_item["atlas_source_id"]])
    if len(composite) != 21 or len(classical) != 21:
        raise HOLD("invalid candidate permutation")
    canonical = tuple(sources)
    policies = {
        "CANONICAL_FIVE_CLASSICAL": canonical,
        "STRONG_CLASSICAL_TRAINED_GREEDY": tuple(classical),
        "COMPOSED_LEAF_FIRST_TRAINED": tuple(composite),
    }
    frozen = {name: [p["atlas_source_id"] for p in sequence]
              for name, sequence in policies.items()}
    fingerprint = sha256(json.dumps(frozen, sort_keys=True,
              separators=(",", ":")).encode()).hexdigest()
    preferred = composite[0]
    reusable = {
        "kind": "TRAINING_FROZEN_PROBE_CARTRIDGE",
        "new_question": "Can a one-vertex extension of a previously known "
                        "four-vertex source distinguish these graphs?",
        "generated_source": characterize(preferred["source"]),
        "atlas_source_id": preferred["atlas_source_id"],
        "source_parent": characterize(preferred["parent"]),
        "construction": preferred["operator"],
        "added_vertex_neighbors": list(preferred["new_vertex_neighbors"]),
        "operator_arity": preferred["operator_arity"],
        "verified_training_coverage": [
            list(p) for p in coverage[preferred["atlas_source_id"]]],
        "selection_used_five_vertex_training_answers_only": True,
        "candidate_was_not_in_previous_four_vertex_grammar": True,
        "known_mathematical_invention": False,
        "classical_five_vertex_grammar_already_existed_in_LEGIT021": True,
        "source_frozen_sha256": fingerprint,
    }
    return policies, {
        "question_trigger": "ALL_PREVIOUS_CONNECTED_PROBES_UP_TO_FOUR "
                            "EQUAL_AND_CARRIERS_NONISOMORPHIC",
        "next_relevant_question": reusable["new_question"],
        "candidate_count": len(sources),
        "leaf_candidate_count": len(leaf),
        "training_coverage_by_atlas_five_source": {
            str(k): [list(x) for x in v] for k, v in coverage.items()},
        "policies_frozen_sha256": fingerprint,
        "frozen_source_orders": frozen,
        "selected_training_cartridge": reusable,
        "no_heldout_five_probe_answers_used": True,
    }


def complement(graph):
    n, edges = graph
    existing = set(edges)
    return n, tuple((a,b) for a in range(n) for b in range(a+1,n)
                    if (a,b) not in existing)


def universal_join(graph):
    n, edges = graph
    return n+1, tuple(sorted(edges + tuple((i,n) for i in range(n))))


def transfer_tasks(heldout):
    """Dissimilar evaluation settings, but correlated by construction!

    The heldout external Atlas pairs are also transformed by graph
    complement and adding a universal 8th node. These are synthetic
    derivatives of known carriers, NOT independently originated graph
    datasets or an independent next research generation.
    """
    result = {"atlas_original_7": tuple(heldout)}
    result["atlas_complements_7"] = tuple(
        (ids, tuple(complement(g) for g in graphs))
        for ids, graphs in heldout)
    result["atlas_join_universal_8"] = tuple(
        (ids, tuple(universal_join(g) for g in graphs))
        for ids, graphs in heldout)
    # Confirm the OLD tool remains insufficient on these future problems.
    for family, cases in result.items():
        for ids, graphs in cases:
            if _spectrum(graphs[0], grammar()) != _spectrum(graphs[1], grammar()):
                raise HOLD("old grammar already distinguishes transformed pair")
    return result


def _evaluate(cases, source_order, method):
    rows = []
    begin = process_time_ns()
    for ids, graphs in cases:
        observed = []
        for source in source_order:
            pair_counts = _spectrum_pair(graphs, source)
            verified = [reference_count(source, g) for g in graphs]
            if pair_counts != verified:
                raise HOLD("new question disagrees with independent enumerator")
            observed.append({
                "source": characterize(source),
                "counts": pair_counts,
                "independent_enumerator_agrees": True,
                "separates": pair_counts[0] != pair_counts[1],
            })
            if observed[-1]["separates"]:
                break
        rows.append({
            "atlas_parent_pair_ids": list(ids),
            "resolved_by_hom_witness": bool(observed and
                                             observed[-1]["separates"]),
            "questions": len(observed),
            "all_attempted_question_receipts": observed,
        })
    return {
        "method": method, "total_questions": sum(x["questions"] for x in rows),
        "resolved": sum(x["resolved_by_hom_witness"] for x in rows),
        "cases": len(cases), "cpu_ms_with_independent_per_question_check":
            round((process_time_ns()-begin) / 1e6, 5),
        "all_question_receipts": rows,
    }


def _trial():
    train, heldout, origin = find_blindspots()
    policies, plan = make_plan(train)
    frozen = json.dumps(plan["frozen_source_orders"], sort_keys=True,
                         separators=(",", ":")).encode()
    if sha256(frozen).hexdigest() != plan["policies_frozen_sha256"]:
        raise HOLD("source plan changed after freeze")
    branches = transfer_tasks(heldout)
    old4 = grammar()
    outcomes = {}
    for family, cases in branches.items():
        variants = {"NO_ADAPTATION_OLD_FOUR": _evaluate(cases, old4,
                                                       "NO_ADAPTATION_OLD_FOUR")}
        for label, source_plan in policies.items():
            variants[label] = _evaluate(cases, [x["source"] for x in source_plan],
                                         label)
        outcomes[family] = variants

    if outcomes["atlas_original_7"]["NO_ADAPTATION_OLD_FOUR"]["resolved"] != 0:
        raise HOLD("old grammar unexpectedly solved the gap")
    return {
        "experiment": "MOTIF-LEGIT-025",
        "title": "APERTURE ESCAPE: A LEARNED FIFTH-VERTEX QUESTION",
        "status": STATUS,
        "origin": origin,
        "training_pairs": len(train),
        "heldout_original_pairs": len(heldout),
        "generation": {
            "rule": "ADD_NEW_VERTEX_TO_ANY_NONEMPTY_NEIGHBOR_SUBSET",
            "generated_unlabeled_connected_5_patterns": 21,
            "same_as_LEGIT021_existing_classical_5_grammar": True,
            "not_autonomous_algorithm_invention": True,
        },
        "training_frozen_plan": plan,
        "transferred_research": outcomes,
        "limitations": [
            "Original external Atlas graphs only; graph pairs engineer-selected",
            "Task selection intentionally conditioned on old-probe failure",
            "All generated fifth-vertex source types are established graph theory",
            "Heldout complement and universal-join cases are dependent transformations",
            "Existing LEGIT-021 grammar already supported connected graphs to five",
            "No new formal mathematical theorem or historical novelty",
            "Only one constructed probe-selection episode; not autonomous compounding",
            "No full human research or engineering opportunity-cost accounting",
        ],
    }


def run():
    result = _trial()
    return result


if __name__ == "__main__":
    if sys.argv[1:] != ["--emit"]:
        raise SystemExit("Usage: python experiments/legit025/research.py --emit")
    print(json.dumps(run(), indent=2, sort_keys=True))
