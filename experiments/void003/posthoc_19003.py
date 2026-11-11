"""Explicitly POST-HOC: rerun the old VOID-002 19003 wide-exploration case.

It is NOT a new test seed or part of VOID-003 primary six-seed comparison.
"""
from __future__ import annotations
from pathlib import Path
import json
import two_run
from memory import seal

SEED=19003  # already scored in VOID-002, never held out for VOID-003
def diagnostic():
    two_run.DEV_SEEDS=tuple(two_run.DEV_SEEDS)+(SEED,)
    m=two_run.game_episode(SEED,"motif003",stage="scout")
    c=two_run.game_episode(SEED,"classical_2ply",stage="scout")
    f0=two_run.game_episode(SEED,stage="followup")
    fm=two_run.game_episode(SEED,followup_memory=m["map_memory_packet"],stage="followup")
    fc=two_run.game_episode(SEED,followup_memory=c["map_memory_packet"],stage="followup")
    mm={tuple(row[0]) for row in m["map_memory_packet"]["historical_cells"]}
    cm={tuple(row[0]) for row in c["map_memory_packet"]["historical_cells"]}
    out={"status":"POST_HOC_KNOWN_OLD_SEED_NOT_HELDOUT",
         "original_question":"Does the already noticed high-coverage first run improve a second run via its remembered historical map?",
         "seed":SEED,"source":"CRAFTER_1_8_3_UNMODIFIED_RESET",
         "scout_seen_motif":len(mm),"scout_seen_classical":len(cm),
         "motif_exclusive":len(mm-cm),"classical_exclusive":len(cm-mm),
         "second_round_goal_counts":{"no_memory":f0["goal_count"],"motif_memory":fm["goal_count"],"classical_memory":fc["goal_count"]},
         "second_round_actions":{"no_memory":f0["actions"],"motif_memory":fm["actions"],"classical_memory":fc["actions"]},
         "two_run_net":{"motif_memory":two_run.net(m,fm),"classical_memory":two_run.net(c,fc),
                        "motif_no_memory":two_run.net(m,f0),"classical_no_memory":two_run.net(c,f0)},
         "waypoint_steps":{"motif_memory":fm["used_historical_waypoint_steps"],
                           "classical_memory":fc["used_historical_waypoint_steps"]},
         "full_records":{"scouts":{"motif003":m,"classical_2ply":c},
                         "followups":{"no_memory":f0,"motif_memory":fm,"classical_memory":fc}},
         "real_world_actions":0,"not_confirmatory":True}
    out["seal"]=seal(out)
    return out

if __name__=="__main__":
    out=diagnostic()
    p=Path(two_run.ROOT)/"void003-posthoc-seed19003.json"
    p.write_text(json.dumps(out,sort_keys=True,indent=2)+"\n")
    print(json.dumps({k:v for k,v in out.items() if k!="full_records"},sort_keys=True,indent=2))
