"""One small front door for live discovery + selective MOTIF execution.

The census always runs first. Inert branch source passports NEVER become
executing handlers from a name, manifest, summary, or model preference.
An operator (or separately approved typed caller) must request concrete
installed outputs. No automatic human-language intent inference here.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys

import discovery
import ring
import source_reader
import triad

SCHEMA = "motif.living-cartridge-ring.v1"


def session(*, fetch_page, read_outputs=(), specialist_ids=(), source_ref=None,
            source_query=None, repo_root=None, observed_at=None, native=False):
    """Observe current branch heads on demand and recruit only needed organs."""
    roots = Path(repo_root) if repo_root is not None else Path(__file__).resolve().parents[2]
    rows = discovery.get_branches(fetch_page)
    observed = observed_at or datetime.now(timezone.utc).isoformat(timespec="seconds")
    catalog = discovery.snapshot(rows, observed_at=observed)
    if not isinstance(read_outputs,(tuple,list)) or not isinstance(specialist_ids,(tuple,list)):
        raise discovery.DiscoveryHOLD("Requests must be typed method collections")
    if (source_ref is None) != (source_query is None):
        raise discovery.DiscoveryHOLD("Source inspection needs a branch and a query")
    # The whole snapshot is retained only in the catalog artifact, not misread
    # as 154 verified live reasoning handlers.
    receipt={
        "schema":SCHEMA,
        "catalog_observed_at":catalog["observed_at"],
        "branches_observed_total":catalog["branches_total"],
        "source_only_cartridges_addressable":catalog["cartridges_indexed_non_executable"],
        "admitted_source_native_specialist_ids":sorted(triad.BY_ID),
        "original_ring_outputs_available":sorted(c.provides for c in ring.door.registry()),
        "selected_method_outputs":list(read_outputs),
        "selected_specialists":list(specialist_ids),
        "source_inspection":None,
        "ring_work":None,
        "native_specialist_work":None,
        "this_census_does_not_admit_new_code":True,
        "external_action_executed":False,
        "authority":"NONE",
    }
    if source_ref is not None:
        receipt["source_inspection"]=source_reader.inspect(
            catalog,source_ref,source_query,repo_root=roots)
    if read_outputs:
        receipt["ring_work"]=ring.run(tuple(read_outputs))
    if specialist_ids:
        if not native:
            receipt["native_specialist_work"]={
                "status":"DECLARED_ONLY",
                "reason":"Explicit --native and isolated Docker required to run source-native specialists",
                "selected":list(specialist_ids),
            }
        else:
            receipt["native_specialist_work"]=triad.run(tuple(specialist_ids),
                                                         repo_root=roots)
    body=json.dumps(receipt,sort_keys=True,separators=(",",":"))
    receipt["receipt_sha256"]=hashlib.sha256(body.encode()).hexdigest()
    return receipt


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--offline-frozen",action="store_true",
                   help="Use original reproducible 149-branch snapshot, NOT live discovery")
    p.add_argument("--outputs",nargs="*",default=[])
    p.add_argument("--specialists",nargs="*",default=[])
    p.add_argument("--native",action="store_true",
                   help="Execute specifically pinned native adapters in Docker only")
    p.add_argument("--inspect-branch")
    p.add_argument("--query")
    p.add_argument("--output",type=Path)
    args=p.parse_args()
    if args.offline_frozen:
        rows=discovery.from_frozen_inventory()
        def fetch(page,size):
            cut=rows[(page-1)*size:page*size]
            return [{"name":r,"commit":{"sha":s}} for r,s in cut]
        observed="2026-11-06:FROZEN_NOT_LIVE"
    else:
        def fetch(page,size):
            return discovery.github_page(page,size,os.getenv("GITHUB_TOKEN"))
        observed=None
    try:
        result=session(fetch_page=fetch,read_outputs=tuple(args.outputs),
                       specialist_ids=tuple(args.specialists),
                       source_ref=args.inspect_branch,source_query=args.query,
                       observed_at=observed,native=args.native)
        payload=json.dumps(result,indent=2,sort_keys=True)+"\n"
        if args.output:
            args.output.parent.mkdir(parents=True,exist_ok=True)
            args.output.write_text(payload,encoding="utf-8")
            print(json.dumps({"status":"OK","catalog_count":result[
                "source_only_cartridges_addressable"],
                "receipt_sha256":result["receipt_sha256"],
                "output":str(args.output)}))
        else:
            print(payload,end="")
    except (discovery.DiscoveryHOLD,source_reader.HOLD,triad.HOLD,ring.HOLD) as exc:
        print(json.dumps({"status":"HOLD","reason":str(exc),
                          "no_execution_grant":True}),file=sys.stderr)
        raise SystemExit(2)


if __name__=="__main__":
    main()
