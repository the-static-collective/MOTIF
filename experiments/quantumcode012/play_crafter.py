"""Play real Crafter episodes using an openly documented local debug sensor.

The environment is an independently authored open-source survival game.
This is a hand-coded controller, NOT MOTIF policy/LLM cognition or fair
benchmarking: it reads current local tile types via Crafter internals.
Every executed action is logged into the exact QC-011 replay schema.
No game video or other copyrighted playthrough is scraped or copied.
"""
from __future__ import annotations
import collections
import importlib.metadata
import json
import os
import random
import sys
from pathlib import Path

import crafter
from PIL import Image,ImageDraw

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"quantumcode011"))
from game_replay import Episode,GameState,Replay,interpret,relatte_preview

ACTS=["noop","move_left","move_right","move_up","move_down","do","sleep",
      "place_stone","place_table","place_furnace","place_plant",
      "make_wood_pickaxe","make_stone_pickaxe","make_iron_pickaxe",
      "make_wood_sword","make_stone_sword","make_iron_sword"]
DIRS={"move_left":(-1,0),"move_right":(1,0),
      "move_up":(0,-1),"move_down":(0,1)}
WALK={"grass","path","sand"}
RADIUS=7


def snapshot(t,inventory,achievements,pos):
    return GameState(
        tuple(sorted((str(k),int(v)) for k,v in inventory.items())),
        tuple(sorted("achievement:"+k for k,v in achievements.items() if v>0)),
        (),
        "GAME_TILE:%d,%d"%(int(pos[0]),int(pos[1])),t,
    )


class Controller:
    def __init__(self,seed):
        self.rng=random.Random(seed+919)
        self.visited=collections.Counter()

    @staticmethod
    def pos(env):
        return tuple(int(v) for v in env._player.pos)

    def tile(self,env,p,start=None):
        start=self.pos(env) if start is None else start
        if abs(p[0]-start[0])+abs(p[1]-start[1])>RADIUS:
            return None
        if not (0<=p[0]<64 and 0<=p[1]<64):
            return None
        try:
            return env._world[p]
        except (IndexError,KeyError,ValueError):
            return None

    def explore(self,env):
        pos=self.pos(env)
        options=[]
        for a,d in DIRS.items():
            p=(pos[0]+d[0],pos[1]+d[1])
            t=self.tile(env,p)
            if t is not None and t[0] in WALK and t[1] is None:
                options.append((self.visited[p],self.rng.random(),a))
        if not options:
            return "noop","trapped"
        _,_,action=min(options)
        return action,"explore_less_visited"

    def approach(self,env,kind):
        """Path to a visible resource, WITHOUT peeking at distant cells."""
        origin=self.pos(env)
        options=[]
        for dx in range(-RADIUS,RADIUS+1):
            for dy in range(-RADIUS,RADIUS+1):
                p=(origin[0]+dx,origin[1]+dy)
                if abs(dx)+abs(dy)>RADIUS: continue
                tile=self.tile(env,p)
                if tile and tile[0]==kind:
                    options.append(p)
        bfs=collections.deque((origin,))
        prev={origin:None}
        while bfs:
            here=bfs.popleft()
            for name,d in DIRS.items():
                nxt=(here[0]+d[0],here[1]+d[1])
                if nxt in prev: continue
                cell=self.tile(env,nxt,origin)
                if cell is None or cell[0] not in WALK or cell[1] is not None:
                    continue
                prev[nxt]=here
                bfs.append(nxt)
        paths=[]
        for target in options:
            for d in DIRS.values():
                stand=(target[0]+d[0],target[1]+d[1])
                if stand not in prev: continue
                walk=[]
                cursor=stand
                while prev[cursor] is not None:
                    walk.append(cursor)
                    cursor=prev[cursor]
                walk.reverse()
                paths.append((len(walk),target,walk))
        if not paths:
            return None
        _,target,path=min(paths,key=lambda x:(x[0],x[1]))
        if path:
            delta=(path[0][0]-origin[0],path[0][1]-origin[1])
            return next(a for a,d in DIRS.items() if d==delta),"approach_"+kind
        delta=(target[0]-origin[0],target[1]-origin[1])
        if tuple(env._player.facing)!=delta:
            return next(a for a,d in DIRS.items() if d==delta),"face_"+kind
        return "do","collect_"+kind

    def act(self,env):
        inv=env._player.inventory
        ach=env._player.achievements
        self.visited[self.pos(env)]+=1
        if inv["drink"]<=3:
            item=self.approach(env,"water")
            if item: return item
        if ach["place_table"]==0:
            if inv["wood"]<3:
                item=self.approach(env,"tree")
                if item: return item
            else:
                p=self.pos(env)
                front=tuple(p[i]+env._player.facing[i] for i in (0,1))
                cell=self.tile(env,front)
                if cell and cell[0] in WALK and cell[1] is None:
                    return "place_table","create_crafting_table"
        elif inv["wood_pickaxe"]<1:
            if inv["wood"]<1:
                item=self.approach(env,"tree")
                if item:return item
            else:
                return "make_wood_pickaxe","craft_pickaxe_if_table_nearby"
        if inv["wood_pickaxe"]>0 and inv["stone"]<4:
            item=self.approach(env,"stone")
            if item:return item
        if inv["stone"]>=4 and ach["place_furnace"]==0:
            p=self.pos(env)
            front=tuple(p[i]+env._player.facing[i] for i in (0,1))
            cell=self.tile(env,front)
            if cell and cell[0] in WALK and cell[1] is None:
                return "place_furnace","build_furnace"
        if inv["energy"]<=3 and inv["health"]>=5:
            return "sleep","regain_game_energy"
        return self.explore(env)


