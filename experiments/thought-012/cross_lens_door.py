"""THOUGHT-012 local-only optional JAR;VIS bridge; no server, memory or export.

Use existing THOUGHT-010 strict request schema and real THOUGHT-008 engine.
The caller explicitly chooses two index identities for a pencil inquiry.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
if str(HERE) not in sys.path:sys.path.append(str(HERE))
for family in ('thought-010','thought-008'):
    folder=ROOT/family
    if not folder.is_dir():folder=ROOT/family.replace('-','')
    if str(folder) not in sys.path:sys.path.append(str(folder))
from door import _guard_request, _make_ideas_engine, DoorError, MAX_REQUEST
from cross_lens import CrossLensInquiry

REPLY='motif.thought-cross-door.reply.v1'

def handle(req, seed_a:int, seed_b:int, *, max_steps=3):
    _guard_request(req)
    if req['mode']!='ideas' or req.get('privacy','PRIVATE_LOCAL')!='PRIVATE_LOCAL' or \
       req.get('export','NONE')!='NONE' or req.get('allow_export',False):
        raise DoorError('cross-lens local desk is private idea mode only; no export')
    if req.get('phase','ABSTRACT_PENCIL')=='PEN_REVIEW':
        raise DoorError('cross-lens exploration cannot pretend to be a PEN reviewer')
    ideas=req['ideas']
    if type(seed_a) is not int or type(seed_b) is not int or \
       seed_a==seed_b or not(0<=seed_a<len(ideas)) or not(0<=seed_b<len(ideas)):
        raise DoorError('two distinct known idea indices required; labels cannot identify nodes')
    if type(max_steps) is not int or not 0<=max_steps<=3:
        raise DoorError('local cross-lens budget must be 0..3')
    engine=_make_ideas_engine(req)
    solver=CrossLensInquiry(engine)
    pair=(f'm:{seed_a:02d}',f'm:{seed_b:02d}')
    result=solver.start(seed_pair=pair, max_steps=max_steps,
                        allow_geometry=req.get('show_geometry', True),policy='sequential')
    baseline=solver.start(seed_pair=pair,max_steps=max_steps,
                          allow_geometry=False,policy='sequential')
    if result['carried_questions']!=baseline['carried_questions']:
        raise DoorError('source-only cross-lens parity violated')
    return {'schema':REPLY,'request_id':req['request_id'],'caller':req['caller'],
            'privacy':'PRIVATE_LOCAL','status':'HOLD_FOR_OPERATOR_REVIEW',
            'question_pair_indices':[seed_a,seed_b],
            'source_evidence_digest':result['source_digest'],
            'source_snapshot_digest':result['source_snapshot_digest'],
            'initial_question':result['initial_inquiries'][0],
            'carried_questions':result['carried_questions'],
            'steps':result['steps'],'visited_lenses':result['visited_lenses'],
            'no_map_question_parity':True,'source_roots_authenticated':False,
            'pen_status':'UNCHANGED','external_authority':'NONE',
            'stored':False,'exported':False,'sent_externally':False,
            'warning':'All evidence is operator authored; changing lenses is NOT independent corroboration.'}

def main(argv=None):
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('request_file',type=Path)
    parser.add_argument('--seed-a',required=True,type=int)
    parser.add_argument('--seed-b',required=True,type=int)
    parser.add_argument('--steps',type=int,default=3)
    args=parser.parse_args(argv)
    raw=args.request_file.read_bytes()
    if len(raw)>MAX_REQUEST:raise DoorError('oversized local request')
    try:data=json.loads(raw)
    except (ValueError,UnicodeError) as exc:raise DoorError('invalid request JSON') from exc
    output=handle(data,args.seed_a,args.seed_b,max_steps=args.steps)
    print(json.dumps(output,sort_keys=True,allow_nan=False))

if __name__=='__main__':main()
