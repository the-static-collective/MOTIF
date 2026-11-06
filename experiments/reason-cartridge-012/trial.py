"""Tiny real-opinion excerpt evaluation, not full-document NLP or legal advice."""
from __future__ import annotations

from pathlib import Path
import json

from corpus import OPINIONS,passages
from classifier import fit,validate,classify,feature,pin_source
from receiver import Receiver
from review_keys import labeled_training,LABELS
from bridge011 import evaluate


def trained():
    raw=fit(labeled_training())
    review=Receiver(raw)
    receipt=review.preview(passages(False))
    if receipt["errors"]==0:
        review.admit("ADMIT_READ_ONLY",receipt["review_digest"])
    return raw,review,receipt


def run(directory=None):
    raw,receiver,review=trained()
    method=validate(raw)
    bridge=evaluate(receiver)
    heldout=passages(False)
    baseline=sum(LABELS[fragment["span_id"]][0]=="LEGAL_TREATMENT"
                 for fragment in heldout)
    result={
        "schema":"motif.reason.real-opinion-excerpts.v1",
        "trained_on_opinions":[key for key,v in OPINIONS.items() if v["train"]],
        "strictly_new_heldout_opinions":[key for key,v in OPINIONS.items() if not v["train"]],
        "number_of_short_verbatim_source_fragments":len(passages(True)+heldout),
        "training_fragments":len(passages(True)),
        "heldout_fragments":len(heldout),
        "learned_cue_to_epistemic_type":method["learned_feature_routes"],
        "unlearned_fact_issue_feature":"F_E",
        "heldout_correct_accepted":review["correct_accepted"],
        "heldout_correct_abstained":review["correct_abstentions"],
        "heldout_errors":review["errors"],
        "naive_always_legal_holdout_correct":baseline,
        "strong_classical_predefined_typed_cue_baseline_may_tie":True,
        "quoted_text_not_full_opinion":True,
        "live_source_quote_verification_in_CI":False,
        "new_court_opinion_human_paraphrase_labels":True,
        "curated_issue_polarity_not_inferred_from_unstructured_text":True,
        "heldout_assessments":review["outcomes"],
        "typed_bridge":bridge,
        "source_corpus_blob":pin_source(),
        "classifier_sha256":method["checksum_sha256"],
        "independent_review_digest":review["review_digest"],
        "external_actions":False,"real_world_authority":False,
    }
    four=bridge["four_value_propositions"]
    if (review["correct_accepted"]!=3 or review["correct_abstentions"]!=1
            or four["NARUTO/ARTICLE_III_STANDING"]["four_value"]!="SUPPORTED"
            or four["NARUTO/COPYRIGHT_STATUTORY_STANDING"]["four_value"]!="REFUTED"
            or four["COCA/CAFFEINE_ADDED_INGREDIENT"]["four_value"]!="SUPPORTED"
            or four["COCA/CAFFEINE_HARM_PROVEN"]["four_value"]!="UNDETERMINED"
            or four["STAMBOVSKY/PHYSICAL_GHOST_EXISTS"]["four_value"]!="UNDETERMINED"
            or four["ULYSSES/PORNOGRAPHIC_INTENT"]["four_value"]!="REFUTED"):
        raise AssertionError("Changed independently curated legal-epistemic evidence contract")
    if directory:
        p=Path(directory)
        p.mkdir(parents=True,exist_ok=True)
        (p/"type-cartridge.json").write_text(raw,encoding="utf-8")
        (p/"benchmark.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
        (p/"typed-four-value-bridge.json").write_text(
            json.dumps(bridge,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return result


if __name__=="__main__":
    import sys
    if len(sys.argv)>2:
        raise SystemExit("usage: python trial.py [evidence-folder]")
    print(json.dumps(run(sys.argv[1] if len(sys.argv)==2 else None),
                     indent=2,sort_keys=True))
