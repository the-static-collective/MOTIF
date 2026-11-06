"""GEOM-007 Contextual Imagination: finite local-to-global reasoning.

A bounded *synthetic* constraint solver. Sources are labels, not authenticated
witnesses. Different presentations never manufacture information. There is no
network, action authority, PEN promotion, or claim of mathematical novelty.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from math import log2, sqrt
from typing import Mapping

MAX_CONTEXTS = 9
MAX_VARIABLES = 13
MAX_RAW_COMBINATIONS = 4096
MAX_GLOBAL_SECTIONS = 512
HEX_AXIAL = ((1, 0), (0, 1), (-1, 1), (-1, 0), (0, -1), (1, -1))


def _id(value: str, kind: str) -> None:
    if not isinstance(value, str) or not value or len(value) > 128:
        raise ValueError(f'bad {kind} identity')


@dataclass(frozen=True)
class Context:
    """Alternative complete local assignments, not asserted ground truth.

    The *scope* binds temporal cut/observer/decoder. Cross-scope gluing is
    forbidden, because opposing observers or times need not share a valuation.
    """
    id: str
    scope: str
    variables: tuple[str, ...]
    alternatives: tuple[Mapping[str, str], ...]
    source_root: str

    def __post_init__(self):
        _id(self.id, 'context'); _id(self.scope, 'scope'); _id(self.source_root, 'source root')
        if not 1 <= len(self.variables) <= MAX_VARIABLES or len(set(self.variables)) != len(self.variables):
            raise ValueError('invalid variable list')
        for variable in self.variables:
            _id(variable, 'variable')
        if not 1 <= len(self.alternatives) <= 32:
            raise ValueError('invalid alternatives')
        seen = set()
        for alternative in self.alternatives:
            if not isinstance(alternative, Mapping) or set(alternative) != set(self.variables):
                raise ValueError('alternatives must assign each declared variable exactly once')
            for value in alternative.values():
                _id(value, 'categorical value')
            signature = tuple((k, alternative[k]) for k in sorted(self.variables))
            if signature in seen:
                raise ValueError('duplicate local alternative')
            seen.add(signature)


@dataclass(frozen=True)
class Lens:
    id: str
    variables: tuple[str, ...]
    layout: str = 'NONE'

    def __post_init__(self):
        _id(self.id, 'lens')
        if len(set(self.variables)) != len(self.variables) or len(self.variables) > MAX_VARIABLES:
            raise ValueError('invalid lens variables')
        if self.layout not in {'NONE', 'HEX', 'RADIAL'}:
            raise ValueError('unknown display layout')
        for v in self.variables:
            _id(v, 'variable')


@dataclass(frozen=True)
class Question:
    id: str
    variable: str
    cost: float
    permitted: bool = False

    def __post_init__(self):
        _id(self.id, 'question'); _id(self.variable, 'question variable')
        if isinstance(self.cost, bool) or not isinstance(self.cost, (int, float)) or not (0 < self.cost < float('inf')):
            raise ValueError('question cost must be finite and positive')
        if type(self.permitted) is not bool:
            raise ValueError('question permission must be explicit bool')


def _sections(contexts: tuple[Context, ...]):
    """Incremental exact join of finite partial assignments.

    Constraint solve is independent of layouts, representations and questions.
    A global section is compatible with authored possibilities, NOT reality.
    """
    bound = 1
    for c in contexts:
        bound *= len(c.alternatives)
        if bound > MAX_RAW_COMBINATIONS:
            raise ValueError('too many raw combinations; abstain instead of truncating')
    assignments = [{}]
    for c in sorted(contexts, key=lambda c: c.id):
        nxt = []
        for prior in assignments:
            for alternative in c.alternatives:
                if all(k not in prior or prior[k] == v for k, v in alternative.items()):
                    nxt.append({**prior, **alternative})
        # We only collapse identical global assignments, never source families.
        unique = {tuple(sorted(a.items())): a for a in nxt}
        assignments = [unique[k] for k in sorted(unique)]
        if len(assignments) > MAX_GLOBAL_SECTIONS:
            raise ValueError('too many compatible global sections; abstain')
        if not assignments:
            break
    return tuple(assignments)


def _entropy(group_sizes: list[int]) -> float:
    total = sum(group_sizes)
    return -sum((n / total) * log2(n / total) for n in group_sizes if n)


def _projection(section: Mapping[str, str], visible: set[str]):
    return tuple(sorted((k, v) for k, v in section.items() if k in visible))


def _geometry(variables: set[str], layout: str):
    if layout == 'NONE':
        return {}
    nodes = sorted(variables)
    if len(nodes) > MAX_VARIABLES:
        raise ValueError('display exceeds 13-node experimental bound')
    if layout == 'RADIAL':
        from math import cos, sin, tau
        return {node: [round(cos(tau * i / max(len(nodes), 1)), 6),
                       round(sin(tau * i / max(len(nodes), 1)), 6)]
                for i, node in enumerate(nodes)}
    positions = [(0, 0)] + list(HEX_AXIAL) + [(2 * q, 2 * r) for q, r in HEX_AXIAL]
    return {node: [round(q + r / 2, 6), round(sqrt(3) * r / 2, 6)]
            for node, (q, r) in zip(nodes, positions)}


class ContextualAtlas:
    def __init__(self, contexts: list[Context], lenses: list[Lens], questions: list[Question]):
        if not 1 <= len(contexts) <= MAX_CONTEXTS:
            raise ValueError('bounded 1..9 contexts required')
        if len({c.id for c in contexts}) != len(contexts):
            raise ValueError('duplicate context')
        if len({c.scope for c in contexts}) != 1:
            raise ValueError('cross-observer/cut/decoder gluing refused: require same scope')
        self.contexts = tuple(contexts)
        self.variables = set().union(*(set(c.variables) for c in contexts))
        if len(self.variables) > MAX_VARIABLES:
            raise ValueError('more than 13 variables')
        if not 1 <= len(lenses) <= 12 or len({l.id for l in lenses}) != len(lenses):
            raise ValueError('invalid lens set')
        if any(not set(l.variables) <= self.variables for l in lenses):
            raise ValueError('lens invents variables')
        if len(questions) > 32 or len({q.id for q in questions}) != len(questions):
            raise ValueError('invalid question set')
        if any(q.variable not in self.variables for q in questions):
            raise ValueError('question invents variable')
        self.lenses = {l.id: l for l in lenses}
        self.questions = tuple(questions)
        self.scope = contexts[0].scope
        # Check resource bounds at construction (not after publishing a partial result).
        self.sections = _sections(self.contexts)

    def _minimal_conflict(self):
        # Deletion-based subset-minimal inconsistent core, not minimum cardinality.
        core = list(self.contexts)
        for item in tuple(core):
            trial = [c for c in core if c.id != item.id]
            if trial and not _sections(tuple(trial)):
                core = trial
        return [{'context': c.id, 'claimed_source_root': c.source_root} for c in sorted(core, key=lambda c:c.id)]

    def inspect(self, selected_lenses: tuple[str, ...], *, display: bool = False):
        if len(set(selected_lenses)) != len(selected_lenses) or any(l not in self.lenses for l in selected_lenses):
            raise ValueError('unknown/duplicate selected lens')
        visible = set().union(*(set(self.lenses[l].variables) for l in selected_lenses)) if selected_lenses else set()
        coordinates = {name: _geometry(set(self.lenses[name].variables), self.lenses[name].layout)
                       for name in selected_lenses} if display else {}
        if not self.sections:
            return {'status': 'INCOMPATIBLE_LOCAL_CONTEXTS', 'scope': self.scope,
                    'minimal_conflict': self._minimal_conflict(),
                    'global_sections': 0, 'authority': 'NONE', 'instrument': 'PENCIL',
                    'coordinates': coordinates}
        projections = {_projection(s, visible) for s in self.sections}
        hidden = sorted(self.variables - visible)
        # Variables that demonstrably distinguish currently compatible worlds.
        useful_hidden = [v for v in hidden if len({s[v] for s in self.sections}) > 1]
        result = {'status': 'UNIQUE_WITHIN_GRAMMAR' if len(self.sections) == 1 else 'PLURAL_WORLD_MODELS',
                  'scope': self.scope, 'global_sections': len(self.sections),
                  'view_signatures': len(projections),
                  'representation_blind': len(self.sections) > 1 and len(projections) == 1,
                  'hidden_discriminators': useful_hidden,
                  'authority': 'NONE', 'instrument': 'PENCIL',
                  'coordinates': coordinates}
        # A representation may suggest a missing *question*, never a new fact.
        return result

    def next_question(self, selected_lenses: tuple[str, ...], *, budget: float = float('inf')):
        if isinstance(budget, bool) or not isinstance(budget, (int, float)) or budget <= 0 or budget != budget:
            raise ValueError('invalid budget')
        state = self.inspect(selected_lenses)
        if not self.sections:
            return {'status': 'HOLD', 'reason': 'incompatible local contexts; check assumptions or sources',
                    'minimal_conflict': state['minimal_conflict'], 'authority': 'NONE'}
        if len(self.sections) < 2:
            return {'status': 'HOLD', 'reason': 'only one model in declared grammar', 'authority': 'NONE'}
        visible = set().union(*(set(self.lenses[name].variables) for name in selected_lenses)) if selected_lenses else set()
        candidates = []
        for q in self.questions:
            if not q.permitted or q.cost > budget:
                continue
            bins = {}
            for section in self.sections:
                bins.setdefault(section[q.variable], 0)
                bins[section[q.variable]] += 1
            if len(bins) < 2:
                continue
            bits = _entropy(list(bins.values()))
            # Under uniform candidate weights, deterministic answers partition worlds.
            candidates.append({'question': q.id, 'variable': q.variable,
                               'information_gain_bits': round(bits, 9),
                               'gain_per_cost': round(bits / q.cost, 9),
                               'cost': q.cost,
                               'requires_reframing': q.variable not in visible,
                               'outcomes': dict(sorted(bins.items())),
                               'status': 'PROPOSED_ONLY'})
        candidates.sort(key=lambda item:(-item['gain_per_cost'], item['cost'], item['question']))
        if not candidates:
            return {'status': 'HOLD', 'reason': 'no permitted affordable discriminating question', 'authority': 'NONE'}
        return {'status': 'QUESTION_PROPOSED', 'best': candidates[0],
                'alternatives': candidates[1:], 'authority': 'NONE',
                'interpretation': 'classical entropy under uniform synthetic-world weights; no probe executed'}

    def filter_on_observation(self, variable: str, value: str, source_root: str):
        """Non-mutating what-if: supplied label, not actual measurement."""
        _id(source_root, 'source root')
        if variable not in self.variables or not isinstance(value, str):
            raise ValueError('invalid observation')
        matches = [s for s in self.sections if s[variable] == value]
        return {'status': 'PENCIL_COUNTERFACTUAL', 'source_root': source_root,
                'matching_sections': len(matches), 'previous_sections': len(self.sections),
                'authority': 'NONE'}


def from_geom006_models(models, *, scope: str):
    """Read-only bridge from GEOM-006 Model predictions; never carries admission.

    Intended as *candidate* alternatives for the contextual reasoner. Priors are
    deliberately not inherited as evidence. Source roots remain declarations.
    """
    if not 2 <= len(models) <= 32:
        raise ValueError('requires two to 32 GEOM-006 candidates')
    variables = tuple(sorted(models[0].predictions))
    if not variables or any(set(m.predictions) != set(variables) for m in models):
        raise ValueError('model prediction keys differ')
    alternatives = []
    seen = set()
    for m in models:
        alt = dict(m.predictions)
        signature = tuple(sorted(alt.items()))
        if signature not in seen:
            seen.add(signature)
            alternatives.append(alt)
    return Context('geom006-model-candidates', scope, variables, tuple(alternatives),
                   'geom006:declared-synthetic-models')


def run_document(doc: Mapping):
    """Small bounded JSON interchange, no implicit file/network effects."""
    if not isinstance(doc, Mapping):
        raise ValueError('request must be a mapping')
    allowed = {'contexts', 'lenses', 'questions', 'selected_lenses', 'display', 'budget'}
    if set(doc) - allowed:
        raise ValueError('unknown top-level key')
    contexts = [Context(c['id'], c['scope'], tuple(c['variables']), tuple(c['alternatives']), c['source_root'])
                for c in doc['contexts']]
    lenses = [Lens(l['id'], tuple(l['variables']), l.get('layout', 'NONE')) for l in doc['lenses']]
    questions = [Question(q['id'], q['variable'], q['cost'], q.get('permitted', False))
                 for q in doc['questions']]
    atlas = ContextualAtlas(contexts, lenses, questions)
    selected = tuple(doc.get('selected_lenses', ()))
    if type(doc.get('display', False)) is not bool:
        raise ValueError('display must be bool')
    return {'inspection': atlas.inspect(selected, display=doc.get('display', False)),
            'inquiry': atlas.next_question(selected, budget=doc.get('budget', float('inf')))}
