"""MOTIF-007: read *generated PNG frames* back into grounded text reasoning.

Narration is derived from stored frames and their checked coordinate motion,
not from a model inventing a story about the images. The declared scene
geometry is an assumption made by text_to_visual, never a witnessed fact.
"""
from __future__ import annotations
from pathlib import Path
import argparse
import json
from hashlib import sha256
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"door-foundry-006"))
import visual_in as vision
import text_to_visual as text_bridge

class HOLD(ValueError): pass

DIRECTIONS={(0,-1):"up",(-1,0):"left",(1,0):"right",(0,1):"down"}

def get_json(path):
    p=Path(path)
    if not p.is_file() or p.stat().st_size>100000:
        raise HOLD("HOLD_MISSING_OR_OVERSIZED_REASONING_RECEIPT")
    try:
        x=json.loads(p.read_text())
    except ValueError as exc:
        raise HOLD("HOLD_MALFORMED_REASONING_RECEIPT") from exc
    if not isinstance(x,dict):
        raise HOLD("HOLD_EXPECTED_RECORD")
    return x

def shrink_png(path, width, height, scale=10):
    raw=Path(path).read_bytes()
    if len(raw)>100000:raise HOLD("HOLD_PNG_BUDGET")
    picture=vision.decode_png(raw,limit=160)
    if len(picture)!=height*scale or len(picture[0])!=width*scale:
        raise HOLD("HOLD_RENDERED_PNG_NOT_DECLARED_IMAGE_SCALE")
    rows=[]
    for y in range(height):
        chars=[]
        for x in range(width):
            tile={picture[yy][xx]
                  for yy in range(y*scale,(y+1)*scale)
                  for xx in range(x*scale,(x+1)*scale)}
            if len(tile)!=1:
                raise HOLD("HOLD_NONUNIFORM_IMAGE_TILE")
            chars.append(next(iter(tile)))
        rows.append("".join(chars))
    return tuple(rows)

def position(rows):
    pixels=vision._one_red_block(rows)
    return min(x for x,y in pixels),min(y for x,y in pixels)

