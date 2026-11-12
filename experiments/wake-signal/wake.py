#!/usr/bin/env python3
"""WAKE SIGNAL 001: local, voluntary invitation experiment (standard library)."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import random
import re
import sys

ARMS = ("small", "creative", "autonomous")
NEXT = {
    "NONE": ("offered", "opted_out"),
    "OFFERED": ("replied", "declined", "opted_out"),
    "REPLIED": ("action", "declined", "opted_out"),
    "ACTION": ("novel_action", "opted_out"),
    "NOVEL_ACTION": ("opted_out",),
    "DECLINED": (),
    "OPTED_OUT": (),
}
STATUS = {
    "offered": "OFFERED", "replied": "REPLIED",
    "action": "ACTION", "novel_action": "NOVEL_ACTION",
    "declined": "DECLINED", "opted_out": "OPTED_OUT",
}
RECEIPT = re.compile(r"^[A-Za-z0-9_.-]{1,64}$")
MAX_COUNT = 1000


class Hold(ValueError):
    """An attempted crossing lacks the necessary evidence or permission."""


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(obj):
    return hashlib.sha256(canonical(obj).encode("utf-8")).hexdigest()


def make_plan(title, context, actions, *, count=100, seed=1, verified=False):
    if not (1 <= count <= MAX_COUNT):
        raise Hold("count must be between 1 and 1000")
    if not isinstance(seed, int):
        raise Hold("seed must be an integer")
    parts = [title, context] + [actions.get(arm) for arm in ARMS]
    if any(not isinstance(v, str) or not v.strip() or len(v) > 500
           for v in parts):
        raise Hold("title, context and all three actions must be nonempty (<=500 chars)")
    arms = [ARMS[i % 3] for i in range(count)]
    random.Random(seed).shuffle(arms)
    spec = {
        "version": "WAKE-001", "title": title.strip(),
        "context": context.strip(),
        "actions": {arm: actions[arm].strip() for arm in ARMS},
        "count": count, "seed": seed,
        "verified_opportunity": bool(verified),
    }
    study_id = digest(spec)[:20]
    wording = {
        "small": "Could you help with one small thing? ",
        "creative": "Have you got an idea we have not considered? ",
        "autonomous": "Would you like to propose and own one bounded piece? ",
    }
    assignments = []
    for index, arm in enumerate(arms, 1):
        message = (
            f"{title.strip()}\n{context.strip()}\n\n"
            f"{wording[arm]}{spec['actions'][arm]}\n\n"
            "You're free to decline or ignore this. No follow-up without permission. "
            "Nothing is committed until you choose."
        )
        assignments.append({"slot": f"P{index:03d}", "arm": arm, "message": message})
    return {"study_id": study_id, "spec": spec, "assignments": assignments}


def read_plan(path):
    plan = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(plan, dict) or "spec" not in plan:
        raise Hold("invalid plan")
    spec = plan["spec"]
    expected = make_plan(
        spec["title"], spec["context"], spec["actions"],
        count=spec["count"], seed=spec["seed"],
        verified=spec["verified_opportunity"]
    )
    if plan != expected:
        raise Hold("plan is incomplete or modified; regenerate and use a fresh ledger")
    return expected


def read_events(path):
    target = Path(path)
    if not target.exists():
        return []
    if target.stat().st_size > 3_000_000:
        raise Hold("event log exceeds 3 MB")
    rows = []
    for line in target.read_text(encoding="utf-8").splitlines():
        try:
            record = json.loads(line)
        except (ValueError, TypeError) as exc:
            raise Hold("event log is truncated or malformed") from exc
        rows.append(record)
    return rows


def replay(plan, rows):
    slots = {item["slot"] for item in plan["assignments"]}
    states = {slot: "NONE" for slot in slots}
    seen = {slot: set() for slot in slots}
    for row in rows:
        if not isinstance(row, dict) or set(row) != {
                "study_id", "slot", "event", "time_utc",
                "consent_confirmed", "attested", "receipt"}:
            raise Hold("event record schema mismatch")
        slot = row["slot"]
        event = row["event"]
        if row["study_id"] != plan["study_id"] or slot not in slots:
            raise Hold("event belongs to another study or unknown slot")
        if event not in STATUS or event not in NEXT[states[slot]]:
            raise Hold(f"invalid transition for {slot}: {states[slot]} -> {event}")
        if not isinstance(row["time_utc"], str) or not row["time_utc"]:
            raise Hold("event timestamp missing")
        if not isinstance(row["consent_confirmed"], bool) or not isinstance(row["attested"], bool):
            raise Hold("consent/attestation must be boolean")
        if event == "offered":
            if not plan["spec"]["verified_opportunity"]:
                raise Hold("draft opportunity cannot be recorded as offered")
            if not row["consent_confirmed"]:
                raise Hold("offering requires recipient contact permission")
        elif row["consent_confirmed"]:
            raise Hold("contact permission applies only to offered event")
        if event in ("action", "novel_action"):
            if not row["attested"] or not isinstance(row["receipt"], str) or not RECEIPT.fullmatch(row["receipt"]):
                raise Hold("action requires operator attestation and nonpersonal receipt ID")
        elif row["attested"] or row["receipt"] is not None:
            raise Hold("unverified event cannot carry an action receipt")
        seen[slot].add(event)
        states[slot] = STATUS[event]
    return states, seen


def record(plan_path, event_path, slot, event, *, consent=False, attested=False, receipt=None):
    plan = read_plan(plan_path)
    rows = read_events(event_path)
    # Recheck every historical event, rather than trusting an aggregate counter.
    replay(plan, rows)
    row = {
        "study_id": plan["study_id"], "slot": slot, "event": event,
        "time_utc": datetime.now(timezone.utc).isoformat(),
        "consent_confirmed": bool(consent), "attested": bool(attested),
        "receipt": receipt,
    }
    replay(plan, rows + [row])  # Validate before writing anything.
    path = Path(event_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    # Local-only single-operator log; NOT a transaction-safe multiwriter store.
    with path.open("a", encoding="utf-8") as f:
        f.write(canonical(row) + "\n")
        f.flush()
    return row


def report(plan, rows):
    _, seen = replay(plan, rows)
    by_slot = {entry["slot"]: entry for entry in plan["assignments"]}
    results = {}
    for arm in ARMS:
        slots = [slot for slot, entry in by_slot.items() if entry["arm"] == arm]
        def n(event):
            return sum(event in seen[slot] for slot in slots)
        assigned, offered, replied = len(slots), n("offered"), n("replied")
        actions, novel = n("action"), n("novel_action")
        results[arm] = {
            "assigned": assigned, "offered": offered, "replied": replied,
            "declined": n("declined"), "opted_out": n("opted_out"),
            "operator_attested_actions": actions,
            "operator_attested_unplanned_actions": novel,
            "action_per_offered_descriptive": round(actions / offered, 4) if offered else None,
        }
    return {
        "study_id": plan["study_id"], "protocol": "WAKE-001",
        "results": results,
        "offerings_complete": all(r["assigned"] == r["offered"] for r in results.values()),
        "inference": (
            "No causal winner established. Only operator-attested outcomes, "
            "not proof of personal traits or awareness. Missing replies are unknown."
        ),
        "external_delivery": "NOT IMPLEMENTED",
    }


def cli(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("plan", help="Create randomized local draft; never sends anything")
    for name in ("title", "context", "small", "creative", "autonomous", "out"):
        p.add_argument("--" + name, required=True)
    p.add_argument("--count", type=int, default=100)
    p.add_argument("--seed", type=int, default=1)
    p.add_argument("--verified-opportunity", action="store_true",
                   help="Operator has independently confirmed opportunity exists")
    p = sub.add_parser("record", help="Manually append one consent/evidence-gated event")
    for name in ("plan", "events", "slot"):
        p.add_argument("--" + name, required=True)
    p.add_argument("--event", choices=list(STATUS), required=True)
    p.add_argument("--consent-confirmed", action="store_true",
                   help="Human verified recipient permitted this invitation")
    p.add_argument("--attested", action="store_true",
                   help="Operator personally confirms action and receipt")
    p.add_argument("--receipt", help="Nonpersonal evidence reference, not a person's name")
    p = sub.add_parser("report", help="Summarize arms; never score people")
    p.add_argument("--plan", required=True)
    p.add_argument("--events", required=True)
    args = parser.parse_args(argv)
    try:
        if args.cmd == "plan":
            plan = make_plan(args.title, args.context,
                {arm: getattr(args, arm) for arm in ARMS},
                count=args.count, seed=args.seed,
                verified=args.verified_opportunity)
            path = Path(args.out)
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("x", encoding="utf-8") as f:
                f.write(json.dumps(plan, indent=2, ensure_ascii=False) + "\n")
            print(json.dumps({
                "study_id": plan["study_id"], "draft_only": not args.verified_opportunity,
                "assigned": dict(Counter(x["arm"] for x in plan["assignments"])),
                "sample": plan["assignments"][:3],
                "automatic_delivery": False
            }, indent=2))
        elif args.cmd == "record":
            print(json.dumps(record(args.plan, args.events, args.slot, args.event,
                  consent=args.consent_confirmed, attested=args.attested,
                  receipt=args.receipt), indent=2))
        elif args.cmd == "report":
            print(json.dumps(report(read_plan(args.plan), read_events(args.events)), indent=2))
    except (Hold, FileExistsError, FileNotFoundError, KeyError, TypeError, ValueError) as exc:
        parser.exit(2, "HOLD: " + str(exc) + "\n")


if __name__ == "__main__":
    cli()
