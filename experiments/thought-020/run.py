"""Run control vs critic on an installed local Ollama model; never replay a model answer."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from critic import comparison
from direct_model import DirectLocalLLM, ModelTransportError
DEFAULT_BRIEF=('Investigate transitions when arriving at a node can turn a switch '
 'off as well as on. Propose a mechanism and a discriminating test. '
 'Do not change source code or claim authority.')


def cli(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', required=True)
    parser.add_argument('--rounds',type=int,default=3)
    parser.add_argument('--timeout',type=int,default=120)
    parser.add_argument('--output',type=Path)
    opts = parser.parse_args(argv)
    try:
        if not 1<=opts.rounds<=6:raise ValueError('rounds 1..6 required')
        # No hidden provider fallback: the original source-owned 019 gateway.
        model_factory=lambda:DirectLocalLLM(opts.model, timeout_seconds=opts.timeout)
        result=comparison(model_factory,DEFAULT_BRIEF,max_calls=opts.rounds)
    except (ModelTransportError, ValueError) as exc:
        print(json.dumps({'status':'HOLD_MODEL_UNAVAILABLE_OR_INVALID',
           'error':type(exc).__name__, 'details':str(exc), 'installed':False}))
        return 2
    if opts.output:
        opts.output.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    report={'model':opts.model,'inference_budget_per_arm':opts.rounds,
            'control':{k:result['control'][k] for k in ('status','model_generations','director_dev_probes','semantic_replays_vetoed')},
            'critic':{k:result['critic'][k] for k in ('status','model_generations','director_dev_probes','semantic_replays_vetoed')},
            'installed':False}
    print(json.dumps(report,indent=2,sort_keys=True))
    # Actual generation required in both arms, otherwise do not label as a
    # successful direct-model comparison.
    return 0 if all(result[a]['model_generations']>=1 and
                   len(result[a]['model_receipts'])>=1 for a in ('control','critic')) else 2

if __name__ == '__main__':
    raise SystemExit(cli())
