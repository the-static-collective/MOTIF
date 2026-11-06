"""GEOM-003: bounded typed program synthesis of classic triangle constructions.

This is classical enumerative synthesis in a finite DSL. No new geometry theorem
is claimed. Inputs and algebra are rational for exact finite-instance witnesses.
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
    c: F  # ax + by = c


@dataclass(frozen=True)
class Program:
    op: str
    args: tuple["Program", ...] = ()
    name: str = ""

    def signature(self) -> str:
        return self.name if self.op == "input" else self.op + "(" + ",".join(a.signature() for a in self.args) + ")"

    def size(self) -> int:
        # Tree description length: expanded cost; does not assert runtime costs.
        return 1 + sum(a.size() for a in self.args)


P = {name: Program("input", name=name) for name in "ABC"}


def point(x, y) -> Point:
    return Point(F(x), F(y))


def _dot(a: Point, b: Point) -> F:
    return a.x * b.x + a.y * b.y


def _minus(a: Point, b: Point) -> Point:
    return Point(a.x - b.x, a.y - b.y)


def dist2(a: Point, b: Point) -> F:
    d = _minus(a, b)
    return _dot(d, d)


def midpoint(a: Point, b: Point) -> Point:
    return Point((a.x + b.x) / 2, (a.y + b.y) / 2)


def line(a: Point, b: Point) -> Line | None:
    if a == b:
        return None
    dx, dy = b.x-a.x, b.y-a.y
    na, nb = dy, -dx
    return Line(na, nb, na*a.x + nb*a.y)


def perpendicular_through(l: Line, p: Point) -> Line:
    a, b = -l.b, l.a
    return Line(a, b, a*p.x + b*p.y)


def intersection(l: Line, m: Line) -> Point | None:
    det = l.a*m.b - m.a*l.b
    if not det:
        return None
    return Point((l.c*m.b-m.c*l.b)/det, (l.a*m.c-m.a*l.c)/det)


def evaluate(expr: Program, abc: tuple[Point, Point, Point]):
    if expr.op == "input":
        if expr.name not in "ABC" or len(expr.name) != 1:
            raise ValueError("unknown input role")
        return abc["ABC".index(expr.name)]
    values = [evaluate(a, abc) for a in expr.args]
    if any(v is None for v in values):
        return None
    if expr.op == "midpoint" and len(values) == 2 and all(isinstance(v, Point) for v in values):
        return midpoint(*values)
    if expr.op == "line" and len(values) == 2 and all(isinstance(v, Point) for v in values):
        return line(*values)
    if expr.op == "perpendicular" and len(values) == 2 and isinstance(values[0], Line) and isinstance(values[1], Point):
        return perpendicular_through(*values)
    if expr.op == "intersection" and len(values) == 2 and all(isinstance(v, Line) for v in values):
        return intersection(*values)
    raise ValueError("invalid typed expression")


def structural_candidates(*, allow_midpoint=True, allow_perpendicular=True):
    """Enumerate methods, not coordinate values or an answer-specific formula.

    Search space: all distinct segment lines through A/B/C; perpendiculars
    through any input role or any pair midpoint; all line-line crossings.
    """
    points = list(P.values())
    if allow_midpoint:
        points += [Program("midpoint", (P[a], P[b])) for a,b in combinations("ABC", 2)]
    bases = [Program("line", (P[a], P[b])) for a,b in combinations("ABC", 2)]
    lines = list(bases)
    if allow_perpendicular:
        lines += [Program("perpendicular", (l, p)) for l in bases for p in points]
    return [Program("intersection", (a,b)) for a,b in combinations(lines, 2)]


def solve2(a, b, c, d, e, f):
    """Independent 2x2 linear solver for direct classical oracle."""
    det = a*d-b*c
    if not det:
        return None
    return Point((e*d-b*f)/det, (a*f-e*c)/det)


def oracles(abc: tuple[Point, Point, Point]) -> dict[str, Point] | None:
    """Closed-form reference independent of search operators."""
    a,b,c = abc
    u, v = _minus(b,a), _minus(c,a)
    o = solve2(
        2*u.x, 2*u.y, 2*v.x, 2*v.y,
        b.x*b.x+b.y*b.y-a.x*a.x-a.y*a.y,
        c.x*c.x+c.y*c.y-a.x*a.x-a.y*a.y,
    )
    if o is None:
        return None
    h = Point(a.x+b.x+c.x-2*o.x, a.y+b.y+c.y-2*o.y)
    # Teacher does not call midpoint(O,H), though that identity is true.
    n = Point((a.x+b.x+c.x-o.x)/2, (a.y+b.y+c.y-o.y)/2)
    return {"circumcenter": o, "orthocenter": h, "nine_point_center": n}


def certificates(abc: tuple[Point, Point, Point], results: dict[str, Point]) -> dict[str, bool]:
    """Exact-instance invariant checks, NOT a universal formal proof."""
    a,b,c = abc
    o,h,n = (results[k] for k in ("circumcenter", "orthocenter", "nine_point_center"))
    radius2 = dist2(o,a)
    sides = (midpoint(a,b),midpoint(b,c),midpoint(a,c))
    return {
        "equidistant_circumcenter": radius2 == dist2(o,b) == dist2(o,c),
        "orthogonal_altitudes": all(_dot(_minus(h,p),_minus(q,r)) == 0
                                     for p,q,r in ((a,b,c),(b,a,c),(c,a,b))),
        "ninepoint_side_midpoints": all(dist2(n,p) == radius2/4 for p in sides),
        "ninepoint_parent_relation": n == midpoint(o,h),
    }


def learn(teachers: list[tuple[Point, Point, Point]], *,
          allow_midpoint=True, allow_perpendicular=True) -> dict:
    if len(teachers) < 4:
        return {"status": "HOLD", "reason": "need at least four independent demonstrations"}
    if len(set(teachers)) != len(teachers):
        return {"status": "HOLD", "reason": "teacher demonstrations are duplicated"}
    if any(oracles(abc) is None for abc in teachers):
        return {"status": "HOLD", "reason": "degenerate teacher triangle"}
    targets = [oracles(abc) for abc in teachers]
    candidates = structural_candidates(allow_midpoint=allow_midpoint,
                                       allow_perpendicular=allow_perpendicular)
    learned = {}
    successful = {}
    for label in ("circumcenter", "orthocenter"):
        matches = [expr for expr in candidates
                   if all(evaluate(expr, abc) == t[label] for abc,t in zip(teachers, targets))]
        matches.sort(key=lambda x: (x.size(), x.signature()))
        successful[label] = len(matches)
        if not matches:
            return {"status":"HOLD", "reason":label+" not expressible in bounded grammar",
                    "candidate_programs":len(candidates), "matches":successful}
        learned[label] = matches[0]
    # A second-stage typed composition is now possible: reuse entire
    # discovered methods, not a hardcoded formula for nine-point center.
    leaves = [*P.values(),learned["circumcenter"],learned["orthocenter"]]
    composites = [Program("midpoint", (l,r)) for l,r in combinations(leaves,2)] if allow_midpoint else []
    wins = [p for p in composites
            if all(evaluate(p, abc)==t["nine_point_center"] for abc,t in zip(teachers,targets))]
    wins.sort(key=lambda x: (x.size(),x.signature()))
    successful["nine_point_center"] = len(wins)
    if not wins:
        return {"status":"HOLD", "reason":"no nine-point composition in bounded grammar",
                "candidate_programs":len(candidates), "matches":successful}
    learned["nine_point_center"] = wins[0]
    return {"status":"PROPOSE_ONLY", "programs":learned, "matches":successful,
            "candidate_programs":len(candidates),
            "secondary_compositions":len(composites),
            "admission":"HOLD", "effective_authority":"NONE"}


def apply(learned: dict, abc, *, geometry="euclidean") -> dict:
    if geometry != "euclidean":
        return {"status":"HOLD", "reason":"requires Euclidean metric"}
    if oracles(abc) is None:
        return {"status":"HOLD", "reason":"collinear or duplicate triangle"}
    if learned.get("status") != "PROPOSE_ONLY":
        return {"status":"HOLD", "reason":"no valid candidate methods"}
    actual = {label:evaluate(p,abc) for label,p in learned["programs"].items()}
    if any(p is None or not isinstance(p,Point) for p in actual.values()):
        return {"status":"HOLD", "reason":"derived method undefined"}
    proofs = certificates(abc, actual)
    return {"status":"PROPOSE_ONLY" if all(proofs.values()) else "HOLD",
            "reason":"exact instance invariants" if all(proofs.values()) else "invariant failed",
            "points":actual, "witnesses":proofs,
            "admission":"HOLD", "effective_authority":"NONE"}
