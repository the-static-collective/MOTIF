"""MOTIF GEOM-004: discover a missing *macro* from an existing geometry DSL.

Exact-rational synthetic demonstration. The new 'median' function is a
reusable composition of midpoint + line, not a genuinely new primitive.
"""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction as F
from itertools import combinations
from typing import NamedTuple

class Point(NamedTuple):
    x: F
    y: F

class Line(NamedTuple):
    a: F
    b: F
    c: F

@dataclass(frozen=True)
class Expr:
    op: str
    args: tuple["Expr", ...] = ()
    role: str = ""

    def signature(self):
        return self.role if self.op == "input" else self.op + "(" + ",".join(x.signature() for x in self.args) + ")"

    def size(self):
        return 1 + sum(x.size() for x in self.args)

P = {role: Expr("input", role=role) for role in "ABC"}

def point(x, y):
    return Point(F(x), F(y))

def midpoint(a, b):
    return Point((a.x+b.x)/2, (a.y+b.y)/2)

def line(a, b):
    if a == b:
        return None
    na, nb = b.y-a.y, a.x-b.x
    return Line(na,nb,na*a.x+nb*a.y)

def crossing(a, b):
    d = a.a*b.b-b.a*a.b
    if d == 0:
        return None
    return Point((a.c*b.b-b.c*a.b)/d, (a.a*b.c-b.a*a.c)/d)

def run(expr, abc):
    if expr.op == "input":
        if expr.role not in P:
            raise ValueError("unknown role")
        return abc["ABC".index(expr.role)]
    values = [run(x,abc) for x in expr.args]
    if any(x is None for x in values):
        return None
    if expr.op == "midpoint" and len(values)==2 and all(isinstance(x,Point) for x in values):
        return midpoint(*values)
    if expr.op == "line" and len(values)==2 and all(isinstance(x,Point) for x in values):
        return line(*values)
    if expr.op == "intersection" and len(values)==2 and all(isinstance(x,Line) for x in values):
        return crossing(*values)
    raise ValueError("unsupported expression")

def centroid_direct(abc):
    return Point(sum(p.x for p in abc)/3, sum(p.y for p in abc)/3)

def nondegenerate(abc):
    a,b,c=abc
    return (b.x-a.x)*(c.y-a.y)!=(b.y-a.y)*(c.x-a.x)

def candidate_programs(allow_nested=False):
    """Search controls are constructed without seeing target coordinates.

    Stage 0: only sides through original input vertices: no centroid.
    Stage 1: allow a constructed midpoint to be passed to a line primitive.
    """
    basic=[Expr("line",(P[a], P[b])) for a,b in combinations("ABC",2)]
    lines=list(basic)
    if allow_nested:
        for anchor in "ABC":
            for u,v in combinations("ABC",2):
                if anchor not in (u,v): # Opposite-side midpoint is the smallest meaningful missing subroutine
                    lines.append(Expr("line",(P[anchor],Expr("midpoint",(P[u],P[v])))))
    return [Expr("intersection",(a,b)) for a,b in combinations(lines,2)]

def discover(teachers, counterexamples=()):
    """Finite counterexample-guided candidate elimination; preserve HOLD.

    No oracle supplied as an executable goal function. Teacher provides only
    output points; counterexample observations are separately revealed.
    """
    teachers=list(teachers)
    if len(teachers)<2 or len(set(tuple(t) for t in teachers))!=len(teachers):
        return {"status":"HOLD","reason":"insufficient independent cases"}
    if not all(nondegenerate(t) for t in teachers):
        return {"status":"HOLD","reason":"degenerate teacher"}
    baseline=candidate_programs(False)
    if any(all(run(expr, t)==centroid_direct(t) for t in teachers) for expr in baseline):
        return {"status":"HOLD","reason":"not a missing construction in this grammar"}
    expanded=candidate_programs(True)
    survivors=[x for x in expanded if all(run(x,t)==centroid_direct(t) for t in teachers)]
    checks=0
    for t in counterexamples:
        if not nondegenerate(t):
            continue
        survivors=[x for x in survivors if run(x,t)==centroid_direct(t)]
        checks+=1
    if not survivors:
        return {"status":"HOLD","reason":"no consistent generated method", "counterexamples_checked":checks}
    survivors.sort(key=lambda x:(x.size(),x.signature()))
    selected=survivors[0]
    return {"status":"PROPOSAL_ONLY","method":selected,"signature":selected.signature(),
            "candidate_counts":{"old":len(baseline),"expanded":len(expanded),"surviving":len(survivors)},
            "invented_macro":{"name":"median_line", "definition":"line(vertex, midpoint(opposite_a, opposite_b))", 
                              "nature":"composition of existing operators, not novel primitive"},
            "counterexamples_checked":checks,"authority":"HOLD"}

def apply(model,abc):
    if not nondegenerate(abc) or model.get("status")!="PROPOSAL_ONLY":
        return {"status":"HOLD"}
    output=run(model["method"],abc)
    return {"status":"PROPOSAL_ONLY","point":[str(output.x),str(output.y)],"authority":"HOLD"} if output is not None else {"status":"HOLD"}
