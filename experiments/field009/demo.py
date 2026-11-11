"""Invented demonstration: two possible routes, drawing ratios, one known length."""
import json
from pathlib import Path
from geometry import Scene,Trace,Point,Anchor
from planner import Alternative,explore

def demo():
    p=lambda x,y:Point(x,y)
    scene=Scene('invented-paper','SKETCH_APPROX','ground','fixture:nonblind',.40)
    ref=Trace('hypothetical-panel','invented-paper','ground',(p(40,310),p(80,310)),'fixture:drawn 40px',2)
    a=Trace('dotted-route','invented-paper','ground',(p(40,110),p(190,110)),'fixture:drawn target',2)
    b=Trace('rearranged-route','invented-paper','ground',(p(40,110),p(80,155),p(125,155)),'fixture:drawn option',2)
    paths=(Alternative('follow-dotted',a,'fixture:user hypothetical'),
           Alternative('move-boundary',b,'fixture:role reassignment and relocated material'))
    no=explore(scene,ref,paths)
    anchored=explore(scene,ref,paths,Anchor('hypothetical-panel',4,4,'ft','fixture:one known tape length'),3.)
    return {'no_measurements':no,'one_known_measurement':anchored,
            'warning':'All dimensions, proportions and known lengths in this demo are invented. No yard measurements.'}

def make_svg(path):
    svg='''<svg xmlns="http://www.w3.org/2000/svg" width="800" height="350" viewBox="0 0 800 350">
    <rect width="800" height="350" fill="#f7f5f0"/>
    <text x="25" y="34" font-size="23" fill="#222">FIELD-009 / PROPORTION BEFORE PRECISION</text>
    <text x="25" y="60" font-size="14" fill="#555">FICTIONAL REFERENCE SKETCH — not a yard survey</text>
    <rect x="28" y="80" width="370" height="245" fill="white" stroke="#bbb"/>
    <path d="M 65 145 L 355 145" stroke="#af4b37" stroke-width="5" stroke-dasharray="12 9"/>
    <path d="M 65 145 L 143 228 L 237 228" stroke="#277569" stroke-width="5" fill="none"/>
    <text x="430" y="145" font-size="18" fill="#af4b37">Follow drawn dotted route</text>
    <text x="430" y="190" font-size="18" fill="#277569">Explore relocating boundary</text>
    <text x="430" y="245" font-size="15" fill="#444">No known dimension: ratios only</text>
    <text x="430" y="272" font-size="15" fill="#444">One reference: uncertain estimates</text>
    <text x="430" y="299" font-size="15" fill="#444">Perspective/depth unknown: HOLD</text>
    </svg>'''
    Path(path).write_text(svg)

if __name__=='__main__':
    root=Path(__file__).resolve().parent
    data=demo()
    (root/'demo_receipt.json').write_text(json.dumps(data,indent=2))
    make_svg(root/'synthetic_geometry.svg')
    for mode,packet in data.items():
        if isinstance(packet,dict):
            print(mode,packet['decision_confidence'])
            for row in packet['alternatives']:
                print(row['id'],'drawing ratio',round(row['ratio']['center'],2),
                      'length',row['length']['status'],
                      'interval',(row['length']['lower'],row['length']['upper']))
    print('Synthetic only; no real yard measurements or physical safety evidence.')
