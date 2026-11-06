"""MOTIF Human Talk 001, inspired by Full Measure Human Terminal's operator membrane.

English sentences are first-class *typed speech acts*, not privileged program
instructions. Supports a tiny bounded grammar; unknown words remain UNKNOWN.
One never claims a natural-language model or real humanlike comprehension.
"""
from __future__ import annotations

import re
from hashlib import sha256
from inquiry import InquiryCycle, InquiryError, sha

VERSION = 'motif.human-talk.v1'
# Full Measure Human Terminal's small intent boundary inspired these aliases;
# its own application/worldRuntimeClient execution authority is NOT imported.
ALIASES = {
    'where am i': 'ORIENT', 'orient me': 'ORIENT', 'orient': 'ORIENT',
    'what can i safely do': 'INSPECT_MOVES', 'what can i do': 'INSPECT_MOVES',
    'show me the evidence': 'INSPECT_EVIDENCE', 'show evidence': 'INSPECT_EVIDENCE',
    'what happened last time': 'REVIEW_PRIOR',
    'what needs me': 'INSPECT_MOVES',
}
# External writes should never even be interpreted as an inquiry instruction.
EFFECT_WORDS = re.compile(r'\b(?:deploy|delete|execute|merge|email|send|contact|publish|dispatch|push|run shell|run code|wire money|grant permission)\b', re.I)


def normalize(value):
    if type(value) is not str or not 1 <= len(value.strip()) <= 320:
        raise InquiryError('bounded nonempty utterance 1..320 chars required')
    return re.sub(r'\s+', ' ', value.strip().lower().rstrip('?!., '))


PROPOSAL_SCHEMA = 'motif.human-talk.interpreter-proposal.v1'
ALLOWED_SPEECH_ACTS = frozenset({
    'ORIENT', 'INSPECT_MOVES', 'INSPECT_EVIDENCE', 'REVIEW_PRIOR',
    'EXPLORE_POSSIBILITY', 'CHALLENGE', 'COMPARE'
})


def validate_language_proposal(proposal, text, engine):
    """An OPTIONAL external-language candidate; validated, never trusted.

    A future local language model may offer a frame with this exact shape.
    This function does not run a model or accept new operations/permissions.
    """
    if not isinstance(proposal,dict) or set(proposal) != {
            'schema','input_digest','speech_act','manifestation_ids','rationale'}:
        raise InquiryError('invalid interpreter candidate shape')
    if proposal['schema'] != PROPOSAL_SCHEMA:
        raise InquiryError('unknown interpreter proposal schema')
    if proposal['input_digest'] != sha256(text.encode('utf-8')).hexdigest():
        raise InquiryError('proposal is not bound to exact user phrase')
    if proposal['speech_act'] not in ALLOWED_SPEECH_ACTS:
        raise InquiryError('unsupported or effectful proposed speech act')
    ids=proposal['manifestation_ids']
    if (not isinstance(ids,list) or len(ids) not in (0,2) or
        len(ids) != len(set(ids)) or
        any(type(x) is not str or x not in engine.manifests for x in ids)):
        raise InquiryError('proposal invents/conflates idea identities')
    if (not isinstance(proposal['rationale'],str) or
        not 1 <= len(proposal['rationale']) <= 240):
        raise InquiryError('interpreter rationale required')
    if proposal['speech_act'] in ('EXPLORE_POSSIBILITY','CHALLENGE','COMPARE') and len(ids)!=2:
        raise InquiryError('exploration proposal must bind two exact manifestations')
    return proposal


