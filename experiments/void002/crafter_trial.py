"""VOID-002: compare real game outcomes on unmodified seeded Crafter worlds.

Zero network/service/model calls. Simulator is third-party Crafter 1.8.3.
Same source-pinned QC-017 BFS for all visible goals. Only exploration differs.
"""
from __future__ import annotations
from collections import Counter
from pathlib import Path
import hashlib
import importlib.metadata
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PINNED = ROOT / "sources" / "qc017" / "experiments"
for path in (PINNED / "quantumcode017", PINNED / "quantumcode012"):
    sys.path.insert(0, str(path))
from frontier import choose, POLICIES

DEV_SEEDS = (1042, 2026, 3199, 8765)
HOLDOUT_SEEDS = (19001, 19003, 19007, 19009, 19013, 19021)
MAX_ACTIONS = 70
SOURCE_PIN = "7e35ab7157755c83c6353e939a2ae1b018d70667"


def source_modules():
    from plan import observe, traverse, check_goals
    from play_crafter import ACTS, Controller
    return observe, traverse, check_goals, ACTS, Controller


def seal(obj):
    return hashlib.sha256(json.dumps(
        obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def game_run(seed, policy):
    if policy not in POLICIES or seed not in DEV_SEEDS + HOLDOUT_SEEDS:
        raise ValueError("UNREGISTERED_BENCHMARK_ARGUMENT")
    import crafter
    if importlib.metadata.version("crafter") != "1.8.3":
        raise RuntimeError("CRAFTER_VERSION_MISMATCH")
    observe, traverse, check_goals, ACTS, Controller = source_modules()
    env = crafter.Env(seed=seed, length=MAX_ACTIONS, view=(9, 9), size=(64, 64))
    env.reset()
    actor = Controller(seed)
    if env._player not in env._world.objects:
        raise RuntimeError("GAME_PLAYER_NOT_ACTIVE")
    visited = Counter()
    seen = set()
    success = {"game_wood_obtained": False, "game_drink_obtained": False}
    actions = []
    no_effect = 0
    first_error = None
    for tick in range(MAX_ACTIONS):
        goal = next((g for g in success if not success[g]), None)
        if goal is None:
            break
        belief = observe(env, actor,
                         f"crafter:1.8.3:seed{seed}:turn{tick}:privileged-r7")
        seen.update(c.xy for c in belief.cells)
        visited[belief.start] += 1
        planned = traverse(belief, goal)
        if planned.status == "PLAN_CANDIDATE":
            action = planned.actions[0]
            reason = "SHARED_CLASSICAL_BFS_ROUTE_TO_OBSERVED_RESOURCE"
        else:
            action = choose(belief, seen, visited, policy)
            reason = f"{policy}:EXPLORATORY_INFORMATION_ACTION"
        if action is None:
            break
        if action not in ACTS:
            raise RuntimeError("UNKNOWN_GAME_ACTION")
        inv_before = dict(env._player.inventory)
        ach_before = dict(env._player.achievements)
        pos_before = tuple(int(x) for x in env._player.pos)
        facing_before = tuple(int(x) for x in env._player.facing)
        _, reward, done, info = env.step(ACTS.index(action))
        inv_after = dict(info["inventory"])
        ach_after = dict(info["achievements"])
        pos_after = tuple(int(x) for x in env._player.pos)
        facing_after = tuple(int(x) for x in env._player.facing)
        verified = check_goals(inv_before, inv_after, ach_before, ach_after, goal)
        if verified != "GOAL_NOT_YET_WITNESSED":
            success[goal] = True
        changed = (pos_after != pos_before or facing_after != facing_before
                   or inv_after != inv_before or ach_after != ach_before)
        no_effect += int(not changed)
        receipt = {
            "tick": tick + 1, "goal": goal, "action": action,
            "reason": reason, "sensor_pin": belief.pin,
            "observed_terrain_count": len(belief.cells),
            "planned_status": planned.status,
            "before_pos": pos_before, "after_pos": pos_after,
            "before_facing": facing_before, "after_facing": facing_after,
            "before_target_resource": int(inv_before.get(
                "wood" if "wood" in goal else "drink", 0)),
            "after_target_resource": int(inv_after.get(
                "wood" if "wood" in goal else "drink", 0)),
            "verified_goal_outcome": verified, "changed_in_engine": changed,
            "terminal": bool(done), "game_reward": float(reward),
        }
        receipt["sha256"] = seal(receipt)
        actions.append(receipt)
        if not changed and first_error is None:
            first_error = tick + 1
        if done:
            break
    k = len(actions)
    goals = sum(success.values())
    net = goals - .1 * k / MAX_ACTIONS - .05 * no_effect / MAX_ACTIONS
    result = {
        "seed": seed,
        "split": "development" if seed in DEV_SEEDS else "heldout",
        "policy": policy, "engine": "ACTUAL_UNMODIFIED_CRAFTER_1_8_3",
        "goals_witnessed": success, "total_goal_count": goals,
        "game_actions": k, "no_effect_actions": no_effect,
        "first_no_effect_tick": first_error,
        "net_score": round(net, 9),
        "newly_observed_positions": len(seen), "game_actions_only": True,
        "real_world_actions": 0,
        "no_engine_world_mutations_by_research_runner": True,
        "privileged_radius_seven_source_sensor": True,
        "source_dependency_sha": SOURCE_PIN, "action_receipts": actions,
    }
    result["sha256"] = seal(result)
    return result


def aggregate(rows, split):
    subset = [r for r in rows if r["split"] == split]
    return {policy: {
        "episodes": sum(r["policy"] == policy for r in subset),
        "witnessed_goals": sum(r["total_goal_count"] for r in subset
                               if r["policy"] == policy),
        "total_steps": sum(r["game_actions"] for r in subset
                           if r["policy"] == policy),
        "no_effect_steps": sum(r["no_effect_actions"] for r in subset
                               if r["policy"] == policy),
        "mean_net": round(sum(r["net_score"] for r in subset
                              if r["policy"] == policy) /
                          max(1, sum(r["policy"] == policy for r in subset)), 9)
    } for policy in POLICIES}


def benchmark():
    rows = [game_run(seed, policy) for seed in DEV_SEEDS + HOLDOUT_SEEDS
            for policy in POLICIES]
    result = {
        "experiment": "VOID-002",
        "status": "REAL_CRAFTER_UNMODIFIED_WORLD_TRIAL_NOT_GENERAL_AI",
        "source_dependency_sha": SOURCE_PIN,
        "development": aggregate(rows, "development"),
        "heldout": aggregate(rows, "heldout"),
        "episode_count": len(rows),
        "actions_witnessed": sum(r["game_actions"] for r in rows),
        "model_calls": 0, "paid_services": 0,
        "controlling_algorithm":
            "SAME_SOURCE_PINNED_QC017_CLASSICAL_BFS_FOR_VISIBLE_GOALS",
        "policies": POLICIES, "rows": rows,
    }
    result["sha256"] = seal(result)
    return result


if __name__ == "__main__":
    output = benchmark()
    path = ROOT / "void002-crafter-audit.json"
    path.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: v for k, v in output.items() if k != "rows"},
                     indent=2, sort_keys=True))
