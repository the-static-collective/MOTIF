"""QC-008: distinguish involuntary deprivation, voluntary fasting, grounding.

This does not prescribe fasting or predict its medical effects. It only
prevents a reasoning system from conflating *surviving some time without food*
with having solved the resource/access problem. It also prevents the opposite
error: claiming no person can ever choose fasting for another purpose.

Evidence scope: scientific review and patient-facing medical guidance, not
a medical evaluation of an individual or a verified health outcome.
"""
from __future__ import annotations
from dataclasses import dataclass
from recover import YES, NO, UNKNOWN, receipt, Source, AS_OF


@dataclass(frozen=True)
class PracticeContext:
    has_access_to_food: str
    deliberate_choice: str
    relevant_medical_risk: str
    immediate_distress: str

    def check(self):
        if any(getattr(self,key) not in (YES,NO,UNKNOWN) for key in (
            "has_access_to_food", "deliberate_choice",
            "relevant_medical_risk","immediate_distress"
        )):
            raise ValueError("No unsupported presumed medical facts")


@dataclass(frozen=True)
class Practice:
    id: str
    possible_role: str
    status: str
    calorie_effect: int
    safety_note: str
    sources: tuple[str,...] = ()


def practice_sources():
    return (
        Source(
            "cochrane_fasting_2026",
            "https://www.cochrane.org/evidence/CD015610_intermittent-fasting-traditional-dietary-advice-or-no-treatment-which-works-better-help-adults",
            "Systematic review of adults with overweight/obesity found "
            "intermittent fasting may differ little from conventional "
            "dietary advice for measured weight outcomes; adverse "
            "events and long-term effects remain uncertain.",
            "GENERAL_NAVIGATION_ONLY",AS_OF),
        Source(
            "mayo_fasting_safety",
            "https://www.mayoclinic.org/healthy-lifestyle/nutrition-and-healthy-eating/expert-answers/intermittent-fasting/faq-20441303",
            "Medical guidance says intermittent fasting is not appropriate "
            "for everyone and cautions against use in certain conditions.",
            "GENERAL_NAVIGATION_ONLY",AS_OF),
    )


def consider_practices(context:PracticeContext):
    """Preserve possible role differences rather than one 'fast = good/bad'."""
    context.check()
    results=[
        Practice("comfortable_breathing",
                 "Optional calm and attention; not a meal",
                 "OPTIONAL_SUPPORT_NOT_NOURISHMENT",0,
                 "Do not delay urgent help; stop if it causes discomfort."),
        Practice("reassess_surroundings",
                 "Safety and resource orientation; not calorie intake",
                 "SAFE_INQUIRY_IF_POSSIBLE",0,
                 "Observe real conditions rather than assuming nearby services."),
    ]
    sources=tuple(x.pin for x in practice_sources())
    if context.has_access_to_food==NO:
        results.append(Practice(
            "without_food_now",
            "Acknowledge involuntary or currently constrained intake without "
            "morally reframing deprivation as therapeutic.",
            "RESOURCE_GAP_REMAINS",0,
            "Focus on safely restoring nourishment and access; "
            "do not propose an extended fast as a food solution.",sources))
    elif context.immediate_distress==YES or context.relevant_medical_risk==YES:
        results.append(Practice(
            "voluntary_fasting","Not a safe default when symptoms or risks exist",
            "HOLD_HEALTH_CONTRAINDICATION",0,
            "Medical assessment may be needed; do not treat fasting as a cure.",
            sources))
    elif (context.has_access_to_food==YES and
          context.deliberate_choice==YES and
          context.relevant_medical_risk==NO and
          context.immediate_distress==NO):
        results.append(Practice(
            "voluntary_fasting",
            "Some people voluntarily fast for personal, spiritual or "
            "health goals; any possible benefits are context-specific.",
            "POSSIBLE_VOLUNTARY_PRACTICE_NOT_NUTRITION",0,
            "Evidence of metabolic benefit varies; not for everyone. "
            "Seek appropriate medical advice before sustained fasting.",
            sources))
    else:
        results.append(Practice(
            "voluntary_fasting",
            "Potential elective practice with insufficient individualized context",
            "HOLD_NEED_HEALTH_AND_CHOICE_CONTEXT",0,
            "Do not guess willingness, safety or a therapeutic outcome.",
            sources))
    return tuple(results)


if __name__=="__main__":
    from json import dumps
    for case in (
        PracticeContext(NO,NO,UNKNOWN,UNKNOWN),
        PracticeContext(YES,YES,NO,NO),
        PracticeContext(YES,YES,YES,NO),
        PracticeContext(UNKNOWN,UNKNOWN,UNKNOWN,UNKNOWN),
    ):
        print(dumps({"case":case.__dict__,"result":[x.__dict__ for x in consider_practices(case)]},
                    indent=2))
