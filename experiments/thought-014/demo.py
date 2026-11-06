"""Minimal developer loop output suitable for a JAR;VIS read-only proposal card."""
from __future__ import annotations
import json
from benchmark import main


def demo():
    r=main();l=r['language_developer'];p=r['policy_developer']
    return {'schema':'motif.thought014.demo.v1',
        'claim':'MOTIF invoked a tiny trained language model as a dev-test subject; no local LLM present',
        'model_kind':r['model_tested_kind'],
        'model_inference_calls':r['model_inference_calls'],
        'language_rules_staged':len(l['staged_rules']),
        'language_development_correct':[l['development_baseline'],l['development_final'],l['development_total']],
        'language_frozen_correct':[l['frozen_baseline'],l['frozen_candidate'],l['frozen_total']],
        'safety_passed':[l['safety_passed'],l['safety_total']],
        'selected_reasoning_policy':p['selected_after_dev'],
        'policy_development':{k:{j:v[j] for j in ('resolved','queries')} for k,v in p['development'].items()},
        'policy_frozen':{k:{j:v[j] for j in ('resolved','queries')} for k,v in p['heldout'].items()},
        'staged_only':True,'installed':False,'pen_unchanged':True,
        'authority':'NONE','status':l['status']}

if __name__=='__main__':print(json.dumps(demo(),indent=2,sort_keys=True))
