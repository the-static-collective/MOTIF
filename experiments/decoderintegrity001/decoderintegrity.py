"""DECODER-INTEGRITY-001: audit a fallible policy-routing observation channel.

Classical rolling agreement monitor with conservative Hoeffding controls.
No hidden environment labels, outcome rewards, online weight tuning, proof
checker, real-world sensor, or external actions enter the live decision path.
The independent audit channel is a *synthetic assumption*, not authenticated.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from hashlib import sha256
from math import log, sqrt
from random import Random
from pathlib import Path
from typing import Iterable
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'contextgate001'))
sys.path.insert(0, str(ROOT / 'fir001'))
from contextgate import BASE, Choice, Episode, Gate, choose_validation, generate, regret, policy_score
from fir import Claim, FIRWorld, Warrant

TOKENS = ('amber', 'blue')


def swap(token: str) -> str:
    if token not in TOKENS:
        raise ValueError('unknown sensor token')
    return 'blue' if token == 'amber' else 'amber'


@dataclass(frozen=True)
class WitnessPair:
    """Observed pair only. No rewards, hidden regimes, or target labels."""
    event_key: str
    primary: str
    audit: str | None
    primary_origin: str = 'synthetic-primary'
    audit_origin: str = 'synthetic-audit'

    def __post_init__(self):
        if not self.event_key or self.primary not in TOKENS:
            raise ValueError('event key and primary token required')
        if self.audit is not None and self.audit not in TOKENS:
            raise ValueError('invalid audit token')
        if not self.primary_origin or not self.audit_origin:
            raise ValueError('origin metadata required')


def audit_pairs(split: str, size: int, primary_inverted: bool = False,
                audit_inverted: bool = False, audit_reliability: float = 0.90,
                missing_every: int = 0, shared_origin: bool = False,
                episode_reliability: float = 0.85) -> tuple[tuple[Episode, WitnessPair], ...]:
    """Synthetic fixture constructor. Hidden label used ONLY to synthesize a
    fallible second instrument, never passed to Monitor or Gate.

    Flip conditions reuse identical underlying episodes/noise for fair pairing.
    """
    if not 0 <= audit_reliability <= 1 or missing_every < 0:
        raise ValueError('invalid audit fixture parameters')
    episodes = generate(split, size, reliability=episode_reliability)
    rng = Random(int.from_bytes(sha256(f'decoder001:audit:{split}:v1'.encode()).digest()[:8], 'big'))
    data = []
    for i, episode in enumerate(episodes):
        true_expansion = episode.hidden_regime == 'expansion'  # fixture only
        reference_expansion = true_expansion if rng.random() < audit_reliability else not true_expansion
        reference = 'amber' if reference_expansion else 'blue'
        primary = swap(episode.signal) if primary_inverted else episode.signal
        audit = swap(reference) if audit_inverted else reference
        if missing_every and (i+1) % missing_every == 0:
            audit = None
        pair = WitnessPair(episode.key, primary, audit,
                           'synthetic-same-source' if shared_origin else 'synthetic-primary',
                           'synthetic-same-source' if shared_origin else 'synthetic-audit')
        data.append((episode, pair))
    return tuple(data)


def pair_digest(pairs: Iterable[WitnessPair]) -> str:
    s = '|'.join(f'{p.event_key}:{p.primary}:{p.audit}:{p.primary_origin}:{p.audit_origin}'
                 for p in pairs)
    return sha256(s.encode()).hexdigest()[:20]


@dataclass(frozen=True)
class Calibration:
    count: int
    matches: int
    estimated_agreement: float
    lower_agreement: float
    digest: str
    confidence_budget: float


def calibrate(pairs: tuple[WitnessPair, ...], confidence_budget: float = 0.01,
              min_cases: int = 100) -> Calibration:
    """Freeze an agreement lower bound on CALIBRATION data only.
    Hoeffding is used without assumptions about hidden world labels, but
    independence across calibration events is an experimental assumption.
    """
    if not 0 < confidence_budget < 1 or len(pairs) < min_cases:
        raise ValueError('insufficient calibration or invalid confidence budget')
    if len({p.event_key for p in pairs}) != len(pairs):
        raise ValueError('duplicate calibration events')
    if any(p.audit is None or p.audit_origin == p.primary_origin for p in pairs):
        raise ValueError('calibration requires two declared, available source origins')
    matches = sum(p.primary == p.audit for p in pairs)
    p = matches/len(pairs)
    lower = max(0.0, p - sqrt(log(2/confidence_budget)/(2*len(pairs))))
    return Calibration(len(pairs), matches, p, lower, pair_digest(pairs), confidence_budget)


@dataclass(frozen=True)
class Decision:
    status: str
    selected: str | None
    expert: str | None
    trusted_context: bool
    evidence_count: int


@dataclass
class Monitor:
    calibration: Calibration
    window: int = 48
    max_checks: int = 300
    alarm_budget: float = 0.01
    max_missing_run: int = 10
    state: str = 'WATCH'
    checks: int = 0
    missing_run: int = 0
    records: deque = field(default_factory=deque, repr=False)
    seen: set[str] = field(default_factory=set, repr=False)
    alarm_event: str | None = None
    receipts: list[dict] = field(default_factory=list)
    world: FIRWorld = field(init=False, repr=False)
    working_assumption: Claim = field(init=False)

    def __post_init__(self):
        if self.window < 2 or self.max_checks < 1 or not 0 < self.alarm_budget < 1 or self.max_missing_run < 1:
            raise ValueError('invalid sequential monitor configuration')
        self.records = deque(maxlen=self.window)
        self.world = FIRWorld('synthetic witnessed context channel', 'primary/audit agreement')
        self.working_assumption = Claim('Primary context decoder adequate for conditional routing',
                                        'ASSUMPTION: calibration:'+self.calibration.digest)
        self.world.propose(self.working_assumption)
        self.world.admit(self.working_assumption, Warrant('assumption',
                         'working assumption; NOT proof of independent sensor correctness'))
        self.receipts.extend(self.world.receipts)

    @property
    def threshold(self) -> float:
        # Time-uniform (finite horizon) lower-tail guard using a union bound.
        return max(0.0, self.calibration.lower_agreement -
                   sqrt(log(self.max_checks/self.alarm_budget)/(2*self.window)))

    def decide(self, gate: Gate, primary: str, moves) -> Decision:
        """Call BEFORE a new event's audit feedback. Never sees hidden label."""
        if self.state == 'HOLD_SHARED_ORIGIN':
            return Decision('HOLD_SHARED_ORIGIN',None,None,False,self.checks)
        if self.state == 'HOLD_MISSING_AUDIT':
            return Decision('HOLD_MISSING_AUDIT',None,None,False,self.checks)
        if self.state == 'HOLD_MONITOR_HORIZON':
            return Decision('HOLD_MONITOR_HORIZON',None,None,False,self.checks)
        if self.state == 'DEGRADED':
            if not moves or any(m.truncated for m in moves) or len(set(m.name for m in moves)) != len(moves):
                return Decision('HOLD_INCOMPLETE_OR_DUPLICATE_MOVES',None,None,False,self.checks)
            i = BASE.choose(moves)
            return Decision('I_DEGRADED_BASE_PROPOSAL',moves[i].name,'BASE',False,self.checks)
        choice: Choice = gate.choose(primary, moves)
        return Decision(choice.status,choice.selected,choice.expert,
                        choice.status == 'I_PROPOSAL_ONLY',self.checks)

    def _reopen(self, reason: str, event: str):
        if self.working_assumption in self.world.facts:
            start = len(self.world.receipts)
            self.world.reopen(self.working_assumption, reason)
            self.receipts.extend(self.world.receipts[start:])
        self.alarm_event = event
        self.receipts.append({'operation':'decoder_hold','event':event,'state':self.state,'reason':reason})

    def observe(self, pair: WitnessPair):
        """Delayed, *separate* second-instrument reading after decision."""
        if pair.event_key in self.seen:
            raise ValueError('duplicate event cannot update monitor twice')
        self.seen.add(pair.event_key)
        if self.state != 'WATCH':
            self.receipts.append({'operation':'observe_while_held','event':pair.event_key,'state':self.state})
            return
        if pair.audit_origin == pair.primary_origin:
            self.state = 'HOLD_SHARED_ORIGIN'
            self._reopen('declared audit source shares origin with primary', pair.event_key)
            return
        if pair.audit is None:
            self.missing_run += 1
            self.receipts.append({'operation':'audit_absent','event':pair.event_key,'missing_run':self.missing_run})
            if self.missing_run >= self.max_missing_run:
                self.state = 'HOLD_MISSING_AUDIT'
                self._reopen('reference unavailable for too many consecutive decisions',pair.event_key)
            return
        self.missing_run=0
        self.records.append(int(pair.primary == pair.audit))
        if len(self.records) < self.window:
            return
        if self.checks >= self.max_checks:
            self.state = 'HOLD_MONITOR_HORIZON'
            self._reopen('declared repeated-testing budget exhausted',pair.event_key)
            return
        self.checks+=1
        rate=sum(self.records)/self.window
        if rate < self.threshold:
            # An exact local observation is admitted, NOT a cause or universal diagnosis.
            scope='window:'+pair.event_key+':'+str(self.window)
            observation = Claim('Rolling primary/audit agreement below predeclared bound', scope)
            start=len(self.world.receipts)
            self.world.propose(observation)
            self.world.admit(observation,Warrant('finite_computation',
                f'{sum(self.records)}/{self.window} < {self.threshold:.8f}',scope))
            self.receipts.extend(self.world.receipts[start:])
            self.receipts.append({'operation':'agreement_alarm','event':pair.event_key,
                                  'rate':rate,'threshold':self.threshold,
                                  'calibration_digest':self.calibration.digest,
                                  'mechanism_claim':'I_ONLY'})
            self.state='DEGRADED'
            self._reopen('unexpected agreement drop; cause remains unproved',pair.event_key)


