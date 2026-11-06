"""MOTIF THOUGHT-008: parallel evidence-bound projections of non-fungible thoughts.

Reads THOUGHT-007 snapshot without mutation. Geometric positions cannot create
relations, concept equivalence, proof, PEN status or authority. No network I/O.
"""
from __future__ import annotations

import copy
from collections import defaultdict, deque
from hashlib import sha256
from json import dumps
from math import cos, sin, pi, sqrt, hypot, isfinite

SCHEMA = "motif.thought-multiview.v1"
LENSES = ("association", "dependency", "tension", "affordance", "flower_hex", "NONE")
RELATIONS = {"associated", "requires", "enables", "contradicts", "precedes"}
STATUSES = {"AUTHORED", "HYPOTHESIS_ONLY"}
MAX_MANIFESTATIONS = 80
MAX_RELATIONS = 300

class ViewError(ValueError):
    pass


def canonical(obj):
    return dumps(obj, sort_keys=True, ensure_ascii=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def digest(obj):
    return sha256(canonical(obj)).hexdigest()


def _text(s, what, limit=200):
    if not isinstance(s, str) or not s.strip() or len(s) > limit:
        raise ViewError(f"invalid {what}")
    return s


def _unique(items, what):
    ids = [x.get("id") for x in items]
    if len(ids) != len(set(ids)):
        raise ViewError(f"duplicate {what} ids")


class ThoughtViews:
    def __init__(self, field_snapshot, relations):
        """snapshot: exact THOUGHT-007 output; relations: attributed read-only input.

        A stated origin is not an authenticated independent witness. Existing
        ledger PEN commitments are neither inferred nor modified here.
        """
        if not isinstance(field_snapshot, dict) or not isinstance(relations, list):
            raise ViewError("field snapshot and relation list required")
        self._original = copy.deepcopy(field_snapshot)
        self._relations = copy.deepcopy(relations)
        semantic = self._original.get("semantic", {})
        if semantic.get("schema") != "motif.thought-field.semantics.v1":
            raise ViewError("requires THOUGHT-007 semantic snapshot")
        concepts = semantic.get("concepts", [])
        manifests = semantic.get("manifestations", [])
        views = self._original.get("views", [])
        placements = self._original.get("placements", [])
        if (not all(isinstance(x, list) for x in (concepts, manifests, views, placements))
                or len(manifests) > MAX_MANIFESTATIONS or len(relations) > MAX_RELATIONS
                or len(placements) > 400 or len(views) > 100):
            raise ViewError("invalid or excessive field dimensions")
        for block, name in ((concepts, "concept"), (manifests, "manifestation"),
                            (views, "view"), (placements, "placement")):
            if not all(isinstance(x, dict) and isinstance(x.get("id"), str) for x in block):
                raise ViewError(f"invalid {name} records")
            _unique(block, name)
        self.concepts = {x["id"]: x for x in concepts}
        self.manifests = {x["id"]: x for x in manifests}
        self.source_views = {x["id"]: x for x in views}
        self.source_placements = placements
        for m in manifests:
            if m.get("concept_id") not in self.concepts:
                raise ViewError("manifestation has unknown concept")
        for v in views:
            if v.get("lens") not in LENSES:
                raise ViewError("unknown source lens")
        for p in placements:
            if (p.get("manifestation_id") not in self.manifests or
                    p.get("view_id") not in self.source_views or type(p.get("active")) is not bool):
                raise ViewError("invalid source placement reference")
            if p["active"]:
                view_lens = self.source_views[p["view_id"]]["lens"]
                x,y=p.get("x"),p.get("y")
                if view_lens == "NONE":
                    if x is not None or y is not None:
                        raise ViewError("NONE cannot have coordinates")
                elif (type(x) not in (float,int) or type(y) not in (float,int) or
                      not isfinite(x) or not isfinite(y) or abs(x)>1e6 or abs(y)>1e6):
                    raise ViewError("invalid source coordinates")
        self.relations = []
        ids = set()
        for r in self._relations:
            if not isinstance(r, dict) or set(r) != {
                    "id", "source", "target", "predicate", "origin", "status"}:
                raise ViewError("relation requires six explicit fields")
            rid = _text(r["id"], "relation id")
            if rid in ids:
                raise ViewError("duplicate relation id")
            ids.add(rid)
            if r["source"] not in self.manifests or r["target"] not in self.manifests:
                raise ViewError("relation endpoints must be known manifestations")
            if r["source"] == r["target"]:
                raise ViewError("self relation not supported")
            if r["predicate"] not in RELATIONS or r["status"] not in STATUSES:
                raise ViewError("unrecognized relation predicate/status")
            _text(r["origin"], "claimed origin")
            self.relations.append(copy.deepcopy(r))
        self.relations.sort(key=lambda x:x["id"])
        # Input digest is a provenance fingerprint, *not* verification of source truth.
        self.input_digest = digest({"semantic": semantic, "relations": self.relations})
        self.source_snapshot_digest = digest(field_snapshot)

    def _authored(self, predicate):
        return [r for r in self.relations
                if r["status"] == "AUTHORED" and r["predicate"] == predicate]

    def association_questions(self):
        """Classical common-neighbor baseline. Questions, not new graph edges."""
        neighbors = defaultdict(lambda: defaultdict(set))
        for r in self._authored("associated"):
            a,b,o=r["source"],r["target"],r["origin"]
            neighbors[a][b].add(o)
            neighbors[b][a].add(o)
        existing = {frozenset((r["source"], r["target"]))
                    for r in self._authored("associated")}
        nodes=sorted(self.manifests)
        answer=[]
        for i,a in enumerate(nodes):
            for b in nodes[i+1:]:
                if frozenset((a,b)) in existing:
                    continue
                via=sorted(set(neighbors[a]) & set(neighbors[b]))
                roots={root for m in via for root in neighbors[a][m] | neighbors[b][m]}
                if len(via)>=2 and len(roots)>=2:
                    answer.append({"source":a,"target":b,"via":via,
                                   "claimed_roots":sorted(roots),
                                   "status":"QUESTION_ONLY",
                                   "meaning":"shared authored neighbors; direct link NOT established"})
        return answer

    def dependencies(self, anchor=None):
        deps = defaultdict(set)
        for r in self._authored("requires"):
            deps[r["source"]].add(r["target"])
        cycles=[]
        color={}
        stack=[]
        def visit(node):
            color[node]=1;stack.append(node)
            for nxt in sorted(deps[node]):
                if color.get(nxt,0)==0:
                    visit(nxt)
                elif color.get(nxt)==1:
                    cyc=stack[stack.index(nxt):]+[nxt]
                    if cyc not in cycles:cycles.append(cyc)
            stack.pop();color[node]=2
        for node in sorted(self.manifests):
            if not color.get(node):visit(node)
        reachable=[]
        if anchor is not None:
            if anchor not in self.manifests:raise ViewError("unknown anchor")
            pending=deque([anchor]);seen={anchor}
            while pending:
                x=pending.popleft()
                for y in sorted(deps[x]):
                    if y not in seen:
                        seen.add(y);reachable.append(y);pending.append(y)
        return {"required_edges":sorted([r["id"] for r in self._authored("requires")]),
                "cycles":cycles,"anchor":anchor,"required_by_anchor":reachable,
                "interpretation":"declared prerequisites, not independently verified necessity"}

    def tensions(self):
        return [{"relation_id":r["id"],"between":[r["source"],r["target"]],
                 "claimed_origin":r["origin"],"unresolved":True}
                for r in self._authored("contradicts")]

    def affordances(self, anchor=None):
        if anchor is not None and anchor not in self.manifests:
            raise ViewError("unknown anchor")
        outgoing=defaultdict(set); requirements=defaultdict(set)
        for r in self._authored("enables"):
            outgoing[r["source"]].add(r["target"])
        for r in self._authored("requires"):
            requirements[r["source"]].add(r["target"])
        if anchor is None:
            return {"anchor":None,"conditional_reach":[],"interpretation":"no anchor; no action proposed"}
        seen={anchor};dist={anchor:0};q=deque([anchor]);candidates=[]
        while q:
            x=q.popleft()
            for y in sorted(outgoing[x]):
                if y in seen:continue
                seen.add(y);dist[y]=dist[x]+1;q.append(y)
                candidates.append(y)
        return {"anchor":anchor,"conditional_reach":[{
            "manifestation_id":n,"enables_hops":dist[n],
            "other_declared_requirements":sorted(requirements[n] - seen),
            "status":"CONDITIONAL_ONLY"
        } for n in candidates],
        "interpretation":"reachability in authored toy rules, not feasible real-world action"}

    def evidence_index(self, anchor=None):
        return {"associations":[r["id"] for r in self._authored("associated")],
                "bridge_questions":self.association_questions(),
                "dependency":self.dependencies(anchor),
                "tension":self.tensions(),
                "affordance":self.affordances(anchor),
                "hypothesis_links":[r["id"] for r in self.relations if r["status"]=="HYPOTHESIS_ONLY"],
                "external_authority":"NONE"}

    def _coordinates(self, lens, anchor=None, seed=0):
        if lens=="NONE":return {}
        ids=sorted(self.manifests)
        n=len(ids)
        if not n:return {}
        if type(seed) is not int or not -100000<=seed<=100000:
            raise ViewError("seed must be bounded integer")
        order=sorted(ids,key=lambda x:(sha256((str(seed)+":"+x).encode()).hexdigest(),x))
        if anchor in order: order.remove(anchor);order.insert(0,anchor)
        if lens=="flower_hex":
            coords=[(0,0)];radius=1
            while len(coords)<n:
                coords.extend(sorted([(q,r) for q in range(-radius,radius+1)
                                       for r in range(-radius,radius+1)
                                       if max(abs(q),abs(r),abs(q+r))==radius]))
                radius+=1
            return {id:(q+r/2,sqrt(3)*r/2) for id,(q,r) in zip(order,coords)}
        if lens=="tension":
            conflict_ids={y for r in self._authored("contradicts")
                          for y in (r["source"],r["target"])}
            left=sorted(conflict_ids);right=sorted(set(ids)-conflict_ids)
            return {**{x:(-2,float(i-len(left)/2)) for i,x in enumerate(left)},
                    **{x:(2,float(i-len(right)/2)) for i,x in enumerate(right)}}
        if lens=="dependency":
            deps=self.dependencies(anchor)
            prioritized=deps["required_by_anchor"] if anchor else []
            seq=[anchor]+prioritized if anchor else []
            seq=[x for x in seq if x is not None]+[x for x in ids if x not in seq]
            return {x:(float(i%4)*1.75, float(i//4)*1.5) for i,x in enumerate(seq)}
        if lens=="affordance":
            reachable=self.affordances(anchor)["conditional_reach"] if anchor else []
            priorities=[anchor]+[x["manifestation_id"] for x in reachable] if anchor else []
            seq=[x for x in priorities if x is not None]+[x for x in ids if x not in priorities]
            return {x:(3*cos(2*pi*i/max(1,n)),3*sin(2*pi*i/max(1,n))) for i,x in enumerate(seq)}
        # Deterministic finite force-directed 2D *display*. It has no epistemic status.
        pos={x:[2*cos(2*pi*i/n),2*sin(2*pi*i/n)] for i,x in enumerate(order)}
        edges=[r for r in self._authored("associated")]
        for iteration in range(80):
            shift={x:[0.0,0.0] for x in ids}
            for i,x in enumerate(ids):
                for y in ids[i+1:]:
                    dx=pos[x][0]-pos[y][0];dy=pos[x][1]-pos[y][1]
                    d=max(.01,hypot(dx,dy));f=.04/(d*d)
                    shift[x][0]+=dx/d*f;shift[x][1]+=dy/d*f
                    shift[y][0]-=dx/d*f;shift[y][1]-=dy/d*f
            for edge in edges:
                a,b=edge["source"],edge["target"]
                dx=pos[b][0]-pos[a][0];dy=pos[b][1]-pos[a][1]
                d=max(.01,hypot(dx,dy));f=.025*d
                shift[a][0]+=dx/d*f;shift[a][1]+=dy/d*f
                shift[b][0]-=dx/d*f;shift[b][1]-=dy/d*f
            for x in ids:
                dx,dy=shift[x];d=hypot(dx,dy)
                if d:
                    scale=min(d, .07*(1-iteration/80)+.006)/d
                    pos[x][0]+=dx*scale;pos[x][1]+=dy*scale
        return {x:(round(pos[x][0],6),round(pos[x][1],6)) for x in ids}

    def project(self, lens, *, anchor=None, seed=0):
        if lens not in LENSES:
            raise ViewError("unsupported lens")
        if anchor is not None and anchor not in self.manifests:
            raise ViewError("unknown anchor")
        coords=self._coordinates(lens,anchor=anchor,seed=seed)
        placements=[]
        for p in sorted(self.source_placements,key=lambda x:x["id"]):
            if not p["active"] or self.source_views[p["view_id"]]["lens"]!=lens:
                continue
            m=self.manifests[p["manifestation_id"]]
            placements.append({"placement_id":"source:"+p["id"],
                "manifestation_id":m["id"],"concept_id":m["concept_id"],
                "x":p["x"],"y":p["y"],"appearance":"preserved_007"})
        present={p["manifestation_id"] for p in placements}
        for m in sorted(self.manifests):
            if m in present:continue
            x,y=(None,None) if lens=="NONE" else coords[m]
            placements.append({"placement_id":f"generated:{lens}:{m}",
                               "manifestation_id":m,"concept_id":self.manifests[m]["concept_id"],
                               "x":x,"y":y,"appearance":"derived_view_only"})
        edges=[copy.deepcopy(r) for r in self.relations]
        analysis={"association":self.association_questions,
                  "dependency":lambda:self.dependencies(anchor),
                  "tension":self.tensions,
                  "affordance":lambda:self.affordances(anchor),
                  "flower_hex":lambda:{"status":"DISPLAY_ONLY","extra_inferences":0},
                  "NONE":lambda:self.evidence_index(anchor)}[lens]()
        return {"lens":lens,"source_evidence_digest":self.input_digest,
                "source_snapshot_digest":self.source_snapshot_digest,
                "placements":placements,"relations":edges,"analysis":analysis,
                "scope":"PROPOSAL_ONLY","coordinate_authority":"NONE",
                "semantic_authority":"UNCHANGED","external_authority":"NONE"}

    def run(self,lenses=LENSES,*,anchor=None,seed=0):
        if not isinstance(lenses,(list,tuple)) or not lenses or len(lenses)>len(LENSES):
            raise ViewError("bounded nonempty lens selection required")
        if len(lenses)!=len(set(lenses)) or any(lens not in LENSES for lens in lenses):
            raise ViewError("duplicate/unknown lens")
        views=[self.project(lens,anchor=anchor,seed=seed) for lens in lenses]
        return {"schema":SCHEMA,"source_evidence_digest":self.input_digest,
                "source_snapshot_digest":self.source_snapshot_digest,
                "baseline":self.evidence_index(anchor),"views":views,
                "working_claims":"source assertions and explicitly hypothetical questions only",
                "external_authority":"NONE", "pen_authority":"UNCHANGED"}
