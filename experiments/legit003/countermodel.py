"""MOTIF LEGIT-003: construct countermodels for an unobserved target.

The code does NOT translate arbitrary natural language, discover a new law,
authenticate evidence, or know anyone's subjective experience. It constructs
the entire compatible finite family for a specifically typed observation
grammar WITHOUT the prior world-list or invented Bayesian priors of LEGIT-001.

The target and proxy are opaque symbols. The inference concerns what follows
from the *admitted* observations, not what is necessarily true in reality.
Python 3.10+ standard library. No I/O, remote services, external actions.
"""
from __future__ import annotations

from hashlib import sha256
import json
import re

SCHEMA = "motif.latent-countermodel.v1"
IDENT = re.compile(r"^[A-Za-z][A-Za-z0-9_:-]{0,79}$")
SCOPES = frozenset(("CURATED_PUBLIC_RESEARCH", "SYNTHETIC_ONLY"))
LIMIT_ROWS = 12
MAX_COUNT = 100000


class HOLD(ValueError):
    pass


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False, ensure_ascii=True)


def digest(value):
    return sha256(canonical(value).encode("utf-8")).hexdigest()


def symbol(value):
    return isinstance(value, str) and IDENT.fullmatch(value) is not None


def _strict(record, keys, label):
    if not isinstance(record, dict) or set(record) != set(keys):
        raise HOLD("Unrecognized " + label + " schema")


def _count(value):
    return type(value) is int and 0 <= value <= MAX_COUNT


def validate(case):
    _strict(case, ("schema", "id", "scope", "question", "latent_target",
                   "observed_proxy", "observations", "anchors", "sources"),
            "case")
    if case["schema"] != SCHEMA or case["scope"] not in SCOPES:
        raise HOLD("Unknown epistemic scope")
    if not symbol(case["id"]) or not symbol(case["latent_target"]) or not symbol(case["observed_proxy"]):
        raise HOLD("Invalid target or proxy identifiers")
    if case["latent_target"] == case["observed_proxy"]:
        raise HOLD("Cannot infer target from itself by aliasing an observation")
    if not isinstance(case["question"], str) or not 15 <= len(case["question"]) <= 600:
        raise HOLD("Question missing or excessive")
    if len(canonical(case).encode("utf-8")) > 45000:
        raise HOLD("Oversized evidence packet")
    receipts = case["sources"]
    if not isinstance(receipts, list) or not 1 <= len(receipts) <= 12:
        raise HOLD("Missing sources")
    source_ids = set()
    for r in receipts:
        _strict(r, ("id", "url", "provenance"), "source")
        if not symbol(r["id"]) or r["id"] in source_ids:
            raise HOLD("Duplicated source identity")
        if case["scope"] == "CURATED_PUBLIC_RESEARCH":
            if r["provenance"] != "HAND_CURATED" or not isinstance(r["url"], str) or not r["url"].startswith("https://"):
                raise HOLD("Unverified public source address")
        else:
            if r["provenance"] != "SYNTHETIC_SIMULATOR" or not isinstance(r["url"], str) or not r["url"].startswith("synthetic://"):
                raise HOLD("Unknown synthetic provenance")
        source_ids.add(r["id"])
    rows = case["observations"]
    if not isinstance(rows, list) or not 1 <= len(rows) <= LIMIT_ROWS:
        raise HOLD("Unsupported row count")
    row_ids = set()
    seen_population = set()
    for r in rows:
        _strict(r, ("group", "proxy_positive", "proxy_negative", "source_id"), "observation")
        if not symbol(r["group"]) or r["group"] in row_ids:
            raise HOLD("Duplicate or invalid group")
        if r["source_id"] not in source_ids:
            raise HOLD("Unknown source lineage")
        if not _count(r["proxy_positive"]) or not _count(r["proxy_negative"]):
            raise HOLD("Invalid observation counts")
        if r["proxy_positive"] + r["proxy_negative"] < 1:
            raise HOLD("Empty observation group")
        row_ids.add(r["group"])
        # These are disjoint *declared* groups within a source, not proof
        # that different published studies contain no overlapping patients.
        seen_population.add((r["source_id"], r["group"]))
    anchors = case["anchors"]
    if not isinstance(anchors, list) or len(anchors) > 2*len(rows):
        raise HOLD("Invalid anchor count")
    seen = set()
    for a in anchors:
        _strict(a, ("group", "proxy", "known_latent_true", "known_latent_false",
                    "origin"), "anchor")
        if case["scope"] != "SYNTHETIC_ONLY" or a["origin"] != "SIMULATOR_TRUTH":
            raise HOLD("Human-curated research has no certified subjective-experience labels")
        if a["group"] not in row_ids or a["proxy"] not in ("positive", "negative"):
            raise HOLD("Anchor references unknown observation")
        if not _count(a["known_latent_true"]) or not _count(a["known_latent_false"]):
            raise HOLD("Invalid synthetic anchor counts")
        key = (a["group"], a["proxy"])
        if key in seen:
            raise HOLD("Duplicated anchor evidence")
        seen.add(key)
        row = next(x for x in rows if x["group"] == a["group"])
        n = row["proxy_positive" if a["proxy"] == "positive" else "proxy_negative"]
        if a["known_latent_true"] + a["known_latent_false"] > n:
            raise HOLD("Inconsistent target constraints")
    return case


