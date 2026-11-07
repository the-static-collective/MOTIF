"""Reproducible read-only demonstration of both mathal layers."""
import json
from mathal import nominate_motif003
from nunumathal import Graph, perform, compare


def demonstration():
    graph=Graph.build({'a','b','c'},[('a','b'),('b','c')])
    a=perform(graph,'isolated','d')
    b=perform(graph,'subdivide','d',edge=('b','c'))
    nominations=nominate_motif003([{'operator':'repair','roles':('actor','bike')}])
    return {
        'scope':'synthetic, local, counterfactual',
        'same_n_different_mechanism':compare(a,b),
        'motif003_nominations':[{'status':r.status,'facts':len(r.world.facts),
                                 'ideas':len(r.world.ideas)} for r in nominations],
        'external_actions':0,
    }

if __name__=='__main__':
    print(json.dumps(demonstration(),indent=2))
