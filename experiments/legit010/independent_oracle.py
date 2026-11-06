"""Independent finite Boolean oracle for self-composed reason cartridges.
3/4-input exact truth tables, plus fully enumerable classical controls.
"""
from itertools import product, permutations

TRI_TASKS=("ODD_PARITY3","ALL3","ANY3","NOR3",
           "PAIR_AGREE_AND_THIRD","PAIR_DISAGREE_AND_THIRD")
UNREACHABLE="MAJORITY3"

def truth3(kind,a,b,c):
    if any(type(x) is not bool for x in (a,b,c)):
        raise ValueError("Expected Boolean inputs")
    if kind=="ODD_PARITY3": return a ^ b ^ c
    if kind=="ALL3": return a and b and c
    if kind=="ANY3": return a or b or c
    if kind=="NOR3": return not(a or b or c)
    if kind=="PAIR_AGREE_AND_THIRD": return (a==b) and c
    if kind=="PAIR_DISAGREE_AND_THIRD": return (a!=b) and c
    if kind=="MAJORITY3": return int(a)+int(b)+int(c)>=2
    raise ValueError("Unknown semantic task")

def interpret(gates,output,inputs):
    wires=list(inputs)
    if len(inputs) not in (2,3,4) or any(type(v) is not bool for v in inputs):
        raise ValueError("Unsupported input domain")
    if not isinstance(gates,(list,tuple)) or len(gates)>36:
        raise ValueError("Unsupported program")
    for pair in gates:
        if (not isinstance(pair,(list,tuple)) or len(pair)!=2 or
            any(type(i) is not int or i<0 or i>=len(wires) for i in pair)):
            raise ValueError("Illegal gate reference")
        wires.append(not(wires[pair[0]] and wires[pair[1]]))
    if type(output) is not int or not 0<=output<len(wires):
        raise ValueError("Bad output reference")
    return wires[output]

class TernaryVerifier:
    def __init__(self,name):
        if name not in TRI_TASKS+(UNREACHABLE,):
            raise ValueError("Unknown 3-variable task")
        self.name=name
    def truth(self,a,b,c):
        return truth3(self.name,a,b,c)
    def label_initial(self,a,b,c):
        return self.truth(a,b,c)
    def check(self,gates,output):
        for x in product((False,True),repeat=3):
            y=self.truth(*x)
            if interpret(gates,output,x) is not y:
                return (*x,y)
        return None

class QuaternaryVerifier:
    def check(self,gates,output):
        for x in product((False,True),repeat=4):
            if interpret(gates,output,x) is not (x[0]^x[1]^x[2]^x[3]):
                return (*x,x[0]^x[1]^x[2]^x[3])
        return None

def independent_minimal_composition(library,task):
    """Exhaustive classical 16x16x2x6 operator search; separate code."""
    if set(library)!=set(range(16)):
        raise ValueError("Require full binary function library")
    goal=TernaryVerifier(task)
    best=None
    checked=0
    for first in range(16):
        for second in range(16):
            cost=library[first]["gate_count"]+library[second]["gate_count"]
            for association in ("LEFT","RIGHT"):
                for order in permutations((0,1,2)):
                    checked+=1
                    okay=True
                    for tup in product((False,True),repeat=3):
                        x,y,z=(tup[k] for k in order)
                        def op(mask,u,v):
                            return bool((mask>>(2*int(u)+int(v)))&1)
                        got=(op(second,op(first,x,y),z)
                             if association=="LEFT" else
                             op(second,x,op(first,y,z)))
                        if got!=goal.truth(*tup):
                            okay=False
                            break
                    if okay and (best is None or cost<best):
                        best=cost
    return {"task":task,"least_total_NAND_gates":best,
            "candidate_compositions_checked":checked,
            "strong_exact_classical_composition":True}

def flat_nand_search(task,limit=5):
    """Finite source primitive-only solver; not a general lower bound."""
    if type(limit) is not int or not 0<=limit<=5:
        raise ValueError("Bad comparison budget")
    test=TernaryVerifier(task)
    target=sum(int(test.truth(*x))<<i for i,x in
               enumerate(product((False,True),repeat=3)))
    roots=(0b11110000,0b11001100,0b10101010)
    checked=3
    def go(masks,left):
        nonlocal checked
        if left==0:
            checked+=1
            return masks[-1]==target
        for i in range(len(masks)):
            for j in range(i,len(masks)):
                if go(masks+((255^(masks[i]&masks[j])),),left-1):
                    return True
        return False
    found=target in roots
    for count in range(1,limit+1):
        if found: break
        found=go(roots,count)
    return {"task":task,"limit":limit,"within_budget":found,
            "terminal_candidates_examined":checked}
