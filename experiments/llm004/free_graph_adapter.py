"""LLM-004 public Free Graph v0 *projection* of MOTIF-owned reason memory.

Pinned source owner: the-static-collective/free-graph@ec0ad8743c5faac3f3675760bbafcbcb1df846c1.
It is not an owning-world API call, does not update Free Graph, and NEVER
constitutes owner-local authority. A many-to-many hyperedge is reified as a
portable artifact node joined with Free Graph's existing five relation verbs.
"""
from __future__ import annotations
import copy,hashlib,json
from hypermap import ReasonHypermap,canonical,hash_of

FREE_GRAPH_COMMIT="ec0ad8743c5faac3f3675760bbafcbcb1df846c1"
VERBS={"connects","descends-from","tests","bears-on","constitutes"}
KIND={"hypothesis":"claim","observation":"testimony","prediction":"claim",
      "test":"test","receipt":"receipt","counterexample":"claim",
      "revision":"artifact","question":"question","hyperedge":"artifact"}

def record_id(prefix,record):
    item={k:v for k,v in record.items() if k!="id"}
    return f"{prefix}:sha256:{hashlib.sha256(canonical(item).encode()).hexdigest()}"

def packet_from_hypermap(hmap):
    if not isinstance(hmap,ReasonHypermap):raise ValueError("NOT_REASON_HYPERMAP")
    if hmap.active is not None:raise ValueError("PROPOSED_TEST_NOT_YET_RESOLVED")
    src=[];nodes=[];links=[]
    src_map={};node_map={}
    for root,local in sorted(hmap.sources.items()):
        content=canonical(local["content"])
        # Source excerpt never holds an actual hidden owner rule or private user info.
        s={"source_class":local["kind"],
           "locator":{"system":"MOTIF-LMM004 authored simulator",
               "coordinate":root,"revision":"2026-11-12 synthetic-v0",
               "resolution":"one independently labeled authored receipt"},
           "observed_at":"2026-11-12",
           "acquisition":"author-designed bounded synthetic experiment",
           "digest":"sha256:"+hash_of(content),
           "access":"public","export":"portable",
           "authority":"source-local",
           "excerpt":content[:2400],
           "extensions":{"source_root":root,"synthetic":True,
                         "portable_not_authority":True}}
        s["id"]=record_id("fgs",s)
        src_map[root]=s["id"];src.append(s)
    for id,local in sorted(hmap.nodes.items()):
        roots=[src_map[r] for r in local["source_roots"]]
        n={"kind":KIND[local["kind"]],"label":local["label"],
           "status":local["status"],"source_ids":roots,
           "extensions":{"motif_local_node":id,"motif_kind":local["kind"],
                         "local_metadata":local["metadata"],"public_fixture":True}}
        if n["kind"]=="claim":
            n["claim_class"]="mathematical" if local["kind"]=="hypothesis" else "inferential"
            n["witness_requirement"]="owner-defined"
        n["id"]=record_id("fgn",n)
        nodes.append(n);node_map[id]=n["id"]
    def node(kind,label,status,source_ids,extensions):
        n={"kind":kind,"label":label,"status":status,
           "source_ids":list(source_ids),"extensions":copy.deepcopy(extensions)}
        n["id"]=record_id("fgn",n);nodes.append(n)
        return n["id"]
    def link(frm,to,verb,qualifier,status,sources,extra=None):
        if verb not in VERBS:raise ValueError("SIXTH_VERB_FORBIDDEN")
        item={"from":frm,"to":to,"verb":verb,"qualifier":qualifier,
              "status":status,"source_ids":sorted(set(sources)),
              "authority":"none"}
        item.update(extra or {})
        item["id"]=record_id("fgl",item);links.append(item)
    for hid,edge in sorted(hmap.edges.items()):
        roots=[src_map[r] for r in edge["source_roots"]]
        h=node("artifact","Hyperedge: "+edge["relation"],
               edge["status"],roots,
               {"motif_hyperedge":hid,"local_relation":edge["relation"],
                "metadata":edge["metadata"],"tails":len(edge["tails"]),
                "heads":len(edge["heads"]),"reified_hyperedge":True})
        for frm in edge["tails"]:
            link(node_map[frm],h,"connects","hyperedge-tail",edge["status"],roots,
                 {"extensions":{"local_relation":edge["relation"],"role":"tail"}})
        for to in edge["heads"]:
            link(h,node_map[to],"connects","hyperedge-head",edge["status"],roots,
                 {"extensions":{"local_relation":edge["relation"],"role":"head"}})
        if edge["relation"] in ("report-bears-on-rivals","report-supports-rivals"):
            # Tested synthetic *reports* bear on hypotheses. Not owner-current truth.
            bearing=edge["metadata"]["bearing"]
            for other in edge["heads"]:
                link(node_map[edge["tails"][0]],node_map[other],
                     "bears-on","synthetic-owner-report-not-truth",
                     "tested",roots,{"bearing":bearing,"extensions":{
                          "local_relation":edge["relation"],"not_authority":True}})
        if edge["relation"]=="test-revises-possibilities":
            originals=[a for a in edge["tails"] if hmap.nodes[a]["kind"]=="hypothesis"]
            probes=[a for a in edge["tails"] if hmap.nodes[a]["kind"]=="test"]
            for probe in probes:
                for hyp in originals:
                    link(node_map[probe],node_map[hyp],"tests",
                         "synthetic-probe-tests-favorite",edge["status"],roots)
            revisions=[a for a in edge["heads"] if hmap.nodes[a]["kind"]=="revision"]
            for revision in revisions:
                for probe in probes:
                    link(node_map[revision],node_map[probe],"descends-from",
                         "synthetic-posterior-revision-derived-from-test",edge["status"],roots)
    allids=[s["id"] for s in src]+[n["id"] for n in nodes]+[l["id"] for l in links]
    if len(set(allids))!=len(allids):raise ValueError("DUPLICATE_FREE_GRAPH_RECORD")
    p={"schema":"free-graph.packet/v0",
       "purpose":"Public-safe historical traversal of MOTIF Reason Hypermap fictional counterexample inquiry; no authority transport.",
       "modes":["seed","metabolize"],
       "scope":{"task":"Explain what a provisional mistake changed under one bounded synthetic test.",
                "worlds":["MOTIF-owned synthetic LLM-004","Free Graph portable projection"],
                "as_of":"2026-11-12",
                "resolution":"one pinned authored independent owner fixture"},
       "task_world_cut":{"status":"sufficient","selected_ids":allids,
            "owner_head_source_ids":[],"omitted":[
              {"door":"Production JAR;VIS or private MEMENTO",
               "reason":"Not required, not authorized, and not imported."},
              {"door":"Real-world owner gate receipts",
               "reason":"Synthetic simulator contains no authority to adopt actions."}],
            "rationale":"All nodes and links derive only from the current fictional MOTIF fixture; no owner current-state gate is requested."},
       "sources":src,"nodes":nodes,"links":links,
       "residual_fog":["Synthetic owner reports may be noisy; historical bearing is not truth.",
                      "No external task generalization or real-world authorization established."],
       "non_imports":["No private personal sources, coordinates, photographs or MEMENTO.",
                      "No real JAR;VIS permissions, current project state or execution.",
                      "No owner-local Free Graph constitution and no sixth relation verb."],
       "extensions":{"producer":"MOTIF LLM-004 public fixture",
             "motif_state_id":hmap.state_id(),
             "free_graph_source_commit":FREE_GRAPH_COMMIT,
             "projection_only":True,"no_promotion":True}}
    p["packet_id"]=record_id("fgp",{k:v for k,v in p.items() if k!="packet_id"})
    return p
