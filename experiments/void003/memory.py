"""VOID-003: bounded source-tied map memory and conditional waypoint suggestions.

Historical observations remain historical. Offscreen remembered material is a
hypothesis, NEVER a current observation, permission or witnessed outcome.
Only the current radius-seven sensor can authorize the very next game move.
"""
from __future__ import annotations
from collections import deque
from hashlib import sha256
import json

WALKABLE=frozenset(("grass", "path", "sand"))
DIRS=(("move_left",(-1,0)),("move_right",(1,0)),
      ("move_up",(0,-1)),("move_down",(0,1)))
TARGETS={"game_wood_obtained":"tree", "game_drink_obtained":"water"}
MAX_CELLS=4096


def seal(obj):
    return sha256(json.dumps(obj,sort_keys=True,separators=(",", ":")).encode()).hexdigest()


def signature(belief):
    return seal([list(belief.start),list(belief.facing),
                 sorted([[list(c.xy),c.material,bool(c.object_present)]
                         for c in belief.cells])])


class EpisodicMap:
    def __init__(self, seed, first_belief=None):
        self.seed=seed
        self.first_signature=signature(first_belief) if first_belief else None
        self.start=tuple(first_belief.start) if first_belief else None
        self.cells={}  # last OBSERVED state of each coordinate, not necessarily current
        self.changes=0
        self.sensor_reads=0
        if first_belief:
            self.remember(first_belief)

    def remember(self,belief):
        self.sensor_reads+=1
        for c in belief.cells:
            p=tuple(c.xy)
            entry=(c.material,bool(c.object_present))
            if p in self.cells and self.cells[p]!=entry:
                self.changes+=1
            self.cells[p]=entry
        if len(self.cells)>MAX_CELLS:
            raise RuntimeError("MEMORY_BEYOND_DECLARED_GRID_BUDGET")

    @property
    def coordinates(self):
        return frozenset(self.cells)

    def export(self):
        packet={"schema":"void003-map-memory/v0", "game":"CRAFTER_1_8_3",
                "seed":self.seed, "first_signature":self.first_signature,
                "start":self.start, "sensor_reads":self.sensor_reads,
                "historical_change_count":self.changes,
                "historical_cells":[[list(p),m,o] for p,(m,o) in sorted(self.cells.items())],
                "current_truth_claim":False,"real_world_authority":False}
        packet["seal"]=seal(packet)
        return packet

    @classmethod
    def admit(cls,packet,seed,reset_belief):
        if packet.get("seal")!=seal({k:v for k,v in packet.items() if k!="seal"}):
            raise ValueError("MEMORY_PACKET_TAMPERED")
        if (packet.get("schema")!="void003-map-memory/v0" or
            packet.get("game")!="CRAFTER_1_8_3" or
            packet.get("seed")!=seed or
            tuple(packet.get("start",()))!=tuple(reset_belief.start) or
            packet.get("first_signature")!=signature(reset_belief) or
            packet.get("current_truth_claim") is not False or
            packet.get("real_world_authority") is not False):
            raise ValueError("MEMORY_WRONG_WORLD_OR_RESET_FINGERPRINT")
        rows=packet.get("historical_cells",[])
        if not isinstance(rows,list) or len(rows)>MAX_CELLS:
            raise ValueError("MEMORY_SIZE_INVALID")
        inst=cls(seed)
        inst.first_signature=packet["first_signature"]
        inst.start=tuple(packet["start"])
        for row in rows:
            if (not isinstance(row,list) or len(row)!=3 or
                not isinstance(row[0],list) or len(row[0])!=2 or
                not all(isinstance(x,int) and 0<=x<64 for x in row[0]) or
                not isinstance(row[1],str) or type(row[2]) is not bool):
                raise ValueError("MALFORMED_MEMORY_CELL")
            pos=tuple(row[0])
            if pos in inst.cells:
                raise ValueError("DUPLICATE_MEMORY_CELL")
            inst.cells[pos]=(row[1],row[2])
        return inst


def waypoint_action(belief, memory, goal):
    """Shortest remembered walkable path toward a historically seen resource.

    Current sensor overrides stale memory. First action MUST be currently safe.
    Destination is not treated as currently observed until within current sensor.
    A plan is rebuilt after every actual game step, with no route-level claim.
    """
    if goal not in TARGETS:
        raise ValueError("UNDECLARED_GAME_GOAL")
    if memory is None:
        return None
    current=belief.grid
    states={**memory.cells, **{p:(c.material,bool(c.object_present))
                               for p,c in current.items()}}
    material=TARGETS[goal]
    targets={p for p,(m,o) in memory.cells.items()
             if m==material and not o and p not in current}
    if not targets:
        return None
    start=tuple(belief.start)
    queue=deque([start]); parent={start:None}; first={start:None}; distance={start:0}
    best=None
    while queue:
        pos=queue.popleft()
        if any((pos[0]+dx,pos[1]+dy) in targets for _,(dx,dy) in DIRS):
            if first[pos] is not None:
                best=(first[pos],distance[pos],pos)
                break
        for action,(dx,dy) in DIRS:
            nxt=(pos[0]+dx,pos[1]+dy)
            mat,occupied=states.get(nxt,(None,True))
            if nxt in parent or mat not in WALKABLE or occupied:
                continue
            if distance[pos]>=70:
                continue
            parent[nxt]=pos
            first[nxt]=first[pos] if first[pos] is not None else action
            distance[nxt]=distance[pos]+1
            queue.append(nxt)
    if best is None:
        return None
    action=best[0]
    dx,dy=next(d for a,d in DIRS if a==action)
    nextcell=(start[0]+dx,start[1]+dy)
    # The remembered path can guide but never authorize an unseen first step.
    observed=current.get(nextcell)
    if observed is None or observed.material not in WALKABLE or observed.object_present:
        return None
    return {"action":action,"destination_is_historical_hypothesis":True,
            "target_kind":material,"prior_source_reads":memory.sensor_reads,
            "estimated_steps_to_resource_neighbor":best[1],
            "first_move_verified_in_current_sensor":True}
