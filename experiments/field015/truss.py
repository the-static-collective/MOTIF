"""FIELD-015 miniature finite-stiffness truss: axial, planar, linear, hinged.

SINGULAR means the idealized arrangement has unconstrained deformation modes.
A finite solution does NOT validate a real-world fence, hinge or tie strength.
"""
from dataclasses import dataclass
from math import hypot
import numpy as np

@dataclass(frozen=True)
class Node:
    name:str
    x:float
    y:float
    fixed_x:bool=False
    fixed_y:bool=False
    fx:float=0.
    fy:float=0.

@dataclass(frozen=True)
class Link:
    a:str
    b:str
    E:float|None=None
    A:float|None=None
    allowable:float|None=None
    tension_only:bool=False

def solve(nodes:list[Node],links:list[Link]):
    if not 2<=len(nodes)<=40 or not links:raise ValueError("Invalid scene size")
    ids={n.name:i for i,n in enumerate(nodes)}
    if len(ids)!=len(nodes):raise ValueError("Duplicate node")
    if any(l.E is None or l.A is None for l in links):
        return {"status":"HOLD_MISSING_MEMBER_STIFFNESS","physical_safety_verified":False}
    K=np.zeros((2*len(nodes),2*len(nodes)))
    forces=np.array([c for n in nodes for c in (n.fx,n.fy)])
    for m in links:
        if m.a not in ids or m.b not in ids or m.a==m.b or m.E<=0 or m.A<=0:raise ValueError("Invalid member")
        a,b=nodes[ids[m.a]],nodes[ids[m.b]]
        dx,dy=b.x-a.x,b.y-a.y;L=hypot(dx,dy)
        if L<1e-10:raise ValueError("Zero length")
        q=np.array([-dx/L,-dy/L,dx/L,dy/L])
        row=[2*ids[m.a],2*ids[m.a]+1,2*ids[m.b],2*ids[m.b]+1]
        K[np.ix_(row,row)]+=m.E*m.A/L*np.outer(q,q)
    free=[2*i+d for i,n in enumerate(nodes) for d,fixed in ((0,n.fixed_x),(1,n.fixed_y)) if not fixed]
    if not free:return {"status":"HOLD_NO_FREE_DOF","physical_safety_verified":False}
    sv=np.linalg.svd(K[np.ix_(free,free)],compute_uv=False)
    if not len(sv) or sv[0]<=0 or sv[-1]<sv[0]*1e-11:
        return {"status":"HOLD_SINGULAR_UNBRACED_OR_UNANCHORED",
                "physical_safety_verified":False}
    displacement=np.zeros(2*len(nodes))
    displacement[free]=np.linalg.solve(K[np.ix_(free,free)],forces[free])
    failures=[]
    for m in links:
        a,b=nodes[ids[m.a]],nodes[ids[m.b]]
        L=hypot(b.x-a.x,b.y-a.y)
        dr=displacement[2*ids[m.b]:2*ids[m.b]+2]-displacement[2*ids[m.a]:2*ids[m.a]+2]
        axial=m.E*m.A/L*np.dot(dr,[(b.x-a.x)/L,(b.y-a.y)/L])
        if m.tension_only and axial<0:failures.append("TIE_COMPRESSION_NOT_SUPPORTED")
        if m.allowable is not None and abs(axial)>m.allowable:failures.append("AXIAL_LIMIT_EXCEEDED")
    return {"status":"MODEL_FAILS_ASSUMPTIONS" if failures else "HOLD_UNVALIDATED_3D_AND_JOINTS",
            "max_displacement_m":round(float(np.max(np.abs(displacement))),8),
            "failures":failures,"physical_safety_verified":False,
            "note":"No 3D tipping, soil, wind turbulence, dynamic pet loading, torsion, buckling or real tie behavior."}

if __name__=="__main__":
    a=Node("a",0,0,True,True)
    b=Node("b",2,0,True,True)
    c=Node("c",2,1,False,False,50,0)
    bar=lambda x,y:Link(x,y,2e11,1e-4)
    print("Without diagonal:",solve([a,b,c],[bar("a","b"),bar("b","c")]))
    print("With diagonal:",solve([a,b,c],[bar("a","b"),bar("b","c"),bar("a","c")]))
