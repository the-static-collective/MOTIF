"""MOTIF-009: source-reviewed visual alternatives from ambiguous text.

Real PNG world hypotheses (left/right x short/full wall) are checked by
original MOTIF-006 image-in and original GRAFT-generated, CANNON-reviewed
visual step executor. No possible world is asserted to be the actual world.
"""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
from hashlib import sha256
HERE=Path(__file__).resolve().parent
sys.path[:0]=[str(HERE.parent/"door-foundry-008"),
              str(HERE.parent/"door-foundry-007"),
              str(HERE.parent/"door-foundry-006")]
import cross_examine as previous
import text_to_visual as language
import visual_in as png
import decision as ask

AMBIGUOUS=("A red crate is beside a blue wall. Move it to the other side.")
WORLD_IDS=("LEFT_PARTIAL","RIGHT_PARTIAL","LEFT_FULL","RIGHT_FULL")
class HOLD(ValueError):pass
def need(v,msg):
    if not v:raise HOLD(msg)
def read(path):
    path=Path(path)
    need(path.is_file() and path.stat().st_size<=120000,"HOLD_MISSING_EVIDENCE")
    obj=json.loads(path.read_text())
    need(isinstance(obj,dict),"HOLD_NOT_A_RECEIPT")
    return obj

def verified_ambiguous(root):
    root=Path(root)
    receipt=read(root/"text-to-picture.json")
    claims=dict(receipt);digest=claims.pop("content_sha256",None)
    need(digest==png.digest(claims),"HOLD_AMBIGUOUS_TEXT_DIGEST")
    parsed=language.parse(AMBIGUOUS)
    need(receipt.get("schema")=="motif.text-picture-hypotheses.v0" and
      receipt.get("status")=="UNRESOLVED_MULTIPLE_VISUAL_HYPOTHESES" and
      receipt.get("candidate_count")==2 and
      receipt.get("source_text_sha256")==sha256(AMBIGUOUS.encode()).hexdigest() and
      receipt.get("grammar")==language.GRAMMAR and
      receipt.get("automatic_t5_invocations")==0 and
      receipt.get("authority")=={"human_question_answered":False,
          "external_calls":0,"real_world_actions":0,
          "deploy":False,"promote_canon":False},
      "HOLD_AMBIGUOUS_TEXT_IS_NOT_SOURCE_OWNED")
    for n,(reading,claim) in enumerate(zip(parsed["readings"],
                               receipt["candidate_scenes"]),1):
        scene,start,target,gap=language.render(reading)
        dir=root/f"H{n:02d}"
        need(claim["scene"]==scene and claim["reading"]==reading and
           claim["start_png_sha256"]==sha256(start).hexdigest() and
           claim["target_png_sha256"]==sha256(target).hexdigest() and
           claim["visual_gap_sha256"]==gap["content_sha256"] and
           (dir/"start.png").read_bytes()==start and
           (dir/"target.png").read_bytes()==target and
           read(dir/"visual-gap.json")==gap and
           read(dir/"scene.json")==scene,
           "HOLD_PNG_DOES_NOT_MATCH_ORIGINAL_TEXT_INTERPRETATION")
    return receipt

def generate_worlds(ambiguous,base,imagined,build):
    origin=verified_ambiguous(ambiguous)
    # This replay verifies original generated JS, GRAFT source digest, CANNON
    # original review, original text, and every prior imagined PNG step.
    context=previous.verified_prior(base,imagined,build)
    native=context["native"]
    worlds=[]
    for index,side in enumerate(("left","right"),1):
        claim=origin["candidate_scenes"][index-1]
        scene=claim["scene"]
        start_short=(Path(ambiguous)/f"H{index:02d}"/"start.png").read_bytes()
        target_short=(Path(ambiguous)/f"H{index:02d}"/"target.png").read_bytes()
        need(scene["canvas"]==[9,8] and scene["start_relation"]==side,
             "HOLD_UNSUPPORTED_SOURCE_GEOMETRY")
        for extent in ("partial","full"):
            if extent=="partial":start,target=start_short,target_short
            else:
                width,height=scene["canvas"]
                wall=[(4,y) for y in range(height)]
                start=png.encode_png(png.demo_scene(
                    *scene["origin"],wall,width,height))
                target=png.encode_png(png.demo_scene(
                    *scene["destination"],wall,width,height))
            gap=png.question(start,target)
            first=png.decode_png(start);last=png.decode_png(target)
            proof=previous.prove_reachable(native,first,last)
            need(proof["closed"] is True and
                 proof["reached"]==(extent=="partial"),
                 "HOLD_COMPILED_VISUAL_PROGRAM_DISAGREES_WITH_WORLD")
            worlds.append({
               "id":side.upper()+"_"+extent.upper(),
               "side":side,"wall_extent":extent,
               "start":start,"target":target,"gap":gap,"proof":proof,
               "source":f"H{index:02d}","world_observed":False
            })
    need({w["id"] for w in worlds}==set(WORLD_IDS),
         "HOLD_MISSING_ONE_OF_FOUR_WORLDS")
    return worlds,context,origin

