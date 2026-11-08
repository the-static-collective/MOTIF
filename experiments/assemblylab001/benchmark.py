"""Small independent-purpose coverage control, not a novel reasoning benchmark."""
from dataclasses import replace
from pathlib import Path
import json
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'assemblylab001'))
from assembly import Goal,compile_assembly,execute,fixture,_import_real


def run_benchmark(root: Path=ROOT, cases_per_domain: int=12):
    if type(cases_per_domain) is not int or not 1<=cases_per_domain<=25:
        raise ValueError('bounded fixture count required')
    real=_import_real(root)
    records=[]
    for k in range(cases_per_domain):
        for domain in ('affordance','witness'):
            goal=Goal(domain,'immediate' if k%2 else 'new_choices')
            plan=compile_assembly(root,goal)
            if domain=='affordance':
                state=frozenset({('need','repair'), ('resource',f'r{k%3}')})
                data={'scene':state}
            else:
                from witnesschain import HYPOTHESES
                witness=real['State']()
                for observation,_ in real['synthetic_cases'](HYPOTHESES[k%len(HYPOTHESES)],11+k,32):
                    witness=witness.add(observation)
                data={'witness_state':witness,
                      'witness_goal':real['NextGoal']('absolute_polarity',budget=3,max_steps=2)}
            output=execute(plan,root,data)
            correct=(output['status']=='EXECUTED_TYPED_COMPOSITION'
                     and output.get('external_actions')==0
                     and output['result']['domain']==domain
                     and not output['result']['new_independent_evidence'])
            records.append({'fixture':k,'domain':domain,'success':correct,
                            'stage_ids':plan.stages,
                            'status':output['status'],
                            'next_question':output.get('result',{}).get('next_question')})
    # Declared weak control: a fixed witness-only workflow has no graph adapter.
    fixed_witness_coverage = sum(r['domain']=='witness' and r['success'] for r in records)
    return {'experiment':'SELF-ASSEMBLY-001',
            'scope':'synthetic typed assembly coverage, not algorithm performance',
            'fixtures':len(records),
            'typed_composer_completed':sum(x['success'] for x in records),
            'fixed_witness_only_completed':fixed_witness_coverage,
            'distinct_actual_source_stages':sorted({s for x in records for s in x['stage_ids']}),
            'known_domains':('affordance','witness'),
            'independent_real_world_validation':False,
            'reusable_general_autonomous_programming':False,
            'real_actions':0,
            'records':records}

if __name__=='__main__':
    print(json.dumps(run_benchmark(),indent=2,sort_keys=True))
