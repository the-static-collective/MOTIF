"""COLLECTIVE-002: proof-bound missing-link question synthesis and source re-entry.

The two inputs are *actual* COLLECTIVE-001 proof-bearing synthetic set
results. One bounded, outside-the-proof finite cross-relation remains unknown.
Only the declared relation owner can answer generated typed questions.

Research limits: 3-bit, author-controlled finite synthetic worlds; not genuine
independent agents, authenticated provenance, general language understanding
or a proof of physical-world absence.
"""
from __future__ import annotations

from copy import deepcopy
from fractions import Fraction
from hashlib import sha256
from itertools import permutations
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
for family in ("thought-025", "thought-026", "thought-027",
               "thought-028", "collective001"):
    location = str(HERE.parent / family)
    if location not in sys.path:
        sys.path.insert(0, location)

from proof_memory import ProofError, digest
from answer_weave import verify_answer

SCHEMA = "motif.collective002.missing-link-proof.v1"
OBS_SCHEMA = "motif.collective002.source-observation.v1"
RELATION = "FINITE_CROSS_MATCH"
ITEMS = tuple(range(3))
ALL_PAIRS = tuple((a, b) for a in ITEMS for b in ITEMS)
ALL_KEYS = {f"{a}:{b}" for a, b in ALL_PAIRS}
OPEN = [
    "Source-owner labels and SHA-256 checksums do not authenticate identity",
    "Separate source-owned task scopes do not prove independent authorship",
    "Absence is proved only inside a declared finite closed relation",
    "Predicted priors are developer-authored, not calibrated real-world probabilities",
    "No transfer of human-language semantics or real-world action authority",
]


def key(pair):
    if type(pair) not in (tuple, list) or len(pair) != 2:
        raise ProofError("Malformed typed relation pair")
    a, b = pair
    if type(a) is not int or type(b) is not int or a not in ITEMS or b not in ITEMS:
        raise ProofError("Cross pair outside declared 3x3 relation")
    return f"{a}:{b}"


class BridgeOwner:
    """Simulated source owner; hidden answers are not in its public contract.

    The controller is coded against contract()/ask()/recheck() only. Co-located
    Python objects are not security or information-flow isolation.
    """

    def __init__(self, source_id, truth, *, priors=None, costs=None,
                 revision=1, closed=True):
        if type(source_id) is not str or not source_id.startswith("fixture:"):
            raise ProofError("Only explicitly synthetic fixture source")
        if type(revision) is not int or revision < 1 or type(closed) is not bool:
            raise ProofError("Invalid fixture revision or scope")
        if type(truth) is not dict or set(truth) != ALL_KEYS or any(
                type(v) is not bool for v in truth.values()):
            raise ProofError("Truth fixture must contain every directed pair")
        if priors is None:
            priors = {key(p): 500 for p in ALL_PAIRS}
        if costs is None:
            costs = {key(p): 1 for p in ALL_PAIRS}
        if (type(priors) is not dict or set(priors) != ALL_KEYS
                or any(type(v) is not int or not 0 <= v <= 1000
                       for v in priors.values())
                or type(costs) is not dict or set(costs) != ALL_KEYS
                or any(type(v) is not int or not 1 <= v <= 20
                       for v in costs.values())):
            raise ProofError("Public priors/costs must cover all pairs exactly")
        self._truth = dict(truth)
        self._prior = dict(priors)
        self._cost = dict(costs)
        self._source_id = source_id
        self._revision = revision
        self._closed = closed
        self.query_count = 0
        self.recheck_count = 0

    def contract(self):
        return {
            "relation": RELATION,
            "owner_id": self._source_id,
            "revision": self._revision,
            "universe": list(ITEMS),
            "closed_domain": self._closed,
            "query_costs": dict(sorted(self._cost.items())),
            "prior_per_thousand": dict(sorted(self._prior.items())),
            "priors_validated_by_external_data": False,
            "owner_authentication_proven": False,
            "external_authority": "NONE",
        }

    def ask(self, pair):
        code = key(pair)
        self.query_count += 1
        raw = {
            "schema": OBS_SCHEMA, "relation": RELATION, "pair": list(pair),
            "owner_id": self._source_id,
            "world_revision": self._revision,
            "observation": self._truth[code],
            "query_cost": self._cost[code],
            "source_kind": "SYNTHETIC_FIXTURE_OWNER",
            "proof_of_real_world_fact": False,
        }
        raw["integrity_digest"] = digest(raw)
        return raw

    def recheck(self, receipt):
        # Rechecks source-owned truth but creates no new investigative query.
        self.recheck_count += 1
        if type(receipt) is not dict or set(receipt) != {
            "schema", "relation", "pair", "owner_id", "world_revision",
            "observation", "query_cost", "source_kind",
            "proof_of_real_world_fact", "integrity_digest"
        }:
            raise ProofError("Malformed observation receipt")
        if receipt["integrity_digest"] != digest({
            k: v for k, v in receipt.items() if k != "integrity_digest"
        }):
            raise ProofError("Observation receipt checksum invalid")
        code = key(receipt["pair"])
        if (receipt["schema"] != OBS_SCHEMA or receipt["relation"] != RELATION
                or receipt["owner_id"] != self._source_id
                or receipt["world_revision"] != self._revision
                or type(receipt["observation"]) is not bool
                or receipt["observation"] != self._truth[code]
                or receipt["query_cost"] != self._cost[code]
                or receipt["source_kind"] != "SYNTHETIC_FIXTURE_OWNER"
                or receipt["proof_of_real_world_fact"] is not False):
            raise ProofError("Observation disagrees with current source owner")
        return True


