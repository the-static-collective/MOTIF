"""COGNITION-002: opt-in Understory residue -> Free Graph possible relation.

PRIVATE MEMENTO is never copied into public MOTIF. Native MEMENTO validation
requires an explicitly mounted owner-local MEMENTO tree. Native Free Graph
validation requires a pinned PUBLIC Free Graph checkout. No writes to either.
"""
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import argparse
import json
import os
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE.parent / "cognition001"))
from circuit import (AppState, FourSpeedMind, demo_book, seal as local_seal,
                     LENSES, lens_question)

FREE_GRAPH_PIN = "ec0ad8743c5faac3f3675760bbafcbcb1df846c1"
MEMENTO_PIN = "70ceaad8fd7a87e5b5f753f8f345693aec7570a0"
OWNER_BRIDGE = "scripts/validate-understory-contemplation.mjs"
MEMENTO_ENVELOPE = "motif.understory-contemplation/v0"
EXPECTED_IDS = frozenset(("demo-01","demo-02","demo-03","demo-04","demo-05","demo-06"))
OBSERVER = "motif-synthetic-observer"


def _fg_native():
    path = ROOT / "sources" / "free-graph" / "scripts"
    if not (path / "fg_core.py").is_file():
        raise RuntimeError("PINNED_FREE_GRAPH_SOURCE_UNAVAILABLE")
    if str(path) not in sys.path:
        sys.path.insert(0,str(path))
    from fg_core import record_id, packet_id, validate_packet
    return record_id, packet_id, validate_packet


def _time(day, hour):
    return f"{day}T{hour}:00:00Z"


def understory_fixture(book):
    """Only explicit synthetic daybook fixture IDs may enter this public demo."""
    rows = {r.rid:r for r in book.rows}
    if set(rows)!=EXPECTED_IDS or any(not r.origin_root.startswith("bench-") for r in rows.values()):
        raise ValueError("NOT_AUTHORIZED_FOR_REAL_DATA")
    earlier = [rows["demo-02"],rows["demo-03"]]
    trigger = rows["demo-05"]
    if not (all(r.day<trigger.day for r in earlier)
            and earlier[0].origin_root != earlier[1].origin_root):
        raise ValueError("MISSING_HISTORICAL_INDEPENDENT_CONTACTS")
    common = {"schema":"memento.understory-record/v0", "observer":OBSERVER}
    contacts=[]
    for n,r in enumerate(earlier,1):
        when=_time(r.day,f"0{8+n}")
        contacts.append({**common,"id":f"cognition002-contact-{n}",
                         "family":"contact","recorded_at":when,"sensed_at":when,
                         "occurrence_ref":f"synthetic:{r.rid}",
                         "evidence_refs":[f"synthetic:{r.rid}"]})
    assoc={**common,"id":"cognition002-association-1",
           "family":"association","recorded_at":_time(earlier[0].day,"12"),
           "member_refs":[r["id"] for r in contacts],
           "evidence_refs":[f"synthetic:{r.rid}" for r in earlier],
           "relation_hint":"May share an unknown dependency; no causal claim",
           "status":"unresolved"}
    activation={**common,"id":"cognition002-activation-1",
                "family":"activation","recorded_at":_time(trigger.day,"13"),
                "activated_at":_time(trigger.day,"13"),
                "trace_refs":[assoc["id"]],
                "trigger_ref":f"synthetic:{trigger.rid}",
                "descendant_projection_ref":"synthetic:pending-question",
                "evidence_refs":[f"synthetic:{trigger.rid}"]}
    return {"schema":MEMENTO_ENVELOPE,
            "source_mode":"synthetic-fixture",
            "owner_permission":"read-only-validation",
            "admission":"none",
            "records":[*contacts,assoc,activation]}


