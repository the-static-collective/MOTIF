"""Evidence route proposals from indexed MOTIF artifacts, not answer-key data.

Navigation hints are merely ranked filenames and typed graph IDs. They are not
oracle labels, trusted quotes, factual assertions or compulsory model actions.
"""
from __future__ import annotations
import re
from pathlib import Path

STOP=set('the and this that from with into only each given there their have will would your than what which when were was who for are can how list return items item new old set sets an a by to in on of at is not it be or as if do does then all some above remove field record two three names currently'.split())
BOOST={'graph_or_symbolic_structure':3.0,'geometry_or_thought_space':2.5,
       'proof_or_evidence':2.5,'derived_claimed_proof_graph':2.0,
       'reasoning_cartridge':2.0,'evaluation_receipt':1.5,'research_document':1.0,
       'source_code_as_data':0.5}

class NavigationError(ValueError):pass

def terms(text):
    if type(text) is not str:return set()
    return {x for x in re.findall('[a-z][a-z0-9_]{2,}',text.lower()) if x not in STOP}

class EvidenceNavigator:
    """A source-owner heuristic; no task oracle, target policy or model output used."""
    def __init__(self,portal):
        self.portal=portal
        self.ids=list(portal._items)
    def orient(self,public_task,history=(),*,max_suggestions=6):
        if type(public_task) is not dict or set(public_task)!={'story','input_fields','feature_count','meaning'}:
            raise NavigationError('unexpected task brief')
        if type(max_suggestions) is not int or not 1<=max_suggestions<=12:
            raise NavigationError('suggestion budget exceeded')
        q=terms(public_task['story'])
        q|=set().union(*(terms(x.get('human_description','')) for x in public_task['input_fields']))
        used=set();requests=set()
        for entry in history:
            if type(entry) is not dict:continue
            if entry.get('stage')=='READ_ONLY_TOOL':
                req=entry.get('request',{})
                if type(req) is dict:
                    if type(req.get('artifact_id')) is str:used.add(req['artifact_id'])
                    requests.add(str(sorted(req.items())))
        ranked=[]
        for aid in self.ids:
            meta,content,_=self.portal._items[aid]
            if aid in used:continue
            path_terms=terms(aid.replace('/',' ').replace('-',' ').replace('_',' '))
            description_terms=terms((content or '')[:3500])
            matched=q & (path_terms|description_terms)
            if not matched:continue
            score=4*len(q&path_terms)+min(3,len(q&description_terms)) + BOOST.get(meta['kind'],0)
            if score<=0:continue
            ranked.append({'artifact_id':aid,'kind':meta['kind'],'score':round(score,2),
                           'matched_terms':sorted(matched)[:5],
                           'truth_status':meta.get('truth_status','UNVERIFIED_INDEX_DATA')})
        ranked.sort(key=lambda x:(-x['score'],x['artifact_id']))
        # Diversify by artifact KIND before filling the rest: no repeated
        # source filename monopolizing the LLM's attention.
        selected=[];kinds=set()
        for item in ranked:
            if item['kind'] not in kinds:
                selected.append(item);kinds.add(item['kind'])
                if len(selected)>=max_suggestions:break
        for item in ranked:
            if len(selected)>=max_suggestions:break
            if item not in selected:selected.append(item)
        selected.sort(key=lambda x:(-x['score'],x['artifact_id']))
        graph_rows=[]
        for g in self.portal._graphs.values():
            if g.get('artifact_id') in {x['artifact_id'] for x in selected}:
                graph_rows.append({'graph_id':g['id'],'kind':g['kind'],
                                   'node_count':g['node_count'],'edge_count':g['edge_count']})
        return {'schema':'motif.thought030.evidence-route.v1',
                'task_terms':sorted(q)[:28],
                'suggestions':selected,
                'related_graph_views':graph_rows[:max_suggestions],
                'already_inspected_artifacts':sorted(used)[:20],
                'relevance_is_unverified':True,
                'not_a_task_answer':True,
                'not_model_authority':True,
                'model_may_ignore_route':True}
