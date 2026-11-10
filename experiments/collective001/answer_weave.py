"""COLLECTIVE-001: proof-carrying, relevance-limited answer nodes and re-entry.

This is a narrow synthetic 3-bit set research projection over the *existing*
THOUGHT-027/028 independently rechecked proof memory. It cannot certify
arbitrary natural-language answers or real-world assertions.

The packet contains public proof/evidence artifacts, never hidden model
reasoning or private chain-of-thought. Hashes check integrity, not origin.
"""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
for family in ("thought-025", "thought-026", "thought-027", "thought-028"):
    path = str(HERE.parent / family)
    if path not in sys.path:
        sys.path.insert(0, path)

from specimens import Specimen, public_brief, independent_target
from abstraction import evaluate_reply
from proof_memory import ProofError, digest
from weave import EvidenceStore, investigate

SCHEMA = "motif.collective001.proof-carrying-answer.v1"
KIND = "SCOPED_SYNTHETIC_3BIT_RESULT"
OPEN = (
    "External-world truth and source identity not established",
    "No automatic inference of unfamiliar natural-language task semantics",
    "No automatic permission, installation, publication, or external action",
)


def _raw(task, inputs):
    if not isinstance(task, Specimen) or not task.representable:
        raise ProofError("Only source-owned, representable synthetic tasks")
    fields = [key for key, _ in task.fields]
    if type(inputs) is not dict or set(inputs) != set(fields):
        raise ProofError("Inputs must exactly match source-task fields")
    if any(type(inputs[key]) is not int or not 0 <= inputs[key] <= 7
           for key in fields):
        raise ProofError("Only exactly bounded 3-bit integer inputs")
    return {key: inputs[key] for key in fields}


def _lineage(store, card):
    """Minimal ordered ancestry: evidence is not duplicated as fake votes."""
    sources, derived = set(), []
    visiting, visited = set(), set()

    def visit(ident):
        if ident in visiting:
            raise ProofError("Cyclic proof ancestry")
        if ident in visited:
            return
        visiting.add(ident)
        if ident in store.sources:
            sources.add(ident)
        elif ident in store.derived:
            item = store.derived[ident]
            for parent in item["parent_proof_digests"]:
                visit(parent)
            derived.append(ident)
        else:
            raise ProofError("Missing proof ancestor")
        visiting.remove(ident)
        visited.add(ident)

    visit(card["proof_digest"])
    return (sorted(sources), derived)


def _minimal_memory(store, card):
    """Reconstruct a portable proof store with no unrelated task cards."""
    store.verify_all()
    source_ids, derived_ids = _lineage(store, card)
    complete = store.export()
    complete["source_cards"] = [
        deepcopy(store.sources[i]) for i in source_ids
    ]
    complete["derived_cards"] = [
        deepcopy(store.derived[i]) for i in derived_ids
    ]
    complete["integrity_digest"] = digest({
        k: v for k, v in complete.items() if k != "integrity_digest"
    })
    # Reverification is mandatory even for our own projection.
    EvidenceStore.load(complete, store.registry)
    return complete


def _evidence_nodes(store, card):
    source_ids, derived_ids = _lineage(store, card)
    nodes = []
    for ident in source_ids:
        p = store.sources[ident]
        nodes.append({
            "type": "SCOPED_SOURCE_PROOF",
            "digest": ident,
            "task_key": p["task_key"],
            "source_relation": p["relation"],
            "parents": [],
            "not_independent_world_witness": True,
        })
    for ident in derived_ids:
        p = store.derived[ident]
        nodes.append({
            "type": "COMPOSED_SCOPED_PROOF",
            "digest": ident,
            "task_key": p["task_key"],
            "parents": p["parent_proof_digests"],
            "finite_cases": p["independent_evaluation"]["correct"],
            "independent_runtime_cases": p["trusted_template_evaluation"]["correct"],
            "not_independent_world_witness": True,
        })
    return nodes


def _answer(task, card, inputs):
    values = _raw(task, inputs)
    proposed = evaluate_reply(task, card["proposal"], values)
    checked = independent_target(task, values)
    if proposed != checked:
        raise ProofError("Claim fails independent task-owned case check")
    return {
        "kind": KIND,
        "input": values,
        "output_mask": proposed,
        "owner_oracle_output_mask": checked,
        "rule": deepcopy(card["proposal"]),
        "finite_oracle_cases_verified": card["independent_evaluation"]["correct"],
        "independent_template_cases_verified": card["trusted_template_evaluation"]["correct"],
        "proof_digest": card["proof_digest"],
        "claim_about_reality": False,
    }


def _check_inquiry(task, card, inquiry):
    if type(inquiry) is not dict or inquiry.get("receipt_digest") != digest({
        k: v for k, v in inquiry.items() if k != "receipt_digest"
    }):
        raise ProofError("Broken or missing inquiry receipt")
    if inquiry.get("task") != task.key or (
        inquiry.get("status") != "REVIEW_SCOPED_CANDIDATE_NOT_INSTALLED"
    ) or inquiry.get("installed") is not False:
        raise ProofError("Uncertified inquiry")
    if inquiry.get("proposal") != card["proposal"]:
        raise ProofError("Answer not linked to inquiry proposal")
    if sorted(set(inquiry.get("source_proof_digests", []))) != sorted(
        card["parent_proof_digests"]
    ):
        raise ProofError("Answer not linked to stated source evidence")
    observations = inquiry.get("development_observations")
    if type(observations) is not list or len(observations) < 2 or (
        inquiry.get("development_queries") != len(observations)
    ):
        raise ProofError("Inconsistent development trace")
    # Historical probe selection is *reported*, not fully re-executed. Values
    # and scope are independently rechecked on re-entry.
    for event in observations:
        values = _raw(task, event["raw_inputs"])
        if independent_target(task, values) != event["source_owner_oracle_observed"]:
            raise ProofError("Past development observation no longer holds")
    return True


