"""MOTIF CONTEXT-GATE-001: bounded, non-deployed context-conditional policy selection.

The machine sees a fallible *observation*, never the synthetic world's hidden
regime. Full feedback is available only from separately provided train/validation
fixtures. Neither held-out fixture can influence learning. This is a classical
categorical lookup experiment, not an invented general learning algorithm.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from random import Random
from typing import Callable
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "selfmirror001"))
from selfmirror import Move, Policy
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "mathal001"))
from mathal import Step, Program, execute
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "fir001"))
from fir import Claim, FIRWorld, Warrant

CARRIER = "synthetic routing among MOTIF-003-shaped hypothetical moves"
DECODER = "fallible categorical signal and public action features"
BASE = Policy(0, 0)
SPECIALIST = Policy(2, 1)  # SELF-MIRROR-001's frozen selected candidate, NOT retuned here
SIGNALS = ("amber", "blue")  # opaque tokens, NOT truth labels


@dataclass(frozen=True)
class Episode:
    key: str
    signal: str
    moves: tuple[Move, ...]
    rewards: tuple[int, ...]   # inaccessible to the decision interface
    hidden_regime: str         # for evaluation/hostile controls ONLY

    def __post_init__(self):
        if (not self.key or not self.signal or not self.moves
                or len(self.moves) != len(self.rewards)
                or len(set(m.name for m in self.moves)) != len(self.moves)):
            raise ValueError("episode has invalid identifiers or incomplete feedback")


@dataclass(frozen=True)
class Choice:
    status: str
    selected: str | None
    expert: str | None
    receipt: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class Gate:
    # Frozen, interpretable map learned from TRAIN ONLY. A lookup, not a neural net.
    route: tuple[tuple[str, str], ...]
    support: tuple[tuple[str, int], ...]
    train_digest: str
    min_support: int
    min_gain: float

    def choose(self, signal: str, moves: tuple[Move, ...]) -> Choice:
        """No outcome, hidden regime, or training-set handle at inference time."""
        if signal not in dict(self.route):
            return Choice("HOLD_UNKNOWN_CONTEXT", None, None, (("signal", signal),))
        if not moves:
            return Choice("HOLD_NO_MOVES", None, None, (("signal", signal),))
        if any(m.truncated for m in moves):
            return Choice("HOLD_INCOMPLETE_FRONTIER", None, None, (("signal", signal),))
        if len({m.name for m in moves}) != len(moves):
            return Choice("HOLD_DUPLICATE_ACTION", None, None, (("signal", signal),))
        expert = dict(self.route)[signal]
        if expert == "HOLD":
            return Choice("HOLD_INSUFFICIENT_EVIDENCE", None, None, (("signal", signal),))
        policy = BASE if expert == "BASE" else SPECIALIST
        index = policy.choose(moves)
        return Choice("I_PROPOSAL_ONLY", moves[index].name, expert,
                      (("signal", signal), ("expert", expert),
                       ("train_digest", self.train_digest)))


def generate(split: str, size: int, reliability: float = 0.85,
             invert_sensor: bool = False) -> tuple[Episode, ...]:
    """Frozen synthetic fixture; success regime is distinct from noisy sensor."""
    if split not in {"train", "validation", "test", "ood"} or size < 1:
        raise ValueError("unsupported split or size")
    if not 0.0 <= reliability <= 1.0 or (invert_sensor and split != "ood"):
        raise ValueError("invalid sensor experiment")
    seed = int.from_bytes(sha256(f"contextgate001:{split}:v1".encode()).digest()[:8], "big")
    rng = Random(seed)
    examples = []
    for j in range(size):
        expansion = rng.random() < 0.5
        regime = "expansion" if expansion else "scarcity"  # privileged simulation mechanism
        observed_expansion = expansion if rng.random() < reliability else not expansion
        if invert_sensor:
            observed_expansion = not observed_expansion
        signal = "amber" if observed_expansion else "blue"
        moves, rewards = [], []
        for tag in "ABCD":
            immediate, afford, reach, noise = (rng.randint(0, 15), rng.randint(0, 5),
                                               rng.randint(1, 8), rng.randint(-2, 2))
            moves.append(Move(tag, immediate, afford, reach))
            # Reward differs for the two hidden world mechanisms.
            rewards.append(immediate + (3 if expansion else -4) * afford + reach + noise)
        examples.append(Episode(f"{split}-{j:04d}", signal, tuple(moves),
                                tuple(rewards), regime))
    return tuple(examples)


def digest(data: tuple[Episode, ...]) -> str:
    return sha256(json.dumps([
        (e.key,e.signal,e.hidden_regime,
         [(m.name,m.immediate,m.affordances,m.reach,m.truncated) for m in e.moves],
         e.rewards) for e in data], separators=(",", ":")).encode()).hexdigest()[:20]


def regret(policy: Policy, episode: Episode) -> int:
    selected = policy.choose(episode.moves)
    return max(episode.rewards) - episode.rewards[selected]


def train_gate(training: tuple[Episode, ...], min_support: int = 12,
               min_gain: float = 0.5) -> Gate:
    """Use TRAIN *only*: choose which expert minimizes regret per visible token.

    When support is too thin, hold instead of inventing information. The
    reference immediate policy remains the fall-back if specialist evidence
    is not convincing. Gate selection has no path to hidden_regime.
    """
    if min_support < 1 or min_gain < 0 or not training:
        raise ValueError("invalid training controls")
    mapping = []
    support = []
    for signal in SIGNALS:
        subgroup = [e for e in training if e.signal == signal]
        support.append((signal, len(subgroup)))
        if len(subgroup) < min_support:
            mapping.append((signal, "HOLD"))
            continue
        # Full feedback in TRAIN only: compute counterfactual regret exactly.
        gain = sum(regret(BASE,e) - regret(SPECIALIST,e) for e in subgroup) / len(subgroup)
        mapping.append((signal, "SPECIALIST" if gain >= min_gain else "BASE"))
    return Gate(tuple(mapping), tuple(support), digest(training), min_support, min_gain)


@dataclass(frozen=True)
class Score:
    cases: int
    covered: int
    mean_regret_covered: float | None
    mean_regret_all_with_hold_penalty: float
    misroutes: int


def evaluate(gate: Gate, cases: tuple[Episode,...], hold_penalty: int = 20) -> Score:
    if not cases or hold_penalty < 0:
        raise ValueError("evaluation needs data and declared penalty")
    total = 0
    covered = 0
    misroutes = 0
    regret_covered = 0
    for c in cases:
        result = gate.choose(c.signal,c.moves)
        if result.selected is None:
            total += hold_penalty
        else:
            covered += 1
            selected = [m.name for m in c.moves].index(result.selected)
            d = max(c.rewards) - c.rewards[selected]
            regret_covered += d
            total += d
            # Offline diagnostic only, never used in choice or learning:
            if (result.expert == "SPECIALIST") != (c.hidden_regime == "expansion"):
                misroutes += 1
    return Score(len(cases),covered,regret_covered/covered if covered else None,
                 total/len(cases),misroutes)


def policy_score(policy: Policy, cases: tuple[Episode, ...]) -> float:
    return sum(regret(policy,e) for e in cases)/len(cases)


def oracle_score(cases: tuple[Episode, ...]) -> float:
    """Privileged upper-bound control: forbidden to inference-time gate."""
    return sum(regret(SPECIALIST if e.hidden_regime == "expansion" else BASE,e)
               for e in cases)/len(cases)


@dataclass(frozen=True)
class Selection:
    gate: Gate
    validation: Score
    candidates: int
    status: str
    receipt: tuple[dict,...]


def choose_validation(training: tuple[Episode, ...], validation: tuple[Episode,...]) -> Selection:
    if not training or not validation or set(e.key for e in training) & set(e.key for e in validation):
        raise ValueError("disjoint training and validation required")
    # Fixed grammar. No held-out test object appears in the function signature.
    trials = [(minimum,gain) for minimum in (8,12,24)
              for gain in (0.0,0.5,1.0,2.0)]
    options = [(train_gate(training,n,g),n,g) for n,g in trials]
    # Objective pays a cost for HOLD, unlike reporting only covered regret.
    scored = [(evaluate(model,validation),n,g,model) for model,n,g in options]
    score,n,g,model = min(scored,key=lambda x:(x[0].mean_regret_all_with_hold_penalty,
                                               -x[0].covered,x[1],x[2]))
    claim=Claim("Proposed context-dependent choice of synthetic policies",
                "train:"+digest(training)+";validation:"+digest(validation))
    world=FIRWorld(CARRIER,DECODER)
    run=execute(world,Program("route-hypothesis",(Step("propose",claim),),CARRIER,DECODER))
    if not run.applied or claim not in run.world.ideas or claim in run.world.facts:
        raise AssertionError("FIR proposal boundary crossed")
    receipts=tuple(run.receipts)+({"operation":"validation_choice","min_support":n,
                                   "min_gain":g,"options_checked":len(options),
                                   "validation_digest":digest(validation),
                                   "selected_routes":model.route},)
    return Selection(model,score,len(options),"I_VALIDATION_SELECTION",receipts)


def audit(selection: Selection, test: tuple[Episode,...], ood: tuple[Episode,...]) -> dict:
    """Holdouts used ONLY after gate and hyperparameters are frozen."""
    held=evaluate(selection.gate,test)
    attacked=evaluate(selection.gate,ood)
    baseline_test=policy_score(BASE,test)
    baseline_ood=policy_score(BASE,ood)
    global_test=policy_score(SPECIALIST,test)
    global_ood=policy_score(SPECIALIST,ood)
    train_scope="test:"+digest(test)
    local_claim=Claim("Gate has lower mean hold-penalized regret than BASE on this finite test fixture",train_scope)
    proposal=execute(FIRWorld(CARRIER,DECODER),Program("finite-observation",
                      (Step("propose",local_claim),),CARRIER,DECODER))
    receipts=list(selection.receipt)+list(proposal.receipts)
    role="I"
    if held.mean_regret_all_with_hold_penalty < baseline_test:
        admission=execute(proposal.world,Program("finite-admission",
             (Step("admit",local_claim,Warrant("finite_computation",
                 "exact synthetic fixture: "+train_scope,train_scope)),),CARRIER,DECODER))
        assert admission.applied
        receipts+=list(admission.receipts)
        role="F_LOCAL"
    damaged = attacked.mean_regret_all_with_hold_penalty > baseline_ood
    general="HOLD_SENSOR_SHIFT_REGRESSION" if damaged else "HOLD_UNPROVEN_TRANSFER"
    receipts.append({"operation":"refuse","claim":"universal adaptive policy improvement",
                     "reason":"sensor inversion worsens regret" if damaged else "finite synthetic tests cannot prove transfer",
                     "ood_digest":digest(ood),"status":general})
    return {"status":general,"finite_test_role":role,"test":held,"ood":attacked,
            "base_test":baseline_test,"base_ood":baseline_ood,
            "global_specialist_test":global_test,"global_specialist_ood":global_ood,
            "oracle_regime_test":oracle_score(test),
            "receipts":tuple(receipts)}


def preview_motif003(rows: list[dict], observed_signal: str, gate: Gate) -> Choice:
    """Read-only adapter, no hidden reward, no agent update, no action execution."""
    moves=tuple(Move(str(r['operator'])+":"+repr(tuple(r['roles'])),
                     int(r['immediate_delta']),len(r['new_affordances']),
                     int(r['reachable_after_first_move']),bool(r.get('truncated',False)))
                for r in rows)
    return gate.choose(observed_signal,moves)


def demonstration() -> dict:
    training=generate('train',240)
    validation=generate('validation',120)
    test=generate('test',200)
    ood=generate('ood',200,invert_sensor=True)
    selected=choose_validation(training,validation)
    result=audit(selected,test,ood)
    return {
        "experiment":"CONTEXT-GATE-001",
        "scope":"local synthetic full-feedback policy routing only",
        "source":"MOTIF SELF-MIRROR-001's frozen BASE and specialist policy",
        "routing_status":selected.status,
        "observed_context_routes":selected.gate.route,
        "hyperparameter_candidates":selected.candidates,
        "split_digests":{k:digest(v) for k,v in (("train",training),("validation",validation),
                                               ("test",test),("sensor_inversion",ood))},
        "validation_mean_regret":selected.validation.mean_regret_all_with_hold_penalty,
        "test_mean_regret":{"gate":result['test'].mean_regret_all_with_hold_penalty,
                            "base":result['base_test'],
                            "global_specialist":result['global_specialist_test'],
                            "privileged_regime_oracle":result['oracle_regime_test']},
        "sensor_inversion_mean_regret":{"gate":result['ood'].mean_regret_all_with_hold_penalty,
                                        "base":result['base_ood'],
                                        "global_specialist":result['global_specialist_ood']},
        "covered_test":result['test'].covered,
        "covered_ood":result['ood'].covered,
        "finite_test_status":result['finite_test_role'],
        "generalization_status":result['status'],
        "trained_on_test_or_ood":False,
        "external_actions":0,
        "autonomous_self_modification":False,
        "claim":"classical conditional lookup; not general environment recognition",
    }


if __name__=='__main__':
    print(json.dumps(demonstration(), indent=2,sort_keys=True))
