"""Opt-in open-weights VLM image intake for FIELD-013.

Uses FIELD-012's constrained localhost Qwen3-VL/Ollama adapter. Each photograph
is treated separately; an imported box is never mapped to yard coordinates.
No server is contacted until `consent_local_model=True`.
"""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import argparse, json, re, sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'field012'))
from local_vlm import ask_local_model, make_packet

@dataclass(frozen=True)
class PhotoRequest:
    photo_id: str
    path: Path


def parse_photo(spec: str) -> PhotoRequest:
    if '=' not in spec: raise ValueError('Use photo-id=/private/path.png')
    name,path = spec.split('=', 1)
    if not re.fullmatch(r'[A-Za-z0-9_.-]{1,120}',name) or not path:
        raise ValueError('Invalid photo identifier')
    local=Path(path).expanduser()
    if local.suffix.lower() not in ('.jpg','.jpeg','.png','.webp'):
        raise ValueError('Unsupported photo format')
    return PhotoRequest(name,local)


def inspect(reqs: list[PhotoRequest],model='qwen3-vl:2b-instruct',*,consent=False,ask=ask_local_model):
    if not consent: raise PermissionError('Explicit local model consent required')
    if not 1<=len(reqs)<=20: raise ValueError('Expect 1–20 photographs')
    if len({r.photo_id for r in reqs})!=len(reqs):raise ValueError('Duplicate photo IDs')
    packets=[]
    for req in reqs:
        photo=req.path.read_bytes()
        if len(photo)>15_000_000:raise ValueError('Photo too large')
        prediction=ask(photo,model,consent=True)
        packet=make_packet(photo,req.photo_id,prediction)
        packets.append(packet)
    return {'schema':'motif.field013.batch.v1',
            'engine':'REAL_LOCAL_VLM_IF_RUN__NO_INDEPENDENT_VERIFICATION',
            'model_name':model,'photo_to_yard_registration':False,
            'structural_safety_verified':False,'physical_dimensions_verified':False,
            'packets':packets,
            'recommendation':'Import each photo packet or batch into local workbench; confirm boxes, roles and mobility before planning.'}


def main():
    p=argparse.ArgumentParser(description='Opt-in local Qwen3-VL materials scan; outputs tentative photo regions')
    p.add_argument('--photo',action='append',required=True,help='Photo identifier matching board, e.g. photo-0=/private/yard.jpg')
    p.add_argument('--model',default='qwen3-vl:2b-instruct')
    p.add_argument('--consent-local-model',action='store_true')
    p.add_argument('--output',required=True,type=Path)
    args=p.parse_args()
    r=inspect([parse_photo(x) for x in args.photo],args.model,consent=args.consent_local_model)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(r,indent=2,ensure_ascii=False),encoding='utf-8')
    print(f"Local model inference requested for {len(r['packets'])} photos; results tentative, not verified.")

if __name__=='__main__':main()
