"""MOTIF-007 — Inheritance without empire.

A source-independent, graph-only METHOD transfer experiment:
export an abstract operator dependency closure (not the donor's world),
verify hashes and source semantics, HOLD by default, test in the recipient's
own synthetic world, and require an explicit LOCAL review decision.

No network, keys, signatures, human identity verification, real permission,
remote execution, neural learning, or external authority.
Python 3.10+, standard library only.
"""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import json
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "002"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "006"))
from motif002 import F, Fact, World, Verb, induce, lessons, scene
from composition import (Call, Macro, Operator, Trace, Inapplicable,
                         signature, checked_apply, replay, rename_world,
                         bind_prefix, two_level_training, compile_trace)

SCHEMA = "motif.portable-method.v0"
LIMIT_BYTES = 160000
LIMIT_OPERATORS = 24
MAX_EXPANDED = 12
# A source method is unable to mint permission-like relations as a side effect.
# This is a synthetic graph rule, NOT real-world authorization validation.
RESERVED_EFFECTS = frozenset({
    "permits", "authorizes", "consent", "admitted", "verified",
    "identity_verified", "signature_valid", "grant_authority"})
VALID_TOKEN = re.compile(r"^[a-zA-Z0-9_?.:-]{1,96}$")


class HOLD(ValueError):
    """Reject or defer an untrusted transfer. No automatic fallback to admission."""


def digest(value) -> str:
    """Content hash. This is NOT a signature, proof of authorship or custody."""
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"),
                     ensure_ascii=True)
    return sha256(raw.encode("utf-8")).hexdigest()


def facts_json(facts: World):
    return [list(x) for x in sorted(facts)]


def encoded(op: Operator) -> dict:
    payload = {
        "id": op.id, "role_types": list(op.role_types),
        "requires": facts_json(op.requires), "adds": facts_json(op.adds),
        "removes": facts_json(op.removes),
        "demonstrations": op.demonstrations,
        "semantic_sha256": signature(op)
    }
    if isinstance(op, Verb):
        return dict(payload, kind="primitive")
    return dict(payload, kind="composite", status=op.status, depth=op.depth,
                calls=[{"operator": c.operator, "roles": list(c.roles)}
                       for c in op.calls],
                pins=[list(x) for x in op.pins])


def method_closure(root: str, catalog: dict[str, Operator]) -> tuple[str, ...]:
    """Deterministic dependency-first closure; no personal world history."""
    completed, active, order = set(), set(), []

    def visit(name):
        if name in completed:
            return
        if name in active:
            raise HOLD("Dependency cycle")
        op = catalog.get(name)
        if op is None:
            raise HOLD("Missing source dependency")
        active.add(name)
        if isinstance(op, Macro):
            for dep in sorted({x.operator for x in op.calls}):
                visit(dep)
        active.remove(name)
        completed.add(name)
        order.append(name)

    visit(root)
    if len(order) > LIMIT_OPERATORS:
        raise HOLD("Operator closure too large")
    return tuple(order)


def export_method(root: str, catalog: dict[str, Operator],
                  origin_claim="UNVERIFIED_FIXTURE_A") -> str:
    """Export only the abstract operator closure.

    Every literal constant inside an operator still deserves a privacy review:
    absence of a donor world graph does NOT prove all source code is harmless.
    """
    if not isinstance(origin_claim, str) or not VALID_TOKEN.fullmatch(origin_claim):
        raise HOLD("Invalid unverified origin label")
    names = method_closure(root, catalog)
    body = {
        "schema": SCHEMA, "origin_claim": origin_claim,
        "root": root,
        "operators": [encoded(catalog[name]) for name in names]
    }
    packet = dict(body, checksum_sha256=digest(body))
    raw = json.dumps(packet, indent=2, sort_keys=True) + "\n"
    if len(raw.encode("utf-8")) > LIMIT_BYTES:
        raise HOLD("Encoded package too large")
    # Independently parse the artifact we are about to export.
    verify_packet(raw)
    return raw


