"""QC-017 — source-grounded bounded classical planner for observed Crafter worlds.

No hard-coded sequence to water/wood. The planner composes actual primitive
game operators with a bounded breadth-first search over observed local tiles,
including orientation and a final resource-interaction operator. It returns
the shortest action sequence within its DECLARED game model, not a guarantee
that the engine or world will cooperate.

The sensor is intentionally *privileged*: a radius-seven current-world tile
read via Crafter internals, not RGB-only human observation. No hidden cells
are traversed, no unpublished engine state is used as evidence of access,
no actions are sent by this pure module, and no human survival inference.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from hashlib import sha256
import json

DIRECTIONS=(("move_left",(-1,0)),("move_right",(1,0)),
            ("move_up",(0,-1)),("move_down",(0,1)))
WALKABLE=frozenset(("grass","path","sand"))
GOAL_RULES={
    # This *typed* game knowledge is supplied from known Crafter mechanics.
    # Learning these dynamics from experience is a DIFFERENT experiment.
    "game_drink_obtained":("water","drink"),
    "game_wood_obtained":("tree","wood"),
}
MAX_VISIBLE_CELLS=260
MAX_NODE_EXPANSIONS=5000
MAX_ACTIONS=18


def seal(value):
    return sha256(json.dumps(value,sort_keys=True,
                             separators=(',',':')).encode()).hexdigest()


@dataclass(frozen=True)
class SeenCell:
    xy: tuple[int,int]
    material: str
    object_present: bool
    source: str

    def __post_init__(self):
        if (len(self.xy)!=2 or not all(isinstance(x,int) for x in self.xy)
            or not self.material or not self.source):
            raise ValueError("Unverifiable game cell")


@dataclass(frozen=True)
class Belief:
    start: tuple[int,int]
    facing: tuple[int,int]
    cells: tuple[SeenCell,...]
    source: str
    world: str="CRAFTER_GAME_ONLY"

    def __post_init__(self):
        if (len(self.start)!=2 or len(self.facing)!=2 or
            self.facing not in tuple(d for _,d in DIRECTIONS) or
            not self.source or self.world!="CRAFTER_GAME_ONLY" or
            not self.cells or len(self.cells)>MAX_VISIBLE_CELLS or
            len({c.xy for c in self.cells})!=len(self.cells) or
            self.start not in {c.xy for c in self.cells}):
            raise ValueError("Unsupported belief or missing current-location evidence")

    @property
    def pin(self):
        return seal((
            self.start,self.facing,
            tuple(sorted((c.xy,c.material,c.object_present,c.source)
                         for c in self.cells)),self.source,self.world))

    @property
    def grid(self):
        return {c.xy:c for c in self.cells}


@dataclass(frozen=True)
class Plan:
    goal: str
    actions: tuple[str,...]
    target: tuple[int,int] | None
    status: str
    input_pin: str
    expanded_states: int
    model_label: str="CLASSICAL_BFS_ON_OBSERVED_GAME_TILES"
    predicted_but_unverified: bool=True
    real_world_authority: bool=False

    @property
    def cost(self):
        return len(self.actions)


def observe(env,actor,source_ref,radius=7):
    """Read ONLY current nearby tiles through the existing declared sensor."""
    if not 1<=radius<=7:
        raise ValueError("Radius cannot exceed declared observation aperture")
    pos=actor.pos(env)
    cells=[]
    for dx in range(-radius,radius+1):
        for dy in range(-radius,radius+1):
            if abs(dx)+abs(dy)>radius:
                continue
            location=(pos[0]+dx,pos[1]+dy)
            tile=actor.tile(env,location)
            if tile is not None:
                cells.append(SeenCell(location,str(tile[0]),
                                      tile[1] is not None,source_ref))
    return Belief(pos,tuple(int(v) for v in env._player.facing),
                  tuple(cells),source_ref)


def traverse(belief,goal,max_actions=MAX_ACTIONS):
    """Shortest explicit state-space *game action* plan by BFS.

    Node = (player position, direction faced), not a point alone.
    Movement onto a walkable observed cell changes position and facing.
    Attempt to walk into an observed solid resource is a legitimate
    *orientation* action (the game blocks movement but faces the resource).
    A final "do" is legal only when facing a source-observed goal resource.
    Unknown cells, hidden objects and unobserved shortcuts are not usable.
    """
    if goal not in GOAL_RULES or not 1<=max_actions<=MAX_ACTIONS:
        raise ValueError("Unrecognized game objective or unbounded search")
    material,claimed_resource=GOAL_RULES[goal]
    grid=belief.grid
    targets={p for p,c in grid.items()
             if c.material==material and not c.object_present}
    if not targets:
        return Plan(goal,(),None,"HOLD_NO_OBSERVED_GOAL_RESOURCE",
                    belief.pin,0)
    start=(belief.start,belief.facing)
    queue=deque((start,))
    paths={start:()}
    expansions=0
    while queue and expansions<MAX_NODE_EXPANSIONS:
        node=queue.popleft()
        expansions+=1
        pos,face=node
        path=paths[node]
        target=(pos[0]+face[0],pos[1]+face[1])
        if target in targets and len(path)+1<=max_actions:
            # The returned path is a prediction; the actual game later
            # must record goal-specific inventory/capability improvement.
            return Plan(goal,path+("do",),target,"PLAN_CANDIDATE",
                        belief.pin,expansions)
        if len(path)>=max_actions-1:
            continue
        for action,delta in DIRECTIONS:
            nextpos=(pos[0]+delta[0],pos[1]+delta[1])
            cell=grid.get(nextpos)
            if cell is None:
                continue
            if cell.material in WALKABLE and not cell.object_present:
                outcome=(nextpos,delta)
            elif nextpos in targets:
                # Specific interaction to face a target; not an attempt to
                # walk through unrelated blocked terrain.
                outcome=(pos,delta)
            else:
                continue
            if outcome not in paths:
                paths[outcome]=path+(action,)
                queue.append(outcome)
    return Plan(goal,(),None,"HOLD_OBSERVED_NO_VERIFIED_PATH",
                belief.pin,expansions)


def check_goals(inv_before,inv_after,ach_before,ach_after,goal):
    """Evidence rule must use the real engine's observations AFTER execution."""
    if goal not in GOAL_RULES:
        raise ValueError("Unknown goal")
    _,resource=GOAL_RULES[goal]
    before=int(inv_before.get(resource,0))
    after=int(inv_after.get(resource,0))
    if after>before:
        return "WITNESSED_GAME_RESOURCE_GAIN"
    if goal=="game_wood_obtained" and (
        int(ach_after.get("collect_wood",0))>
        int(ach_before.get("collect_wood",0))):
        return "WITNESSED_GAME_ACHIEVEMENT"
    return "GOAL_NOT_YET_WITNESSED"


def plans_for_goals(belief,goals):
    """Generate competing objective-specific plans, not fixed route scripts."""
    if len(goals)>8:
        raise ValueError("Maximum eight simultaneous game objectives")
    return tuple(traverse(belief,g) for g in goals)


def next_action(plan):
    if plan.status!="PLAN_CANDIDATE":
        return None
    return plan.actions[0] if plan.actions else None


def minimal_example():
    # A deliberately incomplete map: no real world, no engine call.
    cell=(SeenCell((0,0),"grass",False,"fixture"),
          SeenCell((0,-1),"grass",False,"fixture"),
          SeenCell((0,-2),"water",False,"fixture"))
    p=traverse(Belief((0,0),(0,1),cell,"fictional:fixture"),
               "game_drink_obtained")
    return {
        "plan":p.actions,
        "cost":p.cost,
        "source_pin":p.input_pin,
        "automatic_execution":False,
        "physical_world_actions":0,
        "note":"Example only. No game engine was executed here.",
    }


if __name__=="__main__":
    print(json.dumps(minimal_example(),sort_keys=True,indent=2))
