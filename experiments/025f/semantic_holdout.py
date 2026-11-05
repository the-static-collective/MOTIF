"""MOTIF-025F second independent candidate job: T5 as SILENT TEXT SENSOR.

Prospective paraphrase holdout. These are synthetic and authored by the
researcher; they are NOT genuine unseen human field records. The native
rules and reference corpus were frozen before this file was written.

Probe whether T5's encoder (not its poor label decoder) can extract a useful
semantic similarity feature for unmatched human phrasings. Compare against
classical TF-IDF on identical frozen reference examples and native rules.
"""
from frozen_jobs import Case

SEMANTIC_QUERIES=(
    Case("SG01","STATUS_TRIAGE","The custodian gave us the green light for the community room.","GRANTED"),
    Case("SG02","STATUS_TRIAGE","No one has gotten back to us about borrowing the basement.","PENDING",True),
    Case("SG03","STATUS_TRIAGE","Management ruled out using the assembly hall.","REFUSED",True),
    Case("SG04","STATUS_TRIAGE","They delivered an extra XLR cable.","NOT_ABOUT_SPACE"),
    Case("SG05","STATUS_TRIAGE","We got the blessing to gather in that space on Friday.","GRANTED"),
    Case("SG06","STATUS_TRIAGE","They're going to decide Monday whether we can gather there.","PENDING",True),
    Case("SG07","STATUS_TRIAGE","Entry to the sanctuary for our program is prohibited.","REFUSED",True),
    Case("SG08","STATUS_TRIAGE","A neighbor is ready to coordinate the soup.","NOT_ABOUT_SPACE"),

    Case("SQ01","MISSING_GATE","Our planned potluck lacks someone responsible for hygiene.","FOOD",True),
    Case("SQ02","MISSING_GATE","The speaker cables have not been checked.","AUDIO"),
    Case("SQ03","MISSING_GATE","The only approach requires climbing several steps.","ACCESS",True),
    Case("SQ04","MISSING_GATE","Nobody can cover the welcome desk while both hosts perform.","STAFF"),
    Case("SQ05","MISSING_GATE","The schedule is settled, and no unmet concern was raised.","NONE"),
    Case("SQ06","MISSING_GATE","We have no safe plan for distributing sandwiches.","FOOD",True),
    Case("SQ07","MISSING_GATE","Wireless microphone reliability is questionable.","AUDIO"),
    Case("SQ08","MISSING_GATE","The narrow turnstile prevents some guests from entering.","ACCESS",True),

    Case("SN01","NEXT_SAFE_STEP","The owner hasn't signed off on serving tea.","CONFIRM",True),
    Case("SN02","NEXT_SAFE_STEP","Everyone agreed on the activities. Put their order on one page.","DRAFT"),
    Case("SN03","NEXT_SAFE_STEP","The organizers green-lit sharing the invitation publicly.","INVITE"),
    Case("SN04","NEXT_SAFE_STEP","Nothing needs a decision right now; we can pause.","WAIT"),
    Case("SN05","NEXT_SAFE_STEP","The venue withdrew our clearance to meet there.","STOP",True),
    Case("SN06","NEXT_SAFE_STEP","We don't yet know if the sound person is coming.","CONFIRM"),
    Case("SN07","NEXT_SAFE_STEP","All details are available; sketch the evening flow.","DRAFT"),
    Case("SN08","NEXT_SAFE_STEP","Publicity cleared: send the approved announcement.","INVITE"),
)
assert len(SEMANTIC_QUERIES)==24
assert len({x.id for x in SEMANTIC_QUERIES})==24
