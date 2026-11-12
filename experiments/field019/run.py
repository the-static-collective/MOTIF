import argparse,json
from pathlib import Path
from fusion import fuse,save_receipt
from synthetic import packet

def main():
    p=argparse.ArgumentParser(description='Source-preserving conditional multi-domain geometric inversion')
    p.add_argument('--input',type=Path)
    p.add_argument('--sample',choices=['synthetic','private-hold'])
    p.add_argument('--out',type=Path)
    a=p.parse_args()
    if bool(a.input)==bool(a.sample):p.error('Specify exactly one of --input or --sample')
    if a.input:
        payload=json.loads(a.input.read_text())
    elif a.sample=='synthetic':payload=packet(1,sketch_noise=.03)
    else:
        # Real sources have not been independently corresponded or camera calibrated.
        payload={'height_reference_m':1.8288,'height_source':'USER_REPORT_MOST_PANELS_APPROX',
                 'sketch_proportionality':'UNKNOWN', 'sketch_tolerance_fraction':None,
                 'landmarks':{},'views':[]}
    q=save_receipt(payload,fuse(payload))
    if a.out:
        a.out.parent.mkdir(parents=True,exist_ok=True)
        a.out.write_text(json.dumps(q,indent=2,sort_keys=True))
    print(json.dumps({k:q['output'][k] for k in ('status','reason','horizontal_m_per_sketch_unit','reprojection_rms_px')},indent=2))

if __name__=='__main__':main()
