"""A frozen, reproducible synthetic discovery of a rotated flower."""
import json
import random
from math import hypot
from pathlib import Path
from discover import discover, point_set
from cartridge import make_cartridge, verify_cartridge

HERE=Path(__file__).parent


def scenario():
    rng=random.Random(770)
    truth=point_set('triangular',1.0,23,(1.2,-0.5))
    absent={(0,0),(1,0),(-1,1)}
    observed=[v for k,v in truth.items() if k not in absent]
    rng.shuffle(observed)
    noisy=[(x+rng.gauss(0,0.015),y+rng.gauss(0,0.015)) for x,y in observed]
    noisy += [(rng.uniform(-3,4),rng.uniform(-4,3)) for _ in range(2)]
    return noisy,truth,absent


def svg(points,report):
    all_points=list(points)+[p['xy'] for p in report['holes']]
    left=min(x for x,y in all_points)-1.4
    top=min(y for x,y in all_points)-1.4
    width=max(x for x,y in all_points)-left+1.4
    height=max(y for x,y in all_points)-top+1.4
    body=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{left:.3f} {top:.3f} {width:.3f} {height:.3f}" role="img" aria-label="Observed points and inferred flower of life circle candidates">',
          f'<rect x="{left:.3f}" y="{top:.3f}" width="{width:.3f}" height="{height:.3f}" fill="#fbf7ee"/>']
    seen=set(report['inlier_indices'])
    radius=min(report['rule']['axis_lengths'])
    for idx,(x,y) in enumerate(points):
        col='#385d66' if idx in seen else '#bf6d52'
        if idx in seen:
            body.append(f'<circle cx="{x:.4f}" cy="{y:.4f}" r="{radius:.4f}" fill="none" stroke="{col}" stroke-width=".012"/>')
        body.append(f'<circle cx="{x:.4f}" cy="{y:.4f}" r=".043" fill="{col}"/>')
    for p in report['holes']:
        x,y=p['xy']
        body.append(f'<circle cx="{x:.4f}" cy="{y:.4f}" r="{radius:.4f}" fill="none" stroke="#98742a" stroke-dasharray=".10 .09" stroke-width=".018"/>')
        body.append(f'<circle cx="{x:.4f}" cy="{y:.4f}" r=".055" fill="#98742a"/>')
    body.append('</svg>')
    return '\n'.join(body)+'\n'


def run():
    points,truth,missing=scenario()
    report=discover(points)
    if report['status'] != 'PROPOSE_ONLY':
        raise AssertionError('frozen reconstruction abstained')
    recovered=sum(any(hypot(p['xy'][0]-x,p['xy'][1]-y)<0.2
                      for p in report['holes'])
                  for k,(x,y) in truth.items() if k in missing)
    carrier=make_cartridge(points)
    result={
        'experiment':'MOTIF-GEOM-002',
        'input':'16 observed noisy centers + 2 distractors, three hidden among 19 centers',
        'observed_points':len(points),
        'withheld_centers':len(missing),
        'recovered_withheld_centers':recovered,
        'proposed_hole_count':len(report['holes']),
        'fitted_rule':report['rule'],
        'coverage':report['coverage'],
        'candidate_count':report['tested_hypotheses'],
        'cartridge_verified':verify_cartridge(carrier),
        'authority':'HOLD: synthetic geometric proposal, not an observed event',
    }
    (HERE/'example-discovery-cartridge.json').write_text(json.dumps(carrier,indent=2)+'\n')
    (HERE/'flower-discovery.svg').write_text(svg(points,report))
    (HERE/'experiment-results.json').write_text(json.dumps(result,indent=2)+'\n')
    return result

if __name__=='__main__':
    print(json.dumps(run(),indent=2))
