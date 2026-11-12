"""Opt-in local Qwen3-VL/Ollama photo -> *tentative* object-region packet.

No network call unless --consent-local-model explicitly supplied. Never places
photo pixel boxes in the yard. No physical size, mobility, or structural claims.
"""
from __future__ import annotations
import argparse
import base64
from hashlib import sha256
import json
from pathlib import Path
import re
from urllib.request import Request, urlopen

ROLES = {'boundary_module','support_candidate','flexible_barrier','visual_cue','unknown'}
LOOPBACK = 'http://127.0.0.1:11434/api/chat'

PROMPT = '''Identify at most 12 visible *salvage/material objects* in this image.
Return JSON only: {"objects":[{"label":"short visible label","bbox":[x0,y0,x1,y1],"possible_role":"boundary_module|support_candidate|flexible_barrier|visual_cue|unknown"}]}.
BBox coordinates MUST be normalized floats in [0,1] relative to the photograph.
Boxes should closely cover visible objects, not the whole scene. Ignore people.
Describe only visible evidence. NO physical size measurements, certified stability,
actual mobility, dog safety, boundary route, or photo-to-map coordinates.
When unclear, label 'unknown'. A semantic object role is a hypothesis only.'''


def _check_raw(items):
    if not isinstance(items,list) or len(items)>24:
        raise ValueError('Invalid model objects list')
    results=[]
    for row in items:
        if not isinstance(row,dict) or set(row)-{'label','bbox','possible_role'}:
            raise ValueError('Unsupported model object fields')
        label=row.get('label','')
        bbox=row.get('bbox')
        role=row.get('possible_role')
        if not isinstance(label,str) or not label.strip() or len(label)>120 or role not in ROLES:
            raise ValueError('Unrecognized object/role')
        if not isinstance(bbox,list) or len(bbox)!=4 or any(type(v) not in (float,int) or not 0<=v<=1 for v in bbox):
            raise ValueError('Untrusted bbox values')
        x0,y0,x1,y1=bbox
        if x1-x0<=.005 or y1-y0<=.005:
            raise ValueError('Degenerate bbox')
        results.append({'label':label.strip(),'bbox':bbox,'role':role})
    return results


def make_packet(photo:bytes, photo_id:str, model_output:dict)->dict:
    if not photo or len(photo)>15_000_000 or not isinstance(photo_id,str) or not re.fullmatch(r'[a-zA-Z0-9_.\-]{1,120}',photo_id):
        raise ValueError('Invalid photo or photo id')
    if not isinstance(model_output,dict) or set(model_output)-{'objects'}:
        raise ValueError('Unsupported model response')
    detected=_check_raw(model_output.get('objects'))
    digest=sha256(photo).hexdigest()
    rows=[{'id':f'material-vlm-{digest[:12]}-{i+1:02d}',
           'label':m['label'],'role':m['role'],'status':'tentative','mobility':'unknown',
           'source_frame':'photo_normalized','photo_id':photo_id,'photo_sha256':digest,
           'bbox':m['bbox'],'provenance':'LOCAL_VLM_TENTATIVE','registered_to_sketch':False,
           'certified_safe':False,'width':None} for i,m in enumerate(detected)]
    return {'schema':'motif.field012.materials.v1','coordinate_frame':'photo_normalized',
            'source_kind':'USER_PHOTO','photo_id':photo_id,'photo_sha256':digest,
            'photo_to_sketch_registration':False,'physical_scale_inferred':False,
            'safe_assembly_certified':False,'model_source':'LOCAL_LOOPBACK_UNVERIFIED',
            'items':rows,'note':'Object/region proposals only, not source-grounded construction measurements.'}


def ask_local_model(photo:bytes, model:str, *, consent:bool=False, opener=urlopen):
    if not consent:
        raise PermissionError('Image may not be sent even to localhost without explicit consent')
    if not re.fullmatch(r'[a-zA-Z0-9_.:\-/]{1,100}',model):
        raise ValueError('Invalid model id')
    body={'model':model,'stream':False,'format':'json','messages':[
        {'role':'user','content':PROMPT,'images':[base64.b64encode(photo).decode('ascii')]}]}
    req=Request(LOOPBACK,data=json.dumps(body).encode(),headers={'Content-Type':'application/json'},method='POST')
    with opener(req,timeout=150) as res:
        raw=res.read(1_000_000)
    envelope=json.loads(raw)
    content=envelope.get('message',{}).get('content','')
    return json.loads(content)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--photo',type=Path,required=True)
    parser.add_argument('--photo-id',required=True,help='Use the photo ID shown in the workbench')
    parser.add_argument('--model',default='qwen3-vl:2b-instruct')
    parser.add_argument('--consent-local-model',action='store_true',help='Explicit permission to transfer this photo to local Ollama')
    parser.add_argument('--output',type=Path,required=True)
    a=parser.parse_args()
    photo=a.photo.read_bytes()
    if a.photo.suffix.lower() not in ('.jpg','.jpeg','.png','.webp'):
        raise ValueError('Only PNG, JPEG, WEBP files are allowed')
    output=ask_local_model(photo,a.model,consent=a.consent_local_model)
    packet=make_packet(photo,a.photo_id,output)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(packet,indent=2,ensure_ascii=False))
    print('Tentative candidate count:',len(packet['items']),'— no physical map or fit verified')

if __name__=='__main__':main()
