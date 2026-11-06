"""Generated MOTIF-012 certified graph solver. DRAFT RESEARCH ONLY.
Generated from verified LEGIT-011 search source by typed CEGIS.
No file, network, shell or production permissions.
"""
RESEARCH_HOLD = True
NO_EXTERNAL_ACTIONS = True
SCHEMA = "motif.generated-graph-search.v1"

def solve(columns,size,ordered):
    memo = {}
    result = {}
    operations = 0
    for facts,parents in ordered:
        if not facts:
            bits = (1 << size) - 1
        else:
            before = parents[0]
            added = next(item for item in facts if item not in before)
            bits = memo[before] & columns[added]
            operations += 1
        memo[facts] = bits
        if not bits:
            result[facts] = None
        else:
            result[facts] = (bits & -bits).bit_length() - 1
    return result, {"bitset_updates":operations}
