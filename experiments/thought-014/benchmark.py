"""Run the first MOTIF-as-its-own-developer language/model/strategy comparison."""
from __future__ import annotations
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from devlab import SelfDevelopmentLab, reasoning_policy_trial, evaluate, TinyModelDeveloper
from fixtures import TRAIN, DEV, HELDOUT, SAFETY
import sys
p=Path(__file__).resolve().parent.parent/'thought-013'
if not p.is_dir():p=Path(__file__).resolve().parent.parent/'thought013'
if str(p) not in sys.path:sys.path.append(str(p))
from source013 import make_engine, possible_worlds
from language_space import LanguageSpace
from model_gateway import TinyTextModel


def main():
    with TemporaryDirectory() as td:
        _,engine,_=make_engine(Path(td)/'model-field.jsonl')
        pair=('m:food','m:meal')
        developer=TinyModelDeveloper(TRAIN)
        lab=SelfDevelopmentLab(engine,pair,TRAIN,DEV,HELDOUT,SAFETY)
        lang=lab.run(max_rounds=4,developer=developer)
        policy=reasoning_policy_trial(engine,possible_worlds(engine),pair)
        space=LanguageSpace(engine)
        baseline=space.explore('I wonder whether food and a meal can connect',selected_pair=pair)
        model=space.explore('I wonder whether food and a meal can connect',selected_pair=pair,
                            model=developer.model)
        # The learned classifier is actually consulted, but a model proposal is
        # not a source fact or PEN commitment.
        return {'experiment':'THOUGHT-014','status':'LOCAL_SYNTHETIC_DEVELOPMENT',
                'model_tested_kind':developer.model.model_kind,
                'model_inference_calls':sum(len(x.get('learned_predictions',[])) for x in developer.calls),
                'model_reflection_receipts':len([x for x in developer.calls if x['kind']=='MODEL_RECEIVES_DEV_CRITIQUE']),
                'language_developer':lang,'policy_developer':policy,
                'dialogue_utterances':[baseline,model],
                'local_ollama_called':False,'runtime_model_backend_available':'OPTIONAL_LOCAL_OLLAMA',
                'no_automatic_code_edit':True,'no_pen_promotion':True,
                'external_authority':'NONE',
                'limitations':'Tiny supervised classifier, user-authored synthetic tasks, small holdout; no real LLM or autonomous software engineering benchmark.'}

if __name__=='__main__':
    result=main()
    print(json.dumps(result,sort_keys=True,indent=2))
    if result['language_developer']['status']=='HOLD_AUDIT_REGRESSION':raise SystemExit(1)
