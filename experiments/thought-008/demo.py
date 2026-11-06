"""Synthetic six-view demonstration on a real THOUGHT-007 instance."""
from __future__ import annotations
import json, sys
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0,str(Path(__file__).resolve().parent.parent / 'thought-007'))
from field import ThoughtField,canonical
from multiview import ThoughtViews, LENSES
from render import render_board


def synthetic(path):
    f=ThoughtField(path)
    for id,name,description in [
        ('home-shelter','Home','Physical shelter'),('home-belong','Home','Sense of belonging'),
        ('food','Food','Fictional donated food'),('storage','Cold storage','Fictional refrigerator'),
        ('volunteers','Volunteers','Fictional helpers'),('meal','Community meal','Fictional gathering'),
        ('van','Vehicle','Fictional transport'),('claim-open','Venue open','Fictional claim'),
        ('claim-closed','Venue closed','Fictional opposing claim')]:
        f.concept('c:'+id,name,description,'fixture:author')
    f.expression('e:home','home','fixture:text','ambiguous phrase')
    f.propose_referent('ref:shelter','e:home','c:home-shelter','literal meaning','fixture:author')
    f.propose_referent('ref:belong','e:home','c:home-belong','symbolic meaning','fixture:author')
    for id,cid,ctx in [
        ('shelter-log','home-shelter','logistics'),('shelter-values','home-shelter','values'),
        ('belong-values','home-belong','values'),('food','food','supplies'),
        ('storage','storage','logistics'),('volunteers','volunteers','staffing'),
        ('meal','meal','event'),('van','van','travel'),
        ('claim-open','claim-open','venue availability'),('claim-closed','claim-closed','venue availability')]:
        f.manifest('m:'+id,'c:'+cid,ctx,'fixture role')
    f.view('v:assoc','association','free association')
    f.view('v:hex','flower_hex','flower-of-life layout')
    f.view('v:none','NONE','source-only view')
    f.place('p:home-one','m:shelter-log','v:assoc',-1,1,'first appearance')
    f.place('p:home-two','m:shelter-log','v:assoc',1,-1,'second appearance of same manifestation')
    f.place('p:values','m:shelter-values','v:hex',.5,.866,'hex room')
    f.place('p:none','m:belong-values','v:none',None,None,'non-geometric')
    def r(id,a,b,pred,origin,status='AUTHORED'):
        return dict(id='r:'+id,source='m:'+a,target='m:'+b,predicate=pred,
                    origin='fixture:'+origin,status=status)
    relations=[
        r('food-storage','food','storage','associated','donation'),
        r('meal-storage','meal','storage','associated','recipe'),
        r('food-vol','food','volunteers','associated','staffing'),
        r('meal-vol','meal','volunteers','associated','coordination'),
        r('meal-requires-vol','meal','volunteers','requires','workplan'),
        r('meal-requires-van','meal','van','requires','transport'),
        r('meal-requires-storage','meal','storage','requires','facility'),
        r('vol-enables-meal','volunteers','meal','enables','role'),
        r('store-enables-meal','storage','meal','enables','freezer'),
        r('open-vs-closed','claim-open','claim-closed','contradicts','disagreement'),
        r('shelter-belonging','shelter-log','belong-values','associated','analogy','HYPOTHESIS_ONLY'),
    ]
    return f, relations


def main(output=None):
    with TemporaryDirectory() as temp:
        f,relations=synthetic(Path(temp)/'field.jsonl')
        before=canonical(f.semantic_snapshot())
        engine=ThoughtViews(f.snapshot(),relations)
        result=engine.run(LENSES,anchor='m:volunteers',seed=11)
        same=(canonical(f.semantic_snapshot())==before)
        replay=(ThoughtField(f.path).snapshot()==f.snapshot())
        report={
            'experiment':'THOUGHT-008','status':'PROPOSAL_ONLY','views':[v['lens'] for v in result['views']],
            'manifestations':len(f.manifestations),'concepts':len(f.concepts),
            'authored_relations':len([r for r in relations if r['status']=='AUTHORED']),
            'hypothetical_relations':len([r for r in relations if r['status']=='HYPOTHESIS_ONLY']),
            'simultaneous_assoc_home_occurrences':len([p for p in result['views'][0]['placements']
                          if p['manifestation_id']=='m:shelter-log']),
            'same_source_digest_all_views':len({v['source_evidence_digest'] for v in result['views']})==1,
            'semantic_snapshot_unchanged':same,'field_replay_exact':replay,
            'questions':result['baseline']['bridge_questions'],
            'dependency_cycles':result['baseline']['dependency']['cycles'],
            'tensions':result['baseline']['tension'],
            'affordance':result['baseline']['affordance'],
            'external_authority':'NONE',
            'limitations':'synthetic, no blinded accuracy improvement, no learned semantic embeddings',
        }
        if output:
            output=Path(output);output.mkdir(parents=True,exist_ok=True)
            (output/'parallel-thought-fields.svg').write_text(render_board(result,f.snapshot()),encoding='utf-8')
            (output/'parallel-thought-fields.json').write_text(json.dumps(result,indent=2,sort_keys=True),encoding='utf-8')
            (output/'experiment-results.json').write_text(json.dumps(report,indent=2,sort_keys=True),encoding='utf-8')
        return report

if __name__=='__main__':
    output=Path(__file__).resolve().parent if len(sys.argv)==1 else Path(sys.argv[1])
    print(json.dumps(main(output),indent=2,sort_keys=True))
