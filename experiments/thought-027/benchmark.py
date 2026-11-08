"""Reproducible offline receipt: all hypothesis-generation fixtures are scripted."""
import json
from pathlib import Path
from proof_memory import ProofLibrary,identifiable_stages,retain_hypotheses
from reuse import reuse,compose_difference_union
from stages import stage_trial
from stage_fixtures import DeterministicStages
from specimens import BY_KEY

def run():
    pool=ProofLibrary()
    provenance='SCRIPTED_STAGE_FIXTURE_NOT_A_LIVE_LLM'
    trained={key:pool.admit(BY_KEY[key],stage_trial(BY_KEY[key],DeterministicStages()),origin=provenance)
             for key in ('food_safe','volunteer_eligible','food_donations','not_on_shelf')}
    partial=stage_trial(BY_KEY['food_safe'],DeterministicStages(incorrect_binding=True),repair=False)
    tentative=retain_hypotheses(BY_KEY['food_safe'],partial)
    trials={key:reuse(BY_KEY[key],pool,BY_KEY) for key in ('reverse_outreach','food_recalled_elsewhere','unknown_beliefs','cancel_or_add')}
    composed=compose_difference_union(BY_KEY['cancel_or_add'],trained['food_safe'],trained['food_donations'],BY_KEY)
    return {'schema':'motif.thought027.offline-fragment-reuse.v1',
            'proposer':'SCRIPTED_TEST_FIXTURE_NOT_GENERATIVE_LLM',
            'source_tasks':list(trained),
            'proof_cards':list(trained.values()),
            'unverified_partial':tentative,'reuse_trials':trials,
            'composed_trial':composed,
            'all_claims_limited_to_3_bit_author_designed_world':True,
            'number_real_llm_generations':0,'new_task_meaning_inferred_without_oracle':False,
            'installed':False,'external_authority':'NONE'}

if __name__=='__main__':
    o=run()
    path=Path(__file__).with_name('offline-results.json')
    path.write_text(json.dumps(o,indent=2,ensure_ascii=True,sort_keys=True)+'\n')
    print(json.dumps({'provenance':o['proposer'],
           'certified_cards':len(o['proof_cards']),
           'reuse_trials':{k:{'status':v['status'],'queries':v['oracle_queries'],
                  'frozen':v['frozen']['correct'] if v.get('frozen') else None}
                  for k,v in o['reuse_trials'].items()},
           'composition':o['composed_trial']['status'],
           'real_model_calls':0,'installed':False},indent=2))
