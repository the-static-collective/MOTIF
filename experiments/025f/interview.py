"""MOTIF-025F — ACTUAL tiny-model job interview after classical preflight.

Question: Can FLAN-T5-small add any value over a same-evidence native baseline
as observer, critic or 'safe next step' assistant? Doing nothing (NO_T5) is
a first-class, cost-zero outcome. Model outputs NEVER become event permission.

One precommitted 36-case evaluation; fixed decoder, frozen checkpoint.
Second candidate-order-reversal pass probes answer-label preference. No
fine-tuning, data-dependent prompt alteration or model retraining.
"""
from __future__ import annotations

from dataclasses import asdict
import json
import os
from pathlib import Path
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
for rel in ("021f","023f","025f"):
    p=str(ROOT/rel)
    if p not in sys.path:sys.path.append(p)

from chorus import LocalFlanT5Small
from model_backend import permitted_sequences, allowed_next
from frozen_jobs import CASES, JOBS, frozen_digest
from native_careers import preflight_research_menu, native_rule, choose_job


def real_t5_label(model: LocalFlanT5Small, job, note: str, *, reversed_order: bool = False):
    """Use the actual public frozen checkpoint logits, never a fake T5 label."""
    import torch
    tokenizer=model._tokenizer
    network=model._model
    ids=tuple(reversed(job.labels)) if reversed_order else job.labels
    seqs=permitted_sequences(tokenizer,ids,allow_abstain=False)
    instruction=(
        "Classify this fictional operator note. Do not invent a permission, "
        "person, completed action or future event. "
        "Choose the one category best supported by the note. "
        "This is a READ-ONLY experimental classification; no action follows.\n"
        "TASK: "+job.question+"\n"
        "NOTE: "+json.dumps(note,ensure_ascii=False)+"\n"
        "REGISTERED_LABELS: "+", ".join(ids)+"\n"
        "Reply with exactly TEST_ID=<REGISTERED_LABEL> and nothing else."
    )
    inputs=tokenizer(instruction,return_tensors="pt",
                     max_length=384,truncation=True)
    decoder_start=network.config.decoder_start_token_id
    eos=tokenizer.eos_token_id
    if not isinstance(decoder_start,int):
        raise ValueError("HOLD_DECODER_MISSING_START")
    def allowed(_batch_id, output_ids):
        current=tuple(output_ids.tolist())
        if current and current[0]==decoder_start:
            current=current[1:]
        return allowed_next(current,seqs,eos)
    start=time.monotonic()
    with torch.inference_mode():
        result=network.generate(
            **inputs, num_beams=2, do_sample=False,
            prefix_allowed_tokens_fn=allowed,
            max_new_tokens=max(len(k) for k in seqs)+2,
            early_stopping=True,
        )
    latency=time.monotonic()-start
    tokens=tuple(result[0].tolist())
    if tokens and tokens[0]==decoder_start:
        tokens=tokens[1:]
    if tokens not in seqs:
        raise ValueError("HOLD_INVALID_MODEL_TOKENS")
    packet=seqs[tokens]
    choice=packet.split("=",1)[1]
    if choice not in job.labels:
        raise ValueError("HOLD_UNREGISTERED_MODEL_CLASS")
    return choice, round(latency,4),packet


def perform():
    import torch
    torch.set_num_threads(2)
    preflight=preflight_research_menu()
    begin=time.monotonic()
    model_path=os.environ.get("MOTIF_FLAN_MODEL_DIR","google/flan-t5-small")
    model=LocalFlanT5Small(model_path)
    model._prepare()
    loaded=time.monotonic()
    job_map={x.id:x for x in JOBS}
    results={job.id:[] for job in JOBS}
    reversed_results={job.id:[] for job in JOBS}
    for case in CASES:
        job=job_map[case.job]
        original=real_t5_label(model,job,case.note)
        swapped=real_t5_label(model,job,case.note,reversed_order=True)
        rules=native_rule(job,case.note)
        # Frozen gold label and native baseline never enter the prompt.
        for output,destination in ((original,results),(swapped,reversed_results)):
            choice,latency,raw=output
            destination[job.id].append({
                "case_id":case.id,"job":case.job,"gold":case.gold,
                "native":rules,"selected":choice,"seconds":latency,
                "raw_t5_model_tokens":raw,
                "model_changed_native_label":choice!=rules,
                "model_correct":choice==case.gold,
            })
    verdict=choose_job(results)
    swapped_verdict=choose_job(reversed_results)
    original_flat=[x for group in results.values() for x in group]
    swapped_flat=[x for group in reversed_results.values() for x in group]
    by_case={x["case_id"]:x for x in swapped_flat}
    changed=sum(x["selected"]!=by_case[x["case_id"]]["selected"]
                for x in original_flat)
    return {
        "schema":"motif025f.t5-job-interview/0",
        "actual_t5_weights_executed":model._model is not None,
        "model":"google/flan-t5-small",
        "model_revision":os.environ.get("MOTIF_FLAN_REVISION","UNPINNED_LOCAL_CACHE"),
        "frozen_case_digest":frozen_digest(),
        "research_plan_before_model_run":preflight,
        "real_model_load_seconds":round(loaded-begin,4),
        "real_model_calls":2*len(CASES),
        "generation_seconds_total":round(sum(
            x["seconds"] for group in (*results.values(),*reversed_results.values())
            for x in group
        ),4),
        "wall_seconds_total":round(time.monotonic()-begin,4),
        "main_label_decisions":results,
        "reversed_label_decisions":reversed_results,
        "changed_choice_when_labels_reversed":changed,
        "original_order_native_job_verdict":asdict(verdict),
        "reversed_order_native_job_verdict":asdict(swapped_verdict),
        "role_assignment_or_human_permission_automated":False,
        "no_user_file_or_live_source_used":True,
        "all_cases_synthetic":True,
        "note":"Original and reverse are two diagnostics, not independent holdout datasets. No real field claim is made.",
    }


if __name__=="__main__":
    print(json.dumps(perform(),indent=2,sort_keys=True))
