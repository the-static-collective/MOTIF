"""QC-015: actual Crafter engine 2-N oscillation detection / bounded escape.

This is an experiment with a hand-coded monitor and heuristic, not autonomous
learning or a real-world survival agent. Local tile perception is privileged,
and deliberate test fixtures patch the game's starting terrain.
"""
from __future__ import annotations
from pathlib import Path
import json,os,sys
import crafter

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'quantumcode012'))
sys.path.insert(0,str(ROOT/'quantumcode013'))
sys.path.insert(0,str(ROOT/'quantumcode011'))
from play_crafter import Controller,ACTS,DIRS,WALK,snapshot,encode_state
from expert_intervention import expert_informed_act
from game_replay import Episode,Replay,relatte_preview
from cycle_field import FieldState,FieldStep,CycleMonitor,VITALS


def game_state(t,env):
    p=env._player
    iv=dict(p.inventory)
    return FieldState(
        tuple(int(x) for x in p.pos),
        tuple(sorted((k,int(v)) for k,v in iv.items() if k not in VITALS)),
        tuple(sorted('achievement:'+k for k,v in p.achievements.items() if v>0)),
        tuple(sorted((k,int(v)) for k,v in iv.items() if k in VITALS)),t)


class LocalKnowledge:
    """New nearby terrain cells/materials only, not hallucinated new facts."""
    def __init__(self):
        self.seen=set()
        self.new_cells=0

    def scan(self,env,actor):
        origin=actor.pos(env)
        fresh=0
        for dx in range(-7,8):
            for dy in range(-7,8):
                if abs(dx)+abs(dy)>7:continue
                loc=(origin[0]+dx,origin[1]+dy)
                tile=actor.tile(env,loc)
                if tile is None:continue
                key=(loc,str(tile[0]))
                if key not in self.seen:
                    self.seen.add(key)
                    fresh+=1
        self.new_cells+=fresh
        return fresh


def injected_oscillation_setup(env):
    """Clearly mark artificial alteration: a tiny controlled test, not play."""
    p=tuple(int(x) for x in env._player.pos)
    if not (3<p[0]<60 and 3<p[1]<60):
        raise ValueError('Unexpected controlled starting location')
    altered=[]
    for dx,dy in ((1,0),(0,-1),(-1,0)):
        loc=(p[0]+dx,p[1]+dy)
        material,obj=env._world[loc]
        if obj is not None:
            env._world.remove(obj)
        env._world[loc]='grass'
        altered.append({'tile':loc,'original_material':str(material),
                        'was_object':obj is not None})
    return {'starting_coordinate':p,'replaced_cells':altered,
            'naturally_observed':False,
            'source':'explicitly controlled test injection'}


def oscillation_action(env,anchor):
    xy=tuple(int(x) for x in env._player.pos)
    return ('move_right' if xy==anchor else 'move_left'), \
           'intentionally_broken_oscillator'


def alternate_tile(env,controller,taboo):
    """Inspect four actual nearby passable tiles; do not invent a route."""
    pos=controller.pos(env)
    options=[]
    for name,delta in DIRS.items():
        loc=(pos[0]+delta[0],pos[1]+delta[1])
        material=controller.tile(env,loc)
        if material is None or material[0] not in WALK or material[1] is not None:
            continue
        if loc in taboo:continue
        options.append((controller.visited[loc],name,loc))
    if not options:
        return None
    _,action,loc=min(options,key=lambda x:(x[0],x[1],x[2]))
    return action,loc


