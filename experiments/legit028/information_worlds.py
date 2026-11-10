"""LEGIT-028: three different exact question/answer geometries.

Graph outputs: unbounded nonnegative exact graph-homomorphism counts.
Polynomial outputs: finite modular integers.
Constraint outputs: Boolean satisfiability values.

Engineer-authored worlds and old-grammar-failure filtering. All future
worlds use NEW, separately seeded inputs but are NOT independently sourced,
blinded, or representative of open-world research.
"""
from __future__ import annotations

from collections import defaultdict
from functools import lru_cache
from pathlib import Path
from random import Random
import sys

HERE = Path(__file__).resolve().parent
for name in ("legit021", "legit022", "legit023", "legit025", "legit026",
             "legit027"):
    sys.path.insert(0, str(HERE.parent / name))

import networkx as nx
from graph_inventor import grammar, reference_count
from methods import hom_count
from research import (_degree, _graph, _spectrum, generate_extensions, HOLD)
from worlds import training_worlds as prior_graph_training
import tasks as previous_math

DOMAINS = ("graph_hom_witness",) + previous_math.DOMAINS
GRAPH_FUTURE_SEEDS = (28001, 28002)
MATH_FUTURE_SEEDS = (28011, 28012)
FUTURE_DRAW_COUNT = 1000
GRAPH_PAIR_LIMIT = 8
MATH_CASES_PER_WORLD = 16


def candidate_questions(domain):
    if domain == "graph_hom_witness":
        return tuple(entry["atlas_source_id"] for entry in
                     generate_extensions())
    if domain in previous_math.DOMAINS:
        return previous_math.questions(domain)
    raise HOLD("unknown research contract")


@lru_cache(1)
def graph_source_by_id():
    return {row["atlas_source_id"]: row["source"] for row in
            generate_extensions()}


def observation(domain, case, question):
    if domain == "graph_hom_witness":
        a, b = case["payload"]
        source = graph_source_by_id()[question]
        return (hom_count(source, a)["value"],
                hom_count(source, b)["value"])
    if domain in previous_math.DOMAINS:
        return tuple(previous_math.observe(domain, case["payload"], question))
    raise HOLD("unknown goal")


def independent_observation(domain, case, question):
    if domain == "graph_hom_witness":
        a, b = case["payload"]
        source = graph_source_by_id()[question]
        return (reference_count(source, a),
                reference_count(source, b))
    if domain in previous_math.DOMAINS:
        return tuple(previous_math.independent_observe(
            domain, case["payload"], question))
    raise HOLD("unknown goal")


def is_witness(pair):
    return pair[0] != pair[1]


def _label_graph(world, cases):
    return tuple({"id": world + "_" + str(ids[0]) + "_" + str(ids[1]),
                  "payload": tuple(targets)}
                 for ids, targets in cases)


def _label_math(domain, cases):
    return tuple({"id": case["case_id"], "payload": case}
                 for case in cases)


@lru_cache(1)
def training_worlds():
    graph_worlds, graph_origin = prior_graph_training()
    result = {"graph_hom_witness": {
        name: _label_graph(name, pairs)
        for name, pairs in graph_worlds.items()}}
    provenance = {"graph_hom_witness": graph_origin}
    for domain in previous_math.DOMAINS:
        groups = {}
        origin = {}
        for seed in previous_math.TRAIN_SEEDS:
            cases, details = previous_math.world(domain, seed)
            name = "math_train_seed_" + str(seed)
            groups[name] = _label_math(domain, cases)
            origin[name] = details
        result[domain] = groups
        provenance[domain] = origin
    return result, provenance


@lru_cache(maxsize=4)
def future_graph_world(seed):
    if seed not in GRAPH_FUTURE_SEEDS:
        raise HOLD("unregistered graph future")
    rng = Random(seed)
    buckets = defaultdict(list)
    old = grammar()
    for index in range(FUTURE_DRAW_COUNT):
        source = (8, tuple((i, j) for i in range(8)
                           for j in range(i+1, 8) if rng.randrange(2)))
        buckets[(_degree(source), _spectrum(source, old))].append(
            (index, source))
    choices = []
    for items in buckets.values():
        match = None
        for ix, a in enumerate(items):
            for b in items[ix+1:]:
                if not nx.is_isomorphic(_graph(a[1]), _graph(b[1])):
                    match = ((a[0], b[0]), (a[1], b[1]))
                    break
            if match is not None:
                break
        if match is not None:
            choices.append(match)
    choices.sort(key=lambda row: row[0])
    if len(choices) < GRAPH_PAIR_LIMIT:
        raise HOLD("new graph population contains too few blind spots")
    selected = tuple(choices[:GRAPH_PAIR_LIMIT])
    return _label_graph("graph_future_" + str(seed), selected), {
        "seed": seed, "random_graph_draws": FUTURE_DRAW_COUNT,
        "selected_old_four_source_blindspots": GRAPH_PAIR_LIMIT,
        "total_old_source_blindspot_pairs": len(choices),
        "selection_used_five_source_outcomes": False,
        "source": "ENGINEER_GENERATED_SEEDED_GNP8",
        "not_externally_blinded": True,
    }


@lru_cache(maxsize=4)
def future_math_world(domain, seed):
    if domain not in previous_math.DOMAINS or seed not in MATH_FUTURE_SEEDS:
        raise HOLD("unregistered math future")
    rng = Random(seed + 1_000_003*previous_math.DOMAINS.index(domain))
    cases = []
    attempts = 0
    q = previous_math.questions(domain)
    while len(cases) < MATH_CASES_PER_WORLD and attempts < 50000:
        attempts += 1
        candidate = (previous_math._random_poly(rng) if
                     domain == previous_math.DOMAINS[0] else
                     previous_math._random_constraint(rng))
        item = {"id": domain + "_future_" + str(seed) + "_" +
                str(len(cases)), "payload": {
                    "objects": candidate["objects"]}}
        if any(is_witness(observation(domain, item, qq))
               for qq in q[:2]):
            continue
        if not any(is_witness(observation(domain, item, qq))
                   for qq in q):
            continue
        if not previous_math.oracle_nonidentical(domain, item["payload"]):
            raise HOLD("selected false mathematical distinction")
        cases.append(item)
    if len(cases) != MATH_CASES_PER_WORLD:
        raise HOLD("insufficient future mathematical counterexamples")
    return tuple(cases), {
        "seed": seed,
        "selection_attempts": attempts,
        "case_count": len(cases),
        "source": "ENGINEER_AUTHORED_SEEDED_MATH_FIXTURES",
        "selected_for_old_probe_failure": True,
        "witness_existence_checked_during_generation": True,
        "not_externally_blinded": True,
    }


def future_worlds():
    """Must only be called after all strategy-selection hashes are frozen."""
    results = {"graph_hom_witness": {}}
    origin = {"graph_hom_witness": {}}
    for seed in GRAPH_FUTURE_SEEDS:
        label = "graph_future_seed_" + str(seed)
        results["graph_hom_witness"][label], origin["graph_hom_witness"][
            label] = future_graph_world(seed)
    for domain in previous_math.DOMAINS:
        results[domain], origin[domain] = {}, {}
        for seed in MATH_FUTURE_SEEDS:
            label = "math_future_seed_" + str(seed)
            results[domain][label], origin[domain][label] = future_math_world(
                domain, seed)
    return results, origin
