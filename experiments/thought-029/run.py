"""Run the artifact-guided interpreter with a preinstalled local Ollama model.

Default `offline` mode uses scripted portal actions, not LLM inference.
Outputs both accepted and held proposals without source installation.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
from artifact_portal import ArtifactPortal
from interpreter import trial,response_digest
from specimens import BY_KEY
from direct_artifact_llm import DirectArtifactLLM

class OfflineAgent:
    kind='FIXTURE_NOT_LLM'
    def __init__(self,task):self.task=task;self.calls=[]
    def next(self,t,h,c):
        n=len(self.calls)
        self.calls.append({'not_a_generating_model':True})
        if n==0:return {'action':'graphs'}
        if n==1:return {'action':'read','artifact_id':'experiments/thought-027/reuse.py'}
        # Task-specific regression fixture supplied ONLY by source-owned harness.
        policy={'food_safe':('register_f','register_g','DIFFERENCE'),
                'food_recalled_elsewhere':('register_g','register_f','DIFFERENCE'),
                'volunteer_eligible':('stream_a','stream_b','INTERSECTION')}
        a,b,rel=policy[self.task]
        return {'action':'final','bindings':{'current':a,'event':b},'relation':rel,
                'evidence_ids':['experiments/thought-027/reuse.py'],
                'rationale':'Source-owner scripted fixture for internal portal integration'}

def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument('--backend',choices=('offline','ollama'),default='offline')
    p.add_argument('--model')
    p.add_argument('--repo',type=Path,default=Path(__file__).resolve().parents[2])
    p.add_argument('--tasks',default='food_safe,food_recalled_elsewhere,volunteer_eligible')
    p.add_argument('--steps',type=int,default=5)
    p.add_argument('--output',type=Path)
    args=p.parse_args(argv)
    if args.backend=='ollama' and not args.model:p.error('requires explicit installed local Ollama model')
    if args.backend=='offline' and args.model:p.error('offline fixture never calls Ollama')
    names=args.tasks.split(',')
    if len(names)!=len(set(names)) or not names or any(t not in BY_KEY for t in names):p.error('unknown or repeated task')
    if args.backend=='offline' and any(t not in ('food_safe','food_recalled_elsewhere','volunteer_eligible') for t in names):
        p.error('offline fixture supports only three known regression tasks')
    portal=ArtifactPortal(args.repo)
    model=DirectArtifactLLM(args.model,timeout_seconds=150) if args.backend=='ollama' else None
    if model is not None:model.verify_local_model()
    results={}
    for task_name in names:
        task=BY_KEY[task_name]
        current=model if model is not None else OfflineAgent(task_name)
        results[task_name]=trial(task,portal,current,max_steps=args.steps)
    real=len(model.calls) if model is not None else 0
    out={'schema':'motif.thought029.tool-guided-abstraction-experiment.v1',
         'backend':args.backend,'model_tag':args.model,
         'real_local_ollama_model_generations':real,
         'real_model_execution_verified':real>0 and model is not None,
         'source_scope':'EXPLICIT_CHECKOUT_ONLY',
         'repository_artifact_count':len(portal._items),
         'symbolic_graph_count':len(portal._graphs),
         'typed_artifact_types':sorted({v[0]['kind'] for v in portal._items.values()}),
         'trials':results,'all_model_origin_claims_unverified':True,
         'available_tools':['catalog','search','graphs','read','neighbors'],
         'unbounded_pagination_reachable':True,
         'allowed_runtime_snapshots_require_source_owner_approval':True,
         'external_project_accounts_not_automatically_connected':True,
         'text_only_model_cannot_see_opaque_media_pixels':True,
         'artifact_data_not_granted_authority':True,
         'installed':False,'external_authority':'NONE'}
    out['digest']=response_digest(out)
    if args.output:args.output.write_text(json.dumps(out,indent=2,ensure_ascii=True,sort_keys=True)+'\n')
    print(json.dumps({'backend':args.backend,'real_ollama_generations':real,
            'repo_artifacts':len(portal._items),'graphs':len(portal._graphs),
            'trial_statuses':{k:v['status'] for k,v in results.items()},
            'installed':False},indent=2))
    return 0 if args.backend=='offline' or real>0 else 2

if __name__=='__main__':raise SystemExit(main())
