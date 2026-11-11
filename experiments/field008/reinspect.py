"""Turn an evidence contradiction into a specific local visual reinspection crop.

A selected crop is a question. It never becomes evidence of a new structure.
"""
from __future__ import annotations
from pathlib import Path
import cv2


def focus_crop(image, report:dict, out_path:str|Path, margin=.09):
    im=cv2.imread(str(image)) if isinstance(image,(str,Path)) else image
    if im is None:raise ValueError('Could not open image')
    h,w=im.shape[:2]
    by_id={r['claim_id']:r for r in report['reviews']}
    suspect=next((c for c in report['claims'] if by_id[c['id']]['verdict']=='HOLD_UNSUPPORTED_DOTTED_TRACE'),None)
    if not suspect:return {'status':'NO_UNSUPPORTED_MODEL_TRACE','crop':None,
                          'question':report['next_probe']}
    pts=suspect['points']
    x0=max(0,int((min(p[0] for p in pts)-margin)*w));x1=min(w,int((max(p[0] for p in pts)+margin)*w))
    y0=max(0,int((min(p[1] for p in pts)-margin)*h));y1=min(h,int((max(p[1] for p in pts)+margin)*h))
    # Avoid extremely thin crops; provide surrounding contextual pixels.
    pad=max(90,round(min(h,w)*.17))
    if x1-x0<pad:
        cx=(x0+x1)//2;x0=max(0,cx-pad//2);x1=min(w,x0+pad)
    if y1-y0<pad:
        cy=(y0+y1)//2;y0=max(0,cy-pad//2);y1=min(h,y0+pad)
    if x1<=x0 or y1<=y0:raise ValueError('Invalid crop')
    Path(out_path).parent.mkdir(parents=True,exist_ok=True)
    cv2.imwrite(str(out_path),im[y0:y1,x0:x1])
    return {'status':'CROP_CREATED_FOR_HUMAN_OR_OPT_IN_LOCAL_VLM',
            'claim_id':suspect['id'],'crop_file':str(out_path),'crop_pixel_bounds':[x0,y0,x1,y1],
            'crop_source_space':'original-image pixels',
            'question':'Does this cropped source image actually contain the claimed separate dashed stroke? Identify visible ink only; do not join gaps.',
            'does_not_certify_original_claim':True}
