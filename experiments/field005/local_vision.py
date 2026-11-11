"""Opt-in, local-only Ollama perceptual and visual reinspection adapter.

Requires Ollama running on user's own machine; no model download or
outside network call is performed. All model claims are MODEL_TENTATIVE.
"""
from __future__ import annotations
import base64, json, mimetypes
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.parse import urlparse
from typing import Any
from visual_thought import load

SYSTEM = '''Return ONLY a JSON object containing 'things' (an array of objects).
Each object has: id, label, original_use, capabilities (a subset of:
delineate,support,hold,organize,shelter,route,elevate), features (subset of:
flat,rigid,flexible,frame,container,connector,weight,surface),
movable (YES,NO,UNKNOWN), bbox (4 normalized floats or null), source.
Only include clearly visible objects. Do not infer permission, capacity,
material ratings, actual dimensions or safe usage. Missing values UNKNOWN.
Object origin must always be MODEL_TENTATIVE. Never fabricate sketch
mark meaning. Return no geographic details, people names or identifications.
'''


def endpoint_check(endpoint:str):
    u=urlparse(endpoint)
    if u.scheme!='http' or u.hostname not in ('127.0.0.1','localhost','::1') or u.username or u.password:
        raise ValueError("Only local Ollama loopback is permitted")
    if u.port != 11434 or u.path!='/api/chat' or u.query or u.fragment:
        raise ValueError("Only local Ollama /api/chat on port 11434 is permitted")


def _chat(images:list[Path], prompt:str, model:str, endpoint:str,
          consent:bool, transport=None)->dict:
    endpoint_check(endpoint)
    if not consent: raise PermissionError("Explicit local image submission permission required")
    if not images or len(images)>12: raise ValueError("Expected 1-12 images")
    imgdata=[]
    for f in images:
        f=Path(f)
        if f.suffix.lower() not in {'.png','.jpg','.jpeg','.webp'}:
            raise ValueError("Unsupported raster image")
        if not f.is_file() or f.stat().st_size>12_000_000:raise ValueError("Missing or oversized image")
        imgdata.append(base64.b64encode(f.read_bytes()).decode())
    if not model or len(model)>80:raise ValueError("Invalid model name")
    body={"model":model,"stream":False,"format":"json",
          "messages":[{"role":"user","content":prompt,"images":imgdata}],
          "options":{"temperature":0}}
    send=transport or _real_transport
    response=send(endpoint,body)
    content=response.get('message',{}).get('content')
    if not isinstance(content,str):raise ValueError("Model response missing content")
    result=json.loads(content)
    if not isinstance(result,dict):raise ValueError("Expected model object")
    return result


def _real_transport(endpoint:str,body:dict)->dict:
    req=Request(endpoint,data=json.dumps(body).encode(),headers={"Content-Type":"application/json"},method='POST')
    with urlopen(req,timeout=180) as r: return json.loads(r.read(2_000_000))


def perceive(images:list[Path],goal:str,desired_function:str,*,consent=False,
             model='qwen3-vl:2b-instruct',endpoint='http://127.0.0.1:11434/api/chat',transport=None):
    response=_chat(images,SYSTEM+"\nGoal: "+goal,model,endpoint,consent,transport)
    if set(response)-{'things'} or not isinstance(response.get('things'),list):
        raise ValueError("Unexpected perceptual envelope")
    rows=[]
    for i,row in enumerate(response['things']):
        if not isinstance(row,dict):raise ValueError("Invalid object")
        allowed={'label','original_use','capabilities','features','movable','bbox','source','id','origin'}
        if set(row)-allowed:raise ValueError("Invalid object field")
        row={**row,"id":f"vision-{i+1}","origin":"MODEL_TENTATIVE",
             "source":f"local-ollama:{model}"}
        rows.append(row)
    return load({"goal":goal,"desired_function":desired_function,"source":"LOCAL_VLM_UNVERIFIED", "things":rows})


def reread_diagram(image_png:Path,*,consent=False,model='qwen3-vl:2b-instruct',
                   transport=None):
    """Read back a *rasterized* scratchpad as a tentative second opinion.
    The output cannot clear a safety HOLD or prove measurements.
    """
    res=_chat([Path(image_png)],
      "Inspect this SCHEMATIC drawing. Identify any visible layout ambiguities or labels that overlap. "
      "Return JSON with strings in field 'comments'. Do not assert physical dimensions or safety.",
      model,'http://127.0.0.1:11434/api/chat',consent,transport)
    comments=res.get('comments',[])
    if not isinstance(comments,list) or any(not isinstance(s,str) for s in comments):
        raise ValueError("Bad visual critique")
    return {"model":model,"status":"MODEL_TENTATIVE_ONLY", "comments":comments[:10],"clears_safety_hold":False}