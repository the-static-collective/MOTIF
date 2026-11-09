"""Bounded offline and genuinely invoked Ollama shared-concept experiment."""
import argparse,json
from pathlib import Path
from concept_language import digest
from experiment import session
from specimens import BY_KEY
from model import DirectConceptLLM

class ScriptedConceptAgent:
    kind='SCRIPTED_SOURCE_OWNER_FIXTURE_NOT_GENERATIVE_LLM'
    def __init__(self):self.calls=[]
    def prepare(self,context,pidgin_enabled):
        self.calls.append({'phase':'PREPARE','scripted':True})
        if not pidgin_enabled:return {'choice':'baseline','definition':None}
        return {'choice':'coin','definition':{'word':'yiblat','gloss':'Exclude a second finite category set from a primary one',
            'relation':'DIFFERENCE','graph_pattern':'DEPENDENCY_CHAIN',
            'proof_gate':'DEV_THEN_FROZEN_64',
            'uncertainty':'TRANSFER_REQUIRES_NEW_EVIDENCE',
            'next_experiment':'DISCRIMINATING_DEV_QUERIES'}}
    def apply(self,task,context,concept_book,pidgin_enabled):
        self.calls.append({'phase':'APPLY','scripted':True})
        ids={x['human_description']:x['id'] for x in task['input_fields']}
        if 'recalled items' in ids and 'shelf inventory' in ids:
            binding={'current':ids['recalled items'],'event':ids['shelf inventory']}
        elif 'declined to volunteer' in ids and 'confirmed availability' in ids:
            binding={'current':ids['declined to volunteer'],'event':ids['confirmed availability']}
        else:raise ValueError('unsupported scripted test specimen')
        return {'bindings':binding,
             'word':'yiblat' if pidgin_enabled else None,
             'relation':None if pidgin_enabled else 'DIFFERENCE',
             'evidence_refs':[context['proof_seed']['proof_digest']],
             'rationale':'Scripted fixture excludes secondary labels from the primary set'}

def main(argv=None):
    ap=argparse.ArgumentParser()
    ap.add_argument('--backend',choices=('offline','ollama'),default='offline')
    ap.add_argument('--model')
    ap.add_argument('--output',type=Path)
    args=ap.parse_args(argv)
    if args.backend=='ollama' and not args.model:ap.error('explicit model required for actual inference')
    if args.backend=='offline' and args.model:ap.error('offline must not specify model')
    targets=[BY_KEY[k] for k in ('food_recalled_elsewhere','reverse_outreach')]
    rows={};receipts=[]
    for name,enabled in (('baseline',False),('optional_concept',True)):
        model=ScriptedConceptAgent() if args.backend=='offline' else DirectConceptLLM(args.model,timeout_seconds=150)
        if args.backend=='ollama':model.verify_local_model()
        result=session(targets,model,pidgin_enabled=enabled)
        rows[name]=result
        if args.backend=='ollama':receipts.extend(result['model_inference_receipts'])
    out={'schema':'motif.thought032.comparison.v1','backend':args.backend,
        'actual_model_inference':args.backend=='ollama' and bool(receipts),
        'real_model_calls':len(receipts),'receipts':receipts,
        'arms':rows,'matched_max_model_calls':True,'matched_token_cost':False,
        'target_scenarios_independently_blind':False,
        'scripted_fixture_is_not_generations':args.backend=='offline',
        'automatically_installed':False,'external_authority':'NONE'}
    out['digest']=digest(out)
    if args.output:args.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n',encoding='utf8')
    print(json.dumps({'backend':args.backend,'real_calls':len(receipts),
       'results':{arm:{'coined':v['concept_book']['coined'],'uses':v['concept_book']['uses'],
            'calls':v['inference_calls'],
            'task_statuses':{k:r['status'] for k,r in v['results'].items()}}
            for arm,v in rows.items()},'installed':False},indent=2))
    return 0 if args.backend=='offline' or receipts else 2
if __name__=='__main__':raise SystemExit(main())
