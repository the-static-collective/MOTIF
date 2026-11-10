"""IMMUNE-003 independent-origin public BIPIA benchmark ingress.

Read original externally authored Microsoft BIPIA *test* material at an exact
Git commit. Data are NEVER executed; no personal account or connector data.
Task selection and appended attack placement are MOTIF-authored and therefore
this is BIPIA-derived, NOT an official BIPIA benchmark score.
"""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha1, sha256
from urllib.request import Request, urlopen
import json

COMMIT = "a004b69ec0dd446e0afd461d98cb5e96e120a5d0"
ROOT = "https://raw.githubusercontent.com/microsoft/BIPIA/" + COMMIT + "/benchmark/"
MAX_BYTES = 160_000
# GitHub's Git-blob identifiers independently pin exact third-party file
# bytes in addition to the immutable commit path. Hash identities authenticate
# file identity relative to the pinned commit, NOT truth of its annotations.
EXPECTED_GIT_BLOBS = {
    "email/test.jsonl": "ad8f5aeb3f7ab665fe9d3efdb345476ad4338e20",
    "text_attack_test.json": "259e58a7aaf696ecddbf664022c0f254318b0a05",
}


def git_blob_sha1(raw: bytes) -> str:
    return sha1(b"blob " + str(len(raw)).encode() + b"\\0" + raw).hexdigest()
# Predeclared before the first live-model run; never tune on the test labels.
ATTACK_PAIRS = (
    (3, "Base Encoding", 0),
    (4, "Reverse Text", 0),
    (5, "Language Translation", 0),
    (6, "Information Dissemination", 0),
    (7, "Marketing & Advertising", 0),
    (8, "Substitution Ciphers", 1),
    (9, "Scams & Fraud", 0),
    (14, "Sentiment Analysis", 1),
    (16, "Conversational Agent", 0),
    (17, "Entertainment", 0),
    (34, "Research Assistance", 0),
    (44, "Base Encoding", 2),
)
CLEAN_INDICES = (0, 3, 5, 8, 16, 44)


@dataclass(frozen=True)
class Case:
    key: str
    source: str
    question: str
    ideal: str
    attack: str
    attack_category: str
    source_hash: str


def _hash(value: bytes) -> str:
    return sha256(value).hexdigest()


def _fetch(path: str) -> bytes:
    if path not in ("email/test.jsonl", "text_attack_test.json"):
        raise ValueError("Unregistered external read")
    with urlopen(Request(ROOT + path, headers={"User-Agent": "MOTIF-IMMUNE-003"}),
                 timeout=40) as stream:
        raw = stream.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError("External source size exceeds declared read budget")
    if git_blob_sha1(raw) != EXPECTED_GIT_BLOBS[path]:
        raise ValueError("External content differs from pinned original Git blob")
    return raw


def prepare(email_bytes: bytes, attack_bytes: bytes) -> tuple[tuple[Case, ...], dict]:
    """No trust in downloaded data except for exact source and structural format."""
    if len(email_bytes) > MAX_BYTES or len(attack_bytes) > MAX_BYTES:
        raise ValueError("Oversized source")
    emails = [json.loads(line) for line in email_bytes.decode().splitlines()
              if line.strip()]
    attacks = json.loads(attack_bytes.decode())
    if (len(emails) < 50 or not isinstance(attacks, dict)
            or any(not isinstance(e, dict) or
                   set(("context", "question", "ideal")) - set(e)
                   for e in emails)):
        raise ValueError("Unexpected externally authored benchmark shape")
    cases = []
    def include(idx: int, category: str, entry: int, injection: str):
        row = emails[idx]
        if (not all(type(row[k]) is str and row[k] for k in
                    ("context", "question", "ideal"))
                or type(injection) is not str
                or len(injection) > 2000 or len(row["context"]) > 6000):
            raise ValueError("Invalid external corpus record")
        key = f"email-{idx:02d}-" + (f"{category}-{entry}" if category else "clean")
        cases.append(Case(key, row["context"], row["question"], row["ideal"],
                          injection, category or "CLEAN",
                          _hash(row["context"].encode())))
    for idx, category, entry in ATTACK_PAIRS:
        if category not in attacks or entry >= len(attacks[category]):
            raise ValueError("Frozen external attack index unavailable")
        include(idx, category, entry, attacks[category][entry])
    # Every attacked email has an exact paired no-injection control to measure
    # change in task correctness. These pairs were fixed before live calls.
    for idx, _, _ in ATTACK_PAIRS:
        include(idx, "", 0, "")
    # Additional ordinary controls with no adversarial suffix.
    for idx in CLEAN_INDICES:
        if idx not in {i for i, _, _ in ATTACK_PAIRS}:
            include(idx, "", 0, "")
    keys = [c.key for c in cases]
    if len(keys) != len(set(keys)):
        raise ValueError("Duplicate synthetic pairing")
    metadata = {
        "third_party_corpus": "Microsoft BIPIA",
        "third_party_commit": COMMIT,
        "third_party_email_test_sha256": _hash(email_bytes),
        "third_party_text_attacks_sha256": _hash(attack_bytes),
        "selection_authored_by": "MOTIF-IMMUNE-003",
        "attack_placement": "appended as untrusted external note",
        "original_bipia_generation": False,
        "official_bipia_score": False,
        "attack_count": len(ATTACK_PAIRS),
        "clean_count": len(cases) - len(ATTACK_PAIRS),
        "case_keys": keys,
    }
    return tuple(cases), metadata


def fetch_test_cases() -> tuple[tuple[Case, ...], dict]:
    return prepare(_fetch("email/test.jsonl"), _fetch("text_attack_test.json"))
