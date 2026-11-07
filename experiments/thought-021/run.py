"""Opt-in live local-model experiment: control vs refutation critic vs CEGIS ledger.

Only the source-owner DirectLocalLLM may contact fixed local Ollama. The LLM
cannot choose endpoints, tests, grading, code execution, installation or writes.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from constraints import comparison
from direct_model import DirectLocalLLM, ModelTransportError

DEFAULT_BRIEF=('Investigate transitions when arriving at a node can turn a switch '
               'off as well as on. Propose a mechanism and a discriminating test. '
               'Do not change source code or claim authority.')

def cli(argv=None):
    parser=argparse.ArgumentParser(description='THOUGHT-021 real local LLM constraints trial')
    parser.add_argument('--model',required=True,help='operator-selected already installed Ollama model')
    parser.add_argument('--rounds',type=int,default=4)
    parser.add_argument('--timeout',type=int,default=120)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args(argv)
    if not 1 <= args.rounds <= 6:parser.error('rounds must be 1..6')
    try:
        output=comparison(lambda:DirectLocalLLM(args.model,timeout_seconds=args.timeout),
                          DEFAULT_BRIEF,max_calls=args.rounds)
    except (ModelTransportError,ValueError) as exc:
        print(json.dumps({'status':'HOLD_MODEL_ERROR','error_type':type(exc).__name__,
          'installed':False,'external_authority':'NONE'}))
        return 2
    if args.output:
        args.output.write_text(json.dumps(output,sort_keys=True,indent=2,ensure_ascii=True)+'\n')
    summary={'model_requested':args.model,'max_calls_per_arm':args.rounds,
      'installed':False,'arms':{}}
    for name,arm in output['runs'].items():
        receipts=arm['model_receipts']
        summary['arms'][name]={
          'status':arm['status'],
          'actual_completed_http_generations':sum(x.get('http_generation_completed') is True for x in receipts),
          'valid_model_candidates':arm['model_generations'],
          'director_development_probes':arm['director_dev_probes'],
          'constraint_veto_count':arm['constraint_veto_count'],
          'semantic_veto_count':arm['semantic_veto_count'],
          'tokens_generated':sum(x.get('eval_count') or 0 for x in receipts),
          'selected_mechanism':arm['selected_mechanism'],
          'audit':arm['director_report']['frozen_graph_audit']}
    print(json.dumps(summary,indent=2,sort_keys=True))
    # A meaningful comparison requires at least one genuine completed inference
    # in every arm. No synthetic fallback, and HOLD is an acceptable result.
    if not all(any(x.get('http_generation_completed') is True and
                       x.get('transport')=='DIRECT_LOOPBACK_OLLAMA_HTTP'
                       for x in arm['model_receipts']) for arm in output['runs'].values()):
        return 2
    return 0

if __name__=='__main__':raise SystemExit(cli())
