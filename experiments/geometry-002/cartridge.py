"""MOTIF geometry-002 candidate schema. Local evidence ONLY; admission remains HOLD."""
import hashlib
import json
from discover import discover


def _bytes(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':'),
                      allow_nan=False).encode('utf-8')


def make_cartridge(points, *, min_coverage=0.68):
    original = [[float(x),float(y)] for x,y in points]
    result = discover(original, min_coverage=min_coverage)
    payload = {
        'schema':'motif.geometry.discovery.v1',
        'input_points':original,
        'minimum_coverage':min_coverage,
        'result':result,
        'admission':'HOLD',
        'effective_authority':'NONE',
        'reason':'candidate model does not authenticate origin, fact, or action',
    }
    return {'payload':payload,
            'sha256':hashlib.sha256(_bytes(payload)).hexdigest()}


def verify_cartridge(cartridge):
    try:
        payload = cartridge['payload']
        if not isinstance(cartridge['sha256'],str):
            return False
        expected = make_cartridge(payload['input_points'],
                                  min_coverage=payload['minimum_coverage'])
        return (_bytes(payload)==_bytes(expected['payload']) and
                cartridge['sha256']==expected['sha256'])
    except (ValueError, TypeError, KeyError, OverflowError):
        return False
