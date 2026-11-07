"""Reproduce 024 offline or invoke a real local Ollama language model.

No silent replay, no model-supplied Python, no automated installation.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
from tasks import TASKS,BY_KEY
from transfer import offline_report,model_trial
from transfer_llm import DirectTransferLLM

def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument('--backend',choices=('offline','ollama'),default='offline')
    p.add_argument('--model')
    p.add_argument('--tasks',default='permits_reverse,missing_supplies,not_endorsed,expire_names,cross_category_threshold,open_world_truth')
    p.add_argument('--rounds',type=int,default=2)
    p.add_argument('--output',type=Path)
    args=p.parse_args(argv)
    if args.backend=='ollama' and not args.model:p.error('ollama requires --model')
    if args.backend=='offline' and args.model:p.error('--model requires ollama backend')
    if type(args.rounds) is not int or not 1<=args.rounds<=3:p.error('1..3 rounds')
    keys=args.tasks.split(',')
    if not keys or len(set(keys))!=len(keys) or any(k not in BY_KEY for k in keys):p.error('unknown or duplicate tasks')
    selected=[BY_KEY[k] for k in keys]
    base=offline_report(selected)
    if args.backend=='offline':
        out=base
    else:
        model=DirectTransferLLM(args.model,timeout_seconds=160)
        observed={}
        for t in selected:
            start=len(model.calls)
            observed[t.key]=model_trial(t,model,max_calls=args.rounds)
            observed[t.key]['real_http_inference_receipts']=model.calls[start:]
        out={'schema':'motif.thought024.direct-llm-transfer.v1',
             'offline':base,'model':args.model,
             'model_calls':len(model.calls),'real_direct_llm_http_calls':sum(x['http_generation_completed'] for x in model.calls),
             'llm_trials':observed,'model_receipts':model.calls,
             'frozen_oracle_disclosed_to_model':False,
             'model_wrote_python':False,'source_or_grammar_installed':False,
             'installed':False,'external_authority':'NONE',
             'note':'Domain-to-set role mapping predefined by developer. Familiar synthetic Boolean descriptions only; not independent blind transfer or real-world understanding.'}
    if args.output:args.output.write_text(json.dumps(out,ensure_ascii=True,sort_keys=True,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'status':out.get('status','DIRECT_MODEL_EVALUATION_COMPLETED'),
                      'model_calls':out.get('model_calls',0),
                      'tasks':keys,
                      'classical_review':sum(r['expanded']['status']=='REVIEW_CANDIDATE_NOT_INSTALLED' for r in base['results']),
                      'model_review':sum(v['status']=='CANDIDATE_FOR_REVIEW_NOT_INSTALLED' for v in out.get('llm_trials',{}).values()),
                      'installed':False},indent=2))
    return 0 if args.backend=='offline' or out['real_direct_llm_http_calls']>0 else 2
if __name__=='__main__':raise SystemExit(main())