def explain(text_dir,imagined_dir,output_file):
    text_dir=Path(text_dir)
    imagined_dir=Path(imagined_dir)
    report=get_json(text_dir/"text-to-picture.json")
    body=dict(report);digest=body.pop("content_sha256",None)
    if digest!=vision.digest(body):
        raise HOLD("HOLD_TEXT_COMPILER_RECEIPT_CHANGED")
    if report["status"] not in ("UNAMBIGUOUS_GRAMMAR",
         "EXPLICIT_CHOICE_OF_AMBIGUOUS_TEXT") or report["candidate_count"]!=1:
        raise HOLD("HOLD_MULTIPLE_UNRESOLVED_VISUAL_HYPOTHESES")
    if (report.get("grammar")!=text_bridge.GRAMMAR or
        report.get("compiler")!="DETERMINISTIC_CLASSICAL_RELATIONAL_PARSE" or
        report.get("automatic_t5_invocations")!=0 or
        report.get("candidate_model_source")!="NONE" or
        report.get("privacy")!="LOCAL_ONLY_TEXT_AND_SYNTHETIC_IMAGES" or
        report.get("authority")!={"human_question_answered":True,
          "external_calls":0,"real_world_actions":0,
          "deploy":False,"promote_canon":False}):
        raise HOLD("HOLD_TEXT_EVIDENCE_CANNOT_GRANT_AUTHORITY")
    scene=report["candidate_scenes"][0]["scene"]
    folder=text_dir/"H01"
    start=vision.read_png(folder/"start.png")
    goal=vision.read_png(folder/"target.png")
    if (sha256((folder/"start.png").read_bytes()).hexdigest()
             !=report["candidate_scenes"][0]["start_png_sha256"] or
        sha256((folder/"target.png").read_bytes()).hexdigest()
             !=report["candidate_scenes"][0]["target_png_sha256"]):
        raise HOLD("HOLD_SOURCE_IMAGE_CUSTODY_CHANGED")
    if scene["schema"]!="motif.relational-scene.v0":
        raise HOLD("HOLD_UNRECOGNIZED_RELATIONAL_SCENE")
    png_gap=get_json(folder/"visual-gap.json")
    vision.verify_gap(png_gap,(folder/"start.png").read_bytes(),
                      (folder/"target.png").read_bytes())
    outcome=get_json(imagined_dir/"imagination-receipt.json")
    body=dict(outcome);check=body.pop("content_sha256",None)
    if check!=vision.digest(body):
        raise HOLD("HOLD_SIMULATION_RECEIPT_CHANGED")
    if (outcome.get("schema")!="motif.visual-imagination-outcome.v0" or
        outcome.get("imagined_goal_reached") is not True or
        outcome.get("superior_to_classical") is not False or
        outcome.get("actual_object_movements")!=0 or
        outcome.get("external_network_calls")!=0 or
        outcome.get("source_image_sha256")!=png_gap["start_png_sha256"] or
        outcome.get("target_image_sha256")!=png_gap["goal_png_sha256"]):
        raise HOLD("HOLD_UNSUPPORTED_VISUAL_SIMULATION_CLAIMS")
    frames=sorted((imagined_dir/"frames").glob("frame-*.png"))
    if (len(frames)!=outcome["imagined_future_frames"] or
        not 2<=len(frames)<=19):
        raise HOLD("HOLD_INCOMPLETE_FRAME_EVIDENCE")
    width,height=scene["canvas"]
    images=[shrink_png(f,width,height) for f in frames]
    if images[0]!=start or images[-1]!=goal:
        raise HOLD("HOLD_VISUAL_PATH_WRONG_START_OR_END")
    blue=vision.coords(start,"#")
    positions=[]
    for frame in images:
        if vision.coords(frame,"#")!=blue or len(vision.coords(frame,"R"))!=4:
            raise HOLD("HOLD_SIMULATED_OBJECT_OR_OBSTACLE_CHANGED")
        positions.append(position(frame))
    moves=[(b[0]-a[0],b[1]-a[1])
           for a,b in zip(positions,positions[1:])]
    if (any(m not in DIRECTIONS for m in moves) or
        [list(m) for m in moves]!=outcome["imagined_moves"] or
        len(moves)!=outcome["classical_minimum_steps"] or
        len(moves)!=outcome["imagined_actions"]):
        raise HOLD("HOLD_IMAGE_MOVEMENT_DISAGREES_WITH_PLANNER")
    if (text_bridge.describe(start,scene["obstacle_cells"])!=scene["start_relation"] or
        text_bridge.describe(goal,scene["obstacle_cells"])!=scene["goal_relation"]):
        raise HOLD("HOLD_VISUAL_PICTURE_DISAGREES_WITH_INPUT_RELATION")
    sentences=[]
    for direction in DIRECTIONS:
        n=sum(m==direction for m in moves)
        if n:sentences.append(str(n)+" "+DIRECTIONS[direction])
    transcript=[
      "# MOTIF-007: a thought in pictures",
      "",
      "**Source:** constrained English text → explicit assumed scene → original PNG image-in →",
      "GRAFT-generated visual operator (CANNON-reviewed) → imagined PNG frames → checked textual description.",
      "",
      "## Input meaning (not a physical observation)",
      "",
      "A red "+scene["noun"]+" was described as **"+scene["start_relation"]+
      "** of a blue "+scene["barrier_noun"]+
      ", and the requested relation was **"+scene["goal_relation"]+"**.",
      "The system chose a **"+str(width)+"×"+str(height)+
      "** synthetic grid with a stationary obstacle. Its exact metric geometry and object",
      "dimensions are modeling assumptions absent from the user's text.",
      "",
      "## Before: independently decoded picture", "","```text",
      *images[0],"```","",
      "## Hypothetical picture-driven plan","",
      "The generated visual operator proposed **"+str(len(moves))+
      " cardinal steps**, confirmed by rereading the actual resulting PNG images.",
      "Directions: **"+", ".join(DIRECTIONS[m] for m in moves)+"**.",
      "Total by direction: "+", ".join(sentences)+".",
      "",
      "## Imagined end image (not an observed outcome)","","```text",
      *images[-1],"```","",
      "## Provenance and limits","",
      "- Every step was reconstructed from the saved PNGs and cross-checked against the",
      "  simulation receipt. The obstacle layer and object's four-cell area remained fixed.",
      "- No T5, transformer model, LLM or generative image model was needed.",
      "- A classical equal-information visual planner also found the same minimal path.",
      "- This is a finite symbolic scene, not semantic interpretation of a photograph.",
      "- No physical action, external service contact, repo merge or promotion occurred.",
    ]
    output_file=Path(output_file)
    if output_file.exists():
        raise HOLD("HOLD_NEVER_OVERWRITE_EXISTING_REASONING")
    output_file.write_text("\n".join(transcript)+"\n")
    return {
      "schema":"motif.visual-reasoning-narration.v0",
      "status":"VERIFIED_TEXT_TO_IMAGES_TO_TEXT",
      "source_text_sha256":report["source_text_sha256"],
      "scene_assumptions":scene["interpretation"]["renderer_assumptions"],
      "visual_frames_independently_checked":len(images),
      "motions_independently_reconstructed":len(moves),
      "directions":[DIRECTIONS[m] for m in moves],
      "same_information_classical_minimum":outcome["classical_minimum_steps"],
      "evidence_is_hypothetical":True,
      "external_actions":0,
      "output_sha256":sha256(output_file.read_bytes()).hexdigest(),
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--text-scenes",type=Path,required=True)
    p.add_argument("--imagined",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    try: print(json.dumps(explain(a.text_scenes,a.imagined,a.out),indent=2))
    except (HOLD,vision.HOLD,text_bridge.HOLD) as e:
        print(json.dumps({"status":"HOLD","reason":str(e)}))
        raise SystemExit(1)
if __name__=="__main__":main()
