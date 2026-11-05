"""Distil novel *conditional procedures* from two teacher-visible step traces.

Only a tiny, fixed guard DSL is available. Unknowns HOLD. The two independent
teacher implementations are not used by this learner.
"""
from __future__ import annotations
from itertools import combinations, permutations
import json

from language import (SCHEMA, SOURCE_REVISION, GUARDS, OPS, MAX_BYTES,
                      State, Case, HOLD, digest, execute, matches, portable,
                      transition, label)


class Distillery:
    def __init__(self, lessons):
        if not isinstance(lessons, tuple) or len(lessons) != 3:
            raise HOLD("Expected two teacher domains and a neutral contrast")
        self.lessons = lessons
        self._verify_lessons()

    def _verify_lessons(self):
        teachers = set()
        contexts = set()
        refs = set()
        for lesson in self.lessons:
            if lesson.source_revision != SOURCE_REVISION:
                raise HOLD("Teacher source revision not current")
            label(lesson.teacher_claim)
            if lesson.teacher_claim not in ("TEACHER_A", "TEACHER_B"):
                raise HOLD("Unknown teacher in the bounded evaluator")
            if lesson.case.ref in refs:
                raise HOLD("Repeated teacher scenario")
            refs.add(lesson.case.ref)
            teachers.add(lesson.teacher_claim)
            contexts.add((lesson.case.need_lookup, lesson.case.need_challenge))
            expected = digest({"teacher": lesson.teacher_claim,
                               "ref": lesson.case.ref,
                               "context": lesson.case.context(),
                               "events": list(lesson.events),
                               "revision": SOURCE_REVISION})
            if expected != lesson.receipt:
                raise HOLD("Corrupted public demonstration")
            state = State()
            for event in lesson.events:
                if not isinstance(event, dict) or set(event) != {"op", "before", "after"}:
                    raise HOLD("Unexpected teacher reasoning trace")
                if event["before"] != state.packet():
                    raise HOLD("Broken demonstrated precondition")
                state = transition(event["op"], state, lesson.case)
                if event["after"] != state.packet():
                    raise HOLD("Fabricated observable transition")
            if not state.drafted:
                raise HOLD("Only teacher-demonstrated success is admitted")
        if teachers != {"TEACHER_A", "TEACHER_B"} or contexts != {
            (True, False), (False, True), (False, False)
        }:
            raise HOLD("Insufficient contrastive teacher coverage")

    def _infer_guards(self):
        used_ops = set(e["op"] for lesson in self.lessons for e in lesson.events)
        guards = {}
        for op in sorted(used_ops):
            labels = tuple(any(e["op"] == op for e in lesson.events)
                           for lesson in self.lessons)
            candidates = tuple(g for g in GUARDS if
                               tuple(matches(g, l.case) for l in self.lessons) == labels)
            if len(candidates) != 1:
                raise HOLD(f"Guard for {op} ambiguous; more lessons required")
            guards[op] = candidates[0]
        if used_ops != set(OPS):
            raise HOLD("Missing step learned from teacher")
        return guards

    def _orders(self):
        # Preserve every order that teachers actually demonstrated. Unknown
        # pairs remain unordered; the receiver must check their interaction.
        edges = {(a["op"], b["op"])
                 for lesson in self.lessons
                 for i, a in enumerate(lesson.events)
                 for b in lesson.events[i+1:]}
        orders = tuple(order for order in permutations(OPS)
                       if all(order.index(a) < order.index(b) for a, b in edges))
        if not orders or len(orders) > 24:
            raise HOLD("Contradictory/unbounded teacher partial orders")
        unresolved = tuple(sorted([list(pair) for pair in combinations(OPS, 2)
                                  if not any((a, b) in edges or (b, a) in edges
                                             for a, b in [pair])]))
        return orders, unresolved

    def synthesize(self):
        guards = self._infer_guards()
        orders, unresolved = self._orders()
        # Select a canonical linearization of the observed partial order.
        # Other possible orders are review obligations, not hidden facts.
        order = min(orders)
        program = [{"op": op, "guard": guards[op]} for op in order]
        portable(program)
        for lesson in self.lessons:
            observed = execute(program, lesson.case)
            if observed["result"] != "DRAFT" or tuple(observed["events"]) != lesson.events:
                raise HOLD("Candidate fails demonstration replay")
        body = {"schema": SCHEMA, "source_contract": SOURCE_REVISION,
                "origin_claim": "TWO_SYNTHETIC_TEACHERS_UNVERIFIED",
                "program": program,
                "teacher_claims": sorted({x.teacher_claim for x in self.lessons}),
                "teaching_receipts": sorted(x.receipt for x in self.lessons),
                "unobserved_order_pairs": unresolved,
                "possible_orders": len(orders),
                "status": "PROPOSED", "scope": "LOCAL_SYNTHETIC_READ_ONLY",
                "real_world_authority": False}
        packet = dict(body, checksum_sha256=digest(body))
        raw = json.dumps(packet, indent=2, sort_keys=True) + "\n"
        validate(raw)
        return raw


