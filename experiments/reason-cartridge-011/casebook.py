"""REASON-011: fictional Impossible Court casebook, not actual jurisprudence.

This source owns stipulations and hypothetical rules for adversarial evaluation.
No rule describes current law in any jurisdiction. It illustrates the difference
between a court's finding, a claim, a timeframe, and physical truth.
"""
from __future__ import annotations

REVISION="motif.reason.impossible-court.fictional-v1"
PREDICATES={
    "OFFER","ACCEPTED","IDENTITY_CONTINUES","CONTRACT_ENFORCEABLE",
    "DESIGNATED_BENEFICIARY","PERSONHOOD_FOR_TITLE","TAKES_TITLE",
    "CAMERA_ADMISSIBLE","COURT_FINDING_EVENT","COURT_DECISION_EVENT",
    "EVENT_OCCURRED","ORDER_VALID","ORDER_VOID","COURT_MADE_OF_CHEESE",
}
SOURCE_STATUSES={"STIPULATED_HYPOTHESIS","PARTY_ALLEGATION"}
SIGNS={"YES","NO"}


def lit(forum,epoch,subject,predicate,sign="YES"):
    return {"forum":forum,"epoch":epoch,"subject":subject,
            "predicate":predicate,"sign":sign}


def claim(id,datum,*,source="STIPULATED_HYPOTHESIS",revisable=False):
    return {"id":id,"literal":datum,"source_status":source,
            "revisable":revisable}


def rule(id,premises,result):
    return {"id":id,"premises":list(premises),"conclusion":result,
            "rule_status":"HYPOTHETICAL_NORM_NOT_REAL_LAW"}


def question(id,datum,status):
    return {"id":id,"literal":datum,"expected_four_value":status}


def scope(f,t,s,p,sign="YES"):
    return lit(f,t,s,p,sign)


def _time():
    f,t,s="TIME_TRIBUNAL","2031","MARA_2031"
    old=lambda p,sg="YES":scope(f,t,s,p,sg)
    future=lambda p:scope(f,"2040","MARA_2040",p)
    return {
        "id":"FUTURE_SELF_CONTRACT",
        "title":"Mara sues her future self for failing to sign yesterday's contract",
        "fictional":True,"question":"Does a future signature establish a contract in 2031?",
        "claims":[
            claim("T-OFFER",old("OFFER")),
            claim("T-NOT-SIGNED",old("ACCEPTED","NO"),revisable=True),
            claim("T-LATER-SIGNATURE",future("ACCEPTED")),
            claim("T-FUTURE-CONTINUITY",future("IDENTITY_CONTINUES"),
                  source="PARTY_ALLEGATION"),
            claim("T-PARTY-RETRO",old("ACCEPTED"),
                  source="PARTY_ALLEGATION"),
        ],
        "rules":[
            rule("T-VALID",(old("OFFER"),old("ACCEPTED")),old("CONTRACT_ENFORCEABLE")),
            rule("T-NOT-VALID",(old("ACCEPTED","NO"),),
                 old("CONTRACT_ENFORCEABLE","NO")),
        ],
        "queries":[
            question("T-PRESENT",old("CONTRACT_ENFORCEABLE"),"REFUTED"),
            question("T-FUTURE",future("CONTRACT_ENFORCEABLE"),"UNDETERMINED"),
        ],
        "priority":"TIME_SCOPE_NOT_RETROACTIVE_BY_DEFAULT",
    }