def derive_questions(left_packet, right_packet, registry, contract):
    """Invent typed cross-boundary questions from proven result masks.

    Does not accept target answers, hidden edge truth, or expected labels.
    """
    if (type(left_packet) is not dict or type(right_packet) is not dict
            or not isinstance(registry, dict) or type(contract) is not dict):
        raise ProofError("Invalid proof-bearing evidence inputs")
    _, left_task, _ = verify_answer(left_packet, registry)
    _, right_task, _ = verify_answer(right_packet, registry)
    if left_task.key == right_task.key:
        raise ProofError("Require two separately scoped source-task proofs")
    if (contract.get("relation") != RELATION
            or contract.get("universe") != list(ITEMS)
            or contract.get("external_authority") != "NONE"
            or contract.get("owner_authentication_proven") is not False
            or contract.get("priors_validated_by_external_data") is not False
            or type(contract.get("closed_domain")) is not bool
            or type(contract.get("owner_id")) is not str
            or not contract["owner_id"].startswith("fixture:")
            or type(contract.get("revision")) is not int
            or contract["revision"] < 1):
        raise ProofError("Unknown or unapproved relation contract")
    priors = contract.get("prior_per_thousand")
    costs = contract.get("query_costs")
    if (type(priors) is not dict or set(priors) != ALL_KEYS
            or any(type(v) is not int or not 0 <= v <= 1000
                   for v in priors.values())
            or type(costs) is not dict or set(costs) != ALL_KEYS
            or any(type(v) is not int or not 1 <= v <= 20
                   for v in costs.values())):
        raise ProofError("Malformed public question costs or priors")
    left = left_packet["answer"]["output_mask"]
    right = right_packet["answer"]["output_mask"]
    if any(type(v) is not int or not 0 <= v <= 7 for v in (left, right)):
        raise ProofError("Only verified three-bit source outputs")
    questions = []
    for a in ITEMS:
        if not left & (1 << a):
            continue
        for b in ITEMS:
            if not right & (1 << b):
                continue
            pair = [a, b]
            k = key(pair)
            questions.append({
                "question_schema": "motif.collective002.typed-question.v1",
                "relation": RELATION, "pair": pair,
                "human_gloss": f"Does verified left member {a} have an observed "
                               f"cross-match to verified right member {b}?",
                "left_proof_digest": left_packet["answer"]["proof_digest"],
                "right_proof_digest": right_packet["answer"]["proof_digest"],
                "relevance": "BOTH_MEMBERS_IN_INDEPENDENTLY_RECHECKED_MASKS",
                "prior_per_thousand": priors[k],
                "query_cost": costs[k],
                "not_yet_observed": True,
            })
    return questions


def policy_order(questions):
    """Known classical p/c optimal priority under independent Bernoulli model."""
    return sorted(
        questions, key=lambda q: (
            -Fraction(q["prior_per_thousand"], q["query_cost"]), tuple(q["pair"])
        )
    )


