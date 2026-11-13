"""Browse ALL visible experimental code at immutable Git commits, without checkout.

A branch's name is not a claim about its implemented behavior. Inspecting code
does not authorize executing or adopting it. Main can keep this module while
source commits live on unmerged branches.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re

from .branch_garden import HoldError, Pointer, _git, discover, valid_ref

READABLE = (".py", ".js", ".mjs", ".cjs", ".json", ".md", ".txt", ".yaml", ".yml")
PATH = re.compile(r"^[A-Za-z0-9._/-]{1,240}$")
MAX_FILE = 128_000
MAX_LIST = 10000


def _path_ok(path):
    return (isinstance(path, str) and bool(PATH.fullmatch(path))
            and not path.startswith(("/", "-", "."))
            and not any(p in ("", ".", "..") for p in path.split("/"))
            and path.endswith(READABLE))


def observe(repo, ref):
    if not valid_ref(ref):
        raise HoldError("Unsafe branch label")
    pointer = next((p for p in discover(repo) if p.ref == ref), None)
    if pointer is None:
        raise HoldError("Branch is not in live visible refs")
    _git(repo, "fetch", "--no-tags", "--depth=1", "origin",
         "refs/heads/" + pointer.ref, max_bytes=10000)
    head = _git(repo, "rev-parse", "FETCH_HEAD").decode().strip()
    if head != pointer.sha:
        raise HoldError("Branch changed after selection; re-observe")
    return pointer


def list_paths(repo, pointer):
    raw = _git(repo, "ls-tree", "-r", "--name-only", pointer.sha,
               max_bytes=2_000_000)
    try:
        paths = raw.decode("utf-8").splitlines()
    except UnicodeDecodeError as exc:
        raise HoldError("Invalid path list encoding") from exc
    if len(paths) > MAX_LIST:
        raise HoldError("Too many files to inspect in one pass")
    return [p for p in paths if _path_ok(p)]


def read_text(repo, pointer, path, include_text=False):
    if not isinstance(pointer, Pointer) or pointer.source != "git-remote":
        raise HoldError("Only currently observed exact remote heads may be used")
    if not _path_ok(path):
        raise HoldError("Only simple bounded source-text paths are supported")
    raw = _git(repo, "show", pointer.sha + ":" + path,
               max_bytes=MAX_FILE)
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise HoldError("Not a UTF-8 text source") from exc
    output = {
        "schema": "motif.branch-source-witness/v1",
        "source": pointer.as_dict(),
        "path": path,
        "bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "status": "HELD_UNMERGED_CODE_WITNESS_NOT_EXECUTED",
        "execution": False,
        "merging": False,
        "authority": "NONE",
    }
    if include_text:
        output["text"] = text
    return output


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--repo", default=".")
    p.add_argument("--ref", required=True)
    p.add_argument("--path")
    p.add_argument("--list", action="store_true")
    p.add_argument("--show", action="store_true", help="include bounded source text")
    args = p.parse_args(argv)
    try:
        pointer = observe(args.repo, args.ref)
        if args.list:
            output = {"source": pointer.as_dict(), "status": "SOURCE_INDEX_ONLY",
                      "paths": list_paths(args.repo, pointer)}
        elif args.path:
            output = read_text(args.repo, pointer, args.path, args.show)
        else:
            raise HoldError("Provide --list or a --path")
    except HoldError as exc:
        output = {"disposition": "HOLD", "reason": str(exc)}
        print(json.dumps(output, indent=2))
        return 2
    print(json.dumps(output, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
