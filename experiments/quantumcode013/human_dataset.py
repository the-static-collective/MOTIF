"""QC-013: Ingest real human Crafter demonstrations and derive game-only lessons.

Usage: python human_dataset.py /path/to/dataset.zip [--replay 0]
Never fetches remote sources, extracts ZIP paths, runs models, or dispatches acts.
Historical recorded files use the misspelling achivement_*.
Row zero is a placeholder; paired transitions run from row 1 -> row 2 onward.
"""
from __future__ import annotations
import collections
import hashlib
import io
import json
from pathlib import Path
import statistics
import sys
import zipfile
import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"quantumcode011"))
from game_replay import GameState,Episode,Replay,relatte_preview

PUBLIC_SOURCE="https://archive.org/details/crafter_human_dataset"
ACTS=("noop","move_left","move_right","move_up","move_down",
      "do","sleep","place_stone","place_table","place_furnace",
      "place_plant","make_wood_pickaxe","make_stone_pickaxe",
      "make_iron_pickaxe","make_wood_sword","make_stone_sword",
      "make_iron_sword")
MAX_FILES=500
MAX_MEMBER=18_000_000
MAX_BYTES=300_000_000
ACH_PREFIX="achivement_"


def members(z):
    files=sorted([m for m in z.infolist() if not m.is_dir()],
                 key=lambda m:m.filename)
    if (not files or len(files)>MAX_FILES
        or sum(f.file_size for f in files)>MAX_BYTES or
        any(not f.filename.startswith("dataset/") or
            not f.filename.endswith(".npz") or f.file_size>MAX_MEMBER
            for f in files)):
        raise ValueError("Unsafe or unexpected ZIP member inventory")
    return files


def get_stats(a):
    if not {"action","done","inventory_health",
            "inventory_food","inventory_drink"}.issubset(a.files):
        raise ValueError("Required gameplay telemetry absent")
    x=a["action"]
    n=len(x)
    if (n<3 or n>100000 or x.dtype.kind not in "iu" or
        (x<0).any() or (x>=len(ACTS)).any() or len(a["done"])!=n):
        raise ValueError("Bad action series")
    inv=[k for k in a.files if k.startswith("inventory_")]
    ach=[k for k in a.files if k.startswith(ACH_PREFIX)]
    if (not inv or not ach or
        any(len(a[k])!=n for k in inv+ach)):
        raise ValueError("Unaligned telemetry")
    first={}
    for k in ach:
        hit=np.flatnonzero(a[k][1:]>0)
        if hit.size:first[k[len(ACH_PREFIX):]]=int(hit[0]+1)
    return {
        "recorded_actions":n-1,
        "paired_steps":n-2,
        "terminated":bool(a["done"][-1]),
        "health":int(a["inventory_health"][-1]),
        "food":int(a["inventory_food"][-1]),
        "drink":int(a["inventory_drink"][-1]),
        "first":first,
        "actions":dict(collections.Counter(ACTS[int(y)] for y in x[1:])),
    }