def interpret(text, *, engine, selected_pair=None, language_proposal=None):
    """Conservative typed interpretation; no invented referents or relations."""
    if not hasattr(engine,'manifests'):
        raise InquiryError('source graph required')
    normalized=normalize(text)
    if language_proposal is not None and not EFFECT_WORDS.search(normalized):
        checked=validate_language_proposal(language_proposal,text,engine)
        selected_pair=checked['manifestation_ids'] or selected_pair
        intent=checked['speech_act']
        proposed=True
    else:
        intent=None
        proposed=False
    if EFFECT_WORDS.search(normalized):
        intent='HOLD_EFFECT_REQUEST'
    elif proposed:
        pass
    elif normalized in ALIASES:
        intent=ALIASES[normalized]
    elif any(normalized.startswith(x) for x in ('what if ','could ','might ','maybe ','suppose ')):
        intent='EXPLORE_POSSIBILITY'
    elif ('which question' in normalized or 'what should we ask' in normalized or
          'how do we know' in normalized or 'test this' in normalized):
        intent='CHALLENGE'
    elif ('why ' in normalized or 'what evidence' in normalized):
        intent='INSPECT_EVIDENCE'
    elif ('compare ' in normalized or 'difference between' in normalized):
        intent='COMPARE'
    else:
        intent='UNKNOWN'
    pair=selected_pair
    if pair is not None:
        if (not isinstance(pair,(tuple,list)) or len(pair)!=2 or
            any(type(x) is not str or x not in engine.manifests for x in pair) or pair[0]==pair[1]):
            raise InquiryError('language cannot invent or conflate graph referents')
    need_pair=intent in ('EXPLORE_POSSIBILITY','CHALLENGE','COMPARE')
    status=('HOLD' if intent in ('HOLD_EFFECT_REQUEST','UNKNOWN') else
            'CLARIFY_REFERENTS' if need_pair and pair is None else 'TYPED_ONLY')
    return {'schema':VERSION+'.interpretation', 'speech_act':intent,
            'status':status, 'normalized_input':normalized,
            'selected_manifestations':list(pair) if pair is not None else [],
            'interpreter_origin':'UNVERIFIED_EXTERNAL_PROPOSAL' if proposed else 'BOUNDED_LOCAL_GRAMMAR',
            'routing_preference':'world' if intent=='EXPLORE_POSSIBILITY' else 'decision',
            'inferred_relations':[], 'can_execute':False, 'can_commit_pen':False,
            'clarification':'Choose two exact manifestation IDs; equal words need not mean identical concepts.'
                if status=='CLARIFY_REFERENTS' else None,
            'limits':'Bounded aliases and phrase rules, not general natural language understanding.'}


def manifest_label(engine, mid):
    manifest = engine.manifests[mid]
    concept = engine.concepts[manifest['concept_id']]
    label = concept['label']
    same = [m for m in engine.manifests if engine.concepts[engine.manifests[m]['concept_id']]['label']==label]
    return f'{label} [{mid}]' if len(same)>1 else label


def question_utterance(engine, q):
    a=manifest_label(engine,q['source']); b=manifest_label(engine,q['target'])
    verb={'requires':'requires','associated':'is associated with',
          'contradicts':'contradicts','enables':'enables'}[q['predicate']]
    # Explicitly spoken as an inquiry; no affirmative assertion created.
    return {'speaker':'MOTIF', 'speech_act':'ASK', 'instrument':'PENCIL',
            'text':f'Could we check whether {a} {verb} {b}?',
            'relation_id':q['relation_id'], 'question_id':q['id'],
            'claimed_origin':q['claimed_origin'],
            'source_digest':engine.input_digest, 'status':'QUESTION_ONLY'}


def answer_utterance(q, answer):
    if answer == 'UNKNOWN':
        phrasing='The supplied test cannot answer that. I will leave it unresolved.'
    elif answer is True:
        phrasing='The synthetic test says yes for this modeled possibility. That does not verify the real world.'
    else:
        phrasing='The synthetic test says no for this modeled possibility. The original authored link remains a historical claim.'
    return {'speaker':'MOTIF', 'speech_act':'RECORD_TEST_RESULT',
            'instrument':'PENCIL', 'text':phrasing, 'question_id':q['id'],
            'status':'UNVERIFIED_FIXTURE_OBSERVATION'}