@dataclass(frozen=True)
class Score:
    cases: int
    covered: int
    mean_regret_penalized: float
    mean_regret_covered: float | None
    alarm_index: int | None
    final_state: str
    first_n_statuses: tuple[str,...]
    receipts: tuple[dict,...]


def simulate(gate: Gate, calibration: Calibration, data: tuple[tuple[Episode,WitnessPair],...],
             *, window: int = 48, max_checks: int = 300, hold_penalty: int = 20,
             max_missing_run: int = 10) -> Score:
    """Prequential: choose current action from old monitor state; only then
    read this episode's reference. Outcomes are used strictly for OFFLINE scoring.
    """
    if not data or hold_penalty < 0 or any(pair.event_key != ep.key for ep,pair in data):
        raise ValueError('invalid evaluation fixture')
    monitor=Monitor(calibration,window=window,max_checks=max_checks,max_missing_run=max_missing_run)
    total=0
    covered=0
    statuses=[]
    for ep,pair in data:
        d=monitor.decide(gate,pair.primary,ep.moves)
        statuses.append(d.status)
        if d.selected is None:
            total+=hold_penalty
        else:
            chosen=[m.name for m in ep.moves].index(d.selected)
            total+=max(ep.rewards)-ep.rewards[chosen]
            covered+=1
        monitor.observe(pair)
    return Score(len(data),covered,total/len(data),
                 ((total-(len(data)-covered)*hold_penalty)/covered if covered else None),
                 None if monitor.alarm_event is None else next(i for i,(_,p) in enumerate(data)
                      if p.event_key==monitor.alarm_event),
                 monitor.state,tuple(statuses[:16]),tuple(monitor.receipts))


