"""Resume-safe, single-case independent audit; never adjust the policy mid-audit."""
import subprocess,os,sys,json, argparse
from pathlib import Path
from field005 import DATASETS,AUDIT_SEEDS,POLICIES,compact
HERE=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--output-dir',required=True);args=p.parse_args()
base=Path(args.output_dir);base.mkdir(parents=True,exist_ok=True)
for dataset in DATASETS:
 for seed in AUDIT_SEEDS:
  for policy in POLICIES:
   out=base/(f'{dataset}_{seed}_{policy}.json')
   if not out.exists():
    env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',NUMEXPR_NUM_THREADS='1')
    c=[sys.executable,str(HERE/'field005.py'),'--dataset',dataset,'--seed',str(seed),'--policy',policy]
    r=subprocess.run(c,text=True,capture_output=True,env=env,timeout=80,check=True)
    obj=json.loads(r.stdout)
    out.write_text(json.dumps(obj,sort_keys=True))
   else:obj=json.loads(out.read_text())
   print(f'{dataset}/{seed}/{policy}: {obj["test"]["raw"]["correct"]}/{obj["test"]["raw"]["total"]} raw, {obj["test"]["relational"]["correct"]}/{obj["test"]["relational"]["total"]} rel',flush=True)
rows=[json.loads((base/f'{dataset}_{seed}_{policy}.json').read_text()) for dataset in DATASETS for seed in AUDIT_SEEDS for policy in POLICIES]
ledger=compact(rows);ledger['cohort_scored']='audit'
(Path(__file__).parent/'experiment-results.json').write_text(json.dumps(ledger,sort_keys=True,indent=2)+'\n')
print('AUDIT_COMPLETE',len(rows), 'cases',flush=True)
