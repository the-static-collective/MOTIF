"""FIRE-001 predeclared training/test seeds; audit results are not blind."""
import json
from math import sqrt
from combustion import run

TRAIN = tuple(range(4100, 4140))
TEST = tuple(range(32000, 32200))
WEIGHTS = (0., .25, .5, 1., 2.)
POLICIES = ('value', 'information', 'ratio', 'fire')


def summarize(rows):
    n = len(rows)
    return {key: round(sum(row[key] for row in rows) / n, 4)
            for key in ('verified_value', 'correct_tasks',
                        'false_attempts', 'steps', 'unlocked')}


def paired_delta(first, second):
    differences = [a['verified_value'] - b['verified_value']
                   for a, b in zip(first, second)]
    n = len(differences)
    mean = sum(differences) / n
    variance = sum((d - mean) ** 2 for d in differences) / (n - 1)
    margin = 1.96 * sqrt(variance / n)  # Descriptive normal-approx CI, not proof.
    return {'mean': round(mean, 4), 'approx_95pct_interval':
            [round(mean - margin, 4), round(mean + margin, 4)]}


def main():
    # Deterministic, bounded, engineer-specified method tuning only.
    training = {weight: summarize([run(seed, 'fire', weight)
                                   for seed in TRAIN]) for weight in WEIGHTS}
    selected = max(WEIGHTS, key=lambda w: (training[w]['verified_value'], -w))
    raw = {name: [run(seed, name, selected) for seed in TEST]
           for name in POLICIES}
    raw['fire_no_spark'] = [run(seed, 'fire', 0.) for seed in TEST]
    outputs = {name: summarize(rows) for name, rows in raw.items()}
    print(json.dumps({'experiment': 'FIRE-001', 'scope': 'synthetic-only',
                      'training_seeds': [TRAIN[0], TRAIN[-1]],
                      'test_seeds': [TEST[0], TEST[-1]],
                      'selected_weight': selected, 'training': training,
                      'test': outputs,
                      'paired_fire_minus_ratio': paired_delta(raw['fire'], raw['ratio']),
                      'paired_fire_minus_no_spark': paired_delta(raw['fire'], raw['fire_no_spark']),
                      'limits': 'Fixed task grammar, known source counts, no real-world learning'},
                     indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
