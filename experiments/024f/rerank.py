"""MOTIF-024F: native prefilter -> REAL FLAN-T5-small advisory reranking.

Native 022F + 016 checks *both* registered options first. The small model
never sees rejected candidates, never runs a physical sensor, never modifies
facts or permissions. A constrained token trie ensures it can only return
one already vetted native ID. We evaluate the advice in SHADOW, not deploy it.
"""
from __future__ import annotations

from dataclasses import asdict
import json
import re
import time

from model_backend import permitted_sequences, allowed_next
from native import TwinCase, NativeShortlist


def risk_score(note: str) -> int:
    """Independent, strong lexical heuristic baseline with identical notes.

    This classifier is deliberately explicit: measure it head-to-head rather
    than choosing only a weak random or naive alphabetical comparator.
    No corpus training, model inference or approval is implied.
    """
    x=" ".join(note.lower().split())
    bad = (
        "sporadic interference", "readings fluctuated", "unscheduled controller reset",
        "loose connector", "firmware changed", "timestamp mismatch",
        "no follow-up verification", "declared the signal perfect",
    )
    good = (
        "spot observations stayed consistent", "repeated spot observations stayed consistent",
        "consistent signal", "matching spot measurements", "no new faults",
        "repeated tests agreed", "timing remained consistent",
        "later checks stayed consistent", "later repeated observations agreed",
        "no new failure is documented", "independent recent checks agreed",
        "no externally verified anomaly",
    )
    return 2*sum(token in x for token in bad)-sum(token in x for token in good)


def lexical_rule(case: TwinCase) -> str:
    scores={"PROBE_ALPHA":risk_score(case.alpha_note),
            "PROBE_BETA":risk_score(case.beta_note)}
    return min(scores,key=lambda x:(scores[x],x))


def prompt(case: TwinCase, shortlist: NativeShortlist, *, reverse: bool = False) -> str:
    if len(shortlist.eligible_ids)<2:
        raise ValueError("HOLD_NO_ACTUAL_RERANK_CHOICE")
    ids=tuple(reversed(shortlist.eligible_ids)) if reverse else shortlist.eligible_ids
    notes={"PROBE_ALPHA":case.alpha_note,"PROBE_BETA":case.beta_note}
    choices="\n".join(f"{name}: {notes[name]}" for name in ids)
    # The notes are unverified and are NOT authentic field evidence.
    return (
        "In an invented experiment, two independent tests passed the SAME "
        "earlier calibration and have equal information gain and cost. "
        "Their latest UNVERIFIED maintenance descriptions may indicate a "
        "post-calibration failure. Select the source most likely to stay "
        "accurate under future change. A real observer, not you, will "
        "measure the future outcome. Reply with ONLY one registered ID.\n"
        "Proposed instruments:\n"+choices+
        "\nWhich measurement would you trust more for the next synthetic test? "
        "Format exactly TEST_ID=PROBE_ALPHA or TEST_ID=PROBE_BETA."
    )


def rerank_with_real_model(model, case: TwinCase,
                           shortlist: NativeShortlist, *, reverse=False):
    """Typed inference: real FLAN-T5 next-token scores, never fuzzy name fix."""
    if len(shortlist.eligible_ids)<2:
        return {"status":"BYPASS_NO_TIE","selected":shortlist.native_choice,
                "actual_model_called":False,"latency_seconds":0.}
    import torch
    model._prepare()
    tokenizer=model._tokenizer
    network=model._model
    ids=shortlist.eligible_ids
    seqs=permitted_sequences(tokenizer,ids,allow_abstain=False)
    p=prompt(case,shortlist,reverse=reverse)
    tokens=tokenizer(p,return_tensors="pt",max_length=384,truncation=True)
    decoder_start=network.config.decoder_start_token_id
    eos=tokenizer.eos_token_id
    if not isinstance(decoder_start,int):
        raise ValueError("HOLD_UNAVAILABLE_DECODER_START")
    def allowed(_batch_index, decoder_ids):
        prefix=tuple(decoder_ids.tolist())
        if prefix and prefix[0]==decoder_start:
            prefix=prefix[1:]
        return allowed_next(prefix,seqs,eos)
    start=time.monotonic()
    with torch.inference_mode():
        out=network.generate(
            **tokens, num_beams=2, do_sample=False,
            prefix_allowed_tokens_fn=allowed,
            max_new_tokens=max(len(x) for x in seqs)+2,
            early_stopping=True,
        )
    elapsed=time.monotonic()-start
    tokens_observed=tuple(out[0].tolist())
    if tokens_observed and tokens_observed[0]==decoder_start:
        tokens_observed=tokens_observed[1:]
    if tokens_observed not in seqs:
        return {
            "status":"HOLD_OUT_OF_REGISTERED_TOKEN_TRIE",
            "selected":shortlist.native_choice,
            "actual_model_called":True,
            "latency_seconds":round(elapsed,4),
            "raw_decode":tokenizer.decode(out[0],skip_special_tokens=True)[:240],
        }
    answer=seqs[tokens_observed]
    selected=answer.removeprefix("TEST_ID=")
    if selected not in ids:
        raise ValueError("HOLD_MODEL_OUTPUT_NOT_NATIVE_REVIEWED")
    return {
        "status":"UNVERIFIED_ADVISORY_RANK",
        "selected":selected,
        "actual_model_called":True,
        "latency_seconds":round(elapsed,4),
        "raw_decode":tokenizer.decode(out[0],skip_special_tokens=True)[:240],
        "canonical":answer,
        "prompt_chars":len(p),
    }
