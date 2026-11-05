"""MOTIF-013 oracle: genuinely stochastic *simulated* witnesses and interventions.

Only benchmark.py and unit tests may import this file. The probabilistic
learner never imports the oracle, knows the true mechanism, receives latent
outcomes, or receives the hidden reliabilities.

Pseudorandom Bernoulli outcomes, compliance failures, noisy sources, missing
reports, forwarded duplicate witnesses, and a held-out regime change are
reproducible through a frozen seed. These are statistical random draws in a
simulator, NOT real-world noise, cryptographic randomness or proof of cause.
"""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
from random import Random

VERSION="probabilistic-witness-v1"
FAMILIES=("FIRST","SECOND","AND","OR","XOR","SHIFT")
SEEDS=(11,23,37,41,59)
PAIRS=((False,False),(False,True),(True,False),(True,True))
ORIGINS=("source_0","source_1","source_2")
CALIBRATION_PER_ORIGIN=60
CALIBRATION_PER_ACTUATOR=80

@dataclass(frozen=True)
class Witness:
    origin: str
    reporter: str
    claim: bool
    provenance: str="SYNTHETIC_WITNESS"

@dataclass(frozen=True)
class PublicTrial:
    ticket: str
    before: frozenset[tuple[str,...]]
    roles: tuple[str,str]
    commanded: tuple[bool,bool]
    audited_applied: tuple[bool,bool] | None
    witnesses: tuple[Witness,...]
    provenance: str="SYNTHETIC_UNADJUDICATED"

@dataclass(frozen=True)
class SecretTrial:
    public: PublicTrial
    realized: tuple[bool,bool]
    truth: bool

@dataclass(frozen=True)
class Calibration:
    """Aggregate results of a DIFFERENT, adjudicated synthetic calibration.

    No individual world-outcome truth from the model-training/test episodes
    appears in this object.
    """
    source_accuracy_counts: tuple[tuple[str,int,int],...]
    actuator_compliance_counts: tuple[tuple[int,int,int],...]
    provenance: str="INDEPENDENT_SYNTHETIC_CALIBRATION"

@dataclass(frozen=True)
class World:
    family: str
    seed: int
    control_predicates: tuple[str,str]
    source_accuracies: tuple[float,...]
    compliance: tuple[float,float]
    # Evaluator-only. NEVER pass a World object into witness_model.py.

def _seed(*parts):
    raw=":".join(map(str,(VERSION,*parts))).encode()
    return int.from_bytes(sha256(raw).digest()[:8],"big")

def world(family:str,seed:int)->World:
    if family not in FAMILIES or type(seed) is not int or seed<0:
        raise ValueError("Unregistered synthetic witness world")
    rng=Random(_seed(family,seed,"world"))
    names=tuple("q"+sha256(f"{VERSION}:{family}:{seed}:port:{i}".encode()
                             ).hexdigest()[:20] for i in range(2))
    return World(family,seed,names,
                 (round(rng.uniform(.86,.96),4),
                  round(rng.uniform(.59,.76),4),
                  round(rng.uniform(.12,.31),4)),
                 (round(rng.uniform(.75,.89),4),
                  round(rng.uniform(.78,.93),4)))

def true_mechanism(family:str,phase:str)->str:
    if family=="SHIFT":
        return "FIRST" if phase=="train" else "SECOND"
    return family

def _rule(program:str,a:bool,b:bool)->bool:
    return {"FIRST":a,"SECOND":b,"AND":a and b,
            "OR":a or b,"XOR":a!=b}[program]

def success_probability(spec:World,applied:tuple[bool,bool],phase:str)->float:
    program=true_mechanism(spec.family,phase)
    return .15+.70*int(_rule(program,*applied))

def _coin(rng:Random,p:float)->bool:
    return rng.random()<p

def calibration(spec:World)->Calibration:
    # Separate adjudicated source samples; the training model can see only
    # aggregate correct/total and never the oracle's hidden source accuracy.
    source=[]
    for i,origin in enumerate(ORIGINS):
        rng=Random(_seed(spec.family,spec.seed,"source_calibration",i))
        matched=0
        for _ in range(CALIBRATION_PER_ORIGIN):
            truth=_coin(rng,.5)
            reported=truth if _coin(rng,spec.source_accuracies[i]) else not truth
            matched+=reported==truth
        source.append((origin,matched,CALIBRATION_PER_ORIGIN))
    actuators=[]
    for i in range(2):
        rng=Random(_seed(spec.family,spec.seed,"actuator_calibration",i))
        matched=sum(_coin(rng,spec.compliance[i])
                    for _ in range(CALIBRATION_PER_ACTUATOR))
        actuators.append((i,matched,CALIBRATION_PER_ACTUATOR))
    return Calibration(tuple(source),tuple(actuators))

def trial(spec:World,phase:str,index:int,command=None)->SecretTrial:
    if phase not in ("train","validation","test") or type(index) is not int or index<0:
        raise ValueError("Unregistered synthetic trial")
    if command is None:
        command=PAIRS[index%4]
    if (not isinstance(command,tuple) or len(command)!=2 or
            any(type(x) is not bool for x in command)):
        raise ValueError("Explicit two-port Boolean command required")
    rng=Random(_seed(spec.family,spec.seed,phase,index,"trial"))
    actual=tuple(command[i] if _coin(rng,spec.compliance[i])
                 else not command[i] for i in range(2))
    truth=_coin(rng,success_probability(spec,actual,phase))
    actor=f"w13_{phase}_{index}_actor"
    target=f"w13_{phase}_{index}_target"
    facts={("role_actor",actor),("role_target",target),("pending",target)}
    # BEFORE is a graph of the *command*, not a falsely asserted effect.
    for i,flag in enumerate(command):
        if flag:
            facts.add((spec.control_predicates[i],actor if i==0 else target))
    observations=[]
    for i,origin in enumerate(ORIGINS):
        if _coin(rng,.14):  # Missing evidence is explicitly allowed.
            continue
        claim=truth if _coin(rng,spec.source_accuracies[i]) else not truth
        observations.append(Witness(origin,origin,claim))
        if i==0:
            # Reposted hearsay, NOT a second independent witness:
            observations.append(Witness(origin,"source_0_forwarded",claim))
    # Some synthetic actuator receipts are missing. Never interpret the
    # *requested* control setting as a verified realized intervention.
    audited=(actual if phase!="test" and _coin(rng,.85) else None)
    public=PublicTrial(f"{phase}-{index}",frozenset(facts),
                       (actor,target),command,audited,tuple(observations))
    return SecretTrial(public,actual,truth)

def records(spec:World,phase:str,count:int)->tuple[SecretTrial,...]:
    if type(count) is not int or not 1<=count<=500:
        raise ValueError("Bounded synthetic set size only")
    return tuple(trial(spec,phase,i) for i in range(count))

def oracle_plan_probability(spec:World,command:tuple[bool,bool],
                            phase:str)->float:
    """Evaluator-only unattainable oracle upper bound: true program and compliance."""
    total=0.0
    for a,b in PAIRS:
        weight=1.0
        for i,applied in enumerate((a,b)):
            weight*=spec.compliance[i] if applied==command[i] else (
                1-spec.compliance[i])
        total+=weight*success_probability(spec,(a,b),phase)
    return total
