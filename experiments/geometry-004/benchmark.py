"""Fixed development benchmarks; not preregistered or statistical generalization."""
import json,random
from invention import point,nondegenerate,centroid_direct,run,discover,candidate_programs,apply

def triangles(n,seed):
    r=random.Random(seed)
    result=[]
    while len(result)<n:
        t=tuple(point(r.randint(-17,17),r.randint(-17,17)) for _ in range(3))
        if nondegenerate(t) and t not in result:result.append(t)
    return result

def main():
    train=triangles(3,40)
    adversarial=triangles(20,41)
    holdout=triangles(60,42)
    model=discover(train,adversarial)
    assert model['status']=='PROPOSAL_ONLY'
    learned=[run(model['method'], t)==centroid_direct(t) for t in holdout]
    classical=[centroid_direct(t)==centroid_direct(t) for t in holdout]
    return {'experiment':'MOTIF-GEOM-004','method':model['signature'],
            'method_size':model['method'].size(),'invented_macro':model['invented_macro'],
            'old_grammar_candidates':len(candidate_programs(False)),
            'expanded_grammar_candidates':len(candidate_programs(True)),
            'teacher_triangles':len(train),'adversarial_triangles':len(adversarial),
            'holdout_triangles':len(holdout),'learned_correct':sum(learned),
            'classical_correct':sum(classical),'learned_wrong':len(learned)-sum(learned),
            'authority':model['authority'],'claim':'invented reusable intermediate macro; not a new math primitive'}

if __name__=='__main__':print(json.dumps(main(),indent=2))
