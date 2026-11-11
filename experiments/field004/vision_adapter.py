"""Opt-in multimodal image intake for the FIELD-004 reframe experiment.

Raw photos stay local unless allow_external=True is explicitly supplied.
No real-model inference or unprompted photo understanding validated here.
"""
from __future__ import annotations

import base64
import json
import mimetypes
from pathlib import Path
from typing import Any

from engine import Input, Observation, VALID_KIND

PERCEPTION_PROMPT = """You are an EVIDENCE EXTRACTOR, not a construction recommender.
Observe each supplied photo/sketch. Produce ONLY one JSON object:
{"observations":[{"id":"v:0","kind":"EXISTING_BARRIER","subject":"...",
"status":"PHOTO_OBSERVED","source":"image:0","detail":"..."}]}
Kinds allowed: GOAL_BOUNDARY,TARGET_ROUTE,EXISTING_BARRIER,RIGID_PANEL,FLEXIBLE_MESH,ANCHOR_CANDIDATE,STRUCTURE,CONNECTOR,ACCESS_ROUTE,HAZARD,BEHAVIOR,OTHER.
Status only PHOTO_OBSERVED, SKETCH_LABELED, MODEL_TENTATIVE.
Use image:N exactly matching numbered images. Every fact must point to a photo.
Describe visible objects/arrangements. If marks look like a desired route, use
TARGET_ROUTE and MODEL_TENTATIVE unless explicitly labeled new/desired.
Uncertainty is not permission to move property, a measurement, engineering
capacity or proof of dog behavior. Never infer dimensions, property rights,
structural load ratings or guaranteed pet containment.
Do not invent ties, clamps, fasteners or supplies not visibly identifiable.
Do not copy addresses, faces, license plates or private identifying information.
Use MODEL_TENTATIVE with a reason when uncertain. Max 40 observations.
Return no code fences or explanatory prose.
"""


def _parse_json(text: str) -> dict:
    txt=text.strip()
    if txt.startswith('```'):
        txt=txt.removeprefix('```json').removeprefix('```JSON').removeprefix('```')
        txt=txt.split('```',1)[0].strip()
    data=json.loads(txt)
    if not isinstance(data, dict) or set(data)!={'observations'}:
        raise ValueError('vision output must contain only observations')
    if not isinstance(data['observations'],list) or len(data['observations'])>40:
        raise ValueError('model returned invalid observation count')
    return data


def _validated_input(goal: str, data: dict, n_images: int) -> Input:
    values=[]
    allowed={'id','kind','subject','status','source','detail'}
    for item in data['observations']:
        if not isinstance(item,dict) or not set(item).issubset(allowed):
            raise ValueError('unexpected visual observation shape')
        if item.get('status') not in ('PHOTO_OBSERVED','SKETCH_LABELED','MODEL_TENTATIVE'):
            raise ValueError('vision model claimed user testimony or authority')
        if item.get('source') not in {f'image:{i}' for i in range(n_images)}:
            raise ValueError('observation cites an unknown image')
        if item.get('kind') not in VALID_KIND:
            raise ValueError('unknown kind')
        values.append(Observation(**item))
    if not any(v.kind=='GOAL_BOUNDARY' for v in values):
        values.insert(0, Observation('goal:0','GOAL_BOUNDARY','desired boundary',
                                     'USER_REPORTED','human:request',goal[:180]))
    packet=Input(goal=goal, observations=tuple(values))
    packet.check()
    return packet


def ingest_photos(image_paths: list[str], goal: str, *, model: str,
                  allow_external: bool=False, client: Any=None) -> Input:
    """Explicit opt-in transfer to vision API. Mockable without network."""
    if not allow_external:
        raise PermissionError('Sending user photos externally requires explicit opt-in')
    if not (1<=len(image_paths)<=12) or not model:
        raise ValueError('requires 1-12 images and an explicit model identifier')
    content=[{'type':'input_text','text':PERCEPTION_PROMPT+'\nUser goal: '+goal}]
    for p in image_paths:
        path=Path(p)
        media=mimetypes.guess_type(path.name)[0]
        if media not in ('image/png','image/jpeg','image/webp'):
            raise ValueError('Only PNG/JPEG/WEBP inputs supported')
        if not path.is_file() or not 0 < path.stat().st_size <= 15_000_000:
            raise ValueError('Missing or oversized image')
        payload=base64.b64encode(path.read_bytes()).decode('ascii')
        content.append({'type':'input_image',
                        'image_url':f'data:{media};base64,{payload}','detail':'high'})
    if client is None:
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError('Optional OpenAI Python SDK not installed') from exc
        client=OpenAI()
    response=client.responses.create(model=model,input=[{'role':'user','content':content}])
    return _validated_input(goal,_parse_json(response.output_text),len(image_paths))
