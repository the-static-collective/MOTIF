"""MOTIF NEXT-STEP-001: ask the next relevant question, execute safe bounded
local work, and show the result. Research adapter for synthetic witness evidence.

This is a finite typed action registry, NOT general natural-language question
understanding, not evidence acquisition, and not an autonomous external agent.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
from itertools import product
from pathlib import Path
from typing import Any
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'witnesschain001'))
from witnesschain import (
    State, HYPOTHESES, READINGS, _likelihood, challenge_reference,
    fir_receipt, propose,
)

QUESTIONS = frozenset({'absolute_polarity', 'primary_audit_alignment'})
# This executable does NOT accept arbitrary code, shell commands or network URLs.
LOCAL_ACTIONS = frozenset({'ANSWER_RELATIVE', 'TEST_SYMMETRY', 'DESIGN_PROBE',
                           'CHALLENGE_REFERENCE', 'COUNT_EVIDENCE'})


@dataclass(frozen=True)
class Goal:
    question: str
    intended_use: str = 'understand the limits of the evidence'
    budget: int = 5
    max_steps: int = 2
    inquiry_budget: int = 4  # hypothetical probe budget, NEVER spent by this adapter
    allowed_inquiries: frozenset[str] = frozenset({'NEW_TRIPLET', 'VERIFY_EXISTING'})

    def __post_init__(self):
        if (self.question not in QUESTIONS or not self.intended_use
                or type(self.budget) is not int or self.budget < 0
                or type(self.max_steps) is not int or not 1 <= self.max_steps <= 3
                or type(self.inquiry_budget) is not int or self.inquiry_budget < 0
                or not self.allowed_inquiries <= {'NEW_TRIPLET', 'VERIFY_EXISTING'}):
            raise ValueError('undeclared question, budget, horizon or inquiry permissions')


@dataclass(frozen=True)
class Candidate:
    question: str
    action: str
    reason: str
    relevance: int
    cost: int
    expected_information_bits: float = 0.0
    side_effect: str = 'NONE'
    epistemic_status: str = 'I_PROPOSAL'

    def __post_init__(self):
        if (not self.question or not self.reason or not 1 <= self.relevance <= 10
                or type(self.cost) is not int or self.cost < 0
                or self.expected_information_bits < 0):
            raise ValueError('invalid proposed question/action')


def fingerprint(state: State) -> str:
    # Hash is an inspectable change detector, NOT authenticity or identity proof.
    # Canonicalize set-valued fields so receipt IDs do not depend on PYTHONHASHSEED.
    canonical = {
        'accepted': [asdict(event) for event in state.accepted],
        'truth_receipts': [asdict(r) for r in state.truth_receipts],
        'seen': sorted(state.seen),
        'holds': list(state.holds),
    }
    return sha256(json.dumps(canonical,sort_keys=True,default=str,
                             separators=(',', ':')).encode('utf8')).hexdigest()[:20]


def orient(state: State, goal: Goal) -> dict:
    """Separate knowable-under-model, held, and unidentifiable quantities."""
    absolute = state.decision('absolute_polarity')
    relative = state.decision('primary_audit_alignment')
    known = []
    held = []
    if relative['status'] == 'I_RELATIVE_MODEL_ONLY':
        known.append('relative primary/audit alignment, conditional on model')
    else:
        held.append('relative alignment at declared confidence')
    if absolute['status'] == 'I_CONDITIONAL_ON_FIXTURE_REFERENCE':
        known.append('absolute polarity conditional on unverified fixture reference')
    elif absolute['status'] == 'HOLD_GLOBAL_FLIP_SYMMETRY':
        held.append('absolute polarity is unidentifiable from ungrounded pairs/triplets')
    else:
        held.append('absolute polarity below requested confidence')
    return {
        'requested_question': goal.question,
        'requested_answer': absolute if goal.question == 'absolute_polarity' else relative,
        'known_under_declared_model': known,
        'unknown_or_unjustified': held,
        'possible_next_evidence': 'externally authenticated reference would be required to ground absolute polarity',
        'authenticity_verified': False,
        'ledger_events': len(state.accepted),
        'assumed_reference_count': len(state.truth_receipts),
        'evidence_digest': fingerprint(state),
    }


def nominate(state: State, goal: Goal, excluded: frozenset[str] = frozenset()) -> tuple[Candidate, ...]:
    """Typed finite candidate generator. Future NLP suggestions must pass same gate."""
    if not excluded <= LOCAL_ACTIONS:
        raise ValueError('excluded actions must belong to local registry')
    absolute = state.decision('absolute_polarity')
    relative = state.decision('primary_audit_alignment')
    candidates = []
    if (goal.question == 'absolute_polarity'
            and relative['status'] == 'I_RELATIVE_MODEL_ONLY'):
        candidates.append(Candidate(
            'What useful relationship can we answer now, without assuming absolute truth?',
            'ANSWER_RELATIVE', 'The narrower question is identifiable even when the original is not.',
            8 if state.truth_receipts else 10, 1))
    if absolute['status'] == 'HOLD_GLOBAL_FLIP_SYMMETRY':
        candidates.append(Candidate(
            'Could any number of ordinary independent triplets resolve the ambiguity?',
            'TEST_SYMMETRY', 'Exact finite-model counterexample clarifies which uncertainty cannot be reduced by repetition.',
            9, 1))
        candidates.append(Candidate(
            'Which permitted verification would most reduce uncertainty next?',
            'DESIGN_PROBE', 'Select a budget-aware hypothetical inquiry; obtaining external evidence is separate.',
            8, 1))
    elif absolute['status'] == 'I_CONDITIONAL_ON_FIXTURE_REFERENCE' and state.truth_receipts:
        candidates.append(Candidate(
            'What would remain justified if the declared reference were challenged?',
            'CHALLENGE_REFERENCE', 'Stress-test an assumed root without modifying the original ledger.',
            10, 1))
    if goal.question == 'primary_audit_alignment' and relative['status'] != 'I_RELATIVE_MODEL_ONLY':
        candidates.append(Candidate(
            'Which permitted synthetic evidence check could reduce the unresolved model uncertainty?',
            'DESIGN_PROBE', 'Current relative question is not yet supported.',
            8, 1))
    candidates.append(Candidate(
        'How many distinct evidence events and assumed references support this orientation?',
        'COUNT_EVIDENCE', 'Recount exact finite evidence, not the truth of the sources.',
        3, 1))
    return tuple(c for c in candidates if c.action not in excluded)


def rank(candidates: tuple[Candidate, ...], budget: int) -> tuple[Candidate, ...]:
    """Declared relevance-first bounded policy. A simple classical control."""
    if budget < 0:
        raise ValueError('negative budget')
    # A future language generator cannot grant itself tool authority or relabel
    # an effectful tool as a harmless question. The trusted dispatcher has the
    # final fixed allowlist as a second, independent boundary.
    choices = [c for c in candidates if c.cost <= budget and c.action in LOCAL_ACTIONS
               and c.side_effect == 'NONE' and c.epistemic_status == 'I_PROPOSAL']
    # Cost breaks ties, so the policy is deterministic and inspectable.
    return tuple(sorted(choices, key=lambda c: (-c.relevance, -c.expected_information_bits,
                                                 c.cost, c.action)))


def _execute(state: State, action: str, goal: Goal, budget: int) -> dict:
    """Only allowlisted read-only operations. No user-provided function execution."""
    if action not in LOCAL_ACTIONS:
        raise PermissionError('unregistered action must not execute')
    if action == 'ANSWER_RELATIVE':
        return {'kind': 'MODEL_ESTIMATE', 'result': state.decision('primary_audit_alignment'),
                'truth_status': 'I_CONDITIONAL_MODEL', 'new_evidence': False}
    if action == 'TEST_SYMMETRY':
        max_difference = 0.0
        comparisons = 0
        for bits in HYPOTHESES:
            inverted = tuple(1-x for x in bits)
            for readings in product(READINGS, repeat=3):
                discrepancy = abs(_likelihood(bits, readings)
                                  - _likelihood(inverted, readings))
                max_difference = max(max_difference, discrepancy)
                comparisons += 1
        return {'kind':'EXHAUSTIVE_FINITE_CHECK', 'pairs_checked':comparisons,
                'max_likelihood_discrepancy':max_difference,
                'result':'GLOBAL_FLIP_INVARIANCE_VERIFIED_IN_DECLARED_MODEL' if max_difference < 1e-12
                         else 'INVARIANCE_COUNTEREXAMPLE_FOUND',
                'external_world_proof':False,'new_evidence':False}
    if action == 'DESIGN_PROBE':
        proposal = propose(state, goal.allowed_inquiries, goal.inquiry_budget)
        return {'kind':'HYPOTHETICAL_INQUIRY_DESIGN',
                'result':asdict(proposal),
                'status':'PROPOSAL_NOT_EXECUTED',
                'truth_attestation_collected':False,'new_evidence':False}
    if action == 'CHALLENGE_REFERENCE':
        if not state.truth_receipts:
            return {'kind':'COUNTERFACTUAL','status':'HOLD_NO_REFERENCE'}
        receipt = state.truth_receipts[0]
        counterfactual = challenge_reference(state,receipt.event,
                                              'test premise rather than assume infallibility')
        return {'kind':'COUNTERFACTUAL','status':'REFERENCE_CONDITIONALLY_REOPENED_IN_COPY',
                'before':counterfactual.before.decision('absolute_polarity'),
                'after':counterfactual.after.decision('absolute_polarity'),
                'receipt':counterfactual.receipt,'original_unchanged':True,'new_evidence':False}
    if action == 'COUNT_EVIDENCE':
        report = fir_receipt(state)
        return {'kind':'FINITE_LEDGER_RECOUNT',
                'accepted_events':len(state.accepted),
                'fixture_references':len(state.truth_receipts),
                'FIR_role':report['ledger_count_role'],
                'model_role':report['hypothesis_role'],
                'status':'F_LOCAL_LEDGER_ONLY','scope':report['scope'], 'new_evidence':False}
    raise AssertionError('missing trusted dispatcher implementation')


def advance(state: State, goal: Goal) -> dict:
    """One user goal -> orientation -> self-chosen questions -> actual read-only results.

    A synthetic external verification may be *proposed*, never silently claimed
    executed. No operational side effects, internet, tools or delegated authority.
    """
    initial = fingerprint(state)
    orientation = orient(state, goal)
    spent = 0
    steps = []
    excluded: frozenset[str] = frozenset()
    for index in range(goal.max_steps):
        remaining = goal.budget - spent
        available = nominate(state, goal, excluded)
        ranked = rank(available, remaining)
        if not ranked:
            break
        pick = ranked[0]
        before = fingerprint(state)
        output = _execute(state, pick.action, goal, remaining)
        after = fingerprint(state)
        # Never silently mutate upstream state during inquiry.
        if before != after:
            raise AssertionError('next-step computation modified evidence')
        spent += pick.cost
        steps.append({'step':index+1,'next_question':pick.question,
                      'reason':pick.reason,'action_executed':pick.action,
                      'scope':'LOCAL_READ_ONLY', 'cost':pick.cost,
                      'epistemic_status':('F_LOCAL' if pick.action in {'COUNT_EVIDENCE','TEST_SYMMETRY'} else 'I_CONDITIONAL'), 'result':output,
                      'receipt':{'operation':'auto_executed_local_inquiry',
                                 'input_evidence_digest':before,'output_evidence_digest':after,
                                 'question':pick.question,'action':pick.action,
                                 'new_independent_source':False}})
        excluded = excluded | {pick.action}
    return {'experiment':'NEXT-STEP-001',
            'scope':'synthetic witness-model adapter only',
            'orientation':orientation,'steps':steps,
            'status':'EXECUTED_LOCAL_STEPS' if steps else 'HOLD_NO_PERMITTED_AFFORDABLE_STEP',
            'budget_spent':spent,'budget_remaining':goal.budget-spent,
            'same_evidence_before_after':initial==fingerprint(state),
            'real_world_actions':0, 'external_evidence_acquired':False,
            'general_intelligence_claim':False,
            'next_frontier':'Add authorized domain adapters and independently verified sources.'}


def demonstration() -> dict:
    from witnesschain import synthetic_cases, TruthReceipt
    state = State()
    episodes = synthetic_cases((1,1,1),seed=7,size=100)
    for event,_ in episodes:
        state = state.add(event)
    plan = advance(state, Goal('absolute_polarity',budget=4,max_steps=3))
    referenced = state
    for event,truth in episodes[:3]:
        referenced = referenced.verify(TruthReceipt(event.id,truth,'synthetic-fixture-only'))
    challenge = advance(referenced,Goal('absolute_polarity',budget=2,max_steps=2))
    return {'unreferenced':plan,'challenged_reference':challenge}


if __name__ == '__main__':
    print(json.dumps(demonstration(),indent=2,sort_keys=True))
