"""Read-only interpretation of a GEOM-005 JSON graph as THOUGHT-006 pencil.

The import creates *new local ledger events*. GEOM-005 `observed=True` means
an authored graph edge, NOT a verified observation. It is never a pen commit.
"""
from __future__ import annotations

from hashlib import sha256

from ledger import LedgerError, ThoughtLedger
from schema import ALLOWED_PREDICATES, nonempty_text


def import_geom005(snapshot: dict, ledger: ThoughtLedger, *, scope: str) -> list[str]:
    if not isinstance(snapshot, dict) or not isinstance(snapshot.get('nodes'), list) \
            or not isinstance(snapshot.get('edges'), list):
        raise ValueError('GEOM-005 snapshot requires nodes and edges arrays')
    if len(snapshot['nodes']) > 100 or len(snapshot['edges']) > 500:
        raise ValueError('GEOM-005 import bounded at 100 nodes and 500 edges')
    nonempty_text(scope, 'import scope')
    # Preflight structural shape before appending anything.
    nodes = snapshot['nodes']
    edges = snapshot['edges']
    if any(not isinstance(n, dict) or set(n) != {'id','label','kind'} for n in nodes):
        raise ValueError('invalid GEOM-005 node')
    if any(not isinstance(e, dict) or set(e) != {
        'source', 'target', 'relation', 'origin', 'confidence', 'observed'}
           for e in edges):
        raise ValueError('invalid GEOM-005 edge')
    if any(e['relation'] not in ALLOWED_PREDICATES or
           type(e['observed']) is not bool or
           not isinstance(e['origin'], str) or not e['origin'] or
           not isinstance(e['confidence'], (float, int)) or
           not 0 < e['confidence'] <= 1
           for e in edges):
        raise ValueError('invalid GEOM-005 edge fields')
    names = [n['id'] for n in nodes]
    if len(set(names)) != len(names):
        raise ValueError('duplicate GEOM-005 node')
    if any(e['source'] not in names or e['target'] not in names
           for e in edges):
        raise ValueError('dangling GEOM-005 edge')
    if any(n in ledger.nodes for n in names):
        raise LedgerError('duplicate imported identity; use a separate workspace')
    for n in nodes:
        ledger.register_node(n['id'], n['label'], n['kind'])
    source_ids = {}
    for e in edges:
        origin = e['origin']
        sid = 'import:' + sha256(origin.encode('utf-8')).hexdigest()[:24]
        if sid not in source_ids.values():
            ledger.register_source(sid, 'root:' + sha256(origin.encode('utf-8')).hexdigest(),
                                   'human_statement',
                                   'Unauthenticated GEOM-005 origin: ' + origin[:250])
        source_ids[origin] = sid
    assertions = []
    for index, e in enumerate(edges, 1):
        aid = f'import-edge-{index:05d}'
        ledger.sketch(aid, e['source'], e['relation'], e['target'], scope,
                      idea=f"GEOM-005 supplied {e['relation']} edge; confidence={e['confidence']} "
                           'is source-authored, not validated',
                      introduced_by=source_ids[e['origin']],
                      observed_input=e['observed'])
        assertions.append(aid)
    return assertions