def classical_signal_frequency_control(data: tuple[tuple[Episode,WitnessPair],...]) -> float:
    """Single-channel statistic: sign inversion is not identifiable when
    contexts are balanced. This control records ONLY primary amber frequency.
    """
    return sum(pair.primary=='amber' for _,pair in data)/len(data)


def demonstrate() -> dict:
    route=choose_validation(generate('train',240),generate('validation',120)).gate
    cal_fixture=audit_pairs('train',320)
    cal=calibrate(tuple(pair for _,pair in cal_fixture))
    clean=audit_pairs('test',240)
    shifted=audit_pairs('ood',240,primary_inverted=True)
    tandem=audit_pairs('ood',240,primary_inverted=True,audit_inverted=True)
    audit_only=audit_pairs('ood',240,audit_inverted=True)
    clean_score=simulate(route,cal,clean)
    shifted_score=simulate(route,cal,shifted)
    tandem_score=simulate(route,cal,tandem)
    audit_only_score=simulate(route,cal,audit_only)
    unguarded_clean = sum(max(ep.rewards)-ep.rewards[
        next(i for i,m in enumerate(ep.moves) if m.name==route.choose(pair.primary,ep.moves).selected)]
        for ep,pair in clean)/len(clean)
    unguarded_shifted = sum(max(ep.rewards)-ep.rewards[
        next(i for i,m in enumerate(ep.moves) if m.name==route.choose(pair.primary,ep.moves).selected)]
        for ep,pair in shifted)/len(shifted)
    return {
        'experiment':'DECODER-INTEGRITY-001',
        'scope':'synthetic independently-noised retrospective audit; NOT verified independence',
        'frozen_route':route.route,
        'calibration':{'size':cal.count,'agreement':round(cal.estimated_agreement,4),
                       'lower':round(cal.lower_agreement,4),'digest':cal.digest},
        'monitor':{'window':48,'max_checks':300,'threshold':round(Monitor(cal).threshold,4)},
        'clean':{'monitored_regret':clean_score.mean_regret_penalized,
                 'unguarded_regret':unguarded_clean,'final_state':clean_score.final_state,
                 'alarm_event_index':clean_score.alarm_index},
        'inverted_primary':{'monitored_regret':shifted_score.mean_regret_penalized,
                  'unguarded_regret':unguarded_shifted,'base_regret':policy_score(BASE,tuple(ep for ep,_ in shifted)),
                  'final_state':shifted_score.final_state,'alarm_event_index':shifted_score.alarm_index},
        'both_sensors_inverted':{'monitored_regret':tandem_score.mean_regret_penalized,
                   'final_state':tandem_score.final_state,'alarm_event_index':tandem_score.alarm_index},
        'audit_only_inverted':{'monitored_regret':audit_only_score.mean_regret_penalized,
                   'final_state':audit_only_score.final_state,'alarm_event_index':audit_only_score.alarm_index,
                   'warning':'agreement drop cannot identify WHICH instrument changed'},
        'single_sensor_amber_frequency':{'clean_ood':classical_signal_frequency_control(audit_pairs('ood',240)),
              'inverted_ood':classical_signal_frequency_control(shifted)},
        'finite_evidence_only':True,'real_actions':0,'automatic_code_changes':0,
        'generalization':'HOLD: correlated witness failures and unverified provenance remain undetected',
    }


if __name__=='__main__':
    import json
    print(json.dumps(demonstrate(),indent=2,sort_keys=True))