def expect_keys(data, allowed, label):
    if not isinstance(data, dict) or set(data) != set(allowed):
        raise HOLD(f"{label}: unexpected fields")


def require_token(value, label):
    if not isinstance(value, str) or not VALID_TOKEN.fullmatch(value):
        raise HOLD(f"{label}: invalid token")
    return value


def decode_facts(items, label):
    if not isinstance(items, list) or len(items) > 150:
        raise HOLD(f"{label}: invalid fact collection")
    result = set()
    for entry in items:
        if not isinstance(entry, list) or len(entry) < 2 or len(entry) > 6:
            raise HOLD(f"{label}: invalid fact arity")
        result.add(tuple(require_token(x, label) for x in entry))
    if len(result) != len(items):
        raise HOLD(f"{label}: duplicate facts")
    return frozenset(result)


def decode_operator(entry) -> Operator:
    base = {"id", "role_types", "requires", "adds", "removes",
            "demonstrations", "semantic_sha256", "kind"}
    if not isinstance(entry, dict):
        raise HOLD("Operator must be object")
    kind = entry.get("kind")
    keys = base if kind == "primitive" else (
        base | {"status", "depth", "calls", "pins"})
    expect_keys(entry, keys, "operator")
    name = require_token(entry["id"], "operator ID")
    if not ((kind == "primitive" and name.startswith("verb-")) or
            (kind == "composite" and name.startswith("macro-"))):
        raise HOLD("Operator ID incompatible with kind")
    role_types = entry["role_types"]
    if not isinstance(role_types, list) or not (1 <= len(role_types) <= 8):
        raise HOLD("Invalid role types")
    if any(x not in ("person", "bike") for x in role_types):
        raise HOLD("Unknown role ontology (MOTIF-002 bounded experiment)")
    demonstrations = entry["demonstrations"]
    if type(demonstrations) is not int or demonstrations < 1 or demonstrations > 100000:
        raise HOLD("Invalid source support")
    requires = decode_facts(entry["requires"], "preconditions")
    adds = decode_facts(entry["adds"], "effects")
    removes = decode_facts(entry["removes"], "effects")
    if any(f[0] in RESERVED_EFFECTS for f in (adds | removes)):
        raise HOLD("Method may not manufacture or revoke a permission relation")
    for relation in (requires | adds | removes):
        for word in relation[1:]:
            if word.startswith("?") and word[1:].isdigit():
                if int(word[1:]) >= len(role_types):
                    raise HOLD("Unbound role placeholder")
    if not any(x[0] == "permits" for x in requires) and kind == "primitive":
        raise HOLD("Missing synthetic permission prerequisite")
    if kind == "primitive":
        op = Verb(name, tuple(role_types), requires, adds,
                  removes, demonstrations)
    else:
        if entry["status"] != "CANDIDATE_ONLY":
            raise HOLD("Non-candidate composite not accepted")
        depth = entry["depth"]
        if type(depth) is not int or not (2 <= depth <= MAX_EXPANDED):
            raise HOLD("Invalid expanded macro length")
        raw_calls = entry["calls"]
        if not isinstance(raw_calls, list) or not (2 <= len(raw_calls) <= MAX_EXPANDED):
            raise HOLD("Invalid macro program")
        calls = []
        for call in raw_calls:
            expect_keys(call, {"operator", "roles"}, "call")
            target = require_token(call["operator"], "dependency")
            roles = call["roles"]
            if not isinstance(roles, list) or len(roles) > 8:
                raise HOLD("Invalid call role bindings")
            if any(not isinstance(x, str) or not re.fullmatch(r"\?[0-7]", x)
                   or int(x[1:]) >= len(role_types) for x in roles):
                raise HOLD("Macro may only reference its declared role variables")
            calls.append(Call(target, tuple(roles)))
        pins_data = entry["pins"]
        if not isinstance(pins_data, list) or len(pins_data) > MAX_EXPANDED:
            raise HOLD("Invalid dependency pins")
        pins = []
        for row in pins_data:
            if not isinstance(row, list) or len(row) != 2:
                raise HOLD("Bad source pin")
            dep = require_token(row[0], "pin source")
            hexval = row[1]
            if not isinstance(hexval, str) or not re.fullmatch("[a-f0-9]{64}", hexval):
                raise HOLD("Bad source fingerprint")
            pins.append((dep, hexval))
        if tuple(sorted(set(pins))) != tuple(pins):
            raise HOLD("Duplicate or unordered source pins")
        if {c.operator for c in calls} != {p[0] for p in pins}:
            raise HOLD("Source pins must cover exact macro dependencies")
        op = Macro(name, tuple(role_types), tuple(calls), requires, adds,
                   removes, tuple(pins), demonstrations, depth)
    if entry["semantic_sha256"] != signature(op):
        raise HOLD("Operator fingerprint mismatch")
    return op


