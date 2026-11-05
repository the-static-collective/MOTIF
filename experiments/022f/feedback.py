"""MOTIF-022F — a sidecar critique can propose a typed TEST, not a fact.

Pipeline: parallel 021F Chorus note -> strict test ID -> immutable operator
catalog -> independent synthetic review -> 016 LivingForest counterfactual
replan -> optional external-to-model synthetic test receipt.

No generated text gains capability, changes the user's facts, schedules action,
or calls a third party. At most one new synthetic probe can enter the plan.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from hashlib import sha256
import json
from math import isfinite
from pathlib import Path
import re
import sys
from typing import Mapping, Sequence

sys.path.append(str(Path(__file__).resolve().parents[1] / "016"))
sys.path.append(str(Path(__file__).resolve().parents[1] / "021f"))
from forest import LivingForest, Road, ForestPlan
from multiplex import Hypothesis
from chorus import PublicProjection, SidecarRun

GRAMMAR = re.compile(r"TEST_ID=([A-Z][A-Z0-9_]{0,39})\Z")
MAX_PROPOSALS_PER_TURN = 2


@dataclass(frozen=True)
class RegisteredTest:
    road: Road
    label: str
    scope: str = "SYNTHETIC_ONLY"
    human_execution_required: bool = False
    operator_approved_for_synthetic: bool = True
    latency_ticks: int = 0

    def __post_init__(self):
        if (not self.label or len(self.label) > 100
                or self.scope != "SYNTHETIC_ONLY"
                or not 0 <= self.latency_ticks <= 3
                or self.road.kind not in {"ASK", "VERIFY"}
                or self.road.allowed or not self.road.origin):
            raise ValueError("HOLD_UNSUPPORTED_REGISTERED_TEST")


@dataclass(frozen=True)
class ReviewReceipt:
    case_id: str
    world: str
    source: str
    outcome: str
    cost: float
    phase: str = "CALIBRATION"
    authenticated_real_world: bool = False


@dataclass(frozen=True)
class CriticChallenge:
    status: str
    proposed_test: str | None
    note_sha256: str
    original_plan: ForestPlan
    challenged_plan: ForestPlan | None
    original_expected_accuracy: float
    challenged_expected_accuracy: float | None
    review_errors: tuple[str, ...] = ()
    model_permission: str = "SYNTHETIC_PREDICTION_ONLY"
    field_execution_authorized: bool = False
    real_source_authenticated: bool = False
    no_automatic_adoption: bool = True


class QuestionLedger:
    """Per-session stop rule: do not self-referentially request the same test."""
    def __init__(self, max_attempts: int = MAX_PROPOSALS_PER_TURN):
        if max_attempts < 1 or max_attempts > 3:
            raise ValueError("HOLD_UNBOUNDED_LOOP")
        self.max_attempts = max_attempts
        self.seen: set[str] = set()

    def claim(self, test_id: str) -> str | None:
        if test_id in self.seen:
            return "HOLD_REPEATED_QUESTION_LOOP"
        if len(self.seen) >= self.max_attempts:
            return "HOLD_RESEARCH_ATTEMPT_LIMIT"
        self.seen.add(test_id)
        return None


class QuestionAwareBackend:
    """Wrap an existing T5/text backend. Inject only operator-owned test IDs.

    The Chorus remains the native 021F parallel three-role worker. Critic is
    asked to output exactly one machine-readable ID; nonconforming language
    is an untrusted comment, not something we infer a test from.
    """
    def __init__(self, inner, catalog: Sequence[RegisteredTest]):
        if len(catalog) > 8 or len({x.road.name for x in catalog}) != len(catalog):
            raise ValueError("HOLD_INVALID_QUESTION_CATALOG")
        self.inner = inner
        self.name = "QUESTION_CONTRACT_OVER_" + inner.name
        self.catalog = tuple(catalog)

    def generate(self, prompt: str) -> str:
        if prompt.startswith("ROLE=CRITIC."):
            choices = "; ".join(
                t.road.name + " (" + t.label + ")" for t in self.catalog
            )
            # Prompt is *not* proof that a little T5 will follow the format.
            # Every candidate passes a strict deterministic parser afterward.
            prompt = (
                "Return EXACTLY TEST_ID=<ONE_REGISTERED_ID> with no explanation. "
                "Choose a falsifiable next test if useful. The listed IDs "
                "are suggestions, NOT executable permissions. "
                "REGISTERED=" + choices + ". " + prompt
            )
        return self.inner.generate(prompt)


def critic_note_hash(text: str) -> str:
    return sha256(text.encode("utf-8")).hexdigest()


def validate_review(
    test: RegisteredTest, receipts: Sequence[ReviewReceipt],
    worlds: Sequence[str],
) -> tuple[str, tuple[str, ...]]:
    """Independently scored synthetic fixtures only; never LLM output.

    Full-state coverage stops a single conveniently correct world from
    licensing an arbitrary hypothesis mapping. No real-world authentication.
    """
    if len(receipts) < len(worlds) or len(set(worlds)) != len(worlds):
        return "HOLD_INSUFFICIENT_CALIBRATION", ()
    failures = []
    seen = set()
    coverage = set()
    predictions = test.road.predicted
    if set(predictions) != set(worlds):
        return "HOLD_HYPOTHESIS_FAMILY_MISMATCH", ()
    for r in receipts:
        if r.case_id in seen:
            failures.append("DUPLICATE_CASE:" + r.case_id)
        seen.add(r.case_id)
        if r.phase != "CALIBRATION":
            failures.append("PHASE_MISMATCH:" + r.case_id)
        if r.authenticated_real_world:
            failures.append("FALSE_REAL_AUTHENTICATION:" + r.case_id)
        if r.source != test.road.origin:
            failures.append("SOURCE_MISMATCH:" + r.case_id)
        if r.world not in predictions:
            failures.append("OUT_OF_GRAMMAR:" + r.case_id)
        else:
            coverage.add(r.world)
            if r.outcome != predictions[r.world]:
                failures.append("COUNTEREXAMPLE:" + r.case_id)
        if not isfinite(r.cost) or abs(r.cost - test.road.cost) > 1e-9:
            failures.append("COST_MISMATCH:" + r.case_id)
    if coverage != set(worlds):
        failures.append("MISSING_WORLD_COVERAGE")
    if failures:
        return "REFUSE_CALIBRATION_FALSIFIED", tuple(failures)
    return "ELIGIBLE_SYNTHETIC_TEST_ONLY", ()


def submit_critic_question(
    sidecar: SidecarRun,
    projection: PublicProjection,
    hypotheses: Sequence[Hypothesis],
    original_roads: Sequence[Road],
    catalog: Sequence[RegisteredTest],
    independent_reviews: Mapping[str, Sequence[ReviewReceipt]],
    ledger: QuestionLedger,
    *,
    budget: float = 0.65,
    cost_of_wait_if_delayed: float = 0.0,
) -> CriticChallenge:
    """Bounded return edge into the existing MOTIF-016 question planner.

    Critical gate: a critique nominates **one existing registered test**;
    only independent calibration can offer it to a *fresh sandbox planner*.
    The primary native decision in SidecarRun is never modified or replaced.
    """
    if (not isfinite(cost_of_wait_if_delayed) or cost_of_wait_if_delayed < 0
            or not isfinite(budget) or budget < 0):
        raise ValueError("HOLD_INVALID_QUESTION_TIME_COST")
    if not isinstance(sidecar.native, ForestPlan) or not sidecar.native_completed:
        raise ValueError("HOLD_MISSING_NATIVE_FOREST_PLAN")
    baseline = sidecar.native

    def result(status: str, name: str | None = None,
               challenged: ForestPlan | None = None,
               errors: tuple[str, ...] = (), note_hash: str = "") -> CriticChallenge:
        return CriticChallenge(
            status, name, note_hash, baseline, challenged,
            baseline.expected_final_accuracy,
            challenged.expected_final_accuracy if challenged else None,
            errors,
        )

    notes = [n for n in sidecar.notes if n.role == "CRITIC"]
    if len(notes) != 1:
        return result("HOLD_CRITIC_NOTE_MISSING")
    note = notes[0]
    hashed = critic_note_hash(note.text)
    if (note.snapshot_sha256 != projection.digest()
            or note.execution_authority != "NONE"
            or note.affects_native_decision
            or note.epistemic_status != "UNVERIFIED_LLM_COMMENTARY"):
        return result("HOLD_STALE_OR_UNTRUSTED_CRITIC_NOTE", note_hash=hashed)
    if note.status != "UNVERIFIED_TEXT_AVAILABLE":
        return result("HOLD_CRITIC_NOT_READY", note_hash=hashed)
    match = GRAMMAR.fullmatch(note.text.strip())
    if not match:
        return result("HOLD_UNSTRUCTURED_OR_INJECTED_CRITIQUE", note_hash=hashed)
    name = match.group(1)
    # Reserved zero-authority option for constrained tiny-model decoders.
    # Explicitly not a registered sensing program; no work or replan occurs.
    if name == "NO_TEST":
        return result("HOLD_MODEL_ABSTAINED", name, note_hash=hashed)
    held = ledger.claim(name)
    if held:
        return result(held, name, note_hash=hashed)
    by_name = {t.road.name: t for t in catalog}
    if len(by_name) != len(catalog):
        return result("HOLD_DUPLICATE_TEST_REGISTRY", name, note_hash=hashed)
    if name not in by_name:
        return result("HOLD_HALLUCINATED_TEST_ID", name, note_hash=hashed)
    test = by_name[name]
    if (test.scope != "SYNTHETIC_ONLY" or test.human_execution_required
            or not test.operator_approved_for_synthetic):
        return result("HOLD_HUMAN_AUTHORITY_REQUIRED", name, note_hash=hashed)
    # No artificial conversion between accuracy and societal welfare.
    # Tests consuming real time must be separately evaluated using actual
    # outcome/latency estimates; the LLM cannot decide that calibration.
    if test.latency_ticks and cost_of_wait_if_delayed > 0:
        return result("HOLD_DELAY_INFORMATION_TRADEOFF_UNCALIBRATED", name, note_hash=hashed)
    if (name in {r.name for r in original_roads}
            or any((r.origin, tuple(sorted(r.predicted.items()))) ==
                   (test.road.origin, tuple(sorted(test.road.predicted.items())))
                   for r in original_roads)):
        return result("HOLD_DUPLICATE_OR_EXISTING_QUESTION", name, note_hash=hashed)
    review_status, errors = validate_review(
        test, independent_reviews.get(name, ()), [h.name for h in hypotheses]
    )
    if review_status != "ELIGIBLE_SYNTHETIC_TEST_ONLY":
        return result(review_status, name, errors=errors, note_hash=hashed)

    admitted = replace(test.road, allowed=True)
    # Actual 016 expectimax; using exactly the same finite world/permissions
    # as the baseline except for the independently admitted test.
    forest = LivingForest(hypotheses, tuple(original_roads) + (admitted,),
                          budget=budget, rounds=1, max_parallel=2)
    revised = forest.plan()
    if name not in revised.selected:
        return result("HOLD_TEST_NOT_CHOSEN_BY_NATIVE_PLANNER", name,
                      revised, note_hash=hashed)
    if revised.expected_final_accuracy <= baseline.expected_final_accuracy + 1e-9:
        return result("HOLD_NO_EXPECTED_DECISION_IMPROVEMENT", name,
                      revised, note_hash=hashed)
    return result("ELIGIBLE_SYNTHETIC_REPLAN_ONLY", name, revised,
                  note_hash=hashed)