def encode_state(x):
    return {**x.__dict__,
            "resources":[list(t) for t in x.resources],
            "capabilities":list(x.capabilities),"hazards":list(x.hazards)}


def run(seed,limit,policy,outdir):
    env=crafter.Env(seed=seed,length=limit,view=(9,9),size=(64,64))
    obs=env.reset()
    ctrl=Controller(seed)
    before=snapshot(0,env._player.inventory,
                    env._player.achievements,env._player.pos)
    events=[]
    frames=[obs]
    milestones=[]
    reward_total=0
    done=False
    for n in range(limit):
        if policy=="random":
            action=ctrl.rng.choice(ACTS)
            reason="random_control"
        else:
            action,reason=ctrl.act(env)
        obs,reward,done,info=env.step(ACTS.index(action))
        reward_total+=float(reward)
        after=snapshot(n+1,info["inventory"],info["achievements"],info["player_pos"])
        new_caps=tuple(sorted(set(after.capabilities)-set(before.capabilities)))
        changed_position=before.location!=after.location
        inventory_change=before.resources!=after.resources
        success=(bool(new_caps) or
                 action.startswith("move_") and changed_position or
                 action in ("do","sleep") and inventory_change)
        e=Episode(
            f"crafter-seed{seed}-{policy}-step{n+1:04}","OTHER_GAME",
            "GAME_TELEMETRY",
            f"crafter-1.8.3:seed{seed}:policy{policy}:tick{n+1}",
            "OWNER_PROVIDED",n,n+1,action,before,after,
            "SUCCESS" if success else "INCONCLUSIVE",
            "Controller=%s; decision=%s; episode times are action indices not video seconds."%
                (policy,reason),
            "OBSERVED",("OBSERVED_GAME",))
        e.validate()
        events.append(e)
        if new_caps or (n+1)%40==0 or done:
            d=interpret(e)
            milestones.append({
                "step":n+1,"action":action,"rationale":reason,
                "capabilities_gained":new_caps,
                "resources_received":d.gained_resources,
                "resources_spent":d.spent_resources,
                "health":dict(after.resources).get("health"),
                "food":dict(after.resources).get("food"),
                "drink":dict(after.resources).get("drink")})
        if n%35==0 or done or n==limit-1:
            frames.append(obs)
        before=after
        if done:break
    replay=Replay(
        "OTHER_GAME",tuple(events),
        ("REAL_CRAFTER_ENGINE_EXECUTION;version=%s;seed=%d;policy=%s;"
         "local_debug_tiles=%s;https://github.com/danijar/crafter")%
        (importlib.metadata.version("crafter"),seed,policy,
         str(policy!="random")),
        True)
    replay.validate()
    preview=relatte_preview(replay)
    outdir.mkdir(parents=True,exist_ok=True)
    data={
        "schema":"motif.annotated-gameplay/v0",
        "game":"OTHER_GAME",
        "provenance":replay.provenance,
        "consent_for_derived_research":True,
        "episodes":[{
            **{k:v for k,v in ep.__dict__.items()
               if k not in ("before","after","tags")},
            "before":encode_state(ep.before),
            "after":encode_state(ep.after),
            "tags":list(ep.tags)} for ep in replay.episodes]}
    (outdir/"annotated_gameplay.json").write_text(
        json.dumps(data,indent=2,sort_keys=True)+"\n")
    cols=4
    rows=(len(frames)+cols-1)//cols
    sheet=Image.new("RGB",(cols*256,rows*276),(24,24,24))
    drawing=ImageDraw.Draw(sheet)
    for i,f in enumerate(frames):
        x=(i%cols)*256
        y=(i//cols)*276
        resized=Image.fromarray(f).resize((256,256),Image.Resampling.NEAREST)
        sheet.paste(resized,(x,y+20))
        drawing.text((x+6,y+3),"Observation %02d"%i,fill="white")
    sheet.save(outdir/"actual_gameplay_frames.png")
    summary={
        "engine":"crafter","engine_version":importlib.metadata.version("crafter"),
        "seed":seed,"policy":policy,
        "sensor":"PRIVILEGED_CURRENT_LOCAL_TILES_RADIUS_7"
                 if policy!="random" else "NO_SENSOR_RANDOM",
        "real_engine_steps":len(events),"done":done,
        "reward":round(reward_total,2),
        "achievements":[x.replace("achievement:","") for x in before.capabilities],
        "final_inventory":dict(before.resources),
        "replay_pin":replay.pin,
        "replay_validated":True,
        "relatte_status":preview["status"],
        "milestones":milestones,
        "real_world_actions":0}
    (outdir/"summary.json").write_text(
        json.dumps(summary,indent=2,sort_keys=True)+"\n")
    print("QC012_SUMMARY_JSON="+json.dumps({
        k:v for k,v in summary.items() if k!="milestones"},sort_keys=True),
        flush=True)
    print("QC012_MILESTONES_JSON="+json.dumps(milestones[:45],sort_keys=True),
          flush=True)
    return summary


def main():
    root=Path(os.environ.get("QC012_OUTPUT_DIR","runs/crafter-qc012"))
    specs=((1042,220,"local_debug"),(2026,220,"local_debug"),
           (1042,220,"random"))
    summaries=[]
    for seed,limit,policy in specs:
        name=f"seed{seed}-{policy}"
        print("QC012_BEGIN="+name,flush=True)
        summaries.append(run(seed,limit,policy,root/name))
    (root/"comparison.json").write_text(
        json.dumps({"runs":[{k:v for k,v in s.items() if k!="milestones"}
                            for s in summaries],
                    "equivalent_observations":False,
                    "not_a_comparative_performance_claim":True,
                    "real_game_steps":sum(s["real_engine_steps"] for s in summaries),
                    "world_actions":0},indent=2,sort_keys=True)+"\n")
    print("QC012_COMPLETE="+json.dumps({
        "total_game_steps":sum(s["real_engine_steps"] for s in summaries),
        "achievements":[len(s["achievements"]) for s in summaries]}),flush=True)


if __name__=="__main__":
    main()
