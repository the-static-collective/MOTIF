"""Original Dogram as independent *algorithm* witness for REASON-008.

Run original, unmodified Dogram at an exact pinned Git revision in CI. Native
ablation removes an isolated decoy edge U->V, leaving the source-owned graph
reachability unchanged. Original Dogram answers on S->T become external
algorithm checks, NEVER independent observations of real-world edges.
"""
from __future__ import annotations

from hashlib import sha1
from pathlib import Path
import json
import sys

from source import Case, bfs_truth, SOURCE_REVISION

ORIGINAL_DOGRAM_REPO="the-static-collective/Dogram"
ORIGINAL_DOGRAM_COMMIT="551b5f9df18f17ec69b452ddcdff01718e0ff771"
PUPIL=Path(__file__).resolve().parents[1]/"reason-cartridge-003"/"pupil.py"
PUPIL_GIT_BLOB="5534b0b82d33b6c81776058170f091038d2ae9b2"


def pin():
    raw=PUPIL.read_bytes()
    actual=sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
    if actual!=PUPIL_GIT_BLOB:
        raise RuntimeError("Changed original Dogram receipt evaluator")
    return actual


pin()
sys.path.append(str(PUPIL.parent))
from pupil import verify_native, HOLD as NativeHOLD


def specimen(mask):
    c=Case(mask)
    edges=[list(e) for bit,e in zip(c.features,c.edges) if bit]
    edges.append(["U","V"])
    return {
        "schema":"dogram.specimen/v0",
        "specimen_id":f"reason-008-native-{mask:02d}",
        "operator":"ablate","operator_version":1,
        "inputs":{
            "graph":{"nodes":sorted(c.nodes+("U","V")),
                     "edges":sorted(edges)},
            "target":{"kind":"edge","source":"U","target":"V"},
            "requested_targets":[["S","T"]],
        },
        "assumptions":[],
        "metadata":{
            "teacher_repo":ORIGINAL_DOGRAM_REPO,
            "teacher_commit":ORIGINAL_DOGRAM_COMMIT,
            "source_owner_revision":SOURCE_REVISION,
            "synthetic_only":True,
            "decoy_removal_does_not_change_graph_reachability":True,
            "independent_world_witness":False,
        },
    }


def emit(root):
    directory=Path(root)
    directory.mkdir(parents=True,exist_ok=True)
    for mask in range(32):
        (directory/f"reason-008-native-{mask:02d}.json").write_text(
            json.dumps(specimen(mask),indent=2,sort_keys=True)+"\n",encoding="utf-8")
    manifest={"schema":"motif.reason.eight.native-audit.v1",
              "source_repo":ORIGINAL_DOGRAM_REPO,
              "source_commit":ORIGINAL_DOGRAM_COMMIT,
              "source_owner_revision":SOURCE_REVISION,
              "cases":32,"requires_actual_native_receipts":True,
              "foreign_checkout_removed_before_review":True,
              "real_world_witness":False}
    (directory/"manifest.json").write_text(
        json.dumps(manifest,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return manifest


def validate_original(root):
    if Path("_external/dogram").exists():
        raise RuntimeError("Teacher checkout still present during independent review")
    directory=Path(root)
    manifest=json.loads((directory/"manifest.json").read_text())
    if (manifest["source_commit"]!=ORIGINAL_DOGRAM_COMMIT
            or manifest["cases"]!=32
            or manifest["requires_actual_native_receipts"] is not True):
        raise RuntimeError("Changed native source contract")
    validated=[]
    for mask in range(32):
        name=f"reason-008-native-{mask:02d}"
        sp=json.loads((directory/(name+".json")).read_text())
        raw=json.loads((directory/(name+".receipt.json")).read_text())
        if sp!=specimen(mask):
            raise RuntimeError("Native specimen changed after generation")
        try:
            native=verify_native(sp,raw)
        except NativeHOLD as exc:
            raise RuntimeError("Original native Dogram receipt refused") from exc
        owner=bfs_truth(Case(mask))
        if native!=owner:
            raise RuntimeError("Dogram disagrees with source-owned BFS")
        validated.append({"mask":mask,"original_dogram_after_decoy_ablation":native,
                          "independent_bfs":owner,"matches":native==owner})
    result={
        "schema":"motif.reason.eight.original-dogram-conformance.v1",
        "original_source_commit":ORIGINAL_DOGRAM_COMMIT,
        "cases":len(validated),"agreement_count":sum(x["matches"] for x in validated),
        "teacher_removed":True,
        "native_receipts_reused_without_foreign_execution":True,
        "algorithm_agreement_not_world_evidence":True,
        "external_actions":False,"real_world_authority":False,
    }
    (directory/"crosscheck.json").write_text(
        json.dumps(result,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    return result


if __name__=="__main__":
    if len(sys.argv)!=3 or sys.argv[1] not in ("emit","verify"):
        raise SystemExit("usage: python native.py emit|verify <evidence-directory>")
    print(json.dumps(emit(sys.argv[2]) if sys.argv[1]=="emit"
                     else validate_original(sys.argv[2]),sort_keys=True,indent=2))