def validate(raw):
    if not isinstance(raw, str) or len(raw.encode("utf-8")) > MAX_BYTES:
        raise HOLD("Too large/malformed method cartridge")
    try:
        obj = json.loads(raw)
    except (ValueError, TypeError) as exc:
        raise HOLD("Invalid JSON") from exc
    keys = {"schema", "source_contract", "origin_claim", "program", "teacher_claims",
            "teaching_receipts", "unobserved_order_pairs", "possible_orders",
            "status", "scope", "real_world_authority", "checksum_sha256"}
    if not isinstance(obj, dict) or set(obj) != keys:
        raise HOLD("Unexpected method-cartridge fields")
    if (obj["schema"] != SCHEMA or obj["source_contract"] != SOURCE_REVISION or
            obj["origin_claim"] != "TWO_SYNTHETIC_TEACHERS_UNVERIFIED" or
            obj["status"] != "PROPOSED" or
            obj["scope"] != "LOCAL_SYNTHETIC_READ_ONLY" or
            obj["real_world_authority"] is not False):
        raise HOLD("Unsupported source or authority claims")
    program = portable(obj["program"])
    if ({p["op"] for p in program} != set(OPS) or
            program[0] != {"op": "VERIFY_SOURCE", "guard": "ALWAYS"} or
            program[-1] != {"op": "DRAFT_HYPOTHESIS", "guard": "ALWAYS"} or
            next(p["guard"] for p in program if p["op"] == "EXACT_LOOKUP") != "NEED_LOOKUP" or
            next(p["guard"] for p in program if p["op"] == "TEST_COUNTEREXAMPLE") != "NEED_CHALLENGE"):
        raise HOLD("Changed or enlarged learned procedure")
    if obj["teacher_claims"] != ["TEACHER_A", "TEACHER_B"]:
        raise HOLD("Invalid donor set")
    receipts = obj["teaching_receipts"]
    if (not isinstance(receipts, list) or len(receipts) != 3 or receipts != sorted(set(receipts))
            or any(not isinstance(s, str) or len(s) != 64 or
                   any(c not in "0123456789abcdef" for c in s) for s in receipts)):
        raise HOLD("Invalid teaching receipt references")
    if obj["unobserved_order_pairs"] != [["EXACT_LOOKUP", "TEST_COUNTEREXAMPLE"]]:
        raise HOLD("Unresolved order evidence changed")
    if type(obj["possible_orders"]) is not int or obj["possible_orders"] != 2:
        raise HOLD("Incompatible ordering uncertainty")
    if obj["checksum_sha256"] != digest({k: v for k, v in obj.items()
                                         if k != "checksum_sha256"}):
        raise HOLD("Cartridge content changed")
    return obj


class LocalReceiver:
    """Receiving organ owns all revalidation and the explicit admission decision."""
    def __init__(self, raw, source_revision=SOURCE_REVISION):
        self.packet = validate(raw)
        if source_revision != self.packet["source_contract"]:
            raise HOLD("Changed recipient world contract")
        self.admitted = False
        self.preview_digest = None
        self.passed = False

    def preview(self, independently_labeled_cases):
        if (not isinstance(independently_labeled_cases, tuple)
                or not independently_labeled_cases):
            raise HOLD("Requires independent test labels")
        reviewed = []
        seen = set()
        alternate = [dict(p) for p in self.packet["program"]]
        alternate[1], alternate[2] = alternate[2], alternate[1]
        unresolved_order_disagreements = 0
        for case, expected in independently_labeled_cases:
            if not isinstance(case, Case) or case.ref in seen or expected not in ("DRAFT", "HOLD"):
                raise HOLD("Invalid independent case")
            seen.add(case.ref)
            outcome = execute(self.packet["program"], case)
            other = execute(alternate, case)
            if outcome["result"] != other["result"]:
                unresolved_order_disagreements += 1
            reviewed.append({"case": case.ref, "actual": outcome["result"],
                             "expected": expected,
                             "context": case.context()})
        errors = sum(row["actual"] != row["expected"] for row in reviewed)
        # Test the unseen combined case and one refusal, and verify that the
        # previously unordered teacher steps commute under this source revision.
        both_ok = any(case.need_lookup and case.need_challenge and expected == "DRAFT"
                      for case, expected in independently_labeled_cases)
        negative = any(expected == "HOLD" for _, expected in independently_labeled_cases)
        if not both_ok or not negative:
            raise HOLD("Review omitted joint challenge or refusal")
        self.passed = errors == 0 and unresolved_order_disagreements == 0
        self.preview_digest = digest({"cartridge": self.packet["checksum_sha256"],
                                      "review": reviewed, "errors": errors,
                                      "order_disagreements": unresolved_order_disagreements})
        return {"stage": "HOLD_REVIEW", "correct": len(reviewed)-errors,
                "cases": len(reviewed), "errors": errors,
                "unresolved_order_disagreements": unresolved_order_disagreements,
                "review_digest": self.preview_digest,
                "real_world_authority": False}

    def admit(self, decision, preview_digest):
        if (decision != "ADMIT_READ_ONLY" or not self.passed or
                preview_digest != self.preview_digest):
            raise HOLD("Failed or unapproved local preview")
        self.admitted = True

    def suggest(self, case):
        if not self.admitted:
            raise HOLD("Reason-procedure cartridge not admitted locally")
        if not isinstance(case, Case):
            raise HOLD("Unknown scenario")
        return {"stage": "SUGGEST_ONLY", "procedure": self.packet["program"],
                "toy_outcome": execute(self.packet["program"], case),
                "executed_externally": False, "authority": False}
