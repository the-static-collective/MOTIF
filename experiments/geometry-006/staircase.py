"""MOTIF GEOM-006: source-attributed temporal relational atlas (synthetic only).

This module neither imports nor promotes GEOM-005 claims.  Optional positions
are display projections.  Claim authorship, independent evidence, admission and
external permission are never established by graph structure or coordinates.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from heapq import heappop, heappush
from math import log2, sqrt
from typing import Mapping

RELATIONS = frozenset({'route', 'causes', 'depends', 'resembles'})
HEX_AXIAL = ((1, 0), (0, 1), (-1, 1), (-1, 0), (0, -1), (1, -1))


def _clock(value, name):
    if type(value) is not int or value < 0:
        raise ValueError(f'{name} must be a nonnegative integer synthetic tick')


def _access(access, name):
    if not isinstance(access, dict) or not access:
        raise ValueError(f'{name} needs explicit observer availability')
    for observer, time in access.items():
        if not isinstance(observer, str) or not observer:
            raise ValueError('empty observer ID')
        _clock(time, f'{name} availability')


@dataclass(frozen=True)
class Place:
    id: str
    occurred_at: int
    visible_to: Mapping[str, int] = field(default_factory=dict)

    def __post_init__(self):
        if not self.id:
            raise ValueError('missing node ID')
        _clock(self.occurred_at, 'occurred_at')
        _access(self.visible_to, 'place')


@dataclass(frozen=True)
class Relation:
    id: str
    source: str
    target: str
    kind: str
    # Valid-time history (effective in the synthetic world), not admission time.
    effective_from: int
    effective_until: int | None
    # Knowledge-time history (not necessarily the date the relation began).
    discovered_at: int
    admitted_at: int | None
    withdrawn_at: int | None
    visible_to: Mapping[str, int]
    source_root: str  # attributed label only; NOT independent or authenticated
    duration: int = 1

    def __post_init__(self):
        if not self.id or not self.source or not self.target or not self.source_root:
            raise ValueError('missing relation identity/provenance')
        if self.source == self.target or self.kind not in RELATIONS:
            raise ValueError('invalid endpoints or relation kind')
        for name in ('effective_from', 'discovered_at', 'duration'):
            _clock(getattr(self, name), name)
        if self.duration < 1:
            raise ValueError('duration must be positive')
        for name in ('effective_until', 'admitted_at', 'withdrawn_at'):
            val = getattr(self, name)
            if val is not None:
                _clock(val, name)
        if self.effective_until is not None and self.effective_until <= self.effective_from:
            raise ValueError('empty/negative effective interval')
        if self.admitted_at is not None and self.admitted_at < self.discovered_at:
            raise ValueError('admission cannot predate discovery')
        if self.withdrawn_at is not None and (self.admitted_at is None or self.withdrawn_at <= self.admitted_at):
            raise ValueError('withdrawal requires a prior admission')
        _access(self.visible_to, 'relation')


@dataclass(frozen=True)
class Model:
    id: str
    prior: float
    predictions: Mapping[str, str]


@dataclass(frozen=True)
class Probe:
    id: str
    cost: float
    permitted: bool = False   # fixture-level allow-list; not real authorization


class Atlas:
    def __init__(self, places: list[Place], relations: list[Relation]):
        self.places = {p.id: p for p in places}
        self.relations = {r.id: r for r in relations}
        if len(self.places) != len(places) or len(self.relations) != len(relations):
            raise ValueError('duplicate identity')
        if any(r.source not in self.places or r.target not in self.places for r in relations):
            raise ValueError('missing endpoint')
        # A relationship cannot begin before both of its endpoints occur.
        if any(r.effective_from < max(self.places[r.source].occurred_at,
                                      self.places[r.target].occurred_at) for r in relations):
            raise ValueError('relation predates endpoint')

    @staticmethod
    def _available(access: Mapping[str, int], observer: str, cut: int) -> bool:
        # A missing observer is NOT implicitly authorized to see a witness.
        return observer in access and access[observer] <= cut

    def _known_places(self, world_cut: int, knowledge_cut: int, observer: str):
        return {n for n, p in self.places.items()
                if p.occurred_at <= world_cut and self._available(p.visible_to, observer, knowledge_cut)}

    @staticmethod
    def _state(r: Relation, knowledge_cut: int) -> str:
        if r.withdrawn_at is not None and r.withdrawn_at <= knowledge_cut:
            return 'WITHDRAWN'
        if r.admitted_at is not None and r.admitted_at <= knowledge_cut:
            return 'DECLARED_ADMITTED'
        return 'PENCIL'

    def view(self, world_cut: int, knowledge_cut: int, observer: str, *, geometry: bool = False):
        """Reconstruct an observer's view of world-cut W as known at K."""
        _clock(world_cut, 'world_cut'); _clock(knowledge_cut, 'knowledge_cut')
        if not observer:
            raise ValueError('observer required')
        nodes = self._known_places(world_cut, knowledge_cut, observer)
        edges = []
        for r in sorted(self.relations.values(), key=lambda r: r.id):
            if r.source not in nodes or r.target not in nodes:
                continue
            if not (r.effective_from <= world_cut and
                    (r.effective_until is None or world_cut < r.effective_until)):
                continue
            if r.discovered_at > knowledge_cut or not self._available(r.visible_to, observer, knowledge_cut):
                continue
            edges.append({'id': r.id, 'from': r.source, 'to': r.target,
                          'kind': r.kind, 'state': self._state(r, knowledge_cut),
                          'effective_from': r.effective_from, 'discovered_at': r.discovered_at,
                          'source_root': r.source_root})
        return {'world_cut': world_cut, 'knowledge_cut': knowledge_cut, 'observer': observer,
                'nodes': sorted(nodes), 'relations': edges,
                'coordinates': hex_projection(nodes) if geometry else {},
                'projection': 'HEX_DISPLAY_ONLY' if geometry else 'NONE',
                'authority': 'NONE'}

    def earliest_route(self, source: str, target: str, start_at: int,
                       world_cut: int, knowledge_cut: int, observer: str):
        """Earliest time-respecting directed route among declared-admitted ROUTE edges.

        Waiting is allowed. Travel must complete before closure and by world_cut.
        Geometry, resemblance and merely visible pencil edges are irrelevant.
        This is historical replay on a tiny synthetic time axis, not a forecast.
        """
        for name, value in [('start_at', start_at), ('world_cut', world_cut),
                            ('knowledge_cut', knowledge_cut)]:
            _clock(value, name)
        if not observer or source not in self.places or target not in self.places:
            return {'status': 'HOLD', 'reason': 'unknown or unauthorized anchor', 'authority': 'NONE'}
        allowed = self._known_places(world_cut, knowledge_cut, observer)
        if source not in allowed or target not in allowed or self.places[source].occurred_at > start_at:
            return {'status': 'HOLD', 'reason': 'endpoint unavailable', 'authority': 'NONE'}
        if start_at > world_cut:
            return {'status': 'HOLD', 'reason': 'start after historical cut', 'authority': 'NONE'}
        outgoing = {n: [] for n in allowed}
        for r in self.relations.values():
            if r.kind != 'route' or r.source not in allowed or r.target not in allowed:
                continue
            if r.discovered_at > knowledge_cut or not self._available(r.visible_to, observer, knowledge_cut):
                continue
            if self._state(r, knowledge_cut) != 'DECLARED_ADMITTED':
                continue
            if r.effective_from > world_cut:
                continue
            outgoing[r.source].append(r)
        for edges in outgoing.values():
            edges.sort(key=lambda r: r.id)
        todo = [(start_at, source)]
        best = {source: start_at}
        parent = {}
        while todo:
            time, here = heappop(todo)
            if time != best[here]:
                continue
            if here == target:
                hops = []
                cur = target
                while cur != source:
                    prev, r, depart, arrive = parent[cur]
                    hops.append({'edge': r.id, 'from': prev, 'to': cur,
                                 'depart': depart, 'arrive': arrive})
                    cur = prev
                return {'status': 'PATH', 'arrival': time, 'hops': list(reversed(hops)),
                        'authority': 'NONE', 'basis': 'declared-admitted synthetic route history'}
            for r in outgoing[here]:
                depart = max(time, r.effective_from)
                arrive = depart + r.duration
                if arrive > world_cut or (r.effective_until is not None and arrive >= r.effective_until):
                    continue
                if arrive < self.places[r.target].occurred_at:
                    continue
                if arrive < best.get(r.target, float('inf')):
                    best[r.target] = arrive
                    parent[r.target] = (here, r, depart, arrive)
                    heappush(todo, (arrive, r.target))
        return {'status': 'HOLD', 'reason': 'no time-respecting admitted path', 'authority': 'NONE'}


