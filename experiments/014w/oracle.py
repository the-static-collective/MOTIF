"""MOTIF-014 independent stochastic simulator: witnesses of witnesses.

The oracle alone knows latent calibration truths, realized controls, actual
outcomes, source reliability, and auditor quality. Learner receives only
PublicCalibration and PublicTrial objects, not World/SecretTrial.

A FALLIBLE audit channel reports whether calibration claims are true and
whether a commanded actuator actually complied. The learner infers audit
quality jointly with witness quality, compliance and causal structure.
Some entire channels deliberately change during validation and test.

All outcomes are seeded Bernoulli draws; these are *not* real witnesses.
"""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
from random import Random

VERSION="witness-of-witnesses-v1"
FAMILIES=("FIRST","SECOND","AND","XOR","SOURCE_SHIFT",
          "AUDIT_SHIFT","COMPLIANCE_SHIFT")
SEEDS=(11,23,37,41)
PORTS=((False,False),(False,True),(True,False),(True,True))
ORIGINS=("s0","s1")
PHASES=("calibration","train","validation","test")


@dataclass(frozen=True)
class Witness:
    origin: str
    reporter: str
    says_success: bool
    provenance: str="SYNTHETIC_UNVERIFIED_WITNESS"


@dataclass(frozen=True)
class PublicCalibration:
    ticket: str
    reporters: tuple[Witness,...]
    audit_says_success: bool | None
    provenance: str="SYNTHETIC_UNADJUDICATED_CALIBRATION"


@dataclass(frozen=True)
class PublicTrial:
    ticket: str
    before: frozenset[tuple[str,...]]
    roles: tuple[str,str]
    requested: tuple[bool,bool]
    audit_says_first_port_applied: bool | None
    reporters: tuple[Witness,...]
    provenance: str="SYNTHETIC_UNADJUDICATED_INTERVENTION"


@dataclass(frozen=True)
class SecretCalibration:
    public: PublicCalibration
    truth: bool


@dataclass(frozen=True)
class SecretTrial:
    public: PublicTrial
    actually_applied: tuple[bool,bool]
    truth: bool


@dataclass(frozen=True)
class World:
    family: str
    seed: int
    predicate_names: tuple[str,str]
    source_truthfulness: tuple[float,float]
    auditor_truthfulness: float
    actuator_compliance: float


def _seed(*parts):
    raw=":".join(map(str,(VERSION,*parts))).encode()
    return int.from_bytes(sha256(raw).digest()[:8],"big")


def create_world(family,seed):
    if family not in FAMILIES or type(seed) is not int or seed<0:
        raise ValueError("Unregistered stochastic world")
    rng=Random(_seed(family,seed,"params"))
    predicates=tuple("q"+sha256(
        f"{VERSION}:{family}:{seed}:port{i}".encode()).hexdigest()[:20]
                     for i in (0,1))
    return World(family,seed,predicates,
                 (round(rng.uniform(.84,.94),4),
                  round(rng.uniform(.17,.33),4)),
                 round(rng.uniform(.75,.90),4),
                 round(rng.uniform(.72,.90),4))


def rates(spec,phase):
    r0,r1=spec.source_truthfulness
    q=spec.auditor_truthfulness
    c=spec.actuator_compliance
    if phase in ("validation","test"):
        if spec.family=="SOURCE_SHIFT":
            r0=.18
        if spec.family=="AUDIT_SHIFT":
            q=.28
        if spec.family=="COMPLIANCE_SHIFT":
            c=.28
    return r0,r1,q,c


def _flip(rng,reliability,truth):
    return truth if rng.random()<reliability else not truth


def _reporters(rng,truth,source_rates):
    reports=[]
    for index,(origin,reliability) in enumerate(zip(ORIGINS,source_rates)):
        if rng.random()<.12:
            continue
        says=_flip(rng,reliability,truth)
        reports.append(Witness(origin,origin,says))
        if index==0 and rng.random()<.65:
            # Republished, same upstream event: NOT independent evidence.
            reports.append(Witness(origin,"s0_forward",says))
    return tuple(reports)


def hidden_rule(family,applied):
    if family in ("FIRST","SOURCE_SHIFT","AUDIT_SHIFT","COMPLIANCE_SHIFT"):
        return applied[0]
    if family=="SECOND":
        return applied[1]
    if family=="AND":
        return applied[0] and applied[1]
    if family=="XOR":
        return applied[0]!=applied[1]
    raise ValueError("Unsupported hidden causal program")


def probability(spec,applied):
    return .12+.76*int(hidden_rule(spec.family,applied))


def calibration_case(spec,index):
    if type(index) is not int or index<0:
        raise ValueError("Invalid calibration identifier")
    rng=Random(_seed(spec.family,spec.seed,"calibration",index))
    r0,r1,q,_=rates(spec,"calibration")
    truth=rng.random()<.5
    sources=_reporters(rng,truth,(r0,r1))
    audit=(_flip(rng,q,truth) if rng.random()>=.10 else None)
    public=PublicCalibration(f"cal-{index}",sources,audit)
    return SecretCalibration(public,truth)


def intervention_case(spec,phase,index,request=None):
    if phase not in ("train","validation","test") or type(index) is not int or index<0:
        raise ValueError("Invalid experimental phase/index")
    if request is None:
        request=PORTS[index%4]
    if (not isinstance(request,tuple) or len(request)!=2
            or any(type(x) is not bool for x in request)):
        raise ValueError("Explicit two-Boolean control pair required")
    rng=Random(_seed(spec.family,spec.seed,phase,index))
    r0,r1,q,c=rates(spec,phase)
    actual_first=request[0] if rng.random()<c else not request[0]
    applied=(actual_first,request[1])  # port 2 actuator is verified exact
    truth=rng.random()<probability(spec,applied)
    source=_reporters(rng,truth,(r0,r1))
    audit=( _flip(rng,q,actual_first) if rng.random()>=.20 else None )
    actor=f"w14_{phase}_{index}_actor"
    target=f"w14_{phase}_{index}_target"
    before={("role_actor",actor),("role_target",target),
            ("pending",target)}
    if request[0]:
        before.add((spec.predicate_names[0],actor))
    if request[1]:
        before.add((spec.predicate_names[1],target))
    public=PublicTrial(f"{phase}-{index}",frozenset(before),
                       (actor,target),request,audit,source)
    return SecretTrial(public,applied,truth)


def calibration_set(spec,n):
    return tuple(calibration_case(spec,i) for i in range(n))


def trial_set(spec,phase,n):
    return tuple(intervention_case(spec,phase,i) for i in range(n))


def true_command_probability(spec,request,phase):
    _,_,_,compliance=rates(spec,phase)
    p0=(compliance*probability(spec,request)
        +(1-compliance)*probability(spec,(not request[0],request[1])))
    return p0
