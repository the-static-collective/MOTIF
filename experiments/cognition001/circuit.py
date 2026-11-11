"""COGNITION-001: four-speed bounded local thought + foreground contemplation.

This module never starts a daemon, opens a network socket, calls an LLM,
reads the user's records or changes its own running code. The real upstream
GHoT scheduling *decision function* is imported at a checked-out pinned SHA.
The offered capability is explicitly a synthetic local lab fixture.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from hashlib import sha256
from itertools import product
from pathlib import Path
import importlib.util
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
GHOT_REV = "9748a0772c4a13135421c4fa84a9991e0a51e05f"
CAPABILITY = "motif.contemplate.v0"
LENSES = ("skeptic", "systems", "story", "planner", "experimenter")
MAX_DAY_EVENTS = 32
MAX_DAILY_UNITS = 6
MIN_IDLE_SECONDS = 20


def seal(payload):
    return sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def native_affordance():
    path = HERE.parent / "003" / "affordance.py"
    spec = importlib.util.spec_from_file_location("cognition001_native003", path)
    if not path.is_file() or spec is None or spec.loader is None:
        raise RuntimeError("NATIVE_MOTIF_003_NOT_AVAILABLE")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def native_ghot():
    """Load upstream source. No fallback that impersonates a GHoT decision."""
    root = ROOT / "sources" / "ghot" / "ghot"
    if not (root / "energy_scheduler.py").is_file():
        raise RuntimeError("PINNED_GHOT_SOURCE_NOT_CHECKED_OUT")
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    from energy_scheduler import decide_from_candidates
    return decide_from_candidates


@dataclass(frozen=True)
class Record:
    rid: str
    day: str
    origin_root: str
    task: str
    action: str
    status: str
    note: str

    def __post_init__(self):
        date.fromisoformat(self.day)
        if (not self.rid or not self.origin_root or not self.task
            or not self.action or not self.note or len(self.note) > 180
            or self.status not in {"verified_success", "verified_failure", "reported", "unverified"}):
            raise ValueError("INVALID_SOURCE_BOUND_RECORD")

    def public(self):
        return {k: getattr(self, k) for k in ("rid", "day", "origin_root",
                    "task", "action", "status", "note")}


@dataclass
class DayBook:
    """Append-only bounded *synthetic* source record book."""
    rows: list[Record] = field(default_factory=list)
    identifiers: set[str] = field(default_factory=set)

    def append(self, row: Record):
        if row.rid in self.identifiers:
            raise ValueError("DUPLICATED_SOURCE_RECEIPT")
        if len(self.rows) >= MAX_DAY_EVENTS:
            raise ValueError("EXCESSIVE_UNREVIEWED_EVIDENCE")
        self.rows.append(row)
        self.identifiers.add(row.rid)

    def reflection(self, current_day: str):
        """A possible contradiction is a question, not automatically a cause."""
        today = [r for r in self.rows if r.day == current_day]
        past = [r for r in self.rows if r.day < current_day]
        delta = []
        for new in today:
            for old in past:
                if new.task != old.task or new.action != old.action:
                    continue
                if old.status != new.status:
                    delta.append({"earlier":old.rid, "later":new.rid,
                                  "change":f"{old.status}->{new.status}",
                                  "classification":"UNRESOLVED_DISAGREEMENT_NOT_CAUSE",
                                  "next_question":"What changed in the task, source, environment or measurement?"})
        return {"mode":"REFLECTION", "compared":len(past)*len(today),
                "changed_reports":delta[:16],
                "reviewed_today":len(today),
                "prior_days":len({r.day for r in past})}

    def reflex(self, task: str, action: str):
        witnessed = [r for r in self.rows if r.task == task and
                     r.action == action and r.status == "verified_success"]
        return {"mode":"REFLEX", "recommendation":action, "source_ids":[r.rid for r in witnessed],
                "automatic_candidate":True, "effect_executed":False,
                "guard":"CURRENT_CONTEXT_AND_AUTHORITY_MUST_BE_RECHECKED"} if len(witnessed)>=2 else None

    def deliberate(self, task: str):
        rows = [r for r in self.rows if r.task == task]
        if not rows:
            return {"mode":"DELIBERATION", "request":"Find first authorized observation",
                    "confidence":"UNKNOWN", "executed":False}
        disputed = any(r.status in {"reported","unverified","verified_failure"} for r in rows)
        return {"mode":"DELIBERATION",
                "request":"Seek independent current confirmation" if disputed
                          else "Review next achievable objective",
                "source_ids":[r.rid for r in rows],
                "confidence":"UNRESOLVED" if disputed else "CONDITIONAL",
                "executed":False}


@dataclass(frozen=True)
class AppState:
    visible: bool
    opted_in: bool
    idle_seconds: int
    user_task_active: bool
    battery_percent: int | None
    charging: bool
    thermal_c: float | None
    cpu_pressure: float
    power_willingness: str = "normal"

    def __post_init__(self):
        if self.power_willingness not in {"normal","abundant","conserve","critical"}:
            raise ValueError("UNKNOWN_POWER_WILLINGNESS")
        if self.battery_percent is not None and not 0<=self.battery_percent<=100:
            raise ValueError("BATTERY_OUT_OF_RANGE")
        if self.idle_seconds<0 or not 0<=self.cpu_pressure<=1:
            raise ValueError("UNBOUNDED_PRESSURE")


def candidate_for_ghot(state: AppState):
    """A synthetic *declared* local offer; NOT a real GHoT BODY registration."""
    return [{
        "node_id":"lab-local", "location":"local", "field_state":"awake",
        "body":{
            "identity":{"available":False},
            "power":{"source":"ac" if state.charging else "battery",
                     "charging":state.charging,
                     "willingness":state.power_willingness,
                     "renewable_surplus":False},
            "offers":[{"capability":CAPABILITY,"available":True,
                       "power":{"class":"heavy","policy_reasons":[]}}]
        }
    }]


def admission(state:AppState, budget_left:int):
    """Strict local gate plus the real GHoT energy candidate selector."""
    if not state.opted_in:
        return {"action":"hold","why":"USER_HAS_NOT_OPTED_IN"}
    if not state.visible:
        return {"action":"hold","why":"APP_NOT_VISIBLE"}
    if state.user_task_active or state.idle_seconds < MIN_IDLE_SECONDS:
        return {"action":"hold","why":"USER_IS_ACTIVE"}
    if budget_left<=0:
        return {"action":"hold","why":"DAILY_BUDGET_EXHAUSTED"}
    if state.thermal_c is None or state.thermal_c>=75:
        return {"action":"hold","why":"THERMAL_UNKNOWN_OR_HIGH"}
    if state.cpu_pressure>.60:
        return {"action":"hold","why":"CPU_PRESSURE_HIGH"}
    if not state.charging and (state.battery_percent is None or state.battery_percent<35):
        return {"action":"hold","why":"BATTERY_UNKNOWN_OR_LOW"}
    # Do not run on any remote body or an unverified availability claim.
    decide = native_ghot()
    decision = decide(candidate_for_ghot(state), CAPABILITY,
                      urgency="background", deferrable=True,
                      prefer_surplus_for_background=True)
    if decision["action"] != "run_here":
        return {"action":"hold", "why":"GHOT_"+str(decision["action"]).upper(),
                "ghot_action":decision["action"]}
    return {"action":"run_here", "why":"FOREGROUND_IDLE_SURPLUS",
            "ghot_action":"run_here", "ghot_selector":"UPSTREAM_GHOT_PINNED"}


def lens_question(lens:str, a:Record, b:Record):
    label = f"{a.task} / {b.task}"
    texts = {
        "skeptic":("Could both accounts be explained by measurement or source error?",
                   "Seek independent contradictory evidence before claiming a relation."),
        "systems":("Do these two processes share a missing dependency or bottleneck?",
                   "Compare their provenance and the effect of removing the suspected dependency."),
        "story":("Does a later event change the interpretation of an earlier account?",
                 "Keep the original testimony unchanged; ask an independent reviewer."),
        "planner":("Could an observation in one workflow enable a new action in the other?",
                   "A matched control should test actual downstream useful progress."),
        "experimenter":("What small safe comparison could discriminate two explanations?",
                         "Predeclare a prospective test before seeing its outcome."),
    }
    question, falsifier = texts[lens]
    return {"mode":"CONTEMPLATION", "perspective":lens,
            "source_ids":[a.rid,b.rid], "source_roots":[a.origin_root,b.origin_root],
            "scope":label, "question":question, "falsifier":falsifier,
            "status":"PENCIL_UNTESTED", "real_world_effects":0,
            "auto_revision_permitted":False}


@dataclass
class FourSpeedMind:
    book: DayBook
    day: str
    remaining_units: int = MAX_DAILY_UNITS
    cursor: int = 0
    cards: list[dict] = field(default_factory=list)
    saw_native: bool = False

    def _ideas(self):
        """Hypothetical cross-day/cross-origin comparisons, not causality."""
        today = [r for r in self.book.rows if r.day == self.day]
        earlier = [r for r in self.book.rows if r.day < self.day]
        pairs = [(a,b) for a in earlier for b in today
                 if a.origin_root != b.origin_root]
        # Stable bounded research queue. Cross-day references encourage
        # contemplation about change, not merely rerunning today's summary.
        return [(lens, a,b) for lens in LENSES for a,b in pairs][:100]

    def _native_rank(self, ideas):
        """Actually execute canonical MOTIF-003 on hypothetical alternatives."""
        native=native_affordance()
        start=frozenset({("source",r.rid) for r in self.book.rows})
        def possible(state, _verbs):
            for index,(lens,a,b) in enumerate(ideas):
                # Thought generation creates future QUESTION affordances only,
                # never hidden factual answers to those questions.
                if ("contemplated",str(index)) in state:
                    continue
                yield (f"consider:{index}",(a.rid,b.rid,lens),
                       state | frozenset({("contemplated",str(index)),
                                          ("skill",f"question:{index}")}))
        rows=native.analyze_first_moves(
            start, (), possible,
            lambda future,initial:len(future-initial),horizon=1,max_worlds=128)
        return {int(r["operator"].split(":",1)[1]):r for r in rows}

    def tick(self, state:AppState):
        gate=admission(state,self.remaining_units)
        if gate["action"]!="run_here":
            return {"mode":"CONTEMPLATION","status":"HOLD",**gate,
                    "remaining_units":self.remaining_units}
        candidates=self._ideas()
        if not candidates:
            return {"mode":"CONTEMPLATION","status":"HOLD",
                    "why":"NO_INDEPENDENT_CROSS_DAY_PAIRS"}
        ranked=self._native_rank(candidates)
        self.saw_native=True
        eligible=[i for i in ranked if i>=self.cursor]
        if not eligible:
            return {"mode":"CONTEMPLATION","status":"HOLD","why":"QUEUE_EXHAUSTED"}
        i=min(eligible)
        lens,a,b=candidates[i]
        card=lens_question(lens,a,b)
        card["hypothetical_new_choices"]=len(ranked[i]["new_affordances"])
        card["has_source_pin"]=True
        card["no_external_execution"]=True
        self.cards.append(card)
        self.cursor=i+1
        self.remaining_units-=1
        return {"mode":"CONTEMPLATION","status":"PROPOSED_NOT_ADMITTED",
                "proposal":card,"remaining_units":self.remaining_units,
                "ghot_decision":gate["ghot_action"],
                "native_motif003_executed":True}

    def proposal_for_optimization(self):
        """Never silently alter source, policy, models or app preferences."""
        return {"status":"HOLD_FOR_OWNER_REVIEW","mode":"SELF_OPTIMIZATION_PROPOSAL",
                "hypothesis":"Memoize duplicate tested cross-thread comparisons",
                "reason":"Avoid repeating already examined pairs when source revisions are unchanged",
                "measured_perf_gain":None,
                "requires":["offline ablation","independent outcome verifier","owner approval"],
                "code_changed":False,
                "model_weights_changed":False}


def demo_book():
    """Entirely invented example; no personal user data processed."""
    rows=[
        Record("demo-01","2026-11-10","bench-a","delivery","route_fast",
               "verified_failure","Delivery route missed the closing time."),
        Record("demo-02","2026-11-10","bench-b","review","count_reports",
               "reported","The dashboard described an improvement."),
        Record("demo-03","2026-11-10","bench-c","delivery","route_fast",
               "verified_success","A different time window delivered on time."),
        Record("demo-04","2026-11-11","bench-d","delivery","route_fast",
               "verified_success","A subsequent run completed on time."),
        Record("demo-05","2026-11-11","bench-e","review","count_reports",
               "verified_failure","Independent count did not match the dashboard."),
        Record("demo-06","2026-11-11","bench-f","new_skill","verify_first",
               "unverified","The new verification idea has not been tested."),
    ]
    book=DayBook()
    for r in rows:
        book.append(r)
    return book


def demonstration():
    book=demo_book()
    mind=FourSpeedMind(book,"2026-11-11")
    stages={"reflex":book.reflex("delivery","route_fast"),
            "deliberation":book.deliberate("review"),
            "reflection":book.reflection("2026-11-11")}
    good=AppState(True,True,50,False,94,True,37.0,.14,"abundant")
    before=mind.tick(AppState(False,True,50,False,94,True,37.0,.14,"abundant"))
    proposals=[mind.tick(good) for _ in range(3)]
    return {"experiment":"COGNITION-001","input":"SYNTHETIC_TWO_DAY_RECORDS_ONLY",
            "four_modes":stages,
            "invisible_gate":before,
            "contemplation":proposals,
            "optimization":mind.proposal_for_optimization(),
            "executed_original_motif003":mind.saw_native,
            "ghot_revision":GHOT_REV,
            "external_actions":0,"llm_calls":0,"no_os_daemon":True,
            "app_integration_deployed":False}


if __name__=="__main__":
    print(json.dumps(demonstration(),indent=2,sort_keys=True))
