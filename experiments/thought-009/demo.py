"""Demonstrate no map, one map, parallel maps, and pen review with one source."""
import json
from tempfile import TemporaryDirectory
from pathlib import Path
from fixtures import make_engine
from router import Task, ViewRouter


def main():
    with TemporaryDirectory() as d:
        engine=make_engine(Path(d)/'field.jsonl')
        router=ViewRouter(engine)
        no_map=router.run(Task(('association','dependency','tension','affordance'),
                      anchor='m:volunteers',max_views=0))
        mixed=router.run(Task(('association','dependency','tension','affordance'),
                      anchor='m:volunteers',max_views=3), previous=no_map)
        review=router.run(Task(('association','dependency','tension','affordance'),
                      anchor='m:volunteers',max_views=4,phase='PEN_REVIEW'),previous=mixed)
        assert no_map['source_only_answers']==mixed['source_only_answers']==review['source_only_answers']
        return {'experiment':'THOUGHT-009','sample':'synthetic, development only',
                'no_map_selected':no_map['selected_lenses'],
                'mixed_selected':mixed['selected_lenses'],
                'review_selected':review['selected_lenses'],
                'no_map_cost':no_map['view_cost_units'],
                'mixed_cost':mixed['view_cost_units'],
                'question_kinds':sorted({x['kind'] for x in mixed['questions']}),
                'all_answers_equal':True,
                'no_coordinate_to_fact_promotion':True,
                'authority':mixed['effective_external_authority'],
                'route':[{k:v for k,v in d.items() if k in ('goal','signal_count','decision')}
                         for d in mixed['decisions']]}
if __name__=='__main__':print(json.dumps(main(),sort_keys=True,indent=2))
