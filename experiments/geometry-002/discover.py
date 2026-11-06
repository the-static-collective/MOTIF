"""MOTIF-GEOM-002: infer a finite near-equal-step 2D lattice from unlabeled points.

No given angle, origin, radius, rotation, or shape family. Bounded search over
local vectors is a classical lattice-fitting procedure, NOT new mathematics.
No observed point is created, altered, or promoted from a conjecture.
"""
from __future__ import annotations

from math import acos, cos, degrees, hypot, isfinite, radians, sin
from statistics import median

MAX_POINTS = 48
INLIER_RATIO = 0.24


def _inv(basis, point):
    ux, uy, vx, vy = basis
    det = ux * vy - uy * vx
    if abs(det) < 1e-12:
        return None
    x, y = point
    return ((vy*x - vx*y)/det, (-uy*x + ux*y)/det)


def _project(origin, basis, ij):
    i, j = ij
    return (origin[0] + basis[0]*i + basis[2]*j,
            origin[1] + basis[1]*i + basis[3]*j)


def _assign(points, origin, basis, tolerance):
    matches = {}
    for idx, p in enumerate(points):
        v = _inv(basis, (p[0]-origin[0], p[1]-origin[1]))
        if v is None:
            return {}
        ij = (round(v[0]), round(v[1]))
        predicted = _project(origin, basis, ij)
        error = hypot(p[0]-predicted[0], p[1]-predicted[1])
        if error > tolerance:
            continue
        if ij not in matches or error < matches[ij][2]:
            matches[ij] = (idx, p, error)
    return matches


def _solve3(a, b):
    a = [list(row) + [rhs] for row, rhs in zip(a, b)]
    for i in range(3):
        pivot = max(range(i, 3), key=lambda k: abs(a[k][i]))
        if abs(a[pivot][i]) < 1e-9:
            return None
        a[i], a[pivot] = a[pivot], a[i]
        div = a[i][i]
        a[i] = [val/div for val in a[i]]
        for k in range(3):
            if k == i:
                continue
            weight = a[k][i]
            a[k] = [v-weight*p for v, p in zip(a[k], a[i])]
    return [row[-1] for row in a]


def _refine(matches):
    """Least-squares affine lattice fit for established integer assignments."""
    if len(matches) < 4:
        return None
    design = [(1.0, float(i), float(j)) for (i,j) in matches]
    normal = [[sum(row[i]*row[j] for row in design) for j in range(3)]
              for i in range(3)]
    xs = [entry[1][0] for entry in matches.values()]
    ys = [entry[1][1] for entry in matches.values()]
    x = _solve3(normal, [sum(row[i]*target for row,target in zip(design,xs)) for i in range(3)])
    y = _solve3(normal, [sum(row[i]*target for row,target in zip(design,ys)) for i in range(3)])
    if x is None or y is None:
        return None
    return (x[0],y[0]),(x[1],y[1],x[2],y[2])


def _reduced_basis(basis):
    """Classical 2D Gauss reduction: remove arbitrary sheared basis choices.

    Does not resolve absolute reflection, origin, or 60-degree gauge freedom.
    """
    u=[basis[0],basis[1]]
    v=[basis[2],basis[3]]
    for _ in range(16):
        du=u[0]*u[0]+u[1]*u[1]
        dv=v[0]*v[0]+v[1]*v[1]
        if dv<du-1e-9:
            u,v=v,u
            continue
        projection=round((u[0]*v[0]+u[1]*v[1])/du)
        if projection==0:
            break
        v=[v[0]-projection*u[0],v[1]-projection*u[1]]
    return (u[0],u[1],v[0],v[1])

def _geometry(basis):
    ux, uy, vx, vy = basis
    u, v = hypot(ux,uy), hypot(vx,vy)
    cosine = max(-1.0,min(1.0,(ux*vx+uy*vy)/(u*v)))
    angle = degrees(acos(cosine))
    acute = min(angle,180-angle)
    family = ('triangular' if abs(acute-60) <= 5 else
              'square' if abs(acute-90) <= 5 else 'oblique')
    return {'angle_degrees':round(acute,3),
            'axis_lengths':[round(u,5),round(v,5)],
            'family':family}