@dataclass(frozen=True)
class Portable:
    root: str
    origin_claim: str
    checksum: str
    catalog: dict[str, Operator]
    raw: str


def verify_packet(raw: str) -> Portable:
    """Checks *structural* integrity only. Anybody can recompute a checksum."""
    if not isinstance(raw, str) or len(raw.encode("utf-8")) > LIMIT_BYTES:
        raise HOLD("Malformed or oversized transfer")
    try:
        packet = json.loads(raw)
    except (ValueError, TypeError) as exc:
        raise HOLD("Invalid JSON") from exc
    expect_keys(packet, {"schema", "origin_claim", "root",
                         "operators", "checksum_sha256"}, "packet")
    if packet["schema"] != SCHEMA:
        raise HOLD("Unrecognized transfer protocol")
    origin = require_token(packet["origin_claim"], "origin claim")
    root = require_token(packet["root"], "root")
    checksum = packet["checksum_sha256"]
    if not isinstance(checksum, str) or not re.fullmatch("[a-f0-9]{64}", checksum):
        raise HOLD("Malformed checksum")
    body = {key: val for key, val in packet.items() if key != "checksum_sha256"}
    if digest(body) != checksum:
        raise HOLD("Artifact checksum mismatch")
    entries = packet["operators"]
    if not isinstance(entries, list) or not (1 <= len(entries) <= LIMIT_OPERATORS):
        raise HOLD("Invalid number of source operators")
    operators = [decode_operator(entry) for entry in entries]
    catalog = {x.id: x for x in operators}
    if len(catalog) != len(operators) or root not in catalog:
        raise HOLD("Duplicate or missing root operator")
    order = method_closure(root, catalog)
    if set(order) != set(catalog):
        raise HOLD("Package contains unrelated operators")
    for op in operators:
        if not isinstance(op, Macro):
            continue
        for dep, pin in op.pins:
            if dep not in catalog or pin != signature(catalog[dep]):
                raise HOLD("Transitive source fingerprint mismatch")
        for call in op.calls:
            child = catalog[call.operator]
            if len(call.roles) != len(child.role_types):
                raise HOLD("Wrong nested call arity")
            for place, expected_type in zip(call.roles, child.role_types):
                actual_type = op.role_types[int(place[1:])]
                if actual_type != expected_type:
                    raise HOLD("Nested role type mismatch")
        expanded = sum(catalog[c.operator].depth if isinstance(
            catalog[c.operator], Macro) else 1 for c in op.calls)
        if expanded != op.depth or expanded > MAX_EXPANDED:
            raise HOLD("Invalid nested expanded length")
    return Portable(root, origin, checksum, catalog, raw)


@dataclass(frozen=True)
class LocalPreview:
    artifact_checksum: str
    root: str
    roles: tuple[str, ...]
    local_world_sha256: str
    predicted_world_sha256: str
    preview_digest: str
    status: str


@dataclass(frozen=True)
class LocalDecision:
    artifact_checksum: str
    root: str
    decision: str
    reviewer_claim: str
    preview_digest: str
    note: str


