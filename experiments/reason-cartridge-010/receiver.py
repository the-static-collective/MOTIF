"""Independent curated-source review and read-only admission for legal cards."""
from __future__ import annotations

from typed_lens import HOLD,validate,select,digest
from casebook import CASES
from tasks import Scenario,canonical_cards


def independently_check_card(card):
    """Identity check against complete curator-owned original card.

    This is *not* authentication of the original court's online document:
    it checks that the selected result belongs to the pinned curated corpus.
    """
    if not isinstance(card,dict) or card.get("case_id") not in CASES:
        return False
    return card in canonical_cards(card["case_id"])


class Receiver:
    def __init__(self,raw):
        self.method=validate(raw)
        self.approved=False
        self.passed=False
        self.review_digest=None

    def preview(self,heldout):
        if (not isinstance(heldout,tuple) or len(heldout)!=6
                or any(not isinstance(s,Scenario)
                       or s.id.split("-")[0] not in ("NARUTO","PIERSON")
                       for s in heldout)
                or len({s.id for s in heldout})!=6):
            raise HOLD("Independent non-training court cases required")
        checks=[]
        for question in heldout:
            prediction=select(self.method["selected_guard_program"],question)
            picked=prediction["selected"]
            valid=(picked is not None and picked["id"]==question.expected
                   and independently_check_card(picked))
            checks.append({"task":question.id,"expected":question.expected,
                           "actual":picked["id"] if picked else None,
                           "curated_source_verified":independently_check_card(picked),
                           "correct":valid,
                           "source_is_historical_not_current_law":True})
        mistakes=sum(not row["correct"] for row in checks)
        self.passed=mistakes==0
        self.review_digest=digest({
            "source_bound_method":self.method["checksum_sha256"],
            "source_card_checks":checks})
        return {"schema":"motif.reason.strange-law.holdout.v1",
                "cases":len(checks),"errors":mistakes,
                "court_families":2,"independent_curated_card_checks":checks,
                "review_digest":self.review_digest,
                "live_case_status_verified":False,
                "method_was_not_trained_on_holdout_questions":True,
                "automatic_human_or_court_approval":False}

    def admit(self,decision,review_digest):
        if (decision!="ADMIT_READ_ONLY" or not self.passed
                or review_digest!=self.review_digest):
            raise HOLD("No local source-curated independent review")
        self.approved=True

    def suggest(self,scenario):
        if not self.approved or not isinstance(scenario,Scenario):
            raise HOLD("No admitted source-owned legal card query")
        prediction=select(self.method["selected_guard_program"],scenario)
        selected=prediction["selected"]
        if selected is not None and not independently_check_card(selected):
            raise HOLD("A spoofed source card or fabricated court assertion")
        if selected is None:
            return {"stage":"SUGGEST_ONLY","status":"HOLD_OUTSIDE_VERIFIED_RECORD",
                    "source":None,"opinion":None,
                    "reason":"No unambiguous curated historical holding supports that query.",
                    "current_law_inferred":False,"legal_advice":False,
                    "external_actions":False}
        return {"stage":"SUGGEST_ONLY",
                "status":("HISTORICAL_HOLDING" if selected["voice"]=="COURT_MAJORITY"
                          and selected["kind"]=="HOLDING"
                          else "SEPARATE_VIEW_NOT_MAJORITY_HOLDING"),
                "source_id":selected["id"],
                "historical_paraphrase":selected["explanation"],
                "citation":selected["citation"],
                "opinion_url":selected["opinion_url"],
                "jurisdiction":selected["court"],
                "epistemic_type":selected["layer"],
                "current_law_inferred":False,"legal_advice":False,
                "external_actions":False,"real_world_authority":False}
