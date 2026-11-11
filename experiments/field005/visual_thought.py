"""MOTIF FIELD-005: provisional visual thinking, not physical certification.

Zero external effects by default. A generic typed graph proposes alternative
roles, assemblies and scene changes; a schematic SVG is an inspectable working
memory that can later be re-read by a local vision model.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from collections import Counter
from hashlib import sha256
from html import escape
import json
from typing import Any

TRI = {"YES", "NO", "UNKNOWN"}
SOURCES = {"PHOTO_OBSERVED", "SKETCH_LABELED", "USER_REPORTED", "MODEL_TENTATIVE", "SYNTHETIC"}
FUNCTIONS = {"delineate", "support", "hold", "organize", "shelter", "route", "elevate"}
SHAPES = {"flat", "rigid", "flexible", "frame", "container", "connector", "weight", "surface"}

@dataclass(frozen=True)
class Object:
    id: str
    label: str
    original_use: str
    capabilities: tuple[str, ...]
    features: tuple[str, ...]
    origin: str
    movable: str = "UNKNOWN"
    bbox: tuple[float, float, float, float] | None = None  # normalized source-image or sketch box
    source: str = "fixture"

    def validate(self):
        if not self.id or not self.label or not self.original_use or not self.source:
            raise ValueError("Missing object identity/provenance")
        if self.origin not in SOURCES or self.movable not in TRI:
            raise ValueError("Invalid origin/movability")
        if any(x not in FUNCTIONS for x in self.capabilities) or any(x not in SHAPES for x in self.features):
            raise ValueError("Unknown affordance vocabulary")
        if self.bbox is not None:
            if len(self.bbox) != 4 or not all(isinstance(x,(int,float)) and 0 <= x <= 1 for x in self.bbox):
                raise ValueError("Invalid normalized image box")
            if self.bbox[0] >= self.bbox[2] or self.bbox[1] >= self.bbox[3]:
                raise ValueError("Inverted image box")

@dataclass(frozen=True)
class Scene:
    goal: str
    desired_function: str
    things: tuple[Object, ...]
    present_boundary: tuple[tuple[float,float], ...] = ()
    desired_boundary: tuple[tuple[float,float], ...] = ()
    use_safety_review: bool = True
    source: str = "synthetic"

    def validate(self):
        if not self.goal or self.desired_function not in FUNCTIONS or not self.source:
            raise ValueError("Invalid scene objective")
        if len(self.things) > 60 or len(set(o.id for o in self.things)) != len(self.things):
            raise ValueError("Duplicate or excessive objects")
        for o in self.things: o.validate()
        for poly in (self.present_boundary,self.desired_boundary):
            if poly and (len(poly) < 2 or len(poly) > 80 or
                any(len(p)!=2 or not all(isinstance(x,(int,float)) and 0<=x<=1 for x in p) for p in poly)):
                raise ValueError("Invalid schematic geometry")

@dataclass(frozen=True)
class Proposal:
    id: str
    operation: str
    ingredients: tuple[str, ...]
    proposed_function: str
    needed_checks: tuple[str, ...]
    rationale: str
    evidence: tuple[str, ...]
    verdict: str = "CANDIDATE_NOT_VERIFIED"


def think(scene: Scene) -> tuple[Proposal, ...]:
    """Typed transform search. No dog-fence-specific noun rules or invented dimensions."""
    scene.validate()
    goal=scene.desired_function
    objs=scene.things
    out=[]
    def emit(op, parts, checks, why):
        if len(out) >= 80: return
        key=op+":"+"-".join(x.id for x in parts)
        out.append(Proposal(key,op,tuple(x.id for x in parts),goal,tuple(checks),why,
                            tuple(x.source+"#"+x.id for x in parts)))
    relevant=[o for o in objs if goal in o.capabilities]
    for o in relevant:
        if o.original_use != goal:
            emit("REASSIGN_FUNCTION",[o],["verify actual suitability and geometry"],
                 "Reuse an existing object's possible function rather than its product label")
        if o.movable != "NO":
            emit("RELOCATE_EXISTING",[o],["confirm movement permitted" if o.movable=="UNKNOWN" else "confirm new position","confirm fit"],
                 "Change where resources sit rather than fabricate new material")
    if scene.present_boundary and scene.desired_boundary:
        movable=[o for o in objs if o.movable!="NO"]
        if movable:
            emit("REDRAW_PROBLEM",movable[:2],["check target line means desired layout","verify access and true lengths"],
                 "Try a different boundary or route before constructing the original one")
    joiners=[o for o in objs if "connector" in o.features]
    rigid=[o for o in relevant if "rigid" in o.features or "frame" in o.features]
    if len(rigid)>=2:
        if joiners:
            for i in range(min(len(rigid)-1,4)):
                emit("COMPOSE_NETWORK",[rigid[i],rigid[i+1],joiners[0]],
                     ["joint suitability","assembly stability","do not infer load rating from connector rating"],
                     "Joined components might acquire a new function; test the network")
        else:
            emit("INVENT_MISSING_JOIN",rigid[:2],["identify a suitable reversible joining method"],
                 "The absent connector is itself a solvable subproblem")
    supports=[o for o in objs if "support" in o.capabilities and ("frame" in o.features or "weight" in o.features)]
    for r in rigid[:3]:
        for a in supports[:3]:
            if r.id != a.id:
                emit("OPPORTUNISTIC_SUPPORT",[r,a],["check stability, tipping and movement","check connection without damaging anchor"],
                     "Reinterpret an environmental object as a possible support, never verified by appearance")
    return tuple(out)


def critique(scene:Scene, proposals:tuple[Proposal,...]) -> tuple[dict[str,Any], ...]:
    """A rule-based critic independent of hypothesis emission. No physical claim."""
    objects={o.id:o for o in scene.things}
    results=[]
    for p in proposals:
        holds=[]
        if p.operation in {"RELOCATE_EXISTING","REDRAW_PROBLEM"} and any(objects[i].movable=="UNKNOWN" for i in p.ingredients):
            holds.append("MOVABILITY_UNKNOWN")
        if p.operation in {"RELOCATE_EXISTING","REDRAW_PROBLEM"} and any(objects[i].movable=="NO" for i in p.ingredients):
            holds.append("FIXED_OBJECT")
        if p.operation in {"COMPOSE_NETWORK","OPPORTUNISTIC_SUPPORT"}:
            holds.append("NO_STRUCTURAL_VALIDATION")
        if scene.use_safety_review:
            holds.append("DOMAIN_SAFETY_UNREVIEWED")
        if p.operation == "REDRAW_PROBLEM" and scene.present_boundary==scene.desired_boundary:
            holds.append("REDRAW_DOES_NOT_CHANGE_GEOMETRY")
        results.append({"proposal":p.id,"status":"HOLD_FOR_TEST" if holds else "UNVERIFIED_PREVIEW",
                        "holds":sorted(set(holds)), "executed":False})
    return tuple(results)


def svg_sketch(scene:Scene, proposals:tuple[Proposal,...]) -> str:
    """Typed SVG visual memory. Dashed marks are hypothetical; never measured scale."""
    scene.validate()
    bits=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 850 540" role="img" aria-label="Provisional scene and transformations">',
          '<rect width="850" height="540" fill="#faf8f4"/>',
          '<text x="24" y="28" font-size="20" font-family="sans-serif">MOTIF visual scratchpad · schematic, NOT TO SCALE</text>',
          '<rect x="20" y="46" width="590" height="450" fill="#fff" stroke="#aaa"/>',
          '<text x="634" y="72" font-size="14" font-family="sans-serif">Hypotheses, not observations</text>']
    def path(coords,stroke,dash=""):
        if not coords:return
        pts=" ".join(f"{24+x*580:.1f},{50+y*432:.1f}" for x,y in coords)
        bits.append(f'<polyline points="{pts}" fill="none" stroke="{stroke}" stroke-width="4" {dash}/>')
    path(scene.present_boundary,"#555")
    path(scene.desired_boundary,"#327eaa",'stroke-dasharray="10 7"')
    for j,o in enumerate(scene.things):
        if o.bbox is None:
            x=40+(j%5)*105; y=80+(j//5)*88; w=94; h=60
            inferred=True
        else:
            x=24+o.bbox[0]*580;y=50+o.bbox[1]*432
            w=(o.bbox[2]-o.bbox[0])*580;h=(o.bbox[3]-o.bbox[1])*432
            inferred=False
        border="#b36b33" if o.origin=="MODEL_TENTATIVE" else "#3d6757"
        bits.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="none" stroke="{border}" stroke-width="2" {"stroke-dasharray=\"4 4\"" if inferred else ""}/>')
        bits.append(f'<text x="{x:.1f}" y="{y-5:.1f}" font-family="sans-serif" font-size="11">{escape(o.label[:25])}</text>')
    for i,p in enumerate(proposals[:14]):
        bits.append(f'<text x="634" y="{98+i*23}" font-family="monospace" font-size="10">{escape(p.operation[:25])}</text>')
    bits.append('<text x="24" y="525" font-family="sans-serif" font-size="12">Solid: presently recorded line · Blue dashed: desired line · Orange boxes: tentative evidence</text>')
    bits.append('</svg>')
    return "\n".join(bits)


def run(scene:Scene) -> dict[str,Any]:
    proposals=think(scene)
    reviews=critique(scene,proposals)
    # Reinspectable artifact is not a claim that a vision model read it.
    svg=svg_sketch(scene,proposals)
    obj={"experiment":"FIELD-005-VISUAL-THOUGHT", "scene_source":scene.source,
         "goal":scene.goal,"scene_objects":len(scene.things),
         "proposals":[asdict(p) for p in proposals],"critique":list(reviews),
         "visual_scratchpad_sha256":sha256(svg.encode()).hexdigest(),
         "visual_reread_by_model":False,"real_world_test":False,"actions_executed":0,
         "limits":"No real vision model ran; layout is schematic; all suggestions conditional."}
    obj["receipt_sha256"]=sha256(json.dumps(obj,sort_keys=True).encode()).hexdigest()
    return obj


def load(raw:dict) -> Scene:
    if not isinstance(raw,dict):raise ValueError("Scene must be a mapping")
    allowed=set(Scene.__dataclass_fields__)
    if set(raw)-allowed:raise ValueError("Unknown scene keys")
    objs=[]
    for row in raw.get("things",[]):
        if set(row)-set(Object.__dataclass_fields__):raise ValueError("Unknown object keys")
        obj=Object(**{**row,"capabilities":tuple(row.get("capabilities",[])),"features":tuple(row.get("features",[])),
                      "bbox":tuple(row["bbox"]) if row.get("bbox") is not None else None})
        objs.append(obj)
    scene=Scene(**{**raw,"things":tuple(objs),
                   "present_boundary":tuple(tuple(p) for p in raw.get("present_boundary",[])),
                   "desired_boundary":tuple(tuple(p) for p in raw.get("desired_boundary",[]))})
    scene.validate()
    return scene