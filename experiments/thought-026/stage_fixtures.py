"""Scripted model fixtures. NOT LLM; these solely exercise and falsify stage machinery."""
from __future__ import annotations
from copy import deepcopy
from stages import RELATIONS

# Reference labels are owned by a fixture for regression testing ONLY.
# Not imported by the direct-model implementation, prompts or real-model runs.
LABELS={'DIFF':'DIFFERENCE','INTERSECTION':'INTERSECTION','UNION':'UNION',
        'SECOND':'SECOND','INVERT':'COMPLEMENT','XOR':'SYMMETRIC_DIFFERENCE'}
class DeterministicStages:
    kind='SCRIPTED_FIXTURE_NOT_LLM'
    def __init__(self,incorrect_binding=False,incorrect_relation=False,repair_correct=True):
        self.calls=[];self.incorrect_binding=incorrect_binding
        self.incorrect_relation=incorrect_relation;self.repair_correct=repair_correct
    def _truth(self,task):
        from pathlib import Path
        import sys
        p=str(Path(__file__).resolve().parent.parent/'thought-025')
        if p not in sys.path:sys.path.insert(0,p)
        from specimens import BY_KEY
        from specimens import public_brief
        match=next((s for s in BY_KEY.values() if s.description==task['story']),None)
        if match is None:raise ValueError('unknown scripted test specimen')
        return match
    def bind(self,public):
        task=self._truth(public)
        self.calls.append({'stage':'BIND','simulated':True})
        ids=task.roles[::-1] if self.incorrect_binding else task.roles
        return {'bindings':{'current':ids[0],'event':ids[1]},
                'rationale':'Scripted fixture field selection'}
    def relate(self,public,roles):
        task=self._truth(public)
        self.calls.append({'stage':'RELATION','simulated':True})
        label='UNION' if self.incorrect_relation else LABELS[task.policy]
        return {'relation':label,'rationale':'Scripted fixture relation selection'}
    def repair(self,public,roles,relation,witnesses,diagnosis):
        task=self._truth(public)
        self.calls.append({'stage':'REPAIR','simulated':True})
        ids=task.roles if self.repair_correct else task.roles[::-1]
        label=LABELS[task.policy] if self.repair_correct else 'UNION'
        return {'binding':{'bindings':{'current':ids[0],'event':ids[1]},
                           'rationale':'Scripted fixture repaired binding'},
                'relationship':{'relation':label,
                          'rationale':'Scripted fixture repaired relation'}}
