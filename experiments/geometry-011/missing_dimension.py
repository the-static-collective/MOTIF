"""MOTIF GEOM-011: The Missing Dimension.

A synthetic, local-only extension to GEOM-010's indistinguishability diagnostic.
The engine NEVER invents a sensor reading or authorizes a measurement. It can
recommend *declared, permitted* sensors, learn a small derived Boolean feature
from pilot observations, and demonstrate that a previously indistinguishable
label pair separates under that expanded vocabulary.

Classical baselines: conditional entropy, finite Boolean function enumeration.
No unrestricted ontology invention, evidence authentication, or outside acts.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from math import isfinite, log2
from typing import Mapping, Sequence
import hashlib
import json


def canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False)


def digest(prefix: str, value: object) -> str:
    return prefix + hashlib.sha256(canonical(value).encode('utf-8')).hexdigest()


def token(value: str, label: str) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > 256:
        raise ValueError(f'bad {label}')
    return value


def pairs(value: Mapping[str, str], label: str) -> tuple[tuple[str, str], ...]:
    if not isinstance(value, Mapping):
        raise ValueError(f'{label} must be a mapping')
    for k, v in value.items():
        token(k, 'feature key'); token(v, 'feature value')
    return tuple(sorted(value.items()))


@dataclass(frozen=True)
class Case:
    identity: str
    before: tuple[str, ...]
    after: tuple[str, ...]
    visible: tuple[tuple[str, str], ...]
    expected: bool
    source_root: str
    scope: str

    def __post_init__(self):
        for name, value in [('case id', self.identity), ('source root', self.source_root),
                            ('scope', self.scope)]:
            token(value, name)
        if type(self.expected) is not bool:
            raise ValueError('case label must be boolean')
        if not isinstance(self.before, tuple) or not isinstance(self.after, tuple) or self.before == self.after:
            raise ValueError('case must contain distinct tuple before/after expressions')
        for value in self.before + self.after:
            token(value, 'expression token')
        if not isinstance(self.visible, tuple) or self.visible != tuple(sorted(self.visible)) or len({k for k, _ in self.visible}) != len(self.visible):
            raise ValueError('visible features must be sorted, unique pairs')
        for k, v in self.visible:
            token(k, 'visible key'); token(v, 'visible value')

    @classmethod
    def make(cls, identity: str, before: Sequence[str], after: Sequence[str],
             visible: Mapping[str, str], expected: bool, source_root: str, scope: str):
        return cls(identity, tuple(before), tuple(after), pairs(visible, 'visible'),
                   expected, source_root, scope)

    def data(self) -> dict:
        return {'id': self.identity, 'before': list(self.before), 'after': list(self.after),
                'visible': dict(self.visible), 'expected': self.expected,
                'source_root': self.source_root, 'scope': self.scope}


@dataclass(frozen=True)
class Sensor:
    identity: str
    cost: float
    permitted: bool
    available: bool
    scope: str

    def __post_init__(self):
        token(self.identity, 'sensor id'); token(self.scope, 'sensor scope')
        if type(self.cost) not in (int, float) or not isfinite(self.cost) or self.cost <= 0:
            raise ValueError('sensor cost must be finite positive')
        if type(self.permitted) is not bool or type(self.available) is not bool:
            raise ValueError('sensor permission and availability must be declared booleans')

    def data(self):
        return {'id': self.identity, 'cost': self.cost, 'permitted': self.permitted,
                'available': self.available, 'scope': self.scope}


@dataclass(frozen=True)
class PilotReading:
    case_id: str
    sensor_id: str
    value: str
    source_root: str
    scope: str

    def __post_init__(self):
        for k, v in [('case id', self.case_id), ('sensor id', self.sensor_id),
                     ('reading source', self.source_root), ('scope', self.scope)]:
            token(v, k)
        if self.value not in ('0', '1'):
            raise ValueError('synthetic pilot sensor values must be 0 or 1')

    def data(self):
        return {'case_id': self.case_id, 'sensor_id': self.sensor_id,
                'value': self.value, 'source_root': self.source_root, 'scope': self.scope}


def _entropy_counts(values: Sequence[bool]) -> float:
    if not values:
        return 0.0
    p = sum(values) / len(values)
    return 0.0 if p in (0., 1.) else -(p * log2(p) + (1 - p) * log2(1 - p))


def _conditional_entropy(groups: Mapping[tuple, list[bool]]) -> float:
    total = sum(len(g) for g in groups.values())
    return sum(len(g) * _entropy_counts(g) / total for g in groups.values()) if total else 0.


def _matches_rewrite(find: tuple[str, ...], replace: tuple[str, ...], before, after) -> bool:
    length = len(find)
    for pos in range(len(before) - length + 1):
        if before[pos:pos + length] == find and before[:pos] + replace + before[pos + length:] == after:
            return True
    return False


@dataclass(frozen=True)
class SynthesizedDimension:
    signals: tuple[str, ...]
    gate: str
    find: tuple[str, ...]
    replace: tuple[str, ...]
    scope: str

    def __post_init__(self):
        token(self.scope, 'dimension scope')
        if len(self.signals) not in (1, 2) or len(set(self.signals)) != len(self.signals):
            raise ValueError('a dimension consumes one or two distinct sensors')
        if self.gate not in ('IDENTITY', 'NOT', 'AND', 'OR', 'XOR', 'XNOR', 'NAND', 'NOR'):
            raise ValueError('unknown derived operator')
        if len(self.signals) == 1 and self.gate not in ('IDENTITY', 'NOT'):
            raise ValueError('binary gate needs two sensors')
        if len(self.signals) == 2 and self.gate in ('IDENTITY', 'NOT'):
            raise ValueError('unary gate needs one sensor')
        if self.find == self.replace:
            raise ValueError('rewrite must have a nonidentity effect')
        for t in self.find + self.replace:
            token(t, 'rewrite token')

    def value(self, readings: Mapping[str, str]) -> bool | None:
        vals = [readings.get(s) for s in self.signals]
        if any(x is None for x in vals):
            return None
        if any(x not in ('0', '1') for x in vals):
            raise ValueError('sensor value must be bit')
        a = vals[0] == '1'
        b = vals[1] == '1' if len(vals) == 2 else False
        return {'IDENTITY': lambda: a, 'NOT': lambda: not a,
                'AND': lambda: a and b, 'OR': lambda: a or b,
                'XOR': lambda: a != b, 'XNOR': lambda: a == b,
                'NAND': lambda: not (a and b), 'NOR': lambda: not (a or b)}[self.gate]()

    def decide(self, case: Case, measurements: Mapping[str, str]):
        if case.scope != self.scope:
            raise ValueError('cross-scope evaluation refused')
        if not _matches_rewrite(self.find, self.replace, case.before, case.after):
            return False
        return self.value(measurements)

    def data(self):
        return {'signals': list(self.signals), 'operator': self.gate,
                'base_rewrite': {'find': list(self.find), 'replace': list(self.replace)},
                'scope': self.scope, 'instrument': 'PENCIL', 'authority': 'NONE'}


class MissingDimensionLab:
    def __init__(self, cases: Sequence[Case], sensors: Sequence[Sensor],
                 pilot: Sequence[PilotReading], *, scope: str):
        self.scope = token(scope, 'scope')
        self.cases = tuple(cases)
        self.sensors = tuple(sensors)
        self.pilot = tuple(pilot)
        if not self.cases or len({x.identity for x in self.cases}) != len(self.cases):
            raise ValueError('nonempty unique development cases required')
        if len({x.identity for x in self.sensors}) != len(self.sensors):
            raise ValueError('duplicate sensor')
        if any(x.scope != scope for x in self.cases + self.sensors + self.pilot):
            raise ValueError('different observer/time/decoder scope refused')
        self.case_index = {x.identity: x for x in self.cases}
        self.sensor_index = {x.identity: x for x in self.sensors}
        self.readings: dict[str, dict[str, str]] = {x.identity: {} for x in self.cases}
        for reading in self.pilot:
            if reading.case_id not in self.case_index or reading.sensor_id not in self.sensor_index:
                raise ValueError('pilot references unknown case or sensor')
            observed = self.readings[reading.case_id]
            if reading.sensor_id in observed:
                raise ValueError('duplicate pilot reading, even when identical')
            observed[reading.sensor_id] = reading.value
        self.domain = digest('geom011-domain:', {'scope': self.scope,
            'cases': [x.data() for x in self.cases],
            'sensors': [x.data() for x in self.sensors],
            'pilot': [x.data() for x in sorted(self.pilot, key=lambda x: (x.case_id, x.sensor_id))]})

    @classmethod
    def from_geom010_cases(cls, cases, sensors, pilot, *, scope: str):
        """Read-only adapter of GEOM-010 SituatedCase fields: PENCIL, not PEN.

        Does not import hidden data or grant permission. Caller supplies additional
        candidate sensors and already recorded pilot measurements explicitly.
        """
        adapted = [Case.make(c.identity, c.before, c.after, dict(c.facts),
                             c.expected, c.source_root, c.scope) for c in cases]
        return cls(adapted, sensors, pilot, scope=scope)

    def collisions(self):
        buckets: dict[tuple, list[Case]] = {}
        for c in self.cases:
            buckets.setdefault((c.before, c.after, c.visible), []).append(c)
        witness = []
        for _, bucket in sorted(buckets.items(), key=lambda x: str(x[0])):
            yes = sorted((c for c in bucket if c.expected), key=lambda c: c.identity)
            no = sorted((c for c in bucket if not c.expected), key=lambda c: c.identity)
            if yes and no:
                witness.append({'positive_case': yes[0].identity, 'negative_case': no[0].identity,
                                'positive_claimed_root': yes[0].source_root,
                                'negative_claimed_root': no[0].source_root,
                                'visible_signature': dict(yes[0].visible),
                                'reason': 'same supplied before/after and visible features; opposing declared labels'})
        return witness

    def diagnose(self):
        witnesses = self.collisions()
        return {'status': 'MISSING_DISTINCTION_CERTIFICATE' if witnesses else 'NO_VISIBLE_COLLISION',
                'conflict_witnesses': witnesses, 'development_cases': len(self.cases),
                'interpretation': 'No deterministic classifier restricted to supplied visible inputs fits contradictory labels. Labels and roots are declarations.',
                'instrument': 'PENCIL', 'authority': 'NONE'}

    def _complete_permitted(self, budget: float):
        if type(budget) not in (int, float) or not isfinite(budget) or budget <= 0:
            raise ValueError('finite positive proposed measurement budget required')
        permitted = [s for s in self.sensors if s.permitted and s.available and s.cost <= budget]
        complete = [s for s in permitted if all(s.identity in self.readings[c.identity] for c in self.cases)]
        missing = {s.identity: sum(s.identity not in self.readings[c.identity] for c in self.cases)
                   for s in permitted if s not in complete}
        return sorted(complete, key=lambda s: s.identity), missing

    def probe_options(self, *, budget: float, max_sensors: int = 2):
        """Classical supervised conditional information gain, from recorded PILOT ONLY.

        Explicit sensor costs and scope; a proposed probe is NEVER executed.
        MAX_SENSORS=2 is the currently searched operator grammar, not graph size.
        """
        if type(max_sensors) is not int or max_sensors not in (1, 2):
            raise ValueError('supported sensor combinations have arity 1 or 2')
        complete, missing = self._complete_permitted(budget)
        groups: dict[tuple, list[bool]] = {}
        for c in self.cases:
            groups.setdefault((c.before, c.after, c.visible), []).append(c.expected)
        before = _conditional_entropy(groups)
        results = []
        for arity in range(1, min(max_sensors, len(complete)) + 1):
            for bundle in combinations(complete, arity):
                cost = sum(x.cost for x in bundle)
                if cost > budget:
                    continue
                after_groups: dict[tuple, list[bool]] = {}
                for c in self.cases:
                    signature = (c.before, c.after, c.visible, tuple(
                        self.readings[c.identity][s.identity] for s in bundle))
                    after_groups.setdefault(signature, []).append(c.expected)
                gain = max(0., before - _conditional_entropy(after_groups))
                ids = tuple(s.identity for s in bundle)
                results.append({'sensors': list(ids), 'pilot_information_gain_bits': round(gain, 9),
                                'gain_per_cost': round(gain / cost, 9), 'declared_cost': cost,
                                'status': 'PROPOSED_ONLY', 'actual_measurement_executed': False})
        results.sort(key=lambda x: (-x['gain_per_cost'], x['declared_cost'], x['sensors']))
        if not results:
            status = 'HOLD_NEEDS_PILOT' if missing else 'HOLD_NO_PERMITTED_SENSOR'
            return {'status': status, 'unmeasured_development_cases_by_sensor': missing,
                    'inference': 'No sensor outcome was invented', 'authority': 'NONE'}
        # Sensor synergy is useful only if a pair improves over the best single.
        singles = {x['sensors'][0]: x['pilot_information_gain_bits'] for x in results
                   if len(x['sensors']) == 1}
        for x in results:
            x['synergy_bits_above_best_single'] = (round(x['pilot_information_gain_bits'] -
                max(singles.get(s, 0.) for s in x['sensors']), 9) if len(x['sensors']) == 2 else 0.)
        return {'status': 'PILOT_BASED_PROBE_RANKING', 'best': results[0],
                'options': results, 'unmeasured_development_cases_by_sensor': missing,
                'visible_conditional_entropy_bits': round(before, 9),
                'interpretation': 'Data-dependent synthetic pilot scores; selection is not a physical measurement.',
                'authority': 'NONE', 'instrument': 'PENCIL'}

    def _candidates(self, *, find: tuple[str, ...], replace: tuple[str, ...], budget: float):
        eligible, missing = self._complete_permitted(budget)
        candidates = []
        for s in eligible:
            for gate in ('IDENTITY', 'NOT'):
                candidates.append(SynthesizedDimension((s.identity,), gate, find, replace, self.scope))
        for a, b in combinations(eligible, 2):
            if a.cost + b.cost > budget:
                continue
            for gate in ('AND', 'OR', 'XOR', 'XNOR', 'NAND', 'NOR'):
                candidates.append(SynthesizedDimension((a.identity, b.identity), gate, find, replace, self.scope))
        return candidates, missing

    def _score(self, op: SynthesizedDimension, cases: Sequence[Case] | None = None,
               readings: Mapping[str, Mapping[str, str]] | None = None):
        cases = self.cases if cases is None else cases
        readings = self.readings if readings is None else readings
        correct = wrong = abstentions = 0
        for c in cases:
            p = op.decide(c, readings.get(c.identity, {}))
            if p is None: abstentions += 1
            elif p == c.expected: correct += 1
            else: wrong += 1
        return {'total': len(cases), 'correct': correct, 'wrong': wrong, 'abstentions': abstentions}

    def invent(self, *, find: Sequence[str], replace: Sequence[str], budget: float,
               work_budget: int, cursor: dict | None = None):
        """Finite operator composition from declared pilot sensors, not new facts.

        Return a revisable PENCIL cartridge only after complete candidate scan.
        It cannot read heldout cases and never returns executable permissions.
        """
        if type(work_budget) is not int or work_budget <= 0:
            raise ValueError('work budget must be a positive integer')
        a, b = tuple(find), tuple(replace)
        if a == b or any(not isinstance(t, str) or not t.strip() for t in a + b):
            raise ValueError('invalid rewrite')
        collision = self.collisions()
        if not collision:
            return {'status': 'HOLD', 'reason': 'no indistinguishable opposing label examples supplied', 'authority': 'NONE'}
        if len({c.source_root for c in self.cases}) < 2:
            return {'status': 'HOLD', 'reason': 'fewer than two separately declared case source roots',
                    'authority': 'NONE'}
        candidates, missing = self._candidates(find=a, replace=b, budget=budget)
        if not candidates:
            return {'status': 'HOLD_NEEDS_PILOT' if missing else 'HOLD_NO_PERMITTED_SENSOR',
                    'missing_pilot': missing, 'authority': 'NONE'}
        domain = digest('geom011-search:', {'lab': self.domain, 'find': list(a),
            'replace': list(b), 'measurement_budget': budget,
            'catalog': [x.data() for x in candidates]})
        offset = 0
        if cursor is not None:
            if not isinstance(cursor, dict) or set(cursor) != {'domain', 'offset'} or cursor['domain'] != domain \
                    or type(cursor['offset']) is not int or cursor['offset'] < 0 or cursor['offset'] > len(candidates):
                raise ValueError('invalid or mismatched search cursor')
            offset = cursor['offset']
        # A cursor cannot skip an earlier exact fit and falsely claim optimality.
        for past in candidates[:offset]:
            s = self._score(past)
            if s['correct'] == len(self.cases) and s['abstentions'] == 0:
                raise ValueError('continuation cursor skips an already sufficient candidate')
        for i in range(offset, min(len(candidates), offset + work_budget)):
            x = candidates[i]
            score = self._score(x)
            if score['correct'] == len(self.cases) and score['abstentions'] == 0:
                return {'status': 'PENCIL_DIMENSION_PROPOSED', 'cartridge': x.data(),
                        'development': score, 'evaluated_candidate_prefix': i + 1,
                        'search_space': len(candidates), 'search_domain': domain,
                        'measurement_budget': budget, 'completeness': 'MINIMAL_ARITY_FIRST_EXACT_FIT_IN_ORDER',
                        'source_roots_are_authenticated': False,
                        'instrument': 'PENCIL', 'authority': 'NONE'}
        stop = min(len(candidates), offset + work_budget)
        if stop < len(candidates):
            return {'status': 'CONTINUE_SEARCH', 'cursor': {'domain': domain, 'offset': stop},
                    'considered_this_slice': stop - offset, 'completeness': 'INCOMPLETE',
                    'authority': 'NONE'}
        return {'status': 'HOLD', 'reason': 'none of the admitted small Boolean functions separates all supplied pilot labels',
                'search_space': len(candidates), 'completeness': 'COMPLETE_FOR_DECLARED_GRAMMAR',
                'authority': 'NONE'}

    def evaluate_new_cases(self, proposal: Mapping, cases: Sequence[Case],
                           readings: Sequence[PilotReading]):
        """Read-only heldout evaluation; training selection is already frozen."""
        candidate = self._from_proposal(proposal)
        if any(c.scope != self.scope for c in cases):
            raise ValueError('cross-scope heldout case')
        if len({c.identity for c in cases}) != len(cases) or {c.identity for c in cases} & set(self.case_index):
            raise ValueError('heldout identity overlap or duplication')
        seen: dict[str, dict[str, str]] = {c.identity: {} for c in cases}
        for reading in readings:
            if reading.scope != self.scope or reading.case_id not in seen or reading.sensor_id not in self.sensor_index:
                raise ValueError('bad heldout measurement')
            if reading.sensor_id in seen[reading.case_id]:
                raise ValueError('duplicate heldout measurement')
            # Permission is checked again at consumption, not inferred from a proposal.
            sensor = self.sensor_index[reading.sensor_id]
            if not sensor.permitted or not sensor.available:
                raise ValueError('heldout reading is from unpermitted or unavailable sensor')
            seen[reading.case_id][reading.sensor_id] = reading.value
        return {'status': 'HELDOUT_SYNTHETIC_EVALUATION', 'scores': self._score(candidate, cases, seen),
                'cartridge': candidate.data(), 'instrument': 'PENCIL', 'authority': 'NONE',
                'note': 'Supplied readings are fixture records, not physical sensors automatically invoked.'}

    def _from_proposal(self, proposal: Mapping):
        if not isinstance(proposal, Mapping) or proposal.get('status') != 'PENCIL_DIMENSION_PROPOSED' or proposal.get('authority') != 'NONE':
            raise ValueError('proposal must be a PENCIL derived dimension')
        data = proposal.get('cartridge')
        if not isinstance(data, Mapping) or set(data) != {'signals', 'operator', 'base_rewrite', 'scope', 'instrument', 'authority'} or \
                data['instrument'] != 'PENCIL' or data['authority'] != 'NONE' or data['scope'] != self.scope:
            raise ValueError('invalid PENCIL candidate shape or scope')
        if not isinstance(data['signals'], list) or not isinstance(data['base_rewrite'], Mapping):
            raise ValueError('invalid cartridge signals/rewrite')
        br = data['base_rewrite']
        if set(br) != {'find', 'replace'} or not isinstance(br['find'], list) or not isinstance(br['replace'], list):
            raise ValueError('invalid cartridge rewrite')
        op = SynthesizedDimension(tuple(data['signals']), data['operator'], tuple(br['find']), tuple(br['replace']), self.scope)
        declared_budget = proposal.get('measurement_budget')
        if type(declared_budget) not in (int, float) or not isfinite(declared_budget) or declared_budget <= 0:
            raise ValueError('missing finite measurement budget in proposal receipt')
        # Re-run selection on original development cases; accepting a matching
        # display shape alone could let a caller forge a new rule at evaluation.
        checked = self.invent(find=op.find, replace=op.replace,
                              budget=declared_budget, work_budget=10**9)
        if checked.get('status') != 'PENCIL_DIMENSION_PROPOSED' or \
                any(proposal.get(k) != checked.get(k) for k in
                    ('cartridge','development','search_domain','evaluated_candidate_prefix','measurement_budget')):
            raise ValueError('candidate is not the selected tested development proposal')
        if any(s not in self.sensor_index or not self.sensor_index[s].permitted or
               not self.sensor_index[s].available for s in op.signals):
            raise ValueError('unpermitted or unknown sensor in proposed cartridge')
        return op

    def archive_pencil(self, graph, proposal: Mapping, *, measurement_budget: float,
                       work_budget: int = 100000):
        """Append an attributed proposal to GEOM-008/009 LivingGraph; never PEN.

        Recompute with the supplied pilot before accepting an alleged proposal.
        Lives in existing provenance-labeled graph; no grammar rebinding.
        """
        op = self._from_proposal(proposal)
        if graph.scope != self.scope:
            raise ValueError('graph scope mismatch')
        recalculated = self.invent(find=op.find, replace=op.replace,
                                   budget=measurement_budget, work_budget=work_budget)
        protected = ('status', 'cartridge', 'development', 'evaluated_candidate_prefix',
                     'search_domain')
        if any(proposal.get(k) != recalculated.get(k) for k in protected):
            raise ValueError('forged or incomplete dimension proposal')
        root = digest('dimension-cartridge:', {'domain': self.domain, 'cartridge': op.data()})
        graph.add_node(root, kind='derived_dimension_cartridge', label=op.gate,
                       payload={'proposal': recalculated, 'source_digest': self.domain,
                                'admission': 'PENCIL_ONLY'}, source_root='geom011:synthetic-local')
        participants = [('proposal', root)]
        for c in self.cases:
            identity = digest('dimension-case:', c.data())
            graph.add_node(identity, kind='dimension_development_case', label=c.identity,
                           payload=c.data(), source_root=c.source_root)
            participants.append(('development_case', identity))
        for reading in self.pilot:
            identity = digest('dimension-pilot:', reading.data())
            graph.add_node(identity, kind='dimension_pilot_record',
                           label=reading.case_id + ':' + reading.sensor_id,
                           payload=reading.data(), source_root=reading.source_root)
            participants.append(('pilot_reading', identity))
        graph.add_relation('derived_dimension_witnesses', participants,
                           source_root='geom011:synthetic-local',
                           note={'admission': 'PENCIL_ONLY', 'scope': self.scope})
        return {'status': 'ARCHIVED_PENCIL_ONLY', 'node_id': root,
                'pilot_readings': len(self.pilot), 'authority': 'NONE'}


def case_from_document(obj: Mapping) -> Case:
    if not isinstance(obj, Mapping) or set(obj) != {'id', 'before', 'after', 'visible', 'expected', 'source_root', 'scope'} \
            or not isinstance(obj['before'], list) or not isinstance(obj['after'], list):
        raise ValueError('invalid development case document')
    return Case.make(obj['id'], obj['before'], obj['after'], obj['visible'], obj['expected'],
                     obj['source_root'], obj['scope'])


def sensor_from_document(obj: Mapping) -> Sensor:
    if not isinstance(obj, Mapping) or set(obj) != {'id', 'cost', 'permitted', 'available', 'scope'}:
        raise ValueError('invalid sensor declaration')
    return Sensor(obj['id'], obj['cost'], obj['permitted'], obj['available'], obj['scope'])


def reading_from_document(obj: Mapping) -> PilotReading:
    if not isinstance(obj, Mapping) or set(obj) != {'case_id', 'sensor_id', 'value', 'source_root', 'scope'}:
        raise ValueError('invalid pilot declaration')
    return PilotReading(obj['case_id'], obj['sensor_id'], obj['value'], obj['source_root'], obj['scope'])


def run_document(doc: Mapping) -> dict:
    """Strict local JSON interface; no network, sensor calls, or action execution."""
    required = {'scope', 'development', 'candidate_sensors', 'pilot_readings',
                'base_rewrite', 'measurement_budget', 'work_budget'}
    if not isinstance(doc, Mapping) or set(doc) != required:
        raise ValueError('unknown or missing document keys')
    base = doc['base_rewrite']
    if not isinstance(base, Mapping) or set(base) != {'find', 'replace'} or not isinstance(base['find'], list) or not isinstance(base['replace'], list):
        raise ValueError('invalid base rewrite document')
    lab = MissingDimensionLab([case_from_document(x) for x in doc['development']],
                              [sensor_from_document(x) for x in doc['candidate_sensors']],
                              [reading_from_document(x) for x in doc['pilot_readings']],
                              scope=doc['scope'])
    return {'diagnosis': lab.diagnose(),
            'probe_ranking': lab.probe_options(budget=doc['measurement_budget']),
            'invention': lab.invent(find=base['find'], replace=base['replace'],
                                    budget=doc['measurement_budget'],
                                    work_budget=doc['work_budget'])}
