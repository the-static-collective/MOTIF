"""Transparent authored cross-domain demonstrations; NOT blind learning results."""
import json
from pathlib import Path
from visual_thought import Scene,Object,run,think,svg_sketch


def o(id,label,current,cap,features,movable='UNKNOWN',box=None):
    return Object(id,label,current,tuple(cap),tuple(features),'SYNTHETIC',movable,box,source='synthetic-fixture')

def scenarios():
    return {
      'yard':Scene('Mark revised dog boundary','delineate',(
        o('fence','old chain-link','old perimeter',['delineate'],['rigid','flat'],'UNKNOWN',(.1,.2,.3,.5)),
        o('panel','cage panel','animal cage',['delineate'],['rigid','flat'],'YES',(.4,.2,.5,.5)),
        o('tie','outdoor ties','strap',['hold'],['connector'],'YES'),
        o('frame','trampoline frame','recreation',['support'],['frame'],'NO',(.6,.3,.9,.8))),
        ((.1,.6),(.7,.6)),((.1,.3),(.9,.3))),
      'shelving':Scene('Build shelves from excess materials','support',(
        o('crateA','shipping crate','shipping',['support'],['rigid','container'],'YES'),
        o('crateB','spare crate','shipping',['support'],['rigid','container'],'YES'),
        o('board','scrap board','offcut',['support'],['rigid','surface'],'YES'),
        o('clip','clamp','clamping',['hold'],['connector'],'YES'),
        o('wall','wall stud','building',['support'],['frame'],'NO'))),
      'rain_shelter':Scene('Create dry storage cover','shelter',(
        o('sheet','old tarp','covering',['shelter'],['flexible','flat'],'YES'),
        o('awning','collapsible awning','outdoor shade',['shelter'],['rigid','frame'],'UNKNOWN'),
        o('wall','existing framework','building',['support'],['frame'],'NO'),
        o('cord','rope','tying',['hold'],['connector'],'YES'))),
      'organizing':Scene('Organize scattered tools','organize',(
        o('boxA','clean storage bin','shipping',['organize'],['rigid','container'],'YES'),
        o('boxB','second bin','shipping',['organize'],['rigid','container'],'YES'),
        o('table','old table','dining',['support','organize'],['rigid','frame'],'YES'),
        o('straps','hook straps','securing',['hold'],['connector'],'YES'))),
      'pathway':Scene('Reconfigure a temporary route','route',(
        o('panelA','removable board','decorative panel',['route'],['rigid','flat'],'YES'),
        o('panelB','removable board 2','decorative panel',['route'],['rigid','flat'],'UNKNOWN'),
        o('gate','fixed gate','entrance',['route'],['frame'],'NO'),
        o('hooks','clips','hanger',['hold'],['connector'],'YES')))
    }

def report(output_dir:Path):
    output_dir.mkdir(parents=True,exist_ok=True)
    out={}
    for name,scene in scenarios().items():
        ops=[p.operation for p in think(scene)]
        # Very weak literal-only baseline: no counterfactual search or role changes.
        baseline=sum(scene.desired_function==x.original_use for x in scene.things)
        result=run(scene)
        (output_dir/(name+'.svg')).write_text(svg_sketch(scene,think(scene)),encoding='utf8')
        (output_dir/(name+'.json')).write_text(json.dumps(result,indent=2),encoding='utf8')
        out[name]={'literal_current_use_matches':baseline,'counterfactual_proposals':len(ops),
                   'operator_families':sorted(set(ops)),
                   'all_unverified':all(x['status']!='VERIFIED' for x in result['critique'])}
    # negative controls: don't invent existing joiners, movability, or physics
    return out

if __name__=='__main__':
    result=report(Path('outputs'))
    print(json.dumps({'evaluation':'AUTHORED_NON_BLIND_NO_REAL_VLM', 'cases':result},indent=2))