"""CV+VLM source-image analysis. The VLM is explicitly optional and off by default."""
import argparse,json
from pathlib import Path
from critic import review,overlay
from local_vlm import perceive_local

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--image',type=Path,required=True)
    p.add_argument('--source-id',default='sketch-001')
    p.add_argument('--model-packet',type=Path,help='Inspect an existing model output without sending image')
    p.add_argument('--use-local-ollama',action='store_true',help='Opt into localhost-only inference')
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args()
    if a.model_packet and a.use_local_ollama:p.error('Select exactly one model input mode')
    if a.use_local_ollama:
        result=perceive_local(a.source_id,a.image,explicit_local_model=True)
        packet=result['packet'];receipt=result['model_receipt']
    elif a.model_packet:
        packet=json.loads(a.model_packet.read_text());receipt={'model_executed':False,'mode':'USER_SUPPLIED_TENTATIVE_PACKET'}
    else:
        packet={'source_id':a.source_id,'claims':[],'claimed_complete_route':False}
        receipt={'model_executed':False,'mode':'CV_ONLY_NO_MODEL'}
    report=review(packet,a.image,a.source_id)
    report['model_receipt']=receipt
    a.out.mkdir(parents=True,exist_ok=True)
    (a.out/'review.json').write_text(json.dumps(report,indent=2))
    overlay(a.image,packet,report,a.out/'review_overlay.png')
    print(json.dumps({'ink_groups':report['detected_dash_groups'],'accepted_ink_compatible':report['ink_compatible'],
        'held':report['held'],'model_mode':receipt.get('mode',receipt.get('model')),
        'verified_complete_route':False},indent=2))
if __name__=='__main__':main()
