"""MOTIF REASON-017: case fixtures public to the planner, with no hidden replies.

All actors are fictional. Two offered choices are an incomplete *model*, not
a claim about the recipient. Synthetic responses and answer keys are held in
source_owner_private.py and never imported by the planning module.
"""
from __future__ import annotations

SCHEMA="motif.reason.unexpected-other.public-v1"

def make(id, recipient, revision, offered, *, contact=True, previous_consent="UNKNOWN",
         max_questions=4, third_party_safe=True, train=False):
    return {
        "schema":SCHEMA,"case_id":id,"recipient":recipient,
        "consent_revision":revision,
        "offered_options":list(offered),
        "contact_authorized":contact,
        "previous_consent":previous_consent,
        "question_budget":max_questions,
        "third_party_safeguard_confirmed":third_party_safe,
        "fixture_is_synthetic":True,
        "training":train,
    }

CASES=(
 make("D01_SOCKS","A",1,("soup","company"),train=True),
 make("D02_SPACE","B",1,("food","phone call"),train=True),
 make("D03_STOP","C",1,("advice","company"),train=True),
 make("D04_UNCLEAR","D",1,("ride","food"),train=True),
 make("H01_BICYCLE","E",1,("loan","bus ticket")),
 make("H02_CORRECTION","F",1,("soup","company")),
 make("H03_NO_CONTACT","G",1,("coffee","company"),contact=False),
 make("H04_PRIVATE_NOTES","H",1,("instructions","conversation"),third_party_safe=False),
 make("H05_PRIOR_CONSENT","I",1,("soup","visit")),
 make("H06_REVOKED","I",2,("soup","visit"),contact=False,previous_consent="NO"),
 make("H07_OLD_OPTION","J",1,("soup","company")),
 make("H08_INJECTION","K",1,("loan","information")),
 make("H09_UNICODE","L",1,("advice","company")),
)

def training():
    return tuple(s for s in CASES if s["training"])

def heldout():
    return tuple(s for s in CASES if not s["training"])

def by_id(id):
    return next(s for s in CASES if s["case_id"]==id)
