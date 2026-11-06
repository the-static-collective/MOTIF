"""Reproducible synthetic grammar revision and isolated competing graph futures."""
import json
from living_graph import RewriteGrammar, RewriteRule, LivingGraph
from grammar_invention import Example, propose_revision, compare_fork, preserve_proposal


def scenario():
    parent = RewriteGrammar('demo:declared', (
        RewriteRule('grow-seed', ('seed',), ('bud',)),
        RewriteRule('revisit-seed', ('bud',), ('seed',)),
    ))
    train = [
        Example('oak', ('oak','bud'), ('oak','branch'), True, 'claimed:oak'),
        Example('pine', ('pine','bud'), ('pine','branch'), True, 'claimed:pine'),
        Example('birch', ('birch','bud'), ('birch','branch'), True, 'claimed:birch'),
        Example('negative', ('oak','bud'), ('oak','leaf'), False, 'claimed:control'),
    ]
    heldout = [
        Example('spruce', ('spruce','bud'), ('spruce','branch'), True, 'claimed:heldout1'),
        Example('cedar', ('cedar','bud'), ('cedar','branch'), True, 'claimed:heldout2'),
        Example('wrong-leaf', ('spruce','bud'), ('spruce','leaf'), False, 'claimed:heldout3'),
        Example('wrong-source', ('spruce','leaf'), ('spruce','branch'), False, 'claimed:heldout4'),
    ]
    return parent,train,heldout


def run():
    parent,train,heldout=scenario()
    proposed=propose_revision(parent,train,heldout,candidate_budget=1000)
    assert proposed['status']=='PENCIL_GRAMMAR_REVISION_PROPOSED',proposed
    fork=compare_fork(parent,proposed['rule'],[('oak','seed'),('pine','seed')],
                      [('oak','branch'),('pine','branch')],work_budget=200)
    with LivingGraph(scope=parent.scope) as archive:
        receipt=preserve_proposal(archive,parent,proposed,train,heldout)
        validity=archive.verify()
        catalog=archive.counts()
    return {'experiment':'GEOM-009 self-questioning grammar / synthetic',
            'proposal':proposed,'isolated_counterfactual_graphs':fork,
            'archived_pencil_receipt':receipt,'archive_integrity':validity,
            'archive_counts':catalog,
            'interpretation':'classical supervised rewrite induction; no automatic grammar binding or real-world knowledge'}

if __name__=='__main__':
    print(json.dumps(run(),indent=2,sort_keys=True))
