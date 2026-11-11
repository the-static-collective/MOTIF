"""Fixed, author-generated challenge of a visual critic (not a blind VLM eval)."""
from __future__ import annotations
import json,sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]/'field007'))
import runpy
gen=runpy.run_path(str(Path(__file__).resolve().parents[1]/"field007"/"benchmark.py"))["gen"]
from critic import review


def run():
    out=[]
    for i in range(24):
        scene='both' if i%3==0 else 'horizontal' if i%3==1 else 'ruled_solid_only'
        image=gen(270+i,scene)
        # Simulated VLM proposals based on the known author-created fixture.
        guesses=[('horizontal-dash',[[.15,.215],[.68,.215]],scene in ('both','horizontal')),
                 ('vertical-dash',[[531/640,.345],[531/640,.785]],scene=='both'),
                 ('fake-dotted',[[.12,.70],[.74,.70]],False)]
        claims=[{'id':id,'kind':'VISIBLE_MARK','style':'DOTTED','points':pts}
                for id,pts,truth in guesses]
        r=review({'source_id':'synthetic','claims':claims},image,'synthetic')
        pred={x['claim_id']:x['verdict']=='INK_COMPATIBLE_INTENT_UNVERIFIED' for x in r['reviews']}
        for id,pts,truth in guesses:
            out.append({'scene':i,'claim':id,'ground_truth':truth,'pixel_compatible':pred[id],
                        'literal_model_only_accepts_all':True})
    def rates(label):
        tp=sum(x['ground_truth'] and x[label] for x in out)
        fp=sum(not x['ground_truth'] and x[label] for x in out)
        fn=sum(x['ground_truth'] and not x[label] for x in out)
        tn=sum(not x['ground_truth'] and not x[label] for x in out)
        return {'tp':tp,'fp':fp,'fn':fn,'tn':tn,
                'precision':round(tp/(tp+fp),3) if tp+fp else None,
                'recall':round(tp/(tp+fn),3) if tp+fn else None}
    return {'type':'AUTHOR_GENERATED_NONBLIND_MOCK_MODEL_CLAIMS',
            'synthetic_scenes':24,'candidate_claims':len(out),
            'pixel_critic':rates('pixel_compatible'),
            'naive_accept_every_mock_model_claim':rates('literal_model_only_accepts_all'),
            'real_vision_model_calls':0,'verified_sketch_meaning':False,
            'results':out}
if __name__=='__main__':
    d=run();print(json.dumps({k:v for k,v in d.items() if k!='results'},indent=2))
