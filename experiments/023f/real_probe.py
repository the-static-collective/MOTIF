"""Real FLAN-T5-small smoke test: never report success without real weights.

This is deliberately separate from the scripted 022F evaluation. Model
download, if any, is an explicit pre-run action in GitHub Actions. Every
inference in this file is local_files_only=True, no external field actions.
"""
from __future__ import annotations
from pathlib import Path
import json
import sys
import time
sys.path.append(str(Path(__file__).resolve().parents[1] / "021f"))
from chorus import LocalFlanT5Small

def run():
    import torch
    torch.set_num_threads(2)
    backend = LocalFlanT5Small()
    prompts = [
        "Choose the single best test to check an unconfirmed meal for a December gathering. Reply exactly TEST_ID=FOOD_SERVICE_GATE. Options: FOOD_SERVICE_GATE, REPEAT_AUDIO_TEST.",
        "Return exactly one valid line from: TEST_ID=FOOD_SERVICE_GATE or TEST_ID=REPEAT_AUDIO_TEST. Already have audio check. Food service permission is unknown. Best useful next question?",
        "The venue has granted room use. Food permission is not confirmed. Select one test from FOOD_SERVICE_GATE (check food permission) or REPEAT_AUDIO_TEST (duplicate audio check). Output TEST_ID= followed by the name.",
    ]
    started = time.monotonic()
    outputs = []
    for p in prompts:
        t = time.monotonic()
        answer = backend.generate(p)
        outputs.append({
            "prompt":p,"actual_model_response":answer,
            "generation_seconds":round(time.monotonic()-t,3)
        })
    return {
        "actual_inference":True,
        "model":backend.model_id,
        "torch_version":torch.__version__,
        "total_wall_seconds":round(time.monotonic()-started,3),
        "outputs":outputs,
    }
if __name__ == "__main__":
    print(json.dumps(run(),indent=2))
