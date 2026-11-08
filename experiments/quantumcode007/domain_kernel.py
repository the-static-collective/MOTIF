"""QC-007 domain-neutral continuation graph: a second domain-adapter test.

This planner knows only typed integer resource coordinates, prerequisites,
finite action transitions, goal constraints, and bounded multiobjective
search. There are NO domain-specific IF branches in its planner.

Two unrelated toy domains: community gathering and equipment function.
Neither case authorizes event organizing, money spending, or equipment changes.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json

from living_field import MeaningField, Meaning, fixture_field

STATUS="HYPOTHETICAL_DOMAIN_NEUTRAL_ONLY"


def hashed(value):
    return sha256(json.dumps(value,sort_keys=True,separators=(",", ":")).encode()).hexdigest()


@dataclass(frozen=True)
class MetricWorld:
    metrics: tuple[tuple[str,int],...]

    def __post_init__(self):
        ids=[k for k,_ in self.metrics]
        if len(ids)!=len(set(ids)) or any(
            not isinstance(v,int) or v<0 or not k for k,v in self.metrics
        ):
            raise ValueError("Metrics must be uniquely typed nonnegative integers")

    def get(self,k):
        return dict(self.metrics).get(k,0)

    def change(self,deltas):
        merged=dict(self.metrics)
        for k,delta in deltas:
            if not isinstance(delta,int) or not k:
                raise ValueError("Untyped resource effect")
            merged[k]=merged.get(k,0)+delta
            if merged[k]<0:
                return None
        return MetricWorld(tuple(sorted(merged.items())))

    def receipt(self):
        return hashed(self.metrics)


@dataclass(frozen=True)
class Option:
    id: str
    required: tuple[tuple[str,int],...]
    effects: tuple[tuple[str,int],...]
    minutes: int
    dollars: int = 0
    risk: int = 0
    tags: frozenset[str] = frozenset()
    claim: str = "TOY_ASSUMPTION_UNVERIFIED"

    def check(self):
        if (not self.id or not self.effects or self.minutes<=0 or
            self.dollars<0 or self.risk not in (0,1,2) or
            any(not isinstance(v,int) or v<0 or not k for k,v in self.required)
            or any(not isinstance(v,int) or not k for k,v in self.effects)):
            raise ValueError("Untrusted action specification")

    def next(self,w):
        self.check()
        if all(w.get(k)>=n for k,n in self.required):
            return w.change(self.effects)
        return None


@dataclass(frozen=True)
class Objective:
    id: str
    minima: tuple[tuple[str,int],...]
    values: tuple[str,...]
    horizon: str
    max_minutes: int
    max_dollars: int
    max_risk: int
    max_depth: int
    context_tags: frozenset[str]

    def check(self):
        if (not self.id or self.max_minutes<=0 or self.max_dollars<0 or
            self.max_risk not in (0,1) or not 1<=self.max_depth<=4
            or not self.minima or not self.values or
            any(not k or not isinstance(v,int) or v<0 for k,v in self.minima)):
            raise ValueError("Invalid objective boundary")


@dataclass(frozen=True)
class Route:
    options: tuple[str,...]
    world: MetricWorld
    minutes: int
    dollars: int
    risk: int
    predecessor: str
    status: str = STATUS

    def receipt(self):
        return hashed((self.options,self.world.receipt(),self.minutes,
                       self.dollars,self.risk,self.predecessor))


@dataclass(frozen=True)
class GraphRun:
    domain: str
    status: str
    expanded_nodes: int
    paths_meeting_goal: tuple[Route,...]
    frontier: tuple[Route,...]
    continuations: tuple[tuple[str,tuple[str,...]],...]


def feasible(w,option,route,goal):
    return (option.id not in route.options and option.risk<=goal.max_risk
            and option.next(w) is not None
            and route.minutes+option.minutes<=goal.max_minutes
            and route.dollars+option.dollars<=goal.max_dollars)


def value(route,goal):
    return tuple(route.world.get(k) for k in goal.values)+(
        -route.minutes,-route.dollars,-route.risk)


def nondominated(routes,goal):
    def dominance(a,b):
        aa,bb=value(a,goal),value(b,goal)
        return all(x>=y for x,y in zip(aa,bb)) and aa!=bb
    return tuple(p for p in routes if not any(
        dominance(q,p) for q in routes if q is not p))


def search(initial,goal,inventory,node_limit=3000):
    goal.check()
    if not isinstance(node_limit,int) or not 1<=node_limit<=3000:
        raise ValueError("Invalid bounded search budget")
    if len({a.id for a in inventory})!=len(inventory):
        raise ValueError("Duplicate option IDs")
    for option in inventory:
        option.check()
    first=Route((),initial,0,0,0,"ORIGIN")
    visited=[first]
    wave=[first]
    exhausted=False
    for _ in range(goal.max_depth):
        following=[]
        for last in wave:
            for op in inventory:
                if not feasible(last.world,op,last,goal):
                    continue
                newer=Route(last.options+(op.id,),op.next(last.world),
                            last.minutes+op.minutes,last.dollars+op.dollars,
                            last.risk+op.risk,last.receipt())
                if len(visited)>=node_limit:
                    exhausted=True
                    break
                visited.append(newer)
                following.append(newer)
            if exhausted:
                break
        if exhausted:
            break
        wave=following
        if not wave:
            break
    passing=tuple(p for p in visited if p.options and all(
        p.world.get(k)>=v for k,v in goal.minima))
    best=nondominated(passing,goal)
    return GraphRun(goal.id,"HOLD_BUDGET" if exhausted else
                    "MODELLED_PATHS" if passing else "HOLD_NO_PATH",
                    len(visited),passing,best,
                    tuple((p.receipt(),tuple(a.id for a in inventory if feasible(
                        p.world,a,p,goal))) for p in best))


def meaning_aperture(field: MeaningField,goal:Objective,
                     inventory:tuple[Option,...]):
    """Same historical field, projected through domain-neutral action tags."""
    required=set(goal.context_tags)
    affordances=set().union(*(x.tags for x in inventory)) if inventory else set()
    active={}
    for m in field.meanings:
        if m.need_tags & required or m.action_tags & affordances:
            active[m.id]=["ACTION_RELEVANCE"]
    edges=[]
    for e in field.links:
        if e.source in active or e.target in active:
            edges.append(e)
            for m in (e.source,e.target):
                if m not in active:
                    active[m]=["RELATIONAL_ECHO",e.relationship]
    return {"source":field.receipt(),
            "relevant":tuple(m.id for m in field.meanings if m.id in active),
            "relations":tuple((e.source,e.relationship,e.target) for e in edges),
            "unchanged_history":len(field.meanings)}


def sample(domain):
    if domain=="community_gathering":
        world=MetricWorld((("space_confirmed",1),
                           ("volunteers",0),("meals_prepared",0),
                           ("invitations",0),("return_contacts",0)))
        actions=(
            Option("invite_neighbors",(("space_confirmed",1),),
                   (("invitations",12),),15,tags=frozenset({"connect"})),
            Option("recruit_hosts",(("space_confirmed",1),),
                   (("volunteers",2),),20,tags=frozenset({"connect"})),
            Option("prepare_meal",(("volunteers",1),),
                   (("meals_prepared",10),),40,tags=frozenset({"nourish"})),
            Option("ask_shared_pantry",(("volunteers",1),),
                   (("meals_prepared",8),),30,tags=frozenset({"access"})),
            Option("track_followup",(("invitations",8),),
                   (("return_contacts",5),),10,tags=frozenset({"connect"})),
            Option("neighbor_cohost",(("invitations",10),),
                   (("volunteers",1),),20,tags=frozenset({"connect"})),
        )
        goal=Objective(domain,(("meals_prepared",8),("invitations",8)),
                       ("meals_prepared","invitations","return_contacts",
                        "volunteers"),
                       "ONE_EVENT_WITH_RETURN",160,0,1,4,
                       frozenset({"community","ongoing_food"}))
        return world,goal,actions
    if domain=="equipment_function":
        world=MetricWorld((("available_route",0),("diagnosed",0),
                           ("part_ready",0),("documentation",0)))
        actions=(
            Option("inspect_connector",(),(("diagnosed",1),),12,
                   tags=frozenset({"diagnosis"})),
            Option("test_local_signal",(("diagnosed",1),),
                   (("available_route",1),),28,tags=frozenset({"repair"})),
            Option("obtain_compatible_part",(),(("part_ready",1),),20,
                   dollars=8,tags=frozenset({"repair"})),
            Option("repair_port",(("diagnosed",1),("part_ready",1)),
                   (("available_route",1),),45,tags=frozenset({"repair"})),
            Option("borrow_backup_route",(),(("available_route",1),),20,
                   risk=1,tags=frozenset({"borrow"})),
            Option("record_signal_diagram",(("available_route",1),),
                   (("documentation",1),),15,tags=frozenset({"documentation"})),
        )
        goal=Objective(domain,(("available_route",1),),
                       ("available_route","documentation","diagnosed",
                        "part_ready"),
                       "RESTORE_USE_THEN_CONTINUE",110,10,1,4,
                       frozenset({"function","maintenance"}))
        return world,goal,actions
    raise ValueError("Unknown explicitly declared synthetic domain")


def report():
    results={}
    for domain in ("community_gathering","equipment_function"):
        state,goal,actions=sample(domain)
        run=search(state,goal,actions)
        meaning=meaning_aperture(fixture_field(),goal,actions)
        results[domain]={
            "status":run.status,
            "examined_nodes":run.expanded_nodes,
            "solutions_in_this_horizon":len(run.paths_meeting_goal),
            "nondominated_routes":len(run.frontier),
            "meaning_carriers_kept":meaning["unchanged_history"],
            "active_meanings":meaning["relevant"],
            "route_examples":tuple({
                "steps":route.options,"metrics":route.world.metrics,
                "time_minutes":route.minutes,"cost":route.dollars,
                "further_available":dict(run.continuations).get(route.receipt(),())
            } for route in run.frontier[:8]),
            "reported_as_reality":False,
        }
    return {"experiment":"QC-007-DOMAIN-NEUTRAL",
            "status":STATUS,"domains":results,
            "model_starts_from_researcher_authored_actions":True,
            "external_actions":0}


if __name__=="__main__":
    print(json.dumps(report(),indent=2,sort_keys=True))
