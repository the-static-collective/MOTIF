"""Independent case re-entry: rerun policy and check committed ledger bytes/scores."""
import argparse,json,sys
from pathlib import Path
from field005 import run,compact,DATASETS,AUDIT_SEEDS,POLICIES,digest

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--dataset',choices=DATASETS,required=True)
    parser.add_argument('--seed',type=int,choices=AUDIT_SEEDS,required=True)
    parser.add_argument('--ledger',default=str(Path(__file__).parent/'experiment-results.json'))
    parser.add_argument('--out',default=None)
    args=parser.parse_args()
    saved=json.loads(Path(args.ledger).read_text())
    rows=[]
    for policy in POLICIES:
        r=run(args.dataset,args.seed,policy)
        rows.append(r)
        target=next((x for x in saved['cases'] if x['dataset']==args.dataset
                    and x['seed']==args.seed and x['policy']==policy),None)
        if target is None:raise SystemExit(f'MISSING_CASE {args.dataset}/{args.seed}/{policy}')
        latest=compact([r])['cases'][0]
        if latest != target:
            raise SystemExit(f'MISMATCH_CASE {args.dataset}/{args.seed}/{policy}: '+
                             ', '.join(k for k in latest.keys() if latest.get(k)!=target.get(k)))
        print(f'REPLAY_VERIFIED {args.dataset}/{args.seed}/{policy} frozen={r["proof"]["frozen_sha256"]}')
    if args.out:Path(args.out).write_text(json.dumps({'case':f'{args.dataset}/{args.seed}',
        'proof_packets':[{ 'policy':p,'frozen_sha256':r['proof']['frozen_sha256'],
                 'source_events':r['proof']['events'],
                 'checkpoints':r['proof']['checkpoints']} for p,r in zip(POLICIES,rows)]},indent=2))
