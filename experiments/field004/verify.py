"""Verify immutable FIELD-004 case receipts individually, sharded for CI."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import field004 as m

HERE=Path(__file__).parent
ALGOS=('original_cart_depth3','matched_raw_classical_cv','composed_relation_cv','selected_estimator_raw_ablation')

def check_summary(data):
    assert data['schema']==m.SCHEMA
    assert tuple(data['dev_seeds'])==m.DEV_SEEDS
    assert tuple(data['audit_seeds'])==m.AUDIT_SEEDS
    assert tuple(data['modes'])==m.MODES
    assert len(data['cases'])==len(m.SEEDS)*len(m.DATASETS)*len(m.MODES)
    assert len({(r['dataset'],r['seed'],r['mode']) for r in data['cases']})==len(data['cases'])
    for r in data['cases']:
        assert r['label_queries']==m.previous.BUDGETS[r['dataset']]
        assert r['source_sha256']==m.previous.DATASETS[r['dataset']]['sha256']
        assert r['cohort']==('preexisting_exploratory' if r['seed'] in m.DEV_SEEDS else 'new_seed_frozen_audit')
    for cohort,seeds in (('exploratory',m.DEV_SEEDS),('audit_frozen',m.AUDIT_SEEDS),('all',m.SEEDS)):
        for dataset in m.DATASETS:
            for mode in m.MODES:
                rows=[r for r in data['cases'] if r['dataset']==dataset and r['mode']==mode and r['seed'] in seeds]
                scores=data['summary'][cohort][dataset][mode]['scores']
                for alg in ALGOS:
                    assert scores[alg]=={
                      'correct':sum(r['test_scores'][alg]['correct'] for r in rows),
                      'total':sum(r['test_scores'][alg]['total'] for r in rows)}
    return True


def case_locus(full):
    row=m.compact_report({'cases':[full]})['cases'][0]
    return row


def verify_shard(dataset,mode,data):
    selected=[r for r in data['cases'] if r['dataset']==dataset and r['mode']==mode]
    assert len(selected)==len(m.SEEDS)
    output=[]
    for pinned in selected:
        computed=case_locus(m.run(dataset,pinned['seed'],mode))
        assert computed==pinned, 'FULL_REENTRY_MISMATCH '+str((dataset,mode,pinned['seed']))
        output.append({'record':pinned,'reentry_status':'PASS','proof_sha256':pinned['frozen_sha256']})
        print('PASS',dataset,mode,pinned['seed'],pinned['frozen_sha256'][:16],flush=True)
    return output

if __name__=='__main__':
    a=argparse.ArgumentParser()
    a.add_argument('--dataset',choices=m.DATASETS)
    a.add_argument('--mode',choices=m.MODES)
    a.add_argument('--out',default='')
    args=a.parse_args()
    obj=json.loads((HERE/'experiment-results.json').read_text())
    check_summary(obj)
    if args.dataset or args.mode:
        if not (args.dataset and args.mode):a.error('--dataset and --mode both required')
        receipts=verify_shard(args.dataset,args.mode,obj)
        if args.out:Path(args.out).write_text(json.dumps(receipts,indent=2,sort_keys=True)+'\n')
    print('FIELD-004 verification PASS')
