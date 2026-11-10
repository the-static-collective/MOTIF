"""QC-015: distinguish repeated action/state cycles from useful repetition.

A structural cycle is detected only when the same p actions and state sequence
repeat twice with no observed capability/resource gain; confirmed no-new-facts
requires an actual observation sensor, otherwise it remains a SUSPECTED cycle.
Pure, bounded research kernel, no effects in either world.
"""
from __future__ import annotations
from dataclasses import dataclass,field
from collections import deque
from hashlib import sha256
import json

VITALS=frozenset(('health','food','drink','energy'))
POSSIBLE=('CONFIRMED_NO_INFORMATION_CYCLE','SUSPECTED_CYCLE_VIEW_UNKNOWN')


def seal(x):
    return sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()


@dataclass(frozen=True)
class FieldState:
    xy: tuple[int,int]
    inventory: tuple[tuple[str,int],...]=()
    capabilities: tuple[str,...]=()
    vital: tuple[tuple[str,int],...]=()
    step: int=0

    def __post_init__(self):
        if (len(self.xy)!=2 or not all(isinstance(v,int) for v in self.xy)
            or self.step<0 or len({k for k,_ in self.inventory})!=len(self.inventory)
            or len({k for k,_ in self.vital})!=len(self.vital)
            or any(k in VITALS or not isinstance(v,int) for k,v in self.inventory)
            or any(k not in VITALS or not isinstance(v,int) for k,v in self.vital)
            or len(set(self.capabilities))!=len(self.capabilities)):
            raise ValueError('Invalid typed state or duplicate keys')

    @property
    def structural(self):
        return (self.xy,tuple(sorted(self.inventory)),tuple(sorted(self.capabilities)))

    @property
    def fingerprint(self):
        return seal(self.structural)

    def vital_dict(self):
        return dict(self.vital)


@dataclass(frozen=True)
class FieldStep:
    before: FieldState
    action: str
    after: FieldState
    observed_new_facts: int | None
    source_ref: str

    def __post_init__(self):
        if (not self.action or not self.source_ref
            or self.after.step<=self.before.step
            or (self.observed_new_facts is not None and
                (not isinstance(self.observed_new_facts,int) or
                 self.observed_new_facts<0))):
            raise ValueError('Out-of-order or unsupported transition')

    @property
    def pin(self):
        return seal((self.before.fingerprint,self.action,self.after.fingerprint,
                     self.observed_new_facts,self.source_ref,
                     self.before.step,self.after.step))


@dataclass(frozen=True)
class CycleAlert:
    period: int
    repetitions: int
    detected_step: int
    action_pattern: tuple[str,...]
    location_pattern: tuple[tuple[int,int],...]
    evidence_pins: tuple[str,...]
    status: str
    vital_debt: tuple[tuple[str,int],...]
    new_information: int | None
    question: str
    effective_actions_taken: int=0
    physical_world_claim: bool=False


@dataclass
class CycleMonitor:
    """Bounded periods 2..12. Unknown information yields SUSPECTED, not HOLD."""
    max_period: int=7
    history: deque=field(default_factory=lambda:deque(maxlen=30))
    alerts: list[CycleAlert]=field(default_factory=list)
    last_alert_signature: str | None=None

    def __post_init__(self):
        if not 2<=self.max_period<=12:
            raise ValueError('Periods must be bounded')
        self.history=deque(self.history,maxlen=2*self.max_period+2)

    def observe(self,x:FieldStep):
        if self.history and self.history[-1].after.structural!=x.before.structural:
            raise ValueError('Unwitnessed state transition')
        self.history.append(x)
        data=list(self.history)
        for p in range(2,self.max_period+1):
            if len(data)<2*p:continue
            recent=data[-2*p:]
            actions=[v.action for v in recent]
            if actions[:p]!=actions[p:]:continue
            states=[recent[0].before.structural]+[v.after.structural for v in recent]
            if not all(states[i]==states[i+p] for i in range(p+1)):
                continue
            new=[v.observed_new_facts for v in recent]
            if any(n is not None and n>0 for n in new):
                continue
            known=all(n is not None for n in new)
            status=POSSIBLE[0] if known else POSSIBLE[1]
            # Phase invariant: A-B and B-A are the same underlying orbit.
            orbit=tuple((actions[i],states[i]) for i in range(p))
            canonical=min(orbit[k:]+orbit[:k] for k in range(p))
            signature=seal((p,canonical,status))
            if self.last_alert_signature==signature:
                return None
            before=recent[0].before.vital_dict()
            after=recent[-1].after.vital_dict()
            debt=tuple(sorted((k,after.get(k,0)-before.get(k,0))
                              for k in set(before)|set(after)
                              if after.get(k,0)<before.get(k,0)))
            evidence=tuple(v.pin for v in recent)
            alert=CycleAlert(
                p,2,x.after.step,tuple(actions[:p]),
                tuple(v.before.xy for v in recent[:p]),
                evidence,status,debt,
                sum(new) if known else None,
                'What unmet need or unexplored possibility requires leaving '
                'this repeating action/state loop? Is there a safe observable '
                'alternative, or should the agent HOLD for a missing fact?')
            self.alerts.append(alert)
            self.last_alert_signature=signature
            return alert
        if x.observed_new_facts is not None and x.observed_new_facts>0:
            self.last_alert_signature=None
        return None


def from_qc011(episodes):
    """Older QC-011 recordings lack visibility gain, so alerts are suspected."""
    def snapshot(game):
        if not game.location.startswith('GAME_TILE:'):
            raise ValueError('Game-only coordinate required')
        xy=tuple(int(x) for x in game.location.split(':',1)[1].split(','))
        inv=dict(game.resources)
        return FieldState(
            xy,tuple(sorted((k,int(v)) for k,v in inv.items() if k not in VITALS)),
            tuple(game.capabilities),
            tuple(sorted((k,int(v)) for k,v in inv.items() if k in VITALS)),
            game.clock_tick)
    monitor=CycleMonitor()
    alerts=[]
    for e in episodes:
        x=FieldStep(snapshot(e.before),e.action,snapshot(e.after),None,e.pin)
        a=monitor.observe(x)
        if a:alerts.append(a)
    return {
        'steps':len(episodes),
        'alerts':tuple(a for a in alerts),
        'source_scope':'OBSERVED_GAME_ACTIONS__VISION_GAIN_UNAVAILABLE',
        'confirmed_no_info_cycles':0,
        'external_actions':0,
    }
