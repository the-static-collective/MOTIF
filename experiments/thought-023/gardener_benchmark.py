"""Reproduce source-owned grammar extension evidence without any LLM calls."""
from __future__ import annotations
import json
from pathlib import Path
from gardener_lab import run_offline
from runtime import compile_source

def main(folder=None):
    output=Path(folder) if folder else Path(__file__).resolve().parent
    output.mkdir(parents=True,exist_ok=True)
    data=run_offline()
    g=data['gardener']
    assert g['stage']=='CANDIDATE_GRAMMAR_FOR_HUMAN_REVIEW_NOT_INSTALLED'
    (output/'offline-results.json').write_text(json.dumps(data,sort_keys=True,indent=2)+'\n')
    (output/'candidate_solver.py').write_text(compile_source(
        g['report']['new_invert_expression'],g['advice']['extension']),encoding='utf8')
    return data
if __name__=='__main__':
    x=main()
    print(json.dumps({'stage':x['gardener']['stage'],
        'closure_before':x['gardener']['report']['baseline_grammar_functions'],
        'closure_after':x['gardener']['report']['expanded_grammar_functions'],
        'executable_checks':x['gardener']['executable_audit']['passed'],
        'new_model_calls':0},indent=2))
