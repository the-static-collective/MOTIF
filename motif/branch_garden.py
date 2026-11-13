"""MOTIF Branch Garden: all visible Git refs as source-pinned, non-executable candidates.

The remote is read-only for discovery and Git object retrieval; fetch updates only
FETCH_HEAD. No checkout, import, eval, test command, merge, or repository write occurs.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

SHA = re.compile(r"^[0-9a-f]{40}$")
REF = re.compile(r"^(?![-/])(?!.*(?:\.\.|//|@\{|\\))[A-Za-z0-9._/-]{1,240}(?<![/.])$")
PATH = re.compile(r"^[A-Za-z0-9._/-]{1,240}\.json$")
MAX_JSON_BYTES = 65536
ALLOWED_SCHEMAS = {"motif.reciprocal-capability-passport/v1"}
ALLOWED_CAPABILITIES = {"two-doors", "reason-field", "method-foundry"}


class HoldError(ValueError):
    """A source, capability, or provenance boundary is not established."""


@dataclass(frozen=True)
class Pointer:
    ref: str
    sha: str
    source: str = "git-remote"
    status: str = "PENCIL_SOURCE_POINTER_NOT_ADMITTED"

    def as_dict(self):
        return vars(self)


def valid_ref(name):
    return (isinstance(name, str) and bool(REF.fullmatch(name))
            and not name.endswith(".lock") and not name.startswith(".")
            and not any(part.startswith(".") for part in name.split("/")))


def _git(repo, *args, max_bytes=2000000):
    try:
        proc = subprocess.run(
            ["git", "-C", str(repo), *args],
            capture_output=True, timeout=40, check=False
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise HoldError("Git read unavailable; HOLD") from exc
    if proc.returncode != 0 or len(proc.stdout) > max_bytes:
        raise HoldError("Git source unavailable or too large; HOLD")
    return proc.stdout


def discover(repo="."):
    """Enumerate ALL remote heads, including unmerged research branches.

    Source pointers are not evidence of functionality. Main is retained as a
    comparison source; no branch is silently preferred or executed.
    """
    raw = _git(repo, "ls-remote", "--heads", "origin", max_bytes=8_000_000)
    out = []
    seen = set()
    for line in raw.decode("utf-8").splitlines():
        sha, sep, full = line.partition("\t")
        if sep != "\t" or not full.startswith("refs/heads/"):
            raise HoldError("Malformed remote reference; HOLD")
        ref = full[len("refs/heads/"):]
        if not valid_ref(ref) or not SHA.fullmatch(sha) or ref in seen:
            raise HoldError("Unsafe or duplicate remote reference; HOLD")
        seen.add(ref)
        out.append(Pointer(ref, sha))
    if not out or not any(p.ref == "main" for p in out):
        raise HoldError("Incomplete remote enumeration (missing main); HOLD")
    return sorted(out, key=lambda p: p.ref)


def from_census(data):
    """Read the repo's existing branch-census artifact as an offline snapshot.

    It is never treated as fresh or complete and cannot authorize a fetch.
    """
    if data.get("schema") != "motif.public-branch-census.v1":
        raise HoldError("Unknown census schema; HOLD")
    if data.get("repository") != "the-static-collective/MOTIF" or not data.get("all_pages_checked"):
        raise HoldError("Untrusted/incomplete census; HOLD")
    rows = data.get("passports")
    if not isinstance(rows, list) or len(rows) != data.get("source_only_cartridges"):
        raise HoldError("Census count mismatch; HOLD")
    out = []
    seen = set()
    for row in rows:
        ref, sha = row.get("ref"), row.get("commit")
        if not valid_ref(ref) or not isinstance(sha, str) or not SHA.fullmatch(sha) or ref in seen:
            raise HoldError("Invalid census pointer; HOLD")
        if row.get("executable") is not False or row.get("authority") != "NONE":
            raise HoldError("Census attempted to grant authority; HOLD")
        seen.add(ref)
        out.append(Pointer(ref, sha, "dated-public-census"))
    return sorted(out, key=lambda p: p.ref)


def lead_score(query, pointer):
    """Lexical triage only; names don't establish capabilities."""
    tokens = set(re.findall(r"[a-z0-9]+", query.lower()))
    name_tokens = set(re.findall(r"[a-z0-9]+", pointer.ref.lower()))
    return len(tokens & name_tokens)


def suggest(query, pointers, limit=12):
    if not query.strip():
        raise HoldError("A question is required to select a source lead")
    matches = [(lead_score(query, p), p) for p in pointers if p.ref != "main"]
    matches = [(s, p) for s, p in matches if s > 0]
    return [dict(p.as_dict(), lexical_score=s,
                 finding="PENCIL_LEAD_NOT_INSPECTED") for s, p in
            sorted(matches, key=lambda x: (-x[0], x[1].ref))[:limit]]


