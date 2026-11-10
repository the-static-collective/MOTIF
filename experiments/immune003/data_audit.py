"""IMMUNE-003Q: audit the *judge*, not only the reasoner.

A public answer key can be internally unverifiable from the public source.
Before citing model error rates as truth, record whether the monetary gold
value is literally visible. This checks a necessary condition for a simple
email-extraction task; it does not certify the label's semantic correctness.

All labels stay in the evaluator. No model prompt may receive the audit.
"""
from __future__ import annotations
from collections import Counter
from dataclasses import asdict, dataclass
from hashlib import sha256
import json

from corpus import _fetch
from epistemic import money_values


@dataclass(frozen=True)
class Audit:
    status: str
    source_sha256: str
    gold_amount_count: int
    source_amount_count: int
    semantic_label_adjudicated: bool = False


def audit_label(ideal: str, source: str) -> Audit:
    if type(ideal) is not str or type(source) is not str:
        return Audit("INVALID_SOURCE_OR_LABEL", "", 0, 0)
    digest = sha256(source.encode()).hexdigest()
    amounts = money_values(source)
    if ideal.strip().lower() == "unknown":
        return Audit("UNKNOWN_ABSENCE_NOT_VERIFIED", digest, 0, len(amounts))
    gold = money_values(ideal)
    if not gold:
        return Audit("UNSUPPORTED_LABEL_GRAMMAR", digest, 0, len(amounts))
    if gold <= amounts:
        return Audit("LITERAL_GOLD_AMOUNT_PRESENT_RELATION_UNVERIFIED",
                     digest, len(gold), len(amounts))
    return Audit("GOLD_AMOUNT_NOT_LITERAL_IN_SOURCE",
                 digest, len(gold), len(amounts))


def report(rows: tuple[dict, ...]) -> dict:
    count = Counter()
    exceptions = []
    missing = 0
    seen_keys = set()
    duplicate_row_count = 0
    for idx, row in enumerate(rows):
        if type(row) is not dict or any(type(row.get(k)) is not str
                                       or not row[k]
                                       for k in ("context", "question", "ideal")):
            missing += 1
            continue
        digest = sha256(json.dumps(row,sort_keys=True).encode()).hexdigest()
        if digest in seen_keys:
            duplicate_row_count += 1
        seen_keys.add(digest)
        audit = audit_label(row["ideal"], row["context"])
        count[audit.status] += 1
        if audit.status == "GOLD_AMOUNT_NOT_LITERAL_IN_SOURCE":
            exceptions.append({
                "row_index": idx,
                "gold_label": row["ideal"],
                "source_sha256": audit.source_sha256,
                "risk": "answer key not directly checkable against literal amount in input",
            })
    return {
        "dataset": "BIPIA public EmailQA test.jsonl",
        "row_grain": "original question, source email, supplied ideal",
        "total_rows": len(rows),
        "complete_rows": len(rows) - missing,
        "missing_rows": missing,
        "duplicate_exact_rows": duplicate_row_count,
        "status_counts": dict(sorted(count.items())),
        "potential_annotation_or_context_mismatch": exceptions,
        "source_disagreement_is_not_proof_gold_wrong": True,
        "not_a_semantic_ground_truth_adjudication": True,
    }


def audit_pinned_public_source() -> dict:
    records = tuple(json.loads(line)
                    for line in _fetch("email/test.jsonl").decode().splitlines()
                    if line.strip())
    return report(records)


if __name__ == "__main__":
    print(json.dumps(audit_pinned_public_source(), indent=2, sort_keys=True))
