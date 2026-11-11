"""Frozen FIRE-004 prequential stress test. No fitting on test regimes/seeds."""
from __future__ import annotations
from math import sqrt
import json
from flame import evaluate, POLICIES, REGIMES, N_STEPS

TEST = range(70000, 70240)
FIELDS = ('brier', 'log_loss', 'coverage', 'overconfident_errors',
          'early_post_shift_brier', 'late_post_shift_brier')
COMPARATORS = ('hedge', 'hmm_fast', 'fire003', 'hmm_slow')


def paired(a, b):
    values = [x - y for x, y in zip(a, b)]
    n = len(values)
    mean = sum(values) / n
    sd = sqrt(sum((v - mean) ** 2 for v in values) / (n - 1))
    margin = 1.96 * sd / sqrt(n)
    return {'delta': round(mean, 7), 'approx_95pct_interval':
            [round(mean - margin, 7), round(mean + margin, 7)]}


def summarize(rows):
    return {
        field: round(sum(row[field] for row in rows) / len(rows), 7)
        for field in FIELDS
    } | {'selective_accuracy': round(
        sum(row['selective_accuracy'] for row in rows
            if row['selective_accuracy'] is not None) /
        max(1, sum(row['selective_accuracy'] is not None for row in rows)), 7)}


def experiment():
    result = {'experiment': 'FIRE-004', 'scope': 'synthetic prequential study',
              'steps_per_world': N_STEPS, 'seeds': [TEST.start, TEST.stop - 1],
              'worlds_per_regime': len(TEST), 'regimes': {}}
    for regime in REGIMES:
        observations = [evaluate(seed, regime) for seed in TEST]
        data = {policy: [world[policy] for world in observations]
                for policy in (*POLICIES, 'oracle')}
        alarm_count = sum(len(w['fire004']['alerts']) for w in observations)
        post_detections = [min((s - 48 for s in w['fire004']['alerts']
                                if 48 <= s <= 64), default=None)
                           for w in observations]
        actual = [d for d in post_detections if d is not None]
        result['regimes'][regime] = {
            'policies': {p: summarize(rows) for p, rows in data.items()},
            'paired_fire004_minus': {
                p: paired([r['brier'] for r in data['fire004']],
                          [r['brier'] for r in data[p]])
                for p in COMPARATORS},
            'paired_early_post_fire004_minus_hedge': paired(
                [r['early_post_shift_brier'] for r in data['fire004']],
                [r['early_post_shift_brier'] for r in data['hedge']]),
            'paired_late_post_fire004_minus_hedge': paired(
                [r['late_post_shift_brier'] for r in data['fire004']],
                [r['late_post_shift_brier'] for r in data['hedge']]),
            'alarm_monitor': {
                'alarms_per_world': round(alarm_count / len(TEST), 7),
                'fraction_with_alarm_between_48_and_64':
                    round(len(actual) / len(TEST), 7),
                'mean_detection_delay_given_detection':
                    round(sum(actual) / len(actual), 7) if actual else None,
            },
        }
    result['macro_mean_brier'] = {
        p: round(sum(result['regimes'][r]['policies'][p]['brier']
                     for r in REGIMES) / len(REGIMES), 7)
        for p in (*POLICIES, 'oracle')}
    return result


if __name__ == '__main__':
    print(json.dumps(experiment(), indent=2, sort_keys=True))
