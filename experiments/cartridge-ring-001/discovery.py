"""RING-002: discover every current and future GitHub branch as a read-only passport.

No branch code is downloaded or executed by discovery. A branch pointer is not an
admitted executable cartridge. The live API can fail or be stale, so no silent
fallback or inference of absence is permitted.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

HERE = Path(__file__).resolve().parent
REPO = "the-static-collective/MOTIF"
API = "https://api.github.com/repos/the-static-collective/MOTIF/branches"
REF = re.compile(r"^[A-Za-z0-9._/-]{1,250}$")
SHA = re.compile(r"^[a-f0-9]{40}$")
SCHEMA = "motif.branch-garden.v2"
ROOTS = ("experiment/", "experiments/", "research/", "plan/")
MAX_BRANCHES = 2000
MAX_PAGES = 20


class DiscoveryHOLD(ValueError):
    pass


def _validate(rows):
    if not isinstance(rows, list) or len(rows) > MAX_BRANCHES:
        raise DiscoveryHOLD("Invalid or excessive branch count")
    found = set()
    clean = []
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("name"), str):
            raise DiscoveryHOLD("Malformed branch entry")
        ref = row["name"]
        commit = row.get("commit")
        sha = commit.get("sha") if isinstance(commit, dict) else None
        if (not REF.fullmatch(ref) or not SHA.fullmatch(str(sha)) or ref in found):
            raise DiscoveryHOLD("Bad, missing, or duplicate branch identity")
        found.add(ref)
        clean.append((ref, sha))
    return tuple(sorted(clean))


def get_branches(fetch_page, *, per_page=100):
    """Paginate until an actual short/empty page; never assume 149 is fixed."""
    if type(per_page) is not int or not 1 <= per_page <= 100:
        raise DiscoveryHOLD("Invalid page size")
    received = []
    for page in range(1, MAX_PAGES + 1):
        data = fetch_page(page, per_page)
        if not isinstance(data, list):
            raise DiscoveryHOLD("GitHub did not provide a branch array")
        received.extend(data)
        if len(received) > MAX_BRANCHES:
            raise DiscoveryHOLD("Branch count exceeded safety cap")
        if len(data) < per_page:
            return _validate(received)
    raise DiscoveryHOLD("Discovery truncated at page cap; never claim completeness")


def github_page(page, per_page, token=None):
    url = API + f"?per_page={per_page}&page={page}"
    headers = {"Accept": "application/vnd.github+json",
               "User-Agent": "motif-branch-garden-readonly/2",
               "X-GitHub-Api-Version": "2022-11-28"}
    if token:
        headers["Authorization"] = "Bearer " + token
    try:
        with urlopen(Request(url, headers=headers), timeout=15) as response:
            data = response.read(1_500_001)
            if len(data) > 1_500_000:
                raise DiscoveryHOLD("Oversized branch page")
            return json.loads(data.decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, OSError, ValueError) as exc:
        raise DiscoveryHOLD("Live GitHub discovery unavailable or invalid") from exc


def passport(ref, sha):
    """All branches are addressable as immutable SOURCE POINTERS, not code."""
    return {
        "id": "motif.branch-source:" + hashlib.sha256(
            (ref + "@" + sha).encode("utf-8")).hexdigest()[:20],
        "ref": ref,
        "commit": sha,
        "family": next((p[:-1] for p in ROOTS if ref.startswith(p)), "other"),
        "status": "INDEXED_NON_EXECUTABLE",
        "source_kind": "GIT_COMMIT_POINTER_ONLY",
        "readable_source": True,
        "executable": False,
        "authority": "NONE",
        "description_is_not_a_verified_contract": True,
    }


def snapshot(rows, *, observed_at):
    if not isinstance(observed_at, str) or not observed_at:
        raise DiscoveryHOLD("Explicit timestamp needed")
    cards = [passport(ref, sha) for ref, sha in rows if ref != "main"]
    data = {
        "schema": SCHEMA,
        "repository": REPO,
        "observed_at": observed_at,
        "coverage": "ALL_RETURNED_PAGES_VALIDATED",
        "not_a_compatibility_or_admission_test": True,
        "read_only": True,
        "branches_total": len(rows),
        "cartridges_indexed_non_executable": len(cards),
        "passports": cards,
    }
    return data


def delta(before, after):
    """Missing branch is a missing ref *in this census*, not deleted evidence."""
    def by_ref(v):
        if v.get("schema") != SCHEMA:
            raise DiscoveryHOLD("Wrong catalog schema")
        return {x["ref"]: x["commit"] for x in v["passports"]}
    a, b = by_ref(before), by_ref(after)
    return {
        "added": sorted(b.keys() - a.keys()),
        "not_seen_now": sorted(a.keys() - b.keys()),
        "moved": sorted(n for n in a.keys() & b.keys() if a[n] != b[n]),
        "unchanged": sum(a[n] == b[n] for n in a.keys() & b.keys()),
        "no_automatic_branch_execution": True,
    }


def from_frozen_inventory():
    """Deterministic starting point for tests; NOT a live branch census."""
    p = json.loads((HERE / "branch_inventory.json").read_text())
    if p.get("schema") != "motif.branch-ring-inventory.v1":
        raise DiscoveryHOLD("Invalid frozen census")
    return _validate([{"name": "main",
                        "commit": {"sha": "0" * 40}}] +
                     [{"name": x["ref"], "commit": {"sha": x["commit"]}}
                      for x in p["branches"]])


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--offline-frozen", action="store_true")
    p.add_argument("--output", type=Path)
    p.add_argument("--previous", type=Path)
    args = p.parse_args()
    try:
        if args.offline_frozen:
            rows = from_frozen_inventory()
            observed = "2026-11-06:FROZEN_SNAPSHOT_NOT_LIVE"
        else:
            import os
            rows = get_branches(lambda page, size: github_page(
                page, size, token=os.getenv("GITHUB_TOKEN")))
            observed = datetime.now(timezone.utc).isoformat(timespec="seconds")
        data = snapshot(rows, observed_at=observed)
        if args.previous:
            old = json.loads(args.previous.read_text(encoding="utf-8"))
            data["delta"] = delta(old, data)
        output = json.dumps(data, indent=2, sort_keys=True) + "\n"
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(output, encoding="utf-8")
            print(json.dumps({"status": "INDEXED", "branches_total": len(rows),
                              "passports": len(data["passports"]),
                              "output": str(args.output)}, sort_keys=True))
        else:
            print(output, end="")
    except DiscoveryHOLD as exc:
        print(json.dumps({"status": "HOLD", "reason": str(exc),
                          "no_auto_execution": True}), file=sys.stderr)
        raise SystemExit(2)


if __name__ == "__main__":
    main()
