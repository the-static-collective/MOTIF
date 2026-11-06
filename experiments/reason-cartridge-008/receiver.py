"""Independent source-owner certification; not part of the learner.

The learner receives five labels and is not permitted to query these 27
heldout truth values before committing its typed macro proposal.
"""
from __future__ import annotations
from discover import HOLD, validate, expanded_eval, digest
from source import Case, WITHHELD_MASKS, bfs_truth, SOURCE_REVISION


class Receiver:
    def __init__(self,raw):
        self.packet=validate(raw)
        self.digest=None
        self.passed=False
        self.admitted=False

    def preview(self,cases):
        if (not isinstance(cases,tuple)
                or len(cases)!=len(WITHHELD_MASKS)
                or any(not isinstance(c,Case) or c.variant!="cedar" for c in cases)
                or {c.mask for c in cases}!=set(WITHHELD_MASKS)
                or self.packet["source_revision"]!=SOURCE_REVISION):
            raise HOLD("Independent certification requires all 27 withheld source cases")
        spec=self.packet["proposed_extension"]["program"]
        program=(tuple(spec["triple"]),tuple(spec["pair"]))
        receipts=[]
        for c in sorted(cases,key=lambda q:q.mask):
            observed=bfs_truth(c)
            guessed=expanded_eval(program,c.mask)
            receipts.append({"mask":c.mask,"expected":observed,
                             "predicted":guessed,"passes":observed==guessed})
        errors=sum(not r["passes"] for r in receipts)
        self.passed=(errors==0)
        self.digest=digest({"method":self.packet["checksum_sha256"],
                            "source":SOURCE_REVISION,"receipts":receipts})
        return {"schema":"motif.reason.eight.certificate.v1",
                "cases":len(receipts),"errors":errors,
                "review_digest":self.digest,
                "teacher_training_did_not_contain_heldout":True,
                "local_fixture_review_not_human_approval":True,
                "real_world_authority":False}

    def admit(self, decision, checksum):
        if (decision!="ADMIT_READ_ONLY" or not self.passed or checksum!=self.digest):
            raise HOLD("Method requires independently passed digest-bound local approval")
        self.admitted=True

    def suggest(self, case):
        if (not self.admitted or not isinstance(case,Case)
                or case.variant not in ("quartz","willow")):
            raise HOLD("Undeployed, out-of-contract or in-training graph input")
        spec=self.packet["proposed_extension"]["program"]
        program=(tuple(spec["triple"]),tuple(spec["pair"]))
        return {"stage":"SUGGEST_ONLY",
                "prediction":expanded_eval(program,case.mask),
                "source_variant":case.variant,
                "external_execution":False,"real_world_authority":False}
