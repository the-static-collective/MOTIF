"""QC-014: STAGNATION BREAKER / 'insanity prevention' for action loops.

Distinguishes a real repeated failure from useful repeated work, time-delayed
effects and neutral exploration. Applies a narrow contract to observed
BEFORE/ACTION/AFTER snapshots, never hallucinating a mechanism.

A diagnosis is a *candidate explanation* until checked against explicit
source-referenced prerequisites. This research kernel neither executes
actions nor asserts safe physical-world interventions.
"""
from __future__ import annotations

from collections import Counter,deque
from dataclasses import dataclass,field
from hashlib import sha256
import json

PROGRESS,NO_PROGRESS,UNRESOLVED="PROGRESS","NO_PROGRESS","UNRESOLVED"
CRITICAL=("make_","place_")
PERSISTENT=("move_",)
SOFT=("do","sleep")
BOUND=32


def pin(value):
    return sha256(json.dumps(value,sort_keys=True,separators=(",",":")).encode()).hexdigest()


@dataclass(frozen=True)
class Snapshot:
    """Simple parsed game telemetry; action times are not causal evidence."""
    inventory: tuple[tuple[str,int],...]
    achievements: tuple[str,...]
    position: tuple[int,int]
    facing: tuple[int,int] | None = None
    step: int=0

    def __post_init__(self):
        if (self.step<0 or len({k for k,v in self.inventory})!=len(self.inventory)
            or any(not isinstance(v,int) for _,v in self.inventory)
            or len(self.position)!=2
            or any(not isinstance(p,int) for p in self.position)):
            raise ValueError("Invalid / insufficient game snapshot")

    def count(self,key):
        return dict(self.inventory).get(key,0)

    def has(self,achievement):
        return "achievement:"+achievement in self.achievements

    @property
    def token(self):
        return pin({"inventory":self.inventory,"achievements":self.achievements,
                    "position":self.position,"facing":self.facing})


@dataclass(frozen=True)
class Observation:
    action: str
    before: Snapshot
    after: Snapshot
    evidence: str

    def __post_init__(self):
        if (not self.action or not self.evidence
            or self.after.step<=self.before.step):
            raise ValueError("Unattributed or time-inverted action")

    @property
    def pin(self):
        return pin((self.action,self.before.token,self.after.token,
                    self.before.step,self.after.step,self.evidence))


@dataclass(frozen=True)
class Assessment:
    observation_pin: str
    action: str
    verdict: str
    effect_basis: str
    actual_progress: bool
    explanation_proven: bool = False


def assess(observation:Observation):
    """Game-only outcome signatures. Never penalize time-delayed combat 'do'.

    Passive food/drink/health changes are not evidence that a failed crafting
    command made progress. A movement that changes facing to target material
    can be valuable even when the position does not move.
    """
    b,a=observation.before,observation.after
    name=observation.action
    gained=set(a.achievements)-set(b.achievements)
    if name.startswith("make_"):
        item=name[len("make_"):]
        changed=(a.count(item)>b.count(item)
                 or "achievement:"+name in gained)
        basis="CRAFT_OUTPUT_OR_ACHIEVEMENT"
        status=PROGRESS if changed else NO_PROGRESS
    elif name.startswith("place_"):
        changed="achievement:"+name in gained
        basis="PLACEMENT_ACHIEVEMENT"
        status=PROGRESS if changed else NO_PROGRESS
    elif name.startswith("move_"):
        changed=(a.position!=b.position
                 or (b.facing is not None and a.facing is not None
                     and b.facing!=a.facing))
        basis="POSITION_OR_ORIENTATION"
        status=PROGRESS if changed else (
            NO_PROGRESS if b.facing is not None and a.facing is not None
            else UNRESOLVED)
    elif name=="do":
        changed=bool(gained or any(
            a.count(k)>b.count(k) for k in
            ("wood","stone","coal","iron","diamond","food","drink")))
        basis="GATHERED_ITEMS_OR_ACHIEVEMENTS__HIDDEN_COMBAT_DAMAGE"
        status=PROGRESS if changed else UNRESOLVED
    elif name=="sleep":
        changed=(a.count("energy")>b.count("energy")
                 or "achievement:wake_up" in gained)
        basis="SLOW_REST_CAN_REQUIRE_MULTIPLE_GAME_TICKS"
        status=PROGRESS if changed else UNRESOLVED
    else:
        changed=False
        status=UNRESOLVED
        basis="NO_DEFINED_TASK_SPECIFIC_SUCCESS_SIGNATURE"
    return Assessment(observation.pin,name,status,basis,changed)


@dataclass(frozen=True)
class Alert:
    action: str
    step: int
    failures: int
    reason: str
    observed_tokens: tuple[str,...]
    proposed_next_question: str
    observation_pin: str
    status: str = "STOP_RETRY_AND_INSPECT"
    actual_cause_confirmed: bool = False


