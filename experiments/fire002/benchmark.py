"""FIRE-002 matched-budget learning experiment; no labels enter policy."""
from __future__ import annotations

from math import sqrt
from productive import run

TRAIN = range(6100, 6180)
TEST = range(42000, 42200)
WEIGHTS = (0., .5, 1., 2., 4.)
POLICIES = ('value', 'ratio', 'information', 'fire001',
            'productive_frozen', 'productive_online')
REGIMES = ('steady', 'drift', 'correlated')


def average(rows):
    fields = ('verified_value', 'certified_questions', 'failed_verifications',
              'questions_unlocked', 'steps', 'learning_events')
    return {key: round(sum(r[key] for r in rows) / len(rows), 5)
            for key in fields}


def pair(a, b):
    ds = [x['verified_value'] - y['verified_value'] for x, y in zip(a, b)]
    mean = sum(ds) / len(ds)
    sd = sqrt(sum((d - mean) ** 2 for d in ds) / (len(ds) - 1))
    ci = 1.96 * sd / sqrt(len(ds))
    return {'difference': round(mean, 5),
            'approx_95pct_interval': [round(mean - ci, 5), round(mean + ci, 5)]}


def experiment():
    # Train ONCE using the designated stable training family, then freeze.
    scores = {}
    for weight in WEIGHTS:
        trials = [run(seed, 'steady', 'productive_online', weight)
                  for seed in TRAIN]
        scores[weight] = average(trials)['verified_value']
    weight = max(WEIGHTS, key=lambda w: (scores[w], -w))
    results = {'experiment': 'FIRE-002', 'scope': 'synthetic only',
               'train_seed_range': [TRAIN.start, TRAIN.stop - 1],
               'test_seed_range': [TEST.start, TEST.stop - 1],
               'training_score_by_weight': {str(k): v for k, v in scores.items()},
               'selected_spark_weight': weight, 'regimes': {}}
    for regime in REGIMES:
        trials = {policy: [run(seed, regime, policy, weight) for seed in TEST]
                  for policy in POLICIES}
        results['regimes'][regime] = {
            'summaries': {p: average(trials[p]) for p in POLICIES},
            'paired_online_minus_classical_ratio': pair(
                trials['productive_online'], trials['ratio']),
            'paired_online_minus_fire001': pair(
                trials['productive_online'], trials['fire001']),
            'paired_online_minus_frozen': pair(
                trials['productive_online'], trials['productive_frozen']),
        }
    return results


if __name__ == '__main__':
    import json
    print(json.dumps(experiment(), indent=2, sort_keys=True))
