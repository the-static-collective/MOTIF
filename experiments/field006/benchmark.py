"""Reproduce archived FIELD-006 audit rows against source-owned original labels."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from field006 import batch, SEEDS_AUDIT, POLICIES, DATASETS

HERE=Path(__file__).resolve().parent


def verify_group(dataset):
    recorded=json.loads((HERE/'experiment-results.json').read_text())
    if dataset not in DATASETS or recorded['seeds']!=list(SEEDS_AUDIT) or recorded['policies']!=list(POLICIES):
        raise ValueError('audit definition mismatch')
    observed=batch(datasets=(dataset,),seeds=SEEDS_AUDIT,budget=40)
    expected=[r for r in recorded['results'] if r['dataset']==dataset]
    actual=observed['results']
    key=lambda r:(r['dataset'],r['seed'],r['policy'])
    if sorted(expected,key=key)!=sorted(actual,key=key):
        # Report a precise reproducibility failure; never silently accept drift.
        for earlier,later in zip(sorted(expected,key=key),sorted(actual,key=key)):
            if earlier!=later:
                mismatched={field:{'expected':earlier.get(field),'replayed':later.get(field)}
                            for field in sorted(set(earlier)|set(later)) if earlier.get(field)!=later.get(field)}
                print(json.dumps({'status':'FAILED_REENTRY','dataset':dataset,
                    'seed':earlier['seed'],'policy':earlier['policy'],
                    'differences':mismatched},sort_keys=True),flush=True)
        raise ValueError('source query reentry or test score mismatch')
    if observed['summary'][dataset]!=recorded['summary'][dataset]:
        raise ValueError('audit summary mismatch')
    return {'result':'EXACT_SOURCE_REENTRY_MATCH','dataset':dataset,
            'cases':len(actual),'label_budget':40,
            'source_row_receipt_verified_each_query':True,
            'summary':observed['summary'][dataset]}

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--dataset',required=True,choices=DATASETS)
    p.add_argument('--out',type=Path)
    a=p.parse_args()
    result=verify_group(a.dataset)
    if a.out:a.out.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print(json.dumps(result,sort_keys=True))
