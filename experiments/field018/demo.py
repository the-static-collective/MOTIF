"""Run FIELD-018 locally without internet; personal photos are never uploaded."""
import argparse, tempfile
from pathlib import Path
import cv2,numpy as np
from chain import run,dump


def make_public_fixture(folder:Path):
    img=np.full((580,880),231,np.uint8)
    for y in range(32,560,27): cv2.line(img,(35,y),(845,y),187,1)
    for x in range(160,560,46):cv2.line(img,(x,171),(x+17,171),40,3)
    cv2.rectangle(img,(115,305),(350,495),52,3)
    path=folder/'synthetic_sketch.png'
    cv2.imwrite(str(path),img)
    return path


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--sketch',type=Path)
    p.add_argument('--photo',type=Path,action='append',default=[])
    p.add_argument('--hint',action='append',default=[])
    p.add_argument('--out',type=Path,default=Path('field018_report.json'))
    p.add_argument('--budget',type=int,default=16)
    a=p.parse_args()
    with tempfile.TemporaryDirectory() as tmp:
        sketch=a.sketch or make_public_fixture(Path(tmp))
        r=run(sketch,a.photo,a.hint,a.budget)
        dump(r,a.out)
        for stage in r['stage_gate']:
            print(f"{stage['status']:20} | {stage['name']} — {stage['evidence']}")
        print(f'Receipts written to: {a.out}')
if __name__=='__main__':main()