class Receiver:
    """Independent local *simulation* stewardship.

    No network or shared global registry. Approval is a fixture-level
    explicit action; the reviewer claim is NOT authenticated identity.
    """

    def __init__(self, receiver_label: str):
        self.label = require_token(receiver_label, "receiver label")
        self.pending: dict[str, Portable] = {}
        self.previews: dict[str, LocalPreview] = {}
        self.decisions: list[LocalDecision] = []
        self.admitted: set[str] = set()
        self.local_catalog: dict[str, Operator] = {}

    def offer(self, raw: str) -> str:
        method = verify_packet(raw)
        for key, foreign in method.catalog.items():
            local = self.local_catalog.get(key)
            if local is not None and signature(local) != signature(foreign):
                raise HOLD("Foreign source would overwrite a local operator")
        self.pending[method.checksum] = method
        return method.checksum  # Remains HELD until a separate local decision.

    def preview(self, checksum: str, local_world: World,
                roles: tuple[str, ...]) -> LocalPreview:
        method = self.pending.get(checksum)
        if method is None:
            raise HOLD("No pending local offer")
        if not isinstance(roles, tuple):
            raise HOLD("Expected locally selected role bindings")
        catalog = dict(self.local_catalog, **method.catalog)
        try:
            simulated = checked_apply(local_world, method.root, roles, catalog)
        except (Inapplicable, IndexError, KeyError) as exc:
            raise HOLD("Method has no admissible simulation in local world") from exc
        observed_snapshot = digest(facts_json(local_world))
        projected_snapshot = digest(facts_json(simulated))
        note = digest({
            "package": checksum, "root": method.root, "roles": roles,
            "local_world": observed_snapshot,
            "simulated_world": projected_snapshot,
            "result": "LOCAL_SIMULATION_ONLY"
        })
        result = LocalPreview(checksum, method.root, roles, observed_snapshot,
                              projected_snapshot, note, "SIMULATED_NOT_ADMITTED")
        self.previews[note] = result
        return result

    def review(self, checksum: str, decision: str, reviewer_claim: str,
               preview_digest: str = "", note: str = "") -> LocalDecision:
        if checksum not in self.pending:
            raise HOLD("No pending transfer to review")
        reviewer = require_token(reviewer_claim, "local reviewer claim")
        if decision not in ("ADMIT_PLAN_ONLY", "REFUSE"):
            raise HOLD("Decision must be explicit and locally bounded")
        method = self.pending[checksum]
        if decision == "ADMIT_PLAN_ONLY":
            preview = self.previews.get(preview_digest)
            if preview is None or preview.artifact_checksum != checksum:
                raise HOLD("Exact locally evaluated preview is mandatory")
            for key, foreign in method.catalog.items():
                local = self.local_catalog.get(key)
                if local is not None and signature(local) != signature(foreign):
                    raise HOLD("Conflicting local source")
            self.local_catalog.update(method.catalog)
            self.admitted.add(checksum)
        else:
            self.admitted.discard(checksum)
        receipt = LocalDecision(checksum, method.root, decision, reviewer,
                                preview_digest, str(note)[:240])
        self.decisions.append(receipt)
        return receipt

    def simulate_admitted(self, checksum: str, world: World,
                          roles: tuple[str, ...]) -> World:
        if checksum not in self.admitted:
            raise HOLD("Not locally admitted for simulation")
        portable = self.pending[checksum]
        return checked_apply(world, portable.root, roles, self.local_catalog)

    def revoke(self, checksum: str, reviewer_claim: str) -> LocalDecision:
        require_token(reviewer_claim, "reviewer claim")
        if checksum not in self.admitted:
            raise HOLD("Only admitted methods may be revoked")
        self.admitted.remove(checksum)
        receipt = LocalDecision(checksum, self.pending[checksum].root,
                                "REVOKE_PLAN_ONLY", reviewer_claim, "",
                                "revocation of a local simulated planning permission")
        self.decisions.append(receipt)
        return receipt


def receiver_scene():
    """Synthetic independent local world, never part of the exported package."""
    mapping = {"Jo": "Nina", "Mira": "Omar",
               "bike1": "wheelA", "bike2": "wheelB"}
    return rename_world(scene(), mapping), ("Nina", "Omar", "wheelA", "wheelB")


