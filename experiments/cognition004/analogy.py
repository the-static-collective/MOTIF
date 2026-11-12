"""COGNITION-004 — Unwritten analogy between domains with disjoint nouns.

Synthetic structural analogy, not new causal discovery or a background agent.
The target outcome is owned by a separate programmed verifier. No actual device
action, user history, model call, code rewriting, or private repo export.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
from itertools import permutations
from pathlib import Path
import json
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE.parent/"cognition001"))
sys.path.insert(0,str(HERE.parent/"cognition002"))
sys.path.insert(0,str(HERE.parent/"cognition003"))
from circuit import AppState, admission, native_affordance, seal
from bridge import validate_understory_owner
from resurface import _native_graph

DEV_SEEDS=(72001,72011,72021,72031)
TEST_SEEDS=tuple(99101+47*i for i in range(32))
REGIMES=("isomorphic","renamed_permuted","partial_observation",
         "false_friend","echo_source","unfamiliar_structure")
POLICIES=("motif_council","classical_graph_edit","classical_exact_iso","lexical")
NODES=5
MAX_PROBES=2
FIXES=("dampen_cycle","widen_choke","refresh_measurement",
       "synchronize_clocks","reserve_capacity")
UNSEEN_FIX="unobserved_other_fix"
RELATIONS=(
    ((0,1,"push"),(1,2,"delay"),(2,0,"loop"),(2,3,"amplify"),(3,4,"harm")),
    ((0,2,"feed"),(1,2,"feed"),(2,3,"block"),(3,4,"harm")),
    ((0,1,"observe"),(1,2,"delay"),(2,3,"decide"),(0,4,"change"),(4,3,"harm")),
    ((0,2,"signal"),(1,2,"signal"),(2,3,"wait"),(3,4,"harm")),
    ((0,2,"need"),(1,2,"need"),(2,3,"exhaust"),(3,4,"harm")),
)
SOURCE_DOMAINS=(
    ("irrigation",("flume","faucet","cistern","furrow","waterwheel")),
    ("music",("refrain","tambour","metronome","chord","soundboard")),
    ("community",("supper","volunteer","bulletin","pantry","usher")),
    ("network",("socket","router","cacheline","packet","backplane")),
    ("workshop",("lathe","sprocket","anvil","vise","caliper")),
)
TARGET_WORDS=("bollard","gangway","cargo","tidepool","winch")
STATE=AppState(True,True,50,False,94,True,38.,.12,"abundant")
OWNER="INDEPENDENT_SYNTHETIC_CAUSAL_OUTCOME_OWNER"
MAX_EDIT=1


def seeded(seed,label,n):
    return int(sha256(f"cognition004:{seed}:{label}".encode()).hexdigest()[:14],16)%n


def baseline(seed,regime):
    if seed not in DEV_SEEDS+TEST_SEEDS or regime not in REGIMES:
        raise ValueError("UNREGISTERED_NEW_TEST")
    pattern=seeded(seed,"which-pattern",len(FIXES))
    library=[]
    for i,edges in enumerate(RELATIONS):
        roots=(f"origin-{seed}-source-{i}-a",f"origin-{seed}-source-{i}-b")
        if regime=="echo_source" and i==pattern:
            roots=(roots[0],roots[0])
        domain,words=SOURCE_DOMAINS[i]
        library.append({"sid":f"past-{seed}-{i}","day":"2026-11-10",
                        "domain":domain,"entities":list(words),"edges":[list(e) for e in edges],
                        "historical_verified_fix":FIXES[i],
                        "historical_witness_roots":list(roots),
                        "status":"SOURCE_WORLD_TESTED_ONLY"})
    # Incident noun list is completely disjoint from every source story.
    words=list(TARGET_WORDS)
    permutation=list(range(NODES))
    if regime!="isomorphic":
        permutation.sort(key=lambda i:sha256(f"{seed}:alias:{i}".encode()).hexdigest())
    edges=[[permutation[a],permutation[b],relation] for a,b,relation in RELATIONS[pattern]]
    if regime in ("partial_observation","false_friend"):
        # The visible history looks identical in these two regimes; hidden
        # real causal efficacy differs. The owner test must discriminate it.
        edges.pop()
    if regime=="unfamiliar_structure":
        edges=[[0,1,"unknown"],[1,2,"foreign"],[2,3,"inverse"],[3,4,"isolated"]]
    event={"incident_id":f"incident-{seed}","day":"2026-11-11",
           "domain":"harbor","entities":words,"edges":edges,
           "has_explicit_memory_search_request":False,
           "status":"NEW_OBSERVATION_NOT_REPAIR_FACT"}
    return library,event,pattern


def edit_cost(source_edges,target_edges):
    """Strong exact directed edge-type graph edit search across ALL 5! maps."""
    source={tuple(e) for e in source_edges}
    target={tuple(e) for e in target_edges}
    best=999
    operations=0
    for mapping in permutations(range(NODES)):
        represented={(mapping[a],mapping[b],r) for a,b,r in source}
        operations+=1
        difference=len(represented.symmetric_difference(target))
        if difference<best:
            best=difference
            if best==0:
                # Keep iteration invariant by not breaking; operator count
                # reflects the entire fixed search space for every method.
                pass
    return best,operations


def candidates(library,event,strict=False):
    out=[]
    comparisons=0
    for i,source in enumerate(library):
        score,ops=edit_cost(source["edges"],event["edges"])
        comparisons+=ops
        accepted=score==0 if strict else score<=MAX_EDIT
        if accepted:
            roots=source["historical_witness_roots"]
            out.append({"sid":source["sid"],"index":i,
                        "proposed_fix":source["historical_verified_fix"],
                        "distance":score,"roots":roots,
                        "independent":len(set(roots))==2,
                        "status":"PENCIL_HYPOTHETICAL_TRANSFER"})
    return sorted(out,key=lambda row:(row["distance"],row["index"])),comparisons


def build_prepared(library):
    """Both MOTIF and strong conventional control may prepare identical data."""
    # Explicit immutable rehearsal; never leaks new incident or owner world.
    return json.loads(json.dumps(library,sort_keys=True))


def _source_spec(source):
    return {"source_class":"unresolved-receipt",
            "locator":{"system":"COGNITION-004 invented source",
                       "coordinate":source["sid"],"revision":"synthetic-v1",
                       "resolution":"one prior verified simulated experience"},
            "observed_at":source["day"],
            "acquisition":"programmer-authored synthetic source-world observation",
            "excerpt":"Prior source-world fix was simulator tested; target applicability unknown.",
            "digest":"sha256:"+seal(source),
            "access":"public","export":"portable","authority":"none"}


def free_graph_proposal(source,event,candidate):
    """Validate an invented cross-world relation using NATIVE Free Graph IDs."""
    rec_id,pkt_id,validate,neighbors=_native_graph()
    prior=_source_spec(source)
    prior["id"]=rec_id("source",prior)
    today={"source_class":"unresolved-receipt",
           "locator":{"system":"COGNITION-004 invented target",
                      "coordinate":event["incident_id"],
                      "revision":"synthetic-v1",
                      "resolution":"new task observation; unknown intervention"},
           "observed_at":event["day"],"acquisition":"simulated new incident",
           "excerpt":"Unprompted target incident; no tested outcome yet.",
           "digest":"sha256:"+seal(event),
           "access":"public","export":"portable","authority":"none"}
    today["id"]=rec_id("source",today)
    nodes=[]
    for kind,label,refs in (
        ("artifact","Source-world case "+source["sid"],[prior["id"]]),
        ("artifact","Observed target case "+event["incident_id"],[today["id"]]),
        ("question","Would a source-world intervention transfer under this structure?",
         [prior["id"],today["id"]])):
        node={"kind":kind,"label":label,"status":"unresolved","source_ids":refs,
              "extensions":{"candidate_intervention_is_unverified":True}}
        node["id"]=rec_id("node",node)
        nodes.append(node)
    links=[]
    for x,y in ((0,2),(2,1)):
        l={"from":nodes[x]["id"],"to":nodes[y]["id"],"verb":"connects",
           "qualifier":"prospective-structural-analogy-not-causal-confirmation",
           "status":"unresolved","source_ids":[prior["id"],today["id"]],
           "authority":"none"}
        l["id"]=rec_id("link",l)
        links.append(l)
    packet={"schema":"free-graph.packet/v0",
            "purpose":"Invented structural analogy, witness-provenance only",
            "modes":["re-enter","seed"],
            "scope":{"task":"Test whether source-world strategy transfers to target incident",
                     "worlds":[source["domain"],event["domain"]],
                     "as_of":event["day"],"resolution":"unknown target efficacy"},
            "task_world_cut":{"status":"unresolved",
                "selected_ids":[x["id"] for x in [prior,today,*nodes,*links]],
                "owner_head_source_ids":[],
                "omitted":[{"door":"private MEMENTO owner gate",
                            "reason":"not authorized to import actual records or admit facts"}],
                "rationale":"Matched structure creates a research question, not a causal claim"},
            "sources":[prior,today],"nodes":nodes,"links":links,
            "residual_fog":["Typed ontology is programmer-supplied.",
                            "Target repair requires a separate positive TEST receipt."],
            "non_imports":["No real user history or MEMENTO private files accessed.",
                           "No hidden target answer, canonical adoption or software action."],
            "extensions":{"synthetic":True,"status":"PENCIL_ONLY",
                          "source_roots_independent":candidate["independent"]}}
    packet["packet_id"]=pkt_id(packet)
    errors=validate(packet)
    if errors:raise AssertionError("NATIVE_FREE_GRAPH_REJECTED "+str(errors))
    # Real native graph neighborhood traversal, not copied algorithm.
    nb=neighbors(packet,nodes[2]["id"],depth=1)
    if validate(nb):raise AssertionError("NATIVE_FREE_GRAPH_NEIGHBORS_INVALID")
    return packet,nb


def native_motif_test_affordances(rows):
    """Execute actual MOTIF-003 on hypothetical tests, no oracle ranking."""
    native=native_affordance()
    base=frozenset({("status","not-tested")})
    def possibilities(world, _):
        for i,row in enumerate(rows):
            key=("skill",f"possible-owner-test-{i}")
            if key not in world:
                yield (f"ask-test-{i}",(row["sid"],),
                       world|frozenset({key}))
    options=native.analyze_first_moves(
        base,(),possibilities,
        lambda future,initial:len(future-initial),horizon=1,max_worlds=32)
    if len(options)!=len(rows):
        raise AssertionError("NATIVE_MOTIF003_AFFORDANCE_COUNT_MISMATCH")
    return len(options)


class Owner:
    """Separate simulator observes real test/repair; never supplies hidden truth."""
    def __init__(self,correct_action):
        self._correct=correct_action
        self.probes=0
        self.positive=set()
        self.receipts=[]
        self.repaired=False
    def _receipt(self,kind,**fields):
        row={"kind":kind,"source":OWNER,
             "sequence":len(self.receipts)+1,**fields}
        row["seal"]=seal(row)
        self.receipts.append(row)
        return row
    def test(self,action):
        if self.probes>=MAX_PROBES:raise RuntimeError("PROBE_LIMIT_REACHED")
        if action not in FIXES:raise ValueError("UNSUPPORTED_CANDIDATE")
        self.probes+=1
        valid=action==self._correct
        if valid:self.positive.add(action)
        return self._receipt("TEST",action=action,positive=valid,
                             sealed_simulator=True)
    def repair(self,action):
        if action not in self.positive:raise ValueError("NEED_POSITIVE_INDEPENDENT_TEST")
        if self.repaired:raise RuntimeError("DUPLICATE_REPAIR")
        self.repaired=action==self._correct
        return self._receipt("REPAIR",action=action,
                             independently_verified=self.repaired)
    def evaluation(self):
        return {"expected_action_evaluator_only":self._correct,
                "verified":self.repaired,"receipts":self.receipts}


def understory_envelope(source,event):
    """Synthetic and bounded, validated by actual PRIVATE MEMENTO only when mounted."""
    a,b=source["historical_witness_roots"]
    common={"schema":"memento.understory-record/v0",
            "observer":"motif-synthetic-observer"}
    old=[]
    for i,root in enumerate((a,b)):
        instant=f"2026-11-10T{8+i:02d}:00:00Z"
        old.append({**common,"id":f"cog004-contact-{i}",
                    "family":"contact","recorded_at":instant,
                    "sensed_at":instant,
                    "occurrence_ref":f"synthetic:{root}",
                    "evidence_refs":[f"synthetic:{source['sid']}"]})
    association={**common,"id":"cog004-association",
                 "family":"association","recorded_at":"2026-11-10T11:00:00Z",
                 "evidence_refs":[f"synthetic:{source['sid']}"],
                 "member_refs":[r["id"] for r in old],
                 "relation_hint":"Possible structural relation; unverified",
                 "status":"unresolved"}
    activation={**common,"id":"cog004-activation",
                "family":"activation","recorded_at":"2026-11-11T12:00:00Z",
                "activated_at":"2026-11-11T12:00:00Z",
                "trace_refs":[association["id"]],
                "trigger_ref":f"synthetic:{event['incident_id']}",
                "descendant_projection_ref":"synthetic:analogical-test-proposal",
                "evidence_refs":[f"synthetic:{event['incident_id']}"]}
    return {"schema":"motif.understory-contemplation/v0",
            "source_mode":"synthetic-fixture",
            "owner_permission":"read-only-validation",
            "admission":"none","records":[*old,association,activation]}


def run_case(seed,regime,policy,*,state=STATE,memento_root=None,full=False):
    if policy not in POLICIES:raise ValueError("UNKNOWN_POLICY")
    library,incident,pattern=baseline(seed,regime)
    historical_seal=seal(library)
    # The owner chooses target truth, never disclosed to retrieval.
    correct=(UNSEEN_FIX if regime in ("false_friend","unfamiliar_structure")
             else FIXES[pattern])
    owner=Owner(correct)
    gate=admission(state,1) if policy in ("motif_council","classical_graph_edit",
                                         "classical_exact_iso") else {"action":"hold"}
    idle=gate["action"]=="run_here"
    prepared=(build_prepared(library) if idle else None)
    if policy=="lexical":
        # Weak diagnostic: no source/target word overlap by construction.
        rows=[];edit_operations=0
    else:
        rows,edit_operations=candidates(
            prepared or library,incident,strict=policy=="classical_exact_iso")
    eligible=[x for x in rows if x["independent"]]
    echoes=[x for x in rows if not x["independent"]]
    # Structural comparison count happens at event time here; stronger
    # graph-indexed classical baseline gets exactly the same opportunities.
    motif_options=(native_motif_test_affordances(eligible)
                   if policy=="motif_council" and idle else 0)
    native_graph_checks=0
    graph_ids=[]
    for candidate in eligible[:MAX_PROBES]:
        packet,neighborhood=free_graph_proposal(
            library[candidate["index"]],incident,candidate)
        native_graph_checks+=1
        graph_ids.append(packet["packet_id"])
    native_memento={"status":"NOT_INVOKED_FOR_POLICY","validated":False}
    if policy=="motif_council" and eligible and idle:
        env=understory_envelope(library[eligible[0]["index"]],incident)
        native_memento=validate_understory_owner(env,memento_root)
    attempted=[]
    for candidate in eligible[:MAX_PROBES]:
        receipt=owner.test(candidate["proposed_fix"])
        attempted.append({"sid":candidate["sid"],"distance":candidate["distance"],
                          "source_roots":candidate["roots"],
                          "owner_test_receipt":receipt})
        if receipt["positive"]:
            owner.repair(candidate["proposed_fix"])
            break
    evaluation=owner.evaluation()
    assert seal(library)==historical_seal,"OLD_SOURCE_HISTORY_CHANGED"
    source_nouns={n for x in library for n in x["entities"]}
    target_nouns=set(incident["entities"])
    overlap=source_nouns&target_nouns
    if overlap:raise AssertionError("CROSS_DOMAIN_NOUN_LEAKAGE")
    result={
        "seed":seed,"regime":regime,"policy":policy,
        "source_domain_count":len(library),
        "target_domain":incident["domain"],
        "target_entity_overlap":len(overlap),
        "unprompted_incident":not incident["has_explicit_memory_search_request"],
        "typed_ontology_shared":True,
        "admitted_idle":idle,
        "historical_archive_unchanged":True,
        "graph_candidates":len(rows),
        "credible_candidates":len(eligible),
        "source_echo_rejections":len(echoes),
        "native_free_graph_checks":native_graph_checks,
        "native_graph_packet_ids":graph_ids,
        "native_motif003_test_affordances":motif_options,
        "native_private_understory":native_memento,
        "hypotheses_tested":[a["sid"] for a in attempted],
        "owner_tests":owner.probes,
        "owner_repairs":int(owner.repaired),
        "verified_success":evaluation["verified"],
        "unverified_repairs":0,
        "abstained":not evaluation["verified"],
        "owner_receipts":evaluation["receipts"],
        "expected_action_evaluator_only":evaluation["expected_action_evaluator_only"],
        "trigger_comparison_ops":edit_operations,
        "idle_index_entries":len(prepared) if prepared is not None else 0,
        "real_external_actions":0,"model_calls":0,
        "personal_data_processed":False,"app_deployed":False,
        "source_history_status":"UNALTERED",
        "detail":attempted if full else [],
    }
    result["seal"]=seal(result)
    return result


def benchmark(split="development",full=False):
    if split not in ("development","heldout"):raise ValueError("BAD_SPLIT")
    seeds=DEV_SEEDS if split=="development" else TEST_SEEDS
    rows=[run_case(seed,regime,policy,full=full)
          for seed in seeds for regime in REGIMES for policy in POLICIES]
    summary={}
    comparisons=[]
    for regime in REGIMES:
        summary[regime]={}
        for policy in POLICIES:
            group=[r for r in rows if r["regime"]==regime and r["policy"]==policy]
            summary[regime][policy]={
                "cases":len(group),
                "verified_repairs":sum(r["verified_success"] for r in group),
                "unverified_repairs":sum(r["unverified_repairs"] for r in group),
                "independent_candidate_count":sum(r["credible_candidates"] for r in group),
                "echoes_excluded":sum(r["source_echo_rejections"] for r in group),
                "owner_tests":sum(r["owner_tests"] for r in group),
                "native_graph_checks":sum(r["native_free_graph_checks"] for r in group),
                "native_motif003_affordances":sum(r["native_motif003_test_affordances"] for r in group)}
        for seed in seeds:
            lookup={r["policy"]:r for r in rows if r["seed"]==seed and r["regime"]==regime}
            comparisons.append({
                "seed":seed,"regime":regime,
                "motif_minus_strong_classical_success":
                    int(lookup["motif_council"]["verified_success"])
                    -int(lookup["classical_graph_edit"]["verified_success"]),
                "motif_minus_strong_classical_tests":
                    lookup["motif_council"]["owner_tests"]
                    -lookup["classical_graph_edit"]["owner_tests"]})
    out={"experiment":"COGNITION-004","split":split,
         "source":"AUTHOR_WRITTEN_TYPED_ANALOGY_SIMULATOR",
         "seeds":list(seeds),"regimes":list(REGIMES),
         "policies":list(POLICIES),"cases":len(rows),
         "summary":summary,"paired":comparisons,
         "notes":"No external dataset or model learning; shared typed ontology; private owner absent in public CI",
         "real_external_actions":0,"model_calls":0,
         "rows":rows}
    out["seal"]=seal(out)
    return out


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--split",choices=("development","heldout"),default="development")
    parser.add_argument("--full",action="store_true")
    parser.add_argument("--memento-root",default=None)
    parser.add_argument("--one-seed",type=int,default=None)
    parser.add_argument("--regime",choices=REGIMES,default="renamed_permuted")
    args=parser.parse_args()
    if args.one_seed is not None:
        out=run_case(args.one_seed,args.regime,"motif_council",
                     memento_root=args.memento_root,full=True)
    else:
        out=benchmark(args.split,args.full)
    print(json.dumps(out,indent=2,sort_keys=True))
