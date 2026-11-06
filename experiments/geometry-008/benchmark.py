"""Synthetic scale check and classical matched one-edge baseline.

Call `python benchmark.py --expansions 16000` for the optional disk stress
experiment. All counts are measured at runtime; no fixed total graph cap.
"""
import argparse
import json
import random
import tempfile
import time
from pathlib import Path
from living_graph import LivingGraph, RewriteGrammar, RewriteRule
from repair import World, discover_composition


def dataset(seed=20261106, count=100, *, prefix='heldout'):
    rng = random.Random(seed)
    rows = []
    for i in range(count):
        middle = f'{prefix}-middle-{i}'
        if i % 2 == 0:
            edges = [('s', 'carry', middle), (middle, 'serve', 'g')]
            expected = True
        else:
            edges = [('s', 'serve', middle), (middle, 'carry', 'g')]
            expected = False
        # Disconnected noise cannot accidentally create another s->g path.
        for j in range(rng.randrange(0, 5)):
            edges.append((f'{prefix}-junk-{i}-{j}', rng.choice(['carry', 'serve']),
                          f'{prefix}-extra-{i}-{j}'))
        rows.append(World(f'{prefix}-{i}', 'benchmark', tuple(edges), expected,
                          f'fixture:{prefix}-{i}'))
    return tuple(rows)


def main(expansions=1200):
    if type(expansions) is not int or expansions <= 0:
        raise ValueError('expansions must be positive integer')
    train, heldout = dataset(count=20, prefix='train'), dataset(count=100, prefix='heldout')
    repaired = discover_composition(train, heldout, start='s', goal='g', work_budget=64)
    with tempfile.TemporaryDirectory() as temp:
        file = Path(temp) / 'large.sqlite'
        grammar = RewriteGrammar('benchmark', (
            RewriteRule('left', ('#',), ('0', '#')),
            RewriteRule('right', ('#',), ('1', '#')),
        ))
        with LivingGraph(file, scope='benchmark') as graph:
            graph.seed(['#'])
            t0 = time.perf_counter()
            first = graph.grow(grammar, work_budget=expansions // 2)
            second = graph.grow(grammar, work_budget=expansions - expansions // 2)
            elapsed = round(time.perf_counter() - t0, 3)
            counts = graph.counts()
            integrity = graph.verify()
        return {'experiment': 'GEOM-008 synthetic growth & composition',
                'requested_expansions': expansions,
                'growth': {'first_slice_nodes': first['totals']['nodes'],
                           'total_nodes': counts['nodes'],
                           'total_relations': counts['relations'],
                           'frontier_remaining': counts['unexpanded'],
                           'elapsed_seconds_environment_specific': elapsed,
                           'sqlite_allocated_bytes': counts['db_bytes_allocated_approx'],
                           'integrity': integrity},
                'operator_search': {'status': repaired['status'],
                                    'length': repaired['length'],
                                    'operator': repaired['program'],
                                    'train': repaired['train'],
                                    'heldout': repaired['heldout'],
                                    'matched_best_atomic_baseline': repaired['baseline_single_relation'],
                                    'authority': 'NONE'},
                'disclaimer': 'no visual geometry required; developer-generated train/test share structural generator; scale is machine dependent'}


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--expansions', type=int, default=1200)
    args = ap.parse_args()
    print(json.dumps(main(args.expansions), indent=2, sort_keys=True))
