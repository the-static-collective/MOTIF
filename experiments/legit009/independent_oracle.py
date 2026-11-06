"""LEGIT-009 evaluator only — independent finite Boolean semantics and proof.

Do not import the synthesizer. The checker executes each candidate NAND DAG
using a distinct Boolean interpreter and returns the first counterexample.
Independent minimum-gate proof exhausts all possible normalized NAND DAGs
shorter than the candidate. Both the semantics and search grammar are
bounded to TWO input Boolean functions and at most FIVE NAND gates.

This cannot certify any physical source or infer a new axiom.
"""
from __future__ import annotations

from hashlib import sha256
import itertools
import json

TASKS=("DISAGREEMENT","AGREEMENT","IMPLIES","NOR")


class IndependentVerifier:
    def __init__(self,task_id):
        if task_id not in TASKS:
            raise ValueError("Unrecognized verifier problem")
        self.task_id=task_id

    def truth(self,a,b):
        if type(a) is not bool or type(b) is not bool:
            raise ValueError("Oracle accepts only Boolean inputs")
        if self.task_id=="DISAGREEMENT":
            return a!=b
        if self.task_id=="AGREEMENT":
            return a==b
        if self.task_id=="IMPLIES":
            return (not a) or b
        if self.task_id=="NOR":
            return not (a or b)
        raise AssertionError("Unknown task")

    def label_initial(self,a,b):
        return self.truth(a,b)

    def interpret(self,gates,output,a,b):
        registers=[a,b]
        for pair in gates:
            if (not isinstance(pair,(tuple,list)) or len(pair)!=2 or
                any(type(pin) is not int or not 0<=pin<len(registers) for pin in pair)):
                raise ValueError("Invalid NAND program")
            left,right=pair
            registers.append(not(registers[left] and registers[right]))
        if type(output) is not int or not 0<=output<len(registers):
            raise ValueError("Bad circuit output")
        return registers[output]

    def check(self,gates,output):
        for a,b in itertools.product((False,True),repeat=2):
            observed=self.interpret(gates,output,a,b)
            should=self.truth(a,b)
            if observed is not should:
                return (a,b,should)
        return None

    def proof(self,gates,output):
        if self.check(gates,output) is not None:
            raise AssertionError("Invalid circuit")
        n=len(gates)
        if n>5:
            raise ValueError("Proof budget exceeded")
        truth_masks=[
            sum(int(self.truth(bool(i//2),bool(i%2)))<<i for i in range(4))]
        goal=truth_masks[0]
        examined=0
        # Independent enumeration of *all* shorter programs, including all
        # 0-gate wire outputs. Commutative NAND pin pairs are canonicalized.
        input_masks=(0b1100,0b1010)
        def expand(registers,remaining):
            nonlocal examined
            if remaining==0:
                examined+=1
                return registers[-1]==goal
            for x in range(len(registers)):
                for y in range(x,len(registers)):
                    nxt=15^(registers[x]&registers[y])
                    if expand(registers+(nxt,),remaining-1):
                        return True
            return False

        for length in range(n):
            if length==0:
                examined+=2
                if goal in input_masks:
                    raise AssertionError("Nonminimal: direct input exists")
            elif expand(input_masks,length):
                raise AssertionError("Shorter NAND circuit exists")
        return {
            "semantic_spec":self.task_id,
            "truth_mask":goal,
            "verified_full_input_domain_size":4,
            "shorter_programs_examined":examined,
            "shorter_NAND_DAG_found":False,
            "minimum_NAND_gates_in_declared_grammar":n,
            "minimality_is_for_typed_NAND_only":True,
            "not_real_world_authentication":True,
        }


def canonical_sop_xor():
    """A conventional sum-of-products XOR using exactly 5 NAND gates.

    Wire 0=a, 1=b, 2=~a, 3=~b, 4=~(a&~b),
    5=~(~a&b), 6=(a&~b)|(~a&b).
    """
    return [[0,0],[1,1],[0,3],[1,2],[4,5]]


def direct_builtin_disagreement(a,b):
    """Strong conventional Boolean XOR reference; no NAND instruction cap."""
    return a!=b
