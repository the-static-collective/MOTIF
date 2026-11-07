"""RING-007: bounded, source-scoped semantic inquiry before native execution.

Three possible verdicts on an UNFAMILIAR phrase:
  BLOCK: explicit or indirect transfer/effect request (no native methods)
  EXPLORE: complete match to a fixed, compositional route-question grammar
  UNCERTAIN: anything else (no native methods, preserve review question)

An EXPLORE verdict is a reviewed translation *hypothesis* into this one
synthetic task's canonical read-only inquiry, NOT general semantic knowledge.
The original source-native THOUGHT-014 will separately inspect the unmodified
text as a nonauthoritative hypothesis and the canonical limited question as
a typed input. Untrusted text never creates effects or new identifiers.
"""
from __future__ import annotations
import re
from hashlib import sha256
import json

SCHEMA="motif.ring007.typed-uncertainty-review.v1"
CANONICAL="what if these are connected"

# Unambiguous effect risk by observable text. NOT a natural-language firewall.
# Mark transfer, exposure, third-party distribution and other effect terms.
_TRANSFER=re.compile(
    r"\b(?:forward(?:ing|ed|s)?|broadcast(?:ing|ed|s)?|"
    r"leak(?:ing|ed|s)?|distribut(?:e|ed|ing|ion)|"
    r"circulat(?:e|ed|ing)|relay(?:ed|ing|s)?|"
    r"shar(?:e|ing|ed)|send|sent|post(?:ing|ed|s)?|"
    r"publish|publici[sz]e|deploy|delete|execute|merge|"
    r"email|contact|dispatch|export|upload|"
    r"transfer|reveal|disclose|give|deliver|"
    r"copy|print|announce)\b|"
    r"\bpass\b.{0,85}\balong\b|"
    r"\bmake\b.{0,85}\bpublic\b|"
    r"\blet\b.{0,85}\b(?:everyone|others|people|strangers)\b.{0,85}\bsee\b",
    flags=re.I,
)

# Full-string, bounded grammar: a question about a path through the toy graph.
# These are preauthored source-review rules, NOT learned broad English parsing.
_SUBJECT=r"(?:the|this|another|a) (?:route|path|pathway|connection|graph)"
_QUESTION_PATTERNS=(
    rf"(?:could|can|would) {_SUBJECT} (?:still work|still reach the end|remain connected|still survive|survive|stay connected)",
    rf"(?:does|will) {_SUBJECT} (?:still work|remain|survive|remain connected)",
    r"is there still a path through (?:this|the) graph",
    r"what if (?:these are connected|another path survives|the graph stays connected|"
    r"another route survives|this path survives|the connection remains)",
    r"what would disprove the connection",
)
_QUERY=tuple(re.compile(r"^"+x+r"$",flags=re.I) for x in _QUESTION_PATTERNS)
_SPACES=re.compile(r"\s+")


def normalized(text):
    if type(text) is not str or not 1<=len(text)<=320:
        raise ValueError("Bounded plain-language input required")
    if any(ord(c)<32 and c not in "\t\r\n" for c in text):
        raise ValueError("Control characters not permitted")
    return _SPACES.sub(" ",text.strip().casefold()).rstrip("?.!").strip()


def review(text):
    txt=normalized(text)
    fingerprint=sha256(text.encode("utf-8")).hexdigest()
    if _TRANSFER.search(txt):
        verdict="BLOCK"
        cause="EXPLICIT_OR_INDIRECT_EFFECT_TRANSFER_WORD"
        canonical=None
    elif any(p.fullmatch(txt) for p in _QUERY):
        verdict="EXPLORE"
        cause="FULL_MATCH_TO_SCOPED_READ_ONLY_PATH_QUERY"
        canonical=CANONICAL
    else:
        verdict="UNCERTAIN"
        cause="NO_REVIEWED_SEMANTIC_FRAME"
        canonical=None
    out={
        "schema":SCHEMA,
        "input_sha256":fingerprint,
        "verdict":verdict,
        "reason":cause,
        "canonical_readonly_query":canonical,
        "semantic_scope":"SYNTHETIC_GRAPH_S_A_T_REACHABILITY_ONLY",
        "actual_human_intent_verified":False,
        "new_source_permissions":0,
        "external_action_performed":False,
    }
    return out
