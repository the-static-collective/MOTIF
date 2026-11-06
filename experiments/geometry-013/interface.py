"""Strict local JSON CLI; no network, shell, or physical instruments."""
import json
import sys
from pathlib import Path
from redesign import run_document

if __name__=='__main__':
    if len(sys.argv)!=2:
        raise SystemExit('usage: python interface.py <local-json-document>')
    path=Path(sys.argv[1])
    if not path.is_file() or path.stat().st_size>2_000_000:
        raise SystemExit('input must be an existing local JSON file at most 2 MB')
    with path.open(encoding='utf-8') as source:
        document=json.load(source)
    print(json.dumps(run_document(document),ensure_ascii=False,indent=2,sort_keys=True))