def play(seed,mode,outdir,scenario='controlled',horizon=140):
    env=crafter.Env(seed=seed,length=horizon,view=(9,9),size=(64,64))
    env.reset()
    fixture=injected_oscillation_setup(env) if scenario=='controlled' else None
    ctr=Controller(seed)
    known=LocalKnowledge()
    known.scan(env,ctr)
    monitor=CycleMonitor(max_period=7)
    before=snapshot(0,env._player.inventory,
                    env._player.achievements,env._player.pos)
    episodes=[]
    alerts=[]
    events=[]
    visits={tuple(int(x) for x in env._player.pos)}
    first_alert=None
    first_escape=None
    active_alert=None
    pending_escape=None
    hold=False
    ended=False
    for t in range(horizon):
        observed_before=game_state(t,env)
        if scenario=='controlled':
            intention,reason=oscillation_action(env,fixture['starting_coordinate'])
        else:
            intention,reason=expert_informed_act(ctr,env)
        action=intention
        if mode=='guarded' and active_alert is not None:
            choice=alternate_tile(env,ctr,set(active_alert.location_pattern))
            if choice is None:
                hold=True
                events.append({'step':t+1,'action':'HOLD',
                               'cause':'NO_OBSERVED_ALTERNATIVE_TILE'})
                break
            action,pending_escape=choice
            reason='OBSERVED_NONCYCLIC_NEIGHBOR_PROBE'
            active_alert=None
        obs,reward,ended,info=env.step(ACTS.index(action))
        observed_after=game_state(t+1,env)
        new_facts=known.scan(env,ctr)
        visits.add(observed_after.xy)
        g=snapshot(t+1,info['inventory'],info['achievements'],info['player_pos'])
        newly=set(g.capabilities)-set(before.capabilities)
        succeeded=bool(newly or g.location!=before.location
                       or any(dict(g.resources).get(k,0)>dict(before.resources).get(k,0)
                              for k in ('wood','stone','coal','iron','food','drink')))
        episode=Episode(
            f'qc015:{seed}:{scenario}:{mode}:{t+1}',
            'OTHER_GAME','GAME_TELEMETRY',
            f'crafter:1.8.3:seed{seed}:step{t+1}',
            'OWNER_PROVIDED',t,t+1,action,before,g,
            'SUCCESS' if succeeded else 'INCONCLUSIVE',
            f'Actual environment.step; policy={mode}; intent={reason}; '
            f'visible_new_terrain_facts={new_facts}; '
            'timestamps are game ticks, not video seconds',
            'OBSERVED',('OBSERVED_GAME',))
        episode.validate()
        episodes.append(episode)
        alert=monitor.observe(FieldStep(
            observed_before,action,observed_after,new_facts,episode.pin))
        if alert:
            alerts.append({'step':alert.detected_step,'period':alert.period,
                           'status':alert.status,'actions':alert.action_pattern,
                           'locations':alert.location_pattern,
                           'vital_debt':alert.vital_debt,
                           'source_pins':alert.evidence_pins})
            if first_alert is None:first_alert=t+1
            if (mode=='guarded' and
                alert.status=='CONFIRMED_NO_INFORMATION_CYCLE'):
                active_alert=alert
        if pending_escape is not None:
            if observed_after.xy==pending_escape:
                first_escape=t+1
                events.append({'step':t+1,'action':action,
                               'reason':'ESCAPE_TILE_REACHED',
                               'position':observed_after.xy,
                               'new_cells':new_facts})
                pending_escape=None
                if scenario=='controlled':
                    before=g
                    break
            else:
                events.append({'step':t+1,'action':action,
                               'reason':'ESCAPE_ACTION_FAILED_TO_MOVE'})
                pending_escape=None
        if alert or t<8 or (t+1)%20==0:
            events.append({'step':t+1,'action':action,
                           'reason':reason,'position':observed_after.xy,
                           'new_cells':new_facts,
                           'cycle_detected':bool(alert)})
        before=g
        if ended:break
    if not episodes:raise ValueError('Test had no game engine actions')
    replay=Replay(
        'OTHER_GAME',tuple(episodes),
        f'REAL_CRAFTER;seed={seed};mode={mode};scenario={scenario};'
        f'injected={bool(fixture)};privileged_local_tiles=True',True)
    replay.validate()
    preview=relatte_preview(replay)
    outdir=Path(outdir)
    outdir.mkdir(parents=True,exist_ok=True)
    raw={
        'schema':'motif.annotated-gameplay/v0',
        'game':replay.game,'provenance':replay.provenance,
        'consent_for_derived_research':True,
        'episodes':[{
            **{k:v for k,v in e.__dict__.items()
               if k not in ('before','after','tags')},
            'before':encode_state(e.before),'after':encode_state(e.after),
            'tags':list(e.tags)} for e in replay.episodes]}
    (outdir/'annotated_gameplay.json').write_text(
        json.dumps(raw,sort_keys=True,indent=2)+'\n')
    summary={
        'seed':seed,'mode':mode,'scenario':scenario,
        'controlled_start':fixture,
        'game_steps':len(episodes),'game_ended':ended,
        'game_health':int(env._player.inventory['health']),
        'achievements':sum(v>0 for v in env._player.achievements.values()),
        'new_terrain_observations':known.new_cells,
        'unique_locations':len(visits),
        'first_alert_game_step':first_alert,
        'first_escape_game_step':first_escape,
        'cycles':alerts,'events':events,'entered_hold':hold,
        'replay_pin':replay.pin,'relatte_status':preview['status'],
        'real_world_actions':0,'agent_has_trained_game_policy':False,
    }
    (outdir/'summary.json').write_text(
        json.dumps(summary,sort_keys=True,indent=2)+'\n')
    print('QC015_RUN='+json.dumps(
        {k:v for k,v in summary.items()
         if k not in ('controlled_start','events','cycles')},
        sort_keys=True),flush=True)
    return summary