def expected_cost(order):
    """Exact expected *query cost* to first success or exhausted candidates."""
    survival = Fraction(1)
    cost = Fraction(0)
    for q in order:
        cost += survival * q["query_cost"]
        survival *= (1 - Fraction(q["prior_per_thousand"], 1000))
    return cost


def exhaustive_classical_reference(questions):
    """Separate brute-force classical control; <=5 questions by design."""
    if len(questions) > 5:
        raise ProofError("Classical exhaustive reference limited to five questions")
    if not questions:
        return [], Fraction(0)
    winner = None
    for arrangement in permutations(questions):
        score = expected_cost(arrangement)
        tie = tuple(tuple(q["pair"]) for q in arrangement)
        if winner is None or (score, tie) < (winner[0], winner[1]):
            winner = (score, tie, list(arrangement))
    return winner[2], winner[0]


def _decision(questions, receipts, contract):
    if len(receipts) > len(questions):
        raise ProofError("More answers than questions")
    observed = [x["observation"] for x in receipts]
    if True in observed:
        index = observed.index(True)
        if index != len(receipts) - 1:
            raise ProofError("Query continued after sufficient positive proof")
        return "FOUND_VERIFIED_FINITE_LINK", receipts[-1]["pair"]
    if len(receipts) == len(questions) and contract["closed_domain"]:
        return "PROVED_NO_LINK_WITHIN_DECLARED_FINITE_SCOPE", None
    return "HOLD_UNRESOLVED_BRIDGE_RELATION", None


def _finish(left_packet, right_packet, registry, contract, questions, receipts,
            budget):
    status, witness = _decision(questions, receipts, contract)
    result = {
        "schema": SCHEMA, "task": "FIND_FINITE_CROSS_MATCH",
        "question": "Does at least one proven left member have an owner-confirmed "
                    "cross-match with a proven right member?",
        "left_proof_node": deepcopy(left_packet),
        "right_proof_node": deepcopy(right_packet),
        "relation_owner_contract": deepcopy(contract),
        "candidate_questions": deepcopy(questions),
        "chosen_questions": [list(q["pair"]) for q in policy_order(questions)],
        "observations": deepcopy(receipts),
        "query_budget": budget,
        "query_cost_paid": sum(x["query_cost"] for x in receipts),
        "status": status,
        "positive_witness_pair": deepcopy(witness),
        "negative_result_is_only_finite": True,
        "answer_dependencies": [
            left_packet["answer"]["proof_digest"],
            right_packet["answer"]["proof_digest"],
        ],
        "unresolved": list(OPEN),
        "source_identity_authenticated": False,
        "independent_agent_authorship_proven": False,
        "automatic_admission": False,
        "installed": False,
        "external_authority": "NONE",
    }
    result["integrity_digest"] = digest(result)
    return result


def investigate(left_packet, right_packet, registry, owner, *, budget=None):
    """Construct a relevant question and actually query its outside owner."""
    if not isinstance(owner, BridgeOwner):
        raise ProofError("Requires declared synthetic source owner")
    contract = owner.contract()
    questions = derive_questions(left_packet, right_packet, registry, contract)
    if budget is None:
        budget = len(questions)
    if type(budget) is not int or not 0 <= budget <= len(questions):
        raise ProofError("Bad external evidence query budget")
    observations = []
    for q in policy_order(questions)[:budget]:
        answer = owner.ask(q["pair"])
        owner.recheck(answer)
        observations.append(answer)
        if answer["observation"]:
            break
    return _finish(left_packet, right_packet, registry, contract, questions,
                   observations, budget)


