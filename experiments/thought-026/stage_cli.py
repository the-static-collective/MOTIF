"""MOTIF-026 staging experiment: offline fixtures or real direct Ollama Qwen."""
from __future__ import annotations
import argparse,json
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
p=str(HERE.parent/'thought-025')
if p not in sys.path:sys.path.insert(0,p)
from specimens import BY_KEY
from abstraction import model_trial as monolithic_trial
from abstraction_llm import DirectAbstractionLLM
from stages import stage_trial,digest
from stage_llm import DirectStageLLM

DEFAULT='food_safe,food_recalled_elsewhere,volunteer_eligible,not_on_shelf,cancel_or_add,vague_access,unknown_beliefs'

def run_selected(tasks,model,*,repair=True):
    results={};
    for task in tasks: results[task.key]=stage_trial(task,model,repair=repair)
    return results

def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument('--backend',choices=('offline','ollama'),default='offline')
    p.add_argument('--model')
    p.add_argument('--tasks',default=DEFAULT)
    p.add_argument('--repair',choices=('yes','no'),default='yes')
    p.add_argument('--compare-monolithic',action='store_true')
    p.add_argument('--output',type=Path)
    opts=p.parse_args(argv)
    if opts.backend=='ollama' and not opts.model:p.error('real run requires explicit --model')
    if opts.backend=='offline' and opts.model:p.error('offline mode does not invoke models')
    keys=opts.tasks.split(',')
    if len(set(keys))!=len(keys) or any(k not in BY_KEY for k in keys):p.error('invalid or duplicated tasks')
    tasks=[BY_KEY[k] for k in keys]
    if opts.backend=='offline':
        from stage_fixtures import DeterministicStages
        model=DeterministicStages()
        # This is explicitly a deterministic fixture, not a generative model.
    else:
        model=DirectStageLLM(opts.model,timeout_seconds=150)
        model.verify_local_model()
    rows=run_selected(tasks,model,repair=opts.repair=='yes')
    mono={};monoreceipts=[]
    if opts.compare_monolithic and opts.backend=='ollama':
        baseline=DirectAbstractionLLM(opts.model,timeout_seconds=150)
        baseline.verify_local_model()
        for task in tasks:mono[task.key]=monolithic_trial(task,baseline,max_calls=2)
        monoreceipts=baseline.calls
    result={'schema':'motif.thought026.staged-experiment.v1',
            'backend':opts.backend,'model':opts.model,'results':rows,
            'model_receipts':model.calls,'direct_llm_calls':len(model.calls) if opts.backend=='ollama' else 0,
            'monolithic_025_comparison':mono,'monolithic_direct_llm_calls':len(monoreceipts),
            'monolithic_model_receipts':monoreceipts,
            'mathematic_language_grounding_verified_on_author_designed_tasks_only':True,
            'partial_stages_preserved_even_on_hold':True,
            'compared_at_equal_model_call_budget':False,
            'model_did_not_select_oracle_or_frozen_cases':True,
            'no_model_written_source_executed':True,
            'installed':False,'pen_unchanged':True,'external_authority':'NONE'}
    result['receipt_digest']=digest(result)
    if opts.output:opts.output.write_text(json.dumps(result,indent=2,ensure_ascii=True,sort_keys=True)+'\n')
    print(json.dumps({'backend':opts.backend,'generations':result['direct_llm_calls'],
      'monolithic_generations':result['monolithic_direct_llm_calls'],
      'staged':{k:{'status':v['status'],'model_calls':v['model_calls'],
           'frozen':v['frozen']['correct'] if v['frozen'] else None,
           'partial':v['partial_understanding_preserved'] if 'partial_understanding_preserved' in v else False} for k,v in rows.items()},
      'monolithic':{k:v['status'] for k,v in mono.items()},'installed':False},indent=2))
    return 0 if opts.backend=='offline' or len(model.calls)>0 else 2

if __name__=='__main__':raise SystemExit(main())
