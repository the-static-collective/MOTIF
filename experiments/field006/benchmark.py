"""Authored-annotation audit, not a blind VLM benchmark."""
import json
from pathlib import Path
from atlas import from_dict, audit_preservation, receipt, svg_atlas

HERE=Path(__file__).parent

def run():
    a=from_dict(json.loads((HERE/'fixtures/public_example.json').read_text()))
    return {'case':'invented workshop sketch+photos',
            'retention':audit_preservation(a,('Entry','Wall','Existing shelf')),
            'receipt':receipt(a),
            'limitation':'ALL LABELS PROVIDED BY HUMAN-AUTHORED FIXTURE; NOT VISUAL PERCEPTION'}

if __name__=='__main__':
    print(json.dumps(run(),indent=2))
    (HERE/'output-fixture.svg').write_text(svg_atlas(from_dict(json.loads((HERE/'fixtures/public_example.json').read_text()))))