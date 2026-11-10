"""FIELD-006 typed, local proof ledger. A content hash is NOT identity authentication.

Evidence roots come from independently rechecked source-owned archived records.
A failed *local prediction* is not a refutation of a scientific law.
Support sets are AND sets; the list of sets is OR. Acyclic lineage only.
"""
from __future__ import annotations
import hashlib
import json


def seal(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


class Lineage:
    def __init__(self):
        self.nodes = {}

    def observation(self, key, payload, owner):
        if key in self.nodes:
            raise ValueError('duplicate evidence key')
        if not owner.verify(payload):
            raise ValueError('source-origin recheck failed')
        self.nodes[key] = {'kind':'SOURCE_OBSERVATION', 'payload_sha256':seal(payload),
                           'alternatives':[], 'verdict':'VERIFIED_ARCHIVED_RECORD'}

    def claim(self, key, alternatives, claim_kind='LOCAL_PREDICTION'):
        if key in self.nodes:
            raise ValueError('duplicate claim key')
        if not alternatives or not all(group for group in alternatives):
            raise ValueError('empty support is not evidence')
        normalized=[sorted(set(group)) for group in alternatives]
        if any(len(group)!=len(set(group)) or any(k not in self.nodes for k in group) for group in alternatives):
            raise ValueError('dangling/duplicate prerequisites')
        self.nodes[key] = {'kind':claim_kind, 'alternatives':normalized, 'verdict':'PENCIL'}

    def resolve(self, key, verdict):
        if self.nodes[key]['kind']!='LOCAL_PREDICTION':
            raise ValueError('only pre-registered local predictions can be scored')
        if self.nodes[key]['verdict']!='PENCIL':
            raise ValueError('can score only once')
        if verdict not in ('OBSERVED_MATCH', 'REFUTED_LOCAL_PREDICTION'):
            raise ValueError('bad verdict')
        self.nodes[key]['verdict']=verdict

    def supported(self, key, visiting=None):
        visiting = set() if visiting is None else visiting
        if key in visiting:
            raise ValueError('cycle in provenance graph')
        node=self.nodes[key]
        if node['verdict']=='REFUTED_LOCAL_PREDICTION':
            return False
        # A proposed prediction is not a verified premise; derived nodes may
        # inherit provisional support only through observed-matching parents.
        if node['kind']=='LOCAL_PREDICTION' and node['verdict']=='PENCIL':
            return False
        if node['kind']=='SOURCE_OBSERVATION':
            return True
        visiting.add(key)
        try:
            return any(all(self.supported(x, visiting) for x in alt) for alt in node['alternatives'])
        finally:
            visiting.remove(key)

    def derived_status(self, key):
        n=self.nodes[key]
        return 'SUPPORTED_BY_SURVIVING_ROUTE' if self.supported(key) else 'HOLD_NO_SURVIVING_SUPPORT'

    def receipt(self):
        packet={'schema':'motif.field006.lineage.v1','nodes':self.nodes}
        return {'record':packet,'sha256':seal(packet)}


def check_receipt(receipt):
    if seal(receipt['record'])!=receipt['sha256']:
        return False
    nodes=receipt['record']['nodes']
    if receipt['record']['schema']!='motif.field006.lineage.v1':
        return False
    for key,node in nodes.items():
        if node['kind']=='SOURCE_OBSERVATION':
            if node['verdict']!='VERIFIED_ARCHIVED_RECORD' or not node.get('payload_sha256'):
                return False
        else:
            if not node['alternatives'] or any(not alt or any(x not in nodes for x in alt) for alt in node['alternatives']):
                return False
            if node['verdict'] not in ('PENCIL','OBSERVED_MATCH','REFUTED_LOCAL_PREDICTION'):
                return False
    # Checks packet integrity and graph structure; doesn't authenticate source.
    try:
        def visit(k, path):
            if k in path: raise ValueError('cycle')
            for alt in nodes[k]['alternatives']:
                for pre in alt: visit(pre, path|{k})
        for k in nodes:visit(k,set())
    except (KeyError, ValueError, TypeError):
        return False
    return True