def dialogue(engine, worlds, text, oracle, *, selected_pair=None, budget=3,
             geometry=False, strategy=None, language_proposal=None):
    """A recurring language->thought->question->observation->language loop.

    No services, commands, human confirmations, evidence admissions or PEN.
    Caller supplies the toy oracle explicitly. Without it, no 'observed' claim.
    """
    intent=interpret(text,engine=engine,selected_pair=selected_pair,
                     language_proposal=language_proposal)
    if selected_pair is None and intent['selected_manifestations']:
        selected_pair=tuple(intent['selected_manifestations'])
    record={'schema':VERSION+'.dialogue', 'input':intent,
            'utterances':[{'speaker':'HUMAN','speech_act':intent['speech_act'],
                           'text':text,'status':'OPERATOR_SUPPLIED'}],
            'authority':'NONE','pen':'UNCHANGED'}
    if intent['status']!='TYPED_ONLY':
        record['status']=intent['status'];record['inquiry']=None
        record['utterances'].append({'speaker':'MOTIF','speech_act':'HOLD',
            'text':intent['clarification'] or 'I cannot safely interpret that as a permitted inquiry.',
            'status':'HOLD'})
        record['receipt_digest']=sha(record)
        return record
    if intent['speech_act']=='ORIENT':
        record['status']='SOURCE_ONLY_ORIENTATION';record['inquiry']=None
        record['utterances'].append({'speaker':'MOTIF','speech_act':'EXPLAIN',
            'text':f'I can inspect {len(engine.concepts)} separate concepts and {len(engine.relations)} declared source relations. This does not establish their truth.',
            'status':'SOURCE_INDEX_ONLY'})
        record['receipt_digest']=sha(record)
        return record
    if selected_pair is None:
        record['status']='CLARIFY_REFERENTS';record['inquiry']=None
        record['utterances'].append({'speaker':'MOTIF','speech_act':'CLARIFY',
             'text':'Which two exact ideas should I investigate? Please select their IDs.',
             'status':'HOLD'})
        record['receipt_digest']=sha(record)
        return record
    if not callable(oracle):
        record['status']='HOLD_NO_TEST';record['inquiry']=None
        record['utterances'].append({'speaker':'MOTIF','speech_act':'HOLD',
            'text':'I can propose questions but have no independent test source for answers.',
            'status':'HOLD'})
        record['receipt_digest']=sha(record)
        return record
    brain=InquiryCycle(engine,worlds,seed_pair=selected_pair,
                       strategy=strategy or intent['routing_preference'],geometry=geometry)
    if type(budget) is not int or not 0<=budget<=8:
        raise InquiryError('dialogue budget 0..8 required')
    for _ in range(budget):
        q=brain.next_question()
        if q is None:break
        spoken=question_utterance(engine,q)
        record['utterances'].append(spoken)
        observation=oracle(q['atom'])
        brain.observe(q,observation)
        record['utterances'].append(answer_utterance(q,observation))
        if brain.stop_reason:break
    # run() can be used only if we have not already performed steps. Mark budget
    # exhaustion in a separate, explicit record rather than silently 'PEN'.
    result=brain.report()
    result['conclusion_status']=brain.stop_reason or 'HOLD_BUDGET_EXHAUSTED'
    result['receipt_digest']=sha({k:v for k,v in result.items() if k!='receipt_digest'})
    record['inquiry']=result
    if result['proposed_decision'] is None:
        sentence='I still have multiple plausible models. My working conclusion is unresolved.'
    else:
        sentence=(f'Under the supplied hypothetical worlds, the remaining models all say '
                  f'{result["proposed_decision"]}. This is not independent evidence or a PEN conclusion.')
    record['utterances'].append({'speaker':'MOTIF','speech_act':'PROVISIONAL_SUMMARY',
        'instrument':'PENCIL','text':sentence,'status':'MODEL_CONDITIONAL_ONLY'})
    record['status']='HOLD_FOR_REVIEW'
    record['receipt_digest']=sha(record)
    return record
