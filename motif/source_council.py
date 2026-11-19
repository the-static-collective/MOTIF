"""MOTIF SOURCE COUNCIL 002: inspect unmerged branch evidence before method selection.

This council DOES NOT execute branch code. It cannot approve method admission or
merge. It triages *readable source claims*, with source-hash provenance, against
a user-supplied question. The competing "baseline" is branch-name-only retrieval.
"""
from __future__ import annotations

import argparse
import json
import re

from .branch_garden import HoldError, discover, suggest
from .branch_source import observe, list_paths, read_text

MAX_BRANCHES = 6
MAX_DOCS = 4
DOC_NAMES = ("README.md", "DESIGN.md", "VISION.md", "PREREGISTRATION.md")


def tokens(text):
    return {v for v in re.findall(r"[a-z0-9]+", text.lower()) if len(v) >= 3}


def choose_docs(paths, query):
    """Limit the time and bytes inspected, independent of document instructions."""
    terms = tokens(query)
    candidates = [p for p in paths if p.endswith(DOC_NAMES)]
    def rank(path):
        matches = len(tokens(path) & terms)
        # Experiments, not root README, are the first evidence of new work.
        local = int(path.startswith("experiments/"))
        prereg = int(path.endswith("PREREGISTRATION.md"))
        return (-matches, -local, -prereg, path)
    return sorted(candidates,key=rank)[:MAX_DOCS]


def score_docs(query, witness_docs, paths):
    """Return transparent lexical signals, never verification of code behavior."""
    terms = tokens(query)
    doc_tokens = set()
    provenance = []
    for record in witness_docs:
        doc_tokens |= tokens(record["text"])
        provenance.append({
            "path": record["path"], "sha256": record["sha256"],
            "bytes": record["bytes"], "code_executed": False,
        })
    found = sorted(doc_tokens & terms)
    has_tests = any(
        ("test_" in p or "/test" in p or p.endswith(".test.mjs"))
        and p.endswith((".py",".js",".mjs",".cjs")) for p in paths
    )
    # A test filename is a source lead, not proof a test ran or passed.
    return {
        "query_terms": sorted(terms),
        "document_terms_matched": found,
        "document_coverage": len(found)/max(1,len(terms)),
        "test_file_name_visible": has_tests,
        "tested_behavior_verified": False,
        "strong_baseline_outperformance_verified": False,
        "source_witnesses": provenance,
    }


def decide(query, branch_lead, witness_docs, paths):
    signals = score_docs(query, witness_docs, paths)
    score = signals["document_coverage"]
    result = {
        "schema": "motif.source-council/v1",
        "branch": branch_lead["ref"], "commit": branch_lead["sha"],
        "phase": "PENCIL_SOURCE_EVIDENCE",
        "claim": "SOURCE_DOCUMENT_KEYWORD_MATCH_NOT_MODEL_VERIFICATION",
        "evidence": signals,
        "recommendation": "READ_MORE_OR_RUN_REVIEWED_TEST" if score>0 and signals["test_file_name_visible"] else "HOLD_INSUFFICIENT_DOCUMENT_EVIDENCE",
        "executable": False, "automatic_merge": False,
        "ready_for_admission": False,
        "owner_review_required": True,
    }
    return result


def inspect_candidates(repo, query, budget=MAX_BRANCHES):
    """List all remote heads and inspect at most a bounded relevant shortlist."""
    if not isinstance(query,str) or not query.strip() or len(query)>180:
        raise HoldError("A short substantive question is required")
    if not isinstance(budget,int) or not 1<=budget<=MAX_BRANCHES:
        raise HoldError("Inspection budget must be 1–6 branches")
    all_heads = discover(repo)
    candidates = suggest(query, all_heads,limit=budget)
    cards = []
    for lead in candidates:
        try:
            pin = observe(repo,lead["ref"])
            if pin.sha!=lead["sha"]:
                raise HoldError("Head changed after first census")
            paths = list_paths(repo,pin)
            docs = []
            for path in choose_docs(paths,query):
                docs.append(read_text(repo,pin,path,include_text=True))
            cards.append(decide(query,lead,docs,paths))
        except HoldError as exc:
            cards.append({
                "schema":"motif.source-council/v1",
                "branch":lead["ref"],"commit":lead["sha"],
                "phase":"HOLD_UNAVAILABLE_SOURCE",
                "reason":str(exc),
                "executable":False,"automatic_merge":False,
                "owner_review_required":True
            })
    return {
        "schema":"motif.source-council-selection/v1",
        "question":query, "all_remote_heads_observed":len(all_heads),
        "shortlist_policy":"BRANCH_NAME_FIRST_THEN_SOURCE_CONTENT_LEXICAL_CHECK",
        "selection_budget":budget, "candidates":cards,
        "not_selected_not_rejected":True,
        "automatic_branch_execution":False,
        "automatic_merge":False,
        "algorithm_invention":False,
        "conclusion":"SOURCE_LEADS_ONLY_NOT_EVIDENCE_OF_STRONGER_REASONING",
    }


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo",default=".")
    parser.add_argument("--query",required=True)
    parser.add_argument("--budget",type=int,default=4)
    args=parser.parse_args(argv)
    try:
        result=inspect_candidates(args.repo,args.query,args.budget)
        print(json.dumps(result,indent=2,sort_keys=True))
        return 0
    except HoldError as exc:
        print(json.dumps({"disposition":"HOLD","reason":str(exc)}))
        return 2


if __name__=="__main__":
    raise SystemExit(main())
