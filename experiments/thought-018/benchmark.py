"""Reproduce an actual model->director->independent oracle->trusted runtime cycle."""
from __future__ import annotations
import json
from pathlib import Path
from director import ResearchDirector,compare_controls
from research_model import TinyResearchModel

BRIEF='What if toggles make previously held keys vanish after another visit?'

def main():
    model=TinyResearchModel()
    experiment,_=ResearchDirector(BRIEF,target='FLIP',model=model,max_rounds=5).run()
    return {'experiment':'THOUGHT-018','trial':experiment,'finite_policy_controls':compare_controls(),
      'model_invocations':model.calls,'known_limits':
      'Offline supervised NB ranker, not a real generative LLM. Typed candidates from finite human-reviewed DSL. Audit artificial and frozen only against model feedback.'}

if __name__=='__main__':
    report=main()
    print(json.dumps(report,indent=2,sort_keys=True))
    if report['trial']['status']!='PATCH_FOR_HUMAN_REVIEW_NOT_INSTALLED':raise SystemExit(1)
