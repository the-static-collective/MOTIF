"""Compare 029 browsing with 030 routing, plus an OPTIONAL emergent word channel.

Real mode calls a preinstalled local Ollama model and records negatives. Offline
mode is scripted process tests, not model inference or independent discovery.
"""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
for k in ('thought-025','thought-029'):
    p=str(HERE.parent/k)
    if p not in sys.path:sys.path.insert(0,p)
from specimens import BY_KEY
from artifact_portal import ArtifactPortal
from interpreter import trial as legacy_trial,response_digest
from direct_artifact_llm import DirectArtifactLLM
from navigation import EvidenceNavigator
from direct_routed_llm import DirectRoutedLLM
from session import session

class ScriptedModel:
    kind='SOURCE_OWNED_SCRIPTED_FIXTURE_NOT_GENERATIVE'
    def __init__(self,task,pidgin):
        self.task=task;self.pidgin=pidgin;self.calls=[]
    def next(self,task,history,context):
        self.calls.append({'simulation_only':True})
        n=len(self.calls)
        file='experiments/thought-027/reuse.py'
        if self.pidgin:
            if n==1:
                return {'action':'define','symbol':'nawe','meaning':{
                        'tool':'read','artifact_id':file,'limit':3},
                        'gloss':'inspect a proven fragment for the problem'}
            if n==2:return {'action':'speak','symbol':'nawe'}
        else:
            if n==1:return {'action':'read','artifact_id':file,'limit':3}
        fields=[x['id'] for x in task['input_fields']]
        if self.task=='food_recalled_elsewhere':fields=fields[::-1]
        return {'action':'final','bindings':{'current':fields[0],'event':fields[1]},
                'relation':'DIFFERENCE','evidence_ids':[file],
                'rationale':'Scripted fixture ONLY: mathematical difference interpretation'}

class LegacyScripted:
    def __init__(self,task):self.task=task;self.calls=[]
    def next(self,task,history,catalog):
        self.calls.append({'simulation_only':True})
        n=len(self.calls)
        file='experiments/thought-027/reuse.py'
        if n==1:return {'action':'read','artifact_id':file}
        ids=[x['id'] for x in task['input_fields']]
        if self.task=='food_recalled_elsewhere':ids=ids[::-1]
        return {'action':'final','bindings':{'current':ids[0],'event':ids[1]},
                'relation':'DIFFERENCE','evidence_ids':[file],
                'rationale':'Scripted fixture for legacy direct artifact retrieval'}


def main(argv=None):
    p=argparse.ArgumentParser(description='Evidence guided LLM / optional pidgin A-B-C')
    p.add_argument('--backend',choices=('offline','ollama'),default='offline')
    p.add_argument('--model')
    p.add_argument('--repo',type=Path,default=HERE.parents[1])
    p.add_argument('--tasks',default='food_recalled_elsewhere')
    p.add_argument('--steps',type=int,default=6)
    p.add_argument('--output',type=Path)
    args=p.parse_args(argv)
    if args.backend=='ollama' and not args.model:p.error('requires explicit already-installed local model')
    if args.backend=='offline' and args.model:p.error('offline mode does not invoke any model')
    if not 3<=args.steps<=9:p.error('step budget 3..9')
    names=args.tasks.split(',')
    if not names or any(n not in BY_KEY for n in names) or len(set(names))!=len(names):p.error('unknown/duplicate tasks')
    if args.backend=='offline' and any(n not in ('food_safe','food_recalled_elsewhere') for n in names):
        p.error('source fixtures only cover two known tasks')
    portal=ArtifactPortal(args.repo)
    per_task={};all_receipts=[]
    for name in names:
        task=BY_KEY[name]
        row={}
        if args.backend=='ollama':
            legacy=DirectArtifactLLM(args.model,timeout_seconds=150)
            route=DirectRoutedLLM(args.model,timeout_seconds=150)
            pidgin=DirectRoutedLLM(args.model,timeout_seconds=150)
            for x in (legacy,route,pidgin):x.verify_local_model()
        else:
            legacy=LegacyScripted(name)
            route=ScriptedModel(name,False)
            pidgin=ScriptedModel(name,True)
        row['legacy']=legacy_trial(task,portal,legacy,max_steps=args.steps)
        row['routed']=session(task,portal,route,max_steps=args.steps,enable_pidgin=False)
        row['routed_optional_pidgin']=session(task,portal,pidgin,max_steps=args.steps,enable_pidgin=True)
        per_task[name]=row
        if args.backend=='ollama':
            all_receipts.extend(legacy.calls)
            all_receipts.extend(route.calls)
            all_receipts.extend(pidgin.calls)
    output={'schema':'motif.thought030.evidence-navigation-and-pidgin.v1',
            'mode':args.backend,'model':args.model,'max_model_calls_per_arm':args.steps,
            'same_public_task_brief':True,
            'matched_model_call_ceiling_but_not_prompt_tokens':True,
            'verified_pidgin_emergence_not_assumed':True,
            'all_word_meanings_auditable_and_reversible':True,
            'model_may_ignore_pidgin':True,'synthetic_task_owner_oracle':True,
            'model_calls':len(all_receipts),
            'actual_llm_inference':bool(all_receipts) and args.backend=='ollama',
            'real_model_receipts':all_receipts,'indexed_artifacts':len(portal._items),
            'indexed_graphs':len(portal._graphs),'tasks':per_task,
            'installed':False,'external_authority':'NONE'}
    output['digest']=response_digest(output)
    if args.output:args.output.write_text(json.dumps(output,indent=2,ensure_ascii=True,sort_keys=True)+'\n',encoding='utf8')
    print(json.dumps({'backend':args.backend,'model_calls':len(all_receipts),
         'artifacts':len(portal._items),'graph_views':len(portal._graphs),
         'results':{t:{arm:{'status':v['status'],
                          'read_calls':v.get('read_only_tool_calls'),
                          'pidgin_used':v.get('pidgin_used',False),
                          'pidgin_terms':v.get('pidgin_lexicon',{}).get('tokens_coined',0),
                          'frozen':v['frozen']['correct'] if v.get('frozen') else None}
                         for arm,v in rs.items()} for t,rs in per_task.items()},
         'installed':False},indent=2))
    if args.backend=='ollama' and not all_receipts:return 2
    return 0

if __name__=='__main__':raise SystemExit(main())
