"""Deterministic fictional source graphs. Real THOUGHT-007 identities, 008 analyses."""
from pathlib import Path
import sys
for family in ('thought-007','thought-008'):
    folder=Path(__file__).resolve().parent.parent / family
    if not folder.is_dir(): folder=Path(__file__).resolve().parent.parent / family.replace('-', '')
    if str(folder) not in sys.path: sys.path.append(str(folder))
from field import ThoughtField
from multiview import ThoughtViews


def make_engine(path, variant='complete'):
    if variant not in ('complete','no_tension','no_requirements','no_affordances','no_bridge','hypothesis_only'):
        raise ValueError('unknown fixture variant')
    field=ThoughtField(path)
    terms=['food','meal','storage','volunteers','van','venue-open','venue-closed','home-shelter','home-belonging']
    for n in terms:
        field.concept('c:'+n, 'Home' if n.startswith('home-') else n.replace('-',' ').title(),
                      'Fictional concept '+n,'fixture:origin')
        field.manifest('m:'+n,'c:'+n,'synthetic community-meal inquiry','reasoning role')
    field.expression('word:home','home','fixture:text','ambiguous text')
    field.propose_referent('referent:literal','word:home','c:home-shelter','possible shelter meaning','fixture:text')
    field.propose_referent('referent:metaphor','word:home','c:home-belonging','possible belonging meaning','fixture:text')
    field.view('view:association','association','source illustration')
    field.place('p:one','m:food','view:association',0,0,'first appearance')
    field.place('p:two','m:food','view:association',1,1,'second appearance same manifestation')
    relations=[]
    def add(id,a,b,pred,origin='fixture:root0',status='AUTHORED'):
        relations.append({'id':'r:'+id,'source':'m:'+a,'target':'m:'+b,
                          'predicate':pred,'origin':origin,'status':status})
    if variant != 'no_bridge':
        stat='HYPOTHESIS_ONLY' if variant=='hypothesis_only' else 'AUTHORED'
        for id,a,b,o in [('food-storage','food','storage','fixture:a'),
                          ('food-volunteers','food','volunteers','fixture:a'),
                          ('meal-storage','meal','storage','fixture:b'),
                          ('meal-volunteers','meal','volunteers','fixture:b')]:
            add(id,a,b,'associated',o,stat)
    if variant != 'no_requirements':
        add('meal-needs-van','meal','van','requires')
        add('meal-needs-venue','meal','venue-open','requires')
    if variant != 'no_tension':
        add('disputed-venue','venue-open','venue-closed','contradicts')
        # decoy, outside the same local inquiry neighborhood:
        add('disputed-home','home-shelter','home-belonging','contradicts')
    if variant != 'no_affordances':
        add('volunteers-enable-meal','volunteers','meal','enables')
    add('hypothetical-direct','food','meal','associated','fixture:pencil','HYPOTHESIS_ONLY')
    return field,ThoughtViews(field.snapshot(),relations),relations
