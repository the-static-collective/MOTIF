"""MOTIF-006: verify image-in, GRAFT and CANNON before local build."""
import argparse,json,subprocess
from pathlib import Path
from hashlib import sha1,sha256
import visual_in as v

HERE=Path(__file__).resolve().parent
GRAFT='0347c492c5e517788c0cbd87ee6f57aef3ce2a81'
GRAFT_BLOB='6a3731deaa6c715e5d32ffdcd36004cf01d54cdf'
IMG_BLOB='1feded3526746c2af30346acfba191487bc705d2'
CANNON='3f2210ba6272a9538843d093edb64d1b29d2f294'
PROGRAM='493ecef0320408eed87ec4e9e56c3960f2b6a168caafaa050a22d003f0e5ebe6'
class HOLD(ValueError):pass

def blob(x):
    return sha1(b'blob '+str(len(x)).encode()+bytes([0])+x).hexdigest()
def load(p):
    p=Path(p)
    if not p.is_file() or p.stat().st_size>150000:raise HOLD('Missing bounded evidence')
    return json.loads(p.read_text())
def verify(graft,pkt,gap,start,goal,gap_path):
    graft=Path(graft).resolve()
    commit=subprocess.check_output(['git','-C',str(graft),'rev-parse','HEAD'],
          text=True,stderr=subprocess.DEVNULL,timeout=5).strip()
    src=graft/'src/visual-grammar-030.mjs'
    if commit!=GRAFT or not src.is_file() or blob(src.read_bytes())!=GRAFT_BLOB:
        raise HOLD('Original GRAFT source does not match selected commit')
    r=dict(pkt);claimed=r.pop('content_sha256',None)
    if claimed!=v.digest(r):raise HOLD('CANNON receipt digest mismatch')
    s=pkt['source_owned_generated'];e=pkt['original_png_evidence']
    a=pkt['authority'];c=pkt['fair_classical'];f=pkt['independent_final']
    refs=pkt['source_graft']['exact_git_blobs']
    refs2=pkt['source_motif_image_in']['exact_git_blobs']
    if (pkt['schema']!='cannon.visual-program-review.v0' or
        pkt['status']!='HOLD_VISUAL_SOURCE_NOT_ADMITTED' or
        pkt['source_graft']['commit']!=GRAFT or
        not any(x.get('path')=='src/visual-grammar-030.mjs' and
           x.get('git_blob_sha1')==GRAFT_BLOB for x in refs) or
        pkt['source_motif_image_in']['commit']!='6abd24ad0cb04434b22a07f56b28c638a1bdd146' or
        not any(x.get('path')=='experiments/door-foundry-006/visual_in.py' and
           x.get('git_blob_sha1')==IMG_BLOB for x in refs2) or
        e['start_sha256']!=sha256(start).hexdigest() or
        e['target_sha256']!=sha256(goal).hexdigest() or
        e['motif_question_sha256']!=gap['content_sha256'] or
        e['image_uploads_to_remote_ai']!=0 or
        s['mode']!='move' or s['source_sha256']!=PROGRAM or
        sha256(s['source'].encode()).hexdigest()!=PROGRAM or
        s['code_installed'] is not False or s['right_to_contact_apis'] is not False or
        s['generated_source_replayed'] is not True or
        f['n']!=8 or f['correct']!=8 or f['never_used_to_select_source'] is not True or
        c['correct']!=8 or c['superior_to_classical'] is not False or
        a!={'signed':False,'operator_admitted':False,'external_actions':0,
          'contacts':0,'production_deployments':0,'repository_writes':0}):
        raise HOLD('CANNON did not verify candidate and held authority')
    js=("import {pathToFileURL} from 'node:url';"+
        "import {readFileSync} from 'node:fs';"+
        "import {resolve} from 'node:path';"+
        "const m=await import(pathToFileURL(resolve(process.argv[1],"+
        "'src/visual-grammar-030.mjs')).href);"+
        "const q=JSON.parse(readFileSync(process.argv[2]));"+
        "console.log(JSON.stringify(m.compileVariant(q,'move')));")
    answer=subprocess.check_output(['node','--input-type=module','-e',js,
      str(graft),str(Path(gap_path).resolve())],
      text=True,timeout=12,stderr=subprocess.DEVNULL)
    actual=json.loads(answer)
    if (actual['source']!=s['source'] or actual['source_sha256']!=PROGRAM or
        actual['installed'] is not False or actual['network_authority']!='NONE'):
        raise HOLD('Original GRAFT cannot independently recompile reviewed code')
    if blob((HERE/'visual_in.py').read_bytes())!=IMG_BLOB:
        raise HOLD('Source-owned PNG reader changed')
    return claimed,actual
def build(start,goal,gap_path,receipt,graft,out):
    start=Path(start).read_bytes();goal=Path(goal).read_bytes()
    gap=load(gap_path);v.verify_gap(gap,start,goal)
    pkt=load(receipt)
    review_sha,compiled=verify(graft,pkt,gap,start,goal,gap_path)
    out=Path(out).resolve()
    if out.exists():raise HOLD('Refuse overwrite')
    out.mkdir(parents=True)
    for name,data in [('start.png',start),('goal.png',goal),
         ('visual_in.py',(HERE/'visual_in.py').read_bytes()),
         ('run.py',(HERE/'run_visual.py').read_bytes()),
         ('apply.mjs',(HERE/'apply.mjs').read_bytes()),
         ('new_visual_rule.mjs',compiled['source'].encode())]:
        (out/name).write_bytes(data)
    m={'schema':'motif.visual-build.v0',
       'status':'HELD_LOCAL_IMAGE_IMAGINATION_BUILD',
       'original_graft_commit':GRAFT,'original_cannon_commit':CANNON,
       'original_png_reader_blob':IMG_BLOB,
       'original_graft_grammar_blob':GRAFT_BLOB,
       'generated_visual_source_sha256':PROGRAM,
       'cannon_review_sha256':review_sha,'image_gap_sha256':gap['content_sha256'],
       'start_png_sha256':sha256(start).hexdigest(),
       'goal_png_sha256':sha256(goal).hexdigest(),
       'runner_sha256':sha256((HERE/'run_visual.py').read_bytes()).hexdigest(),
       'bridge_sha256':sha256((HERE/'apply.mjs').read_bytes()).hexdigest(),
       'scope':'TINY_THREE_COLOR_PNG_ONLY',
       'synthetic_only':True,'remote_ai_calls':0,'real_actions_authorized':False,
       'auto_admit':False}
    m['content_sha256']=v.digest(m)
    (out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
    return m
if __name__=='__main__':
    p=argparse.ArgumentParser()
    for name in ('start','goal','gap','receipt','graft','out'):
        p.add_argument('--'+name,required=True,type=Path)
    a=p.parse_args()
    try:
        o=build(a.start,a.goal,a.gap,a.receipt,a.graft,a.out)
        print(json.dumps({'status':o['status'],'build_sha256':o['content_sha256']}))
    except (HOLD,v.HOLD,subprocess.SubprocessError,OSError) as e:
        print(json.dumps({'stage':'HOLD','reason':str(e)}));raise SystemExit(1)
