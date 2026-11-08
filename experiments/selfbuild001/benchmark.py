"""Fixed finite rubric comparing the generated seed to a constant questioner.

The baseline is intentionally weak. This is a functional smoke test, NOT an
accuracy claim about autonomous software construction or natural language.
"""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from test_selfbuild import fixture
from selfbuild import INTERFACES, scan, stage_seed, test_seed


def benchmark():
    with TemporaryDirectory() as t:
        root=fixture(Path(t)/'synthetic-repo')
        staging=Path(t)/'generated'
        orientation=scan(root)
        artifact=stage_seed(orientation,staging)
        checked=test_seed(orientation,staging,artifact)
        if not checked['tests_passed']:
            raise AssertionError('generated cartridge contract failure')
        import subprocess,sys
        names=[comp for comp,_,_ in INTERFACES]
        fixtures=[names,names[:-1],[],['unrecognized',*names]]
        expected=('COUNT_VERIFIED_NAMES','COUNT_MISSING','COUNT_MISSING','COUNT_VERIFIED_NAMES')
        scores=[]
        for present,want in zip(fixtures,expected):
            out=subprocess.run([sys.executable,'-I','-B',str(staging/'motif_seed.py'),json.dumps(present)],
                                capture_output=True,text=True,timeout=8,check=True)
            got=json.loads(out.stdout)['action_executed']
            scores.append(int(got==want))
        weak_baseline=sum(int('COUNT_MISSING'==wanted) for wanted in expected)
        return {'experiment':'SELF-BUILD-001',
                'scope':'four declared synthetic interface-list cases; weak constant baseline',
                'questions_evaluated':len(fixtures),
                'static_always_ask_missing_correct':weak_baseline,
                'generated_child_correct':sum(scores),
                'generated_child_verified':checked['tests_passed'],
                'external_actions':0,'autonomous_code_invention':False,
                'real_repo_integration_not_tested_here':True}


if __name__=='__main__':
    print(json.dumps(benchmark(), indent=2,sort_keys=True))
