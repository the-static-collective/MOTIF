"""Replay one exact source-domain trial, including source authenticity simulation."""
import argparse
import json
from pathlib import Path
from field007 import TASKS,SEEDS,POLICIES,run,seal
from compact import compact_packet

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--task',required=True,choices=TASKS)
 p.add_argument('--seed',required=True,type=int,choices=SEEDS)
 p.add_argument('--policy',required=True,choices=POLICIES)
 p.add_argument('--ledger',default=str(Path(__file__).parent/'experiment-results.json'))
 args=p.parse_args()
 ledger=json.loads(Path(args.ledger).read_text())
 if ledger['sha256']!=seal({k:v for k,v in ledger.items() if k!='sha256'}):
  raise SystemExit('CORRUPT_EVIDENCE_LEDGER')
 stored=next(x for x in ledger['cases'] if (x['source'],x['seed'],x['policy'])==(args.task,args.seed,args.policy))
 current=compact_packet(run(args.task,args.seed,args.policy))
 if stored!=current:raise SystemExit('REENTRY_MISMATCH')
 print('FIELD007_REENTRY_OK',args.task,args.seed,args.policy,stored['packet_sha256'])
