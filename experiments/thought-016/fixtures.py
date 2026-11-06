"""Fictional gated traversal tasks; heldout seeds never passed to the proposer."""
from random import Random

def graph(n,edges,pickups=None,budget=0,note='',category=''):
    p={'n':n,'start':0,'goal':n-1,'risk_budget':budget,
       'edges':[dict(u=a,v=b,cost=c,risk=r,need=list(need)) for a,b,c,r,need in edges],
       'pickups':{str(i):list((pickups or {}).get(i,[])) for i in range(n)}}
    return {'problem':p,'note':note,'category':category}

DEV=[
  graph(4,[(0,3,1,0,['red']),(0,1,1,0,[]),(1,3,2,0,['red'])],{1:['red']},note='gate needs red key; route through pickup',category='guard'),
  graph(4,[(0,1,1,0,[]),(1,0,1,0,[]),(0,3,1,0,['red'])],{1:['red']},note='must revisit origin with collected red key',category='revisit'),
  graph(5,[(0,1,1,0,[]),(1,2,1,0,['red']),(2,4,1,0,['blue']),(1,3,1,0,[]),(3,2,1,0,[])],{1:['red'],3:['blue']},note='blue key must be collected at node 3 before gate to goal',category='collection'),
  graph(5,[(0,4,1,4,[]),(0,1,2,0,[]),(1,4,2,0,[])],{},budget=0,note='risk budget rejects cheapest direct route',category='risk'),
  graph(5,[(0,1,1,1,[]),(0,2,2,0,[]),(2,1,1,0,[]),(1,4,1,1,[])],{},budget=1,note='same location different risk remaining',category='risk_state'),
  graph(5,[(0,4,9,0,[]),(0,1,1,0,[]),(1,4,1,0,[])],{},budget=0,note='weighted priority not merely direct hop',category='weighted'),
  graph(5,[(0,1,1,0,[]),(1,4,1,0,['blue'])],{1:['red']},note='cannot cross gate because blue pickup missing',category='gate_impossible'),
  graph(5,[(0,1,1,0,[]),(1,0,1,0,[]),(0,4,1,0,['red'])],{1:['red']},note='state identity must retain new inventory on revisit',category='identity'),
  graph(6,[(0,1,1,0,[]),(1,0,1,0,[]),(0,3,1,0,['red']),(3,2,1,0,[]),(2,3,1,0,[]),(3,5,1,0,['blue'])],{1:['red'],2:['blue']},note='two distinct keys and multiple revisits needed',category='composition'),
]
SAFETY=[
 graph(3,[(0,2,1,0,['red'])],note='locked shortcut without key is not a valid route'),
 graph(4,[(0,1,1,0,[]),(1,3,1,0,['red'])],{1:['red']},note='valid key route still permitted'),
 graph(4,[(0,1,1,1,[]),(1,3,1,0,[])],budget=0,note='risk bound cannot be bypassed'),
 graph(4,[(0,1,1,0,[]),(1,0,1,0,[])],note='unreachable goal returns none even with cycle'),
]
# Frozen independent synthetic seeds. These are not blind independent real-world tasks.
def random_cases(seed,count=64):
    r=Random(seed);result=[]
    keys=['red','blue','green']
    for i in range(count):
        n=r.randint(4,7);pickup={j:[] for j in range(n)}
        for j in range(1,n-1):
            if r.random()<.35:pickup[j].append(r.choice(keys[:2]))
        e=[]
        for a in range(n):
            for b in range(n):
                if a==b or r.random()>.31:continue
                need=[r.choice(keys[:2])] if r.random()<.2 else []
                e.append((a,b,r.randint(1,9),r.randint(0,2),need))
        if not e:e=[(0,n-1,4,0,[])]
        if len(e)>20:e=e[:20]
        result.append(graph(n,e,pickup,r.randint(0,5),note='unseen synthetic gated graph',category='random'))
    return result
AUDIT=random_cases(161600,72)
STRESS=random_cases(161699,54)
# Paired test candidate proposals from a distinct test-generating component, not oracle.
def discriminating_tests():
    return [
      graph(4,[(0,1,1,0,[]),(1,0,1,0,[]),(0,3,1,0,['red'])],{1:['red']},note='gate after collecting key via required cycle',category='model_proposed_probe'),
      graph(4,[(0,1,1,0,[]),(1,3,1,0,['blue'])],{1:['red']},note='key name mismatch must reject edge',category='model_proposed_probe'),
      graph(5,[(0,1,1,0,[]),(0,2,2,0,[]),(1,4,1,0,['red']),(2,4,1,0,[])],{1:['red']},note='preferred path with pickup beats plain route',category='model_proposed_probe')
    ]
TRAIN=[
 ('a gate requires a key held in inventory','GATE'),('locked edge needs a matching key','GATE'),
 ('collect a red key at a node','PICKUP'),('arrival collects token into inventory','PICKUP'),
 ('same vertex with different keys gives different future moves','KEY_STATE'),('distinguish inventory states after picking a token','KEY_STATE'),
 ('must go back to an earlier vertex with a newly acquired key','REVISIT'),('loop to origin after pickup is necessary','REVISIT'),
 ('the cheapest edge violates risk budget','RISK'),('reject edges that exceed remaining hazard','RISK'),
]
