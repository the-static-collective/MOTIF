"""MOTIF THOUGHT-012: preserve a pencil inquiry while rotating reasoning lenses.

All inspections are over one frozen, authored THOUGHT-008 evidence graph.
Projection positions never create relations, support, PEN, or outside authority.
This is deterministic classical evidence inspection, NOT autonomous cognition.
"""
from __future__ import annotations

import copy
from hashlib import sha256
from json import dumps
from pathlib import Path
import sys

for family in ('thought-008','thought-009'):
    location = Path(__file__).resolve().parent.parent / family
    if not location.is_dir(): location = Path(__file__).resolve().parent.parent / family.replace('-', '')
    if str(location) not in sys.path: sys.path.append(str(location))
from multiview import ThoughtViews, ViewError

SCHEMA = 'motif.thought-cross-lens.v1'
LENSES = ('association', 'dependency', 'tension', 'affordance', 'flower_hex', 'NONE')
MAX_STEPS = 5


def canonical(obj):
    return dumps(obj, sort_keys=True, ensure_ascii=True, allow_nan=False,
                 separators=(',', ':')).encode('utf-8')


def sha(obj):
    return sha256(canonical(obj)).hexdigest()


def _require(condition, reason):
    if not condition: raise ViewError(reason)


def _question(kind, topic, text, witnesses, *, origin_lens, related=(), seed_only=False):
    """An inquiry is a question, never testimony or an asserted relation."""
    _require(bool(text) and len(text) < 400, 'invalid question')
    _require(bool(witnesses) or seed_only, 'a sourced question must name source evidence')
    body={'kind':kind, 'topic':list(topic), 'question':text,
          'witness_relation_ids':sorted(set(witnesses)),
          'origin_lens':origin_lens, 'related_manifestations':sorted(set(related)),
          'status':'QUESTION_ONLY',
          'evidence_class':'UNSOURCED_PENCIL_SEED' if seed_only else 'CLAIMED_AUTHORED_GRAPH',
          'external_authority':'NONE'}
    return {'id':'q:'+sha(body)[:24], **body}


