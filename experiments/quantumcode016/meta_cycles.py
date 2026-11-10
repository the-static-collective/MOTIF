"""QC-016 — bounded cycles OF cycles, with information/progress abstention.

A primitive cycle is a 2..7-action path that returns to the *same typed
structural game state*. A metacycle is a repeating motif of 2..7 *primitive
cycles*, observed 2..7 times. A-B-A-B is detected as [A,B] × 2 even when
each A or B is internally a valid movement loop and the concatenated action
sequence would not fit QC-015's 7-step base horizon.

We preserve (1) all original source-pinned steps, (2) possible resource/
knowledge gain, (3) task-relevant debt and (4) actual sensing uncertainty.
Known new observations veto a claim of a useless metacycle; unknown
visibility yields SUSPECTED, never automatic intervention.

This is a research observer, not an action dispatcher.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from hashlib import sha256
import json

try:
    from cycle_field import FieldStep
except ModuleNotFoundError:
    # supports imports from sibling QC-016 when invoked as a package
    from experiments.quantumcode015.cycle_field import FieldStep


def seal(v):
    return sha256(json.dumps(v,sort_keys=True,separators=(',',':'),
                             ensure_ascii=False).encode()).hexdigest()


@dataclass(frozen=True)
class Primitive:
    token: str
    actions: tuple[str,...]
    positions: tuple[tuple[int,int],...]
    start_step: int
    end_step: int
    receipts: tuple[str,...]
    witnessed_new_facts: int | None
    spent_vitals: tuple[tuple[str,int],...]
    anchor: str

    @property
    def action_count(self):
        return len(self.actions)


@dataclass(frozen=True)
class MetaAlert:
    layer: int
    primitive_motif_length: int
    motif_repetitions: int
    detected_step: int
    primitive_action_patterns: tuple[tuple[str,...],...]
    total_primitive_loops: int
    total_action_steps: int
    source_receipts: tuple[str,...]
    status: str
    vital_debt: tuple[tuple[str,int],...]
    question: str
    new_information: int | None
    authority: str="GAME_TRACE_ONLY"
    action_taken: bool=False


def quality(steps):
    """No time-dependent 'success' if inventory and capabilities return."""
    if not steps:
        raise ValueError('Empty cycle')
    start,end=steps[0].before,steps[-1].after
    if start.structural!=end.structural:
        return False
    if any(s.observed_new_facts is not None and s.observed_new_facts>0
           for s in steps):
        return False
    # Recovering health, energy or food is a meaningful observed gain even
    # when a patrol returns to the same position and inventory.
    if any(
        any(s.after.vital_dict().get(k,0)>s.before.vital_dict().get(k,0)
            for k in s.before.vital_dict().keys()|s.after.vital_dict().keys())
        for s in steps):
        return False
    return True


def primitive_from(steps):
    if not 2<=len(steps)<=7 or not quality(steps):
        return None
    first=steps[0].before
    signature=tuple((step.action,step.before.structural)
                    for step in steps)
    # All base loops start/end at the same anchor. Do NOT rotation-normalize
    # actions here: different entry phases imply different prerequisite edges.
    token=seal((first.structural,signature))
    start=first.vital_dict()
    end=steps[-1].after.vital_dict()
    debt=tuple(sorted((key,end.get(key,0)-start.get(key,0))
                      for key in start.keys()|end.keys()
                      if end.get(key,0)<start.get(key,0)))
    visibility=[x.observed_new_facts for x in steps]
    return Primitive(
        token,tuple(x.action for x in steps),
        tuple(x.before.xy for x in steps),
        first.step,steps[-1].after.step,
        tuple(x.pin for x in steps),
        sum(visibility) if all(x is not None for x in visibility) else None,
        debt,seal(first.structural))


@dataclass
class NestedMonitor:
    """Recognize 2..7 repeated loops OF 2..7 primitive loops.

    Earliest meta finding after 2*2 base loops. Maximum explored evidence:
    7 repetitions of 7 primitives, each at most 7 individual game actions.
    No O(gameplay-length^2) unbounded archive.
    """
    max_primitive_actions: int=7
    max_macro_period: int=7
    max_macro_repetitions: int=7
    pending: deque=field(default_factory=deque)
    primitives: deque=field(default_factory=deque)
    last_step: FieldStep | None=None
    emitted: set[str]=field(default_factory=set)
    alerts: list[MetaAlert]=field(default_factory=list)
    primitives_seen: int=0
    resets_due_to_information: int=0

    def __post_init__(self):
        if not 2<=self.max_primitive_actions<=7:
            raise ValueError('Primitive cap must be 2..7')
        if not 2<=self.max_macro_period<=7:
            raise ValueError('Macro motif cap must be 2..7')
        if not 2<=self.max_macro_repetitions<=7:
            raise ValueError('Macro repetitions must be 2..7')
        self.pending=deque(maxlen=self.max_primitive_actions+1)
        self.primitives=deque(maxlen=self.max_macro_period*self.max_macro_repetitions)

    def _reset_learning_window(self):
        self.pending.clear()
        self.primitives.clear()
        self.emitted.clear()

    def observe(self,step:FieldStep):
        if (self.last_step is not None and
            step.before.structural!=self.last_step.after.structural):
            raise ValueError('Source trace not contiguous')
        self.last_step=step
        if step.observed_new_facts is not None and step.observed_new_facts>0:
            self._reset_learning_window()
            self.resets_due_to_information+=1
            return None
        # Changes to capabilities/resources don't constitute a sealed cycle;
        # reopening from the *new* state is valuable, not failure.
        if self.pending and step.before.structural!=self.pending[-1].after.structural:
            self.pending.clear()
        self.pending.append(step)
        # Find a short closed circuit starting at oldest pending state.
        # If multiple boundaries exist the earliest closure wins, yielding
        # primitive, independently source-pinned loops.
        current=list(self.pending)
        for size in range(2,len(current)+1):
            if current[size-1].after.structural==current[0].before.structural:
                prefix=current[:size]
                loop=primitive_from(prefix)
                if loop is not None:
                    self.primitives.append(loop)
                    self.primitives_seen+=1
                    self.pending.clear()
                    for tail in current[size:]:
                        self.pending.append(tail)
                    return self._meta_alert()
        # Once the anchor fails to recur within the primitive horizon, slide
        # one action forward. This makes arbitrary exploration O(bound).
        if len(self.pending)>self.max_primitive_actions:
            self.pending.popleft()
        return None

    def _meta_alert(self):
        loops=list(self.primitives)
        if len(loops)<4:
            return None
        # After encountering a meta motif, preserve the longest *observed*
        # repetition count but smallest motif size. All evidence is bounded.
        found=[]
        for p in range(2,self.max_macro_period+1):
            if len(loops)<2*p:
                continue
            last=loops[-p:]
            motif=tuple(x.token for x in last)
            # AAAAAA is one primitive repeatedly used, already within
            # QC-015's remit; it isn't independent evidence of a multi-
            # component *cycle of cycles*.
            if len(set(motif))<2:
                continue
            if len(set(x.anchor for x in last))!=1:
                continue
            repeated=1
            while (repeated<self.max_macro_repetitions and
                   len(loops)>=(repeated+1)*p):
                prev=loops[-(repeated+1)*p:-repeated*p]
                if tuple(x.token for x in prev)!=motif:
                    break
                repeated+=1
            if repeated<2:
                continue
            sample=loops[-repeated*p:]
            if any(loop.witnessed_new_facts is not None
                   and loop.witnessed_new_facts>0 for loop in sample):
                continue
            findings_known=all(x.witnessed_new_facts is not None for x in sample)
            status=('CONFIRMED_NO_NEW_SCENE_FACTS_META_CYCLE'
                    if findings_known else 'SUSPECTED_META_CYCLE_VIEW_UNKNOWN')
            sig=seal((p,motif,status))
            if sig in self.emitted:
                continue
            found.append((p,repeated,status,sig,sample))
        if not found:
            return None
        p,repeated,status,sig,sample=sorted(
            found,key=lambda x:(x[0],-x[1]))[0]
        self.emitted.add(sig)
        receipts=tuple(ref for loop in sample for ref in loop.receipts)
        debt={}
        for loop in sample:
            for key,value in loop.spent_vitals:
                debt[key]=debt.get(key,0)+value
        report=MetaAlert(
            layer=2,primitive_motif_length=p,
            motif_repetitions=repeated,
            detected_step=sample[-1].end_step,
            primitive_action_patterns=tuple(x.actions for x in sample[-p:]),
            total_primitive_loops=len(sample),
            total_action_steps=sum(x.action_count for x in sample),
            source_receipts=receipts,status=status,
            vital_debt=tuple(sorted(debt.items())),
            question='Which unmet goal, missing prerequisite or unobserved '
                     'condition warrants breaking this cycle-of-cycles? '
                     'What low-cost probe would actually resolve it?',
            new_information=0 if all(x.witnessed_new_facts is not None
                                     for x in sample) else None)
        self.alerts.append(report)
        return report


def audit_qc015(field_steps):
    """Replay already attributed game transitions, no new executable actions."""
    m=NestedMonitor()
    for step in field_steps:
        m.observe(step)
    return {
        'action_count':len(field_steps),
        'primitive_loops':m.primitives_seen,
        'meta_alert_count':len(m.alerts),
        'alerts':tuple(m.alerts),
        'source_scope':'GAME_ONLY',
        'automatic_real_world_actions':0,
    }
