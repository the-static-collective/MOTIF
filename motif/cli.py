"""Explicit operator CLI: discover every branch, inspect held JSON, reason, compare.

Requires a local MOTIF Git checkout for live branch operations. No branch code
is imported or executed, and all merging remains a separate reviewed action.

Examples:
 python -m motif.cli branches --query "reciprocal"
 python -m motif.cli inspect --ref experiment/reciprocal-004-ecosystem-crosswire-20261112 --path experiments/reciprocal-004/capability-passport.v1.json --case examples/reason-spine-001.json
 python -m motif.cli compare --case examples/reason-spine-001.json
 python -m motif.cli verdict --evidence examples/merge-evidence-held.json
"""
import argparse
import json
from pathlib import Path

from .branch_garden import HoldError, discover, from_census, inspect_json, passport_lenses, suggest, merge_verdict
from .reason_spine import analyze, comparison, CaseError


def _load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".", help="local MOTIF Git checkout")
    sub = parser.add_subparsers(dest="command", required=True)
    branches = sub.add_parser("branches", help="enumerate every visible head, no imports")
    branches.add_argument("--query", default="")
    branches.add_argument("--limit", type=int, default=12)
    branches.add_argument("--all", action="store_true")
    branches.add_argument("--census", help="offline dated branch census; not live")
    inspect = sub.add_parser("inspect", help="read pinned JSON from an unmerged branch")
    inspect.add_argument("--ref", required=True)
    inspect.add_argument("--path", required=True)
    inspect.add_argument("--case")
    compare = sub.add_parser("compare", help="run classical controls and spine on supplied case")
    compare.add_argument("--case", required=True)
    verdict = sub.add_parser("verdict", help="make non-executable merge-review recommendation")
    verdict.add_argument("--evidence", required=True)
    args = parser.parse_args(argv)

    try:
        if args.command == "branches":
            pointers = from_census(_load(args.census)) if args.census else discover(args.repo)
            rows = ([p.as_dict() for p in pointers] if args.all else
                    suggest(args.query, pointers, args.limit) if args.query else
                    [p.as_dict() for p in pointers[:max(0, args.limit)]])
            output = {"schema": "motif.branch-garden/v1",
                      "total_observed": len(pointers),
                      "completeness": ("DATED_SNAPSHOT" if args.census else "LIVE_REMOTE_VISIBLE"),
                      "source_only": True, "code_executed": False, "entries": rows}
        elif args.command == "inspect":
            pointers = discover(args.repo)
            pointer = next((p for p in pointers if p.ref == args.ref), None)
            if pointer is None:
                raise HoldError("No live source pointer; HOLD")
            snapshot = inspect_json(args.repo, pointer, args.path)
            output = {"inspection": {k: v for k, v in snapshot.items() if k != "payload"}}
            try:
                lens = passport_lenses(snapshot)
                output["advisory_lens"] = lens
                if args.case:
                    output["reasoning"] = analyze(_load(args.case), lenses=[lens])
            except HoldError as exc:
                output["advisory_lens"] = {"disposition": "HOLD_UNRECOGNIZED_DATA",
                                           "reason": str(exc)}
        elif args.command == "compare":
            output = comparison(_load(args.case))
        else:
            output = merge_verdict(_load(args.evidence))
    except (HoldError, CaseError, ValueError, OSError, json.JSONDecodeError) as exc:
        output = {"disposition": "HOLD", "reason": str(exc)}
        print(json.dumps(output, indent=2, sort_keys=True))
        return 2
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
