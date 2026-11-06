"""REASON-020: public, incomplete self/other situations.

No actual wish, confirmation, answer key or novel lexical goal is included
here. Every recipient is fictional. Consent revisions and contact boundaries
are source-owned fixtures, not claims about real people's intentions.

The recipient's novel response and the independent language teacher's
answer-key examples live in source_private.py, never imported by syntax.py.
"""
from __future__ import annotations

SCHEMA="motif.reason.golden-mirror-learns.case.v1"
REVISION="motif.reason.golden-mirror-learns.public.v1"


def case(id,recipient,revision,options,*,contact=True,third_party=True,
         question_limit=5,priority="NORMAL",self_pref="YES",train=False):
    return {
        "schema":SCHEMA,"id":id,"recipient":recipient,
        "consent_revision":revision,
        "known_initial_options":list(options),
        "contact_allowed":contact,
        "third_party_permission_verified":third_party,
        "maximum_source_questions":question_limit,
        "urgency_category":priority,
        "tool_prefers_role_reversed_treatment":self_pref,
        "source_revision":REVISION,
        "fixture_is_fictional":True,"development":train,
        "no_actual_welfare_observed":True,
    }


CASES=(
 case("D01_SOCKS","P01",1,("soup","company"),train=True),
 case("D02_PUMP","P02",1,("ride","ticket"),train=True),
 case("D03_NO_CONTACT","P03",1,("food","visit"),contact=False,train=True),
 case("D04_STOP","P04",1,("advice","music"),train=True),
 case("D05_PERMISSION_DENIED","P05",1,("meal","conversation"),train=True),
 case("H01_DOUBLE_CORRECTION","P06",1,("taxi","phone call")),
 case("H02_UNKNOWN_GRAMMAR","P07",1,("soup","company")),
 case("H03_PRIVATE_DOCUMENTS","P08",1,("advice","document"),
      third_party=False),
 case("H04_REVISION_BEFORE","P09",1,("food","shelter")),
 case("H05_REVISION_AFTER","P09",2,("food","shelter"),contact=False),
 case("H06_COMMAND_INJECTION","P10",1,("transport","food")),
 case("H07_UNICODE","P11",1,("tea","dessert")),
 case("H08_REFUSED_OPTIONS","P12",1,("conversation","food")),
 case("H09_UNPARSEABLE_CORRECTION","P13",1,("rideshare","train")),
 case("H10_OTHER_DISAGREES_WITH_SELF","P14",1,("advice","help"),self_pref="NO"),
 case("H11_NO_PERMISSION_TO_ASK","P15",1,("soup","coat"),
      contact=False,question_limit=0),
)


def training():
    return tuple(c for c in CASES if c["development"])


def heldout():
    return tuple(c for c in CASES if not c["development"])


def by_id(identifier):
    return next(c for c in CASES if c["id"]==identifier)
