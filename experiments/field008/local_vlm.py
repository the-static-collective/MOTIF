"""Optional OpenAI-independent *localhost-only* Ollama vision intake.

No network requests occur unless explicitly invoked. Remote endpoints are refused.
Images are sent only to an already running local server on loopback.
"""
from __future__ import annotations
from pathlib import Path
from urllib.parse import urlsplit
import base64, json, urllib.request

PROMPT = '''You are a cautious sketch/photo interpreter. Return only a JSON object:
{"source_id":"SOURCE_ID","claims":[{"id":"c1","kind":"VISIBLE_MARK","style":"DOTTED","points":[[0.1,0.2],[0.4,0.2]],"label":""}],"uncertainty":"...","claimed_complete_route":false}
Coordinate values are proportions of the original image width and height. For the SKETCH:
- Identify short source-visible dotted fragments and solid strokes separately.
- Do not use ruled-paper lines as fencing or join missing strokes.
- Label only visually present objects/text. Do not assume measurements or exact property geometry.
- A separate photo cannot be located on this sketch without actual correspondence evidence.
- Quote specific uncertainty; no invented safe-construction advice.
Return at most 20 tentative claims. Do not infer a complete fence route.
'''

def checked_endpoint(url:str):
    p=urlsplit(url)
    if p.scheme!='http' or p.hostname not in ('127.0.0.1','localhost','::1') or p.username or p.password or p.query or p.fragment:
        raise ValueError('Only unauthenticated HTTP localhost Ollama endpoint allowed')
    if p.port not in (None,11434):raise ValueError('Unexpected local server port')
    if p.path not in ('','/api/chat'):raise ValueError('Unexpected endpoint path')
    return 'http://127.0.0.1:11434/api/chat'

def request_payload(source:str, image_file:str|Path,model:str='qwen3-vl:2b-instruct'):
    data=Path(image_file).read_bytes()
    if len(data)>12*1024*1024:raise ValueError('Image size limit exceeded')
    if not (data.startswith(b'\xff\xd8') or data.startswith(b'\x89PNG\r\n\x1a\n') or data[:4]==b'RIFF' and data[8:12]==b'WEBP'):
        raise ValueError('Only JPEG, PNG or WEBP images')
    if not source or len(source)>90:raise ValueError('Invalid source id')
    return {'model':model,'stream':False,'format':'json','options':{'temperature':0},'messages':[
        {'role':'user','content':PROMPT.replace('SOURCE_ID',source),'images':[base64.b64encode(data).decode('ascii')]}]}

def perceive_local(source,image_file, *, explicit_local_model:bool=False, endpoint='http://127.0.0.1:11434/api/chat',model='qwen3-vl:2b-instruct',transport=None):
    if not explicit_local_model:raise PermissionError('No image transfer without explicit local-model invocation')
    url=checked_endpoint(endpoint)
    p=request_payload(source,image_file,model=model)
    data=json.dumps(p).encode()
    if transport:
        raw=transport(url,data)
    else:
        req=urllib.request.Request(url,data=data,headers={'Content-Type':'application/json'},method='POST')
        with urllib.request.urlopen(req,timeout=180) as r:raw=r.read(1_200_000)
    answer=json.loads(raw)
    content=answer.get('message',{}).get('content')
    if not isinstance(content,str):raise ValueError('Ollama reply missing text content')
    packet=json.loads(content)
    if packet.get('source_id')!=source:raise ValueError('Unexpected source id')
    return {'packet':packet,'model_receipt':{'model':answer.get('model',model),'done':answer.get('done',False),
        'eval_count':answer.get('eval_count'),'prompt_eval_count':answer.get('prompt_eval_count'),
        'image_sent_to':'localhost only','response_mode':'MODEL_TENTATIVE'}}
