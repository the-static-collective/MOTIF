"""MOTIF-007: reversible, bounded classical text-to-picture reasoning bridge.

Text -> explicit relational constraints -> synthetic SceneIR -> genuine PNG
-> independent pixel reread -> original MOTIF-006 visual gap. No T5 calls,
remote image synthesis, fuzzy semantic guessing, or real-world observation.

The author-supplied text specifies *relations* but does not specify metric
geometry. Chosen 9x8 / 9x9 world templates are labeled modeling assumptions,
not facts inferred from prose.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import argparse
import json
import re
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "door-foundry-006"))
import visual_in as png

GRAMMAR = "MOTIF_007_FINITE_ENGLISH_RELATIONAL_V0"
SIDE = ("left", "right", "above", "below")
PAIR = {"left":"right", "right":"left", "above":"below", "below":"above"}
NOUNS = ("block", "crate", "square")
BARRIERS = ("wall", "barrier")
CLAUSE = re.compile(
    r"(?i)^\s*(?:a|the)\s+red\s+(?P<noun>block|crate|square)\s+"
    r"(?:is|starts)\s+(?P<start>left|right|above|below)\s+of\s+"
    r"(?:a|the)\s+blue\s+(?P<obstacle>wall|barrier)\s*\.\s*"
    r"(?:move|imagine|place)\s+(?:it|the\s+(?:red\s+)?"
    r"(?:block|crate|square))\s+(?:to|on)\s+(?:the\s+)?"
    r"(?P<goal>left|right|above|below)(?:\s+side)?\s+of\s+"
    r"(?:the\s+)?(?:blue\s+)?(?:wall|barrier)\s*\.?\s*$"
)
SHORT = re.compile(
    r"(?i)^\s*move\s+(?:a|the)\s+red\s+(?P<noun>block|crate|square)\s+"
    r"from\s+(?P<start>left|right|above|below)\s+of\s+"
    r"(?:a|the)\s+blue\s+(?P<obstacle>wall|barrier)\s+"
    r"to\s+(?:the\s+)?(?P<goal>left|right|above|below)\s+"
    r"of\s+(?:the\s+)?(?:blue\s+)?(?:wall|barrier)\s*\.?\s*$"
)
AMBIGUOUS = re.compile(
    r"(?i)^\s*(?:a|the)\s+red\s+(?P<noun>block|crate|square)\s+"
    r"(?:is|starts)\s+(?:beside|near)\s+(?:a|the)\s+blue\s+"
    r"(?P<obstacle>wall|barrier)\s*\.\s*"
    r"(?:move|imagine|place)\s+it\s+to\s+the\s+other\s+side\s*\.?\s*$"
)
class HOLD(ValueError): pass

def sha(obj):
    if isinstance(obj, (str, bytes)):
        return sha256(obj.encode() if isinstance(obj,str) else obj).hexdigest()
    return png.digest(obj)

def parse(text):
    if not isinstance(text,str) or len(text)>350 or "\x00" in text:
        raise HOLD("HOLD_TEXT_SIZE")
    # Do not silently discard punctuation, negation, extra clauses or names.
    match = CLAUSE.fullmatch(text) or SHORT.fullmatch(text)
    if match is not None:
        fields=match.groupdict()
        start,goal=fields["start"].lower(),fields["goal"].lower()
        if PAIR[start] != goal:
            raise HOLD("HOLD_INCOMPATIBLE_DIRECTION_NOT_A_RELOCATION")
        return {"status":"UNAMBIGUOUS", "readings":[{
            "noun":fields["noun"].lower(), "barrier":fields["obstacle"].lower(),
            "start":start,"goal":goal
        }],"questions":[]}
    match=AMBIGUOUS.fullmatch(text)
    if match:
        fields=match.groupdict()
        return {"status":"AMBIGUOUS", "readings":[
            {"noun":fields["noun"].lower(),"barrier":fields["obstacle"].lower(),
             "start":d,"goal":PAIR[d]} for d in ("left","right")
        ],"questions":["Is the red object initially left or right of the blue wall?"]}
    raise HOLD("HOLD_UNSUPPORTED_TEXT_NO_INVENTED_VISUAL_INTERPRETATION")

def scene_ir(reading):
    if not isinstance(reading,dict) or set(reading)!={"noun","barrier","start","goal"}:
        raise HOLD("HOLD_UNKNOWN_SCENE_FIELDS")
    if (reading["noun"] not in NOUNS or reading["barrier"] not in BARRIERS or
            reading["start"] not in SIDE or reading["goal"] != PAIR[reading["start"]]):
        raise HOLD("HOLD_UNSUPPORTED_RELATION")
    if reading["start"] in ("left","right"):
        size=(9,8)
        barriers=[(4,y) for y in range(2,6)]
        locations={"left":(1,3),"right":(6,3)}
        layout="VERTICAL_STATIONARY_BARRIER"
    else:
        size=(9,9)
        barriers=[(x,4) for x in range(2,7)]
        locations={"above":(3,1),"below":(3,6)}
        layout="HORIZONTAL_STATIONARY_BARRIER"
    return {
      "schema":"motif.relational-scene.v0",
      "noun":reading["noun"], "barrier_noun":reading["barrier"],
      "start_relation":reading["start"], "goal_relation":reading["goal"],
      "obstacle_cells":[list(p) for p in barriers],
      "red_object_extent":[2,2],
      "origin":[*locations[reading["start"]]],
      "destination":[*locations[reading["goal"]]],
      "canvas":[*size], "topology":layout,
      "synthetic_world":True,
      "interpretation":{
        "from_text":["object_color=red","barrier_color=blue",
                     "start_relation","goal_relation"],
        "renderer_assumptions":["exact_canvas_dimensions","exact_wall_length",
           "exact_block_dimensions","exact_gap_or_clearance","exact_coordinates"],
        "observed_physical_scene":False,
        "language_is_fully_understood":False
      }
    }

def describe(rows, barrier_shape):
    red=png._one_red_block(rows)
    blue=png.coords(rows,"#")
    if blue != {(x,y) for x,y in barrier_shape}:
        raise HOLD("HOLD_PICTURE_NO_LONGER_MATCHES_DECLARED_BARRIER")
    minx,maxx=min(x for x,y in red),max(x for x,y in red)
    miny,maxy=min(y for x,y in red),max(y for x,y in red)
    xb1,xb2=min(x for x,y in blue),max(x for x,y in blue)
    yb1,yb2=min(y for x,y in blue),max(y for x,y in blue)
    if maxx < xb1:return "left"
    if minx > xb2:return "right"
    if maxy < yb1:return "above"
    if miny > yb2:return "below"
    raise HOLD("HOLD_PICTURE_RELATION_UNDETERMINED")

def render(reading):
    scene=scene_ir(reading)
    obstacles=[tuple(p) for p in scene["obstacle_cells"]]
    width,height=scene["canvas"]
    start=png.demo_scene(*scene["origin"],obstacles,width,height)
    goal=png.demo_scene(*scene["destination"],obstacles,width,height)
    start_bytes=png.encode_png(start)
    goal_bytes=png.encode_png(goal)
    # Independent pixel-level round-trip and geometric relation recovery.
    reread_start=png.decode_png(start_bytes)
    reread_goal=png.decode_png(goal_bytes)
    if (reread_start!=start or reread_goal!=goal or
        describe(reread_start,obstacles)!=scene["start_relation"] or
        describe(reread_goal,obstacles)!=scene["goal_relation"]):
        raise HOLD("HOLD_TEXT_IMAGE_ROUNDTRIP_MISMATCH")
    gap=png.question(start_bytes,goal_bytes)
    if gap["start_rows"]!=list(start) or gap["goal_rows"]!=list(goal):
        raise HOLD("HOLD_original_MOTIF_IMAGE_GAP_CHANGED")
    return scene,start_bytes,goal_bytes,gap

def compile_to_images(text, output, choice=None):
    output=Path(output)
    if output.exists():
        raise HOLD("HOLD_NEVER_OVERWRITE_PRIOR_EVIDENCE")
    parsed=parse(text)
    if choice is not None:
        if parsed["status"] != "AMBIGUOUS" or choice not in ("left","right"):
            raise HOLD("HOLD_UNNECESSARY_OR_UNKNOWN_DISAMBIGUATION")
        selected=[x for x in parsed["readings"] if x["start"]==choice]
        selection_status="EXPLICIT_CHOICE_OF_AMBIGUOUS_TEXT"
    elif parsed["status"]=="AMBIGUOUS":
        selected=parsed["readings"]
        selection_status="UNRESOLVED_MULTIPLE_VISUAL_HYPOTHESES"
    else:
        selected=parsed["readings"]
        selection_status="UNAMBIGUOUS_GRAMMAR"
    candidates=[]
    result_blobs=[]
    for i,reading in enumerate(selected):
        scene,start,goal,gap=render(reading)
        candidates.append({
          "hypothesis_id":"H%02d"%(i+1),
          "reading":reading,
          "scene":scene,
          "start_png_sha256":sha(start),
          "target_png_sha256":sha(goal),
          "visual_gap_sha256":gap["content_sha256"],
          "status":"SYNTHETIC_VISUAL_HYPOTHESIS_NOT_OBSERVED"})
        result_blobs.append((start,goal,gap))
    body={
      "schema":"motif.text-picture-hypotheses.v0",
      "status":selection_status,
      "source_text_sha256":sha(text),
      "source_text_length":len(text),
      "grammar":GRAMMAR,
      "compiler":"DETERMINISTIC_CLASSICAL_RELATIONAL_PARSE",
      "candidate_count":len(candidates),
      "questions_for_operator":parsed["questions"] if choice is None else [],
      "candidate_scenes":candidates,
      "automatic_t5_invocations":0,
      "candidate_model_source":"NONE",
      "privacy":"LOCAL_ONLY_TEXT_AND_SYNTHETIC_IMAGES",
      "authority":{"human_question_answered":False if parsed["status"]=="AMBIGUOUS" and choice is None else True,
                    "external_calls":0,"real_world_actions":0,
                    "deploy":False,"promote_canon":False}}
    body["content_sha256"]=png.digest(body)
    output.mkdir(parents=True)
    for record,(start,goal,gap) in zip(candidates,result_blobs):
        folder=output/record["hypothesis_id"]
        folder.mkdir()
        (folder/"start.png").write_bytes(start)
        (folder/"target.png").write_bytes(goal)
        (folder/"visual-gap.json").write_text(json.dumps(gap,indent=2)+"\n")
        (folder/"scene.json").write_text(json.dumps(record["scene"],indent=2)+"\n")
    (output/"text-to-picture.json").write_text(json.dumps(body,indent=2)+"\n")
    return body

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--text",type=str,required=True)
    ap.add_argument("--out",type=Path,required=True)
    ap.add_argument("--choose",choices=("left","right"))
    args=ap.parse_args()
    try:
        packet=compile_to_images(args.text,args.out,args.choose)
        print(json.dumps({
         "status":packet["status"],"hypotheses":packet["candidate_count"],
         "text_sha256":packet["source_text_sha256"],
         "receipt_sha256":packet["content_sha256"],
         "t5_used":False}))
    except HOLD as error:
        print(json.dumps({"status":"HOLD","reason":str(error)}))
        raise SystemExit(1)

if __name__=="__main__":main()
