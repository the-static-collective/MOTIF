"""Emit a complete public, synthetic proof-carrying answer and re-entry receipt."""
import json
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
for family in ("thought-025","thought-026","thought-027","thought-028"):
    sibling = str(HERE.parent / family)
    if sibling not in sys.path:
        sys.path.insert(0, sibling)
sys.path.insert(0, str(HERE))

from specimens import BY_KEY
from memory_benchmark import seeds, new_cases
from weave import investigate
from answer_weave import first_answer, reenter, investigate_new_task

def run():
    task = BY_KEY["cancel_or_add"]
    store = seeds()
    discovered = investigate(task, store, mode="compose")
    inputs = {n:v for (n,_),v in zip(task.fields,(3,5))}
    node = first_answer(task,store,discovered,inputs)
    restored = reenter(json.loads(json.dumps(node)),store.registry)
    transfer = investigate_new_task(node, store.registry, new_cases()["toggle_equipment"])
    return {
        "schema": "motif.collective001.demonstration.v1",
        "type": "SYNTHETIC_ONLY",
        "initial_development_queries": discovered["development_queries"],
        "reentry_new_development_queries": restored["new_development_queries"],
        "reentry_still_performed_full_verification": restored["full_owner_proof_recheck_still_required"],
        "new_task_development_queries": transfer["development_queries"],
        "new_task_certified_by_old_proof_alone": False,
        "answer_node": node,
        "new_task_inquiry_status": transfer["status"],
        "external_authority": "NONE",
    }

if __name__ == "__main__":
    print(json.dumps(run(),indent=2,sort_keys=True))
