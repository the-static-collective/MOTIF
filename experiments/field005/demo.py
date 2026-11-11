"""FIELD-005 demo. Default: entirely offline, synthetic, no photos."""
import argparse, json
from pathlib import Path
from benchmark import scenarios
from visual_thought import run,think,svg_sketch

p=argparse.ArgumentParser(description='MOTIF FIELD-005 visual scratchpad')
p.add_argument('--scenario',choices=tuple(scenarios()),default='yard')
p.add_argument('--out',type=Path,default=Path('outputs/demo'))
p.add_argument('--photos',type=Path,nargs='+')
p.add_argument('--goal',default='Arrange existing objects into a useful configuration')
p.add_argument('--function',choices=('delineate','support','hold','organize','shelter','route','elevate'),default='delineate')
p.add_argument('--allow-local-images',action='store_true',help='Explicitly permit sending images to LOCAL Ollama')
p.add_argument('--model',default='qwen3-vl:2b-instruct')
p.add_argument('--reread-local-sketch',action='store_true',help='Use locally installed CairoSVG and local Ollama to reread diagram')
a=p.parse_args()
if a.photos:
 from local_vision import perceive
 scene=perceive(a.photos,a.goal,a.function,consent=a.allow_local_images,model=a.model)
else:
 scene=scenarios()[a.scenario]
a.out.mkdir(exist_ok=True,parents=True)
receipt=run(scene)
svg=svg_sketch(scene,think(scene))
(a.out/'scratchpad.svg').write_text(svg,encoding='utf-8')
(a.out/'receipt.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
if a.reread_local_sketch:
 if not a.allow_local_images:raise PermissionError('Local image permission required for visual reread')
 try:
  import cairosvg
 except ImportError as e:raise RuntimeError('Install cairosvg to rasterize SVG to PNG') from e
 from local_vision import reread_diagram
 png=a.out/'scratchpad.png'
 cairosvg.svg2png(bytestring=svg.encode(),write_to=str(png))
 feedback=reread_diagram(png,consent=True,model=a.model)
 (a.out/'visual_feedback.json').write_text(json.dumps(feedback,indent=2),encoding='utf-8')
print(json.dumps({'scene':scene.source,'hypotheses':len(receipt['proposals']),
 'safety_review_pending':True,'visual_model_used':bool(a.photos or a.reread_local_sketch),
 'files':[str(a.out/'scratchpad.svg'),str(a.out/'receipt.json')]},indent=2))