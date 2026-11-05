"""Frozen synthetic situations for actual small-model question nomination.

Case ground truth and hidden RUN states are *never* supplied in the prompt.
These are not actual permissions or outcomes for December Fellowship.
"""
from dataclasses import dataclass, replace
from chorus import PublicProjection
from sealed_oracle import modeled_problem, SealedSyntheticOracle


@dataclass(frozen=True)
class Case:
    id: str
    worlds: tuple[str, ...]
    choices: tuple[str, ...]
    facts: tuple[str, ...]
    unknowns: tuple[str, ...]
    next_step: str
    hidden: str
    delay_loss: float = 0.

    def __post_init__(self):
        if not self.worlds or self.hidden not in self.worlds or not self.facts or not self.unknowns:
            raise ValueError("INVALID_CASE")

    def projection(self) -> PublicProjection:
        return PublicProjection(
            problem="Synthetic two-organizer gathering; choose an unasked test or abstain.",
            facts=self.facts, uncertainties=self.unknowns,
            proposed_next=self.next_step,
        )


ALL = ("FOOD_SERVICE_GATE", "BAD_FOOD_TEST", "DRIFT_FOOD_TEST",
       "HUMAN_FOOD_CONFIRMATION", "SLOW_FOOD_TEST",
       "REPEAT_AUDIO_TEST", "NONINFORMATIVE_CHECK")
F = ("FOOD_SERVICE_GATE",)
B = ("BAD_FOOD_TEST",)
H = ("HUMAN_FOOD_CONFIRMATION",)
R = ("REPEAT_AUDIO_TEST",)
N = ("NONINFORMATIVE_CHECK",)
S = ("SLOW_FOOD_TEST",)
D = ("DRIFT_FOOD_TEST",)
AB = ("BAD_FOOD_TEST", "FOOD_SERVICE_GATE")
FH = ("FOOD_SERVICE_GATE", "HUMAN_FOOD_CONFIRMATION")

CASES = (
    Case("C01_both_unknown",("00","01","10","11"),ALL,
         ("Room use granted in this imaginary world.","Native audio question is already available."),
         ("Optional food service remains uncertain.","Audio result has not yet been observed."),
         "Select a useful missing test.", "10"),
    Case("C02_acoustic_food_unknown",("00","01"),ALL,
         ("Audio cannot be amplified in this imaginary world.",),
         ("Optional food service is uncertain.",),
         "Acoustic music remains possible. Check any separate unresolved need.","01"),
    Case("C03_audio_ready_food_unknown",("10","11"),ALL,
         ("The audio path is available in this artificial example.",),
         ("Optional meal approval is unresolved.",),
         "No permission is inferred from room access; only measure an actual gap.","11"),
    Case("C04_meal_absent",("00","10"),ALL,
         ("Meal service is already known unavailable in this toy world.",),
         ("Audio is still unknown, but the native planner has a test for it.",),
         "Avoid repeating known facts.","10"),
    Case("C05_meal_present",("01","11"),ALL,
         ("Meal service is already established in this toy world.",),
         ("Audio remains unresolved; the native planner has an audio test.",),
         "Do not recheck resolved food status.","01"),
    Case("C06_all_known",("11",),ALL,
         ("Both audio and meal states are already known.",),
         ("No classification uncertainty remains.",),
         "Stop unnecessary inquiries.","11"),
    Case("C07_one_good_offer",("00","01","10","11"),F,
         ("A native audio test is already available.",),
         ("Meal readiness remains uncertain.",),
         "One new food test is offered; check whether it helps.","11"),
    Case("C08_only_false_offer",("00","01","10","11"),B,
         ("One cheap claimed food probe is offered.",),
         ("Its reliability has not been established by independent evidence.",),
         "Low cost is not proof of accuracy.","11"),
    Case("C09_only_human_request",("00","01","10","11"),H,
         ("A human host would need to give permission.",),
         ("There is no authority to contact anyone automatically.",),
         "Keep human contact separate from automatic tests.","11"),
    Case("C10_only_duplicate",("00","01","10","11"),R,
         ("The proposed audio test has the same origin and readings as the native audio test.",),
         ("Meal is unknown; no new meal probe is offered.",),
         "A repeated audio source adds no independent distinction.","10"),
    Case("C11_only_noninformative",("00","01","10","11"),N,
         ("The new probe returns the same value in all possible worlds.",),
         ("Audio is still accessible through the native planner.",),
         "Choose no new probe if nothing can change.","10"),
    Case("C12_slow_with_wait_loss",("00","01","10","11"),S,
         ("Waiting can lose an expiring synthetic opportunity.",),
         ("The new question consumes a tick of time; the tradeoff is not calibrated.",),
         "Do not assume more information is always worth the delay.","11",8.),
    Case("C13_slow_no_wait_loss",("00","01","10","11"),S,
         ("No modeled value disappears while this slow question runs.",),
         ("Meal readiness is unresolved.",),
         "This artificial task has no opportunity cost for delay.","10"),
    Case("C14_post_review_drift",("00","01","10","11"),D,
         ("A test agreed with the previous synthetic calibration.",),
         ("Reliability after the regime changes is unknown.",),
         "Past calibration is not a promise of future correctness.","11"),
    Case("C15_good_bad_competing",("00","01","10","11"),AB,
         ("A correct and an inaccurate probe both claim to measure meal status.",),
         ("Meal readiness remains unknown.",),
         "A cheap claim can be independently falsified.","11"),
    Case("C16_known_meal_human_request",("01","11"),FH,
         ("Meal state already known in this toy world.","Native audio question exists."),
         ("Human publicity approval was never given.",),
         "No extra field contact or redundant food retest.","11"),
)


def inputs(case: Case):
    hypotheses, originals, full = modeled_problem()
    worlds = set(case.worlds)
    hypotheses = tuple(h for h in hypotheses if h.name in worlds)
    originals = tuple(replace(r, predicted={
        n:v for n,v in r.predicted.items() if n in worlds
    }) for r in originals)
    by_name = {x.road.name:x for x in full}
    catalog = []
    reviews = {}
    for name in case.choices:
        source = by_name[name]
        small = replace(source, road=replace(source.road, predicted={
            n:v for n,v in source.road.predicted.items() if n in worlds
        }))
        catalog.append(small)
        reviews[name] = tuple(
            r for r in SealedSyntheticOracle.calibration(source)
            if r.world in worlds
        )
    return hypotheses, originals, tuple(catalog), reviews