class CrossLensInquiry:
    """Read-only sequence over a frozen ThoughtViews input.

    A card carrying a source fingerprint does not independently establish truth.
    Layout distances cannot appear as evidence. The questions and analysis can
    be computed with geometry disabled, even when lenses are named.
    """
    def __init__(self, engine: ThoughtViews):
        if not isinstance(engine, ThoughtViews):raise ViewError('THOUGHT-008 engine required')
        self.engine=engine
        self.rel={r['id']:copy.deepcopy(r) for r in engine.relations}

    def _authored(self, predicate):
        return [r for r in self.engine.relations if r['status']=='AUTHORED' and r['predicate']==predicate]

    def _associated_witnesses(self, source, target, via):
        out=[]
        for node in via:
            for r in self._authored('associated'):
                if frozenset((r['source'],r['target'])) in (frozenset((source,node)),
                                                           frozenset((target,node))):
                    out.append(r['id'])
        return sorted(set(out))

    def _initial_inquiries(self):
        out=[]
        for bridge in self.engine.association_questions():
            a,b=bridge['source'],bridge['target']
            witnesses=self._associated_witnesses(a,b,bridge['via'])
            if not witnesses:continue
            out.append(_question('association_bridge',(a,b),
                'Do these separately presented ideas have a warranted direct association?',
                witnesses,origin_lens='association',related=bridge['via']))
        return out

    def _context(self, card):
        endpoints=tuple(card['topic'])
        # Local cut: only declared dependencies and enabled targets reachable
        # from the candidate endpoints. It is not an independent evidence source.
        near=set(endpoints)
        requirements=[]
        for r in self._authored('requires'):
            if r['source'] in near:
                requirements.append(r)
                near.add(r['target'])
        # second shallow pass for one step of upstream dependencies only
        for r in self._authored('requires'):
            if r['source'] in near and r['id'] not in {x['id'] for x in requirements}:
                requirements.append(r)
                near.add(r['target'])
        return near,sorted(requirements,key=lambda x:x['id'])

    def _dependency(self, card):
        _, requirements=self._context(card)
        return [_question('verify_prerequisite',(r['source'],r['target']),
                 'Is this declared prerequisite independently satisfied for this possible connection?',
                 [r['id'],*card['witness_relation_ids']], origin_lens='dependency')
                for r in requirements]

    def _tension(self, card):
        near,_=self._context(card)
        return [_question('resolve_tension',(r['source'],r['target']),
                'Do these opposing authored claims affect the candidate; what corroboration resolves them?',
                [r['id'],*card['witness_relation_ids']],origin_lens='tension')
                for r in self._authored('contradicts')
                if r['source'] in near or r['target'] in near]

    def _affordance(self, card):
        near,_=self._context(card)
        return [_question('test_conditional_enablement',(r['source'],r['target']),
                'Does the declared enabling relationship hold, including any unmet requirements?',
                [r['id'],*card['witness_relation_ids']],origin_lens='affordance')
                for r in self._authored('enables')
                if r['source'] in near or r['target'] in near]

    def _lens_questions(self, lens, card):
        return {
            'dependency':self._dependency,
            'tension':self._tension,
            'affordance':self._affordance,
        }.get(lens,lambda _card:[])(card)

    def _relevant_scores(self, card):
        """Signals are source typed facts/questions, not appearance-based quality."""
        return {lens:len(self._lens_questions(lens,card))
                for lens in ('dependency','tension','affordance')}

    def start(self, *, initial_question=None, seed_pair=None, max_steps=3, allow_geometry=True,
              policy='source_first', feedback=()):
        """Compute a reproducible fresh sequence.

        The operator can request a specific question ID and optionally declare
        particular lenses unhelpful; this is NOT autonomous learned feedback.
        Each step retains a complete carried set of questions with exact witness IDs.
        """
        _require(type(max_steps) is int and 0<=max_steps<=MAX_STEPS, 'max_steps must be 0..5')
        _require(type(allow_geometry) is bool, 'allow_geometry must be boolean')
        _require(policy in ('source_first','sequential'), 'unknown routing policy')
        _require(isinstance(feedback,(tuple,list)) and len(feedback)==len(set(feedback)) and
                 all(x in LENSES for x in feedback), 'invalid operator feedback')
        _require(not (initial_question is not None and seed_pair is not None),
                 'choose one initial question selector')
        if seed_pair is not None:
            _require(isinstance(seed_pair,(list,tuple)) and len(seed_pair)==2 and
                     all(isinstance(x,str) and x in self.engine.manifests for x in seed_pair) and
                     seed_pair[0]!=seed_pair[1], 'seed pair requires two distinct known manifestation IDs')
            cards=[_question('operator_pencil_seed',tuple(seed_pair),
                'What source-backed connections, prerequisites or conflicts should be checked between these ideas?',
                [],origin_lens='PENCIL_MANUAL',seed_only=True)]
        else:
            cards=self._initial_inquiries()
        if initial_question is not None:
            _require(isinstance(initial_question,str), 'initial question id must be a string')
            cards=[c for c in cards if c['id']==initial_question]
            _require(len(cards)==1, 'question not in current frozen source')
        if not cards:
            return self._report([],[],[],'HOLD_NO_WITNESSED_BRIDGE',0,allow_geometry,policy,feedback)
        initial=cards[0]
        carried={initial['id']:initial}
        steps=[];seen=set();previous='0'*64
        if initial['kind']!='operator_pencil_seed':
            _require(len(initial['witness_relation_ids'])>=2, 'under-supported candidate')
        # The association proposal starts the inquiry, not a justified conclusion.
        itinerary=['dependency','tension','affordance']
        if policy=='source_first':
            scores=self._relevant_scores(initial)
            itinerary.sort(key=lambda x:(-scores[x],('dependency','tension','affordance').index(x)))
        itinerary=[x for x in itinerary if x not in feedback]
        for lens in itinerary[:max_steps]:
            # Actually construct the source-owner projection when requested. Its
            # placement coordinates remain outside the epistemic inspection.
            projection=self.engine.project(lens,anchor=initial['topic'][1]) if allow_geometry else None
            if projection is not None:
                _require(projection['source_evidence_digest']==self.engine.input_digest and
                         projection['relations']==self.engine.relations and
                         projection['external_authority']=='NONE', 'projection changed source')
            new=self._lens_questions(lens,initial)
            novel=[q for q in new if q['id'] not in carried]
            for q in novel:carried[q['id']]=q
            observed_ids={r['id'] for r in self.engine.relations if r['status']=='AUTHORED'}
            for q in novel:
                _require(set(q['witness_relation_ids']).issubset(observed_ids),
                         'hypothetical assertion leaked into evidence')
            # Each receipt is bound to the same frozen source; positions not read.
            body={'sequence':len(steps)+1,'lens':lens,'source_digest':self.engine.input_digest,
                  'previous_receipt':previous,'carried_question_ids':list(carried),
                  'new_question_ids':[q['id'] for q in novel],
                  'reported_source_witnesses':sorted({w for q in new for w in q['witness_relation_ids']}),
                  'interpretation':'typed evidence pressure, NOT independent corroboration',
                  'geometry_requested':allow_geometry,'geometry_used_for_evidence':False,
                  'projection_generated':projection is not None,
                  'projection_placement_count':len(projection['placements']) if projection else 0,
                  'projection_display_digest':sha(projection['placements']) if projection else None,
                  'survival':'QUESTION_ONLY', 'pen_promotion':False,'external_authority':'NONE'}
            receipt=sha(body);steps.append({**body,'receipt':receipt});previous=receipt
            seen.add(lens)
        status='CARRIED_WITH_OPEN_PRESSURES' if len(carried)>1 else 'CARRIED_UNCHANGED'
        if max_steps==0:status='PENCIL_ONLY_NO_CROSS_LENS'
        return self._report([initial],list(carried.values()),steps,status,len(steps),allow_geometry,policy,feedback)

    def _report(self,initial,carried,steps,status,count,allow_geometry,policy,feedback):
        output={
            'schema':SCHEMA,'source_digest':self.engine.input_digest,
            'source_snapshot_digest':self.engine.source_snapshot_digest,
            'status':status,'initial_inquiries':copy.deepcopy(initial),
            'carried_questions':copy.deepcopy(carried),
            'steps':copy.deepcopy(steps), 'visited_lenses':[s['lens'] for s in steps],
            'view_cost_units':count if allow_geometry else 0,
            'lens_inspection_count':count,
            'geometry_enabled':allow_geometry,'policy':policy,
            'operator_deferred_lenses':list(feedback),
            'assertion_promotion':'NONE', 'pen_status':'UNCHANGED',
            'effective_external_authority':'NONE',
            'scientific_limit':'Finite classical inspections of the SAME authored graph; views are NOT independent evidence or semantic truth',
        }
        output['result_digest']=sha(output)
        return output

    def resume(self, previous, *, max_steps=3, allow_geometry=True, feedback=()):
        """Recompute from source; never trust externally supplied old questions."""
        _require(isinstance(previous,dict) and previous.get('schema')==SCHEMA,
                 'incompatible prior inquiry')
        _require(previous.get('source_digest')==self.engine.input_digest and
                 previous.get('source_snapshot_digest')==self.engine.source_snapshot_digest,
                 'STALE_SOURCE: source or identity changed; previous discoveries must be revalidated')
        digest_value=previous.get('result_digest')
        body={k:v for k,v in previous.items() if k!='result_digest'}
        _require(isinstance(digest_value,str) and sha(body)==digest_value,
                 'previous receipt integrity invalid')
        initial=previous.get('initial_inquiries')
        _require(isinstance(initial,list) and len(initial)==1, 'invalid prior inquiry')
        kwargs=({'seed_pair':initial[0]['topic']} if initial[0]['kind']=='operator_pencil_seed'
                else {'initial_question':initial[0]['id']})
        return self.start(**kwargs,max_steps=max_steps,
                          allow_geometry=allow_geometry,policy=previous.get('policy','source_first'),feedback=feedback)

    def evidence_only_full_control(self, initial_question=None, seed_pair=None):
        """Exact same questions attainable with NONE geometry, and equal access cost ignored."""
        return self.start(initial_question=initial_question,seed_pair=seed_pair,max_steps=3,
                          allow_geometry=False,policy='sequential')