@dataclass
class StagnationGuard:
    """Bounded online sequence monitor with hysteresis and per-action hold."""
    threshold: int = 3
    window: int = 16
    failed_counts: Counter = field(default_factory=Counter)
    recent: deque = field(default_factory=lambda:deque(maxlen=16))
    alert_keys: set[str] = field(default_factory=set)
    held: dict[str,str] = field(default_factory=dict)
    alerts: list[Alert] = field(default_factory=list)
    ignored_unresolved: int = 0

    def __post_init__(self):
        if not 2<=self.threshold<=12 or not 4<=self.window<=BOUND:
            raise ValueError("Bounded thresholds required")
        self.recent=deque(maxlen=self.window)

    def observe(self,observation:Observation):
        result=assess(observation)
        # UNRESOLVED is NOT evidence of failure, and cannot trigger an
        # automatic stop on attacks, wait states, or invisible mechanisms.
        if result.verdict==UNRESOLVED:
            self.ignored_unresolved+=1
            self.failed_counts[observation.action]=0
            self.recent.append((observation.action,UNRESOLVED,result.observation_pin))
            return None
        name=observation.action
        if result.verdict==PROGRESS:
            self.failed_counts[name]=0
            # Failed actions may become retryable when game state changes
            # meaningfully, but the decision process still checks safety.
            if name in self.held:
                self.held.pop(name)
            self.recent.append((name,PROGRESS,result.observation_pin))
            return None
        # Task-specific no-effect repeated after *the same intended action*.
        # Interleaving different options can be useful investigation; count
        # local consecutive failed invocations, not every past attempt.
        previous=self.recent[-1][0] if self.recent else None
        self.failed_counts[name]=(
            self.failed_counts[name]+1 if previous==name else 1)
        self.recent.append((name,NO_PROGRESS,result.observation_pin))
        count=self.failed_counts[name]
        if count<self.threshold:
            return None
        # An independent alert for a NEW failed episode can be raised only
        # after recorded progress; an unchanged episode cannot spam alerts.
        signature=name+":" + str(observation.before.count(
            name[len("make_"):] if name.startswith("make_") else name))
        if signature in self.alert_keys:
            return None
        self.alert_keys.add(signature)
        self.held[name]=result.observation_pin
        alert=Alert(name,observation.after.step,count,
                    "OBSERVED_REPEATED_TASK_NONPROGRESS",
                    tuple(v[2] for v in list(self.recent)[-count:]),
                    "Which required resource, location, tool, permission, "
                    "or environmental condition is still missing?",
                    observation.pin)
        self.alerts.append(alert)
        return alert

    def should_hold(self,action):
        return action in self.held

    def release_after_new_evidence(self,action,evidence):
        """Explicit reassessment, not just enough elapsed time."""
        if not evidence:
            raise ValueError("Release requires a new source-attributed fact")
        self.held.pop(action,None)
        self.failed_counts[action]=0
        self.alert_keys={x for x in self.alert_keys if not x.startswith(action+":")}


@dataclass(frozen=True)
class RequirementDiagnosis:
    action: str
    missing_resources: tuple[tuple[str,int],...]
    missing_utilities: tuple[str,...]
    unknown_utilities: tuple[str,...]
    explanation: str
    rule_source: str
    confidence: str
    current_action_allowed: bool = False
    automatic_external_effects: int = 0


def diagnose_craft(action,inventory,visible_utilities,recipe,
                   rule_source="CRAFT_RULES_PROVIDED_BY_GAME_OWNER"):
    """Typed game recipe lookup; does not invent a missing material."""
    if not action.startswith("make_"):
        raise ValueError("This repair applies only to crafting")
    if not recipe or not isinstance(recipe,dict):
        raise ValueError("Recipe source missing")
    needed=recipe.get("uses",{})
    utilities=recipe.get("nearby",())
    lack=tuple(sorted((k,int(v)-int(inventory.get(k,0)))
                      for k,v in needed.items()
                      if int(inventory.get(k,0))<int(v)))
    # None means not observed, != an authoritative finding of absence.
    absent=tuple(sorted(u for u in utilities
                        if visible_utilities.get(u) is False))
    unknown=tuple(sorted(u for u in utilities
                         if visible_utilities.get(u) is None))
    if lack:
        reason="MISSING_GAME_RECIPE_INPUT"
    elif absent:
        reason="MISSING_NEARBY_CRAFTING_UTILITY"
    elif unknown:
        reason="CANNOT_VERIFY_REQUIRED_NEARBY_UTILITY"
    else:
        reason="PRECONDITIONS_APPEAR_MET__INVESTIGATE_OTHER_CAUSE"
    return RequirementDiagnosis(
        action,lack,absent,unknown,reason,rule_source,
        "GAME_RULE_VERIFIED_IF_CANONICAL_RECIPE" if rule_source else
        "UNVERIFIED_RECIPE",False,0)


def inspect_qc011_replay(episodes,threshold=3):
    """Use an existing action-level before/after replay; no simulation."""
    monitor=StagnationGuard(threshold=threshold)
    alerts=[]
    for ep in episodes:
        def s(game):
            loc=game.location
            if not loc.startswith("GAME_TILE:"):
                raise ValueError("Unrecognized game-only coordinate")
            xy=tuple(int(x) for x in loc.split(":",1)[1].split(","))
            return Snapshot(tuple(game.resources),
                            tuple(game.capabilities),xy,
                            facing=None,step=game.clock_tick)
        a=monitor.observe(Observation(
            ep.action,s(ep.before),s(ep.after),ep.pin))
        if a:alerts.append(a)
    return {
        "audited_steps":len(episodes),
        "alerts":tuple({
            "action":x.action,"step":x.step,
            "failures":x.failures,"reason":x.reason,
            "source_pin":x.observation_pin,
            "causal_explanation_confirmed":False,
        } for x in alerts),
        "unresolved_actions_not_called_failures":monitor.ignored_unresolved,
        "effectful_actions":0,
    }
