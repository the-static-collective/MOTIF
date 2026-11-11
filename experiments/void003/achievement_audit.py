"""VOID-003R: POSTHOC independent outcome audit from stored real-game receipts.

The preregistered inventory-gain score stays unchanged. This audit detects a
previously missed official game achievement and reports first actual completion
of the two goals. It does not retroactively restore unused action budget.
"""
from __future__ import annotations
from pathlib import Path
import json
from memory import seal

GOALS=('game_wood_obtained','game_drink_obtained')

def first_attested_goals(run):
    achieved={}
    for receipt in run['action_receipts']:
        if receipt['seal']!=seal({k:v for k,v in receipt.items() if k!='seal'}):
            raise ValueError('TAMPERED_SOURCE_STEP')
        goal=receipt['goal']
        if goal not in GOALS or goal in achieved:
            continue
        if (receipt['verified_goal_outcome']!='GOAL_NOT_YET_WITNESSED' or
            (goal=='game_drink_obtained' and receipt['action']=='do' and
             receipt['collect_drink_achievement_after']>
             receipt['collect_drink_achievement_before'])):
            achieved[goal]=receipt['tick']
    return achieved

def report(data,posthoc=None):
    if data['seal']!=seal({k:v for k,v in data.items() if k!='seal'}):
        raise ValueError('TAMPERED_PRIMARY_RECORD')
    if data['experiment']!='VOID-003' or data['case_count']!=10:
        raise ValueError('WRONG_AUDIT_SOURCE')
    cases=[]
    for c in data['cases']:
        followups={name:first_attested_goals(r) for name,r in c['followups'].items()}
        scouts={name:first_attested_goals(r) for name,r in c['scouts'].items()}
        cases.append({'seed':c['seed'],'split':c['split'],'followups_first_goals':followups,
                      'scouts_first_goals':scouts,
                      'first_both_goal_tick':{name:max(t.values()) if len(t)==2 else None
                                              for name,t in followups.items()},
                      'historical_motif_map_cells':c['scouts']['motif003']['seen_coordinate_count'],
                      'historical_classical_map_cells':c['scouts']['classical_2ply']['seen_coordinate_count']})
    groups={}
    for split in ('development','heldout'):
        group=[c for c in cases if c['split']==split]
        groups[split]={}
        for name in ('no_memory','classical_memory','motif_memory'):
            values=[c['first_both_goal_tick'][name] for c in group]
            groups[split][name]={
                'both_goals_seen_in_engine_achievements':sum(x is not None for x in values),
                'mean_first_both_tick':round(sum(x for x in values if x is not None)/max(1,sum(x is not None for x in values)),6),
                'ticks_by_seed':dict(zip((c['seed'] for c in group),values)),
            }
    output={'audit':'VOID-003R','classification':'POSTHOC_OUTCOME_CORRECTION_NOT_FROZEN_PRIMARY',
            'source_original_sha':data['seal'],
            'problem':'Water collection achievement can increase while capped drink inventory stays unchanged. Prior checker ignored collect_drink achievements, falsely reporting successful interactions as failures.',
            'new_policy_evaluation':False,'goal_type':'game achievement or resource increase from actual env.step',
            'second_run_timing':groups,
            'game_goal_sample_lines':cases,
            'cases':len(cases),
            'limits':['Rescoring does not replay a policy that would have stopped early.',
                      'Old cohort is now examined and cannot be re-labeled fresh. New controller must face new seeds.',
                      'Crafter official collect_drink achievement verifies virtual game actuation, not real drinking.']}
    if posthoc:
        p=posthoc['full_records']['followups']
        if posthoc['seed']!=19003 or not posthoc['not_confirmatory']:
            raise ValueError('INVALID_POSTHOC_SEED')
        output['already_seen_19003']={
            'motif_map_cells':posthoc['scout_seen_motif'],
            'classical_2ply_map_cells':posthoc['scout_seen_classical'],
            'motif_exclusive_cells':posthoc['motif_exclusive'],
            'first_both_goal_tick':{name:(max(t.values()) if len(t)==2 else None)
                                    for name,run in p.items() for t in [first_attested_goals(run)]},
            'interpretation':'Posthoc: extra inspected terrain did not alter the first measured second-run goal-completion tick.'}
    output['seal']=seal(output)
    return output

if __name__=='__main__':
    root=Path(__file__).resolve().parents[2]
    prior=json.loads((root/'void003-two-run-crafter-audit.json').read_text())
    pp=root/'void003-posthoc-seed19003.json'
    old=json.loads(pp.read_text()) if pp.exists() else None
    result=report(prior,old)
    (root/'void003-achievement-correction-posthoc.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='game_goal_sample_lines'},sort_keys=True,indent=2))