def validate_understory_owner(packet, memento_root):
    """Genuine PRIVATE owner validator; public tests require an explicit HOLD."""
    if memento_root is None:
        return {"status":"HOLD_NATIVE_MEMENTO_UNAVAILABLE","validated":False}
    script=Path(memento_root).expanduser().resolve()/OWNER_BRIDGE
    if not script.is_file():
        return {"status":"HOLD_NATIVE_MEMENTO_UNAVAILABLE","validated":False}
    try:
        result=subprocess.run(
            ["node",str(script)],input=json.dumps(packet),capture_output=True,
            text=True,timeout=8,check=False,
        )
    except (OSError,subprocess.TimeoutExpired):
        return {"status":"HOLD_NATIVE_MEMENTO_FAILED","validated":False}
    if result.returncode:
        # No private stderr content is forwarded to a public caller.
        return {"status":"HOLD_NATIVE_MEMENTO_REJECTED","validated":False}
    try:
        data=json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"status":"HOLD_NATIVE_MEMENTO_INVALID_RESULT","validated":False}
    actual_digest = "sha256:"+sha256(
        json.dumps(packet["records"],separators=(",",":"),ensure_ascii=False).encode()
    ).hexdigest()
    expected_ids=[r["id"] for r in packet["records"]]
    if (data.get("schema")!="memento.understory-contemplation-check/v0"
        or data.get("status")!="validated-nonconstituting"
        or data.get("source")!="native-memento-understory-validator"
        or data.get("record_count")!=len(expected_ids)
        or data.get("record_ids")!=expected_ids
        or data.get("digest")!=actual_digest
        or data.get("authority")!="none"
        or data.get("admission")!="none"
        or data.get("writes")!=0 or data.get("real_world_actions")!=0):
        return {"status":"HOLD_NATIVE_MEMENTO_INCONSISTENT","validated":False}
    return {"status":"NATIVE_UNDERSTORY_STRUCTURAL_VALIDATION",
            "validated":True,"count":data["record_count"],
            "families":data["family_counts"],
            "authority":"none","written":False,
            "source_owner":"PRIVATE_MEMENTO_NOT_EXPORTED"}


def public_free_graph(book, question):
    """Non-admitted synthetic public projection using authentic Free Graph IDs."""
    rec_id,pkt_id,validate = _fg_native()
    rows={r.rid:r for r in book.rows}
    ids=("demo-02","demo-03","demo-05")
    sources=[]
    for name in ids:
        r=rows[name]
        evidence=r.public()
        source={"source_class":"unresolved-receipt",
                "locator":{"system":"COGNITION-002 synthetic fixture",
                           "coordinate":f"synthetic:{name}",
                           "revision":"fixture-v0",
                           "resolution":"invented structured source record"},
                "observed_at":r.day,
                "acquisition":"invented test fixture; no personal data",
                "excerpt":f"Invented {r.task} record: {r.status}; {r.note}",
                "digest":"sha256:"+sha256(
                    json.dumps(evidence,sort_keys=True,separators=(",",":")).encode()
                ).hexdigest(),
                "access":"public","export":"portable","authority":"none"}
        source["id"]=rec_id("source",source)
        sources.append(source)
    s1,s2,s3=[s["id"] for s in sources]
    nodes=[]
    for kind,label,status,refs,extra in [
        ("encounter","Historical synthetic reporting encounter","observed",[s1],{}),
        ("encounter","Historical synthetic delivery encounter","observed",[s2],{}),
        ("claim","Possible shared dependency; unverified","unresolved",[s1,s2],
         {"claim_class":"inferential","witness_requirement":"owner-defined"}),
        ("question",question,"unresolved",[s1,s2,s3],
         {"witness_requirement":"owner-defined"}),
    ]:
        node={"kind":kind,"label":label,"status":status,"source_ids":refs,**extra}
        node["id"]=rec_id("node",node)
        nodes.append(node)
    links=[]
    for source,target,qualifier,refs in [
        (nodes[0],nodes[2],"tentative-association",[s1,s2]),
        (nodes[1],nodes[2],"tentative-association",[s1,s2]),
        (nodes[2],nodes[3],"opens-falsifiable-question",[s1,s2,s3]),
    ]:
        link={"from":source["id"],"verb":"connects","to":target["id"],
              "qualifier":qualifier,"status":"unresolved",
              "source_ids":refs,"authority":"none"}
        link["id"]=rec_id("link",link)
        links.append(link)
    packet={"schema":"free-graph.packet/v0",
            "purpose":"Source-bounded fictional associative residue; hypothesis only",
            "modes":["re-enter","seed"],
            "scope":{"task":"Discover falsifiable questions from earlier synthetic contacts",
                     "worlds":["COGNITION-002 author-built test fixture"],
                     "as_of":"2026-11-11","resolution":"explicitly unresolved research-only"},
            "task_world_cut":{
                "status":"unresolved",
                "selected_ids":[s["id"] for s in sources]+
                               [n["id"] for n in nodes]+[l["id"] for l in links],
                "owner_head_source_ids":[],
                "omitted":[{"door":"Private MEMENTO world-current owner head",
                            "reason":"Not entered, read, or asked to admit its historical records"}],
                "rationale":"Witnessed synthetic old and new records allow a question but not a claim of causation"},
            "sources":sources,"nodes":nodes,"links":links,
            "residual_fog":["Similarity does not establish common cause.",
                            "Native private MEMENTO validation is a separate owner-local step.",
                            "No downstream experiment has confirmed this question."],
            "non_imports":["No MEMENTO private files, world ledger or admissions were imported.",
                           "An Understory activation is not evidence of earlier conscious knowledge.",
                           "No graph edge constitutes a local owner decision."],
            "extensions":{"synthetic":True,"authority":"none",
                          "mode":"ASSOCIATIVE_RESEARCH_NOT_CANON"}}
    packet["packet_id"]=pkt_id(packet)
    errors=validate(packet)
    if errors:
        raise ValueError("NATIVE_FREE_GRAPH_REJECTED: "+"; ".join(errors))
    return packet


