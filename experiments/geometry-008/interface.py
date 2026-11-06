"""Local JSON CLI; no unapproved external action, model request or network."""
import argparse
import json
from living_graph import run_document
from display import render_dot


def main():
    ap = argparse.ArgumentParser(description='GEOM-008 resumable living hypergraph')
    ap.add_argument('request', help='JSON request path; contains grammar and seed')
    ap.add_argument('--db', default=':memory:', help='SQLite path to resume across calls')
    ap.add_argument('--dot', default=None, help='optional output path for bounded DOT view')
    args = ap.parse_args()
    with open(args.request, encoding='utf-8') as handle:
        data = json.load(handle)
    result = run_document(data, filename=args.db)
    if args.dot:
        with open(args.dot, 'w', encoding='utf-8') as handle:
            handle.write(render_dot(result['local_view']))
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
