"""MOTIF THOUGHT-007: non-fungible semantic identities + multiple manifestations.

A word is not a concept. A concept is not its context-local manifestation.
A manifestation is not its view-local placement. Geometry never supplies facts.
All equivalences and referent matches are *proposals*; authority remains HOLD.

Python 3.10+ standard library only; bounded, locally replayable single-writer log.
"""
from __future__ import annotations

import copy
import hashlib
import json
import math
import os
from pathlib import Path

SCHEMA = "motif.thought-field.event.v1"
GENESIS = "0" * 64
LENSES = frozenset({"association", "dependency", "tension", "timeline", "affordance", "flower_hex", "NONE"})
PHASES = frozenset({"ABSTRACT_PENCIL", "CONCRETE_PENCIL", "PEN_CONTEXT"})
EVENT_FIELDS = {
    "CONCEPT": {"id", "label", "description", "origin"},
    "REVISE_CONCEPT": {"id", "label", "description", "reason"},
    "EXPRESSION": {"id", "text", "origin", "context"},
    "REFERENT_PROPOSAL": {"id", "expression_id", "concept_id", "reason", "origin"},
    "MANIFEST": {"id", "concept_id", "context", "role", "phase", "parent_id"},
    "VIEW": {"id", "lens", "purpose"},
    "PLACE": {"id", "manifestation_id", "view_id", "x", "y", "purpose"},
    "MOVE": {"id", "x", "y", "reason", "expected_revision"},
    "REMOVE_PLACEMENT": {"id", "reason"},
    "EQUIVALENCE_PROPOSAL": {"id", "left", "right", "origin", "reason"},
}

class FieldError(ValueError):
    """Invalid typed structure, stale source, or broken local audit chain."""


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
                      allow_nan=False).encode("utf-8")


def digest(obj):
    return hashlib.sha256(canonical(obj)).hexdigest()


def ident(value, field):
    if (not isinstance(value, str) or not value or len(value) > 120 or
            value.strip() != value or any(ch.isspace() for ch in value)):
        raise FieldError(f"invalid {field} identifier")
    return value


def label(value, field, max_len=1000):
    if not isinstance(value, str) or not value.strip() or len(value) > max_len:
        raise FieldError(f"invalid {field} text")
    return value


def optional_ident(value, field):
    if value is not None:
        ident(value, field)
    return value


def coordinate(value):
    if type(value) not in (int, float) or not math.isfinite(value) or abs(value) > 1_000_000:
        raise FieldError("coordinates must be finite, bounded numbers")
    return float(value)


