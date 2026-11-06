"""THOUGHT-018: minimum source-only probe director, no model or execution powers.

This self-contained smoke test is only the first GitHub staging slice. The
complete Python + trained-model trial is a separate local review package.
"""
from collections import Counter

MECHANISMS=('KEEP','GROW','DRAIN','REPLACE','FLIP')

def independent_transition(name, before, toggled):
    if name not in MECHANISMS or not all(type(n) is int and 0<=n<8 for n in (before,toggled)):
        raise ValueError('bounded synthetic switches required')
    return {'KEEP':before,'GROW':before|toggled,'DRAIN':before&(~toggled&7),
            'REPLACE':toggled,'FLIP':before^toggled}[name]

def probe_score(active, before, toggled):
    groups=Counter(independent_transition(name,before,toggled) for name in active)
    total=len(active)
    return total*total-sum(n*n for n in groups.values())

def next_probe(active, used=()):
    if any(name not in MECHANISMS for name in active):raise ValueError('unknown mechanism')
    if len(set(active))!=len(active):raise ValueError('duplicate mechanism')
    seen=set(used)
    options=[(a,b) for a in range(8) for b in range(8) if (a,b) not in seen]
    if not options:return None
    return max(options,key=lambda pair:(probe_score(active,*pair),
                    int(pair[0]!=0 and pair[1]!=0),int(pair[0]&pair[1]!=0),-pair[0],-pair[1]))

def investigate(target, policy='adaptive', budget=6):
    """Independent toy oracle; never model-selected truth or external action."""
    if target not in MECHANISMS or policy not in ('adaptive','fixed') or not 0<=budget<=6:
        raise ValueError('invalid bounded research trial')
    alive=list(MECHANISMS);used=[];trace=[]
    schedule=[(1,1),(0,1),(1,0),(1,2),(3,1),(3,3),(2,3)]
    while len(alive)>1 and len(used)<budget:
        if policy=='fixed':
            pair=next((p for p in schedule if p not in used),None)
        else:pair=next_probe(alive,used)
        if pair is None:break
        a,b=pair;oracle=independent_transition(target,a,b)
        alive=[name for name in alive if independent_transition(name,a,b)==oracle]
        used.append(pair)
        trace.append({'probe':[a,b],'remaining':list(alive),'authority':'NONE'})
    return {'status':'QUESTION_ONLY','target':target,'policy':policy,
            'queries':len(used),'resolved':alive==[target],
            'trace':trace,'pen':'UNCHANGED','external_authority':'NONE'}
