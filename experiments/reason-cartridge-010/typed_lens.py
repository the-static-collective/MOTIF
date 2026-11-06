"""REASON-010: discover a typed applicability operator from odd court cases.

This is *not* a legal reasoning LLM, argument interpretation or legal advice.
Training derives a minimal metadata/epistemic selector from hand-curated
historical opinion cards and clearly simulated adversarial distractors.
It is intentionally narrow but its counterexamples are independently replayed.
"""
from __future__ import annotations

from hashlib import sha1,sha256
from itertools import combinations
from pathlib import Path
import json

SOURCE=Path(__file__).with_name("casebook.py")
SOURCE_BLOB="d9d605e95c1179873e17563a871443f9012a0ef7"
SCHEMA="motif.reason.strange-law.typed-operator.v1"
FIELDS=("case_id","issue","voice","kind","layer","source_status")
REVISION="motif.reason.strange-law-curated-opinions.v1"
MAX_PACKET=50000


class HOLD(ValueError):
    pass


def digest(value):
    return sha256(json.dumps(value,sort_keys=True,separators=(",",":"),
                             ensure_ascii=True,allow_nan=False).encode()).hexdigest()


def pin():
    raw=SOURCE.read_bytes()
    current=sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
    if current!=SOURCE_BLOB:
        raise HOLD("Curated opinion source changed. Re-review each judicial holding.")
    return current


def checks(guards,scenario):
    if not isinstance(guards,(tuple,list)) or any(g not in FIELDS for g in guards):
        raise HOLD("Unbounded or unknown typed operator")
    if any(not isinstance(card,dict) for card in scenario.cards):
        raise HOLD("Invalid evidence cards")
    return tuple(card for card in scenario.cards if all(
        card.get(field)==scenario.query[field] for field in guards))


def select(guards,scenario):
    options=checks(guards,scenario)
    if len(options)!=1:
        return {"status":"HOLD_AMBIGUOUS_OR_MISSING", "selected":None,
                "matching_count":len(options),"real_world_authority":False}
    return {"status":"PROPOSE_HISTORICAL_SOURCE_CARD",
            "selected":options[0],
            "matching_count":1,
            "real_world_authority":False}


def _encode(scenario):
    return {"id":scenario.id,"query":scenario.query,
            "options":list(scenario.cards),"expected":scenario.expected}


def _decode(x):
    if not isinstance(x,dict) or set(x)!={"id","query","options","expected"}:
        raise HOLD("Unsupported teaching record")
    from tasks import Scenario
    if (not isinstance(x["options"],list) or not isinstance(x["query"],dict)):
        raise HOLD("Malformed training row")
    return Scenario(x["id"],x["query"],tuple(x["options"]),x["expected"])


def consistent(guards,rows):
    return all(select(guards,s)["selected"] is not None and
               select(guards,s)["selected"]["id"]==s.expected for s in rows)