def _cells(case):
    anchors = {(x["group"],x["proxy"]):x for x in case["anchors"]}
    result = []
    for r in sorted(case["observations"], key=lambda x:x["group"]):
        for proxy in ("negative", "positive"):
            n = r["proxy_negative" if proxy=="negative" else "proxy_positive"]
            anchor = anchors.get((r["group"],proxy),{})
            lower = anchor.get("known_latent_true",0)
            upper = n-anchor.get("known_latent_false",0)
            result.append({"group":r["group"],"proxy":proxy,"source_id":r["source_id"],
                           "observed":n,"min_target_true":lower,"max_target_true":upper})
    return result


def _completion(cells, mode):
    if mode not in ("min","max"):
        raise ValueError("Unknown countermodel")
    return [{"group":c["group"],"proxy":c["proxy"],
             "observed":c["observed"],
             "latent_true":c["min_target_true" if mode=="min" else "max_target_true"],
             "latent_false":c["observed"]-c["min_target_true" if mode=="min" else "max_target_true"]}
            for c in cells]


def _projection_matches(cells, world):
    return all(c["group"]==w["group"] and c["proxy"]==w["proxy"] and
               c["observed"]==w["latent_true"]+w["latent_false"] and
               c["min_target_true"]<=w["latent_true"]<=c["max_target_true"]
               for c,w in zip(cells,world))


def compile_countermodels(case):
    """Produce real executable countermodels, never assumed latent probabilities."""
    validate(case)
    cells = _cells(case)
    low = _completion(cells,"min")
    high = _completion(cells,"max")
    if not _projection_matches(cells,low) or not _projection_matches(cells,high):
        raise AssertionError("Internal proof construction failed")
    negative = [c for c in cells if c["proxy"]=="negative"]
    neg_observed = sum(c["observed"] for c in negative)
    lower = sum(c["min_target_true"] for c in negative)
    upper = sum(c["max_target_true"] for c in negative)
    all_count = sum(c["observed"] for c in cells)
    all_lower = sum(c["min_target_true"] for c in cells)
    all_upper = sum(c["max_target_true"] for c in cells)
    if neg_observed==0:
        verdict = "NO_NEGATIVE_PROXY_CASES"
    elif upper==0:
        verdict = "ENTAILS_ABSENCE_ONLY_WITHIN_DECLARED_SAMPLE"
    elif lower>0:
        verdict = "COUNTEREXAMPLE_ENTAILED_IN_DECLARED_SAMPLE"
    else:
        verdict = "NOT_IDENTIFIABLE_FROM_ADMITTED_EVIDENCE"

    # The largest unanchored NEGATIVE cell is the best direct discriminator
    # for the precise implication at issue. This is a declared heuristic,
    # not expected information gain without a calibrated response model.
    eligible = sorted((c for c in negative if c["max_target_true"]>c["min_target_true"]),
                      key=lambda c:(-(c["max_target_true"]-c["min_target_true"]),
                                    c["group"]))
    if eligible:
        target = eligible[0]
        next_question = {
            "route": ("SEEK_INDEPENDENT_MEASUREMENT_VALIDATION" if
                      case["scope"]=="CURATED_PUBLIC_RESEARCH" else
                      "REQUEST_SYNTHETIC_TARGET_AUDIT"),
            "stratum": target["group"],
            "proxy": "negative",
            "unresolved_individuals": target["max_target_true"]-target["min_target_true"],
            "why": "The largest unresolved negative-proxy stratum permits opposite target assignments.",
            "issued": False,
        }
    else:
        next_question = None
    return {
        "schema":"motif.countermodel-receipt.v1",
        "case_id":case["id"],
        "scope":case["scope"],
        "source_packet_sha256":digest(case),
        "latent_target":case["latent_target"],
        "observed_proxy":case["observed_proxy"],
        "claim_tested":"PROXY_NEGATIVE_IMPLIES_TARGET_ABSENT_FOR_ADMITTED_SAMPLE",
        "verdict":verdict,
        "total_observed":all_count,
        "negative_proxy_observed":neg_observed,
        "negative_proxy_latent_true_bounds":[lower,upper],
        "all_latent_true_bounds":[all_lower,all_upper],
        "cells":cells,
        "countermodels":{
            "minimum_latent_target":low,
            "maximum_latent_target":high,
            "both_preserve_observed_counts":True,
            "both_respect_declared_anchors":True,
        },
        "next_question":next_question,
        "individual_probability_of_latent_target":None,
        "model_uncertainty_probability":None,
        "method":"FINITE_EXACT_PARTIAL_IDENTIFICATION",
        "method_learned":False,
        "language_understanding":False,
        "source_authenticated":False,
        "automated_action":False,
        "real_world_authority":False,
        "status":"RESEARCH_HOLD",
        "scientific_limit":
            "Countermodels are logical completions of admitted aggregate data, not real observed persons, calibrated posterior distributions, or proof about reality.",
    }
