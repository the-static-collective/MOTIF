"""GEOM-008: a classical, auditable search for composed reasoning operators.

The grammar can grow in *depth* without a built-in ceiling, but each call
uses finite candidate-evaluation work. It does not invent new primitives
outside its typed path-expression grammar, nor does it verify real evidence.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable
from living_graph import LivingGraph, stable_id, nonempty


@dataclass(frozen=True)
class World:
    identity: str
    scope: str
    edges: tuple[tuple[str, str, str], ...]  # (from, relation_kind, to)
    expected: bool                          # synthetic supplied class, not truth oracle
    source_root: str = 'fixture:declared'

    def __post_init__(self) -> None:
        nonempty(self.identity, 'world id')
        nonempty(self.scope, 'world scope')
        nonempty(self.source_root, 'source root')
        if type(self.expected) is not bool:
            raise ValueError('expected label must be bool')
        for x in self.edges:
            if not isinstance(x, tuple) or len(x) != 3:
                raise ValueError('edge must be a (source, kind, target) triple')
            for part in x:
                nonempty(part, 'edge member')


@dataclass(frozen=True)
class Atom:
    relation: str
    reverse: bool = False

    def __post_init__(self) -> None:
        nonempty(self.relation, 'atom relation')
        if type(self.reverse) is not bool:
            raise ValueError('reverse must be a bool')

    def data(self) -> dict:
        return {'relation': self.relation, 'direction': 'reverse' if self.reverse else 'forward'}


def reaches(world: World, start: str, goal: str, program: tuple[Atom, ...]) -> bool:
    """Relational composition, no diagram/metric shortcuts."""
    vertices = {start}
    for atom in program:
        nxt = set()
        for source, rel, target in world.edges:
            if rel != atom.relation:
                continue
            if atom.reverse:
                source, target = target, source
            if source in vertices:
                nxt.add(target)
        if not nxt:
            return False
        vertices = nxt
    return goal in vertices


def _program(index: int, length: int, atoms: tuple[Atom, ...]) -> tuple[Atom, ...]:
    """Direct base-n unranking: resuming does not replay all old candidates."""
    base = len(atoms)
    output = []
    for _ in range(length):
        index, digit = divmod(index, base)
        output.append(atoms[digit])
    if index:
        raise ValueError('operator index outside current length')
    return tuple(reversed(output))


def _score(worlds: tuple[World, ...], start: str, goal: str,
           program: tuple[Atom, ...]) -> dict:
    count = sum(reaches(world, start, goal, program) == world.expected for world in worlds)
    return {'correct': count, 'total': len(worlds), 'accuracy': round(count / len(worlds), 6)}


def _validate_inputs(training: tuple[World, ...], heldout: tuple[World, ...],
                     start: str, goal: str) -> str:
    nonempty(start, 'start'); nonempty(goal, 'goal')
    if not training or not heldout:
        raise ValueError('requires training and separate heldout worlds')
    names = [w.identity for w in (*training, *heldout)]
    if len(set(names)) != len(names):
        raise ValueError('train/heldout overlap or duplicate identities')
    scopes = {w.scope for w in (*training, *heldout)}
    if len(scopes) != 1:
        raise ValueError('all worlds must share the identical observer/cut/decoder scope')
    if {w.expected for w in training} != {True, False}:
        raise ValueError('training requires both positive and negative controls')
    return next(iter(scopes))


def discover_composition(training: Iterable[World], heldout: Iterable[World],
                         *, start: str, goal: str, work_budget: int,
                         cursor: dict | None = None, allow_reverse: bool = False,
                         max_length: int | None = None) -> dict:
    """Invent an *expression* by composing existing typed relation atoms.

    - No arbitrary global operator-length cap unless caller requests one.
    - `work_budget` caps the number of candidates evaluated in this invocation.
    - Heldout labels are never used to pick the candidate; merely reported.
    - No externally sourced evidence is admitted, and nothing executes.
    """
    train = tuple(training)
    test = tuple(heldout)
    scope = _validate_inputs(train, test, start, goal)
    if type(work_budget) is not int or work_budget <= 0:
        raise ValueError('work_budget must be a positive integer')
    if type(allow_reverse) is not bool:
        raise ValueError('allow_reverse must be bool')
    if max_length is not None and (type(max_length) is not int or max_length < 1):
        raise ValueError('max_length must be a positive integer or None')
    kinds = sorted({relation for w in train for _, relation, _ in w.edges})
    if not kinds:
        return {'status': 'HOLD', 'reason': 'no training relation atoms', 'authority': 'NONE'}
    atoms = tuple(Atom(k, backward) for k in kinds for backward in ((False, True) if allow_reverse else (False,)))
    domain = stable_id('search:', {
        'train': [{'id': w.identity, 'scope': w.scope, 'edges': w.edges, 'expected': w.expected,
                   'root': w.source_root} for w in train],
        'heldout_ids': [w.identity for w in test],
        'start': start, 'goal': goal, 'reverse': allow_reverse})
    if cursor is None:
        length, index = 1, 0
    else:
        if not isinstance(cursor, dict) or set(cursor) != {'domain', 'length', 'index'} \
                or cursor['domain'] != domain or type(cursor['length']) is not int \
                or type(cursor['index']) is not int or cursor['length'] < 1 or cursor['index'] < 0:
            raise ValueError('invalid or mismatched continuation cursor')
        length, index = cursor['length'], cursor['index']

    # Best classical single-link control: selected by training alone.
    baseline = sorted((
        (-_score(train, start, goal, (atom,))['correct'], atom.relation, atom.reverse, (atom,))
        for atom in atoms), key=lambda x: x[:3])[0][3]
    baseline_data = {'program': [x.data() for x in baseline],
                     'train': _score(train, start, goal, baseline),
                     'heldout': _score(test, start, goal, baseline)}

    evaluated = 0
    while evaluated < work_budget:
        if max_length is not None and length > max_length:
            return {'status': 'NO_OPERATOR_WITHIN_REQUESTED_GRAMMAR',
                    'evaluated_this_slice': evaluated, 'baseline': baseline_data,
                    'authority': 'NONE'}
        total_this_length = len(atoms) ** length
        if index >= total_this_length:
            length += 1
            index = 0
            continue
        candidate = _program(index, length, atoms)
        index += 1
        evaluated += 1
        train_score = _score(train, start, goal, candidate)
        if train_score['correct'] == len(train):
            test_score = _score(test, start, goal, candidate)
            return {'status': 'EXISTING_ATOM_SUFFICIENT' if length == 1 else 'COMPOSITION_PROPOSED',
                    'representation_gap': length > 1 and baseline_data['train']['correct'] < len(train),
                    'program': [atom.data() for atom in candidate],
                    'length': length, 'train': train_score, 'heldout': test_score,
                    'baseline_single_relation': baseline_data,
                    'evaluated_this_slice': evaluated, 'scope': scope,
                    'source_roots': sorted({w.source_root for w in train}),
                    'status_of_assertion': 'PENCIL', 'authority': 'NONE',
                    'method': 'classical enumerative typed path-composition program synthesis',
                    'limitations': 'search grammar is existing relation atoms; heldout data is synthetic; no new atomic semantics'}
    return {'status': 'CONTINUE_SEARCH', 'evaluated_this_slice': evaluated,
            'next_cursor': {'domain': domain, 'length': length, 'index': index},
            'baseline_single_relation': baseline_data, 'authority': 'NONE',
            'status_of_assertion': 'PENCIL'}


def inspect_composition_on_graph(graph: LivingGraph, start_node: str,
                                 program: tuple[Atom, ...], *,
                                 transition_budget: int) -> dict:
    """Read-only, budget-limited evaluation of a composed 'rewrite' etc. path.

    Returns witnesses with relation IDs. If budget runs out, never claims
    exhaustion, absence or a comprehensive set of endpoints.
    """
    if type(transition_budget) is not int or transition_budget <= 0:
        raise ValueError('positive transition_budget required')
    if not program:
        raise ValueError('nonempty operator required')
    if not graph.db.execute('SELECT 1 FROM nodes WHERE id=?', (start_node,)).fetchone():
        raise ValueError('unknown start')
    current = {start_node: []}
    traversed = 0
    for atom in program:
        nxt = {}
        from_role, to_role = ('to', 'from') if atom.reverse else ('from', 'to')
        for node, path in sorted(current.items()):
            q = graph.db.execute('''SELECT dst.node_id AS target, r.id AS relation_id
                FROM participants src
                JOIN relations r ON src.relation_id=r.id
                JOIN participants dst ON dst.relation_id=r.id
                WHERE src.node_id=? AND src.role=? AND dst.role=? AND r.kind=?
                ORDER BY target,relation_id''', (node, from_role, to_role, atom.relation))
            for row in q:
                if traversed >= transition_budget:
                    return {'status': 'INCOMPLETE_RESOURCE_SLICE',
                            'transition_budget': transition_budget,
                            'transitions_seen': traversed,
                            'provisional_endpoints': sorted(nxt),
                            'authority': 'NONE', 'state': 'PENCIL'}
                traversed += 1
                nxt.setdefault(row['target'], path + [row['relation_id']])
        current = nxt
        if not current:
            break
    return {'status': 'COMPLETE_WITHIN_OPERATOR_AND_GRAPH',
            'endpoints': [{'node_id': node, 'relation_witnesses': path}
                          for node, path in sorted(current.items())],
            'transitions_seen': traversed, 'state': 'PENCIL', 'authority': 'NONE',
            'interpretation': 'derived path over PENCIL relations, not admitted evidence'}


def world_from_document(obj: dict) -> World:
    allowed = {'id', 'scope', 'edges', 'expected', 'source_root'}
    if not isinstance(obj, dict) or set(obj) - allowed:
        raise ValueError('invalid world document')
    if not isinstance(obj.get('edges'), list):
        raise ValueError('edges must be list')
    return World(obj['id'], obj['scope'], tuple(tuple(e) for e in obj['edges']),
                 obj['expected'], obj.get('source_root', 'fixture:declared'))


def preserve_as_pencil(graph: LivingGraph, result: dict, training: Iterable[World],
                       heldout: Iterable[World], *, start: str, goal: str) -> dict:
    """Record a proposed macro and its *declared synthetic* evaluation lineage.

    Recomputes claims; stores N-ary witness hyperedge, no PEN or permissions.
    Only local immutable PENCIL nodes are appended, no remote effects.
    """
    train, test = tuple(training), tuple(heldout)
    scope = _validate_inputs(train, test, start, goal)
    if scope != graph.scope:
        raise ValueError('cannot import candidate across scope')
    if not isinstance(result, dict) or result.get('status') not in (
            'COMPOSITION_PROPOSED', 'EXISTING_ATOM_SUFFICIENT'):
        raise ValueError('only an explicitly proposed program can be stored')
    steps = result.get('program')
    if not isinstance(steps, list) or not steps:
        raise ValueError('missing proposed program')
    if any(not isinstance(d, dict) or set(d) != {'relation', 'direction'}
           or d['direction'] not in ('forward', 'reverse') for d in steps):
        raise ValueError('bad operator program')
    program = tuple(Atom(x['relation'], x['direction'] == 'reverse') for x in steps)
    train_score, heldout_score = _score(train, start, goal, program), _score(test, start, goal, program)
    if train_score['correct'] != len(train):
        raise ValueError('candidate does not solve supplied training controls')
    if train_score != result.get('train') or heldout_score != result.get('heldout'):
        raise ValueError('reported scores do not match independently repeated checks')

    program_payload = {'scope': scope, 'start': start, 'goal': goal,
                       'program': [x.data() for x in program],
                       'train': train_score, 'heldout': heldout_score,
                       'meaning': 'hypothetical derived relation, not a new atomic fact'}
    program_id = stable_id('macro:', program_payload)
    graph.add_node(program_id, kind='reason_cartridge_candidate',
                   label=' ○ '.join(a.relation + ('^-1' if a.reverse else '') for a in program),
                   payload=program_payload, source_root='local:synthetic-program-search')
    witnesses = [('candidate', program_id)]
    for role, set_of_worlds in (('train_case', train), ('heldout_case', test)):
        for w in set_of_worlds:
            content = {'id': w.identity, 'scope': w.scope, 'edges': w.edges,
                       'expected_label': w.expected, 'claimed_root': w.source_root}
            world_id = stable_id('world:', content)
            graph.add_node(world_id, kind='synthetic_world', label=w.identity,
                           payload=content, source_root=w.source_root)
            witnesses.append((role, world_id))
    graph.add_relation('proposed_operator_evaluated_against', witnesses,
                       source_root='local:synthetic-program-search',
                       note={'status': 'PENCIL', 'assertion': 'recomputed synthetic matches',
                             'not': 'proof of truth or independent source authentication'})
    return {'status': 'PENCIL_CARTRIDGE_STORED', 'candidate_node': program_id,
            'witness_count': len(witnesses) - 1, 'authority': 'NONE'}
