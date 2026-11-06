"""Source-owned independent evaluation of a proposed graph method."""
from __future__ import annotations
from compiler import HOLD, validate, classify, digest, REVISION
from source import Case, CERT, bfs_truth, SOURCE_REVISION

class Receiver:
    def __init__(self, raw):
        self.packet = validate(raw)
        self.review_digest = None
        self.passed = False
        self.admitted = False

    def preview(self, cases):
        if (not isinstance(cases, tuple) or len(cases) != len(CERT)
            or any(not isinstance(c, Case) or c.variant != "cedar"
                   or c.mask not in CERT for c in cases)
            or {c.mask for c in cases} != set(CERT)
            or SOURCE_REVISION != REVISION):
            raise HOLD("Independent withheld evaluation coverage required")
        program = tuple(tuple(p) for p in self.packet["program"])
        checks = []
        for c in sorted(cases, key=lambda c:c.mask):
            expected = bfs_truth(c)
            actual = classify(program, c.mask)
            checks.append((c.mask, expected, actual))
        failures = sum(expected != actual for _, expected, actual in checks)
        self.passed = failures == 0
        self.review_digest = digest({"method":self.packet["checksum_sha256"],
                                     "checks":checks, "source":SOURCE_REVISION})
        return {"cases":len(checks), "errors":failures,
                "review_digest":self.review_digest,
                "teacher_not_called_on_withheld_during_learning":True,
                "human_authority":False}

    def admit(self, decision, review_digest):
        if (decision != "ADMIT_READ_ONLY" or not self.passed
                or review_digest != self.review_digest):
            raise HOLD("No successful independent local read-only approval")
        self.admitted = True

    def suggest(self, case):
        if not self.admitted or not isinstance(case, Case) or case.variant == "cedar":
            raise HOLD("Not admitted for this heldout-renamed task")
        program = tuple(tuple(p) for p in self.packet["program"])
        return {"stage":"SUGGEST_ONLY", "prediction":classify(program,case.mask),
                "external_execution":False, "real_world_authority":False}
