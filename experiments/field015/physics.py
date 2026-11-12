"""FIELD-015 classical mechanics screening; never structural or pet safety approval.

Inputs are user-specified hypotheses, not inferred material properties.
Connected zip ties are not automatically verified engineering joints.
"""
from __future__ import annotations
from dataclasses import dataclass
from math import isfinite
G=9.80665
AIR=1.225

@dataclass(frozen=True)
class Panel:
    name:str
    width:float|None=None
    height:float|None=None
    mass:float|None=None
    base_depth:float|None=None
    opacity:float|None=None
    drag:float|None=None
    friction:float|None=None
    anchor_type:str="UNKNOWN"
    anchor_torque:float|None=None
    E:float|None=None
    I:float|None=None

def screen(p:Panel,wind:float):
    if not isfinite(wind) or wind<0 or wind>100: raise ValueError("Bad illustrative wind speed")
    if not p.name or p.anchor_type not in ("UNKNOWN","FREESTANDING","CHARACTERIZED_ANCHOR"):raise ValueError("Bad panel")
    fields=("width","height","mass","base_depth","opacity","drag","friction")
    missing=[n for n in fields if getattr(p,n) is None]
    for n in fields:
        v=getattr(p,n)
        if v is not None and (not isfinite(v) or v<0):raise ValueError("Bad property "+n)
    if p.opacity is not None and p.opacity>1 or p.friction is not None and p.friction>1:
        raise ValueError("Bad fractional property")
    out=dict(panel=p.name,status="HOLD_UNKNOWN_PROPERTIES",missing=missing,
             wind_scenario_mps=wind,verified_structure=False,pet_safety_certified=False,
             fastener_capacity_inferred_from_200lb_claim=False)
    if missing:return out
    F=.5*AIR*wind**2*p.drag*p.width*p.height*p.opacity
    overturn=F*p.height/2
    restoring=G*p.mass*p.base_depth/2
    if p.anchor_type=="UNKNOWN":
        out["missing"].append("anchorage_characterization")
        out["status"]="HOLD_UNKNOWN_SUPPORT"
        return out
    if p.anchor_type=="CHARACTERIZED_ANCHOR":
        if p.anchor_torque is None:
            out["missing"].append("measured_anchor_torque")
            return out
        if p.anchor_torque<0 or not isfinite(p.anchor_torque):raise ValueError("Bad anchor torque")
        restoring+=p.anchor_torque
    slip=p.friction*G*p.mass
    fail=[]
    if overturn>restoring:fail.append("OVERTURNING_IN_SIMPLIFIED_CASE")
    if F>slip and p.anchor_type=="FREESTANDING":fail.append("SLIDING_IN_SIMPLIFIED_CASE")
    out.update(force_n=round(F,5),moment_nm=round(overturn,5),
         restoring_nm=round(restoring,5),friction_n=round(slip,5),failure_modes=fail)
    if p.E is not None and p.I is not None:
        if not (p.E>0 and p.I>0):raise ValueError("Bad elastic properties")
        load=F/p.width if p.width else 0
        out["beam_deflection_m"]=round(5*load*p.width**4/(384*p.E*p.I),8)
    else:out["missing"].append("measured_E_and_second_moment_I")
    out["missing"].extend(["joint_load_sharing","impact_and_gust_dynamics","soil_and_foundation"])
    out["status"]="MODEL_FAILS_ASSUMED_LOAD_CASE" if fail else "HOLD_UNMODELED_LOAD_PATHS"
    return out

def assembly(panels:list[Panel],joins:list[tuple[str,str,str]],wind:float):
    ids=[x.name for x in panels]
    if not ids or len(set(ids))!=len(ids):raise ValueError("Bad inventory")
    parent={k:k for k in ids}
    def find(k):
        while parent[k]!=k:k=parent[k]
        return k
    for a,b,kind in joins:
        if a not in parent or b not in parent or a==b or kind not in ("ZIP_TIE","CLAMP","HINGE","BRACE"):
            raise ValueError("Bad connection")
        parent[find(a)]=find(b)
    components={}
    for k in ids:components.setdefault(find(k),[]).append(k)
    return dict(panels=[screen(x,wind) for x in panels],
         components=list(components.values()),
         connection_topology_known=True,
         joint_shear_peel_fatigue_verified=False,
         overall_stability_verified=False,
         note="A connected graph can be a mechanism; joining to a chair or trampoline does not verify a fixed anchor.")

def demonstration():
    common=dict(width=1.5,height=1,mass=5,base_depth=.35,drag=1.4,friction=.6,
                anchor_type="FREESTANDING")
    return {"opaque":screen(Panel("opaque",opacity=1,**common),8),
            "porous":screen(Panel("mesh",opacity=.2,**common),8),
            "no_model_props":screen(Panel("unmeasured"),8)}

if __name__=="__main__":
    import json
    print(json.dumps(demonstration(),indent=2))
