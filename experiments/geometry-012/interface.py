"""Strict local JSON interface for GEOM-012. Does not call external sensors."""
import json
import sys
from pathlib import Path
from instrument_lab import run_document


def main(argv):
    if len(argv)!=2:
        raise SystemExit('usage: python interface.py <local-request.json>')
    path=Path(argv[1])
    if path.stat().st_size>2_000_000:
        raise ValueError('local JSON request exceeds 2 MB')
    data=json.loads(path.read_text(encoding='utf-8'))
    print(json.dumps(run_document(data),indent=2,sort_keys=True))

if __name__=='__main__':main(sys.argv)
