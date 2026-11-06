"""Original Dogram provides independent algorithm conformance for both families.

At an exact source revision, Dogram receives 64 directed-graph specimens.
Each ablates an isolated decoy U->V, so before/after S->T is identical to
independent source-owned BFS. Its checkout is deleted before receipt review.
No world-edge truth, access token or external action is inferred.
"""
from __future__ import annotations

from pathlib import Path
from hashlib import sha1
import json
import sys

from source import Case,FAMILIES,bfs,SOURCE_REVISION

ORIGINAL_DOGRAM_REPO="the-static-collective/Dogram"
ORIGINAL_DOGRAM_COMMIT="551b5f9df18f17ec69b452ddcdff01718e0ff771"
READER=Path(__file__).resolve().parents[1]/"reason-cartridge-003"/"pupil.py"
READER_BLOB="5534b0b82d33b6c81776058170f091038d2ae9b2"


def pin():
    raw=READER.read_bytes()
    actual=sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
    if actual!=READER_BLOB:
        raise RuntimeError("Original Dogram source-reader contract changed")
    return actual


pin()
sys.path.append(str(READER.parent))
from pupil import verify_native, HOLD as NativeHOLD


def specimen(family,mask):
    if family not in FAMILIES or type(mask) is not int or not 0<=mask<32:
        raise ValueError("Unsupported source specimen")
    names,edges=Case(mask,family).graph()
    nodes=sorted(names+("U","V"))
    active=sorted([list(e) for e in edges]+[["U","V"]])
    return {
        "schema":"dogram.specimen/v0",
        "specimen_id":f"reason-009-{family.lower()}-{mask:02d}",
        "operator":"ablate","operator_version":1,
        "inputs":{
            "graph":{"nodes":nodes,"edges":active},
            "target":{"kind":"edge","source":"U","target":"V"},
            "requested_targets":[["S","T"]],
        },
        "assumptions":[],
        "metadata":{
            "teacher_repo":ORIGINAL_DOGRAM_REPO,
            "teacher_commit":ORIGINAL_DOGRAM_COMMIT,
            "source_revision":SOURCE_REVISION,
            "source_family":family,
            "disconnected_decoy":True,
            "source_world_authentication":False,
            "synthetic_only":True,
        },
    }


def emit(root):
    dest=Path(root)
    dest.mkdir(parents=True,exist_ok=True)
    for family in FAMILIES:
        for mask in range(32):
            sp=specimen(family,mask)
            (dest/(sp["specimen_id"]+".json")).write_text(
                json.dumps(sp,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    manifest={
        "schema":"motif.reason.grammar-009.original-dogram-manifest.v1",
        "source_commit":ORIGINAL_DOGRAM_COMMIT,
        "source_owner_revision":SOURCE_REVISION,
        "families":list(FAMILIES),
        "cases":64,
        "requires_original_native_receipts":True,
        "remove_dogram_source_before_final_review":True,
        "real_world_authority":False,
    }
    (dest/"manifest.json").write_text(
        json.dumps(manifest,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    return manifest


def check(root):
    if Path("_external/dogram").exists():
        raise RuntimeError("Foreign original Dogram code still mounted")
    dest=Path(root)
    manifest=json.loads((dest/"manifest.json").read_text())
    if (manifest["source_commit"]!=ORIGINAL_DOGRAM_COMMIT
            or manifest["source_owner_revision"]!=SOURCE_REVISION
            or manifest["cases"]!=64):
        raise RuntimeError("Original source manifest changed")
    results=[]
    for family in FAMILIES:
        for mask in range(32):
            expected_sp=specimen(family,mask)
            identity=expected_sp["specimen_id"]
            actual_sp=json.loads((dest/(identity+".json")).read_text())
            native_receipt=json.loads((dest/(identity+".receipt.json")).read_text())
            if actual_sp!=expected_sp:
                raise RuntimeError("Native specimen changed after issue")
            try:got=verify_native(actual_sp,native_receipt)
            except NativeHOLD as exc:
                raise RuntimeError("Original native Dogram rejected fixture") from exc
            expected=bfs(Case(mask,family))
            if got!=expected:
                raise RuntimeError("Original Dogram mathematical disagreement")
            results.append({"family":family,"mask":mask,
                            "native_dogram":got,"independent_BFS":expected,
                            "same":got==expected})
    aggregate={
        "schema":"motif.reason.grammar-009.original-dogram-conformance.v1",
        "actual_original_dogram_revision":ORIGINAL_DOGRAM_COMMIT,
        "families":list(FAMILIES),
        "native_receipts_checked":len(results),
        "independently_matching_source_BFS":sum(r["same"] for r in results),
        "native_checkout_absent_at_review":True,
        "algorithm_agreement_not_external_world_evidence":True,
        "external_execution":False,"real_world_authority":False,
    }
    (dest/"conformance.json").write_text(
        json.dumps(aggregate,sort_keys=True,indent=2)+"\n")
    return aggregate


if __name__=="__main__":
    if len(sys.argv)!=3 or sys.argv[1] not in ("emit","verify"):
        raise SystemExit("usage: python native.py emit|verify <evidence-dir>")
    print(json.dumps(emit(sys.argv[2]) if sys.argv[1]=="emit"
                     else check(sys.argv[2]),sort_keys=True,indent=2))
