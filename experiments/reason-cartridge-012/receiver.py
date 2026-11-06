"""Independent quote/annotation owner review (separate from classifier).

Tests two unseen judicial opinions: seized Ulysses (1933) and barrels of
Coca-Cola (1916). This verifies only very short manually anchored quotations
and curator roles; it does NOT evaluate full-text legal interpretation.
"""
from __future__ import annotations

from classifier import HOLD,validate,classify,digest
from corpus import passages,OPINIONS
from review_keys import LABELS,SEALED_KEYS,TRAIN_KEYS


def exact_source(p):
    originals={x["span_id"]:x for x in passages(True)+passages(False)}
    return isinstance(p,dict) and p.get("span_id") in originals and p==originals[p["span_id"]]


class Receiver:
    def __init__(self,raw):
        self.method=validate(raw)
        self.approved=False
        self.review_digest=None
        self.passed=False

    def preview(self,withheld):
        if (not isinstance(withheld,tuple) or len(withheld)!=len(SEALED_KEYS)
                or tuple(p.get("span_id") for p in withheld)!=SEALED_KEYS
                or any(not exact_source(p) or OPINIONS[p["case_id"]]["train"]
                       for p in withheld)):
            raise HOLD("Independent unfamiliar book/soda source observations required")
        for train in self.method["training_evidence"]:
            if train["label"]!=LABELS[train["span_id"]][0]:
                raise HOLD("Learner was taught an unapproved annotation")
        outcomes=[]
        for span in withheld:
            gold=LABELS[span["span_id"]]
            proposal=classify(self.method,span["text"])
            expected_type=gold[0]
            accepted=proposal["status"]=="PROPOSE_TYPE" and proposal["type"]==expected_type
            held=proposal["status"]=="HOLD_UNKNOWN_OR_AMBIGUOUS_TYPE"
            correct_hold=held and expected_type not in self.method["learned_feature_routes"].values()
            outcomes.append({
                "span_id":span["span_id"],"case_id":span["case_id"],
                "source_url":span["opinion_url"],
                "reference_category":expected_type,
                "proposed_category":proposal["type"],
                "accepted_correct":accepted,
                "unsupported_type_abstained":correct_hold,
                "error":not (accepted or correct_hold),
            })
        errors=sum(x["error"] for x in outcomes)
        self.passed=errors==0
        self.review_digest=digest({
            "method_sha256":self.method["checksum_sha256"],"evaluation":outcomes})
        return {
            "schema":"motif.reason.actual-opinion-review.v1",
            "new_opinion_cases":2,
            "unseen_excerpts":len(outcomes),
            "correct_accepted":sum(x["accepted_correct"] for x in outcomes),
            "correct_abstentions":sum(x["unsupported_type_abstained"] for x in outcomes),
            "errors":errors,"outcomes":outcomes,
            "review_digest":self.review_digest,
            "source_checks_local_pinned_corpus_not_live_site":True,
            "source_citations_are_not_legal_conclusions":True,
            "human_lawyer_or_court_review":False,
        }

    def admit(self,decision,review_digest):
        if decision!="ADMIT_READ_ONLY" or not self.passed or review_digest!=self.review_digest:
            raise HOLD("No independent source-bound local approval")
        self.approved=True

    def suggest(self,span):
        if not self.approved or not exact_source(span):
            raise HOLD("No admitted/known source-owned opinion fragment")
        classified=classify(self.method,span["text"])
        if classified["status"]!="PROPOSE_TYPE":
            return {
                "stage":"HOLD_UNFAMILIAR_LEGAL_EPISTEMIC_CATEGORY",
                "citation":span["citation"],"opinion_url":span["opinion_url"],
                "fragment":span["text"],"legal_advice":False,
                "real_world_authority":False}
        return {
            "stage":"SUGGEST_ONLY",
            "category":classified["type"],
            "fragment":span["text"],
            "case_id":span["case_id"],
            "citation":span["citation"],
            "court":span["court"],
            "paragraph_locator":span["paragraph_locator"],
            "opinion_url":span["opinion_url"],
            "full_opinion_interpreted":False,
            "current_law_not_verified":True,
            "legal_advice":False,"external_execution":False,
            "real_world_authority":False}
