import json
import sys
from grammar_invention import run_document

if __name__=='__main__':
    if len(sys.argv)!=2:
        raise SystemExit('usage: python interface.py input.json')
    with open(sys.argv[1], encoding='utf-8') as stream:
        document=json.load(stream)
    print(json.dumps(run_document(document),indent=2,sort_keys=True))