def council_vs_single(book, budget=5):
    """Same declared data and question count; NO fabricated outcome scores."""
    old=[r for r in book.rows if r.day=="2026-11-10"]
    today=[r for r in book.rows if r.day=="2026-11-11"]
    candidates=[(a,b) for a in old for b in today if a.origin_root!=b.origin_root]
    if not candidates or budget<1 or budget>5:
        raise ValueError("UNSUPPORTED_EXPLORATION_BUDGET")
    # Single critic can examine the SAME distinct pairs and make a tailored
    # skepticism question for each. Multi-lens gets same count and source pair
    # choice, but changes the question-generation lens.
    single=[];council=[]
    for i in range(budget):
        a,b=candidates[i]
        single.append(lens_question("skeptic",a,b))
        council.append(lens_question(LENSES[i],a,b))
    return {"budget_each":budget,"single_critic":single,"five_lens_council":council,
            "verified_downstream_successes":{"single_critic":0,
                                             "five_lens_council":0},
            "successes_not_measured":True,
            "interpretation":"Question diversity is observable; usefulness is NOT yet evaluated."}


def integrated_demo(private_memento_root=None, state=None):
    book=demo_book()
    if state is None:
        state=AppState(True,True,50,False,94,True,37.0,.14,"abundant")
    mind=FourSpeedMind(book,"2026-11-11")
    first=mind.tick(state)
    if first["status"]!="PROPOSED_NOT_ADMITTED":
        return {"status":"HOLD_APP_OR_GHOT","gate":first,
                "free_graph":None,"understory":None,"external_actions":0}
    fixture=understory_fixture(book)
    native=validate_understory_owner(fixture,private_memento_root)
    question=first["proposal"]["question"]
    graph=public_free_graph(book,question)
    return {"status":"RESEARCH_PROPOSAL_ONLY",
            "app_gate":"OPTED_IN_VISIBLE_IDLE_RESOURCE_ADMITTED",
            "native_memento":native,
            "free_graph":{"native_validator":True,"packet_id":graph["packet_id"],
                          "sources":len(graph["sources"]),"nodes":len(graph["nodes"]),
                          "links":len(graph["links"]),"owner_admission":False,
                          "graph":graph},
            "understory":{"synthetic_record_count":len(fixture["records"]),
                          "record_families":[r["family"] for r in fixture["records"]],
                          "activation_references_old_trace":True,
                          "history_mutated":False,"admission":"none"},
            "comparison":council_vs_single(book),
            "real_world_effects":0,"model_calls":0,"private_data_read":False,
            "app_deployed":False}


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--memento-root",default=None,
                        help="Owner-installed private MEMENTO source tree; never exported")
    parser.add_argument("--output",default=None,
                        help="Optional local JSON output. Synthetic fixture only.")
    args=parser.parse_args()
    result=integrated_demo(private_memento_root=args.memento_root)
    output=json.dumps(result,indent=2,sort_keys=True)+"\n"
    if args.output:
        Path(args.output).write_text(output)
    else:
        print(output,end="")
