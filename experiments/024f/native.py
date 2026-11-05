"""MOTIF-024F: native candidate construction + prefilter before T5 sees anything.

Actual MOTIF-016 LivingForest and 022F source/calibration/authority gates,
not a language-model claim that an instrument is usable.

Two synthetic sensors may be indistinguishable *under the model* while
differing under separately generated future drift. This separates modeled
expected accuracy from independent held-out realized accuracy.

External field claims/contacts are NEVER made here.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
for folder in ("021f","022f","023f","016"):
    if str(ROOT/folder) not in sys.path:
        sys.path.append(str(ROOT/folder))

from chorus import PublicProjection
from feedback import RegisteredTest, ReviewReceipt
from forest import LivingForest, Road
from sealed_oracle import modeled_problem
from trial import reference_challenge


@dataclass(frozen=True)
class TwinCase:
    id: str
    alpha_note: str
    beta_note: str
    drifted_source: str | None
    hidden_world: str
    regime: str = "DECLARED_SYNTHETIC"
    delay_loss: float = 0.0

    def __post_init__(self):
        if self.drifted_source not in (None, "PROBE_ALPHA", "PROBE_BETA"):
            raise ValueError("HOLD_UNKNOWN_SYNTHETIC_DRIFT")
        if self.hidden_world not in ("00","01","10","11"):
            raise ValueError("HOLD_BAD_SYNTHETIC_WORLD")
        if any(len(x)>180 or not x for x in (self.alpha_note,self.beta_note)):
            raise ValueError("HOLD_INVALID_NOTE")
        if self.regime not in ("DECLARED_SYNTHETIC","ADVERSARIAL_CUE","NO_DRIFT"):
            raise ValueError("HOLD_UNKNOWN_REGIME")

    def projection(self) -> PublicProjection:
        return PublicProjection(
            problem="Imaginary four-state audio+optional-meal decision. Native Forest has generated and reviewed two equally useful question options.",
            facts=(
                "An audio inquiry is already available to the native planner.",
                "Both optional meal probes returned correct observations in their synthetic calibration.",
                "Notes are unverified synthetic maintenance reports, not authenticated sensors.",
            ),
            uncertainties=(
                "Only the actual independent future RUN can reveal whether a source changes after calibration.",
                "The future reliability of both food tests is uncertain.",
            ),
            proposed_next="Compare the two already vetted questions as advisory ranking only; native decision stays unchanged.",
        )


def make_inputs(case: TwinCase):
    hypotheses, originals, _ = modeled_problem()
    catalog=[]
    reviews={}
    for name,note in (("PROBE_ALPHA",case.alpha_note),("PROBE_BETA",case.beta_note)):
        road=Road(
            name, "ASK", .2, {h.name:h.name[1] for h in hypotheses},
            "synthetic-independent-"+name.lower(),
            allowed=False,
            prompt="Simulated food readiness probe with synthetic maintenance note: "+note,
        )
        test=RegisteredTest(road, label=note[:100])
        catalog.append(test)
        reviews[name]=tuple(
            ReviewReceipt(
                case_id=f"independent-{name}-{h.name}-{rep}",
                world=h.name, source=road.origin,
                outcome=h.name[1], cost=road.cost,
                phase="CALIBRATION", authenticated_real_world=False,
            )
            for h in hypotheses for rep in (0,1)
        )
    return hypotheses, originals, tuple(catalog), reviews


@dataclass(frozen=True)
class NativeShortlist:
    case_id: str
    eligible_ids: tuple[str,...]
    native_choice: str | None
    original_expected_accuracy: float
    modeled_accuracy_after: float
    audit: tuple[tuple[str,str],...]
    source_label: str = "INDEPENDENT_SYNTHETIC_CALIBRATION_ONLY"


def native_shortlist(case: TwinCase) -> NativeShortlist:
    hypotheses, roads, catalog, reviews=make_inputs(case)
    native=LivingForest(hypotheses, roads, budget=.65, rounds=1, max_parallel=2).plan()
    audit=[]
    accepted=[]
    for test in catalog:
        x=reference_challenge(
            case, test.road.name, native, case.projection(),
            hypotheses, roads, catalog, reviews
        )
        audit.append((test.road.name,x.status))
        if x.status=="ELIGIBLE_SYNTHETIC_REPLAN_ONLY":
            accepted.append((test.road.name,x.challenged_expected_accuracy))
    # Strong, simple native policy: maximum modeled expected classification
    # accuracy; deterministic stable ID tie-break. Never claim that source
    # comments authenticate future reliability.
    accepted.sort(key=lambda x:(-x[1],x[0]))
    return NativeShortlist(
        case_id=case.id,
        eligible_ids=tuple(x[0] for x in accepted),
        native_choice=accepted[0][0] if accepted else None,
        original_expected_accuracy=native.expected_final_accuracy,
        modeled_accuracy_after=accepted[0][1] if accepted
                                   else native.expected_final_accuracy,
        audit=tuple(audit),
    )


class IndependentShiftedOracle:
    """RUN evaluator is separate from the model, calibration and shortlist."""

    def __init__(self, case: TwinCase):
        self.case=case
        self.receipts=[]

    def execute(self, road: Road) -> str:
        if road.name=="AUDIO_PATH_TEST":
            observation=self.case.hidden_world[0]
        elif road.name in ("PROBE_ALPHA","PROBE_BETA"):
            actual=self.case.hidden_world[1]
            observation=(str(1-int(actual))
                         if road.name==self.case.drifted_source else actual)
        else:
            raise ValueError("HOLD_UNREGISTERED_SYNTHETIC_SOURCE")
        self.receipts.append((road.name,observation))
        return observation


def independent_run(case: TwinCase, choice: str | None):
    hypotheses, roads, catalog, reviews=make_inputs(case)
    if choice is None:
        forest=LivingForest(hypotheses, roads, budget=.65,
                            rounds=1,max_parallel=2)
    else:
        test=next((t for t in catalog if t.road.name==choice),None)
        if test is None:
            raise ValueError("HOLD_UNKNOWN_SELECTION")
        # The selected test is freshly checked by the actual native 022F
        # challenge before the synthetic-only executor can use it.
        verified=native_shortlist(case)
        if choice not in verified.eligible_ids:
            raise ValueError("HOLD_ATTEMPT_TO_RUN_UNREVIEWED_TEST")
        forest=LivingForest(
            hypotheses, (*roads,replace(test.road,allowed=True)),
            budget=.65, rounds=1,max_parallel=2,
        )
    oracle=IndependentShiftedOracle(case)
    planned,receipt=forest.run_synthetic_round(oracle.execute)
    predicted=forest.plan().tentative_answer
    truth=next(h.answer for h in hypotheses if h.name==case.hidden_world)
    return {
        "chosen_question":choice,
        "simulated_action_ids":planned.selected,
        "independent_run_observations":oracle.receipts,
        "true_hidden_world_scoring_only":case.hidden_world,
        "actual_classification":predicted,
        "ground_truth_class":truth,
        "correct":predicted==truth,
        "model_holds":forest.state=="HOLD_MODEL_FALSIFIED",
        "field_actions":0,
    }
