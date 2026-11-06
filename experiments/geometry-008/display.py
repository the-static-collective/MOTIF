"""Small, partial Graphviz DOT projections of an arbitrarily large hypergraph.

This is a view renderer, not a spatial truth model. N-ary relations become
explicit hubs. Never render the full giant graph by default.
"""
import hashlib
import json


def _q(value: str) -> str:
    # Double-quoted DOT with JSON escaping for quotes, newlines and backslashes.
    return json.dumps(str(value), ensure_ascii=True)


def render_dot(view: dict) -> str:
    if not isinstance(view, dict) or not isinstance(view.get('nodes'), list) \
            or not isinstance(view.get('relations'), list):
        raise ValueError('expects a GEOM-008 bounded neighborhood view')
    lines = [
        'digraph LivingAtlas {',
        '  graph [label="PENCIL-only partial projection; layout is not evidence",labelloc=t];',
        '  node [shape=ellipse];',
    ]
    valid = set()
    for node in view['nodes']:
        identity = node['id']
        valid.add(identity)
        name = 'n' + hashlib.sha256(identity.encode()).hexdigest()[:24]
        label = node['label'] + '\n[' + node['kind'] + '/PENCIL]'
        lines.append(f'  {name} [label={_q(label)}];')
    for rel in view['relations']:
        hub = 'r' + hashlib.sha256(rel['id'].encode()).hexdigest()[:24]
        lines.append(f'  {hub} [shape=diamond,label={_q(rel["kind"])}];')
        for p in rel['participants']:
            if p['node_id'] not in valid:
                continue
            name = 'n' + hashlib.sha256(p['node_id'].encode()).hexdigest()[:24]
            role = p['role']
            if role in ('to', 'child', 'target'):
                lines.append(f'  {hub} -> {name} [label={_q(role)}];')
            else:
                lines.append(f'  {name} -> {hub} [label={_q(role)}];')
    lines.append('}')
    return '\n'.join(lines) + '\n'
