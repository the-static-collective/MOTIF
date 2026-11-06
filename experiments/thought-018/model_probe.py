"""Opt-in operator CLI to run local Ollama as research proposer; no auto install."""
import argparse,json
from benchmark import BRIEF
from director import ResearchDirector
from research_model import OllamaResearchModel,TinyResearchModel

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--backend',choices=('tiny','ollama'),default='tiny')
    p.add_argument('--model')
    p.add_argument('--brief',default=BRIEF)
    p.add_argument('--rounds',type=int,default=5)
    args=p.parse_args()
    if args.backend=='ollama' and not args.model:p.error('explicit --model is required for ollama')
    if args.backend=='tiny' and args.model:p.error('--model is only valid with ollama')
    model=OllamaResearchModel(args.model) if args.backend=='ollama' else TinyResearchModel()
    result,_=ResearchDirector(args.brief,model=model,max_rounds=args.rounds).run()
    print(json.dumps(result,indent=2,sort_keys=True))
    if result['status']!='PATCH_FOR_HUMAN_REVIEW_NOT_INSTALLED':raise SystemExit(2)

if __name__=='__main__':main()
