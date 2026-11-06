"""Evaluator-owned synthetic council fixtures, not fetched from outside."""
from __future__ import annotations

from pathlib import Path
import json

from commonwealth import owner4, ToyOwner, LocalObservationOwner, independent_specimen, DOGRAM_SHA


def redundant():
    return owner4.Inquiry(
        ("S","A","B","T"),
        (("S","A"),("A","T"),("S","B"),("B","T"),("S","T")),
        (("S","A","PRESENT","p1"),("A","T","PRESENT","p2"),
         ("S","B","PRESENT","p3"),("B","T","PRESENT","p4")),
        ("S","T"),True)


def fragile():
    return owner4.Inquiry(
        ("S","A","T"),(("S","A"),("A","T"),("S","T")),
        (("S","A","PRESENT","p1"),("A","T","PRESENT","p2")),
        ("S","T"),True)


def absent():
    return owner4.Inquiry(
        ("S","A","T"),(("S","A"),("A","T"),("S","T")),
        (("S","A","PRESENT","p1"),("A","T","ABSENT","p2")),
        ("S","T"),True)


def unresolved():
    return owner4.Inquiry(
        ("S","A","B","T"),
        (("S","B"),("S","A"),("A","T"),("B","T"),("S","T")),
        (("S","A","PRESENT","p1"),("B","T","ABSENT","p2")),
        ("S","T"),True)


def open_world():
    q=unresolved()
    return owner4.Inquiry(q.nodes,q.universe,q.claims,q.removed,False)


def episodes():
    return (
        ("council-strong", redundant(), None),
        ("council-fragile", fragile(), ToyOwner("owner-fragile",{("A","T"):False,
                                                                  ("S","A"):True})),
        ("council-negative", absent(), ToyOwner("owner-negative",{("A","T"):True})),
        ("council-unknown", unresolved(),
         LocalObservationOwner("owner-unknown",{("S","B"):False,("A","T"):True})),
        ("council-open", open_world(), None),
    )


def emit_native(root):
    root=Path(root)
    root.mkdir(parents=True,exist_ok=True)
    emitted=[]
    for name, q, owner in episodes()[:3]:
        specimen=independent_specimen(q,name+"-dogram")
        (root/(name+".json")).write_text(json.dumps(specimen,sort_keys=True,indent=2)+"\n")
        emitted.append(name)
    (root/"manifest.json").write_text(json.dumps({
        "schema":"motif.reason.native-council-manifest.v1",
        "dogram_commit":DOGRAM_SHA, "names":emitted,
        "native_result_required":True,"no_world_authentication":True
    },sort_keys=True,indent=2)+"\n")


def load_native(root,name):
    root=Path(root)
    if name not in [x[0] for x in episodes()[:3]]:
        return None
    specimen=json.loads((root/(name+".json")).read_text())
    receipt=json.loads((root/(name+".receipt.json")).read_text())
    return specimen,receipt


if __name__=="__main__":
    import sys
    if len(sys.argv)!=2:
        raise SystemExit("usage: python cases.py <native-evidence-dir>")
    emit_native(sys.argv[1])