def verify_packet(packet, registry, owner):
    """Full evidence replay; even rehashed forged claims cannot create truth."""
    if type(packet) is not dict or packet.get("schema") != SCHEMA:
        raise ProofError("Unknown collective evidence packet")
    required = {
        "schema", "task", "question", "left_proof_node", "right_proof_node",
        "relation_owner_contract", "candidate_questions", "chosen_questions",
        "observations", "query_budget", "query_cost_paid", "status",
        "positive_witness_pair", "negative_result_is_only_finite",
        "answer_dependencies", "unresolved", "source_identity_authenticated",
        "independent_agent_authorship_proven", "automatic_admission",
        "installed", "external_authority", "integrity_digest",
    }
    if set(packet) != required or packet["integrity_digest"] != digest({
        k: v for k, v in packet.items() if k != "integrity_digest"
    }):
        raise ProofError("Payload structure or checksum changed")
    if (packet["task"] != "FIND_FINITE_CROSS_MATCH"
            or packet["relation_owner_contract"] != owner.contract()
            or packet["unresolved"] != OPEN
            or packet["source_identity_authenticated"] is not False
            or packet["independent_agent_authorship_proven"] is not False
            or packet["automatic_admission"] is not False
            or packet["installed"] is not False
            or packet["external_authority"] != "NONE"
            or packet["negative_result_is_only_finite"] is not True):
        raise ProofError("Unsupported scope, stale owner, or fake authority")
    expected = derive_questions(
        packet["left_proof_node"], packet["right_proof_node"],
        registry, owner.contract()
    )
    if packet["candidate_questions"] != expected:
        raise ProofError("An evidence-based question was changed or omitted")
    order = [list(x["pair"]) for x in policy_order(expected)]
    if packet["chosen_questions"] != order:
        raise ProofError("Question policy or ordering was changed")
    if (type(packet["query_budget"]) is not int
            or not 0 <= packet["query_budget"] <= len(order)
            or type(packet["observations"]) is not list
            or len(packet["observations"]) > packet["query_budget"]):
        raise ProofError("Query count or budget was altered")
    for index, receipt in enumerate(packet["observations"]):
        if receipt.get("pair") != order[index]:
            raise ProofError("Observation not bound to selected question")
        owner.recheck(receipt)
    status, witness = _decision(expected, packet["observations"], owner.contract())
    if (packet["status"] != status
            or packet["positive_witness_pair"] != witness
            or packet["query_cost_paid"] != sum(
                r["query_cost"] for r in packet["observations"]
            )
            or packet["answer_dependencies"] != [
                packet["left_proof_node"]["answer"]["proof_digest"],
                packet["right_proof_node"]["answer"]["proof_digest"],
            ]):
        raise ProofError("Derived conclusion or evidence chain does not match")
    # The record must not silently stop before its declared budget absent
    # a discovered positive link. With no relevant candidates zero is valid.
    if (status != "FOUND_VERIFIED_FINITE_LINK"
            and len(packet["observations"]) != packet["query_budget"]):
        raise ProofError("Unjustified premature termination")
    return True


def reenter(packet, registry, owner):
    before = owner.query_count
    verify_packet(packet, registry, owner)
    if owner.query_count != before:
        raise ProofError("Re-entry issued unexpected new evidence questions")
    return {
        "status": "SCOPED_COLLECTIVE_RESULT_RECHECKED",
        "answer_node": deepcopy(packet),
        "new_source_queries": 0,
        "owner_reverification_performed": True,
        "full_parent_proof_reverification_performed": True,
    }


def synthetic_owner(seed, *, costs=None, priors=None, true_pairs=None,
                    closed=True, revision=1):
    """Evaluator-created fixture; controller never receives the generating seed."""
    if priors is None:
        priors = {
            key(p): (650 if p[0] == p[1] else (330 if p[0] < p[1] else 160))
            for p in ALL_PAIRS
        }
    if costs is None:
        costs = {
            key(p): 1 + (p[0] + 2 * p[1]) % 3
            for p in ALL_PAIRS
        }
    if true_pairs is not None:
        specified = {key(p) for p in true_pairs}
        truth = {key(p): key(p) in specified for p in ALL_PAIRS}
    else:
        rng = random.Random(seed)
        truth = {key(p): rng.randrange(1000) < priors[key(p)] for p in ALL_PAIRS}
    return BridgeOwner(f"fixture:world-{seed}", truth, costs=costs,
                       priors=priors, closed=closed, revision=revision)


def reference_evaluator_only(owner, questions):
    """Evaluator can see hidden truth; never pass this to the query planner."""
    return any(owner._truth[key(q["pair"])] for q in questions)


def evaluate_fixed_order(owner, questions, order):
    """Equal-information classical comparator, same owner ask interface."""
    spent, count, first = 0, 0, None
    for q in order:
        observed = owner.ask(q["pair"])
        owner.recheck(observed)
        spent += observed["query_cost"]
        count += 1
        if observed["observation"]:
            first = observed["pair"]
            break
    return {
        "queries": count, "query_cost_paid": spent,
        "found": first is not None,
        "proved_absent_in_declared_finite_scope": first is None,
    }
