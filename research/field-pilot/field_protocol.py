"""FIELD-001: cautious real-world self-report intake and follow-up.

This is intentionally NOT the BRIDGE-001 simulation. Cards describe what a
human operator says was reported. A match is a review candidate; never an
authenticated agreement, inventory reservation, or actual encounter. No
network access or side effects. Deterministic standard-library Python.
"""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
import json
import re
from typing import Any

SCHEMA = "motif.field-log/v0"
ID = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_.-]{0,79}$")
TAG = re.compile(r"^[a-z0-9][a-z0-9 _-]{0,39}$")
ORIGINS = ("owner_self_report", "operator_heard_owner", "third_party_unverified")
KINDS = ("offer", "need")
EVENTS = (
    "provider_yes_reported", "requester_yes_reported",
    "provider_no_reported", "requester_no_reported",
    "handoff_reported", "benefit_reported", "no_benefit_reported",
    "unknown_reported", "card_withdrawn",
)


class FieldError(ValueError):
    pass


def _utc(value: str) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise FieldError("timestamps must be ISO UTC with Z")
    try:
        date = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise FieldError("invalid timestamp") from exc
    if date.tzinfo is None or date.utcoffset().total_seconds() != 0:
        raise FieldError("timestamp must be UTC")
    return date


def _text(value: object, name: str, maximum: int, *, empty: bool = False) -> str:
    if not isinstance(value, str) or len(value) > maximum:
        raise FieldError(f"{name} must be text up to {maximum} characters")
    if not empty and not value.strip():
        raise FieldError(f"{name} must not be blank")
    return value


