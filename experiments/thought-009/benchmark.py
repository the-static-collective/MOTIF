"""Frozen synthetic control scenarios, measured routing cost and answer parity.

No blind data; fixture expectations authored with the policy. Demonstrates
coherent routing and conservative abstention, not increased answer correctness.
"""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from router import Task,ViewRouter
from fixtures import make_engine

CASES=[
  ('association_bridge','association_only',('association',),None,2,('association',)),
  ('absent_bridge','empty',('association',),None,2,()),
  ('dependency_path','dependencies_only',('dependency',),None,2,('dependency',)),
  ('tension','tension_only',('tension',),None,2,('tension',)),
  ('affordance_conditional','full',('affordance',),'m:volunteers',2,('affordance',)),
  ('inventory','full',('inventory',),None,2,()),
  ('mixed','full',('association','tension'),None,2,('association','tension')),
  ('budgeted','full',('association','tension','dependency'),None,1,('dependency',)),
  ('zero_budget','full',('tension','dependency'),None,0,()),
  ('no_evidence_tension','empty',('tension',),None,2,()),
  ('no_anchor_affordance','full',('affordance',),None,2,()),
]


def main():
    cases=[];passes=0;map_count=0;all_views=0
    with TemporaryDirectory() as td:
        for i,(label,variant,goals,anchor,budget,expected) in enumerate(CASES):
            engine=make_engine(Path(td)/f'f-{i}.jsonl',variant)
            router=ViewRouter(engine)
            task=Task(goals=goals,anchor=anchor,max_views=budget)
            actual=router.run(task)
            control=router.run(Task(goals=goals,anchor=anchor,max_views=0))
            parity=(actual['source_only_answers']==control['source_only_answers'] and
                    actual['questions']==control['questions'])
            selected=tuple(actual['selected_lenses'])
            expected_ok=set(selected)==set(expected)
            strict=all(v['relations']==engine.relations and
                       v['source_evidence_digest']==engine.input_digest for v in actual['views'])
            ok=parity and expected_ok and strict
            passes+=ok;map_count+=actual['view_cost_units'];all_views+=len(engine.manifests)*0+5
            cases.append({'case':label,'selected':selected,'expected':expected,
                          'parity_with_no_map':parity,'source_unchanged':strict,'passed':ok,
                          'rendered_view_cost':actual['view_cost_units']})
    return {'kind':'frozen synthetic development fixtures; not blind task accuracy',
            'cases':cases,'routing_cases_passed':passes,'cases_total':len(CASES),
            'source_only_answer_parity_all':all(x['parity_with_no_map'] for x in cases),
            'all_six_or_zero_source_control':'same classical evidence, no accuracy gain established',
            'selected_total_view_units':map_count,'naive_five_geometric_views_per_case':all_views,
            'abstention_cases':sum(not x['selected'] for x in cases),
            'status':'PASS' if passes==len(CASES) else 'FAIL'}

if __name__=='__main__':
    r=main();print(json.dumps(r,sort_keys=True,indent=2))
    if r['status']!='PASS':raise SystemExit(1)
