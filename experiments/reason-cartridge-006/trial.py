"""End-to-end source-owning council, original-Dogram optional native evidence.

The source owner is an explicit test fixture. A signed/hashed data packet
does not make its synthetic contents a real-world observation.
"""
from __future__ import annotations
import json
from pathlib import Path

from commonwealth import run_council, owner4, Model, HOLD
from cases import episodes, load_native
from distill import learn, validate, Receiver, ROUTES


def heldouts():
    """Evaluation worlds use different topology and witness names from lessons."""
    strong=owner4.Inquiry(
        ("S","X","Y","T"),(("S","X"),("X","T"),("S","Y"),("Y","T"),("S","T")),
        (("S","X","PRESENT","r1"),("X","T","PRESENT","r2"),
         ("S","Y","PRESENT","r3"),("Y","T","PRESENT","r4")),
        ("S","T"),True)
    fragile=owner4.Inquiry(
        ("S","X","T"),(("S","X"),("X","T"),("S","T")),
        (("S","X","PRESENT","r5"),("X","T","PRESENT","r6")),
        ("S","T"),True)
    absent=owner4.Inquiry(
        ("S","X","T"),(("S","X"),("X","T"),("S","T")),
        (("S","X","PRESENT","r7"),("X","T","ABSENT","r8")),
        ("S","T"),True)
    unknown=owner4.Inquiry(
        ("S","X","T"),(("S","X"),("X","T"),("S","T")),
        (("S","X","PRESENT","r9"),),("S","T"),True)
    open_world=owner4.Inquiry(unknown.nodes,unknown.universe,
                             unknown.claims,unknown.removed,False)
    return (
        ("heldout-strong",strong,ROUTES["PROVED_REACHABLE"]),
        ("heldout-fragile",fragile,ROUTES["PROVED_REACHABLE"]),
        ("heldout-negative",absent,ROUTES["PROVED_UNREACHABLE"]),
        ("heldout-unknown",unknown,ROUTES["UNKNOWN"]),
        ("heldout-open",open_world,ROUTES["HOLD_OPEN_WORLD"]),
    )


def run(native_root=None, forbid_teacher_mount=True):
    if forbid_teacher_mount and Path("_external/dogram").exists():
        raise HOLD("Foreign code still mounted: independent recipient cannot attest teacher absence")
    reports=[]
    source_reviews=0
    for name,q,source in episodes():
        before_calls=getattr(source,"calls",0)
        native=load_native(native_root,name) if native_root else None
        report=run_council(q,name=name,source=source,native=native)
        after_calls=getattr(source,"calls",0)
        source_reviews += after_calls-before_calls
        reports.append(report)
    learned=learn(tuple(reports))
    packet=validate(learned)
    receiver=Receiver(learned)
    review=receiver.preview(heldouts())
    if review["errors"]==0:
        receiver.admit("ADMIT_READ_ONLY",review["review_digest"])
    expected={
        "council-strong":("PROVED_REACHABLE","PROVED_REACHABLE"),
        "council-fragile":("PROVED_REACHABLE","PROVED_UNREACHABLE"),
        "council-negative":("PROVED_UNREACHABLE","PROVED_REACHABLE"),
        "council-unknown":("UNKNOWN","PROVED_REACHABLE"),
        "council-open":("HOLD_OPEN_WORLD","HOLD_OPEN_WORLD"),
    }
    if {r["case"]:(r["before"],r["after"]) for r in reports}!=expected:
        raise HOLD("Independent fixture assumptions no longer match actual source-owned code")
    result={
        "schema":"motif.reason.commonwealth-benchmark.v1",
        "native_foreign_teacher_mode":"ACTUAL_PINNED_DOGRAM" if native_root else "NOT_RUN_LOCAL_ONLY",
        "foreign_teacher_source_absent":not Path("_external/dogram").exists(),
        "source_owner_tests":[
            {"case":r["case"],"before":r["before"],"after":r["after"],
             "stop":r["reason_for_stop"],
             "roles":r["marginal"]["contributions"],
             "new_validated_contributions":r["marginal"]["novel"],
             "duplicate_offers_dropped":r["marginal"]["duplicates_rejected"],
             "new_source_evidence":r["marginal"]["new_source_facts"],
             "native_crosscheck":any(e["role"]=="DOGRAMAUDIT" and e["score"]==1
                                     for e in r["ledger"]),
             "external_actions":r["external_actions"],
             "real_world_authority":r["real_world_authority"]}
            for r in reports
        ],
        "source_reviews":source_reviews,
        "naive_review_every_non_open_case":4,
        "new_conclusions_from_local_fixture_reviews":
            sum(r["before"]!=r["after"] for r in reports),
        "duplicate_proposals_suppressed":
            sum(r["marginal"]["duplicates_rejected"] for r in reports),
        "independent_method_review":{"cases":review["cases"],"errors":review["errors"]},
        "method_routes":packet["routes"],
        "method_cartridge_sha256":packet["checksum_sha256"],
        "source_pins":packet["source_blobs"],
        "fixture_only_read_only_admitted":receiver.approved,
        "example_method_suggestion":receiver.suggest(heldouts()[3][1]),
        "full_classical_under_complete_information_would_match":True,
        "no_strong_classical_superiority_claim":True,
        "external_actions":False,"real_world_authority":False,
    }
    if native_root:
        root=Path(native_root)
        (root/"council-receipt.json").write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
        (root/"learned-method.json").write_text(learned)
    return result


if __name__=="__main__":
    import sys
    native=sys.argv[1] if len(sys.argv)==2 else None
    if len(sys.argv)>2:
        raise SystemExit("usage: python trial.py [native-evidence-directory]")
    print(json.dumps(run(native),sort_keys=True,indent=2))
