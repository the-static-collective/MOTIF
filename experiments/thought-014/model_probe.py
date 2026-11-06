"""Explicit local tool: MOTIF invokes its bounded language model and/or dev tests.

Offline demo runs a tiny actually-trained Naive Bayes model. Local Ollama only
when explicitly selected and running on localhost. No source code is changed.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
from tempfile import TemporaryDirectory
from model_gateway import OllamaLocalModel,TinyTextModel
from language_space import LanguageSpace
from devlab import SelfDevelopmentLab,OllamaDeveloper
from fixtures import TRAIN,DEV,HELDOUT,SAFETY
from source013 import make_engine


def main(argv=None):
    parser=argparse.ArgumentParser(description='MOTIF local model tester; output proposals only')
    parser.add_argument('--backend',choices=('tiny','ollama'),default='tiny')
    parser.add_argument('--model',help='required if --backend ollama: existing Ollama-local model identifier')
    parser.add_argument('--utterance',default='I wonder whether food and the meal could connect')
    parser.add_argument('--dev-test',action='store_true',help='propose and test bounded alias candidates')
    args=parser.parse_args(argv)
    if args.backend=='ollama' and not args.model:parser.error('--model required for ollama')
    if args.backend=='tiny' and args.model:parser.error('--model is only for ollama')
    with TemporaryDirectory() as d:
        _,engine,_=make_engine(Path(d)/'field.jsonl')
        pair=('m:food','m:meal')
        model=TinyTextModel(TRAIN) if args.backend=='tiny' else OllamaLocalModel(args.model)
        turn=LanguageSpace(engine).explore(args.utterance,selected_pair=pair,model=model)
        out={'mode':'MOTIF_RUNS_MODEL_AS_PROPOSER', 'model_kind':model.model_kind,
             'utterance':turn,'external_authority':'NONE','pen_state':'UNCHANGED'}
        if args.dev_test:
            developer=None if args.backend=='tiny' else OllamaDeveloper(model,TRAIN)
            out['self_development']=SelfDevelopmentLab(engine,pair,TRAIN,DEV,HELDOUT,SAFETY).run(
                max_rounds=4,developer=developer)
        return out

if __name__=='__main__':print(json.dumps(main(),sort_keys=True,indent=2))
