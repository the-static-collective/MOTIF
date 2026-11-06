"""Fixed synthetic cases adapted from THOUGHT-008; not blind validation."""
from __future__ import annotations
import sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
PARENT=HERE.parent
for folder in (PARENT/'thought-007',PARENT/'thought-008'):
    if str(folder) not in sys.path:sys.path.append(str(folder))
from field import ThoughtField
from multiview import ThoughtViews


def make_engine(path, variant='full'):
    field=ThoughtField(path)
    names=['food','storage','volunteers','meal','van','claim-open','claim-closed','shelter','belonging']
    for n in names:
        field.concept('c:'+n,n.replace('-',' ').title(),'Synthetic '+n,'fixture:operator')
        field.manifest('m:'+n,'c:'+n,'mock reasoning context','scenario')
    field.expression('e:home','home','fixture:expression','ambiguous fixture')
    field.propose_referent('p:shelter','e:home','c:shelter','one sense','fixture:author')
    field.propose_referent('p:belong','e:home','c:belonging','another sense','fixture:author')
    rels=[]
    def edge(code,sub,obj,pred,origin='fixture:one',status='AUTHORED'):
        rels.append(dict(id='r:'+code,source='m:'+sub,target='m:'+obj,
                         predicate=pred,origin=origin,status=status))
    if variant not in ('empty','tension_only','dependencies_only'):
        edge('f-s','food','storage','associated','fixture:root-a')
        edge('m-s','meal','storage','associated','fixture:root-b')
        edge('f-v','food','volunteers','associated','fixture:root-a')
        edge('m-v','meal','volunteers','associated','fixture:root-b')
    if variant not in ('empty','association_only','tension_only'):
        edge('m-v-req','meal','volunteers','requires')
        edge('m-s-req','meal','storage','requires')
        edge('m-van-req','meal','van','requires')
        edge('v-enable-m','volunteers','meal','enables')
    if variant not in ('empty','association_only','dependencies_only'):
        edge('dispute','claim-open','claim-closed','contradicts','fixture:dispute')
    edge('unreviewed','shelter','belonging','associated','fixture:analogy','HYPOTHESIS_ONLY')
    return ThoughtViews(field.snapshot(),rels)
