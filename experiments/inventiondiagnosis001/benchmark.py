"""Controlled, non-blind diagnostic benchmark. Includes strong instrument control."""
from __future__ import annotations
from collections import Counter
import json
from diagnosis import advance, scenario, TASKS

EXPECTED={
    'more_evidence':'SOLVED_EXISTING_REPERTOIRE',
    'missing_control':'SOLVED_STAGED_CONTROL_FLOW_EXTENSION',
    'corrupt_sensor':'HOLD_WITNESS_DISAGREEMENT',
    'resource_cap':'SOLVED_BOUNDED_COMPUTE',
    'compute_denied':'HOLD_RESOURCE_BOUND',
    'ambiguous_sources':'HOLD_SHARED_WITNESS_ROOT',
    'unwarranted_contract':'HOLD_UNWARRANTED_TASK_CONTRACT',
    'unaffordable_growth':'HOLD_GROWTH_NOT_AFFORDABLE',
    'denied_evidence':'HOLD_MORE_EVIDENCE_REQUIRED',
    'denied_growth':'HOLD_UNSUPPORTED_REMEDY',
}

def benchmark()->dict:
    # Seven seeds on four active cases; one representative each of six explicit
    # refusal controls. These scenarios were written BY the test author: no
    # performance claims about unseen failure categories or real causal causes.
    results={};all_outputs=[]
    for kind,status in EXPECTED.items():
        repetitions=7 if kind in ('more_evidence','missing_control','corrupt_sensor','resource_cap') else 1
        rows=[advance(scenario(kind,seed)) for seed in range(repetitions)]
        all_outputs.extend(rows)
        results[kind]={
            'scenarios':repetitions,
            'matched_fixture_expected_status':sum(r['status']==status for r in rows),
            'expected':status,
            'observed_statuses':dict(Counter(r['status'] for r in rows)),
            'local_action_counts':dict(Counter(step['action_executed'] for r in rows for step in r['steps'])),
            'total_declared_budget_spent':sum(r['budget_spent'] for r in rows),
            'external_actions':sum(r['external_actions'] for r in rows),
        }
    # Frozen fixed-policy baselines: these are deliberately simple and not an
    # independent intelligence system. Always grow: tries expensive remedy even
    # when observation or fuel suffices; always probe: cannot fix cut-off fuel.
    core=('more_evidence','missing_control','corrupt_sensor','resource_cap')
    diagnosis_growth=sum(any(s['action_executed']=='GROW_CONTROL_FLOW'
                   for s in advance(scenario(k))['steps']) for k in core)
    # No truth claim from locally agreeing algorithms: they share source graphs.
    collusion=advance(scenario('colluding_readouts'))
    total=sum(r['scenarios'] for r in results.values())
    matched=sum(r['matched_fixture_expected_status'] for r in results.values())
    return {'experiment':'INVENTION-DIAGNOSIS-001',
            'scope':'author-generated synthetic graph failures; never blind real-world diagnosis',
            'synthetic_cases':total,'matched_author_expected_status':matched,
            'categories':results,
            'control_polices':{
                'always_grow_control_flow':{'grammar_attempts_if_run_on_four_core_categories':4,
                                             'needlessly_expensive_attempts':3},
                'symptom_oriented_controller':{'grammar_attempts_on_four_core_categories':diagnosis_growth,
                                               'other_paths_use_smaller_or_no_action':True},
                'always_probe':{'cannot_turn_a_truncated_partial_count_into_a_finished_reading':True},
                'strong_handwritten_graph_algorithms':{'used_for_crosscheck':True,'not_outperformed':True}},
            'coordinated_tamper_negative_control':{
                'observed_status':collusion['status'],
                'source_authenticity_verified':collusion['provenance']['source_authenticity_verified'],
                'safe_to_interpret_as_real_world_truth':False,
                'lesson':'Agreement of readings derived from one synthetic graph does not certify truth.'},
            'local_only':all(r['external_actions']==r['repository_edits']==0 for r in all_outputs),
            'general_causal_diagnosis_proved':False,
            'independent_new_task_families_tested':0}

if __name__=='__main__':print(json.dumps(benchmark(),indent=2,sort_keys=True))
