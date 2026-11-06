"""Bounded JSON CLI. No remote access, code loading from input or side effects."""
import json
import sys
from contextual import run_document

def main():
    if len(sys.argv)!=2:
        raise SystemExit('usage: python interface.py bounded-input.json')
    with open(sys.argv[1],encoding='utf-8') as f:
        doc=json.load(f)
    print(json.dumps(run_document(doc),sort_keys=True,indent=2))

if __name__=='__main__':main()