def fit(training):
    pin()
    if (not isinstance(training,tuple) or len(training)<4
            or len({s.id for s in training})!=len(training)
            or any(s.id.startswith(("NARUTO","PIERSON")) for s in training)):
        raise HOLD("Teaching cases cannot contain sealed legal-domain evaluations")
    possibilities=tuple(tuple(combo) for size in range(1,len(FIELDS)+1)
                        for combo in combinations(FIELDS,size))
    survivors=tuple(program for program in possibilities
                    if consistent(program,training))
    if not survivors:
        raise HOLD("No trusted type guard can explain the source contrasts")
    minimal_size=len(survivors[0])
    minimal=tuple(p for p in survivors if len(p)==minimal_size)
    if len(minimal)!=1:
        raise HOLD("Multiple indistinguishable minimal legal scope operators")
    chosen=minimal[0]
    # Each gate is justified by a falsifying contrast, not merely asserted.
    witnesses=[]
    for gate in chosen:
        altered=tuple(x for x in chosen if x!=gate)
        failed=next((s for s in training if not consistent(altered,(s,))),None)
        if failed is None:
            raise HOLD("A supposedly necessary typed gate has no witness")
        result=select(altered,failed)
        witnesses.append({"gate":gate,"teaching_case":failed.id,
                          "ablation_status":result["status"],
                          "matched_ids":[x["id"] for x in checks(altered,failed)]})
    body={
        "schema":SCHEMA,"source_owner_blob":pin(),
        "source_revision":REVISION,
        "learner":"MINIMAL_TYPED_GUARD_ENUMERATION",
        "candidate_gate_subsets":len(possibilities),
        "selected_guard_program":list(chosen),
        "missing_operator_witnesses":witnesses,
        "training_records":[_encode(s) for s in training],
        "training_checksum":digest([_encode(s) for s in training]),
        "source_ownership":"CURATED_HUMAN_PARAPHRASES_NOT_FULL_OPINION_INFERENCE",
        "status":"PROPOSE_FOR_INDEPENDENT_SOURCE_REVIEW",
        "scope":"HISTORICAL_OPINION_CARD_RETRIEVAL_ONLY",
        "law_firm_or_judicial_authority":False,
        "external_actions":False,"real_world_authority":False,
    }
    obj=dict(body,checksum_sha256=digest(body))
    out=json.dumps(obj,indent=2,sort_keys=True,allow_nan=False)+"\n"
    if len(out.encode())>MAX_PACKET:
        raise HOLD("Oversized legal-card method")
    return out


def validate(raw):
    if not isinstance(raw,str) or len(raw.encode())>MAX_PACKET:
        raise HOLD("Invalid or oversized legal reasoning cartridge")
    try:
        obj=json.loads(raw)
    except (TypeError,ValueError) as exc:
        raise HOLD("Unparseable data-only legal cartridge") from exc
    fields={"schema","source_owner_blob","source_revision","learner",
            "candidate_gate_subsets","selected_guard_program",
            "missing_operator_witnesses","training_records","training_checksum",
            "source_ownership","status","scope","law_firm_or_judicial_authority",
            "external_actions","real_world_authority","checksum_sha256"}
    if not isinstance(obj,dict) or set(obj)!=fields:
        raise HOLD("Unrecognized legal operator metadata")
    if (obj["schema"]!=SCHEMA or obj["source_owner_blob"]!=pin()
            or obj["source_revision"]!=REVISION
            or obj["learner"]!="MINIMAL_TYPED_GUARD_ENUMERATION"
            or obj["source_ownership"]!="CURATED_HUMAN_PARAPHRASES_NOT_FULL_OPINION_INFERENCE"
            or obj["status"]!="PROPOSE_FOR_INDEPENDENT_SOURCE_REVIEW"
            or obj["scope"]!="HISTORICAL_OPINION_CARD_RETRIEVAL_ONLY"
            or obj["law_firm_or_judicial_authority"] is not False
            or obj["external_actions"] is not False
            or obj["real_world_authority"] is not False
            or obj["candidate_gate_subsets"]!=(2**len(FIELDS)-1)):
        raise HOLD("Changed type, source, or permission boundaries")
    if obj["training_checksum"]!=digest(obj["training_records"]):
        raise HOLD("Training evidence did not match original")
    from tasks import training
    source_train=tuple(_encode(s) for s in training())
    if obj["training_records"]!=list(source_train):
        raise HOLD("Unverified or substituted source-owned teaching fixtures")
    regenerated=json.loads(fit(tuple(_decode(x) for x in obj["training_records"])))
    if obj!=regenerated:
        raise HOLD("Rehashed fabricated scope, method, or ablation proofs")
    return obj


def query(raw,scenario):
    packet=validate(raw)
    result=select(packet["selected_guard_program"],scenario)
    return {"stage":"SUGGEST_ONLY","status":result["status"],
            "selected":result["selected"],
            "matching_count":result["matching_count"],
            "legal_advice":False,"external_actions":False,
            "real_world_authority":False}
