"""Portable *candidate* method record. A checksum is integrity, not authorship."""
from hashlib import sha256
import json
from synthesis import learn, apply, oracles, Program, point


def encoding(obj) -> bytes:
    return json.dumps(obj,sort_keys=True,separators=(',',':'),allow_nan=False).encode('utf-8')


def _expression(p: Program):
    return {'op':p.op, 'name':p.name,'args':[_expression(a) for a in p.args]}


def make(teachers):
    result=learn(teachers)
    if result['status']!='PROPOSE_ONLY':
        raise ValueError('cannot package a held method')
    from benchmark import encode
    payload={
        'schema':'motif.geometry.method-synthesis.v1',
        'teacher_triangles':[[encode(p) for p in tri] for tri in teachers],
        'constructors':{k:_expression(v) for k,v in result['programs'].items()},
        'program_search_count':result['candidate_programs'],
        'all_candidates_status':'PROPOSAL_ONLY',
        'admission':'HOLD', 'effective_authority':'NONE',
        'notice':'A hash is not authenticated provenance or general theorem proof.'
    }
    return {'payload':payload,'sha256':sha256(encoding(payload)).hexdigest()}


def verify(record):
    try:
        payload=record['payload']
        if payload['schema']!='motif.geometry.method-synthesis.v1':
            return False
        trainers=[tuple(point(*coords) for coords in tri) for tri in payload['teacher_triangles']]
        return encoding(record)==encoding(make(trainers))
    except (ValueError,KeyError,TypeError,OverflowError,ZeroDivisionError):
        return False