class ThoughtField:
    """Append-only local prototype. Not safe for concurrent multi-process writing.

    The hash chain detects changes to *a fixed trusted head*, not a malicious
    author who can replace the complete file. No cryptographic signer exists.
    """
    def __init__(self, path):
        self.path = Path(path)
        self.reload()

    def _empty(self):
        self.concepts = {}
        self.expressions = {}
        self.referents = {}
        self.manifestations = {}
        self.views = {}
        self.placements = {}
        self.equivalence_proposals = {}
        self._events = []

    @property
    def head_digest(self):
        return self._events[-1]["digest"] if self._events else GENESIS

    def reload(self):
        content = self.path.read_bytes() if self.path.exists() else b""
        if len(content) > 3_000_000:
            raise FieldError("log size exceeds 3MB limit")
        if content and not content.endswith(b"\n"):
            raise FieldError("partial terminal event")
        self._empty()
        previous = GENESIS
        for sequence, line in enumerate(content.splitlines(), 1):
            try:
                event = json.loads(line)
            except (ValueError, UnicodeError) as exc:
                raise FieldError("invalid JSON log record") from exc
            if type(event) is not dict or set(event) != {
                    "schema", "sequence", "event_id", "type", "payload", "previous", "digest"}:
                raise FieldError("malformed event envelope")
            body = {k: v for k, v in event.items() if k != "digest"}
            if (event["schema"] != SCHEMA or type(event["sequence"]) is not int or
                    event["sequence"] != sequence or event["event_id"] != f"evt-{sequence:06d}" or
                    event["previous"] != previous or event["digest"] != digest(body) or
                    line != canonical(event)):
                raise FieldError("invalid hash chain or canonical encoding")
            self._apply(event["type"], event["payload"])
            self._events.append(event)
            previous = event["digest"]
        self._loaded = content

    def _exists(self, registry, key, kind):
        ident(key, kind)
        if key not in registry:
            raise FieldError(f"unknown {kind}: {key}")
        return registry[key]

    def _new(self, registry, key, kind):
        ident(key, kind)
        if key in registry:
            raise FieldError(f"duplicate {kind} id: {key}")

    def _apply(self, event_type, p):
        if event_type not in EVENT_FIELDS or not isinstance(p, dict) or set(p) != EVENT_FIELDS[event_type]:
            raise FieldError("event type or payload does not match schema")
        if event_type == "CONCEPT":
            self._new(self.concepts, p["id"], "concept")
            self.concepts[p["id"]] = dict(id=p["id"], label=label(p["label"], "concept label"),
                                          description=label(p["description"], "concept description"),
                                          origin=ident(p["origin"], "declared origin"), revision=1)
        elif event_type == "REVISE_CONCEPT":
            c = self._exists(self.concepts, p["id"], "concept")
            new_label = label(p["label"], "concept label")
            new_description = label(p["description"], "concept description")
            label(p["reason"], "revision reason")
            c["label"], c["description"] = new_label, new_description
            c["revision"] += 1
        elif event_type == "EXPRESSION":
            self._new(self.expressions, p["id"], "expression")
            self.expressions[p["id"]] = dict(id=p["id"], text=label(p["text"], "text", 5000),
                                             origin=ident(p["origin"], "declared origin"),
                                             context=label(p["context"], "context"))
        elif event_type == "REFERENT_PROPOSAL":
            self._new(self.referents, p["id"], "referent proposal")
            self._exists(self.expressions, p["expression_id"], "expression")
            self._exists(self.concepts, p["concept_id"], "concept")
            self.referents[p["id"]] = dict(id=p["id"], expression_id=p["expression_id"],
                concept_id=p["concept_id"], origin=ident(p["origin"], "declared origin"),
                reason=label(p["reason"], "reason"), status="HYPOTHESIS_ONLY")
        elif event_type == "MANIFEST":
            self._new(self.manifestations, p["id"], "manifestation")
            self._exists(self.concepts, p["concept_id"], "concept")
            if type(p["phase"]) is not str or p["phase"] not in PHASES:
                raise FieldError("unrecognized reasoning phase")
            parent_id = optional_ident(p["parent_id"], "parent manifestation")
            if parent_id is not None:
                parent = self._exists(self.manifestations, parent_id, "parent manifestation")
                if parent["concept_id"] != p["concept_id"]:
                    raise FieldError("fork cannot silently switch concept identity")
            self.manifestations[p["id"]] = dict(id=p["id"], concept_id=p["concept_id"],
                context=label(p["context"], "context"), role=label(p["role"], "role"),
                phase=p["phase"], parent_id=parent_id)
        elif event_type == "VIEW":
            self._new(self.views, p["id"], "view")
            if type(p["lens"]) is not str or p["lens"] not in LENSES:
                raise FieldError("unsupported geometric view lens")
            self.views[p["id"]] = dict(id=p["id"], lens=p["lens"],
                                       purpose=label(p["purpose"], "purpose"),
                                       coordinate_authority="NONE")
        elif event_type == "PLACE":
            self._new(self.placements, p["id"], "placement")
            self._exists(self.manifestations, p["manifestation_id"], "manifestation")
            v = self._exists(self.views, p["view_id"], "view")
            x, y = p["x"], p["y"]
            if v["lens"] == "NONE":
                if x is not None or y is not None:
                    raise FieldError("NONE view cannot have geometric coordinates")
            else:
                x, y = coordinate(x), coordinate(y)
            self.placements[p["id"]] = dict(id=p["id"], manifestation_id=p["manifestation_id"],
                view_id=p["view_id"], x=x, y=y,
                purpose=label(p["purpose"], "purpose"), revision=1, active=True,
                coordinate_authority="NONE")
        elif event_type == "MOVE":
            placement = self._exists(self.placements, p["id"], "placement")
            if not placement["active"]:
                raise FieldError("retired placement cannot be moved")
            if type(p["expected_revision"]) is not int or p["expected_revision"] != placement["revision"]:
                raise FieldError("stale placement revision")
            v = self.views[placement["view_id"]]
            if v["lens"] == "NONE":
                raise FieldError("NONE view cannot move coordinates")
            x, y = coordinate(p["x"]), coordinate(p["y"])
            label(p["reason"], "move reason")
            placement["x"], placement["y"] = x, y
            placement["revision"] += 1
        elif event_type == "REMOVE_PLACEMENT":
            placement = self._exists(self.placements, p["id"], "placement")
            label(p["reason"], "removal reason")
            if not placement["active"]:
                raise FieldError("placement already retired")
            placement["active"] = False
        elif event_type == "EQUIVALENCE_PROPOSAL":
            self._new(self.equivalence_proposals, p["id"], "equivalence proposal")
            left = self._exists(self.concepts, p["left"], "concept")
            right = self._exists(self.concepts, p["right"], "concept")
            if left["id"] == right["id"]:
                raise FieldError("identity equivalence is trivial; no proposal required")
            self.equivalence_proposals[p["id"]] = dict(id=p["id"], left=left["id"], right=right["id"],
                reason=label(p["reason"], "reason"), origin=ident(p["origin"], "declared origin"),
                status="HYPOTHESIS_ONLY")

    def _append(self, event_type, payload):
        current = self.path.read_bytes() if self.path.exists() else b""
        if current != self._loaded:
            raise FieldError("stale writer: reload before editing")
        sequence = len(self._events) + 1
        body = dict(schema=SCHEMA, sequence=sequence, event_id=f"evt-{sequence:06d}",
                    type=event_type, payload=payload, previous=self.head_digest)
        prior = (self.concepts, self.expressions, self.referents, self.manifestations,
                 self.views, self.placements, self.equivalence_proposals)
        (self.concepts, self.expressions, self.referents, self.manifestations,
         self.views, self.placements, self.equivalence_proposals) = copy.deepcopy(prior)
        try:
            self._apply(event_type, payload)
            ev = {**body, "digest": digest(body)}
            record = canonical(ev) + b"\n"
            if len(current) + len(record) > 3_000_000:
                raise FieldError("log exceeds size bound")
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("ab") as out:
                out.write(record)
                out.flush()
                os.fsync(out.fileno())
        except Exception:
            (self.concepts, self.expressions, self.referents, self.manifestations,
             self.views, self.placements, self.equivalence_proposals) = prior
            raise
        self._loaded += record
        self._events.append(ev)
        return copy.deepcopy(ev)

    def concept(self, id, label, description, origin):
        return self._append("CONCEPT", dict(id=id, label=label, description=description, origin=origin))

    def revise_concept(self, id, label, description, reason):
        return self._append("REVISE_CONCEPT", dict(id=id, label=label, description=description, reason=reason))

    def expression(self, id, text, origin, context):
        return self._append("EXPRESSION", dict(id=id, text=text, origin=origin, context=context))

    def propose_referent(self, id, expression_id, concept_id, reason, origin):
        return self._append("REFERENT_PROPOSAL", dict(id=id, expression_id=expression_id,
                        concept_id=concept_id, reason=reason, origin=origin))

    def manifest(self, id, concept_id, context, role, phase="ABSTRACT_PENCIL", parent_id=None):
        return self._append("MANIFEST", dict(id=id, concept_id=concept_id, context=context,
                                            role=role, phase=phase, parent_id=parent_id))

    def view(self, id, lens, purpose):
        return self._append("VIEW", dict(id=id, lens=lens, purpose=purpose))

    def place(self, id, manifestation_id, view_id, x, y, purpose):
        return self._append("PLACE", dict(id=id, manifestation_id=manifestation_id,
                                         view_id=view_id, x=x, y=y, purpose=purpose))

    def move(self, id, x, y, reason, expected_revision):
        return self._append("MOVE", dict(id=id, x=x, y=y, reason=reason,
                                         expected_revision=expected_revision))

    def remove_placement(self, id, reason):
        return self._append("REMOVE_PLACEMENT", dict(id=id, reason=reason))

    def propose_equivalence(self, id, left, right, origin, reason):
        return self._append("EQUIVALENCE_PROPOSAL", dict(id=id, left=left, right=right,
                                                        origin=origin, reason=reason))

    def semantic_snapshot(self):
        """Intentionally invariant under view/placement creation, movement and removal."""
        def ordered(registry):
            return [copy.deepcopy(registry[k]) for k in sorted(registry)]
        return dict(schema="motif.thought-field.semantics.v1",
                    concepts=ordered(self.concepts), expressions=ordered(self.expressions),
                    referent_proposals=ordered(self.referents),
                    manifestations=ordered(self.manifestations),
                    equivalence_proposals=ordered(self.equivalence_proposals),
                    external_authority="NONE")

    def snapshot(self):
        return dict(semantic=self.semantic_snapshot(),
                    views=[copy.deepcopy(self.views[k]) for k in sorted(self.views)],
                    placements=[copy.deepcopy(self.placements[k]) for k in sorted(self.placements)],
                    head_digest=self.head_digest, events=len(self._events),
                    external_authority="NONE")

    def history(self):
        return copy.deepcopy(self._events)

    def occurrences(self, concept_id):
        self._exists(self.concepts, concept_id, "concept")
        ids = {m["id"] for m in self.manifestations.values() if m["concept_id"] == concept_id}
        return dict(concept_id=concept_id,
                    manifestation_ids=sorted(ids),
                    placements=[copy.deepcopy(p) for p in sorted(self.placements.values(), key=lambda x:x["id"])
                                if p["manifestation_id"] in ids and p["active"]],
                    authority="NONE")
