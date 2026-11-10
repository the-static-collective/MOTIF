"""Reproduce a frozen local FIELD-006 case by rerunning original source adapter."""
import argparse
import json
from pathlib import Path
import field006 as experiment
from lineage import seal


def verify(case, raw):
    if case['proof']['sha256']!=seal({k:v for k,v in case['proof'].items() if k!='sha256'}):
        raise ValueError('changed proof contents')
    return case==raw


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--dataset',required=True,choices=experiment.DATASETS)
    p.add_argument('--seed',required=True,type=int)
    p.add_argument('--policy',required=True,choices=experiment.POLICIES)
    p.add_argument('--budget',type=int,default=40,choices=experiment.CHECKPOINTS)
    p.add_argument('--against',type=Path)
    p.add_argument('--save',type=Path)
    a=p.parse_args()
    run=experiment.run(a.dataset,a.seed,a.policy,a.budget)
    if a.against:
        prior=json.loads(a.against.read_text())
        if not verify(prior,run):raise SystemExit('FAIL: source or research result drift')
    if a.save:a.save.write_text(json.dumps(run,sort_keys=True,indent=2)+'\n')
    print(json.dumps({'status':'REPRODUCED','dataset':a.dataset,'seed':a.seed,
                      'policy':a.policy,'budget':a.budget,
                      'proof_sha256':run['proof']['sha256'],'test':run['test']},sort_keys=True))
