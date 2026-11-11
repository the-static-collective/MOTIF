"""Read-only source transparency audit of the U.S. House's historical funding-gap table.

This is not a trained classifier or an assessment of political actors.
"""
import argparse
import json
from datetime import date
from pathlib import Path


def summarize(data: dict) -> dict:
    if data.get("schema") != "motif/org002-historical-funding-gaps-v0":
        raise ValueError("unknown history schema")
    records = data.get("cases")
    if not isinstance(records, list) or not records:
        raise ValueError("history cases are missing")
    ids = set()
    prev = None
    for c in records:
        if not isinstance(c, dict) or not isinstance(c.get("id"), str) or c["id"] in ids:
            raise ValueError("invalid or duplicate history id")
        ids.add(c["id"])
        if c.get("scope") not in {"full", "partial"} or type(c.get("shutdown_procedures_followed")) is not bool:
            raise ValueError("unknown scope or shutdown procedure")
        if c.get("intent") != "NOT_CLASSIFIED_FROM_CHRONOLOGY":
            raise ValueError("chronology does not establish intent")
        if type(c.get("house_reported_days")) is not int or c["house_reported_days"] < 1:
            raise ValueError("invalid House-reported day count")
        first, restored = date.fromisoformat(c["funding_ended"]), date.fromisoformat(c["funding_restored"])
        if first >= restored or (prev and first < prev):
            raise ValueError("invalid or unordered dates")
        prev = first
    discrepancies = []
    for d in data.get("known_count_disagreements", []):
        if d.get("id") not in ids or d.get("resolution") != "PRESERVE_UNRESOLVED_SOURCE_DIFFERENCE":
            raise ValueError("disagreement provenance missing")
        actual = next(x for x in records if x["id"] == d["id"])
        if actual["house_reported_days"] != d.get("house_reported_days") or not d.get("source"):
            raise ValueError("disagreement House value or CRS source missing")
        if type(d.get("crs_full_days")) is not int or d["crs_full_days"] == d["house_reported_days"]:
            raise ValueError("disagreement not supported")
        discrepancies.append({"id": d["id"], "house_days": d["house_reported_days"],
                              "crs_days": d["crs_full_days"], "status": d["resolution"],
                              "crs_source": d["source"]})
    return {
        "kind": "MOTIF_ORG002_SOURCE_AUDIT",
        "source": data["source"], "source_page_date": data["source_page_date"],
        "funding_gap_rows": len(records),
        "procedures_followed_yes": sum(x["shutdown_procedures_followed"] for x in records),
        "procedures_followed_no": sum(not x["shutdown_procedures_followed"] for x in records),
        "full_rows": sum(x["scope"] == "full" for x in records),
        "partial_rows": sum(x["scope"] == "partial" for x in records),
        "intent_assessments": 0,
        "known_unresolved_count_disagreements": discrepancies,
        "warning": "Funding gap is not synonymous with operating shutdown; source day counts are not harmonized; political intent is unclassified",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", type=Path)
    a = parser.parse_args()
    print(json.dumps(summarize(json.loads(a.file.read_text(encoding="utf-8"))), indent=2, sort_keys=True))
