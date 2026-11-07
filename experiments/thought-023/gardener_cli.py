"""MOTIF-023 CLI: offline grammar proof or actual opt-in local LLM advice.

No model writes code. No automatic vocabulary promotion or effectful work.
"""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
from grammar import canonical,digest,GrammarError
from gardener_lab import run_offline,evaluate_advice
HERE=Path(__file__).resolve().parent
sibling=str(HERE.parent/'thought-022')
if sibling not in sys.path:sys.path.insert(0,sibling)
from synth import classical_cegis,TASKS
from live_model import MissingPrimitiveAdvisor


def trial_with_model(model):
    baseline=classical_cegis('invert',oracle_budget=4)
    if baseline['status']!='HOLD_GRAMMAR_INADEQUATE':
        return {'status':'HOLD_NO_MISSING_GRAMMAR','model_called':False}
    reply=None;error=None
    try:
        reply=model.advise(TASKS['invert'],baseline['development_witnesses'])
        gardener=evaluate_advice(reply,source='DIRECT_LOCAL_LLM_ADVICE_REVIEW_ONLY')
    except Exception as exc:
        gardener=None;error={'type':type(exc).__name__,'code':str(exc)[:180]}
    receipts=getattr(model,'calls',[])
    actual=any(r.get('transport')=='DIRECT_LOOPBACK_OLLAMA_HTTP' and r.get('http_generation_completed') for r in receipts)
    status=(gardener['stage'] if gardener else 'HOLD_INVALID_OR_UNAVAILABLE_MODEL_ADVICE')
    out={'schema':'motif.thought023.live-grammar-gardener.v1',
         'status':status,'model_directly_called':actual,'model_calls':len(receipts),
         'model_metadata':'DAEMON_SELF_REPORTED_NOT_SIGNED',
         'model_receipts':receipts,'untrusted_model_reply':reply,
         'baseline_oracle_witnesses':baseline['development_witnesses'],
         'gardener':gardener,'error':error,
         'new_grammar_installed':False,'installed':False,'external_authority':'NONE',
         'frozen_task_family_disclosed_to_model':False,
         'note':'Model receives one DEV witness. Gardener measures finite syntax closure; synthetic task, no independent blind external benchmark.'}
    out['receipt_digest']=digest(out)
    return out


def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument('--backend',choices=('offline','ollama'),default='offline')
    p.add_argument('--model')
    p.add_argument('--output',type=Path)
    args=p.parse_args(argv)
    if args.backend=='ollama' and not args.model:p.error('explicit local --model required')
    if args.backend=='offline' and args.model:p.error('model only allowed for live Ollama')
    report=(run_offline() if args.backend=='offline' else
        trial_with_model(MissingPrimitiveAdvisor(args.model,timeout_seconds=180)))
    if args.output:args.output.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n',encoding='utf8')
    compact={'status':report.get('status',report.get('gardener',{}).get('stage')),
             'model_directly_called':report.get('model_directly_called',False),
             'model_calls':report.get('model_calls',0),
             'grammar_installed':False,
             'extension':report.get('gardener',{}).get('advice',{}).get('extension')}
    print(json.dumps(compact,indent=2,sort_keys=True))
    return 0 if args.backend=='offline' or report['model_directly_called'] else 2
if __name__=='__main__':raise SystemExit(main())