def extended_receiver_scene():
    world, roles = receiver_scene()
    world |= frozenset({
        F("bike", "wheelC"), F("owns", "Nina", "wheelC"),
        F("broken", "wheelC"), F("permits", "Nina", "Nina", "wheelC")
    })
    return world, roles


def demonstrate() -> dict:
    verbs = induce(lessons())
    _, inner, outer = two_level_training(verbs)
    donor_catalog = dict(verbs)
    donor_catalog[inner.id] = inner
    donor_catalog[outer.id] = outer
    artifact = export_method(outer.id, donor_catalog, origin_claim="MOTIF_A_UNVERIFIED")
    source = verify_packet(artifact)
    receiver = Receiver("MOTIF_B")
    ticket = receiver.offer(artifact)
    held = ticket not in receiver.admitted
    local_world, local_roles = extended_receiver_scene()
    preview = receiver.preview(ticket, local_world, local_roles)
    receiver.review(ticket, "ADMIT_PLAN_ONLY", "LOCAL_STEWARD_FIXTURE_B",
                    preview.preview_digest)
    after = receiver.simulate_admitted(ticket, local_world, local_roles)
    # This is B constructing a new source-pinned method from an imported method.
    repair = next(v for v in verbs.values() if F("usable", "?0") in v.adds)
    new_action = Call(repair.id, ("wheelC", "Nina", "Nina"))
    improved_steps = (Call(outer.id, local_roles), new_action)
    improved_world = replay(local_world, improved_steps, receiver.local_catalog)
    improved = compile_trace(Trace(local_world, improved_steps,
                                   improved_world), receiver.local_catalog)
    receiver.local_catalog[improved.id] = improved
    artifact_back = export_method(improved.id, receiver.local_catalog,
                                  origin_claim="MOTIF_B_UNVERIFIED")
    # Source A remains independently authoritative over its own local state.
    return_receiver = Receiver("MOTIF_A")
    returning_ticket = return_receiver.offer(artifact_back)
    local_a = scene() | frozenset({
        F("bike", "bike3"), F("owns", "Jo", "bike3"),
        F("broken", "bike3"), F("permits", "Jo", "Jo", "bike3")
    })
    return_roles = ("Jo", "Mira", "bike1", "bike2", "bike3")
    returned_preview = return_receiver.preview(
        returning_ticket, local_a, return_roles)
    return_receiver.review(returning_ticket, "ADMIT_PLAN_ONLY",
                           "LOCAL_STEWARD_FIXTURE_A",
                           returned_preview.preview_digest)
    return_world = return_receiver.simulate_admitted(
        returning_ticket, local_a, return_roles)
    return {
        "experiment": "MOTIF-007",
        "scope": "two independent synthetic simulated worlds ONLY",
        "donor_world_exported": False,
        "packet_contains_entity_names": any(
            x in artifact for x in ("Jo", "Mira", "bike1", "bike2")),
        "source_closure_operators": len(source.catalog),
        "receiver_held_by_default": held,
        "first_local_preview_before_admission": preview.status,
        "first_local_admission": ticket in receiver.admitted,
        "recipient_after_matches_local_replay": after == replay(
            local_world, (Call(outer.id, local_roles),), receiver.local_catalog),
        "recipient_improved_macro_depth": improved.depth,
        "recipient_did_not_modify_original_graph": F("usable", "wheelA") not in local_world,
        "returned_bundle_dependency_count": len(verify_packet(artifact_back).catalog),
        "reverse_transfer_independently_admitted": returning_ticket in return_receiver.admitted,
        "return_matches_four_primitives": all(
            F("usable", f"bike{i}") in return_world for i in (1, 2, 3)),
        "receiver_claim_is_authenticated": False,
        "bundle_checksum_proves_authorship": False,
        "remote_action_performed": False
    }


if __name__ == "__main__":
    print(json.dumps(demonstrate(), indent=2))
