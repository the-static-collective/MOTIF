"""Provisional grounding atop the existing FIELD-006 AND/OR lineage mechanism.

This is a *ranked support receipt*, never a calibrated likelihood that a
hypothesis is true. Count distinct provenance origins rather than copies.
"""
from __future__ import annotations
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'field006'))
from lineage import Lineage


class BlanchLedger(Lineage):
    def __init__(self):
        super().__init__()
        self.origin = {}

    def ink(self, key, receipt, owner):
        origin = receipt.get('provenance_origin')
        if not isinstance(origin, str) or not origin:
            raise ValueError('NO_ORIGIN')
        self.observation(key, receipt, owner)
        self.origin[key] = origin

    def blanch(self, key, alternatives):
        self.claim(key, alternatives, claim_kind='CONDITIONAL_PROJECTION')
        return self.grounding(key)

    def grounding(self, key):
        """Best *coherent* AND path's independent provenance support.

        Multiple mutually alternative OR paths cannot be combined to inflate
        support. No speculative node, however well supported, is INK.
        """
        def paths(k, visiting):
            if k in visiting:
                raise ValueError('CYCLE')
            node = self.nodes[k]
            if node['kind']=='SOURCE_OBSERVATION':
                return [frozenset([self.origin[k]])]
            if node['verdict']=='REFUTED_LOCAL_PREDICTION':
                return []
            result=[]
            for alt in node['alternatives']:
                combined=[frozenset()]
                for pred in alt:
                    p=paths(pred,visiting|{k})
                    if not p:
                        combined=[];break
                    combined=[a|b for a in combined for b in p]
                result.extend(combined)
            return result
        sets = paths(key,set())
        best=max(sets,key=lambda s:(len(s),sorted(s))) if sets else frozenset()
        return {'key':key,'state':'PENCIL_CONDITIONAL' if sets else 'HOLD_CONTRADICTED',
                'independent_origin_count':len(best),
                'best_route_origins':sorted(best),
                'possible_support_routes':len(sets),
                'source_authentication':'SIMULATED_OWNER_RECHECK_NOT_REAL_AUTHENTICATION'}
