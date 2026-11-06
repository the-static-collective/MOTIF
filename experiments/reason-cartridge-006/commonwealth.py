"""REASON-006: federate independently owned reasoning steps without voting.

A source-pinned, read-only synthetic council. Every accepted contribution is
replayed against source-owned proof/evidence semantics. No method inherits the
authority of any source or teacher. All outcomes are local graph fixtures.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha1, sha256
from pathlib import Path
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
PINS = {
    "005/engine.py": "27df6077af82aacdbbc1d6f7c46bb0c8ff1b7519",
    "005/critic.py": "3a3cd556c7ca94982ae6e28afcc890381eb3d799",
    "003/pupil.py": "5534b0b82d33b6c81776058170f091038d2ae9b2",
}
DOGRAM_SHA = "551b5f9df18f17ec69b452ddcdff01718e0ff771"
SOURCE_SCHEMA = "motif.reason.commonwealth.v1"
METHOD_SCHEMA = "motif.reason.commonwealth-method.v1"
BUDGET = 1
SAFE = re.compile(r"^[A-Za-z0-9_.:-]{1,96}$")


class HOLD(ValueError):
    pass


def sha(obj):
    return sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"),
                             ensure_ascii=True, allow_nan=False).encode("utf8")).hexdigest()


def pins():
    for name, expected in PINS.items():
        generation, filename = name.split("/")
        target = ROOT / ("reason-cartridge-" + generation) / filename
        raw = target.read_bytes()
        actual = sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        if actual != expected:
            raise HOLD("Source owner changed: " + name)
    return dict(sorted(PINS.items()))


pins()
# Existing 005 and 003 adapters run under their own pinned contracts.
sys.path.append(str(ROOT / "reason-cartridge-005"))
sys.path.append(str(ROOT / "reason-cartridge-003"))
from engine import Objection, ToyOwner, Model, owner4, stress, validate as validate_005  # noqa: E402
from critic import Critic  # noqa: E402
from pupil import verify_native, HOLD as FOREIGN_HOLD  # noqa: E402


def exact_proof(q):
    raw = owner4.make(q, false_negative_cost=8.0,
                      false_positive_cost=3.0, question_cost=0.1)
    doc = owner4.validate(raw)
    proof = doc["proof_certificate"]
    if proof:
        if not owner4.check_certificate(q, {"certificate": proof}):
            raise HOLD("Owner proof failed independent check")
    return doc


class Ledger:
    """Novelty is exact signed-by-source-semantics *change in validated output*.

    This is NOT a causal-Shapley score or an accuracy/confidence vote. The
    ledger never promotes proposals to fact without an owner witness.
    """
    def __init__(self):
        self.seen = set()
        self.events = []

    def add(self, role, kind, basis, effect, verified):
        if not verified:
            raise HOLD("Council cannot score unverified propositions")
        fingerprint = sha({"role": role, "kind": kind, "basis": basis})
        new = fingerprint not in self.seen
        if new:
            self.seen.add(fingerprint)
        event = {"role": role, "kind": kind, "fingerprint": fingerprint,
                 "basis": basis, "effect": effect,
                 "new_validated_contribution": bool(new),
                 "marginal_new_fact_count": int(bool(new) and kind == "SOURCE_REVISION"),
                 "score": int(new), "real_world_authority": False}
        self.events.append(event)
        return event

    def repeat(self, event):
        return self.add(event["role"], event["kind"], event["basis"], event["effect"], True)

    def summary(self):
        by_role = {}
        for e in self.events:
            by_role[e["role"]] = by_role.get(e["role"], 0) + e["score"]
        return {"contributions": by_role,
                "novel": sum(x["score"] for x in self.events),
                "duplicates_rejected": sum(not x["new_validated_contribution"] for x in self.events),
                "new_source_facts": sum(x["marginal_new_fact_count"] for x in self.events),
                "no_vote_on_truth": True}


def independent_specimen(q, ref):
    """Build the ORIGINAL Dogram ablation question from a fully known graph."""
    if not isinstance(q, owner4.Inquiry) or not SAFE.fullmatch(ref or ""):
        raise HOLD("No exact source-owned foreign question")
    definite, possible, conflicted, unknown = owner4.evidence(q)
    if (not q.closed_scope or conflicted or unknown or q.source != "S"
            or q.target != "T"):
        raise HOLD("Partial/open world cannot masquerade as complete Dogram graph")
    raw_edges = sorted(definite | {q.removed})
    graph = {"nodes": sorted(q.nodes), "edges": [list(e) for e in raw_edges]}
    return {"schema": "dogram.specimen/v0", "specimen_id": ref,
            "operator": "ablate", "operator_version": 1,
            "inputs": {"graph": graph,
                       "target": {"kind": "edge", "source": q.removed[0],
                                  "target": q.removed[1]},
                       "requested_targets": [["S","T"]]},
            "assumptions": [],
            "metadata": {"teacher_repo": "the-static-collective/Dogram",
                         "teacher_commit": DOGRAM_SHA,
                         "synthetic_only": True,
                         "not_an_independent_world_witness": True}}


def foreign_crosscheck(q, specimen, receipt, reference):
    expected = independent_specimen(q, reference)
    if specimen != expected:
        raise HOLD("Native foreign result is for a different source graph")
    try:
        native = verify_native(specimen, receipt)
    except FOREIGN_HOLD as exc:
        raise HOLD("Foreign source refused or returned unbound evidence") from exc
    local = owner4.decide(q)
    if local["status"] not in ("PROVED_REACHABLE", "PROVED_UNREACHABLE"):
        raise HOLD("Cannot corroborate unsettled graph world")
    local_yes = local["status"] == "PROVED_REACHABLE"
    if native != local_yes:
        raise HOLD("Foreign algorithm and local proof disagree")
    return {"algorithm": "NATIVE_DOGRAM_ABLATE",
            "source_commit": DOGRAM_SHA, "native_receipt_hash": sha(receipt),
            "native_reachable": native,
            "corroborates_same_declared_graph_not_world": True,
            "does_not_count_as_independent_observed_fact": True,
            "source_authority_transferred": False}


@dataclass
class LocalObservationOwner:
    """An opt-in fixture for edges not previously observed, never live data."""
    source_id: str
    hidden_edges: dict

    def __post_init__(self):
        if (not isinstance(self.source_id, str) or not SAFE.fullmatch(self.source_id)
                or not isinstance(self.hidden_edges, dict)
                or not self.hidden_edges or any(
                    not isinstance(e, tuple) or len(e) != 2 or type(b) is not bool
                    for e, b in self.hidden_edges.items()
                )):
            raise HOLD("Unknown local synthetic fixture source")
        self.calls = 0

    def reveal(self, q, edge):
        if self.calls >= BUDGET or edge not in self.hidden_edges:
            raise HOLD("Missing synthetic owner permission or exhausted review")
        if edge not in owner4.evidence(q)[3]:
            raise HOLD("Cannot erase prior witnesses")
        self.calls += 1
        stance = "PRESENT" if self.hidden_edges[edge] else "ABSENT"
        receipt = owner4.observe(q, edge, stance,
                                 f"{self.source_id}-synthetic-{self.calls}")
        before, after = receipt["before"], receipt["after"]
        if before != owner4.digest(owner4.encode(q)):
            raise HOLD("Owner changed during observation")
        updated = receipt["updated_inquiry"]
        if after != owner4.digest(owner4.encode(updated)):
            raise HOLD("Source-owned observation not reproducible")
        return updated, {"schema": "motif.reason.local-observation.v1",
                         "old": before, "new": after, "edge": list(edge),
                         "observed_stance": stance,
                         "source": self.source_id, "fixture_only": True,
                         "external_observation_performed": False}


def _challenge(q, proof, model, owner, ledger):
    flag = proof["refutation_program"]
    status = proof["conclusion"]
    if status == "PROVED_REACHABLE":
        witness = proof["proof_certificate"]["nodes"]
        choices = tuple(reversed(tuple(zip(witness, witness[1:]))))
        # Last-to-first witness challenge, independent of hidden owner truth.
        # The min-cut remains the source-owned fragility bound.
        if not choices:
            raise HOLD("Missing native fragility witness")
        kind = "RETRACT_PRESENT"
    elif status == "PROVED_UNREACHABLE":
        if flag["kind"] != "REOPEN_BLOCKED_ROUTE":
            return q, "HOLD_NO_LOCAL_COUNTEREXAMPLE"
        impossible = set(q.universe) - owner4.evidence(q)[1] - {q.removed}
        choices = tuple(e for e in (tuple(x) for x in
                          flag["counterexample_program"]["premises_to_revise"])
                        if e in impossible)
        if not choices:
            return q, "HOLD_NO_REVIEWABLE_ABSENCE"
        kind = "REVIEW_ABSENCE"
    else:
        raise HOLD("Challenge cannot assume unresolved result")

    candidates = tuple(Objection(f"c-{i}-{status}", kind, (edge,))
                       for i, edge in enumerate(choices[:3]))
    # Use source-owner 005 Critic for its proof challenge and budgeted review.
    critic = Critic(q, candidates, model=model, budget=BUDGET)
    proposals = critic.plan()
    for response in proposals["defenses"]:
        doc = validate_005(json.dumps(response["cartridge"]))
        ledger.add("OBJECTION", "DEFENSE",
                   {"cartridge": doc["checksum_sha256"],
                    "alternate_proof": doc["outcome"]["rebuttal"]},
                   "A_SPECIFIC_OBJECTION_CANNOT_DEFEAT_THIS_PROOF", True)

    if not proposals["chosen"]:
        return q, ("STOP_NO_MATERIAL_INQUIRY" if not proposals["material"]
                   else "STOP_QUERY_COST_OR_BUDGET")

    chosen = next(c for c in candidates
                  if c.reference == proposals["chosen"]["objection"])
    outcome = stress(q, chosen)
    if outcome["classification"] != "MATERIAL_OBJECTION":
        raise HOLD("Source-owned objection is not material")
    ledger.add("OBJECTION", "MATERIAL",
               {"original_conclusion":status, "objection":list(chosen.edges),
                "kind": chosen.kind},
               "WOULD_INVALIDATE_PROOF_IF_TRUE_NOT_CONFIRMED", True)

    if not isinstance(owner, ToyOwner):
        return q, "HOLD_EXTERNAL_SOURCE_NOT_CONNECTED"

    result = Critic(q, (chosen,), model=model, budget=BUDGET).run(owner)
    if result["status"] not in ("CORRECTION","OWNER_DEFENSE"):
        return q, "HOLD_OWNER_DID_NOT_REVIEW"
    record = validate_005(json.dumps(result["outcome_cartridge"]))
    updated = owner4.decode(record["revised_inquiry"])
    ledger.add("SOURCE_OWNER", "SOURCE_REVISION",
               {"receipt": sha(record["synthetic_owner_receipt"]),
                "updated": owner4.digest(owner4.encode(updated))},
               "A_SYNTHETIC_OWNER_REVIEWED_ONE_PREMISE", True)
    ledger.add("OBJECTION", result["status"],
               {"cartridge":record["checksum_sha256"]},
               "CORRECTED_PROOF" if result["status"] == "CORRECTION"
               else "OBJECTION_REFUTED_BY_NEW_SOURCE_REVIEW", True)
    return updated, result["status"]


def _question(q, proof, owner, ledger):
    flag = proof["refutation_program"]
    if flag["kind"] == "HOLD_UNCERTAIN":
        return q, "STOP_DECLARED_QUERY_COST"
    if flag["kind"] != "OBSERVE_DISCRIMINATING_EDGE":
        return q, "HOLD_CONFLICT_OR_INSUFFICIENT_INFORMATION"
    edge = tuple(flag["edge"])
    ledger.add("QUESTION", "PROPOSE",
               {"source": proof["premises"]["source_evidence_hash"],
                "edge": list(edge), "expected_cost_model":
                    proof["refutation_program"]["inquiry_cost_model"]["cost_of_omission"]},
               "A_CONSEQUENTIAL_QUESTION_NOT_YET_ANSWERED", True)
    if not isinstance(owner, LocalObservationOwner):
        return q, "HOLD_SOURCE_OBSERVATION_NOT_AUTHORIZED"
    updated, receipt = owner.reveal(q, edge)
    ledger.add("SOURCE_OWNER", "SOURCE_REVISION",
               {"receipt": sha(receipt), "updated": owner4.digest(owner4.encode(updated))},
               "ONE_NEW_LOCAL_FIXTURE_OBSERVATION", True)
    return updated, "QUESTION_RESOLVED_BY_FIXTURE"


def run_council(q, *, name, model=Model(), source=None, native=None):
    """Four specialists plus optional original Dogram, each bounded by owner."""
    pins()
    if not isinstance(q, owner4.Inquiry) or not SAFE.fullmatch(name or ""):
        raise HOLD("Unrecognized bounded council case")
    if not isinstance(model, Model):
        raise HOLD("Invalid reasoning economy")
    ledger = Ledger()
    old = exact_proof(q)
    ledger.add("PROOF", "SOURCE_BOUND_CONCLUSION",
               {"evidence":old["premises"]["source_evidence_hash"],
                "conclusion":old["conclusion"],
                "certificate":old["proof_certificate"]},
               old["conclusion"], True)
    if native is not None:
        if not isinstance(native, tuple) or len(native) != 2:
            raise HOLD("Native Dogram requires exact specimen+receipt")
        check = foreign_crosscheck(q, native[0], native[1], name + "-dogram")
        ledger.add("DOGRAMAUDIT", "INDEPENDENT_METHOD_CROSSCHECK",
                   check, "SAME_MATH_SEPARATE_IMPLEMENTATION_NOT_NEW_EVIDENCE",True)

    current=q
    if old["conclusion"] in ("PROVED_REACHABLE","PROVED_UNREACHABLE"):
        current,reason=_challenge(q,old,model,source,ledger)
    elif old["conclusion"]=="UNKNOWN":
        current,reason=_question(q,old,source,ledger)
    else:
        reason="HOLD_OPEN_WORLD_OR_UNPROVED"

    after=exact_proof(current)
    if current != q:
        ledger.add("PROOF", "REVISED_SOURCE_CONCLUSION",
                   {"evidence":after["premises"]["source_evidence_hash"],
                    "conclusion":after["conclusion"],
                    "certificate":after["proof_certificate"]},
                   after["conclusion"],True)
    # Loop sentinel receives duplicate proof, does not count as discovery.
    first=ledger.events[0]
    repeated=ledger.repeat(first)
    if repeated["new_validated_contribution"] or repeated["score"] != 0:
        raise HOLD("Loop sentinel failed")
    return {"schema": SOURCE_SCHEMA,
            "case":name, "source_revision": owner4.REVISION,
            "owner_blobs":pins(), "original_evidence_digest":
                old["premises"]["source_evidence_hash"],
            "before":old["conclusion"], "after":after["conclusion"],
            "reason_for_stop":reason, "ledger":ledger.events,
            "marginal":ledger.summary(), "source_witnesses_changed":current!=q,
            "final_witness":after["proof_certificate"],
            "external_actions":False, "real_world_authority":False}
