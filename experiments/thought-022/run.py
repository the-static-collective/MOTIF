"""Operator-selected THOUGHT-022 comparison. No replay or model fallback."""
import argparse,json
from pathlib import Path
from race import llm_cegis,hybrid_cegis,offline_matrix
from live_model import GeneralTaskModel,MissingPrimitiveAdvisor
from synth import TASKS


def main(argv=None):
    p=argparse.ArgumentParser(description='THOUGHT-022 finite grammar / real LLM / hybrid race')
    p.add_argument('--model',help='Explicit already-installed local Ollama model (required for live arm)')
    p.add_argument('--tasks',nargs='+',choices=tuple(TASKS),default=['intersection','flip','invert'])
    p.add_argument('--oracle-budget',type=int,default=2)
    p.add_argument('--model-budget',type=int,default=3)
    p.add_argument('--timeout',type=int,default=150)
    p.add_argument('--output',type=Path)
    args=p.parse_args(argv)
    if not 1<=args.oracle_budget<=8 or not 1<=args.model_budget<=6:p.error('budgets outside bounds')
    base=offline_matrix(tuple(args.tasks),args.oracle_budget)
    results={}
    live_count=0
    for task in args.tasks:
        entry={'classical':next(x for x in base['classical'] if x['task']==task)}
        if args.model:
            model=GeneralTaskModel(args.model,timeout_seconds=args.timeout)
            llm=llm_cegis(task,model,oracle_budget=args.oracle_budget,model_budget=args.model_budget)
            entry['llm']=llm
            live_count+=sum(x.get('http_generation_completed') is True for x in llm['model_receipts'])
            advisor=(MissingPrimitiveAdvisor(args.model,timeout_seconds=args.timeout)
                     if task=='invert' else None)
            hybrid=hybrid_cegis(task,advisor,oracle_budget=args.oracle_budget)
            entry['hybrid']=hybrid
            live_count+=sum(x.get('http_generation_completed') is True for x in hybrid['model_receipts'])
        else:
            entry['hybrid']=hybrid_cegis(task,None,oracle_budget=args.oracle_budget)
        results[task]=entry
    status='RESEARCH_COMPARISON_ONLY' if (not args.model or live_count>0) else 'HOLD_NO_DIRECT_LLM_INFERENCE'
    output={'schema':'motif.thought022.comparison.v1','status':status,
       'model_tag_requested':args.model,'real_llm_generations':live_count,
       'max_model_generations_per_task':args.model_budget,
       'max_oracle_probes_per_arm':args.oracle_budget,
       'same_oracle_budget_not_same_cpu_or_token_budget':True,
       'source_owned_tests_not_independent_external_blind_benchmark':True,
       'grammar_distinct_functions':base['grammar_distinct_functions'],
       'tasks':results,'installed':False,'pen_status':'UNCHANGED',
       'external_authority':'NONE'}
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(output,sort_keys=True,indent=2,ensure_ascii=True)+'\n',encoding='utf-8')
    print(json.dumps({'status':status,'model':args.model,'real_llm_generations':live_count,
          'tasks':{t:{a:{'status':v['status'],
                   'oracle_calls':v.get('oracle_calls',v.get('independent_oracle_calls')),
                   'model_calls':v.get('model_call_count',len(v.get('model_receipts',[])))}
                            for a,v in group.items()} for t,group in results.items()}},indent=2))
    return 0 if status=='RESEARCH_COMPARISON_ONLY' else 2

if __name__=='__main__':raise SystemExit(main())
