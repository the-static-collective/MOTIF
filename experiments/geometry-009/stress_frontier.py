"""GEOM-009 temporary near-unbounded work-budget stress experiment.

Large `work_budget` removes its *practical* binding effect; a monotonic clock
still prevents infinite work. The grammar is deliberately controlled (two child
rewrites per node, max ~3 relations per expansion) to avoid an explosive
single-node transaction. No wall-clock guarantee for a pathological grammar.
"""
import argparse
import json
import os
import resource
import tempfile
import time
from pathlib import Path

from living_graph import LivingGraph, RewriteGrammar, RewriteRule

HUGE_WORK_BUDGET = 10**15


def run(seconds_slices=(1.0,1.0), *, huge_budget=HUGE_WORK_BUDGET):
    if not seconds_slices or any(type(t) not in (int,float) or t <= 0 or t != t or t == float('inf') for t in seconds_slices):
        raise ValueError('nonempty positive finite time slices required')
    if type(huge_budget) is not int or huge_budget <= 0:
        raise ValueError('positive integer huge budget required')
    with tempfile.TemporaryDirectory(prefix='motif-009-stress-') as tmp:
        filename=Path(tmp)/'stress.sqlite'
        grammar=RewriteGrammar('geom009:synthetic-stress', (
            RewriteRule('append-0',('#',),('0','#')),
            RewriteRule('append-1',('#',),('1','#')),
        ))
        with LivingGraph(filename, scope=grammar.scope) as graph:
            graph.seed(['#'],source_root='synthetic:seed')
            slices=[]
            for number,seconds in enumerate(seconds_slices,1):
                t0=time.perf_counter()
                result=graph.grow(grammar,work_budget=huge_budget,seconds=seconds)
                elapsed=time.perf_counter()-t0
                current=result['totals']
                expected_nodes=1+2*current['expanded']
                expected_relations=3*current['expanded']
                if (current['nodes'] != expected_nodes or
                    current['relations'] != expected_relations or
                    current['unexpanded'] != current['expanded']+1):
                    raise AssertionError('independent binary-tree growth invariants violated')
                slices.append({'slice':number,'seconds_declared':seconds,
                    'seconds_measured':round(elapsed,3),
                    'expansions':result['expanded_this_slice'],'stop_reason':result['status'],
                    'nodes':current['nodes'],'relations':current['relations'],
                    'unexpanded':current['unexpanded'],
                    'db_bytes_allocated_approx':current['db_bytes_allocated_approx'],
                    'process_peak_rss_kb':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss})
            integrity=graph.verify()
            final=graph.counts()
        return {'experiment':'GEOM-009 intentionally huge temporary work-budget, timed synthetic growth',
            'requested_work_budget_each_slice':huge_budget,'deadline_seconds_slices':list(seconds_slices),
            'results':slices,'final':final,'integrity':integrity,
            'growth_invariants':'complete binary rewrite tree: nodes=2*expanded+1, relations=3*expanded, unexpanded=expanded+1',
            'limits':'wall clock, storage and memory remain physical bounds; no unbounded compute was run',
            'db_state':'temporary local SQLite file deleted after verification',
            'state':'PENCIL', 'authority':'NONE'}

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--seconds',type=float,nargs='+',default=[1,1])
    parser.add_argument('--work-budget',type=int,default=HUGE_WORK_BUDGET)
    args=parser.parse_args()
    print(json.dumps(run(args.seconds,huge_budget=args.work_budget),indent=2,sort_keys=True))
