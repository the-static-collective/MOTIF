"""QC-007: Living Meaning Field / continuing action-network experiment.

Research-only, bounded, nonexecuting, synthetic example about nourishment and
recurring food access. A symbol is a durable carrier of *accruing, related*
interpretations. An action field makes some interpretations jointly relevant,
without forcing one true decoder or destroying earlier meanings.

Plans are explicit counterfactuals, NOT confirmed real-world provisions. Their
scores and action consequences are researcher-defined for the toy benchmark.
All claims of actual impact require separate, permissioned external witnesses.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from hashlib import sha256
from itertools import combinations
import json

STATUS = "SIMULATED_RESEARCH_ONLY"
MAX_STEPS = 3
MAX_EXPANSIONS = 4000
VALID_RELATIONS = frozenset({
    "SUPPORTS", "TENSIONS", "CO_OCCURS", "REINTERPRETS",
    "POSSIBLE_ROUTE", "FORMAL_RESEMBLANCE"
})
MEANING_KINDS = frozenset({"OBSERVATION", "INTERPRETATION", "HYPOTHESIS"})
ACTION_KINDS = frozenset({"nourish", "access", "connect", "purchase", "supplemental", "substitute"})
SCENARIO_HORIZONS = frozenset({"ACUTE", "PERSISTENT"})


def digest(obj):
    return sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"),
                             default=list).encode("utf8")).hexdigest()


@dataclass(frozen=True)
class Meaning:
    id: str
    carrier: str
    phrase: str
    need_tags: frozenset[str]
    action_tags: frozenset[str]
    witness_id: str
    kind: str
    born: int

    def receipt(self):
        return digest((self.id,self.carrier,self.phrase,
                       sorted(self.need_tags),sorted(self.action_tags),
                       self.witness_id,self.kind,self.born))


@dataclass(frozen=True)
class MeaningEdge:
    source: str
    target: str
    relationship: str
    witness_id: str
    born: int


@dataclass(frozen=True)
class MeaningField:
    """Append-only attributed history. Views, not receipts, may change."""
    meanings: tuple[Meaning,...] = ()
    links: tuple[MeaningEdge,...] = ()

    def add(self, meaning: Meaning):
        if not all((meaning.id, meaning.carrier, meaning.phrase,
                    meaning.witness_id)):
            raise ValueError("Meaning needs its carrier and attributable source")
        if meaning.kind not in MEANING_KINDS or meaning.born < 1:
            raise ValueError("Unsupported meaning type or historical order")
        if any(x.id == meaning.id for x in self.meanings):
            raise ValueError("Never overwrite historical meaning identity")
        if self.meanings and meaning.born < self.meanings[-1].born:
            raise ValueError("Never backdate an accreted interpretation")
        return replace(self,meanings=self.meanings+(meaning,))

    def relate(self, link: MeaningEdge):
        ids={x.id for x in self.meanings}
        if (link.source not in ids or link.target not in ids or
            link.source == link.target or link.relationship not in VALID_RELATIONS
            or not link.witness_id or link.born < 1):
            raise ValueError("Invalid or unanchored meaning relation")
        latest=max((x.born for x in self.meanings if x.id in (link.source,link.target)),
                   default=0)
        latest_link=max((x.born for x in self.links),default=0)
        if link.born < max(latest,latest_link):
            raise ValueError("Relation cannot predate either known source")
        if link in self.links:
            raise ValueError("Repeated relation receipt")
        return replace(self,links=self.links+(link,))

    def as_of(self, time: int):
        history=tuple(x for x in self.meanings if x.born<=time)
        ids={x.id for x in history}
        relationships=tuple(x for x in self.links
                             if x.born<=time and x.source in ids and x.target in ids)
        return MeaningField(history,relationships)

    def receipt(self):
        return digest({"meaning_receipts":[m.receipt() for m in self.meanings],
                       "relations":[(e.source,e.target,e.relationship,
                                     e.witness_id,e.born) for e in self.links]})


@dataclass(frozen=True)
class World:
    meals_today: int = 0
    recurring_days: int = 0
    community_links: int = 0
    stress_tools: int = 0
    budget: int = 0
    food_in_hand: bool = False
    can_travel: bool = True
    has_phone: bool = True
    kitchen: bool = False
    knows_contact: bool = False
    foraging_verified: bool = False
    legal_permission: bool = False

    def receipt(self):
        return digest(self.__dict__)


@dataclass(frozen=True)
class Action:
    id: str
    kind: str
    minutes: int
    spend: int
    risk: int
    needs: tuple[tuple[str,object],...] = ()
    gains: tuple[tuple[str,int],...] = ()
    sets: tuple[tuple[str,bool],...] = ()
    action_tags: frozenset[str] = frozenset()
    description: str = ""

    def validate(self):
        allowed=set(World.__dataclass_fields__)
        int_keys={"meals_today","recurring_days","community_links",
                  "stress_tools","budget"}
        bool_keys=allowed-int_keys
        if (not self.id or self.kind not in ACTION_KINDS or
            self.minutes<1 or self.spend<0 or self.risk not in (0,1,2)):
            raise ValueError("Invalid action specification")
        if any(k not in allowed for k,_ in self.needs):
            raise ValueError("Unknown prerequisite")
        if any(k not in int_keys or not isinstance(v,int) for k,v in self.gains):
            raise ValueError("Only typed integer effects are permitted")
        if any(k not in bool_keys or not isinstance(v,bool) for k,v in self.sets):
            raise ValueError("Only typed flags are permitted")
        if any(v<0 and k != "budget" for k,v in self.gains):
            raise ValueError("No negative health or access effects in toy model")

    def permitted(self,world: World,max_risk=1):
        self.validate()
        if self.risk>max_risk:
            return False
        if self.kind=="substitute":
            # Fast/breathwork cannot be modeled as nourishment.
            return False
        if world.budget < self.spend:
            return False
        for key,wanted in self.needs:
            value=getattr(world,key)
            if isinstance(value,bool):
                if value is not wanted:
                    return False
            elif value < wanted:
                return False
        return True

    def transition(self,world: World):
        if not self.permitted(world):
            return None
        updates={k:getattr(world,k)+v for k,v in self.gains}
        updates["budget"]=world.budget-self.spend
        for k,v in self.sets:
            updates[k]=v
        return replace(world,**updates)


@dataclass(frozen=True)
class ActionField:
    id: str
    horizon: str
    need_tags: frozenset[str]
    deadline_minutes: int
    budget_limit: int
    min_meals: int
    min_recurring_days: int
    max_risk: int = 1
    max_steps: int = MAX_STEPS

    def check(self):
        if (self.horizon not in SCENARIO_HORIZONS or self.max_steps < 1
            or self.max_steps > MAX_STEPS or self.deadline_minutes <= 0
            or self.budget_limit < 0 or self.min_meals < 0
            or self.min_recurring_days < 0 or self.max_risk not in (0,1)):
            raise ValueError("Invalid bounded action field")


@dataclass(frozen=True)
class RelevantMeaning:
    meaning_id: str
    reasons: tuple[str,...]


@dataclass(frozen=True)
class FieldView:
    field_receipt: str
    context_id: str
    meanings: tuple[RelevantMeaning,...]
    relations: tuple[MeaningEdge,...]
    unused_meanings: tuple[str,...]
    status: str = STATUS


def aperture(field: MeaningField, context: ActionField,
             viable_actions: tuple[Action,...]):
    """Return an active *set* plus its witness-bearing relations.

    One-hop related interpretations are present as relation echoes even when
    their tags did not directly intersect this action context. TENSION is
    retained as such, not interpreted as positive factual support.
    """
    context.check()
    kinds={x.kind for x in viable_actions}
    tags=set().union(*(x.action_tags for x in viable_actions)) if viable_actions else set()
    selected={}
    for m in field.meanings:
        reasons=[]
        if m.need_tags & context.need_tags:
            reasons.append("NEED_INTERSECTION")
        if m.action_tags & (tags|kinds):
            reasons.append("ACTION_AFFORDANCE")
        if reasons:
            selected[m.id]=set(reasons)
    links=[]
    for e in field.links:
        if e.source in selected or e.target in selected:
            links.append(e)
            for id in (e.source,e.target):
                if id not in selected:
                    selected[id]={"RELATIONAL_ECHO_"+e.relationship}
    return FieldView(field.receipt(),context.id,
                     tuple(RelevantMeaning(m.id,tuple(sorted(selected[m.id])))
                           for m in field.meanings if m.id in selected),
                     tuple(links),
                     tuple(m.id for m in field.meanings if m.id not in selected))


@dataclass(frozen=True)
class Path:
    """A hypothetical node in a finite action network, not a completed life."""
    action_ids: tuple[str,...]
    state: World
    minutes: int
    spent: int
    cumulative_risk: int
    parent_receipt: str
    status: str = STATUS

    def receipt(self):
        return digest((self.action_ids,self.state.receipt(),self.minutes,
                       self.spent,self.cumulative_risk,self.parent_receipt,
                       self.status))


@dataclass(frozen=True)
class Search:
    context: str
    status: str
    source_receipt: str
    nodes: int
    attempted_edges: int
    viable_paths: tuple[Path,...]
    pareto_paths: tuple[Path,...]
    partial_paths: int
    exhausted: bool
    # Explicit future options show why a "solution" is never a terminal state.
    continuations: tuple[tuple[str,tuple[str,...]], ...]


def meets_need(path: Path,context: ActionField):
    return (path.state.meals_today>=context.min_meals and
            path.state.recurring_days>=context.min_recurring_days)


def vector(path: Path):
    """Multi-objective vector; no hidden scalar with a single best winner."""
    w=path.state
    return (w.meals_today,w.recurring_days,w.community_links,
            w.stress_tools,-path.minutes,-path.spent,-path.cumulative_risk)


def dominates(a: Path,b: Path):
    x,y=vector(a),vector(b)
    return all(i>=j for i,j in zip(x,y)) and any(i>j for i,j in zip(x,y))


def frontier(paths: tuple[Path,...]):
    """Keep all tied and incomparable paths; no arbitrary tie-breaking."""
    return tuple(p for p in paths if not any(
        dominates(q,p) for q in paths if q is not p))


def possible_actions(world: World,inventory: tuple[Action,...],
                     used: tuple[str,...],context: ActionField):
    return tuple(a for a in inventory
                 if a.id not in used and a.permitted(world,context.max_risk))


def plan(world: World,context: ActionField,
         inventory: tuple[Action,...],node_cap=MAX_EXPANSIONS):
    """Explore bounded paths, preserving both incomparable and tied routes.

    This is not a scheduler, API dispatcher, or welfare eligibility checker.
    Later steps execute only in the *preview state* produced by preceding
    hypothetical steps. An output cannot certify real access to food.
    """
    context.check()
    if not isinstance(node_cap,int) or node_cap<1 or node_cap>MAX_EXPANSIONS:
        raise ValueError("Invalid fixed local expansion budget")
    if len({a.id for a in inventory})!=len(inventory):
        raise ValueError("Duplicate action identity")
    for a in inventory:
        a.validate()
    root=Path((),world,0,0,0,"GENESIS")
    wave=[root]
    visited=[root]
    attempts=0
    exhausted=False
    for _ in range(context.max_steps):
        next_wave=[]
        for old in wave:
            for action in possible_actions(old.state,inventory,old.action_ids,context):
                attempts+=1
                if (old.minutes+action.minutes>context.deadline_minutes or
                    old.spent+action.spend>context.budget_limit):
                    continue
                result=action.transition(old.state)
                if result is None:
                    continue
                new=Path(old.action_ids+(action.id,),result,
                         old.minutes+action.minutes,old.spent+action.spend,
                         old.cumulative_risk+action.risk,old.receipt())
                if len(visited)>=node_cap:
                    exhausted=True
                    break
                visited.append(new)
                next_wave.append(new)
            if exhausted:
                break
        if exhausted:
            break
        wave=next_wave
        if not wave:
            break
    viable=tuple(x for x in visited if x.action_ids and meets_need(x,context))
    pareto=frontier(viable)
    continuations=tuple((p.receipt(),tuple(a.id for a in possible_actions(
        p.state,inventory,p.action_ids,context))) for p in pareto)
    if exhausted:
        status="HOLD_BUDGET_EXHAUSTED"
    elif viable:
        status="SIMULATED_OPTIONS_FOUND"
    else:
        status="HOLD_NO_SAFE_COMPLETE_PATH"
    return Search(context.id,status,world.receipt(),len(visited),
                  attempts,viable,pareto,
                  sum(bool(p.action_ids) and not meets_need(p,context)
                      for p in visited),
                  exhausted,continuations)


@dataclass(frozen=True)
class ClaimedWitness:
    """Claim about an observed event. It is never automatically verified."""
    before_receipt: str
    action_id: str
    after_receipt: str
    source_ref: str
    classification: str = "USER_ATTESTED_NOT_INDEPENDENTLY_VERIFIED"

    def seal(self):
        return digest(self.__dict__)


@dataclass(frozen=True)
class Reentry:
    """Preserve counterfactual and alleged actual outcome as different types."""
    preview: Path
    claim: ClaimedWitness | None

    def state_label(self):
        return "CLAIMED_NOT_VERIFIED" if self.claim else "COUNTERFACTUAL_ONLY"


def reenter(path: Path,claim: ClaimedWitness | None):
    if path.status != STATUS:
        raise ValueError("Only explicitly previewed paths may be discussed")
    if claim:
        if (not claim.source_ref or claim.action_id != path.action_ids[-1]
            or claim.after_receipt != path.state.receipt()
            or claim.before_receipt != path.parent_receipt):
            raise ValueError("Claim does not match the local graph receipt")
    return Reentry(path,claim)



@dataclass(frozen=True)
class Contradiction:
    """An attributable *reported* deviation, never independent verification.

    A witness about an action may report that the predicted resource arrived,
    did not arrive, or took a different form. The model must record the
    disagreement without silently rewriting either prediction or history.
    """
    predicted_path_receipt: str
    source_parent_receipt: str
    action_id: str
    expected_state_receipt: str
    reported_state_receipt: str
    source_ref: str
    status: str = "REPORTED_OUTCOME_UNVERIFIED"

    @property
    def disagrees(self):
        return self.expected_state_receipt != self.reported_state_receipt

    def seal(self):
        return digest(self.__dict__)


def receive_feedback(path: Path, reported: World, source_ref: str,
                     source_parent_receipt: str):
    """Receive a report, do not execute an action or assume ground truth."""
    if (path.status != STATUS or not path.action_ids or not source_ref
        or source_parent_receipt != path.parent_receipt
        or not isinstance(reported,World)):
        raise ValueError("Feedback needs source, history and typed reported state")
    return Contradiction(path.receipt(),path.parent_receipt,
                         path.action_ids[-1],path.state.receipt(),
                         reported.receipt(),source_ref)


def accrue_from_feedback(field: MeaningField, prior_meaning_id: str,
                         feedback: Contradiction, new_id: str,
                         proposition: str, time: int,
                         need_tags: frozenset[str],
                         action_tags: frozenset[str]):
    """Attach a cautious new hypothesis. Never promote a report into a fact."""
    existing={m.id:m for m in field.meanings}
    if (prior_meaning_id not in existing or not feedback.source_ref
        or not feedback.predicted_path_receipt or feedback.status !=
        "REPORTED_OUTCOME_UNVERIFIED"):
        raise ValueError("Feedback cannot create unsupported historical knowledge")
    source=existing[prior_meaning_id]
    new_meaning=Meaning(new_id,source.carrier,proposition,need_tags,
                        action_tags,feedback.seal(),"HYPOTHESIS",time)
    expanded=field.add(new_meaning)
    expanded=expanded.relate(MeaningEdge(prior_meaning_id,new_id,
                         "REINTERPRETS",feedback.seal(),time))
    return expanded


def diagnose_report(path: Path, feedback: Contradiction):
    """A discrepancy is a *reason to revise*, not proof of causal mechanism."""
    if (feedback.predicted_path_receipt != path.receipt() or
        feedback.expected_state_receipt != path.state.receipt() or
        feedback.action_id != path.action_ids[-1]):
        raise ValueError("Counterexample receipt belongs to another proposal")
    return {
        "status":"HOLD_MODEL_REVIEW" if feedback.disagrees else
                 "AGREEMENT_REPORTED_NOT_VERIFIED",
        "action_id":feedback.action_id,
        "feedback_receipt":feedback.seal(),
        "reported_as_fact":False,
        "prediction_preserved":path.receipt(),
    }

def action_inventory():
    """Hypothetical mechanisms. Does not claim any service exists or accepts."""
    return (
        Action("community_table","nourish",35,0,0,
               needs=(("can_travel",True),),
               gains=(("meals_today",1),("community_links",1)),
               action_tags=frozenset({"urgent_food","community","shared_table"}),
               description="Hypothetical accessible communal meal"),
        Action("contact_neighbor","connect",10,0,0,
               needs=(("has_phone",True),),
               gains=(("community_links",1),),
               sets=(("food_in_hand",True),("knows_contact",True)),
               action_tags=frozenset({"community","urgent_food","ongoing_food"}),
               description="Model assumes a successful contact; not guaranteed"),
        Action("eat_available_food","nourish",15,0,0,
               needs=(("food_in_hand",True),),
               gains=(("meals_today",1),),
               sets=(("food_in_hand",False),),
               action_tags=frozenset({"urgent_food","nourishment"}),
               description="Access food that is actually safe and available"),
        Action("pantry_pickup","access",45,0,0,
               needs=(("can_travel",True),),
               gains=(("recurring_days",2),("community_links",1)),
               sets=(("food_in_hand",True),("knows_contact",True)),
               action_tags=frozenset({"urgent_food","ongoing_food","distribution"}),
               description="Hypothetical food shelf provision"),
        Action("enroll_recurring_pickup","access",25,0,0,
               needs=(("has_phone",True),("knows_contact",True)),
               gains=(("recurring_days",7),),
               action_tags=frozenset({"ongoing_food","distribution"}),
               description="Hypothetical accepted recurring food arrangement"),
        Action("mutual_aid_exchange","access",30,0,0,
               needs=(("knows_contact",True),),
               gains=(("recurring_days",5),("community_links",2)),
               action_tags=frozenset({"ongoing_food","community"}),
               description="Hypothetical peer exchange, no availability guarantee"),
        Action("weekly_food_sharing","access",50,0,0,
               needs=(("community_links",2),),
               gains=(("recurring_days",7),),
               action_tags=frozenset({"ongoing_food","community","shared_table"}),
               description="Hypothetical cooperative recurring sharing"),
        Action("buy_staples","purchase",25,5,0,
               needs=(("can_travel",True),("kitchen",True)),
               sets=(("food_in_hand",True),),
               action_tags=frozenset({"urgent_food","trade"}),
               description="Model purchase only; prices are fabricated"),
        Action("breathing_focus","supplemental",8,0,0,
               gains=(("stress_tools",1),),
               action_tags=frozenset({"self_regulation"}),
               description="Focus exercise, never nourishment"),
        Action("fast_instead_of_food","substitute",1,0,2,
               action_tags=frozenset({"urgent_food"}),
               description="Intentionally inadmissible replacement for food"),
        Action("unverified_foraging","nourish",40,0,2,
               needs=(("foraging_verified",True),("legal_permission",True)),
               gains=(("meals_today",1),),
               action_tags=frozenset({"urgent_food"}),
               description="Unsafe/illegal foraging is never recommended"),
    )


def fixture_field():
    meaning_rows=(
        Meaning("bread.nutrition","bread","bread as sustenance",
                frozenset({"urgent_food"}),frozenset({"nourish"}),
                "fixture:meal-evidence","OBSERVATION",1),
        Meaning("bread.table","bread","bread as a shared human table",
                frozenset({"community"}),frozenset({"connect","nourish"}),
                "fixture:communal-story","INTERPRETATION",2),
        Meaning("bread.continuity","bread","bread as continued provision",
                frozenset({"ongoing_food"}),frozenset({"access"}),
                "fixture:recurring-care-story","INTERPRETATION",3),
        Meaning("bread.exchange","bread","bread as a circulating resource",
                frozenset({"trade"}),frozenset({"purchase","access"}),
                "fixture:exchange-story","HYPOTHESIS",4),
        Meaning("bread.fasting","bread","bread as a spiritual metaphor of fasting",
                frozenset({"spiritual_practice"}),frozenset({"supplemental"}),
                "fixture:metaphor","INTERPRETATION",5),
        Meaning("neighbor.support","neighbor","neighbor as a possible contributor",
                frozenset({"community","ongoing_food"}),frozenset({"connect"}),
                "fixture:neighbor-interaction","HYPOTHESIS",6),
    )
    field=MeaningField()
    for x in meaning_rows:
        field=field.add(x)
    field=field.relate(MeaningEdge("bread.nutrition","bread.table","SUPPORTS",
                                  "fixture:shared-meal",7))
    field=field.relate(MeaningEdge("bread.fasting","bread.nutrition","TENSIONS",
                                  "fixture:metaphor-not-nutrition",8))
    field=field.relate(MeaningEdge("bread.table","bread.continuity","POSSIBLE_ROUTE",
                                  "fixture:community-to-access",9))
    field=field.relate(MeaningEdge("bread.exchange","neighbor.support","CO_OCCURS",
                                  "fixture:exchange-proposal",10))
    return field


def scenario(name):
    if name=="acute":
        return (World(),ActionField(
            "acute_meal","ACUTE",frozenset({"urgent_food","community"}),
            60,0,1,0))
    if name=="persistent":
        return (World(),ActionField(
            "recurring_sustenance","PERSISTENT",
            frozenset({"ongoing_food","community","urgent_food"}),
            180,0,1,7))
    if name=="isolated":
        return (World(has_phone=False,can_travel=False),ActionField(
            "blocked_local_access","ACUTE",frozenset({"urgent_food","community"}),
            90,0,1,0))
    if name=="stored":
        return (World(food_in_hand=True,kitchen=True,budget=10),
                ActionField("stored_acute","ACUTE",
                            frozenset({"urgent_food"}),45,10,1,0))
    raise ValueError("Unknown synthetic scenario")



def single_step_food_baseline(world: World, context: ActionField,
                              inventory: tuple[Action,...]):
    """Intentionally weak near-term myopic comparison, NOT an optimal planner.

    It asks only which *immediately permitted single action* maximizes the
    model's meal-unit count. This is a control for horizon differences,
    not evidence that classical optimization or planning is inadequate.
    """
    feasible=[]
    for action in possible_actions(world,inventory,(),context):
        if action.minutes<=context.deadline_minutes and action.spend<=context.budget_limit:
            result=action.transition(world)
            if result is not None:
                feasible.append((action,result))
    if not feasible:
        return {"selected":None,"meets_need":False}
    selection=sorted(feasible,key=lambda x:(
        -x[1].meals_today,x[0].minutes,x[0].id))[0]
    action,result=selection
    pseudo=Path((action.id,),result,action.minutes,action.spend,action.risk,"GENESIS")
    return {"selected":action.id,
            "modelled_meal_units":result.meals_today,
            "modelled_future_days":result.recurring_days,
            "meets_need":meets_need(pseudo,context)}

def run_case(name):
    world,context=scenario(name)
    inventory=action_inventory()
    available=possible_actions(world,inventory,(),context)
    field=fixture_field()
    active=aperture(field,context,available)
    result=plan(world,context,inventory)
    def description(path):
        return {"actions":path.action_ids,
                "meal_units":path.state.meals_today,
                "modeled_future_days":path.state.recurring_days,
                "links":path.state.community_links,
                "minutes":path.minutes,"dollars":path.spent,
                "preview_only":True,
                "more_actions_available":dict(result.continuations).get(path.receipt(),())}
    return {
        "case":name,"status":result.status,
        "one_step_baseline":single_step_food_baseline(world,context,inventory),
        "source_receipt":result.source_receipt,
        "carrier_receipt":field.receipt(),
        "meanings_preserved":len(field.meanings),
        "active_meanings":tuple(x.meaning_id for x in active.meanings),
        "meaning_relations":tuple((x.source,x.relationship,x.target)
                                   for x in active.relations),
        "plans_examined":result.nodes,
        "paths_meeting_synthetic_need":len(result.viable_paths),
        "nondominated_paths":len(result.pareto_paths),
        "incomplete_paths":result.partial_paths,
        "exhausted":result.exhausted,
        "shown_pareto_paths":tuple(description(p) for p in result.pareto_paths[:12]),
        "suppressed_pareto_disclosure":max(0,len(result.pareto_paths)-12),
        "unsafe_substitute_admitted":any(
            x in p.action_ids for p in result.viable_paths
            for x in ("fast_instead_of_food","unverified_foraging")),
    }


def report():
    cases={name:run_case(name) for name in ("acute","persistent","isolated","stored")}
    return {"experiment":"QC-007","status":STATUS,
            "cases":cases,
            "fact_origin":"RESEARCHER_AUTHORED_TOY_WORLD",
            "real_world_food_provision_verified":False,
            "external_actions":0,
            "local_planner_only":True,
            "no_terminal_success_claim":True,
            "mathematical_superiority_demonstrated":False}


if __name__=="__main__":
    print(json.dumps(report(),indent=2,sort_keys=True))
