"""ACTUAL T5 Observer/Critic/Hypeman beside the Fellowship native planner.

Production-like 021F sidecar returns on a bounded grace period. This isolated
research harness then explicitly joins the in-flight CPU worker BEFORE the
Python interpreter tears down torch state, preventing unsafe C++ daemon
thread shutdown when the native plan finished first.

All displayed notes are frozen at the original deadline; late commentary is
not retroactively promoted into the native result or its sidecar notes.
"""
from __future__ import annotations
from dataclasses import asdict
import json
from pathlib import Path
import sys
import threading
import time

ROOT = Path(__file__).resolve().parents[1]
for folder in ("020f","021f"):
    sys.path.append(str(ROOT / folder))

from chorus import LocalFlanT5Small, parallel_critique
from demo import sample_projection
from fellowship_operator_update import analyze


def run():
    import torch
    torch.set_num_threads(2)
    backend = LocalFlanT5Small()
    started = time.monotonic()
    backend._prepare()
    loaded = time.monotonic()
    result = parallel_critique(
        analyze,
        sample_projection(),
        backend,
        sidecar_grace_seconds=3.,
    )
    after = time.monotonic()
    workers = [t for t in threading.enumerate()
               if t.name == "motif-local-text-sidecar"]
    for worker in workers:
        worker.join(timeout=30)
    terminated = all(not t.is_alive() for t in workers)
    if not terminated:
        raise RuntimeError("HOLD_STILL_RUNNING_GPU_OR_CPU_WORKER_AT_EXIT")
    return {
        "schema":"motif023f.real-three-role-chorus/v0",
        "model":"google/flan-t5-small",
        "model_weights_really_loaded":backend._model is not None,
        "model_load_seconds":round(loaded-started,3),
        "frozen_result_before_worker_join":{
            "native_wall_ms":result.native_wall_ms,
            "end_to_end_wall_ms":result.end_to_end_wall_ms,
            "sidecar_completed_at_return":result.sidecar_completed,
            "roles":[asdict(n) for n in result.notes],
            "all_three_available_at_cutoff":all(
                n.status=="UNVERIFIED_TEXT_AVAILABLE" for n in result.notes
            ),
        },
        "worker_finished_safely":terminated,
        "cleanup_join_seconds":round(time.monotonic()-after,3),
        "original_native_decision_unmodified":True,
        "venue_permission_still_only_user_report":result.native["observation"]["venue_use_permission"],
        "planz_still_index_only":result.native["source_planz"]["authority"]=="INDEX_ONLY",
        "real_world_actions":False,
        "notes_are_unverified_not_facts":True,
    }

if __name__=="__main__":
    print(json.dumps(run(),indent=2,sort_keys=True))
