"""LEGIT-026 research environments.

Training: known Atlas-025 training pairs, its already-observed synthetic
seed 25025, and new training-only eight-node random graph seeds 26001/26002.
Future evaluation: two unrehearsed disjoint seeded eight-node worlds
26003/26004, plus a clearly labeled known Atlas regression slice.

These tasks are selected because the old <=4 probe grammar fails.
Engineer-selected/generated, public and *not independently blinded*.
No candidate five-node answer is used to select graph pairs.
"""
from __future__ import annotations

from collections import defaultdict
from functools import lru_cache
from random import Random

from research import (_degree, _spectrum, _graph, find_blindspots,
                      grammar, HOLD)

TRAIN_SEEDS = (26001, 26002)
EVAL_SEEDS = (26003, 26004)
DRAWS_PER_SEED = 1000
PER_WORLD_LIMIT = 8
MIN_WORLD_CASES = 4

@lru_cache(maxsize=8)
def synthetic_world(seed):
    import networkx as nx
    if seed not in TRAIN_SEEDS + EVAL_SEEDS:
        raise HOLD("unregistered random-world seed")
    rng = Random(seed)
    buckets = defaultdict(list)
    old = grammar()
    for index in range(DRAWS_PER_SEED):
        graph = (8, tuple((u, v) for u in range(8)
                          for v in range(u+1, 8) if rng.randrange(2)))
        buckets[(_degree(graph), _spectrum(graph, old))].append(
            (index, graph))
    # Deterministic pairing from old-grammar observations only.
    pairs = []
    for cluster in buckets.values():
        if len(cluster) < 2:
            continue
        match = None
        for i, a in enumerate(cluster):
            for b in cluster[i+1:]:
                if not nx.is_isomorphic(_graph(a[1]), _graph(b[1])):
                    match = ((a[0], b[0]), (a[1], b[1]))
                    break
            if match:
                break
        if match:
            pairs.append(match)
    pairs.sort(key=lambda row: row[0])
    if len(pairs) < MIN_WORLD_CASES:
        raise HOLD("random research world has insufficient old-grammar failures")
    return tuple(pairs[:PER_WORLD_LIMIT]), {
        "seed": seed,
        "draws": DRAWS_PER_SEED,
        "source": "ENGINEER_GENERATED_GNP_8_ONE_HALF",
        "old_grammar_blindspot_candidates": len(pairs),
        "selected_indices": [list(ids) for ids, _ in pairs[:PER_WORLD_LIMIT]],
        "selection_uses_only_degree_and_old_four_probe_outcomes": True,
        "five_node_answer_unseen_during_selection": True,
        "not_externally_blinded": True,
    }

@lru_cache(maxsize=1)
def training_worlds():
    from new_population import independent_synthetic_eight
    atlas_train, _, origin = find_blindspots()
    previously_seen, previous_origin = independent_synthetic_eight()
    worlds = {
        "atlas_old_training": tuple(atlas_train),
        "prior_025_random_8": tuple(previously_seen),
    }
    receipts = {"atlas": origin, "prior_random": previous_origin}
    for seed in TRAIN_SEEDS:
        name = "research_train_seed_%d" % seed
        cases, receipt = synthetic_world(seed)
        worlds[name] = cases
        receipts[name] = receipt
    return worlds, receipts

@lru_cache(maxsize=1)
def evaluation_worlds():
    """Separate call! No future probe results may enter training selectors."""
    _, atlas_eval, _ = find_blindspots()
    worlds = {"known_atlas_regression": tuple(atlas_eval)}
    receipts = {
        "known_atlas_regression": {
            "source": "PREVIOUSLY_USED_025_ATLAS_HELDOUT_NOT_NEW"
        }
    }
    for seed in EVAL_SEEDS:
        name = "future_seed_%d" % seed
        cases, receipt = synthetic_world(seed)
        worlds[name] = cases
        receipts[name] = receipt
    return worlds, receipts