def build_packet(ambiguous,base,imagined,build,out,weights=None,costs=None):
    out=Path(out)
    need(not out.exists(),"HOLD_REFUSE_OVERWRITING_EVIDENCE")
    worlds,context,source=generate_worlds(ambiguous,base,imagined,build)
    if weights is None:weights={k:ask.Fraction(v) for k,v in
                               zip(WORLD_IDS,(1,1,4,4))}
    if costs is None:costs=ask.standard_costs()
    ask.validate_inputs(worlds,weights,costs)
    result=ask.analyze(worlds,weights,costs)
    entries=[]
    weight_sum=sum(weights.values())
    for w in worlds:
        entries.append({
          "id":w["id"],"side":w["side"],"wall_extent":w["wall_extent"],
          "simulated_prior":float(weights[w["id"]]/weight_sum),
          "source_text_hypothesis":w["source"],
          "start_png_sha256":sha256(w["start"]).hexdigest(),
          "target_png_sha256":sha256(w["target"]).hexdigest(),
          "image_gap_sha256":w["gap"]["content_sha256"],
          "reachable_in_this_model":w["proof"]["reached"],
          "path_length":len(w["proof"]["steps"]) if w["proof"]["reached"] else None,
          "states_checked":w["proof"]["states"],
          "original_CANNON_review_is_code_only_for_new_images":True,
          "real_world_status":"UNKNOWN_NOT_OBSERVED"
        })
    body={
      "schema":"motif.active-visual-question.v0",
      "status":"UNSENT_QUESTION_WITH_FOUR_IMAGE_HYPOTHESES",
      "source_text_sha256":sha256(AMBIGUOUS.encode()).hexdigest(),
      "original_ambiguous_text_receipt_sha256":source["content_sha256"],
      "original_GRAFT_generated_source_sha256":
           context["manifest"]["generated_visual_source_sha256"],
      "original_CANNON_code_review_sha256":
           context["manifest"]["cannon_review_sha256"],
      "visual_worlds":entries,
      "model":"FOUR_SYNTHETIC_WORLDS_NOT_OBSERVATIONS",
      "analysis":result,
      "custody":{"question_sent":False,"actual_answer_observed":False,
         "current_world_identified":False,
         "physical_actions":0,"external_api_calls":0,"T5_calls":0,
         "code_automatically_admitted":False},
    }
    body["content_sha256"]=png.digest(body)
    out.mkdir(parents=True)
    for w in worlds:
        folder=out/"worlds"/w["id"]
        folder.mkdir(parents=True)
        (folder/"start.png").write_bytes(w["start"])
        (folder/"target.png").write_bytes(w["target"])
        (folder/"image-gap.json").write_text(json.dumps(w["gap"],indent=2)+"\n")
    (out/"active-question.json").write_text(json.dumps(body,indent=2)+"\n")
    best=result["two_question_policy"]
    prompt=ask.QUESTIONS[best["question_id"]]["prompt"] if best["kind"]=="ASK" else None
    (out/"question-for-human.md").write_text(
       "# MOTIF-009 — a question, not a guessed world\n\n"+
       "The text leaves the crate's starting side and the wall's extent unknown.\n"+
       "Four separate real PNG hypotheses are held as possibilities.\n\n"+
       "**Recommended unsent question:** "+(prompt or "None worth the declared cost")+
       "\n\nThis question minimizes expected decision loss in a synthetic "+
       "cost model; it is not automatically sent to a human.\n\n"+
       f"No-query expected loss: {result['zero_question_expected_loss']:.3f}.\n"+
       f"Two-question expected loss: {result['two_question_expected_loss']:.3f}.\n"+
       "Priors, regrets, and answers are hypothetical, not field-observed.\n")
    return body

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for s in ("ambiguous","base","imagined","build","out"):
        p.add_argument("--"+s,type=Path,required=True)
    a=p.parse_args()
    try:
        x=build_packet(a.ambiguous,a.base,a.imagined,a.build,a.out)
        r=x["analysis"]
        print(json.dumps({"status":x["status"],
          "candidate_worlds":len(x["visual_worlds"]),
          "first_unsent_question":r["two_question_policy"].get("question_id"),
          "no_question_loss":r["zero_question_expected_loss"],
          "two_question_loss":r["two_question_expected_loss"],
          "entropy_heuristic_first":r["entropy_greedy"]["first_question"],
          "physical_actions":0},indent=2))
    except (HOLD,previous.HOLD,language.HOLD,png.HOLD,ask.HOLD) as e:
        print(json.dumps({"status":"HOLD","reason":str(e)}))
        raise SystemExit(1)
if __name__=="__main__":main()
