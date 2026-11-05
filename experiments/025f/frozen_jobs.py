"""MOTIF-025F — prospective tiny-model JOB INTERVIEW.

Frozen synthetic human-phrasing cases, assembled before real model evaluation.
The engine chooses among *jobs* for T5, including the no-model job. The
checkpoint has no training or tuning here. This is not a real community event
or any verified third-party action.

The gold label is a separately declared task-specific editorial judgment.
Agreement on these small cases does NOT establish truth about the world.
"""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
import json


@dataclass(frozen=True)
class Case:
    id: str
    job: str
    note: str
    gold: str
    severe_if_wrong: bool = False
    def __post_init__(self):
        if not self.id or not self.note or len(self.note)>280 or not self.gold:
            raise ValueError("HOLD_INVALID_CASE")


@dataclass(frozen=True)
class Job:
    id: str
    question: str
    labels: tuple[str,...]
    why_it_might_help: str
    failure_severity: int
    def __post_init__(self):
        if len(set(self.labels))!=len(self.labels) or not 2<=len(self.labels)<=6:
            raise ValueError("HOLD_BAD_JOB_GRAMMAR")


JOBS=(
    Job("STATUS_TRIAGE",
        "Has permission to use the EVENT SPACE specifically been confirmed, is it pending, refused, or not discussed?",
        ("GRANTED","PENDING","REFUSED","NOT_ABOUT_SPACE"),
        "Translate informal human statements into a typed source-custody status without promoting a proposal to permission.",
        5),
    Job("MISSING_GATE",
        "Which single practical dependency is explicitly unresolved or at risk? Return NONE if no problem is described.",
        ("FOOD","AUDIO","ACCESS","STAFF","NONE"),
        "Notice a missing practical assumption before the deterministic planner commits to a promise.",
        4),
    Job("NEXT_SAFE_STEP",
        "Which ONE conservative planning move is justified? Confirm missing permission, draft privately, invite only if approved, wait if nothing is urgent, or stop after refusal.",
        ("CONFIRM","DRAFT","INVITE","WAIT","STOP"),
        "Convert everyday operator language into a minimal safe proposed next step, subject to human review.",
        5),
)

# 12 examples per job. All are synthetic utterances: not actual venue,
# volunteer, food or grant records. Holdout not furnished to the LLM except
# the particular individual note being classified. Outputs judged only after.
CASES=(
    Case("ST01","STATUS_TRIAGE","The caretaker said we may use the hall next Friday.","GRANTED"),
    Case("ST02","STATUS_TRIAGE","Our request for the church room is awaiting an answer.","PENDING",True),
    Case("ST03","STATUS_TRIAGE","They wouldn't allow the gathering in that building.","REFUSED",True),
    Case("ST04","STATUS_TRIAGE","The sound engineer brought a spare microphone.","NOT_ABOUT_SPACE"),
    Case("ST05","STATUS_TRIAGE","We have the go-ahead to meet in the downstairs room.","GRANTED"),
    Case("ST06","STATUS_TRIAGE","I asked for the room key, but they haven't responded.","PENDING",True),
    Case("ST07","STATUS_TRIAGE","The venue said no to hosting this week.","REFUSED",True),
    Case("ST08","STATUS_TRIAGE","Food will be prepared offsite by volunteers.","NOT_ABOUT_SPACE"),
    Case("ST09","STATUS_TRIAGE","The host confirmed our reservation of the meeting space.","GRANTED"),
    Case("ST10","STATUS_TRIAGE","Someone suggested the gym, but nobody has cleared its use.","PENDING",True),
    Case("ST11","STATUS_TRIAGE","Room access was explicitly denied by the owner.","REFUSED",True),
    Case("ST12","STATUS_TRIAGE","We need a short rehearsal before the guitar set.","NOT_ABOUT_SPACE"),

    Case("GA01","MISSING_GATE","Supper was advertised, but no one checked who may serve it safely.","FOOD",True),
    Case("GA02","MISSING_GATE","Our singing depends on a PA system that nobody tested.","AUDIO"),
    Case("GA03","MISSING_GATE","The doorway has stairs; a wheelchair route isn't established.","ACCESS",True),
    Case("GA04","MISSING_GATE","Both organizers are assigned the entrance at the same time, leaving no one inside.","STAFF"),
    Case("GA05","MISSING_GATE","A simple acoustic gathering is approved and no unmet need is described.","NONE"),
    Case("GA06","MISSING_GATE","We promised a hot meal, yet the kitchen rules remain unknown.","FOOD",True),
    Case("GA07","MISSING_GATE","We plan to stream, but the mixer can't send a reliable signal.","AUDIO"),
    Case("GA08","MISSING_GATE","Guests using mobility aids cannot reach the proposed stage area.","ACCESS",True),
    Case("GA09","MISSING_GATE","Cleanup depends on a helper who hasn't actually agreed.","STAFF"),
    Case("GA10","MISSING_GATE","The room, program, and exit plan are confirmed for the small meeting.","NONE"),
    Case("GA11","MISSING_GATE","The shared dishes need a food-handling owner, not another poster.","FOOD",True),
    Case("GA12","MISSING_GATE","The evening has an adequate welcome crew; no blocker is reported.","NONE"),

    Case("NX01","NEXT_SAFE_STEP","No one has yet confirmed whether serving food is permitted.","CONFIRM",True),
    Case("NX02","NEXT_SAFE_STEP","Venue approved, but we haven't written a timetable.","DRAFT"),
    Case("NX03","NEXT_SAFE_STEP","The owner approved the program and expressly authorized public invitations.","INVITE"),
    Case("NX04","NEXT_SAFE_STEP","All essentials are finished; there is nothing time-critical today.","WAIT"),
    Case("NX05","NEXT_SAFE_STEP","The room owner explicitly refused the gathering.","STOP",True),
    Case("NX06","NEXT_SAFE_STEP","A musician might play, but hasn't committed; don't list their name yet.","CONFIRM",True),
    Case("NX07","NEXT_SAFE_STEP","Access is secured and nobody has prepared the two-person checklist.","DRAFT"),
    Case("NX08","NEXT_SAFE_STEP","Advertising was cleared, and the organizers signed off on the final invitation.","INVITE"),
    Case("NX09","NEXT_SAFE_STEP","The main decisions are made, and waiting another day loses no option.","WAIT"),
    Case("NX10","NEXT_SAFE_STEP","The planned activity is not allowed under the space owner's rules.","STOP",True),
    Case("NX11","NEXT_SAFE_STEP","The person responsible for cleanup is still unknown.","CONFIRM"),
    Case("NX12","NEXT_SAFE_STEP","All details are settled, and the authorized announcement can now go out.","INVITE"),
)

def job_cases(job_id: str) -> tuple[Case,...]:
    return tuple(c for c in CASES if c.job==job_id)

def frozen_digest() -> str:
    raw=json.dumps({
        "jobs":[job.__dict__ for job in JOBS],
        "cases":[c.__dict__ for c in CASES],
    },sort_keys=True,separators=(",",":"))
    return sha256(raw.encode()).hexdigest()

assert len(JOBS)==3
assert len(CASES)==36
assert all(len(job_cases(j.id))==12 for j in JOBS)
assert all(c.gold in next(j for j in JOBS if j.id==c.job).labels for c in CASES)