def experiment():
    output=Path(os.environ.get('QC015_OUTPUT_DIR','runs/crafter-qc015'))
    output.mkdir(parents=True,exist_ok=True)
    controlled=[]
    natural=[]
    for seed in (1042,2026,3199,8765):
        before=play(seed,'blind',output/f'{seed}-blind-loop','controlled',30)
        after=play(seed,'guarded',output/f'{seed}-guarded-loop','controlled',30)
        controlled.append({
            'seed':seed,'baseline_steps':before['game_steps'],
            'guarded_steps':after['game_steps'],
            'baseline_unique_locations':before['unique_locations'],
            'guarded_unique_locations':after['unique_locations'],
            'guarded_alert_step':after['first_alert_game_step'],
            'guarded_escape_step':after['first_escape_game_step'],
            'guarded_hold':after['entered_hold']})
    for seed in (1042,2026,3199,8765,4477,5011):
        before=play(seed,'blind',output/f'{seed}-natural-baseline','natural',220)
        after=play(seed,'guarded',output/f'{seed}-natural-guarded','natural',220)
        natural.append({
            'seed':seed,'baseline_steps':before['game_steps'],
            'guarded_steps':after['game_steps'],
            'baseline_health':before['game_health'],
            'guarded_health':after['game_health'],
            'baseline_achievements':before['achievements'],
            'guarded_achievements':after['achievements'],
            'guarded_cycle_alerts':len(after['cycles']),
            'guarded_escapes':sum(x.get('reason')=='ESCAPE_TILE_REACHED'
                                   for x in after['events']),
            'guarded_hold':after['entered_hold']})
    result={
        'experiment':'MOTIF-QC015',
        'controlled_paired':controlled,'natural_paired':natural,
        'actual_game_engine':'crafter 1.8.3',
        'same_privileged_local_terrain_sensor':True,
        'human_expert_precedent':'QC013 demonstrations; not trained policy',
        'real_world_actions':0,
        'fair_policy_superiority_not_established':True,
        'game_action_count':sum(x['baseline_steps']+x['guarded_steps']
                               for x in controlled+natural)}
    (output/'comparison.json').write_text(
        json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('QC015_COMPARISON='+json.dumps(result,sort_keys=True),flush=True)
    return result

if __name__=='__main__':experiment()
