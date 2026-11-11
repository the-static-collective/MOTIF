"""Local-only CLI: no external vision-model calls or photo uploads."""
import argparse,json
from pathlib import Path
from loop import run_local

def main():
    p=argparse.ArgumentParser(description='Local private image -> tentative dash candidates')
    p.add_argument('--sketch',required=True,type=Path)
    p.add_argument('--source-id',default='paper')
    p.add_argument('--atlas',type=Path,default=None)
    p.add_argument('--photo',action='append',default=[],help='source_id=/private/photo.jpg; optional')
    p.add_argument('--out-dir',required=True,type=Path)
    a=p.parse_args()
    a.out_dir.mkdir(parents=True,exist_ok=True)
    photo_pairs=[]
    for item in a.photo:
        if '=' not in item:raise ValueError('--photo expected id=/path')
        photo_id,raw_path=item.split('=',1)
        if not photo_id.strip() or not raw_path.strip():raise ValueError('Invalid photo ref')
        photo_pairs.append((photo_id,str(Path(raw_path))))
    r=run_local(a.sketch,a.source_id,a.out_dir/'receipt.json',a.out_dir/'ink_preview.png',a.atlas,photo_pairs)
    print(json.dumps({'candidate_groups':r['ink']['candidate_count'],
         'desired_perimeter_complete':r['desired_perimeter_complete'],
         'model_called':r['real_multimodal_model_run'],
         'status':r['claim_level']},indent=2))
if __name__=='__main__':main()
