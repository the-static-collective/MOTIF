"""Read-only projection of THOUGHT-006 reviewed claims into THOUGHT-008.

An explicit ID binding is mandatory: same spelling never implies same concept.
Legacy PEN is only a scoped source assertion, not verified reality or permission.
"""
from __future__ import annotations
from multiview import ViewError

PREDICATES = {'associated', 'requires', 'enables', 'contradicts'}


def from_ledger_snapshot(ledger_snapshot, field_snapshot, bindings):
    """Return (relations, skipped) from an immutable 006 snapshot.

    An operator supplies legacy NODE id -> THOUGHT-007 manifestation id.
    An unsupported type/unknown endpoint is *skipped or rejected*, never guessed.
    """
    if (not isinstance(ledger_snapshot,dict) or
        ledger_snapshot.get('schema')!='motif.thought-ledger.snapshot.v1'):
        raise ViewError('requires THOUGHT-006 ledger snapshot')
    if (not isinstance(field_snapshot,dict) or not isinstance(bindings,dict) or
        field_snapshot.get('semantic',{}).get('schema')!='motif.thought-field.semantics.v1'):
        raise ViewError('field snapshot and explicit bindings required')
    manifests={m['id'] for m in field_snapshot['semantic'].get('manifestations',[])}
    legacy={n['id'] for n in ledger_snapshot.get('nodes',[])}
    if not bindings or set(bindings)-legacy or any(v not in manifests for v in bindings.values()):
        raise ViewError('unknown source or manifestation binding')
    if len(set(bindings.values()))!=len(bindings):
        raise ViewError('legacy identity conflation is not implicit')
    sources={s['id']:s for s in ledger_snapshot.get('sources',[])}
    links=[];skipped=[]
    for a in ledger_snapshot.get('assertions',[]):
        aid=a.get('id')
        if a.get('predicate') not in PREDICATES:
            skipped.append({'assertion_id':aid,'reason':'predicate not structurally supported'})
            continue
        if a.get('subject') not in bindings or a.get('object') not in bindings:
            skipped.append({'assertion_id':aid,'reason':'missing explicit context binding'})
            continue
        declared=a.get('introduced_by')
        if declared not in sources:
            raise ViewError('unknown legacy source')
        is_pen=(a.get('mode')=='PEN' and a.get('status')=='PEN_SCOPED' and
                not a.get('challenges'))
        links.append(dict(id='ledger:'+aid,source=bindings[a['subject']],
            target=bindings[a['object']],predicate=a['predicate'],
            origin='claimed-root:'+sources[declared]['root'],
            status='AUTHORED' if is_pen else 'HYPOTHESIS_ONLY'))
    return links,skipped
