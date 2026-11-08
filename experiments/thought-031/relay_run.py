"""THOUGHT-031: real Ollama or explicit scripted fixtures, no silent substitutions."""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
for d in ('thought-025','thought-029','thought-030'):
    p=str(HERE.parent/d)
    if p not in sys.path:sys.path.insert(0,p)
from specimens import BY_KEY
from artifact_portal import ArtifactPortal
from relay_llm import DirectRelayLLM
from relay_session import trial

class ScriptedFixture:
    kind='SCRIPTED_TEST_FIXTURE_NOT_A_REAL_LLM'
    def __init__(self,task,*,pidgin=False,wrong=False):
        self.task=task;self.pidgin=pidgin;self.wrong=wrong;self.calls=[]
    def research(self,task,evidence,history,lexicon,pidgin):
        self.calls.append({'source':'SCRIPTED_FIXTURE_NOT_MODEL','phase':'RESEARCH'})
        index=sum(x['phase']=='RESEARCH' for x in self.calls)
        if self.pidgin:
            if index==1:
                return {'action':'define','symbol':'vasha',
                    'template':{'tool':'read','artifact_id':'$artifact','limit':4},
                    'gloss':'inspect the selected mathematical artifact'}
            if index==2:
                return {'action':'speak','symbol':'vasha',
                    'values':{'artifact':'experiments/thought-023/grammar.py'}}
        if index==1:return {'action':'read','artifact_id':'experiments/thought-023/grammar.py','limit':4}
        return {'action':'skip'}
    def conclude(self,task,evidence,history,lexicon,pidgin):
        self.calls.append({'source':'SCRIPTED_FIXTURE_NOT_MODEL','phase':'FINAL'})
        ids=[x['id'] for x in task['input_fields']]
        if self.task=='food_recalled_elsewhere':ids=ids[::-1]
        if self.wrong:ids=ids[::-1]
        return {'bindings':{'current':ids[0],'event':ids[1]},
                'relation':'DIFFERENCE',
                'evidence_ids':evidence['actually_read_artifact_ids'][:1],
                'rationale':'Scripted test fixture proposes a finite set difference'}

def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument('--backend',choices=('offline','ollama'),default='offline')
    p.add_argument('--model')
    p.add_argument('--repo',type=Path,default=HERE.parents[1])
    p.add_argument('--tasks',default='food_safe,food_recalled_elsewhere')
    p.add_argument('--research-steps',type=int,default=2)
    p.add_argument('--output',type=Path)
    args=p.parse_args(argv)
    if args.backend=='ollama' and not args.model:p.error('real inference requires installed local model')
    if args.backend=='offline' and args.model:p.error('offline never contacts a model')
    if not 0<=args.research_steps<=3:p.error('research steps 0..3')
    names=args.tasks.split(',')
    if not names or len(set(names))!=len(names) or any(x not in BY_KEY for x in names):p.error('invalid task IDs')
    if args.backend=='offline' and any(x not in ('food_safe','food_recalled_elsewhere') for x in names):
        p.error('scripted fixture only handles difference tasks')
    portal=ArtifactPortal(args.repo)
    results={};all_receipts=[]
    for name in names:
        task=BY_KEY[name];per={}
        for mode in ('plain','optional_pidgin'):
            if args.backend=='offline':
                model=ScriptedFixture(name,pidgin=(mode=='optional_pidgin'))
            else:
                model=DirectRelayLLM(args.model,timeout_seconds=150)
                model.verify_local_model()
            per[mode]=trial(task,portal,model,
                 enable_pidgin=mode=='optional_pidgin',research_steps=args.research_steps)
            if args.backend=='ollama':all_receipts.extend(model.calls)
        results[name]=per
    packet={'schema':'motif.thought031.proof-guided-evidence-relay.v1',
            'backend':args.backend,'model':args.model,
            'research_calls_per_arm':args.research_steps,'reserved_final_calls_per_arm':1,
            'model_call_budget_equal_between_plain_and_optional_pidgin':True,
            'model_tokens_not_equalized':True,
            'real_llm_generations':len(all_receipts),
            'real_llm_inference':args.backend=='ollama' and bool(all_receipts),
            'model_receipts':all_receipts,'source_artifact_count':len(portal._items),
            'source_graph_count':len(portal._graphs),
            'tasks':results,'no_model_written_program_executed':True,
            'not_a_blind_language_benchmark':True,'installed':False,
            'external_authority':'NONE'}
    if args.output:
        args.output.write_text(json.dumps(packet,sort_keys=True,indent=2,ensure_ascii=True)+'\n',encoding='utf8')
    print(json.dumps({'backend':args.backend,'real_model_calls':len(all_receipts),
       'outcomes':{t:{a:{'status':v['status'],
           'llm_calls':v['actual_model_call_count'],'pidgin_used':v.get('pidgin_was_used',False),
           'tokens_coined':v.get('pidgin_lexicon',{}).get('tokens_coined',0),
           'frozen':v.get('frozen',{}).get('correct') if v.get('frozen') else None}
                     for a,v in rows.items()} for t,rows in results.items()},
       'installed':False},indent=2))
    return 0 if args.backend=='offline' or all_receipts else 2

if __name__=='__main__':raise SystemExit(main())
