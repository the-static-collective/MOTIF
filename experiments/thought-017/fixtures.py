"""Synthetic adversarial toggle-routing tasks, distinct frozen audit seeds."""
from random import Random

COLORS=('red','blue','green')

def case(n, edges, toggles=None, initial=(), budget=0, note='', category=''):
    p={'n':n,'start':0,'goal':n-1,'risk_budget':budget,
       'initial_on':list(initial),
       'toggles':{str(i):list((toggles or {}).get(i,[])) for i in range(n)},
       'edges':[dict(u=u,v=v,cost=c,risk=r,need=list(need)) for u,v,c,r,need in edges]}
    return {'problem':p,'note':note,'category':category}

DEV=[
  case(4,[(0,1,1,0,()),(1,3,1,0,('red',)),(0,3,7,0,())],{1:['red']},initial=('red',),note='switch red off; tempting gate invalid',category='off_gate'),
  case(4,[(0,1,1,0,()),(1,2,1,0,()),(2,3,1,0,('red',)),(1,3,1,0,('red',)),(0,3,7,0,())],{1:['red'],2:['red']},initial=('red',),note='turn red off then on again',category='toggle_twice'),
  case(4,[(0,1,1,0,()),(1,2,1,0,()),(2,3,1,0,('red',)),(0,3,8,0,())],{1:['red'],2:['red']},note='red on then off: gate closed again',category='nonmonotone'),
  case(4,[(0,1,1,0,()),(1,3,1,0,('red','blue')),(0,3,6,0,())],{1:['red','blue']},initial=('red','blue'),note='two switches simultaneously off',category='multi'),
  case(4,[(0,1,1,0,()),(1,3,1,0,('red',)),(0,3,9,0,())],{1:['red']},note='one switch turns on: gate opens',category='positive'),
  case(4,[(0,1,3,0,()),(1,3,2,0,()),(0,3,8,0,())],note='no switches weighted shortest route',category='control'),
  case(5,[(0,1,1,0,()),(1,2,1,0,()),(2,4,1,0,('blue',)),(0,4,9,0,()),(1,4,1,0,('blue',))],{1:['blue'],2:['blue']},note='blue erased before passing final gate',category='loss'),
  case(5,[(0,1,1,0,()),(1,2,1,0,()),(2,4,1,0,('green',)),(0,4,7,0,()),(1,4,1,0,('green',))],{1:['green'],2:['green']},initial=('green',),note='green off then restored',category='restoration'),
]
SAFETY=[
 case(3,[(0,1,1,0,()),(1,2,1,0,('red',)),(0,2,5,0,())],{1:['red']},initial=('red',),note='false positive gate after toggle refused'),
 case(4,[(0,1,1,0,()),(1,3,1,0,('blue',))],{1:['blue']},note='positive gate still works'),
 case(4,[(0,1,1,0,()),(1,3,1,1,('blue',))],{1:['blue']},budget=0,note='risk never bypassed'),
 case(4,[(0,1,1,0,()),(1,0,1,0,())],note='cycle cannot certify unreachable goal'),
]

def cases(seed,count):
    r=Random(seed);out=[]
    for k in range(count):
        if k%2==0:
            # A deliberately discriminating gate-off gadget: the simpler
            # monotone approximation falsely crosses red gate after switch-off.
            alternative=r.randint(5,12);branch_cost=r.randint(1,3)
            selected=r.choice(COLORS)
            out.append(case(4,[(0,1,1,0,()),(1,3,branch_cost,0,(selected,)),
                               (0,3,alternative,0,())],{1:[selected]},initial=(selected,),
                               category='gadget',note='frozen discriminating toggle-off gadget'))
            continue
        n=r.randint(4,7);toggles={i:[] for i in range(n)}
        for i in range(n):
            if r.random()<.48:toggles[i]=[r.choice(COLORS)]
        edges=[]
        for u in range(n):
            for v in range(n):
                if u==v or r.random()>.31:continue
                need=[r.choice(COLORS)] if r.random()<.27 else []
                edges.append((u,v,r.randint(1,9),r.randint(0,2),need))
        if not edges:edges=[(0,n-1,8,0,())]
        edges=edges[:20]
        initial=r.sample(COLORS,r.randint(0,2))
        out.append(case(n,edges,toggles,initial,r.randint(0,4),
                        note='frozen random switch network',category='random'))
    return out

AUDIT=cases(170171,60)
STRESS=cases(170172,80)

# Developer generator: creates a discriminating counterexample without access
# to the frozen audit or stress. Oracle will judge generated cases separately.
def challenge_cases():
    return [
      case(4,[(0,1,1,0,()),(1,3,1,0,('red',)),(0,3,10,0,())],{1:['red']},initial=('red',),note='switch off blocks shortcut',category='challenge'),
      case(4,[(0,1,1,0,()),(1,2,1,0,()),(2,3,1,0,('red',))],{1:['red'],2:['red']},initial=('red',),note='reversible switch restores route',category='challenge'),
      case(3,[(0,1,2,0,()),(1,2,2,0,('blue',))],{1:['blue']},note='one toggle on',category='challenge'),
    ]
