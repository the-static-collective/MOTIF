"""QC-011: Survival-game replays as a reasoning curriculum, not survival advice.

The system consumes a *human/vision-model annotated* game-event trace.  It does
NOT watch or download videos, capture game memory, or train an LLM.

Each recorded episode contains:
  BEFORE observed state -> ACTION -> AFTER observed state -> claimed outcome.
Only explicitly witnessed changes become facts; unseen causal explanations
remain hypotheses. Game mechanics never become real-world safety authorities.

The reLATTE adapter emits a *HOLD-only preview*, not a signed crossing.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json

RESULTS=("SUCCESS","FAILURE","INCONCLUSIVE")
SOURCES=("HUMAN_ANNOTATION","VISION_MODEL_UNVERIFIED","GAME_TELEMETRY",
         "SYNTHETIC_FIXTURE")
DOMAINS=("MINECRAFT_LIKE","LAST_OF_US_LIKE","LONG_DARK_LIKE",
         "PROJECT_ZOMBOID_LIKE","DAY_R_LIKE","OTHER_GAME")
TAGS=("OBSERVED_GAME","CLAIMED_GAME","SYNTHETIC_GAME")
NO_REALWORLD="GAME_HYPOTHESIS_ONLY__NOT_REALWORLD_GUIDANCE"


def pin(value):
    return sha256(json.dumps(value,sort_keys=True,separators=(",",":"),
                             ensure_ascii=False).encode()).hexdigest()


@dataclass(frozen=True)
class GameState:
    """Observed game state. Fields absent from view must stay unknown."""
    resources: tuple[tuple[str,int],...]
    capabilities: tuple[str,...]
    hazards: tuple[str,...]
    location: str
    clock_tick: int

    def validate(self):
        if (not self.location or self.clock_tick < 0
            or len(self.capabilities)!=len(set(self.capabilities))
            or len(self.hazards)!=len(set(self.hazards))
            or len({k for k,_ in self.resources})!=len(self.resources)
            or any(not k or not isinstance(v,int) or v<0
                   for k,v in self.resources)):
            raise ValueError("Malformed annotated game state")

    def bag(self):
        self.validate()
        return dict(self.resources)

    @property
    def pin(self):
        self.validate()
        return pin(self.__dict__)


@dataclass(frozen=True)
class Episode:
    """One step from an attributed playthrough, not omniscient causal truth."""
    episode_id: str
    game: str
    source: str
    source_ref: str
    rights: str
    clip_start_seconds: int
    clip_end_seconds: int
    action: str
    before: GameState
    after: GameState
    outcome: str
    claimed_reason: str
    certainty: str
    tags: tuple[str,...]

    def validate(self):
        if (not self.episode_id or not self.action or
            self.game not in DOMAINS or self.source not in SOURCES
            or not self.source_ref or
            self.rights not in ("OWNER_PROVIDED","ANNOTATION_ONLY",
                                "SYNTHETIC") or
            self.clip_start_seconds<0 or
            self.clip_end_seconds<=self.clip_start_seconds
            or self.outcome not in RESULTS or
            self.certainty not in ("OBSERVED","INFERRED","UNKNOWN")
            or not self.claimed_reason or
            any(t not in TAGS for t in self.tags)):
            raise ValueError("Unattributed or untyped gameplay episode")
        self.before.validate()
        self.after.validate()
        if self.after.clock_tick<self.before.clock_tick:
            raise ValueError("Game-state time reversed")
        if self.source=="SYNTHETIC_FIXTURE" and self.rights!="SYNTHETIC":
            raise ValueError("Fixture must not masquerade as captured footage")
        if self.source=="VISION_MODEL_UNVERIFIED" and self.certainty=="OBSERVED":
            raise ValueError("Vision inference alone is not independently confirmed")

    @property
    def pin(self):
        self.validate()
        return pin({
            **{k:v for k,v in self.__dict__.items() if k not in ("before","after")},
            "before":self.before.pin,
            "after":self.after.pin,
        })


@dataclass(frozen=True)
class Change:
    episode_id: str
    action: str
    gained_capabilities: tuple[str,...]
    lost_capabilities: tuple[str,...]
    gained_resources: tuple[tuple[str,int],...]
    spent_resources: tuple[tuple[str,int],...]
    introduced_hazards: tuple[str,...]
    resolved_hazards: tuple[str,...]
    outcome: str
    confidence: str
    explanation_is_proven: bool
    evidence_pin: str
    world_scope: str = NO_REALWORLD


def interpret(ep:Episode):
    """Describe *observable* differences; no fabricated mechanics or motives."""
    ep.validate()
    before,after=ep.before.bag(),ep.after.bag()
    keys=set(before)|set(after)
    gained=tuple(sorted((k,after.get(k,0)-before.get(k,0))
                        for k in keys if after.get(k,0)>before.get(k,0)))
    spent=tuple(sorted((k,before.get(k,0)-after.get(k,0))
                       for k in keys if before.get(k,0)>after.get(k,0)))
    return Change(
        ep.episode_id,ep.action,
        tuple(sorted(set(ep.after.capabilities)-set(ep.before.capabilities))),
        tuple(sorted(set(ep.before.capabilities)-set(ep.after.capabilities))),
        gained,spent,
        tuple(sorted(set(ep.after.hazards)-set(ep.before.hazards))),
        tuple(sorted(set(ep.before.hazards)-set(ep.after.hazards))),
        ep.outcome,
        "HIGHER_CONFIDENCE_OBSERVED_GAME" if ep.certainty=="OBSERVED" else
        "PROVISIONAL_GAME_INTERPRETATION",
        False,ep.pin)


@dataclass(frozen=True)
class Replay:
    game: str
    episodes: tuple[Episode,...]
    provenance: str
    consent_for_derived_research: bool

    def validate(self):
        if (self.game not in DOMAINS or not self.provenance
            or not isinstance(self.consent_for_derived_research,bool)
            or not self.episodes
            or len({x.episode_id for x in self.episodes})!=len(self.episodes)):
            raise ValueError("Malformed replay")
        for ep in self.episodes:
            ep.validate()
            if ep.game != self.game:
                raise ValueError("Mixed game mechanics in single replay")
        for left,right in zip(self.episodes,self.episodes[1:]):
            if right.before.clock_tick<left.after.clock_tick:
                raise ValueError("Out-of-order replay")
            if left.after.pin != right.before.pin:
                raise ValueError("Unwitnessed state jump: add observation boundary")

    @property
    def pin(self):
        self.validate()
        return pin((self.game,self.provenance,
                    self.consent_for_derived_research,
                    tuple(ep.pin for ep in self.episodes)))


@dataclass(frozen=True)
class CandidateRule:
    action: str
    game: str
    witnessed_successes: int
    witnessed_failures: int
    witnessed_inconclusive: int
    possible_gains: tuple[str,...]
    possible_losses: tuple[str,...]
    examples: tuple[str,...]
    conflicts: bool
    conclusion: str = NO_REALWORLD


def derive_rules(replay:Replay):
    """Induce *candidate empirical correlations* from game-only episodes.

    Multiple outcomes for the same action are preserved as conflict rather
    than resolving into a single universal effect rule.
    """
    replay.validate()
    groups={}
    for ep in replay.episodes:
        groups.setdefault(ep.action,[]).append((ep,interpret(ep)))
    rules=[]
    for action,group in sorted(groups.items()):
        successes=sum(e.outcome=="SUCCESS" for e,_ in group)
        fails=sum(e.outcome=="FAILURE" for e,_ in group)
        unknown=sum(e.outcome=="INCONCLUSIVE" for e,_ in group)
        outcomes={(c.gained_capabilities,c.lost_capabilities,
                   c.gained_resources,c.spent_resources,c.introduced_hazards)
                  for _,c in group}
        gains=tuple(sorted({v for _,c in group
                            for v in c.gained_capabilities}))
        losses=tuple(sorted({v for _,c in group
                             for v in c.lost_capabilities}))
        rules.append(CandidateRule(
            action,replay.game,successes,fails,unknown,gains,losses,
            tuple(ep.pin for ep,_ in group),
            len(outcomes)>1))
    return tuple(rules)


@dataclass(frozen=True)
class NextQuestion:
    kind: str
    prompt: str
    related_action: str
    data_needed: tuple[str,...]


def next_questions(replay:Replay):
    """Ask to resolve visible ambiguity instead of hallucinating game rules."""
    replay.validate()
    questions=[]
    for ep in replay.episodes:
        d=interpret(ep)
        if ep.certainty!="OBSERVED":
            questions.append(NextQuestion(
                "VERIFY_VIEW","Can we confirm the state before and after this action?",
                ep.action,("before_state","after_state","human_check")))
        if ep.outcome!="SUCCESS":
            questions.append(NextQuestion(
                "EXPLAIN_FAILURE",
                "What condition made this action fail or remain uncertain?",
                ep.action,("preconditions","environment","counterfactual")))
        if d.gained_capabilities:
            questions.append(NextQuestion(
                "TEST_AFFORDANCE",
                "Which previously impossible action is available now?",
                ep.action,("new_capability","new_action","proof")))
    for rule in derive_rules(replay):
        if rule.conflicts:
            questions.append(NextQuestion(
                "RESOLVE_CONFLICT",
                "Which missing condition explains the differing outcomes?",
                rule.action,("hidden_state","timing","resource_quality")))
    return tuple(questions)


def trajectory(replay:Replay):
    """Simple replay with capability changes, no counterfactual physics claims."""
    replay.validate()
    changes=tuple(interpret(ep) for ep in replay.episodes)
    return {
        "game":replay.game,
        "replay_pin":replay.pin,
        "episode_count":len(changes),
        "capabilities_gained_by_episode":
            tuple((x.action,x.gained_capabilities) for x in changes),
        "capabilities_lost_by_episode":
            tuple((x.action,x.lost_capabilities) for x in changes),
        "resource_flows":
            tuple((x.action,x.gained_resources,x.spent_resources)
                  for x in changes),
        "possible_new_action_questions":
            tuple(x.prompt for x in next_questions(replay)
                  if x.kind=="TEST_AFFORDANCE"),
        "conclusions":"GAME_HYPOTHESES_WITH_UNRESOLVED_CAUSALITY",
        "real_world_actions":0,
    }


def relatte_preview(replay:Replay):
    """Crossing-compatible *proposal*. Not signed, sent, admitted or executed.

    reLATTE sovereignty remains with its own receiver; this is not a native
    envelope, and receiving a packet would never grant effectful authority.
    """
    replay.validate()
    if not replay.consent_for_derived_research:
        return {
            "status":"REFUSE_NO_DERIVATION_CONSENT",
            "source_pin":replay.pin,
            "effects":0,
        }
    packet={
        "schema":"motif.gameplay-observation/v0",
        "source_project":"MOTIF",
        "destination_candidate":"reLATTE",
        "source_pin":replay.pin,
        "domain":replay.game,
        "episodes":tuple(ep.pin for ep in replay.episodes),
        "candidate_rules":tuple(r.__dict__ for r in derive_rules(replay)),
        "questions":tuple(q.__dict__ for q in next_questions(replay)),
        "scope":NO_REALWORLD,
        "consent_for_derived_research":True,
        "requested_effects":[],
    }
    return {
        "status":"HOLD_FOR_SEPARATE_RELATTE_OWNER_REVIEW",
        "packet":packet,
        "packet_sha256":pin(packet),
        "signed":False,
        "transported":False,
        "received":False,
        "admitted":False,
        "executed":False,
        "real_world_actions":0,
    }


def state(resources=(),capabilities=(),hazards=(),tick=0,
          location="GAME_FICTION"):
    return GameState(tuple(resources),tuple(capabilities),
                     tuple(hazards),location,tick)


def sample(game):
    """Synthetic mechanics inspired by genres, NOT any actual game footage."""
    if game=="MINECRAFT_LIKE":
        a=state((("wood",3),),(),(),0)
        b=state((("wood",1),),("basic_tool",),(),1)
        c=state((("wood",0),),("basic_tool","shelter"),(),2)
        entries=(
            ("make_basic_tool",a,b,"SUCCESS",
             "Crafting transformed inventory into a reusable tool."),
            ("build_shelter",b,c,"SUCCESS",
             "Construction created a repeatable environmental capability."),
        )
    elif game=="LAST_OF_US_LIKE":
        a=state((("cloth",1),("alcohol",1)),(),("injury",),0)
        b=state((("cloth",0),("alcohol",0)),("first_aid_item",),("injury",),1)
        c=state((("cloth",0),("alcohol",0)),(),(),2)
        entries=(
            ("craft_first_aid",a,b,"SUCCESS",
             "Choosing to spend scarce components removes other uses."),
            ("use_first_aid",b,c,"SUCCESS",
             "A game inventory item is consumed; injury indicator changes."),
        )
    elif game=="LONG_DARK_LIKE":
        a=state((("dry_layer",1),),(),("cold",),0)
        b=state((("dry_layer",0),),("insulated",),("cold",),1)
        c=state((("dry_layer",0),),("insulated",),(),2)
        entries=(
            ("equip_layer",a,b,"SUCCESS",
             "Clothing changed an available game condition."),
            ("wait_for_condition_update",b,c,"INCONCLUSIVE",
             "Cold indicator changed after time; attribution is uncertain."),
        )
    else:
        raise ValueError("Undefined sample game")
    episodes=tuple(
        Episode(
            f"{game}:fixture:{i+1}",game,"SYNTHETIC_FIXTURE",
            f"fixture:{game}:{i+1}","SYNTHETIC",i*10,(i+1)*10,
            action,before,after,outcome,claimed,"OBSERVED",
            ("SYNTHETIC_GAME",))
        for i,(action,before,after,outcome,claimed) in enumerate(entries))
    return Replay(game,episodes,"synthetic-only:QC011",True)


def demo():
    summaries={}
    for game in ("MINECRAFT_LIKE","LAST_OF_US_LIKE","LONG_DARK_LIKE"):
        replay=sample(game)
        summaries[game]={
            "episodes":len(replay.episodes),
            "new_capabilities":trajectory(replay)["capabilities_gained_by_episode"],
            "next_questions":tuple(q.kind for q in next_questions(replay)),
            "preview_status":relatte_preview(replay)["status"],
        }
    return {
        "experiment":"QC-011",
        "status":"RESEARCH_PREVIEW_ONLY",
        "samples":summaries,
        "actual_gameplay_ingested":False,
        "actual_video_processed":False,
        "real_world_survival_training":False,
        "reLATTE_native_crossing":False,
        "outside_effects":0,
    }


if __name__=="__main__":
    print(json.dumps(demo(),indent=2,sort_keys=True))
