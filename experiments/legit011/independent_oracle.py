"""LEGIT-011 independent evaluator for a self-generated search rewrite.

This module does not import or construct the candidate rewrite. The gold
algorithm is a straightforward scan of the cost-sorted 3-bit program catalog,
plus a separately implemented conventional bitset index.

There are exactly 3^8 = 6,561 possible partial three-input truth tables:
at each row, unknown/false/true. Every search rewrite is checked on ALL
6,561 states. This is a complete finite proof for this narrow catalog only.
"""
from __future__ import annotations

from itertools import product

ROWS=8
CASES=3**ROWS

def states():
    """Each row is either unobserved, false or true."""
    for values in product((-1,0,1),repeat=ROWS):
        yield tuple((i,bool(v)) for i,v in enumerate(values) if v!=-1)

def checked_query(q):
    if not isinstance(q,(tuple,list)):
        raise ValueError("Invalid partial truth table")
    seen=set()
    for item in q:
        if (not isinstance(item,(tuple,list)) or len(item)!=2 or
            type(item[0]) is not int or not 0<=item[0]<8 or
            type(item[1]) is not bool or item[0] in seen):
            raise ValueError("Contradictory/unknown observation")
        seen.add(item[0])
    return tuple(q)

class ScanOracle:
    def __init__(self,rows):
        if not rows or len(rows)>3072 or any(
                type(r.get("truth_mask")) is not int or
                not 0<=r["truth_mask"]<=255 for r in rows):
            raise ValueError("Missing finite program specification")
        self.masks=tuple(r["truth_mask"] for r in rows)

    def query(self,partial):
        checked_query(partial)
        comparisons=0
        for i,mask in enumerate(self.masks):
            okay=True
            for row,wanted in partial:
                comparisons+=1
                if bool(mask&(1<<row)) is not wanted:
                    okay=False
                    break
            if okay:
                return i,comparisons
        return None,comparisons

    def challenge(self,ask):
        for partial in states():
            expected=self.query(partial)[0]
            got=ask(partial)
            if got!=expected:
                return {"partial":[list(x) for x in partial],
                        "expected_index":expected,
                        "candidate_index":got}
        return None

class StrongClassicalIndex:
    """Independent classical indexed control; no candidate generator import."""
    def __init__(self,rows):
        self.n=len(rows)
        self.cols={}
        self.membership_checks=0
        for row in range(ROWS):
            for val in (False,True):
                bits=0
                for j,rec in enumerate(rows):
                    self.membership_checks+=1
                    if bool(rec["truth_mask"]&(1<<row)) is val:
                        bits |= 1<<j
                self.cols[row,val]=bits

    def select(self,observed):
        checked_query(observed)
        mask=(1<<self.n)-1
        intersections=0
        for row,flag in observed:
            mask &= self.cols[row,flag]
            intersections+=1
            if not mask:
                return None,intersections
        return ((mask&-mask).bit_length()-1,intersections) if mask else (None,intersections)

    def session(self):
        return IndexedSession(self)

class IndexedSession:
    """Conventional incremental bitset reduction. Strong matched baseline."""
    def __init__(self,index):
        self.index=index
        self.bits=(1<<index.n)-1
        self.seen={}
        self.operations=0
    def add(self,row,flag):
        if (type(row) is not int or not 0<=row<ROWS or
                type(flag) is not bool or row in self.seen):
            raise ValueError("Unexpected or duplicate observation")
        self.seen[row]=flag
        self.bits &= self.index.cols[row,flag]
        self.operations+=1
    def first(self):
        return (self.bits&-self.bits).bit_length()-1 if self.bits else None

def exact_all_states(scan,ask):
    failures=[]
    comparisons=0
    for partial in states():
        correct,probes=scan.query(partial)
        comparisons+=probes
        got=ask(partial)
        if got!=correct:
            failures.append({"q":partial,"wanted":correct,"got":got})
            if len(failures)>=12:
                break
    return {"states_checked":CASES if not failures else None,
            "errors":failures,"complete":not failures,
            "scan_candidate_row_checks":comparisons}

def independent_update_check(operation):
    """Full four-row bit-level proof, independent of rewritten source."""
    observed=[]
    for old,new in product((False,True),repeat=2):
        result=operation(old,new)
        if type(result) is not bool:
            raise ValueError("Unrecognized update semantics")
        observed.append(result)
        if result is not (old and new):
            return {"complete":False,"counterexample":{
                "old_member":old,"new_member":new,"expected":old and new,
                "observed":result}}
    return {"complete":True,"tested":4,
            "property":"membership_next = membership_previous AND new_evidence",
            "inductive_claim":"The intersection of all observed requirements equals the surviving candidate set."}
