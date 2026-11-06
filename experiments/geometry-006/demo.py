"""Reproducible synthetic 13-center temporal-staircase demonstration."""
from __future__ import annotations
import json
from staircase import Atlas, Place, Relation, Model, Probe, select_question


def example():
    ids = ['c'] + [f'i{i}' for i in range(6)] + [f'o{i}' for i in range(6)]
    places = [Place(id, 0, {'ada': 0, 'bo': 0}) for id in ids]
    def edge(id, a, b, kind, begins, discovered, admitted=None,
             *, ends=None, withdrawn=None, visibility=None, duration=1):
        return Relation(id, a, b, kind, begins, ends, discovered, admitted,
                        withdrawn, visibility or {'ada': discovered, 'bo': discovered},
                        'synthetic:' + id, duration)
    edges = [
        edge('e1', 'c', 'i0', 'route', 1, 1, 2),
        edge('e2', 'i0', 'o0', 'route', 2, 2, 3),
        # The direct link is perceptually enticing but NOT admitted or traversable.
        edge('pretty', 'c', 'o0', 'resembles', 1, 1),
        # Historical relationship, discovered much later. Different observer access.
        edge('late', 'c', 'i2', 'causes', 1, 8, 9, visibility={'ada': 8, 'bo': 12}),
        # A usable route later withdrawn; the receipt is not erased.
        edge('withdrawn', 'i4', 'o4', 'route', 2, 2, 3, withdrawn=8),
        # Aggregate graph looks connected but this route closes too early.
        edge('expired', 'i1', 'o1', 'route', 1, 1, 2, ends=3, duration=2),
        edge('to_i1', 'c', 'i1', 'route', 2, 2, 3, duration=2),
        # Pencil only: no invented relation from geometry.
        edge('temptation', 'i3', 'o3', 'route', 1, 1),
    ]
    return Atlas(places, edges)


def run():
    atlas = example()
    early = atlas.view(4, 4, 'ada')
    hindsight = atlas.view(4, 10, 'ada', geometry=True)
    bo = atlas.view(4, 10, 'bo')
    no_picture = atlas.view(4, 10, 'ada', geometry=False)
    m = [Model('world-A', 0.5, {'scan': 'same', 'ledger': 'old', 'expensive': 'x'}),
         Model('world-B', 0.5, {'scan': 'same', 'ledger': 'new', 'expensive': 'y'})]
    q = [Probe('scan', 1, True), Probe('ledger', 2, True),
         Probe('expensive', 100, True), Probe('unauthorized', 0.1, False)]
    return {'name': 'MOTIF-GEOM-006 synthetic Staircase Lab',
            'early_edges': [(e['id'], e['state']) for e in early['relations']],
            'hindsight_edges': [(e['id'], e['state']) for e in hindsight['relations']],
            'bo_edges_at_same_cut': [(e['id'], e['state']) for e in bo['relations']],
            'historical_path': atlas.earliest_route('c', 'o0', 0, 4, 10, 'ada'),
            'expired_path_held': atlas.earliest_route('c', 'o1', 0, 8, 10, 'ada'),
            'unadmitted_path_held': atlas.earliest_route('i3', 'o3', 0, 4, 10, 'ada'),
            'selected_question': select_question(m, q),
            'no_geometry_invariant': ({k:v for k,v in hindsight.items() if k not in ('projection','coordinates')} ==
                                      {k:v for k,v in no_picture.items() if k not in ('projection','coordinates')}),
            'authority': 'NONE'}


if __name__ == '__main__':
    print(json.dumps(run(), sort_keys=True, indent=2))
