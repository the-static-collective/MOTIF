"""LEGIT-025 future research carriers sampled independently of Atlas examples.

The *sampling population* is disjoint from and not transformed from the
Read/Wilson graph inputs: 1,000 seeded Erdős–Rényi G(8,1/2) labeled graphs.
The generator and filtering protocol are engineer-authored, not externally
sourced, blinded or statistically representative. Selection depends only
on source probes <=4, never on the composed five-vertex answers.
"""
from __future__ import annotations

from collections import defaultdict
from functools import lru_cache
from random import Random

RANDOM_SEED = 25025
NUMBER_DRAWS = 1000
FUTURE_CASES = 8


@lru_cache(maxsize=1)
def independent_synthetic_eight():
    import networkx as nx
    from graph_inventor import grammar
    from research import _degree, _graph, _spectrum, HOLD

    rng=Random(RANDOM_SEED)
    groups=defaultdict(list)
    old=grammar()
    for i in range(NUMBER_DRAWS):
        edges = tuple((u,v) for u in range(8) for v in range(u+1,8)
                      if rng.randrange(2))
        target = (8,edges)
        signature=(_degree(target),_spectrum(target,old))
        groups[signature].append((i,target))
    candidates=[]
    for items in groups.values():
        if len(items)<2:
            continue
        # Avoid graph-isomorphic duplicates in random labeled draws.
        answer=None
        for i, left in enumerate(items):
            for right in items[i+1:]:
                if not nx.is_isomorphic(_graph(left[1]),_graph(right[1])):
                    answer=(tuple(sorted((left[0],right[0]))),
                            (left[1],right[1]))
                    break
            if answer is not None:
                break
        if answer is not None:
            candidates.append(answer)
    candidates.sort(key=lambda item: item[0])
    if len(candidates) < FUTURE_CASES:
        raise HOLD("seeded eight-vertex population has too few blind spots")
    selected=tuple(candidates[:FUTURE_CASES])
    return selected, {
        "generator": "ENGINEER_AUTHORED_SEEDED_GNP_RANDOM_GRAPH",
        "draws": NUMBER_DRAWS, "vertex_count": 8,
        "edge_probability": "1/2",
        "random_seed": RANDOM_SEED,
        "candidate_old_four_probe_blind_pairs": len(candidates),
        "selected_sample_index_pairs": [list(i) for i,_ in selected],
        "not_derived_from_seven_vertex_Atlas_pairs": True,
        "no_five_vertex_responses_used_for_challenge_selection": True,
        "not_independently_authored_or_externally_blinded": True,
    }
