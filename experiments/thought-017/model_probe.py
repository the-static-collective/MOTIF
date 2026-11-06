"""Explicit model experiment: GPT-6 conversation proposal or opt-in installed Ollama.

No model-selected URL, code execution, source mutation or auto-install.
"""
import argparse,json
from benchmark import main
from program import CHAT_MODEL_PROPOSAL,ProposalError
from model_gateway import OllamaMacroProposer,ModelUnavailable

def run(argv=None):
    parser=argparse.ArgumentParser()
    parser.add_argument('--backend',choices=('replay','ollama'),default='replay')
    parser.add_argument('--model',default=None)
    parser.add_argument('--output',default=None)
    opt=parser.parse_args(argv)
    if opt.backend=='ollama':
        if opt.model is None:raise SystemExit('HOLD: explicit local --model required')
        try:proposal=OllamaMacroProposer(opt.model).propose()
        except (ModelUnavailable,ProposalError) as exc:
            print(json.dumps({'status':'HOLD_NO_VALID_MODEL_PROPOSAL','reason':str(exc),
              'model_called':True,'no_source_executed':True,'installed':False},indent=2))
            raise SystemExit(2)
    else:
        if opt.model:raise SystemExit('HOLD: --model only allowed with --backend ollama')
        proposal=CHAT_MODEL_PROPOSAL
    result=main(opt.output,candidate=proposal)
    print(json.dumps({'real_local_ollama_called':opt.backend=='ollama',
      **{k:result[k] for k in
        ('status','model_proposer','truth_table','development','frozen_audit','stress','installed')}},indent=2))
    if result['status']!='PATCH_FOR_HUMAN_REVIEW_NOT_INSTALLED':raise SystemExit(1)

if __name__=='__main__':run()
