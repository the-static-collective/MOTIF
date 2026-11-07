"""Execute classical-only controls or actual local Qwen proposals under MOTIF.

No replay and no model-to-code. Real model branch requires preinstalled Ollama.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
from specimens import TASKS,BY_KEY
from abstraction import model_trial,classical_without_language,digest
from abstraction_llm import DirectAbstractionLLM

def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument('--backend',choices=('offline','ollama'),default='offline')
    p.add_argument('--model')
    p.add_argument('--tasks',default='food_safe,food_recalled_elsewhere,volunteer_eligible,not_on_shelf,cancel_or_add,vague_access,unknown_beliefs')
    p.add_argument('--max-calls',type=int,default=2)
    p.add_argument('--output',type=Path)
    arg=p.parse_args(argv)
    if arg.backend=='ollama' and not arg.model:p.error('real model requires --model')
    if arg.backend=='offline' and arg.model:p.error('offline does not accept --model')
    if not 1<=arg.max_calls<=2:p.error('model call ceiling is 1..2')
    names=arg.tasks.split(',')
    if any(x not in BY_KEY for x in names) or len(set(names))!=len(names):p.error('invalid or duplicated task IDs')
    selected=[BY_KEY[k] for k in names]
    control={task.key:classical_without_language(task) for task in selected}
    real={};receipts=[];model=None
    if arg.backend=='ollama':
        model=DirectAbstractionLLM(arg.model,timeout_seconds=120)
        model.verify_local_model()
        for task in selected:
            real[task.key]=model_trial(task,model,max_calls=arg.max_calls)
        receipts=list(model.calls)
    out={'schema':'motif.thought025.abstraction-discovery.v1',
         'backend':arg.backend,'model':arg.model,
         'model_called':arg.backend=='ollama' and len(receipts)>0,
         'real_llm_generations':len(receipts),
         'model_receipts':receipts,'model_trials':real,
         'classical_oracle_aided_comparison':control,
         'domain_to_abstract_roles_prebound_for_model':False,
         'known_truth_policy_not_in_public_prompt':True,
         'independent_evaluator_knows_hand_authored_task_policy':True,
         'nonboolean_and_ambiguous_gates_evaluator_owned_not_model_discovery':True,
         'synthetic_author_designed_tasks':True,
         'matched_total_compute_budget':False,
         'no_model_written_source_executed':True,
         'installed':False,'pen_unchanged':True,'external_authority':'NONE'}
    out['receipt_digest']=digest(out)
    if arg.output:arg.output.write_text(json.dumps(out,ensure_ascii=True,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'backend':arg.backend,'direct_llm_calls':len(receipts),
       'model_results':{k:{'status':v['status'],'calls':v['model_calls'],'frozen':v.get('frozen',{}).get('correct') if v.get('frozen') else None} for k,v in real.items()},
       'classical_solved':sum(x['status']=='REVIEW_CLASSICAL_CANDIDATE_NOT_INSTALLED' for x in control.values()),
       'installed':False},indent=2))
    if arg.backend=='ollama' and not receipts:return 2
    return 0

if __name__=='__main__':raise SystemExit(main())
