"""LEGIT-013: conventional optimized classical search-DAG baselines.

Independent from emitted source: this module imports no candidate generator.
The strongest control uses two standard Boolean algebra fast paths plus
the exact same indexed dynamic program as the previous legacy algorithm.

The point is to check whether MOTIF's discovered source rewrite genuinely
beats a strong programmer's obvious hand-tuned method, not an easy strawman.
"""
from __future__ import annotations

class StrongClassicalDP:
    def __init__(self,rows):
        self.size=len(rows)
        if not 1<=self.size<=3072:
            raise ValueError("Empty or giant graph")
        self.columns={}
        setup=0
        for row in range(8):
            for value in (False,True):
                bits=0
                for i,c in enumerate(rows):
                    setup+=1
                    if bool(c["truth_mask"]&(1<<row))==value:
                        bits|=1<<i
                self.columns[row,value]=bits
        self.index_bit_comparisons=setup

    def solve(self,ordered):
        full=(1<<self.size)-1
        states={}
        results={}
        ands=0
        absorbed=0
        for facts,parents in ordered:
            if not facts:
                result=full
            else:
                prior=parents[-1]  # different parent choice than candidate.
                changed=next(x for x in facts if x not in prior)
                old=states[prior]
                if old==0:
                    result=0
                    absorbed+=1
                elif old==full:
                    result=self.columns[changed]
                    absorbed+=1
                else:
                    result=old & self.columns[changed]
                    ands+=1
            states[facts]=result
            results[facts]=(result&-result).bit_length()-1 if result else None
        return results,{"bitset_intersections":ands,"branch_skips":absorbed,
                        "source":"CLASSICAL_MANUALLY_OPTIMIZED_DP"}

class UnoptimizedClassicalDP:
    def __init__(self,rows):
        self.impl=StrongClassicalDP(rows)
        self.columns=self.impl.columns
        self.size=len(rows)

    def solve(self,ordered):
        states={(): (1<<self.size)-1}
        result={():0}
        ands=0
        for facts,parents in ordered:
            if not facts:continue
            previous=parents[-1]
            extra=next(x for x in facts if x not in previous)
            bits=states[previous]&self.columns[extra]
            ands+=1
            states[facts]=bits
            result[facts]=(bits&-bits).bit_length()-1 if bits else None
        return result,{"bitset_intersections":ands,"branch_skips":0}
