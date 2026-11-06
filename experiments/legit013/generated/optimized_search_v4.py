"""MOTIF LEGIT-013 generated source: conditional reasoning optimization.
Research draft; finite templates only; no independent deployment authority.
"""
RESEARCH_HOLD = True
NO_EXTERNAL_ACTIONS = True

def solve(columns,size,ordered):
    full = (1 << size) - 1
    memo = {}
    output = {}
    intersections = 0
    skips = 0
    for facts,parents in ordered:
        if not facts:
            bits = full
        else:
            prior = parents[0]
            new_fact = next(x for x in facts if x not in prior)
            p = memo[prior]
            c = columns[new_fact]
            if p == full:
                bits = c
                skips += 1
            elif p == 0:
                bits = 0
                skips += 1
            else:
                bits = p & c
                intersections += 1
        memo[facts] = bits
        output[facts] = ((bits & -bits).bit_length()-1) if bits else None
    return output, {"bitset_intersections":intersections,"branch_skips":skips}