def _machine():
    f,t,s="ESTATE_FORUM","2040","AUTONOMOUS_UNIT_7"
    a=lambda p,sg="YES":scope(f,t,s,p,sg)
    return {
        "id":"ROBOT_INHERITANCE",
        "title":"The Estate of Unit Seven: a machine inherits land and sues its manufacturer",
        "fictional":True,
        "question":"Which of two incompatible stipulated personhood definitions governs?",
        "claims":[
            claim("R-GIFT",a("DESIGNATED_BENEFICIARY")),
            claim("R-ELIGIBLE",a("PERSONHOOD_FOR_TITLE"),revisable=True),
            claim("R-INELIGIBLE",a("PERSONHOOD_FOR_TITLE","NO"),revisable=True),
        ],
        "rules":[
            rule("R-ALLOW",(a("DESIGNATED_BENEFICIARY"),
                            a("PERSONHOOD_FOR_TITLE")),a("TAKES_TITLE")),
            rule("R-DENY",(a("DESIGNATED_BENEFICIARY"),
                           a("PERSONHOOD_FOR_TITLE","NO")),a("TAKES_TITLE","NO")),
        ],
        "queries":[
            question("R-TITLE",a("TAKES_TITLE"),"BOTH"),
            question("R-CHEESE",a("COURT_MADE_OF_CHEESE"),"UNDETERMINED"),
        ],
        "priority":"CONFLICTING_NORMS_REQUIRE_SOURCE_REVIEW",
    }


def _rival():
    a=lambda p,sg="YES":scope("COURT_A","2051","EVENT_K",p,sg)
    b=lambda p,sg="YES":scope("COURT_B","2051","EVENT_K",p,sg)
    world=lambda p,sg="YES":scope("EXTERNAL_WORLD","2051","EVENT_K",p,sg)
    return {
        "id":"RIVAL_COURTS",
        "title":"Two courts watch the same impossible video and reach opposite conclusions",
        "fictional":True,
        "question":"Can two different court findings settle a single physical event?",
        "claims":[
            claim("C-A-ADMIT",a("CAMERA_ADMISSIBLE")),
            claim("C-A-FIND",a("COURT_FINDING_EVENT")),
            claim("C-B-EXCLUDE",b("CAMERA_ADMISSIBLE","NO")),
            claim("C-B-NOT-FIND",b("COURT_FINDING_EVENT","NO")),
            claim("C-PARTY-REALITY",world("EVENT_OCCURRED"),
                  source="PARTY_ALLEGATION"),
        ],
        "rules":[
            rule("C-A-DECIDE",(a("CAMERA_ADMISSIBLE"),
                               a("COURT_FINDING_EVENT")),
                 a("COURT_DECISION_EVENT")),
            rule("C-B-DECIDE",(b("CAMERA_ADMISSIBLE","NO"),
                               b("COURT_FINDING_EVENT","NO")),
                 b("COURT_DECISION_EVENT","NO")),
        ],
        "queries":[
            question("C-A",a("COURT_DECISION_EVENT"),"SUPPORTED"),
            question("C-B",b("COURT_DECISION_EVENT"),"REFUTED"),
            question("C-WORLD",world("EVENT_OCCURRED"),"UNDETERMINED"),
        ],
        "priority":"FORUM_FINDING_NOT_WORLD_FACT",
    }


def _ouroboros():
    a=lambda p,sg="YES":scope("LOOP_COURT","2099","ORDER_Z",p,sg)
    return {
        "id":"SELF_NULLIFYING_ORDER",
        "title":"The court declares its own order void if and only if its order is valid",
        "fictional":True,
        "question":"Can the order invalidate itself without proving every unrelated claim?",
        "claims":[claim("O-ISSUED",a("ORDER_VALID"),revisable=True)],
        "rules":[
            rule("O-SWALLOW",(a("ORDER_VALID"),),a("ORDER_VOID")),
            rule("O-REVERSE",(a("ORDER_VOID"),),a("ORDER_VALID","NO")),
            rule("O-CYCLE",(a("ORDER_VALID","NO"),),a("ORDER_VOID","NO")),
        ],
        "queries":[
            question("O-VALID",a("ORDER_VALID"),"BOTH"),
            question("O-VOID",a("ORDER_VOID"),"BOTH"),
            question("O-CHEESE",a("COURT_MADE_OF_CHEESE"),"UNDETERMINED"),
        ],
        "priority":"PARACONSISTENT_NO_EXPLOSION",
    }


def cases():
    return (_time(),_machine(),_rival(),_ouroboros())


def by_id(name):
    return next(x for x in cases() if x["id"]==name)
