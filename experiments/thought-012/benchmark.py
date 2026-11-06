"""Fixed synthetic development bench: independent lenses as inspections, not witnesses."""
from __future__ import annotations
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from fixtures import make_engine
from cross_lens import CrossLensInquiry


def run():
    results=[]
    with TemporaryDirectory() as td:
        for variant in ('complete','no_tension','no_requirements','no_affordances','no_bridge','hypothesis_only'):
            _field, engine, _relations=make_engine(Path(td)/(variant+'.jsonl'),variant)
            solver=CrossLensInquiry(engine)
            full=solver.start(max_steps=3,allow_geometry=True)
            control=solver.evidence_only_full_control()
            single=solver.start(max_steps=0)
            extracted=[q['id'] for q in full['carried_questions']]
            no_map=[q['id'] for q in control['carried_questions']]
            parity=(set(extracted)==set(no_map))
            # Compare equal evidence questions, NOT cognitive accuracy.
            ok=parity and full['effective_external_authority']=='NONE' and \
                (not full['initial_inquiries'] or full['view_cost_units']==3)
            results.append({'fixture':variant,'passed':ok,
                  'full_inspections':full['lens_inspection_count'],
                  'single_question_count':len(single['carried_questions']),
                  'cross_lens_question_count':len(full['carried_questions']),
                  'source_only_control_count':len(control['carried_questions']),
                  'source_only_question_parity':parity,
                  'no_pen_or_action':full['assertion_promotion']=='NONE'})
    return {'experiment':'THOUGHT-012', 'suite':'synthetic development (not blind)',
      'case_count':len(results),'passed':sum(r['passed'] for r in results),
      'results':results,
      'interpretation':'Cross-lens may expose more questions than association-only, but exhaustive no-map source inspection provides the same results. No measured reasoning accuracy gain.',
      'status':'PASS' if all(r['passed'] for r in results) else 'FAIL'}

if __name__=='__main__':
    r=run();print(json.dumps(r,indent=2,sort_keys=True))
    if r['status']!='PASS':raise SystemExit(1)
