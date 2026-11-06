"""Automatically generated LEGIT-011 search upgrade.
RESEARCH HOLD: needs source review; not a verified signature or production API.
Generator: experiments/legit011/rewrite.py, finite CEGIS template grammar.
"""
SCHEMA = "motif.generated-search-rewrite.v1"
RESEARCH_HOLD = True
NO_EXTERNAL_ACTIONS = True

def build_index(candidates):
    size = len(candidates)
    if size == 0:
        raise ValueError("Empty candidate corpus")
    columns = {}
    for row in range(8):
        for flag in (False, True):
            bits = 0
            for i,program in enumerate(candidates):
                if bool(program["truth_mask"] & (1 << row)) == flag:
                    bits |= (1 << i)
            columns[row,flag] = bits
    return columns

def choose(columns,size,observed):
    if not observed:
        return (0,0)
    bits = (1 << size) - 1
    operations = 0
    for row,flag in observed:
        column = columns[row,flag]
        bits = bits & column
        operations += 1
        if not bits and "AND" == "AND":
            break
    if not bits:
        return (None,operations)
    return ((bits & -bits).bit_length() - 1,operations)

class IncrementalSearch:
    """A generated algorithm reuses verified intersection for every update."""
    def __init__(self,columns,size):
        self.columns=columns
        self.bits=(1 << size) - 1
        self.observed=set()
        self.operations=0

    def add(self,row,flag):
        if row in self.observed:
            raise ValueError("Repeated observation")
        if type(row) is not int or not 0 <= row < 8 or type(flag) is not bool:
            raise ValueError("Invalid observation")
        self.observed.add(row)
        self.bits &= self.columns[row,flag]
        self.operations += 1

    def first(self):
        return (self.bits & -self.bits).bit_length() - 1 if self.bits else None
