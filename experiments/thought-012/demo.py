"""Run full source-grounded rotation over a fictional meal, and draw its trace."""
import json
from tempfile import TemporaryDirectory
from pathlib import Path
from fixtures import make_engine
from cross_lens import CrossLensInquiry,render_svg


def run(output=None):
    with TemporaryDirectory() as td:
        field,engine,relations=make_engine(Path(td)/'source.jsonl')
        before=field.semantic_snapshot()
        solver=CrossLensInquiry(engine)
        report=solver.start(max_steps=3,policy='sequential')
        replay=solver.resume(report,max_steps=3)
        control=solver.evidence_only_full_control()
        assert before==field.semantic_snapshot()
        assert report==replay
        assert {q['id'] for q in report['carried_questions']} == {q['id'] for q in control['carried_questions']}
        svg=render_svg(report)
        result={'experiment':'THOUGHT-012','source_fixture':'fictional community meal',
            'source_digest':report['source_digest'],'same_semantics_after_views':before==field.semantic_snapshot(),
            'visited_lenses':report['visited_lenses'],'original_questions':len(report['initial_inquiries']),
            'carried_open_questions':len(report['carried_questions']),
            'new_question_kinds':sorted({q['kind'] for q in report['carried_questions']}),
            'deterministic_replay':report==replay,
            'source_only_full_control_parity':{q['id'] for q in report['carried_questions']} == {q['id'] for q in control['carried_questions']},
            'pen_unchanged':report['pen_status']=='UNCHANGED',
            'authority':report['effective_external_authority'],
            'limitation':'same authored source, not independent lenses of empirical corroboration'}
        if output is not None:
            output=Path(output);output.mkdir(exist_ok=True,parents=True)
            (output/'cross-lens-inquiry.json').write_text(json.dumps(report,indent=2,sort_keys=True))
            (output/'cross-lens-inquiry.svg').write_text(svg)
            (output/'demo-results.json').write_text(json.dumps(result,indent=2,sort_keys=True))
        return result

if __name__=='__main__':
    import sys
    print(json.dumps(run(Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).parent),indent=2,sort_keys=True))
