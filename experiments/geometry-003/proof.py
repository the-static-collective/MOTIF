"""Exact symbolic conditional proof for the nine-point construction.

This proves algebraic vector identities over rational coefficient vectors.
It assumes the circumcenter is equidistant from the three vertices and that
H=A+B+C-2O. It does NOT by itself prove a synthesized macro meets those
assumptions for arbitrary triangles, nor validate real-world measurements.
"""
from fractions import Fraction as F

VARS = ("A", "B", "C", "O")


def v(**terms):
    unknown=set(terms)-set(VARS)
    if unknown:
        raise ValueError('unknown symbolic vectors: '+repr(unknown))
    return tuple(F(terms.get(k, 0)) for k in VARS)


def add(x,y):
    return tuple(a+b for a,b in zip(x,y))


def sub(x,y):
    return tuple(a-b for a,b in zip(x,y))


def scale(x,k):
    return tuple(c*F(k) for c in x)


def symbolic_certificate():
    A,B,C,O=[v(**{name:1}) for name in VARS]
    H=sub(add(add(A,B),C),scale(O,2))
    N=scale(add(O,H),F(1,2))
    expected_N=scale(sub(add(add(A,B),C),O),F(1,2))
    identities={
        'N_is_midpoint_of_O_and_H':N==scale(add(O,H),F(1,2)),
        'N_is_half_of_A_plus_B_plus_C_minus_O':N==expected_N,
        'N_minus_midpoint_AB_equals_half_C_minus_O':
            sub(N,scale(add(A,B),F(1,2)))==scale(sub(C,O),F(1,2)),
        'N_minus_midpoint_BC_equals_half_A_minus_O':
            sub(N,scale(add(B,C),F(1,2)))==scale(sub(A,O),F(1,2)),
        'N_minus_midpoint_CA_equals_half_B_minus_O':
            sub(N,scale(add(C,A),F(1,2)))==scale(sub(B,O),F(1,2)),
    }
    assert all(identities.values())
    return {
        'conditional_symbolic_vector_identities':identities,
        'premises':[
            'O is equidistant from A, B, and C in a Euclidean metric',
            'H=A+B+C-2O follows from O being the circumcenter',
            'the exact rational linear-vector identities are valid for all A,B,C,O',
        ],
        'consequence':'three side midpoints lie at squared distance R^2/4 from N',
        'proof_scope':'symbolic identities plus explicitly stated premises; not a proof of an arbitrary synthesized program',
    }
