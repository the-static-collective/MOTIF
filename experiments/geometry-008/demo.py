"""Reproducible GEOM-008 free-shape, persistent growth + macro proposal demo."""
import json
import tempfile
from pathlib import Path
from living_graph import LivingGraph, RewriteGrammar, RewriteRule
from repair import Atom, World, discover_composition, inspect_composition_on_graph, preserve_as_pencil


def binary_grammar():
    return RewriteGrammar('observer:demo|cut:0|decoder:literal', (
        RewriteRule('write-0', ('#',), ('0', '#')),
        RewriteRule('write-1', ('#',), ('1', '#')),
    ))


def worlds(part):
    out = []
    for i in range(3):
        mid = f'{part}-middle-{i}'
        # Same typed edge histogram, different two-step compositional relation.
        pos = (('origin', 'carry', mid), (mid, 'serve', 'destination'))
        neg = (('origin', 'serve', mid), (mid, 'carry', 'destination'))
        out += [World(f'{part}-positive-{i}', binary_grammar().scope, pos, True, 'fixture:pos'),
                World(f'{part}-negative-{i}', binary_grammar().scope, neg, False, 'fixture:neg')]
    return tuple(out)


def main():
    grammar = binary_grammar()
    train, holdout = worlds('train'), worlds('heldout')
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / 'atlas.db'
        with LivingGraph(path, scope=grammar.scope) as graph:
            root = graph.seed(['#'], source_root='fixture:synthetic-axiom')
            first = graph.grow(grammar, work_budget=100)
        with LivingGraph(path, scope=grammar.scope) as graph:
            second = graph.grow(grammar, work_budget=200)
            proposed = discover_composition(train, holdout, start='origin',
                                            goal='destination', work_budget=64)
            record = preserve_as_pencil(graph, proposed, train, holdout,
                                        start='origin', goal='destination')
            query = inspect_composition_on_graph(graph, root,
                                                  (Atom('rewrite'), Atom('rewrite')),
                                                  transition_budget=64)
            return {'name': 'MOTIF-GEOM-008 — Grammar-Grown Living Graph',
                    'scope': grammar.scope, 'first_slice': first,
                    'second_slice': second, 'reason_cartridge': proposed,
                    'preserved_cartridge': record,
                    'relational_query': query,
                    'sample_view': graph.neighborhood(root, hops=1,
                                                      node_budget=8, relation_budget=12),
                    'integrity': graph.verify(),
                    'limits': {'global_nodes': 'no artificial cap',
                               'global_edges': 'no artificial cap',
                               'relation_arity': 'no artificial cap',
                               'invocation': 'finite work/time budget',
                               'epistemic': 'PENCIL only, never authenticated PEN'}}


if __name__ == '__main__':
    print(json.dumps(main(), indent=2, sort_keys=True))
