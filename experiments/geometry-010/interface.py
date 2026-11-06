"""MOTIF GEOM-010 finite local JSON entry point; no external services."""
import json
import sys
from pathlib import Path
from reason_lab import run_document

if __name__ == '__main__':
    if len(sys.argv)!=2:
        raise SystemExit('usage: python interface.py <lab-input.json>')
    location=Path(sys.argv[1])
    if location.stat().st_size>2_000_000:
        raise SystemExit('input exceeds 2MB local interface capacity')
    result=run_document(json.loads(location.read_text(encoding='utf-8')))
    print(json.dumps(result,sort_keys=True,indent=2))