def analyze(path):
    path=Path(path)
    if path.stat().st_size>MAX_BYTES:raise ValueError("ZIP too large")
    source_hash=hashlib.sha256(path.read_bytes()).hexdigest()
    samples=[]
    with zipfile.ZipFile(path) as z:
        for m in members(z):
            with np.load(io.BytesIO(z.read(m)),allow_pickle=False) as a:
                samples.append(get_stats(a))
    counts=collections.Counter(k for x in samples for k in x["first"])
    actions=collections.Counter()
    for x in samples:actions.update(x["actions"])
    graph=[]
    for a in sorted(counts):
        for b in sorted(counts):
            if a==b:continue
            present=[s for s in samples if a in s["first"] and b in s["first"]]
            if len(present)<15:continue
            before=[s["first"][b]-s["first"][a] for s in present
                    if s["first"][a]<s["first"][b]]
            if len(before)<12 or len(before)/len(present)<.85:continue
            graph.append({
                "earlier":a,"later":b,"shared":len(present),
                "ordered":len(before),
                "fraction":round(len(before)/len(present),3),
                "median_gap":statistics.median(before),
                "causal_proof":False})
    graph.sort(key=lambda v:(-v["ordered"],-v["fraction"],
                             v["median_gap"],v["earlier"],v["later"]))
    lengths=sorted(x["recorded_actions"] for x in samples)
    return {
        "experiment":"MOTIF-QC013",
        "archive_sha256":source_hash,"source":PUBLIC_SOURCE,
        "episodes":len(samples),
        "recorded_actions":sum(x["recorded_actions"] for x in samples),
        "paired_steps":sum(x["paired_steps"] for x in samples),
        "median_actions":statistics.median(lengths),
        "min_actions":lengths[0],"max_actions":lengths[-1],
        "end_health_zero":sum(x["health"]==0 for x in samples),
        "end_food_zero":sum(x["food"]==0 for x in samples),
        "end_drink_zero":sum(x["drink"]==0 for x in samples),
        "achievements":dict(counts),"actions":dict(actions),
        "ordered_achievement_hypotheses":graph,
        "boundaries":{
            "game_observation_not_human_physiology":True,
            "temporal_precedence_not_causality":True,
            "all_episodes_end_at_death":True,
            "participant_ids_known":False,
            "raw_video_redistributed":False,
            "real_world_actions":0,
        },
    }


def state(a,idx):
    inv=tuple(sorted((k[len("inventory_"):],int(a[k][idx]))
                     for k in a.files if k.startswith("inventory_")))
    ach=tuple(sorted("achievement:"+k[len(ACH_PREFIX):]
                     for k in a.files if k.startswith(ACH_PREFIX)
                     and a[k][idx]>0))
    pos=a["player_pos"][idx]
    return GameState(inv,ach,(),f"GAME_TILE:{int(pos[0])},{int(pos[1])}",idx-1)


def as_replay(blob,source_id,max_steps=240):
    with np.load(io.BytesIO(blob),allow_pickle=False) as a:
        get_stats(a)
        if ("player_pos" not in a.files or
            len(a["player_pos"])!=len(a["action"])):
            raise ValueError("No aligned player position")
        end=min(len(a["action"]),max_steps+2)
        timeline=[]
        for i in range(2,end):
            before=state(a,i-1)
            after=state(a,i)
            gain=set(after.capabilities)-set(before.capabilities)
            timeline.append(Episode(
                f"{source_id}:step{i-1}","OTHER_GAME","GAME_TELEMETRY",
                f"{PUBLIC_SOURCE}#{source_id}:row{i}","OWNER_PROVIDED",
                i-2,i-1,ACTS[int(a["action"][i])],
                before,after,"SUCCESS" if gain else "INCONCLUSIVE",
                "Recorded action and in-game state only; action time is an "
                "ordinal tick rather than a video second; motive unknown.",
                "OBSERVED",("OBSERVED_GAME",)))
    replay=Replay("OTHER_GAME",tuple(timeline),
                  f"{PUBLIC_SOURCE}#{source_id};expert_gameplay",True)
    replay.validate()
    return replay


def preview(path,index=0):
    with zipfile.ZipFile(path) as z:
        selected=members(z)
        if index<0 or index>=len(selected):raise ValueError("Invalid index")
        blob=z.read(selected[index])
    clip_id=hashlib.sha256(blob).hexdigest()[:16]
    replay=as_replay(blob,clip_id)
    crossing=relatte_preview(replay)
    return {
        "source_clip_sha256":hashlib.sha256(blob).hexdigest(),
        "replay_sha256":replay.pin,
        "paired_events":len(replay.episodes),
        "capability_events":sum(bool(set(e.after.capabilities)-
                                      set(e.before.capabilities))
                                 for e in replay.episodes),
        "reLATTE":"HOLD_FOR_SEPARATE_RELATTE_OWNER_REVIEW",
        "crossing_sent":False,"real_world_actions":0,
    }


if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("archive")
    p.add_argument("--replay",type=int,default=None)
    args=p.parse_args()
    result=analyze(args.archive) if args.replay is None else preview(args.archive,args.replay)
    print(json.dumps(result,sort_keys=True,indent=2))