def _roundnum(x):
    return round(x,6)


def _holes(origin,basis,matches):
    """At least 4 witnessed nearest-neighbor lattice cells: local proposals only."""
    observed = set(matches)
    i_values,j_values = zip(*observed)
    scale = min(hypot(basis[0],basis[1]),hypot(basis[2],basis[3]))
    offsets = [(i,j) for i in range(-1,2) for j in range(-1,2)
               if (i,j)!=(0,0)
               and hypot(basis[0]*i+basis[2]*j,basis[1]*i+basis[3]*j)
               <=1.16*scale]
    proposed = []
    for i in range(min(i_values),max(i_values)+1):
        for j in range(min(j_values),max(j_values)+1):
            if (i,j) in observed:
                continue
            adjacent = sum((i+di,j+dj) in observed for di,dj in offsets)
            if adjacent < 4:
                continue
            x,y = _project(origin,basis,(i,j))
            proposed.append({'local_index':[i,j],
                             'xy':[_roundnum(x),_roundnum(y)],
                             'witnessed_neighbors':adjacent,
                             'status':'PROPOSAL_ONLY'})
    return sorted(proposed,key=lambda p:(-p['witnessed_neighbors'],p['local_index']))


def discover(points, *, min_coverage=0.68, refine=True):
    """Return a held, inspectable model or HOLD; no training/actor authority.

    Searches near-equal-step rhombic primitive cells only; arbitrary rectangular
    lattices, perspective distortions, nonperiodic patterns are out-of-family.
    Coordinates are assumed Euclidean and homoscedastically noisy.
    """
    if not 0 < min_coverage <= 1:
        raise ValueError('coverage outside (0,1]')
    raw = [tuple(p) for p in points]
    if any(len(p)!=2 or not all(isinstance(x,(int,float)) and isfinite(x) for x in p)
           for p in raw):
        raise ValueError('finite 2D points required')
    if not (8<=len(raw)<=MAX_POINTS):
        return {'status':'HOLD','reason':'not enough, or too many, observed points','count':len(raw)}
    if len(set(raw))!=len(raw):
        return {'status':'HOLD','reason':'duplicate observed positions','count':len(raw)}
    nearest=[min(hypot(x-xx,y-yy) for j,(xx,yy) in enumerate(raw) if i!=j)
             for i,(x,y) in enumerate(raw)]
    unit=median(nearest)
    if unit<1e-9:
        return {'status':'HOLD','reason':'coordinate scale too small','count':len(raw)}
    # Candidate bases have equal-ish primitive lengths; ANGLES ARE NOT SUPPLIED.
    # This is an explicit structural prior, not discovery of arbitrary geometry.
    candidates=0
    best=None
    for origin in raw:
        adjacent=sorted(((hypot(p[0]-origin[0],p[1]-origin[1]),p)
                          for p in raw if p!=origin),key=lambda x:x[0])
        near=[(p[0]-origin[0],p[1]-origin[1]) for d,p in adjacent[:9]
              if .74*unit<=d<=1.42*unit]
        for i,u in enumerate(near):
            for v in near[i+1:]:
                lu,lv=hypot(*u),hypot(*v)
                if not .78 <= lu/lv <= 1.28:
                    continue
                area=abs(u[0]*v[1]-u[1]*v[0])/(lu*lv)
                if area<.61:
                    continue
                basis=(u[0],u[1],v[0],v[1])
                candidates+=1
                matches=_assign(raw,origin,basis,INLIER_RATIO*unit)
                if len(matches)<4:
                    continue
                fit=_refine(matches)
                if refine and fit is not None:
                    fitted_origin,fitted_basis=fit
                    new=_assign(raw,fitted_origin,fitted_basis,INLIER_RATIO*unit)
                    if len(new)>=len(matches):
                        # Refitting may change assignment; re-evaluate with it.
                        fit2=_refine(new)
                        if fit2 is not None:
                            o2,b2=fit2
                            newer=_assign(raw,o2,b2,INLIER_RATIO*unit)
                            if len(newer)>=len(matches):
                                origin_use,basis_use,matches=o2,b2,newer
                            else:
                                origin_use,basis_use,matches=fitted_origin,fitted_basis,new
                        else:
                            origin_use,basis_use,matches=fitted_origin,fitted_basis,new
                    else:
                        origin_use,basis_use=origin,basis
                else:
                    origin_use,basis_use=origin,basis
                # Canonicalize the primitive basis and use STRICT post-fit
                # support for selection; loose search matches can be aliases.
                basis_use=_reduced_basis(basis_use)
                step=min(hypot(basis_use[0],basis_use[1]),
                         hypot(basis_use[2],basis_use[3]))
                if step < .78*unit or step > 1.42*unit:
                    continue
                strict=_assign(raw,origin_use,basis_use,.125*unit)
                if refine:
                    fitted_strict=_refine(strict)
                    if fitted_strict is not None:
                        os,bs=fitted_strict
                        bs=_reduced_basis(bs)
                        check=_assign(raw,os,bs,.125*unit)
                        if len(check)>=len(strict):
                            origin_use,basis_use,strict=os,bs,check
                matches=strict
                # Insist on two independent dimensions in the observed data.
                coords=list(matches)
                if not coords or max(i for i,j in coords)-min(i for i,j in coords)<2 or max(j for i,j in coords)-min(j for i,j in coords)<2:
                    continue
                error=sum(entry[2]**2 for entry in matches.values()) / len(matches)
                criterion=(len(matches),-error)
                if best is None or criterion>best[0]:
                    best=(criterion,origin_use,basis_use,matches)
    if best is None:
        return {'status':'HOLD','reason':'no independent 2D rule supported','count':len(raw),
                'tested_hypotheses':candidates}
    _,origin,basis,matches=best
    basis=_reduced_basis(basis)
    ratio=len(matches)/len(raw)
    g=_geometry(basis)
    # Oblique is a genuine measured angle; family label is AFTER fitting.
    if len(matches)<8 or ratio<min_coverage:
        return {'status':'HOLD','reason':'insufficient robust lattice coverage',
                'count':len(raw),'inliers':len(matches),
                'coverage':round(ratio,4),'tested_hypotheses':candidates,
                'best_candidate_geometry':g}
    rmse=(sum(entry[2]**2 for entry in matches.values())/len(matches))**.5
    if rmse/median(g['axis_lengths']) > 0.11:
        return {'status':'HOLD','reason':'excessive normalized lattice residual',
                'count':len(raw),'coverage':round(ratio,4),
                'tested_hypotheses':candidates}
    return {'status':'PROPOSE_ONLY','observed_count':len(raw),
            'inliers':len(matches),'coverage':round(ratio,4),
            'normalized_rmse':round(rmse/unit,5),
            'rule':g,
            'origin':[_roundnum(x) for x in origin],
            'basis':[_roundnum(x) for x in basis],
            'inlier_indices':sorted([entry[0] for entry in matches.values()]),
            'holes':_holes(origin,basis,matches),
            'tested_hypotheses':candidates,
            'scope':'finite noisy near-equal-step 2D lattice; local calibration only',
            'authority':'HOLD: candidate model and missing positions are not facts'}


def point_set(family, radius, angle_deg, origin, width=5):
    """Generator for independent *synthetic* benchmark worlds only."""
    if family=='triangular':
        lattice=[(i,j) for i in range(-2,3) for j in range(-2,3)
                 if max(abs(i),abs(j),abs(i+j))<=2]
        alpha=60.0
    elif family=='square':
        lattice=[(i,j) for i in range(-(width//2),width//2+1)
                 for j in range(-(width//2),width//2+1)]
        alpha=90.0
    elif family=='oblique':
        lattice=[(i,j) for i in range(-(width//2),width//2+1)
                 for j in range(-(width//2),width//2+1)]
        alpha=73.0
    else:
        raise ValueError('unsupported generator family')
    angle=radians(angle_deg)
    beta=radians(angle_deg+alpha)
    u=(radius*cos(angle),radius*sin(angle))
    v=(radius*cos(beta),radius*sin(beta))
    return {ij:(origin[0]+ij[0]*u[0]+ij[1]*v[0],
                origin[1]+ij[0]*u[1]+ij[1]*v[1]) for ij in lattice}
