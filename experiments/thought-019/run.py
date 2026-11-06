"""CLI: run actual local LLM under MOTIF director; no silent fallback/replay."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from direct_model import DirectLocalLLM,ModelTransportError,run_direct,digest

DEFAULT_BRIEF=('Investigate transitions when arriving at a node can turn a switch '
 'off as well as on. Propose a mechanism and a discriminating test. '
 'Do not change source code or claim authority.')

def cli(argv=None):
    p=argparse.ArgumentParser(description='MOTIF 019: actual local LLM calls, no replay or mock fallback')
    p.add_argument('--model',required=True,help='preinstalled Ollama model tag')
    p.add_argument('--rounds',type=int,default=3)
    p.add_argument('--timeout',type=int,default=90)
    p.add_argument('--output',type=Path)
    p.add_argument('--allow-held-reply',action='store_true',help='do not fail CI if a real model was called but proposal was unfit')
    p.add_argument('--brief',default=DEFAULT_BRIEF)
    args=p.parse_args(argv)
    if not 1<=args.rounds<=6:p.error('rounds must be 1..6')
    try:
        report=run_direct(args.model,args.brief,rounds=args.rounds,timeout=args.timeout)
    except (ModelTransportError,ValueError) as ex:
        print(json.dumps({'schema':'motif.thought019.run-hold.v1','status':'HOLD_NO_DIRECT_LLM_INFERENCE',
          'error_type':type(ex).__name__,'reason':str(ex),
          'motif_directly_called_llm':False,'installed':False,'external_authority':'NONE'},indent=2))
        return 2
    if args.output:
        # Refuse paths outside an operator-selected location? The local CLI
        # itself is operator-run; only typed JSON and no model-origin path.
        args.output.write_text(json.dumps(report,indent=2,sort_keys=True,ensure_ascii=True)+'\n',encoding='utf-8')
    summary={'status':report['status'],
      'motif_directly_called_llm':report['motif_directly_called_llm'],
      'local_model_calls':len(report['model_calls']),
      'developer_probes':report['director_report']['dev_probe_count'],
      'selected_mechanism':report['director_report']['selected_mechanism'],
      'model_tag':report['model_tag'],
      'model_reported_digest':report['model_fingerprint']['daemon_advertised_sha256'],
      'audit':report['director_report']['frozen_graph_audit'],
      'no_install':not report['installed']}
    print(json.dumps(summary,indent=2,sort_keys=True))
    if not report['motif_directly_called_llm']:return 2
    if not args.allow_held_reply and report['status']!='PATCH_FOR_HUMAN_REVIEW_NOT_INSTALLED':return 1
    return 0

if __name__=='__main__':raise SystemExit(cli())
