"""Execute the predeclared frozen FIELD-007 source-domain transfer trial.

No parameter selection from test labels. Every case is retained, including loss.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from field007 import TASKS,SEEDS,POLICIES,run,summarize,SCHEMA,seal


def benchmark():
 packets=[]
 for source in TASKS:
  for seed in SEEDS:
   for policy in POLICIES:
    packet=run(source,seed,policy)
    packets.append(packet)
    print(f'{source} {seed} {policy}: {packet["snapshots"][-1]["models"]["raw_rbf"]["balanced_accuracy"]}',flush=True)
 summary,verdict=summarize(packets)
 result={'schema':SCHEMA,'predeclared_seeds':SEEDS,'predeclared_policies':POLICIES,
   'ordered_cases':packets,'summary':summary,'primary_verdict':verdict,
   'limitations':['Public historical UCI copies, not prospective owner-blinded evaluation',
     'Repeated holdout splits overlap original specimens',
     'Reference-model fits are not compute-matched between classical and relational committees',
     'No live patient classification, laboratory observations, actions or scientific laws']}
 result['sha256']=seal(result)
 return result

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--out',default=str(Path(__file__).parent/'experiment-results-full-local.json'))
 args=ap.parse_args()
 r=benchmark()
 Path(args.out).write_text(json.dumps(r,indent=2,sort_keys=True)+'\n')
 print(json.dumps({'primary_verdict':r['primary_verdict'],'sha256':r['sha256']},indent=2))