def _seal(task, store, card, inquiry, inputs):
    memory = _minimal_memory(store, card)
    packet = {
        "schema": SCHEMA,
        "question_scope": public_brief(task),
        "task_key": task.key,
        "task_spec_sha256": digest(public_brief(task)),
        "answer": _answer(task, card, inputs),
        "relevant_evidence_nodes": _evidence_nodes(store, card),
        "inquiry_receipt": deepcopy(inquiry),
        "proof_memory": memory,
        "unresolved": list(OPEN),
        "assertion_origin_authenticated": False,
        "automatic_admission": False,
        "installed": False,
        "external_authority": "NONE",
    }
    packet["cache_key"] = digest({
        "scope": packet["task_spec_sha256"],
        "input": packet["answer"]["input"],
        "kind": KIND,
    })
    packet["integrity_digest"] = digest(packet)
    return packet


def first_answer(task, store, inquiry, inputs):
    """Promote only a fully checked inquiry to a *review-only* answer node."""
    if not isinstance(store, EvidenceStore):
        raise ProofError("Requires actual THOUGHT-028 evidence store")
    if not isinstance(task, Specimen) or not task.representable:
        raise ProofError("Unsupported new-task semantics")
    if type(inquiry) is not dict or inquiry.get("task") != task.key:
        raise ProofError("Inquiry for a different task")
    if inquiry.get("status") != "REVIEW_SCOPED_CANDIDATE_NOT_INSTALLED":
        raise ProofError("A HOLD is not a proof")
    # Existing THOUGHT-028 independently rechecks source, runtime and ancestry.
    card = store.add_derived(task, inquiry)
    return _seal(task, store, card, inquiry, inputs)


def verify_answer(packet, registry):
    """Never trust cached status or a rehashed packet without owner replay."""
    if type(packet) is not dict or packet.get("schema") != SCHEMA:
        raise ProofError("Unexpected answer schema")
    required = {"schema", "question_scope", "task_key", "task_spec_sha256",
                "answer", "relevant_evidence_nodes", "inquiry_receipt",
                "proof_memory", "unresolved", "assertion_origin_authenticated",
                "automatic_admission", "installed", "external_authority",
                "cache_key", "integrity_digest"}
    if set(packet) != required or packet["integrity_digest"] != digest({
        k: v for k, v in packet.items() if k != "integrity_digest"
    }):
        raise ProofError("Answer packet integrity mismatch")
    if (packet["assertion_origin_authenticated"] is not False or
        packet["automatic_admission"] is not False or
        packet["installed"] is not False or
        packet["external_authority"] != "NONE" or
        packet["unresolved"] != list(OPEN)):
        raise ProofError("Cannot silently upgrade research-only authority")
    task = registry.get(packet["task_key"])
    if not isinstance(task, Specimen) or not task.representable:
        raise ProofError("Source task unavailable")
    scope = public_brief(task)
    if packet["question_scope"] != scope or packet["task_spec_sha256"] != digest(scope):
        raise ProofError("Stale task scope: re-investigate")
    store = EvidenceStore.load(packet["proof_memory"], registry)
    identifier = packet["answer"].get("proof_digest")
    card = store.derived.get(identifier)
    if card is None or card["task_key"] != task.key:
        raise ProofError("Unverified exact-task proof")
    if packet["relevant_evidence_nodes"] != _evidence_nodes(store, card):
        raise ProofError("Wrong evidence ancestry")
    _check_inquiry(task, card, packet["inquiry_receipt"])
    if packet["answer"] != _answer(task, card, packet["answer"]["input"]):
        raise ProofError("Answer differs from independently replayed rule")
    if packet["cache_key"] != digest({
        "scope": packet["task_spec_sha256"],
        "input": packet["answer"]["input"],
        "kind": KIND,
    }):
        raise ProofError("Cache key no longer matches actual query")
    return store, task, card


def reenter(packet, registry, *, inputs=None):
    """No fresh *discovery* questions; proof/owner verification still runs."""
    store, task, card = verify_answer(packet, registry)
    if inputs is None:
        result = deepcopy(packet)
    else:
        result = _seal(task, store, card, packet["inquiry_receipt"], inputs)
    return {
        "status": "SCOPED_PROOF_REVERIFIED_NO_NEW_INQUIRY",
        "answer_node": result,
        "new_development_queries": 0,
        "new_inference_or_model_calls": 0,
        "full_owner_proof_recheck_still_required": True,
    }


def investigate_new_task(packet, registry, target):
    """A previous proof is only a candidate for an unfamiliar task."""
    store, old, _ = verify_answer(packet, registry)
    if not isinstance(target, Specimen) or target.key == old.key:
        raise ProofError("New task must have a distinct source-owned identity")
    store.add_task(target)
    return investigate(target, store, mode="retrieved")
