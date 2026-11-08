"""Proof-aware read-only evidence relay for MOTIF-031.

Source-owned route based only on PUBLIC task language, artifact structure and
source labels. No evaluator policies, hidden target masks, or frozen results
are read. A model's citations must reference actual retrieved receipts.
"""
from __future__ import annotations
import sys,re,copy
from pathlib import Path
HERE=Path(__file__).resolve().parent
for d in ('thought-029','thought-030'):
    p=str(HERE.parent/d)
    if p not in sys.path:sys.path.insert(0,p)
from artifact_portal import ArtifactPortal,PortalError,compact
from navigation import EvidenceNavigator,terms

SCHEMA='motif.thought031.evidence-relay.v1'
SAFE_SEEDS=(
    'experiments/thought-027/proof_memory.py',
    'experiments/geometry-005/thought-source.json',
    'experiments/thought-028/weave.py',
    'experiments/thought-027/reuse.py',
    'experiments/thought-023/grammar.py',
    'experiments/thought-008/multiview.py',
)
# Exclude task owner's answers, test fixtures, and historical trial result files
# from prefetch. This is not a guarantee that all public source is blind.
BLOCK=re.compile(r'(^|/)(specimens|stage_fixtures|test_[^/]*|offline-results|real-model-results|live-results|[a-z-]*results)\.(?:py|json)$',re.I)
class RelayError(ValueError):pass

class EvidenceRelay:
    def __init__(self,portal):
        if not isinstance(portal,ArtifactPortal):raise RelayError('explicit reviewed portal required')
        self.portal=portal
        self.nav=EvidenceNavigator(portal)
    def _safe(self,id_):
        return type(id_) is str and id_ in self.portal._items and not BLOCK.search(id_)
    def plan(self,public_task,*,limit=3):
        if type(limit) is not int or not 1<=limit<=5:raise RelayError('bounded plan required')
        route=self.nav.orient(public_task,max_suggestions=12)
        candidates=[]
        for id_ in SAFE_SEEDS:
            if self._safe(id_):candidates.append(id_)
        for x in route['suggestions']:
            id_=x['artifact_id']
            if self._safe(id_) and id_ not in candidates:candidates.append(id_)
        if not candidates:raise RelayError('no admissible artifacts')
        # Include useful proof and native graph views for mixed reasoning. The
        # top candidates are intentionally not derived from target answers.
        selected=[]
        for id_ in candidates:
            if len(selected)>=limit:break
            if id_ not in selected:selected.append(id_)
        return {'schema':SCHEMA,'selected_artifact_ids':selected,
                'admissibility':'PUBLIC_REPO_NO_TASK_SPECIMENS_OR_TEST_RESULTS_IN_PREFETCH',
                'source_selected_without_target_oracle':True,
                'all_material_is_untrusted_data':True,
                'selection_does_not_certify_relevance':True}
    def inspect(self,plan,*,page_limit=7):
        if type(page_limit) is not int or not 1<=page_limit<=12:raise RelayError('page budget')
        cards=[]
        for id_ in plan['selected_artifact_ids']:
            if not self._safe(id_):raise RelayError('invalid or blocked source')
            result=self.portal.query({'tool':'read','artifact_id':id_,'limit':page_limit})
            if result.get('artifact',{}).get('id')!=id_:raise RelayError('portal returned wrong source')
            meta=result['artifact']
            cards.append({'artifact_id':id_,'kind':meta['kind'],'sha256':meta['sha256'],
                'truth_status':meta['truth_status'],'retrieved_by_source_owned_portal':True,
                'page_offset':result['offset'],'next_cursor':result['next_cursor'],
                'excerpts':copy.deepcopy(result['items'])[:page_limit],
                'source_content_does_not_speak_as_system':True})
        # Native graph previews expose actual typed node/edge data, not a
        # picture or a prose assertion. These are untrusted graph statements.
        for card in cards:
            item=self.portal._items[card['artifact_id']][2]
            if type(item) is dict and type(item.get('nodes')) is list and type(item.get('edges')) is list:
                graph_nodes=self.portal.query({'tool':'read','artifact_id':card['artifact_id'],
                                               'pointer':'/nodes','limit':5})
                graph_edges=self.portal.query({'tool':'read','artifact_id':card['artifact_id'],
                                               'pointer':'/edges','limit':5})
                card['native_graph_sample']={'nodes':graph_nodes['items'],
                                             'edges':graph_edges['items'],
                                             'graph_claims_not_verification':True}
        # Explicit structured graph metadata stays separate from truth/proofs.
        graph_views=[{'graph_id':g['id'],'artifact_id':g['artifact_id'],
                      'kind':g['kind'],'node_count':g['node_count'],
                      'edge_count':g['edge_count'],
                      'relationships_not_independently_verified':True}
                    for g in self.portal._graphs.values() if g['artifact_id'] in plan['selected_artifact_ids']]
        return {'schema':SCHEMA,'cards':cards,'graphs':graph_views[:10],
            'actually_read_artifact_ids':sorted(c['artifact_id'] for c in cards),
            'no_task_owner_answer_or_frozen_evidence_supplied':True,
            'context_not_an_independent_knowledge_claim':True}
    def prepare(self,public_task,*,limit=3):
        plan=self.plan(public_task,limit=limit)
        return {'plan':plan,'packet':self.inspect(plan)}
