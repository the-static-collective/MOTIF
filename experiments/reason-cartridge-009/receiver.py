"""REASON-009 independent owner/reviewer: source BFS, not the inventor's oracle.

A source-owned reviewer checks all teaching observations and 8 completely
unseen holdout graph worlds. It additionally checks the 24 acquisition worlds
AFTER synthesis. No source truths cross into the learner during grammar search.
"""
from __future__ import annotations

from grammar import HOLD,validate,interpret,digest,ACQUISITION,HOLDOUT
from source import Case,bfs,SOURCE_REVISION


class Receiver:
    def __init__(self,raw):
        self.method=validate(raw)
        self.review_digest=None
        self.passed=False
        self.admitted=False

    def preview(self,cases):
        if (not isinstance(cases,tuple) or len(cases)!=len(HOLDOUT)
                or any(not isinstance(c,Case) or c.family!=self.method["family"]
                       or c.variant!="cedar" or c.mask not in HOLDOUT for c in cases)
                or {c.mask for c in cases}!=set(HOLDOUT)
                or self.method["source_revision"]!=SOURCE_REVISION):
            raise HOLD("Disjoint eight-case independent certification is mandatory")
        family=self.method["family"]
        witness_checks=[]
        for row in self.method["public_observations"]:
            expected=bfs(Case(row["mask"],family))
            witness_checks.append({
                "mask":row["mask"],"source_authored_label":row["reachable"],
                "independent_BFS":expected,"matches":expected==row["reachable"],
            })
        if not all(row["matches"] for row in witness_checks):
            raise HOLD("Public teacher transcript disagrees with independent source")
        ast=self.method["program"]["ast"]
        # Certify withheld masks before any read-only method admission.
        heldout_receipts=[]
        for c in sorted(cases,key=lambda c:c.mask):
            expected=bfs(c)
            predicted=interpret(ast,c.mask)
            heldout_receipts.append({
                "mask":c.mask,"BFS":expected,"proposed":predicted,
                "correct":expected==predicted,
                "not_a_real_world_witness":True,
            })
        errors=sum(not item["correct"] for item in heldout_receipts)
        # Separate, post-synthesis complete-acquisition audit.
        acquisition_errors=sum(
            interpret(ast,mask)!=bfs(Case(mask,family))
            for mask in ACQUISITION
        )
        self.passed=(errors==0 and acquisition_errors==0)
        self.review_digest=digest({
            "proposed_method":self.method["checksum_sha256"],
            "source_revision":SOURCE_REVISION,
            "source_witnesses":witness_checks,
            "heldout":heldout_receipts,
            "acquisition_errors":acquisition_errors,
        })
        return {
            "schema":"motif.reason.grammar-009.owner-certificate.v1",
            "source_family":family,
            "public_source_witnesses_checked":len(witness_checks),
            "heldout_cases":len(heldout_receipts),"heldout_errors":errors,
            "post_synthesis_acquisition_audit_cases":len(ACQUISITION),
            "post_synthesis_acquisition_errors":acquisition_errors,
            "all_32_feature_states_match":errors==0 and acquisition_errors==0,
            "review_digest":self.review_digest,
            "independent_of_learner_during_synthesis":True,
            "local_fixture_review_not_human_admission":True,
            "real_world_authority":False,
        }

    def admit(self,decision,review_digest):
        if (decision!="ADMIT_READ_ONLY" or not self.passed
                or review_digest!=self.review_digest):
            raise HOLD("Uncertified method cannot be locally admitted")
        self.admitted=True

    def suggest(self,c):
        if (not self.admitted or not isinstance(c,Case)
                or c.family!=self.method["family"] or c.variant=="cedar"):
            raise HOLD("Only explicitly admitted renamed future scenarios")
        return {"stage":"SUGGEST_ONLY",
                "family":c.family,"mask":c.mask,
                "prediction":interpret(self.method["program"]["ast"],c.mask),
                "external_execution":False,"real_world_authority":False}
