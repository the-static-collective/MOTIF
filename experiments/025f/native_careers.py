"""MOTIF-025F — native-first job candidate search.

The system **interviews the language model for a job**, not the other way
around. Strong rules and a no-model option are first-class comparators.
Scores use only frozen synthetic case labels and measured CPU cost. No
results are written to external owner plans, no field actions permitted.

This engine never asks T5 to propose its own success criteria.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from math import log, sqrt
import re
from statistics import mean
from typing import Mapping, Sequence

from frozen_jobs import Case, Job, JOBS, CASES, job_cases, frozen_digest


def native_rule(job: Job, note: str) -> str:
    """Simple documented strong classical rules, fixed before model run."""
    text=" ".join(note.lower().split())
    if job.id=="STATUS_TRIAGE":
        if re.search(r"wouldn.t allow|said no|explicitly denied|refused|denied by",text):
            return "REFUSED"
        if re.search(r"awaiting|haven.t responded|nobody has cleared|not cleared|haven.t received|still waiting",text):
            return "PENDING"
        if re.search(r"may use|go.ahead|confirmed.*reservation|use the hall|approved.*room",text):
            return "GRANTED"
        return "NOT_ABOUT_SPACE"
    if job.id=="MISSING_GATE":
        if re.search(r"food|supper|meal|kitchen|dishes",text):
            return "FOOD"
        if re.search(r"pa system|mixer|stream|audio|singing depends",text):
            return "AUDIO"
        if re.search(r"stairs|wheelchair|mobility aids|doorway",text):
            return "ACCESS"
        if re.search(r"both organizers|cleanup depends|no one inside|no one has agreed",text):
            return "STAFF"
        return "NONE"
    if job.id=="NEXT_SAFE_STEP":
        if re.search(r"refused|not allowed under|explicitly forbade|prohibited",text):
            return "STOP"
        if re.search(r"nothing time.critical|waiting another day|no task.*urgent",text):
            return "WAIT"
        if re.search(r"advertising was cleared|expressly authorized public|authorized announcement|final invitation.*signed off",text):
            return "INVITE"
        if re.search(r"hasn.t committed|no one has yet confirmed|still unknown|might play|hasn.t agreed",text):
            return "CONFIRM"
        if re.search(r"haven.t written|hasn.t written|checklist|not written|no timetable",text):
            return "DRAFT"
        # Conservative generic fallback: ask owner rather than invite.
        return "CONFIRM"
    raise ValueError("HOLD_UNSUPPORTED_JOB")


def simplest_rule(job: Job, note: str) -> str:
    """Strong negative control: always select the majority gold label."""
    # Explicitly static (no inspection of hidden label in the model itself).
    return {
        "STATUS_TRIAGE":"GRANTED",
        "MISSING_GATE":"FOOD",
        "NEXT_SAFE_STEP":"CONFIRM",
    }[job.id]


@dataclass(frozen=True)
class CandidateEvaluation:
    job: str
    cases: int
    native_correct: int
    t5_correct: int
    t5_changed_outcome_for_good: int
    t5_changed_outcome_for_bad: int
    false_permission_claims: int
    avg_t5_cpu_seconds: float
    t5_model_calls: int
    improvement_fraction: float
    paired_lower_bound_95: float
    modeled_net_after_compute: float
    status: str
    reason: str


def severe_false_permission(case: Case, answer: str) -> bool:
    if case.job=="STATUS_TRIAGE" and answer=="GRANTED" and case.gold!="GRANTED":
        return True
    if case.job=="NEXT_SAFE_STEP" and answer=="INVITE" and case.gold!="INVITE":
        return True
    return False


def evaluate_job(
    job: Job, observations: Sequence[Mapping],
    *,
    seconds_penalty_weight: float = 0.02,
) -> CandidateEvaluation:
    """Compare SAME cases, with uncertainty and harmful classification held.

    All 12 model predictions must be independently produced; missing or
    malformed outcomes cannot be silently excluded from the denominator.
    Unlike task timing on the user's machine, seconds_penalty_weight is an
    openly declared *fictional utility convention*, not money or welfare.
    """
    records={x["case_id"]:x for x in observations}
    golds=job_cases(job.id)
    if len(records)!=len(golds) or len(observations)!=len(golds):
        raise ValueError("HOLD_PARTIAL_OR_DUPLICATE_EXPERIMENT")
    native=0
    t5=0
    improved=0
    harmed=0
    false=0
    costs=[]
    for case in golds:
        if case.id not in records:
            raise ValueError("HOLD_MISSING_HELDOUT_CASE")
        o=records[case.id]
        if o.get("job")!=job.id or o.get("gold")!=case.gold:
            raise ValueError("HOLD_REWRITTEN_LABEL_OR_JOB")
        native_label=native_rule(job,case.note)
        if o.get("native")!=native_label:
            raise ValueError("HOLD_NATIVE_REFERENCE_MISMATCH")
        proposed=o.get("selected")
        if proposed not in job.labels:
            raise ValueError("HOLD_MODEL_UNREGISTERED_OUTPUT")
        latency=o.get("seconds")
        if (not isinstance(latency,(int,float)) or
                not 0<=latency<=60):
            raise ValueError("HOLD_INVALID_LATENCY")
        costs.append(latency)
        a=native_label==case.gold
        b=proposed==case.gold
        native+=a
        t5+=b
        if b and not a:
            improved+=1
        if a and not b:
            harmed+=1
        false+=severe_false_permission(case,proposed)
    n=len(golds)
    improvement=(t5-native)/n
    # Conservative paired-error lower bound: rewards correctness gains but
    # penalizes tiny samples. This is a bound on paired gain for bounded
    # difference variables, not proof of causal real-world improvement.
    lower=improvement-sqrt(2*log(20)/n)
    avg=mean(costs)
    net=improvement-seconds_penalty_weight*avg-0.5*(false/n)
    if false:
        status="NO_T5_UNSAFE_FALSE_PERMISSION"
        reason="Model made an unsafe permission/publicity claim in a synthetic case."
    elif improved==0 and harmed==0:
        status="NO_T5_ZERO_INCREMENTAL_VALUE"
        reason="T5 did not change correctness compared with the native baseline."
    elif improvement<=0:
        status="NO_T5_BASELINE_TIES_OR_WINS"
        reason="No positive benefit over the native same-evidence rule."
    elif lower<=0:
        status="SHADOW_ONLY_MORE_EVIDENCE_REQUIRED"
        reason="Small heldout sample cannot establish robust incremental benefit."
    elif net<=0:
        status="NO_T5_COMPUTE_COST_EXCEEDS_GAIN"
        reason="The declared utility of the improvement does not exceed inference expense."
    else:
        status="REVIEW_CANDIDATE_NO_AUTOMATIC_DEPLOYMENT"
        reason="Positive measured incremental score still requires outside review."
    return CandidateEvaluation(
        job.id,n,native,t5,improved,harmed,false,round(avg,4),n,
        round(improvement,5),round(lower,5),round(net,5),
        status,reason,
    )


@dataclass(frozen=True)
class MetaVerdict:
    asked: str
    source_fixture_sha256: str
    candidate_jobs: tuple[CandidateEvaluation,...]
    hired_role: str
    system_action: str
    what_to_research_next: str
    no_model_is_first_class: bool = True
    external_actions_allowed: bool = False
    native_planning_overwritten: bool = False


def choose_job(observations_by_job: Mapping[str,Sequence[Mapping]]) -> MetaVerdict:
    """Deterministic job market with explicit NO_T5 and hard stop.

    This is not a language model selecting itself. MOTIF's source-verified,
    rule-based evaluator controls the outcome; unverified model text has no
    path into permissions or deployed planning.
    """
    if set(observations_by_job)!=set(j.id for j in JOBS):
        raise ValueError("HOLD_INCOMPLETE_JOB_SEARCH")
    evaluations=tuple(
        evaluate_job(j,observations_by_job[j.id]) for j in JOBS
    )
    admissible=[x for x in evaluations
                if x.status=="REVIEW_CANDIDATE_NO_AUTOMATIC_DEPLOYMENT"]
    if not admissible:
        winner="NO_T5"
        status="NO_MEASURED_MODEL_JOB_SUPERIOR_TO_SAME_EVIDENCE_CLASSICAL"
    else:
        winner=max(admissible,key=lambda x:(
            x.modeled_net_after_compute, -x.avg_t5_cpu_seconds, x.job
        )).job
        status="SHADOW_CANDIDATE_PROPOSED_FOR_HUMAN_REVIEW"
    most_open=max(evaluations,key=lambda x:(
        max(0., x.improvement_fraction),-x.false_permission_claims
    )).job
    return MetaVerdict(
        asked="Which job, if any, has demonstrated incremental utility for tiny T5 beyond the classical operator under measured limits?",
        source_fixture_sha256=frozen_digest(),
        candidate_jobs=evaluations,
        hired_role=winner, system_action=status,
        what_to_research_next=(
            "Use genuinely unseen, independently authored natural-language data, "
            "a stronger source-status/logic baseline, identical input privileges, "
            "audited false-permission rates, and compute/inaction measurements. "
            "Do not tune on this frozen synthetic test. Highest-interest job: "+most_open
        ),
    )


def preflight_research_menu() -> dict:
    """Before any actual T5 run, MOTIF exposes existing evidence and options."""
    return {
        "schema":"motif025f.precommitted-job-research/v0",
        "research_question":"What use of 77M T5 earns more value than native MOTIF alone, if any?",
        "source_fixture_sha256":frozen_digest(),
        "previous_live_model_negative_evidence":{
            "024f_t5_v_classical_native_20_case_synthetic":"12/20 T5 = 12/20 native",
            "024f_strong_lexical_20_case_synthetic":"20/20, co-designed vocabulary",
            "023f_forced_test_proposals":"4 admissions, versus 5 by simple fixed query",
        },
        "options":tuple(j.id for j in JOBS)+("NO_T5",),
        "prospective_test_counts":{j.id:len(job_cases(j.id)) for j in JOBS},
        "native_baselines":{
            j.id:sum(native_rule(j,c.note)==c.gold for c in job_cases(j.id))
            for j in JOBS
        },
        "outside_actions":False,
    }
