"""Source-owner review proposal for GRAFT and CANNON, no external write.

GRAFT accepts independently reviewed clean source cuts on separate branches.
CANNON is owner-selected canon, not a deployment/build executor. This packet
requests a future human review, not a source import, signing or selection.
"""
from __future__ import annotations
from pathlib import Path
from hashlib import sha1
import json

from discover import HOLD, validate, digest
from market import validate_receipt

ROOT=Path(__file__).resolve().parent
CUT=("source.py","discover.py","receiver.py","market.py",
     "native.py","test_missing.py","test_native.py")
SCHEMA="motif.reason.eight.review-handoff.v1"


def git_blob(path):
    raw=(ROOT/path).read_bytes()
    return sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()


def draft(method_raw,market_raw,receiver):
    method=validate(method_raw)
    checked=validate_receipt(market_raw,receiver)["market"]
    if (not receiver.admitted or checked["winning_method"]!="GAP_REPAIR_MACRO"
            or checked["incorrect_or_abstained"]!=0
            or checked["independently_correct"]!=32
            or checked["commonwealth_new_source_facts"]!=0
            or checked["independent_evidence_gated_savings_points"]<=0):
        raise HOLD("Uncertified or nonbeneficial method cannot seek source transplant review")
    body={
        "schema":SCHEMA,
        "origin":"the-static-collective/MOTIF",
        "source_branch":"experiment/reason-cartridge-008-missing-primitive",
        "selected_public_source_paths":[{
            "path":"experiments/reason-cartridge-008/"+name,
            "git_blob_sha1":git_blob(name),
        } for name in CUT],
        "method_digest":method["checksum_sha256"],
        "independent_certification_digest":receiver.digest,
        "market_review_digest":digest(checked),
        "graft":{
            "destination_repo":"the-static-collective/GRAFT",
            "public_index_readme_git_blob":"a4a5ee55cf349edba34842a6bfa5313d6fdba4b9",
            "intake_state":"REQUEST_INDEPENDENT_CLEAN_SOURCE_REVIEW",
            "approved_for_public_graft":False,
            "license_and_provenance_review_required":True,
            "history_transfer_permitted":False,
            "target_donor_branch":"NOT_CREATED",
        },
        "cannon":{
            "destination_repo":"the-static-collective/CANNON",
            "public_index_readme_git_blob":"f0e0f4d00ce40760e1ef2c965324d5665990f33b",
            "state":"NOT_CANON",
            "owner_selection_required":True,
            "signature_supplied":False,
            "selected_revision":None,
            "no_execution_permission":True,
        },
        "runtime":"ALLOWLISTED_LOCAL_READ_ONLY",
        "GRAFT_called":False,
        "CANNON_called":False,
        "external_writes":False,
        "real_world_authority":False,
    }
    return json.dumps(dict(body,checksum_sha256=digest(body)),
                      indent=2,sort_keys=True,allow_nan=False)+"\n"


def validate_draft(raw,method_raw,market_raw,receiver):
    if not isinstance(raw,str) or len(raw.encode())>16000:
        raise HOLD("Missing or oversized review packet")
    try:
        obj=json.loads(raw)
        expected=json.loads(draft(method_raw,market_raw,receiver))
    except (ValueError,TypeError,KeyError) as exc:
        raise HOLD("Unrecognized review packet") from exc
    if obj!=expected:
        raise HOLD("Stale, forged or expanded source/canon review request")
    return obj
