"""Generate an inspectable geometry demonstration and optional GEOM-002 crossing."""
import json
import sys
from pathlib import Path
from fractions import Fraction as F
from synthesis import point, midpoint, learn, apply, oracles
from benchmark import examples, encode, benchmark
from cartridge import make, verify

HERE=Path(__file__).parent


def svg(abc, values):
    a,b,c=abc
    o,h,n=[values[k] for k in ('circumcenter','orthocenter','nine_point_center')]
    sides=(midpoint(a,b),midpoint(b,c),midpoint(a,c))
    points=[a,b,c,o,h,n,*sides]
    # Cartesian with y flipped for a conventional plot and generous margins.
    coords=[(float(p.x),-float(p.y)) for p in points]
    left=min(x for x,y in coords)-2; right=max(x for x,y in coords)+2
    top=min(y for x,y in coords)-2; bottom=max(y for x,y in coords)+2
    radius=((float((n.x-sides[0].x)**2+(n.y-sides[0].y)**2))**0.5)
    def xy(p): return f'{float(p.x):.3f},{-float(p.y):.3f}'
    elements=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{left:.2f} {top:.2f} {right-left:.2f} {bottom-top:.2f}" role="img" aria-label="Synthesized triangle circumcenter, orthocenter and nine point center">',
        f'<rect x="{left:.2f}" y="{top:.2f}" width="{right-left:.2f}" height="{bottom-top:.2f}" fill="#faf6ed"/>',
        f'<polygon points="{xy(a)} {xy(b)} {xy(c)}" stroke="#315a63" stroke-width=".08" fill="#c6d5d744"/>',
        f'<circle cx="{float(n.x):.3f}" cy="{-float(n.y):.3f}" r="{radius:.3f}" fill="none" stroke="#b17b32" stroke-dasharray=".19 .12" stroke-width=".06"/>']
    for name,p,col in [('A',a,'#315a63'),('B',b,'#315a63'),('C',c,'#315a63'),
                       ('O',o,'#7b5154'),('H',h,'#7b5154'),('N',n,'#b17b32')]:
        x,y=xy(p).split(',')
        elements.extend([f'<circle cx="{x}" cy="{y}" r=".15" fill="{col}"/>',
                         f'<text x="{float(x)+.18:.3f}" y="{float(y)-.18:.3f}" font-size=".7" fill="{col}">{name}</text>'])
    for p in sides:
        x,y=xy(p).split(',')
        elements.append(f'<circle cx="{x}" cy="{y}" r=".11" fill="#b17b32"/>')
    elements.append('</svg>')
    return '\n'.join(elements)+'\n'


def crossing(trained):
    """Read only actual inlier observation indexes from GEOM-002; never holes."""
    parent=HERE.parent/'geometry-002'
    if not (parent/'discover.py').exists():
        return {'status':'HOLD','reason':'GEOM-002 source not available in parent tree'}
    sys.path.insert(0,str(parent))
    from discover import discover, point_set
    coords=point_set('triangular',1.0,19.0,(2.3,-1.2))
    observed=[xy for ij,xy in coords.items() if ij not in {(0,0),(1,0),(-1,1)}]
    result=discover(observed)
    if result['status']!='PROPOSE_ONLY':
        return {'status':'HOLD','reason':'GEOM-002 did not establish a candidate lattice'}
    known=[observed[i] for i in result['inlier_indices']]
    # Select far apart *observed* points; pass exact rational decimal snapshots
    # to the geometric method, not predicted holes.
    witnessed=[]
    for x,y in known:
        witnessed.append(point(str(round(x,6)),str(round(y,6))))
    triple=None
    for a in witnessed:
        for b in witnessed:
            for c in witnessed:
                if a==b or b==c or a==c:
                    continue
                area=(b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x)
                if abs(area)>F(1,5):
                    triple=(a,b,c)
                    break
            if triple:break
        if triple:break
    if not triple:
        return {'status':'HOLD','reason':'insufficient noncollinear witnessed points'}
    geo=apply(trained,triple)
    return {'status':geo['status'], 'source':'GEOM-002 observed inlier indices only',
            'selected_observation_count':3,'geometric_model_status':result['status'],
            'exact_rational_snapshot_witnesses':geo.get('witnesses'),
            'admission':'HOLD','effective_authority':'NONE'}


def run():
    train=examples()[:8]
    learned=learn(train)
    assert learned['status']=='PROPOSE_ONLY'
    example=(point(-4,0),point(5,1),point(1,7))
    found=apply(learned,example)
    assert found['status']=='PROPOSE_ONLY'
    carrier=make(train)
    (HERE/'example-method-cartridge.json').write_text(json.dumps(carrier,indent=2)+'\n')
    (HERE/'triangle-nine-point.svg').write_text(svg(example,found['points']))
    result={
        'experiment':'MOTIF-GEOM-003',
        'programs':{k:v.signature() for k,v in learned['programs'].items()},
        'example_triangle':[encode(p) for p in example],
        'derived_points':{k:encode(p) for k,p in found['points'].items()},
        'exact_certificates':found['witnesses'],
        'carrier_revalidated':verify(carrier),
        'geom002_crossing':crossing(learned),
        'admission':'HOLD',
    }
    (HERE/'experiment-results.json').write_text(json.dumps(result,indent=2)+'\n')
    return result


if __name__=='__main__':
    print(json.dumps(run(),indent=2))
