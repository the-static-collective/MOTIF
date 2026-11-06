"""Local JSON-only CLI. Read-only analysis, no sensor/network execution."""
import json
import sys
from pathlib import Path
from missing_dimension import run_document


def main():
    if len(sys.argv) != 2:
        raise SystemExit('usage: python interface.py INPUT.json')
    path = Path(sys.argv[1])
    if path.stat().st_size > 2_000_000:
        raise ValueError('input exceeds 2 MB local interface bound')
    data = json.loads(path.read_text(encoding='utf-8'))
    print(json.dumps(run_document(data), sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