def _keys(value: object, keys: set[str], name: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != keys:
        raise FieldError(f"{name} has missing or unexpected fields")
    return value


def _identifier(value: object, name: str) -> str:
    if not isinstance(value, str) or not ID.fullmatch(value):
        raise FieldError(f"invalid {name}")
    return value


def validate(log: object) -> dict[str, Any]:
    data = _keys(log, {"schema", "cards", "events"}, "field log")
    if data["schema"] != SCHEMA:
        raise FieldError("unsupported schema")
    if (not isinstance(data["cards"], list) or len(data["cards"]) > 300
            or not isinstance(data["events"], list)
            or len(data["events"]) > 2000):
        raise FieldError("wrong card/event list type or too many records")

    card_ids: set[str] = set()
    cards: dict[str, dict[str, Any]] = {}
    for card in data["cards"]:
        c = _keys(card, {
            "id", "kind", "alias", "topic", "area", "note", "created_at",
            "expires_at", "origin", "share_ok",
        }, "card")
        ident = _identifier(c["id"], "card ID")
        if ident in card_ids:
            raise FieldError("duplicate card ID")
        card_ids.add(ident)
        if c["kind"] not in KINDS:
            raise FieldError("invalid card kind")
        _text(c["alias"], "alias", 60)
        for name in ("topic", "area"):
            if not isinstance(c[name], str) or not TAG.fullmatch(c[name]):
                raise FieldError(f"{name} must be a short lowercase label")
        _text(c["note"], "note", 360, empty=True)
        if c["origin"] not in ORIGINS or type(c["share_ok"]) is not bool:
            raise FieldError("invalid reporting origin or share flag")
        if c["share_ok"] and c["origin"] == "third_party_unverified":
            raise FieldError("third-party report cannot establish sharing permission")
        if _utc(c["expires_at"]) <= _utc(c["created_at"]):
            raise FieldError("expiry must be after creation")
        cards[ident] = c

    match_ids = {
        match_id(a, b)
        for a in data["cards"] for b in data["cards"]
        if a["kind"] == "offer" and b["kind"] == "need"
        and _pair_compatible(a, b)
    }
    events_seen: set[str] = set()
    for event in data["events"]:
        e = _keys(event, {
            "id", "subject", "kind", "reporter", "source",
            "occurred_at", "recorded_at", "note",
        }, "event")
        eid = _identifier(e["id"], "event ID")
        if eid in events_seen:
            raise FieldError("duplicate event ID")
        events_seen.add(eid)
        if e["kind"] not in EVENTS:
            raise FieldError("invalid event kind")
        if (e["source"] not in ORIGINS
                or not isinstance(e["reporter"], str)
                or not e["reporter"].strip() or len(e["reporter"]) > 60):
            raise FieldError("event requires a bounded reporting origin and alias")
        _text(e["note"], "event note", 360, empty=True)
        if _utc(e["occurred_at"]) > _utc(e["recorded_at"]):
            raise FieldError("reported occurrence cannot follow recording")
        if e["kind"] == "card_withdrawn":
            if e["subject"] not in cards:
                raise FieldError("withdrawal refers to unknown card")
        elif e["subject"] not in match_ids:
            raise FieldError("event refers to unsupported pair")
    return data


def _pair_compatible(a: dict[str, Any], b: dict[str, Any]) -> bool:
    return (a["topic"] == b["topic"]
            and a["area"] == b["area"]
            and a["alias"] != b["alias"]
            and a["share_ok"] and b["share_ok"]
            and a["origin"] != "third_party_unverified"
            and b["origin"] != "third_party_unverified")


def match_id(offer: dict[str, Any], need: dict[str, Any]) -> str:
    return "pair:" + offer["id"] + ":" + need["id"]


def candidate_pairs(log: object, now: str) -> list[dict[str, Any]]:
    data = validate(log)
    time = _utc(now)
    withdrawn = {e["subject"] for e in data["events"]
                 if e["kind"] == "card_withdrawn"
                 and _utc(e["occurred_at"]) <= time}
    offers = [c for c in data["cards"] if c["kind"] == "offer"
              and c["id"] not in withdrawn
              and _utc(c["created_at"]) <= time < _utc(c["expires_at"])]
    needs = [c for c in data["cards"] if c["kind"] == "need"
             and c["id"] not in withdrawn
             and _utc(c["created_at"]) <= time < _utc(c["expires_at"])]
    rows = []
    for offer in offers:
        for need in needs:
            if not _pair_compatible(offer, need):
                continue
            mid = match_id(offer, need)
            history = [e for e in data["events"]
                       if e["subject"] == mid and _utc(e["occurred_at"]) <= time]
            types = {e["kind"] for e in history
                     if e["source"] != "third_party_unverified"
                     or e["kind"] not in ("provider_yes_reported",
                                         "requester_yes_reported")}
            if "provider_no_reported" in types or "requester_no_reported" in types:
                disposition = "CLOSED_DECLINED_REPORTED"
            elif "benefit_reported" in types and "no_benefit_reported" in types:
                disposition = "CONFLICTING_OUTCOME_REPORTS"
            elif "benefit_reported" in types:
                disposition = "BENEFIT_REPORTED_NOT_CAUSAL"
            elif "no_benefit_reported" in types:
                disposition = "NO_BENEFIT_REPORTED"
            elif "handoff_reported" in types:
                disposition = "HANDOFF_REPORTED_NOT_VERIFIED"
            elif {"provider_yes_reported", "requester_yes_reported"} <= types:
                disposition = "DUAL_YES_REPORTED_NOT_VERIFIED"
            else:
                disposition = "HOLD_CONFIRM_DIRECTLY"
            rows.append({
                "id": mid, "offer_id": offer["id"], "need_id": need["id"],
                "offer_alias": offer["alias"], "need_alias": need["alias"],
                "topic": offer["topic"], "area": offer["area"],
                "expires_at": min(offer["expires_at"], need["expires_at"]),
                "disposition": disposition,
                "events": len(history),
                "boundary": "candidate only; direct agreement and safety unverified",
            })
    return sorted(rows, key=lambda p: (p["expires_at"], p["id"]))


def summarize(log: object, now: str) -> dict[str, Any]:
    data = validate(log)
    rows = candidate_pairs(data, now)
    types = Counter(e["kind"] for e in data["events"])
    outcomes = {
        "benefit_reports": types["benefit_reported"],
        "no_benefit_reports": types["no_benefit_reported"],
        "handoff_reports": types["handoff_reported"],
        "declines_reported": types["provider_no_reported"]
                             + types["requester_no_reported"],
        "unknown_reports": types["unknown_reported"],
    }
    core = json.dumps(data, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"))
    return {
        "schema": "motif.field-summary/v0",
        "as_of": now,
        "source": "operator-entered reports; origin and timing unverified",
        "eligible_pairs": len(rows),
        "active_candidate_pairs": sum(
            p["disposition"] in ("HOLD_CONFIRM_DIRECTLY",
                                 "DUAL_YES_REPORTED_NOT_VERIFIED")
            for p in rows
        ),
        "dispositions": dict(sorted(Counter(p["disposition"]
                                            for p in rows).items())),
        "reported_outcomes": outcomes,
        "unmatched_is_not_no_demand": True,
        "causal_effect_identified": False,
        "authorship_verified": False,
        "contains_demo_ids": any(c["id"].startswith("demo-") for c in data["cards"]),
        "log_sha256_unsigned": sha256(core.encode("utf-8")).hexdigest(),
        "pairs": rows,
    }


def example() -> dict[str, Any]:
    """Only a marked synthetic example. Never automatically preload as reality."""
    a = "2026-11-04T15:00:00Z"
    b = "2026-11-05T15:00:00Z"
    return {"schema": SCHEMA, "cards": [
        {"id":"demo-offer", "kind":"offer", "alias":"Demo A",
         "topic":"cooler", "area":"fictional-town", "note":"Spare insulated box",
         "created_at":a,"expires_at":b,
         "origin":"owner_self_report","share_ok":True},
        {"id":"demo-need", "kind":"need", "alias":"Demo B",
         "topic":"cooler", "area":"fictional-town",
         "note":"Need a box for a short trip",
         "created_at":a,"expires_at":b,
         "origin":"owner_self_report","share_ok":True},
    ], "events":[]}


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("log", nargs="?", help="local exported log.json")
    parser.add_argument("--as-of", required=False,
                        default=datetime.now(timezone.utc).isoformat(
                            timespec="seconds").replace("+00:00", "Z"))
    args = parser.parse_args()
    if args.log:
        with open(args.log, encoding="utf-8") as f:
            log = json.load(f)
    else:
        log = example()
    print(json.dumps(summarize(log, args.as_of), indent=2))