def render_svg(report):
    """Compact static timeline. All text content escaped; view is non-evidentiary."""
    from html import escape
    if not report.get('initial_inquiries'):raise ViewError('nothing to draw')
    width=1100;count=len(report['steps']);height=270+max(1,count)*150
    row=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-label="MOTIF Cross-Lens Inquiry">',
         '<rect width="100%" height="100%" fill="#f7f2e8"/>',
         '<text x="50" y="58" font-family="Georgia,serif" font-size="31" fill="#18302c">MOTIF / Cross-Lens Inquiry</text>',
         '<text x="50" y="88" font-family="sans-serif" font-size="14" fill="#52615b">Pencil hypothesis travels through distinct inspections. One source graph. No promotion.</text>',
         '<rect x="50" y="117" width="1000" height="80" rx="17" fill="#fce4b0" stroke="#8f6a28" stroke-width="2"/>',
         '<text x="75" y="144" font-family="sans-serif" font-size="13" fill="#735117">PENCIL · ORIGINAL QUESTION</text>',
         f'<text x="75" y="173" font-family="sans-serif" font-size="17" fill="#202c29">{escape(report["initial_inquiries"][0]["question"])}</text>']
    for i,step in enumerate(report['steps']):
        y=233+i*150; lens=escape(step['lens'].upper()); qty=len(step['new_question_ids'])
        row.extend([f'<path d="M 550 {y-35} V {y-18}" stroke="#4a685e" stroke-width="3" stroke-dasharray="4 5"/>',
                    f'<rect x="75" y="{y}" width="950" height="116" rx="16" fill="#ffffff" stroke="#6b8e84" stroke-width="2"/>',
                    f'<text x="102" y="{y+36}" font-family="sans-serif" font-weight="bold" font-size="20" fill="#12342e">{i+1:02d}  {lens}</text>',
                    f'<text x="102" y="{y+66}" font-family="sans-serif" font-size="15" fill="#46524c">{qty} new question(s) · {len(step["carried_question_ids"])} carried · Same source fingerprint</text>',
                    f'<text x="102" y="{y+93}" font-family="sans-serif" font-size="13" fill="#84633b">QUESTION_ONLY · Geometry is not evidence · PEN unchanged</text>'])
    row.extend([f'<text x="50" y="{height-26}" font-family="sans-serif" font-size="12" fill="#59665d">HOLD: no external action. Cross-lens agreement is not independent corroboration.</text>', '</svg>'])
    return '\n'.join(row)+'\n'
