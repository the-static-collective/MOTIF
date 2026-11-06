"""Optional view-only illustration of an actually selected set of maps."""
from pathlib import Path
from tempfile import TemporaryDirectory
from fixtures import make_engine
from router import Task, ViewRouter
from render import render_board


def main(output):
    with TemporaryDirectory() as t:
        engine=make_engine(Path(t)/'source.jsonl')
        result=ViewRouter(engine).run(Task(('association','dependency','tension','affordance'),
                   anchor='m:volunteers',max_views=3))
        doc=render_board({'external_authority':'NONE','views':result['views']},
                         engine._original, title='MOTIF | Selected Thought Lenses')
        Path(output).write_text(doc,encoding='utf-8')
        return {'selected':result['selected_lenses'],'output':str(output)}
if __name__=='__main__':
    import json,sys
    print(json.dumps(main(Path(__file__).with_name('selected-thought-lenses.svg')
                          if len(sys.argv)==1 else Path(sys.argv[1])),indent=2))
