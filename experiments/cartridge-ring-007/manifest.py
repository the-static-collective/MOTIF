"""RING-007: precommit a bounded investigate-or-abstain route for new cases.

No hidden label, author tag, or old training score is mounted to native code.
Each new utterance gets one of:
  FAMILIAR          → already reviewed RING-005 selective method route
  PRECHECK_HOLD     → prior evidence invalid, no native methods
  BLOCK             → new effect/distribution risk, no native methods
  UNCERTAIN         → unexplained language, no native methods
  INVESTIGATE       → reviewed *read-only* path-question frame; native THOUGHT
                       probe plus source-owned graph/measurement as needed

The original human utterance is retained in evidence. A different canonical
input is a separate, provenance-marked *hypothesis* about one synthetic task.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"cartridge-ring-006"))
import sentinel
sys.path.insert(0,str(HERE.parent/"cartridge-ring-005"))
import adaptive, policy
import arbitration,frames

SCHEMA="motif.ring007.reviewed-investigation-manifest.v1"
STRATEGY="ROUTE_VIA_SOURCE_REVIEW_AND_SAFE_CANONICALIZATION"

class HOLD(ValueError):
    pass


def digest(v):
    return sha256(json.dumps(v,sort_keys=True,separators=(",",":"),
                             ensure_ascii=True,allow_nan=False).encode()).hexdigest()


def make(frozen,profile,decision,public):
    arbitration.validate(frozen,profile,decision)
    if public.get("schema")!="motif.shared-evidence-public.v1":
        raise HOLD("Wrong common input schema")
    prior=adaptive.manifest_for(frozen,public)
    routes=[]
    for case,source in zip(public["cases"],prior["routes"]):
        original_frame=frames.review(case["utterance"])
        original_context=source["context"]
        original_route=source["route"]
        if original_frame["verdict"]=="BLOCK":
            # Always block explicit risk, including when old legacy case
            # classification would have incorrectly returned CUT or REPAIR.
            kind="BLOCK"
            reason=original_frame["reason"]
            source_route=None
            canonical=None
        elif original_context=="HOLD":
            kind="PRECHECK_HOLD"
            reason="INVALID_OR_UNTRUSTED_DECLARED_RECORDS_OR_OLD_EFFECT_WORD"
            source_route=None
            canonical=None
        elif not sentinel.is_novel(profile,case):
            kind="FAMILIAR"
            reason="PRESENT_IN_FROZEN_TRAINING_LANGUAGE_PROFILE"
            source_route=original_route
            canonical=None
        elif (decision["selected"]=="TRIAGE" and
              original_frame["verdict"]=="EXPLORE"):
            kind="INVESTIGATE"
            reason="TYPED_READ_ONLY_SOURCE_QUESTION_WITH_CANONICAL_HYPOTHESIS"
            source_route=original_route
            canonical=frames.CANONICAL
        else:
            kind="UNCERTAIN"
            reason="UNREVIEWED_SEMANTICS_OR_BLANKET_FALLBACK"
            source_route=None
            canonical=None
        routes.append({
            "id":case["id"],
            "kind":kind,
            "reason":reason,
            "original_input_sha256":original_frame["input_sha256"],
            "review":original_frame,
            "original_context":original_context,
            "source_route":source_route,
            "requires_proof":source["requires_proof"],
            "canonical_utterance":canonical,
            "source_graph_ids_unmodified":True,
            "no_implicit_runtime_authority":True,
        })
    result={
        "schema":SCHEMA,
        "public_digest_sha256":digest(public),
        "frozen_policy_receipt_sha256":frozen["receipt_sha256"],
        "original_profile_receipt_sha256":profile["receipt_sha256"],
        "strategy_receipt_sha256":decision["receipt_sha256"],
        "selected_strategy":decision["selected"],
        "routes":routes,
        "prepared_before_native_inference":True,
        "hidden_scoring_labels_included":False,
        "source_method_registry_mutated":False,
        "outside_effects_permitted":False,
        "authority":"NONE",
    }
    result["receipt_sha256"]=digest(result)
    return result
