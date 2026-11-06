"""Preregistered within source but not genuinely blind synthetic toy comparator.

Matched question budget; strict no-map comparator gets the exact same catalog,
plus strong classical world-entropy baseline. No universal intelligence claim.
"""
from __future__ import annotations
from pathlib import Path
from tempfile import TemporaryDirectory
from inquiry import InquiryCycle
from fixtures import make_engine,possible_worlds,fixture_oracle
from human_talk import dialogue
import json


def main():
    cases=[]
    with TemporaryDirectory() as td:
        _,engine,_=make_engine(Path(td)/'source.jsonl')
        worlds=possible_worlds(engine)
        pair=('m:food','m:meal')
        for world in worlds:
            runs={}
            for label,strategy,geometry in [
                ('decision_map','decision',True),
                ('decision_no_map','decision',False),
                ('strong_world_entropy','world',False),
                ('dependency_only','decision',False)]:
                opts={'allowed_lenses':('dependency',)} if label=='dependency_only' else {}
                agent=InquiryCycle(engine,worlds,seed_pair=pair,
                    strategy=strategy,geometry=geometry,**opts)
                result=agent.run(fixture_oracle(world),budget=3)
                runs[label]={'queries':len(result['question_steps']),
                    'decision':result['proposed_decision'],
                    'status':result['conclusion_status'],
                    'views':result['view_count'],
                    'question_ids':[s['question_id'] for s in result['question_steps']],
                    'source_digest':result['source_digest']}
            matched=(runs['decision_map']['decision']==runs['decision_no_map']['decision'] and
                runs['decision_map']['question_ids']==runs['decision_no_map']['question_ids'] and
                runs['decision_map']['source_digest']==runs['decision_no_map']['source_digest'])
            cases.append({'world':world['id'], 'truth_within_fixture':world['decision'],
                          'no_geometry_parity':matched, 'strategies':runs})
        count=lambda mode:sum(c['strategies'][mode]['decision']==c['truth_within_fixture'] for c in cases)
        query_count=lambda mode:sum(c['strategies'][mode]['queries'] for c in cases)
        return {'kind':'16 entirely synthetic, developed-with-policy world fixtures',
            'question_budget_each':3,'trials':len(cases),
            'decision_correct_under_model':{x:count(x) for x in ['decision_map','decision_no_map','strong_world_entropy','dependency_only']},
            'questions_issued':{x:query_count(x) for x in ['decision_map','decision_no_map','strong_world_entropy','dependency_only']},
            'no_geometry_parity_all':all(c['no_geometry_parity'] for c in cases),
            'strict_source_unchanged':len({c['strategies']['decision_map']['source_digest'] for c in cases})==1,
            'cases':cases,'external_authority':'NONE',
            'limitations':'Finely specified hypothetical outcomes: not real independent witnesses, not blind data, and not a demonstrated language model.'}

if __name__=='__main__':
    report=main()
    print(json.dumps(report,indent=2,sort_keys=True))
    if not report['no_geometry_parity_all'] or not report['strict_source_unchanged']:
        raise SystemExit(1)
