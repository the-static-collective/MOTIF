"""Deterministic synthetic demonstration of a missing relational dimension."""
import json
from missing_dimension import Case, Sensor, PilotReading, MissingDimensionLab

SCOPE = 'synthetic:observer-a@tick-11:decoder-A'
BASE = {'find': ['bud'], 'replace': ['branch']}


def scenario():
    cases, readings = [], []
    # A/B each contains exactly zero information about XOR labels alone.
    # Both sensor recordings are supplied as synthetic *pilot* data; the system
    # does not know the rule in advance or obtain any new measurement itself.
    for plant in ('oak', 'pine', 'cedar', 'birch', 'willow', 'maple'):
        for a, b in ((0, 0), (0, 1), (1, 0), (1, 1)):
            identity = f'{plant}:{a}{b}'
            cases.append(Case.make(identity, (plant, 'bud'), (plant, 'branch'),
                {'growth': 'bud', 'period': 'spring'}, bool(a ^ b),
                'claimed:' + plant, SCOPE))
            for sensor, value in [('signal-a', a), ('signal-b', b), ('unrelated', 0), ('forbidden-leak', a ^ b)]:
                readings.append(PilotReading(identity, sensor, str(value),
                    f'pilot:{plant}:{sensor}', SCOPE))
    sensors = [Sensor('signal-a', 1., True, True, SCOPE),
               Sensor('signal-b', 1., True, True, SCOPE),
               Sensor('unrelated', 0.5, True, True, SCOPE),
               Sensor('forbidden-leak', 0.01, False, True, SCOPE),
               Sensor('missing-sensor', 0.1, True, True, SCOPE),
               Sensor('unavailable', 0.01, True, False, SCOPE)]
    return MissingDimensionLab(cases, sensors, readings, scope=SCOPE)


def run():
    lab = scenario()
    diagnosis = lab.diagnose()
    probes = lab.probe_options(budget=3.)
    # One deliberately incomplete compute slice; resume from returned cursor.
    incomplete = lab.invent(find=BASE['find'], replace=BASE['replace'],
                            budget=3., work_budget=2)
    assert incomplete['status'] == 'CONTINUE_SEARCH', incomplete
    result = lab.invent(find=BASE['find'], replace=BASE['replace'],
                        budget=3., work_budget=100, cursor=incomplete['cursor'])
    assert result['status'] == 'PENCIL_DIMENSION_PROPOSED', result
    assert result['cartridge']['operator'] == 'XOR', result
    assert result['cartridge']['signals'] == ['signal-a', 'signal-b'], result
    return {'experiment': 'GEOM-011 Missing Dimension (synthetic pilot, local-only)',
            'diagnosis': diagnosis, 'possible_probes': probes,
            'partial_search': incomplete, 'synthesized_cartridge': result,
            'interpretation': 'Individual recorded synthetic signals are uninformative; their XOR composition discriminates conflicting labels. No sensor reading is invented or performed.',
            'scope': SCOPE, 'instrument': 'PENCIL', 'authority': 'NONE'}


if __name__ == '__main__':
    print(json.dumps(run(), sort_keys=True, indent=2))
