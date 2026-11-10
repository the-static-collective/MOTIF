"""Execute FIELD-005 source-owning cases in fresh Python processes.

Usage: python benchmark.py --cohort development|audit|all --output file.json
Each process executes its entire frozen query trajectory BEFORE test scoring.
"""
import argparse,sys,json,subprocess,concurrent.futures,os
from pathlib import Path
from field005 import DATASETS,DEVELOPMENT_SEEDS,AUDIT_SEEDS,POLICIES,compact,digest
HERE=Path(__file__).resolve().parent

def get_case(case):
    d,s,p=case
    cmd=[sys.executable,str(HERE/'field005.py'),'--dataset',d,'--seed',str(s),'--policy',p]
    env=dict(os.environ, OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', NUMEXPR_NUM_THREADS='1')
    result=subprocess.run(cmd,capture_output=True,text=True,timeout=90,check=True,env=env)
    return case,json.loads(result.stdout)

def benchmark(cohort,workers=3):
    seeds=DEVELOPMENT_SEEDS if cohort=='development' else AUDIT_SEEDS if cohort=='audit' else (*DEVELOPMENT_SEEDS,*AUDIT_SEEDS)
    tasks=[(d,s,p) for d in DATASETS for s in seeds for p in POLICIES]
    answers={}
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex:
        for case,result in ex.map(get_case,tasks):
            answers[case]=result
            print(f'{case}: heldout {result["test"]["raw"]["correct"]}/{result["test"]["raw"]["total"]} raw, {result["test"]["relational"]["correct"]}/{result["test"]["relational"]["total"]} relational',flush=True)
    return [answers[t] for t in tasks]

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--cohort',choices=('development','audit','all'),required=True)
    parser.add_argument('--output',required=True);parser.add_argument('--workers',type=int,default=3)
    args=parser.parse_args()
    data=compact(benchmark(args.cohort,args.workers))
    data['cohort_scored']=args.cohort
    Path(args.output).write_text(json.dumps(data,sort_keys=True,indent=2)+'\n')
