"""COGNITION-003: old contacts become relevant after a NEW, unprompted event.

Two-hop history -> source-bounded possible repair test -> verified simulator fix.
Uses actual MOTIF-003, GHoT and Free Graph code; private MEMENTO remains an
optional read-only owner validator. No real hardware, services or personal data.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
from pathlib import Path
import argparse
import json
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE.parent/"cognition001"))
sys.path.insert(0,str(HERE.parent/"cognition002"))
from circuit import AppState, admission, native_affordance, seal
from bridge import validate_understory_owner, _fg_native

DEV_SEEDS=(71001,71011,71021,71031)
TEST_SEEDS=tuple(98201+43*i for i in range(32))
REGIMES=("stable","drift_alternative","drift_unmodeled","echo_source","unrelated_trigger")
POLICIES=("motif_resurface","classical_cached","classical_online_bfs","recent_only")
BUDGET=2
OWNER="INDEPENDENT_AUTHOR_SIM_REPAIR_OWNER"
DEFAULT_STATE=AppState(True,True,50,False,94,True,38.0,.12,"abundant")


def hnum(seed,label,limit):
    return int(sha256(f"cognition003:{seed}:{label}".encode()).hexdigest()[:12],16)%limit


def identifiers(seed):
    """Identifiers deterministic; never include a hidden owner truth bit."""
    q=hnum(seed,"cue",100000)
    return {"cue":f"signal-{q:05d}",
            "bridges":[f"bridge-{q:05d}-a",f"bridge-{q:05d}-b"],
            "units":[f"module-{q:05d}-{i}" for i in range(6)]}


def archive(seed,regime):
    if seed not in DEV_SEEDS+TEST_SEEDS or regime not in REGIMES:
        raise ValueError("UNREGISTERED_WORLD")
    ids=identifiers(seed)
    facts=[]
    for slot in (0,1):
        # The primary echo deliberately has two copies of a shared ORIGIN,
        # not independent evidence; records still have different receipt IDs.
        first_root=f"origin-{seed}-p{slot}-cue"
        second_root=(first_root if regime=="echo_source" and slot==0
                     else f"origin-{seed}-p{slot}-module")
        facts.extend([
            {"rid":f"old-{seed}-slot{slot}-a","day":"2026-11-10",
             "slot":slot,"edge":0,"from":ids["cue"],"to":ids["bridges"][slot],
             "root":first_root,"kind":"contact","status":"unresolved"},
            {"rid":f"old-{seed}-slot{slot}-b","day":"2026-11-10",
             "slot":slot,"edge":1,"from":ids["bridges"][slot],
             "to":ids["units"][slot],
             "root":second_root,"kind":"contact","status":"unresolved"},
        ])
    return facts


def new_incident(seed,regime):
    ids=identifiers(seed)
    cue=(f"unrelated-{hnum(seed,'unrelated',100000):05d}"
         if regime=="unrelated_trigger" else ids["cue"])
    return {"rid":f"incident-{seed}","day":"2026-11-11",
            "kind":"observed-new-incident","cue":cue,
            "question_from_user":False,"owner_authority":"simulated-only",
            "root":f"origin-{seed}-new-incident"}


class RepairOwner:
    """A distinct source of task truth. Policy never gets the hidden target."""
    def __init__(self,seed,regime):
        ids=identifiers(seed)
        target_idx=(0 if regime=="stable"
                    else 1 if regime in ("drift_alternative","echo_source")
                    else 3 if regime=="drift_unmodeled"
                    else 4)
        self._fault=ids["units"][target_idx]
        self._seed=seed
        self._regime=regime
        self.probes=0
        self.repaired=False
        self.confirmed=set()
        self.receipts=[]

    def _receipt(self,kind,**fields):
        row={"kind":kind,"source":OWNER,"seed":self._seed,
             "sequence":len(self.receipts)+1,**fields}
        row["seal"]=seal(row)
        self.receipts.append(row)
        return row

    def probe(self,component):
        if self.probes>=BUDGET:raise RuntimeError("PROBE_BUDGET_EXHAUSTED")
        if component not in identifiers(self._seed)["units"]:
            raise ValueError("NOT_AN_ALLOWED_COMPONENT")
        self.probes+=1
        positive=component==self._fault
        if positive:self.confirmed.add(component)
        return self._receipt("TEST",component=component,positive=positive,
                             cost=1,posthoc_truth=False)

    def repair(self,component):
        if component not in self.confirmed:
            raise ValueError("NO_POSITIVE_OWNER_TEST")
        if self.repaired:raise RuntimeError("ALREADY_REPAIRED")
        self.repaired=component==self._fault
        return self._receipt("REPAIR",component=component,
                             independently_verified=self.repaired,
                             owner_tested_before=True,cost=1)

    def evaluation_only(self):
        return {"true_fault":self._fault,"verified_repair":self.repaired,
                "owner_receipts":self.receipts,"total_probes":self.probes}


def _native_graph():
    """Load real Free Graph canonical ID/validation AND its native traversal."""
    rec_id,pkt_id,validate=_fg_native()
    root=ROOT/"sources"/"free-graph"
    if str(root) not in sys.path:sys.path.insert(0,str(root))
    from scripts.fg_ops import neighbors
    return rec_id,pkt_id,validate,neighbors


def packet_for(facts,incident=None):
    """No synthetic observation becomes accepted evidence or owner-local truth."""
    rec_id,pkt_id,validate,_=_native_graph()
    records=list(facts)
    if incident is not None:
        records=records+[incident]
    sources=[]
    for record in records:
        source={"source_class":"unresolved-receipt",
                "locator":{"system":"COGNITION-003 invented laboratory",
                           "coordinate":record["rid"],"revision":"synthetic-v0",
                           "resolution":"author-generated structured source"},
                "observed_at":record["day"],"acquisition":"generated synthetic case",
                "digest":"sha256:"+seal(record),
                "excerpt":("Unresolved old pairing" if record["kind"]=="contact"
                           else "New incident observed, no user question"),
                "access":"public","export":"portable","authority":"none",
                "extensions":{"origin_root":record["root"],
                              "slot":record.get("slot"),
                              "synthetic":True}}
        source["id"]=rec_id("source",source)
        sources.append(source)
    source_ids={r["rid"]:s["id"] for r,s in zip(records,sources)}
    labels=sorted({label for r in facts for label in (r["from"],r["to"])}
                  | ({incident["cue"]} if incident else set()))
    nodes=[]
    for label in labels:
        matching=[r for r in facts if label in (r["from"],r["to"])]
        refs=[source_ids[r["rid"]] for r in matching]
        if incident and label==incident["cue"]:
            refs.append(source_ids[incident["rid"]])
        node={"kind":"artifact","label":label,
              "status":"unresolved","source_ids":list(dict.fromkeys(refs)),
              "extensions":{"synthetic":True}}
        node["id"]=rec_id("node",node)
        nodes.append(node)
    by_label={n["label"]:n["id"] for n in nodes}
    links=[]
    for r in facts:
        link={"from":by_label[r["from"]],"to":by_label[r["to"]],
              "verb":"connects","qualifier":("potential-cue-mark" if r["edge"]==0
                                             else "potential-mark-unit"),
              "status":"unresolved","authority":"none",
              "source_ids":[source_ids[r["rid"]]],
              "extensions":{"slot":r["slot"],"synthetic":True}}
        link["id"]=rec_id("link",link)
        links.append(link)
    selected=[r["id"] for r in sources+nodes+links]
    packet={"schema":"free-graph.packet/v0",
            "purpose":"Invented cross-day repair hypothesis without adoption",
            "modes":["re-enter","seed"],
            "scope":{"task":"Resurface source-bound two-hop possible repair test",
                     "worlds":["COGNITION-003 author-written repair game"],
                     "as_of":"2026-11-11","resolution":"historical and current observations only"},
            "task_world_cut":{"status":"unresolved","selected_ids":selected,
                              "owner_head_source_ids":[],
                              "omitted":[{"door":"MEMENTO owner-current admission",
                                          "reason":"No admission or private records inspected"}],
                              "rationale":"Two separate old witnesses can propose a test, not certify a repair"},
            "sources":sources,"nodes":nodes,"links":links,
            "residual_fog":["Unverified correlations are not established causal repairs.",
                            "Component fault unknown before an independent test."],
            "non_imports":["No MEMENTO private state copied.","No proposed relation admitted.",
                           "No model hidden reasoning exposed."],
            "extensions":{"case":"COGNITION003","synthetic":True}}
    packet["packet_id"]=pkt_id(packet)
    errs=validate(packet)
    if errs:raise ValueError("NATIVE_FREE_GRAPH_VALIDATION_FAILED: "+";".join(errs))
    return packet


def eligible_paths(packet,cue):
    """Return auditable two-hop source-root-distinct paths from real FG walk."""
    _,_,validate,neighbors=_native_graph()
    if validate(packet):raise ValueError("UNTRUSTED_GRAPH_PACKET")
    starts=[n for n in packet["nodes"] if n["label"]==cue]
    if not starts:return [],0
    # The native traversal is a *projection*, not authority. The owning
    # packet keeps its unresolved cut even if the view has a bounded cut.
    view=neighbors(packet,starts[0]["id"],depth=2)
    if validate(view):raise ValueError("NATIVE_NEIGHBOR_PROJECTION_INVALID")
    src={s["id"]:s for s in view["sources"]}
    nodes={n["id"]:n["label"] for n in view["nodes"]}
    edges=view["links"]
    paths=[]
    for left in edges:
        if left["from"]!=starts[0]["id"] or left["qualifier"]!="potential-cue-mark":
            continue
        for right in edges:
            if (right["from"]!=left["to"] or
                right["qualifier"]!="potential-mark-unit" or
                right["extensions"]["slot"]!=left["extensions"]["slot"]):
                continue
            r1=src[left["source_ids"][0]]["extensions"]["origin_root"]
            r2=src[right["source_ids"][0]]["extensions"]["origin_root"]
            paths.append({"slot":left["extensions"]["slot"],
                          "candidate":nodes[right["to"]],"cue":cue,
                          "intermediate":nodes[left["to"]],
                          "source_ids":left["source_ids"]+right["source_ids"],
                          "source_roots":[r1,r2],
                          "independent":r1!=r2,
                          "status":"PENCIL_NOT_A_REPAIR",
                          "graph_edge_ids":[left["id"],right["id"]]})
    return sorted(paths,key=lambda p:(p["slot"],p["candidate"])),len(view["links"])


def _cached_paths(facts):
    """A real native Free Graph precomputation, usable before incident exists."""
    p=packet_for(facts)
    cues=sorted({r["from"] for r in facts if r["edge"]==0})
    output={}
    ops=0
    for cue in cues:
        paths,walked=eligible_paths(p,cue)
        output[cue]=paths
        ops+=walked
    return output,ops


def _motif_hypothetical_order(paths):
    """Actual MOTIF-003 affordance observer, no hidden truth or acts."""
    native=native_affordance()
    possible=tuple(x for x in paths if x["independent"])
    initial=frozenset({("observation","source-bound-two-hop")})
    def successors(world,_verbs):
        for i,p in enumerate(possible):
            key=("skill",f"authorized_test_option:{i}")
            if key in world:continue
            yield (f"test_option_{i}",(str(p["slot"]),),world|{key})
    results=native.analyze_first_moves(initial,(),successors,
                                      lambda after,before:len(after-before),
                                      horizon=1,max_worlds=24)
    if len(results)!=len(possible):
        raise AssertionError("MOTIF_003_DID_NOT_SEE_ALL_TEST_AFFORDANCES")
    # Predeclared priority (older path first); all candidate expected utility
    # is the same before owner tests. MOTIF-003 proposes, not acts.
    return list(possible),len(results)


def owner_understory_envelope(facts,incident):
    """Private MEMENTO owner-validated synthetic occurrence sequence only."""
    if len(facts)!=4 or incident["kind"]!="observed-new-incident":
        raise ValueError("UNSUPPORTED_OWNER_ENVELOPE")
    common={"schema":"memento.understory-record/v0",
            "observer":"motif-synthetic-observer"}
    contacts=[]
    for i,f in enumerate(facts):
        at=f"2026-11-10T{8+i:02d}:00:00Z"
        contacts.append({**common,"id":f"cog003-contact-{f['rid']}",
                         "family":"contact","recorded_at":at,
                         "sensed_at":at,"occurrence_ref":f"synthetic:{f['rid']}",
                         "evidence_refs":[f"synthetic:{f['rid']}"]})
    assoc=[]
    for slot in (0,1):
        members=[contacts[slot*2]["id"],contacts[slot*2+1]["id"]]
        assoc.append({**common,"id":f"cog003-association-{slot}",
                      "family":"association","recorded_at":"2026-11-10T14:00:00Z",
                      "member_refs":members,
                      "relation_hint":"Two-hop possible association, unverified",
                      "status":"unresolved",
                      "evidence_refs":[f"synthetic:{facts[slot*2]['rid']}",
                                       f"synthetic:{facts[slot*2+1]['rid']}"]})
    activation={**common,"id":f"cog003-activation-{incident['rid']}",
                "family":"activation","recorded_at":"2026-11-11T12:00:00Z",
                "activated_at":"2026-11-11T12:00:00Z",
                "trace_refs":[a["id"] for a in assoc],
                "trigger_ref":f"synthetic:{incident['rid']}",
                "descendant_projection_ref":"synthetic:next-verified-test-question",
                "evidence_refs":[f"synthetic:{incident['rid']}"]}
    return {"schema":"motif.understory-contemplation/v0",
            "source_mode":"synthetic-fixture",
            "owner_permission":"read-only-validation",
            "admission":"none",
            "records":[*contacts,*assoc,activation]}


def run_case(seed,regime,policy,*,memento_root=None,full=False,state=DEFAULT_STATE):
    if seed not in DEV_SEEDS+TEST_SEEDS or regime not in REGIMES or policy not in POLICIES:
        raise ValueError("UNREGISTERED_BENCHMARK_CASE")
    facts=archive(seed,regime)
    before=[dict(r) for r in facts]
    event=new_incident(seed,regime)
    # User opt-in and GHoT resource admission required only for idle
    # contemplation/precompilation, never for a human-directed current event.
    admitted=admission(state,1)
    can_idle=admitted["action"]=="run_here"
    cached=None
    idle_ops=0
    if policy in ("motif_resurface","classical_cached") and can_idle:
        cached,idle_ops=_cached_paths(facts)
    current_packet=packet_for(facts,event)
    current_paths,graph_ops=eligible_paths(current_packet,event["cue"])
    if policy=="recent_only":
        proposals=[]
        wake_ops=0
        idle_ops=0
    elif policy in ("motif_resurface","classical_cached") and cached is not None:
        proposals=cached.get(event["cue"],[])
        wake_ops=1 # associative cue index operation
    else:
        # Fair conventional on-event graph search with all old source data.
        proposals=current_paths
        # Include the starting cue lookup even if it has no graph neighbors.\n        wake_ops=graph_ops+1\n    offered=[p for p in proposals if p["independent"]]
    excluded=[p for p in proposals if not p["independent"]]
    if policy=="motif_resurface" and cached is not None:
        offered,affordances=_motif_hypothetical_order(proposals)
    else:
        affordances=0
    owner=RepairOwner(seed,regime)
    tests=[]
    repair=None
    for c in offered[:BUDGET]:
        result=owner.probe(c["candidate"])
        tests.append({"candidate":c["candidate"],
                      "graph_sources":c["source_ids"],"roots":c["source_roots"],
                      "owner_receipt":result})
        if result["positive"]:
            repair=owner.repair(c["candidate"])
            break
    if before!=facts:raise AssertionError("OLD_ARCHIVE_MUTATED")
    if policy=="motif_resurface" and cached is not None:
        owner_envelope=owner_understory_envelope(facts,event)
        memento=validate_understory_owner(owner_envelope,memento_root)
    else:
        memento={"status":"NOT_INVOKED_FOR_POLICY","validated":False}
    evaluator=owner.evaluation_only()
    output={"seed":seed,"regime":regime,"policy":policy,
            "incident":{"cue":event["cue"],"date":event["day"],
                        "question_from_user":False},
            "source_cut":"UNRESOLVED","graph_native_validated":True,
            "graph_packet_id":current_packet["packet_id"],
            "candidate_paths":len(proposals),
            "credible_paths":len(offered),
            "excluded_echo_paths":len(excluded),
            "resurfaced":bool(offered and cached is not None
                              and policy=="motif_resurface"),
            "native_motif003_options":affordances,
            "native_understory":memento,
            "idle_operations":idle_ops,"wake_operations":wake_ops,
            "probes":owner.probes,"repair_attempts":int(repair is not None),
            "verified_success":evaluator["verified_repair"],
            "unsafe_repairs":int(repair is not None and not evaluator["verified_repair"]),
            "abstained":repair is None,
            "no_source_truth_promoted":True,
            "owner_verified_receipts":evaluator["owner_receipts"],
            "real_external_actions":0,"model_calls":0,
            "app_not_deployed":True,
            "archive_unchanged":True,
            "evaluator_only_hidden_fault":evaluator["true_fault"],
            "tested_candidates":tests if full else [t["candidate"] for t in tests]}
    output["seal"]=seal(output)
    return output


def benchmark(split="development",full=False):
    if split not in ("development","heldout"):
        raise ValueError("UNREGISTERED_SPLIT")
    seeds=DEV_SEEDS if split=="development" else TEST_SEEDS
    rows=[run_case(s,r,p,full=full) for s in seeds for r in REGIMES for p in POLICIES]
    summary={}
    paired=[]
    for regime in REGIMES:
        summary[regime]={}
        for policy in POLICIES:
            group=[x for x in rows if x["regime"]==regime and x["policy"]==policy]
            summary[regime][policy]={
                "cases":len(group),
                "verified_repairs":sum(x["verified_success"] for x in group),
                "unsafe_repairs":sum(x["unsafe_repairs"] for x in group),
                "abstained":sum(x["abstained"] for x in group),
                "source_echo_exclusions":sum(x["excluded_echo_paths"] for x in group),
                "resurfaced":sum(x["resurfaced"] for x in group),
                "total_probes":sum(x["probes"] for x in group),
                "mean_idle_ops":round(sum(x["idle_operations"] for x in group)/len(group),4),
                "mean_wake_ops":round(sum(x["wake_operations"] for x in group)/len(group),4),
            }
        for seed in seeds:
            group={x["policy"]:x for x in rows if x["seed"]==seed and x["regime"]==regime}
            paired.append({"seed":seed,"regime":regime,
                           "motif_minus_classical_cached_success":
                             int(group["motif_resurface"]["verified_success"])
                             -int(group["classical_cached"]["verified_success"]),
                           "motif_minus_classical_online_success":
                             int(group["motif_resurface"]["verified_success"])
                             -int(group["classical_online_bfs"]["verified_success"]),
                           "motif_minus_cached_wake_ops":
                             group["motif_resurface"]["wake_operations"]
                             -group["classical_cached"]["wake_operations"]})
    out={"experiment":"COGNITION-003","split":split,"seeds":list(seeds),
         "regimes":list(REGIMES),"policies":list(POLICIES),
         "n":len(rows),"summary":summary,"paired":paired,
         "source":"AUTHOR_BUILT_TWO_DAY_REPAIR_SIMULATOR",
         "worlds_independent_of_actual_user":True,
         "private_memento_public_runner":"EXPLICIT_HOLD_UNLESS_OWNER_MOUNTED",
         "strong_classical_may_TIE":True,
         "model_calls":0,"external_actions":0,
         "rows":rows}
    out["seal"]=seal(out)
    return out


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--split",choices=("development","heldout"),default="development")
    parser.add_argument("--full",action="store_true")
    parser.add_argument("--memento-root",default=None)
    parser.add_argument("--one-seed",type=int,default=None)
    parser.add_argument("--one-regime",choices=REGIMES,default="stable")
    args=parser.parse_args()
    if args.one_seed is not None:
        result=run_case(args.one_seed,args.one_regime,"motif_resurface",
                        memento_root=args.memento_root,full=True)
    else:
        result=benchmark(args.split,args.full)
    print(json.dumps(result,sort_keys=True,indent=2))
