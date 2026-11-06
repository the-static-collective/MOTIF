"""THOUGHT-010: bounded local JSON doorway to MOTIF's thought instruments.

No HTTP listener, accounts, connector access, subprocess execution, or external
writes. All outputs are proposals. Callable by a local JAR;VIS process or
another steward via explicitly supplied JSON. Transport and owner admission
are OUTSIDE this module's authority.
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parent.parent
for name in ('thought-007', 'thought-008', 'thought-009'):
    sibling = str(ROOT / name)
    if sibling not in sys.path:
        sys.path.append(sibling)
from field import ThoughtField
from multiview import ThoughtViews, ViewError, digest
from router import Task, ViewRouter, GOALS, PHASES

REQUEST = 'motif.thought-door.request.v1'
REPLY = 'motif.thought-door.reply.v1'
MAX_REQUEST = 120_000
KNOWN_FIELDS = frozenset({
    'schema', 'request_id', 'caller', 'mode', 'purpose', 'question',
    'ideas', 'relationships', 'field_snapshot', 'relations',
    'goals', 'anchor', 'max_views', 'show_geometry', 'phase', 'seed',
    'include_views', 'privacy', 'export', 'allow_export',
})
PRIVACY = ('PRIVATE_LOCAL', 'PUBLIC_FIXTURE')

class DoorError(ValueError):
    """Fail-closed schema, scope, privacy or identity violation."""


def check_text(value, what, size=160):
    if not isinstance(value, str) or not value.strip() or len(value) > size:
        raise DoorError(f'{what}: non-empty bounded text required')
    return value


def _guard_request(req):
    if not isinstance(req, dict) or set(req) - KNOWN_FIELDS:
        raise DoorError('request must be an object using the versioned schema fields')
    try:
        size = len(json.dumps(req, ensure_ascii=True, sort_keys=True,
                              allow_nan=False, separators=(',', ':')).encode())
    except (TypeError, ValueError) as ex:
        raise DoorError('request must be strictly JSON encodable') from ex
    if size > MAX_REQUEST:
        raise DoorError('request exceeds local 120KB limit')
    if req.get('schema') != REQUEST:
        raise DoorError('unsupported request schema version')
    for key in ('request_id', 'caller', 'purpose'):
        check_text(req.get(key), key)
    if req.get('caller') not in ('jarvis-local', 'free-graph-local', 'operator-local'):
        raise DoorError('only known local caller labels supported; labels are not authentication')
    if req.get('mode') not in ('ideas', 'snapshot'):
        raise DoorError('select ideas or snapshot mode')
    check_text(req.get('question', 'Explore this structure'), 'question', 300)
    if req.get('privacy', 'PRIVATE_LOCAL') not in PRIVACY:
        raise DoorError('explicit valid privacy class required')
    if req.get('export', 'NONE') not in ('NONE', 'FREE_GRAPH_V0'):
        raise DoorError('unknown export target')
    for key in ('show_geometry', 'include_views', 'allow_export'):
        if key in req and type(req[key]) is not bool:
            raise DoorError(f'{key} must be boolean')
    if 'max_views' in req and (type(req['max_views']) is not int or not 0 <= req['max_views'] <= 5):
        raise DoorError('max_views must be 0..5')
    if 'seed' in req and (type(req['seed']) is not int or not -100000 <= req['seed'] <= 100000):
        raise DoorError('seed must be a bounded integer')
    if 'goals' in req and (not isinstance(req['goals'], list) or not req['goals']
                           or len(req['goals']) > len(GOALS) or
                           any(type(g) is not str or g not in GOALS for g in req['goals']) or
                           len(set(req['goals'])) != len(req['goals'])):
        raise DoorError('goals must be unique recognized typed intentions')
    if req.get('phase', 'ABSTRACT_PENCIL') not in PHASES:
        raise DoorError('invalid thought phase')
    if req['mode'] == 'ideas':
        if 'field_snapshot' in req or 'relations' in req or 'anchor' in req:
            raise DoorError('ideas mode does not accept snapshot, relations or anchor')
        ideas = req.get('ideas')
        if not isinstance(ideas, list) or not 1 <= len(ideas) <= 24:
            raise DoorError('ideas mode requires 1..24 ideas')
        for s in ideas: check_text(s, 'idea', 160)
        rels = req.get('relationships', [])
        if not isinstance(rels, list) or len(rels) > 120:
            raise DoorError('invalid relationships length')
        for i, r in enumerate(rels):
            if not isinstance(r, dict) or set(r) != {'from', 'to', 'predicate', 'origin', 'status'}:
                raise DoorError('each relationship requires exactly five explicit fields')
            if type(r['from']) is not int or type(r['to']) is not int or \
               not (0 <= r['from'] < len(ideas)) or not (0 <= r['to'] < len(ideas)) or \
               r['from'] == r['to']:
                raise DoorError('relationship endpoints require distinct valid idea indices')
            if r['predicate'] not in ('associated', 'requires', 'enables', 'contradicts', 'precedes'):
                raise DoorError('unsupported relationship predicate')
            if r['status'] not in ('AUTHORED', 'HYPOTHESIS_ONLY'):
                raise DoorError('relationship status must be declared')
            check_text(r['origin'], f'relationship[{i}].origin')
    else:
        if 'ideas' in req or 'relationships' in req:
            raise DoorError('snapshot mode cannot invent or reinterpret extra ideas')
        if not isinstance(req.get('field_snapshot'), dict) or not isinstance(req.get('relations'), list):
            raise DoorError('snapshot mode requires field_snapshot and relations')
        if 'anchor' in req and req['anchor'] is not None:
            check_text(req['anchor'], 'anchor')


def _infer_goals(question: str) -> tuple[str, ...]:
    """Transparent trigger words, NOT a natural-language understanding model."""
    q = question.lower()
    picked = []
    for goal, keywords in (
        ('tension', ('contradict', 'conflict', 'disagree', 'incompatible')),
        ('dependency', ('require', 'depend', 'prerequisite', 'need before')),
        ('affordance', ('enable', 'possible action', 'open up', 'affordance')),
        ('association', ('connect', 'relat', 'associat', 'link', 'pattern')),
    ):
        if any(k in q for k in keywords):
            picked.append(goal)
    return tuple(picked) or ('inventory',)


def _make_ideas_engine(req):
    # Each occurrence gets a unique identity. Duplicate labels are NOT merged.
    # Temporary local storage is never an upstream or third-party write.
    with TemporaryDirectory(prefix='motif-thought-door-') as directory:
        f = ThoughtField(Path(directory) / 'field.jsonl')
        for i, phrase in enumerate(req['ideas']):
            cid, mid = f'concept:{i:02d}', f'm:{i:02d}'
            f.concept(cid, phrase, 'Caller-supplied idea occurrence; not a verified concept match',
                      'local:request')
            f.manifest(mid, cid, 'local requested thought-space', 'candidate idea')
        links = [dict(id=f'r:{i:03d}', source=f'm:{r["from"]:02d}',
                      target=f'm:{r["to"]:02d}', predicate=r['predicate'],
                      origin=r['origin'], status=r['status'])
                 for i, r in enumerate(req.get('relationships', []))]
        snapshot = f.snapshot()
    return ThoughtViews(snapshot, links)


def _validate_anchor(engine, req):
    anchor = req.get('anchor')
    if anchor is not None and anchor not in engine.manifests:
        raise DoorError('unknown manifestation anchor; no label-based guessing')
    return anchor


def handle(req: dict) -> dict:
    """Pure request/reply interface (apart from self-deleting local temp ledger).

    The response contains stable typed IDs, source-only answers, bounded view
    summaries and review questions. No automatic PEN commits or remote effects.
    """
    _guard_request(req)
    req = copy.deepcopy(req)
    try:
        engine = (_make_ideas_engine(req) if req['mode'] == 'ideas' else
                  ThoughtViews(req['field_snapshot'], req['relations']))
        anchor = _validate_anchor(engine, req)
        task = Task(goals=tuple(req.get('goals') or _infer_goals(req.get('question', ''))),
                    anchor=anchor, max_views=req.get('max_views', 2),
                    show_geometry=req.get('show_geometry', True),
                    phase=req.get('phase', 'ABSTRACT_PENCIL'),
                    seed=req.get('seed', 0))
        result = ViewRouter(engine).run(task)
    except (ViewError, ValueError) as ex:
        raise DoorError('invalid underlying thought field or typed task: ' + str(ex)) from ex

    summaries = [{'lens': v['lens'], 'placement_count': len(v['placements']),
                  'authored_and_proposed_relations': len(v['relations']),
                  'source_evidence_digest': v['source_evidence_digest'],
                  'coordinate_authority': 'NONE'}
                 for v in result['views']]
    response = {
        'schema': REPLY, 'request_id': req['request_id'], 'caller': req['caller'],
        'status': 'PROPOSAL_ONLY', 'mode': req['mode'],
        'privacy': req.get('privacy', 'PRIVATE_LOCAL'),
        'source_evidence_digest': result['source_evidence_digest'],
        'source_snapshot_digest': result['source_snapshot_digest'],
        'receipt_digest': result['receipt_digest'],
        'selected_lenses': result['selected_lenses'],
        'selection_trace': result['decisions'],
        'source_only_answers': result['source_only_answers'],
        'questions': result['questions'],
        'view_summaries': summaries,
        'view_cost_units': result['view_cost_units'],
        'pen_status': 'UNCHANGED', 'external_authority': 'NONE',
        'claimed_witnesses_authenticated': False,
        'warnings': [
            'Local source labels are not authenticated witnesses.',
            'Coordinates are neither evidence nor semantic truth.',
            'No downstream world has accepted this packet; external authority is NONE.',
        ],
    }
    if req.get('include_views', False):
        response['views'] = result['views']
    if req['mode'] == 'ideas' and not req.get('relationships'):
        response['warnings'].append('No typed relationships supplied; zero relations were inferred from idea labels.')
    if req.get('export') == 'FREE_GRAPH_V0':
        if req.get('privacy', 'PRIVATE_LOCAL') != 'PUBLIC_FIXTURE' or not req.get('allow_export', False):
            response['export'] = {'status': 'HOLD', 'reason': 'Explicit PUBLIC_FIXTURE and allow_export=true required'}
        else:
            from free_graph import export_seed_packet
            response['export'] = {
                'status': 'PROPOSAL_ONLY',
                'packet': export_seed_packet(engine, req['purpose'], req['request_id'])
            }
    else:
        response['export'] = {'status': 'NOT_REQUESTED'}
    return response


def main(argv=None):
    """Explicit local file-in -> stdout JSON. Never sends to other projects."""
    import argparse
    parser = argparse.ArgumentParser(description='MOTIF local thought door: no network or automatic dispatch')
    parser.add_argument('request_file', type=Path)
    args = parser.parse_args(argv)
    raw = args.request_file.read_bytes()
    if len(raw) > MAX_REQUEST:
        raise DoorError('file exceeds local request limit')
    try: request = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise DoorError('request must be valid UTF-8 JSON') from exc
    print(json.dumps(handle(request), sort_keys=True, indent=2, allow_nan=False))

if __name__ == '__main__':
    main()
