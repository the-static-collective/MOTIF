"""Bounded JSON CLI for GEOM-006. No network, side effects or tool dispatch."""
import json
import sys
from pathlib import Path
from staircase import Atlas, Place, Relation, Model, Probe, select_question


def process(data):
    if not isinstance(data, dict):
        raise ValueError('object expected')
    task = data.get('task')
    if task == 'question':
        if len(data.get('models', [])) > 32 or len(data.get('probes', [])) > 64:
            raise ValueError('question capacity exceeded')
        result = select_question([Model(**x) for x in data['models']],
                                 [Probe(**x) for x in data['probes']])
    elif task in ('view', 'route'):
        places = [Place(**x) for x in data['places']]
        edges = [Relation(**x) for x in data['relations']]
        if len(places) > 13 or len(edges) > 128:
            raise ValueError('atlas capacity exceeded')
        atlas = Atlas(places, edges)
        q = data['query']
        if task == 'view':
            result = atlas.view(q['world_cut'],q['knowledge_cut'],q['observer'],
                                geometry=q.get('geometry',False))
        else:
            result = atlas.earliest_route(q['source'],q['target'],q['start_at'],
                                          q['world_cut'],q['knowledge_cut'],q['observer'])
    else:
        raise ValueError('expected task=view|route|question')
    return {'contract':'motif.geom-006/v0', 'result':result, 'authority':'NONE'}


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('usage: python interface.py INPUT.json')
    source=Path(sys.argv[1]); raw=source.read_bytes()
    if len(raw)>256_000:
        raise SystemExit('input too large')
    print(json.dumps(process(json.loads(raw)),indent=2,sort_keys=True))