def inspect_json(repo, pointer, path):
    """Load an original branch's JSON by immutable commit without merging it.

    An exact named head is fetched into FETCH_HEAD. Changed heads cause HOLD,
    rather than silently switching a method in the middle of a decision.
    """
    if not isinstance(pointer, Pointer) or pointer.source != "git-remote":
        raise HoldError("Only live observed remote refs can be fetched")
    if not valid_ref(pointer.ref) or not SHA.fullmatch(pointer.sha):
        raise HoldError("Invalid ref pin")
    if not isinstance(path, str) or not PATH.fullmatch(path) or ".." in path or path.startswith("/"):
        raise HoldError("Only bounded relative JSON files may be inspected")
    # Fetch data, not code execution. No checkout or branch merge.
    _git(repo, "fetch", "--no-tags", "--depth=1", "origin",
         "refs/heads/" + pointer.ref, max_bytes=10000)
    actual = _git(repo, "rev-parse", "FETCH_HEAD").decode().strip()
    if actual != pointer.sha:
        raise HoldError("Branch moved after discovery; re-observe before use")
    raw = _git(repo, "show", pointer.sha + ":" + path,
               max_bytes=MAX_JSON_BYTES)
    if len(raw) > MAX_JSON_BYTES:
        raise HoldError("Oversized candidate")
    try:
        data = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise HoldError("Candidate is not UTF-8 JSON") from exc
    return {
        "pointer": pointer.as_dict(),
        "path": path,
        "blob_sha256": hashlib.sha256(raw).hexdigest(),
        "payload": data,
        "execution": "NONE",
        "admission": "NONE",
        "disposition": "HELD_SOURCE_DATA_ONLY",
    }


def passport_lenses(inspection):
    """Map a known nonmerged *data* contract into limited reasoning affordances.

    This is real branch-sourced influence on the reasoning plan, NOT execution
    of the branch's JS or Python program and NOT cross-repository authority.
    """
    payload = inspection["payload"]
    if not isinstance(payload, dict) or payload.get("schema") not in ALLOWED_SCHEMAS:
        raise HoldError("Candidate schema not recognized")
    if payload.get("owner") != "the-static-collective/MOTIF":
        raise HoldError("Wrong source owner")
    source = payload.get("source", {})
    exchange = payload.get("exchange", {})
    if (not isinstance(source, dict) or source.get("deployed") is not False
            or source.get("realHumanData") is not False
            or not isinstance(exchange, dict)
            or exchange.get("status") != "PROPOSAL_ONLY"):
        raise HoldError("Candidate asserts runtime, personal data or authority")
    caps = payload.get("capabilities")
    if not isinstance(caps, list) or not (0 < len(caps) <= 3):
        raise HoldError("Invalid candidate capabilities")
    ids = [cap.get("id") for cap in caps if isinstance(cap, dict)]
    if len(ids) != len(caps) or len(set(ids)) != len(ids) or not set(ids) <= ALLOWED_CAPABILITIES:
        raise HoldError("Unknown or duplicated capability")
    gate = payload.get("gate", {})
    if (not isinstance(gate, dict) or gate.get("disposition") != "HOLD_FOR_OWNER_REVIEW"
            or gate.get("autoApproval") is not False):
        raise HoldError("Missing owner HOLD")
    return {
        "source": inspection["pointer"],
        "blob_sha256": inspection["blob_sha256"],
        "capabilities": ids,
        "admission": "NONE",
        "execution": "NONE",
        "disposition": "HELD_PLANNING_LENSES",
    }


def merge_verdict(evidence):
    """MOTIF makes an explicit provisional judgment; never performs a merge.

    A passing internal test alone cannot warrant merging; classical comparisons,
    regressions and owner review must be inspectable.
    """
    required = ("pinned_source", "independent_tests", "strong_baseline_compared",
                "no_known_regressions", "owner_review")
    ready = all(evidence.get(k) is True for k in required)
    wins = evidence.get("measured_transfer_gain")
    if ready and isinstance(wins, (float, int)) and not isinstance(wins, bool) and wins > 0:
        result = "RECOMMEND_MERGE_REVIEW"
    else:
        result = "KEEP_UNMERGED_USE_AS_HELD_SOURCE"
    return {"verdict": result, "missing_gates": [k for k in required if evidence.get(k) is not True],
            "automatic_merge": False, "source_executed": False,
            "human_merge_authority": "REQUIRED"}
