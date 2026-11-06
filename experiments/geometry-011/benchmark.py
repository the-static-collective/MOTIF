"""Heldout frozen synthetic evaluation and independent classical lookup control."""
import json
import random
from missing_dimension import Case, PilotReading
from demo import scenario, SCOPE, BASE


def heldout(seed=20261106):
    rng = random.Random(seed)
    cases, pilot = [], []
    for i in range(260):
        # Separate names, never reuse one of the six training plants.
        name = 'unseen_' + str(i) + '_' + str(rng.randrange(10**9))
        a, b = (i % 4) // 2, (i % 4) % 2
        # Missing final 20 readings intentionally force correct abstention.
        case_id = f'test-{i}'
        cases.append(Case.make(case_id, (name, 'bud'), (name, 'branch'),
             {'growth': 'bud', 'period': 'spring'}, bool(a ^ b),
             'heldout:synthetic:' + str(i // 4), SCOPE))
        pilot.append(PilotReading(case_id, 'signal-a', str(a), 'heldout:pilot-a', SCOPE))
        if i < 240:
            pilot.append(PilotReading(case_id, 'signal-b', str(b), 'heldout:pilot-b', SCOPE))
    return cases, pilot


def independent_truth_table(training_lab, test_cases, test_pilot):
    """Direct full truth-table baseline, independent of GEOM-011 operator scoring."""
    lookup = {}
    for case in training_lab.cases:
        a = training_lab.readings[case.identity]['signal-a']
        b = training_lab.readings[case.identity]['signal-b']
        key = (a, b)
        if key in lookup and lookup[key] != case.expected:
            raise AssertionError('inconsistent training truth table')
        lookup[key] = case.expected
    groups = {}
    for reading in test_pilot:
        groups.setdefault(reading.case_id, {})[reading.sensor_id] = reading.value
    correct = wrong = hold = 0
    for case in test_cases:
        signal = groups.get(case.identity, {})
        if 'signal-a' not in signal or 'signal-b' not in signal:
            hold += 1
            continue
        pred = lookup.get((signal['signal-a'], signal['signal-b']))
        if pred is None: hold += 1
        elif pred == case.expected:correct += 1
        else:wrong += 1
    return {'total': len(test_cases), 'correct': correct, 'wrong': wrong, 'abstentions': hold}


def run():
    train = scenario()
    proposal = train.invent(find=BASE['find'], replace=BASE['replace'],
                            budget=3., work_budget=1000)
    assert proposal['status'] == 'PENCIL_DIMENSION_PROPOSED'
    fresh, pilot = heldout()
    scores = train.evaluate_new_cases(proposal, fresh, pilot)['scores']
    classical = independent_truth_table(train, fresh, pilot)
    # Visible-only deterministic classifier cannot disambiguate opposing labels.
    # Predict false for everyone: 130/260 on balanced XOR combinations.
    visible_only = sum(not c.expected for c in fresh)
    return {'experiment': 'GEOM-011 frozen synthetic paired-sensor benchmark',
            'seed': 20261106, 'training_cases': len(train.cases),
            'heldout_cases': len(fresh), 'heldout_missing_probe_cases': 20,
            'synthesized_dimension': proposal['cartridge'],
            'geom011_scores': scores,
            'independent_classical_truth_table': classical,
            'visible_only_always_false_correct': visible_only,
            'matched_classical_baseline': scores == classical,
            'limits': 'Developer-authored XOR world, not externally frozen independent science. A classical depth-two decision tree can match this result.',
            'authority': 'NONE', 'instrument': 'PENCIL'}


if __name__ == '__main__':
    print(json.dumps(run(), indent=2, sort_keys=True))