def hex_projection(node_ids):
    """13-position Metatron-inspired axial display, NOT semantic geometry."""
    ids = sorted(node_ids)
    if len(ids) > 13:
        raise ValueError('13-node hex display is intentionally bounded')
    positions = [(0, 0)] + list(HEX_AXIAL) + [(2*q, 2*r) for q, r in HEX_AXIAL]
    return {node: [round(q + r/2, 6), round(sqrt(3)*r/2, 6)]
            for node, (q, r) in zip(ids, positions)}


def select_question(models: list[Model], probes: list[Probe]):
    """Choose a *permitted synthetic observation proposal* by entropy gain/cost.

    Identical outputs cannot distinguish models. Missing predictions are held,
    not inferred. This is conventional Shannon information gain, not agency.
    """
    if not 2 <= len(models) <= 32 or len({m.id for m in models}) != len(models):
        raise ValueError('needs two to 32 distinct candidate worlds')
    if any(not m.id or not isinstance(m.predictions, Mapping) or
           not isinstance(m.prior, (int, float)) or not 0 < m.prior < float('inf')
           for m in models):
        raise ValueError('invalid prior/model')
    if len({p.id for p in probes}) != len(probes) or any(not p.id or
            not isinstance(p.cost, (int, float)) or not 0 < p.cost < float('inf') for p in probes):
        raise ValueError('invalid probe')
    total = sum(m.prior for m in models)
    priors = {m.id: m.prior / total for m in models}
    entropy = -sum(p * log2(p) for p in priors.values())
    ranked = []
    for probe in probes:
        if not probe.permitted or any(probe.id not in m.predictions for m in models):
            continue
        groups = {}
        for model in models:
            value = model.predictions[probe.id]
            if not isinstance(value, str):
                raise ValueError('prediction must be a categorical string')
            groups.setdefault(value, []).append(model.id)
        if len(groups) < 2:
            continue
        after = 0.0
        for members in groups.values():
            mass = sum(priors[mid] for mid in members)
            after += -sum(priors[mid] * log2(priors[mid] / mass) for mid in members)
        gain = max(0.0, entropy - after)
        ranked.append({'probe': probe.id, 'information_gain_bits': round(gain, 9),
                       'gain_per_cost': round(gain / probe.cost, 9),
                       'outcomes': {key: sorted(members) for key, members in sorted(groups.items())}})
    if not ranked:
        return {'status': 'HOLD', 'reason': 'no permitted fully specified discriminator',
                'authority': 'NONE', 'identified_world': None}
    ranked.sort(key=lambda p: (-p['gain_per_cost'], -p['information_gain_bits'], p['probe']))
    return {'status': 'PROPOSAL_ONLY', 'selected': ranked[0], 'alternatives': ranked[1:],
            'identified_world': None, 'authority': 'NONE',
            'warning': 'fixture permission is not real-world authorization'}
