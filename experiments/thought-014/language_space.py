"""MOTIF language-native pencil operations and a non-authoritative model membrane.

Every utterance has stable identity and referent bindings; model responses cannot
change the source graph or become PEN. The 013 interpreter remains the baseline.
"""
from __future__ import annotations
import hashlib,json,sys
from pathlib import Path
DIR=Path(__file__).resolve().parent.parent/'thought-013'
if not DIR.is_dir(): DIR=Path(__file__).resolve().parent.parent/'thought013'
if str(DIR) not in sys.path:sys.path.append(str(DIR))
from human_talk import interpret, EFFECT_WORDS, validate_language_proposal, PROPOSAL_SCHEMA
from inquiry import InquiryError
from model_gateway import ModelError, SCHEMA, ACTS


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=True,
              separators=(',',':'),allow_nan=False).encode('utf-8')).hexdigest()

class LanguageSpace:
    """One local snapshot, conversations as typed thought events—not merely captions."""
    def __init__(self,engine):
        if not hasattr(engine,'manifests') or not hasattr(engine,'input_digest'):
            raise InquiryError('typed source graph required')
        self.engine=engine;self.source_digest=engine.input_digest
        self.turns=[]

    def explore(self,text,*,selected_pair=None,model=None):
        if self.engine.input_digest != self.source_digest:
            raise InquiryError('STALE_SOURCE')
        # No model is permitted to override an effectful user phrase.
        baseline=interpret(text,engine=self.engine,selected_pair=selected_pair)
        candidate=None;model_error=None;model_kind=None;model_confidence=None
        if model is not None and baseline['status']=='HOLD' and baseline['speech_act']=='UNKNOWN' \
           and not EFFECT_WORDS.search(text):
            try:
                proposed=model.propose(text,selected_pair=selected_pair)
                if not isinstance(proposed,dict) or set(proposed)!={
                    'schema','speech_act','manifestation_ids','rationale','model_kind','confidence'} \
                   or proposed['schema']!=SCHEMA or proposed['speech_act'] not in (*ACTS,'UNKNOWN'):
                    raise ModelError('model contract mismatch')
                model_kind=proposed['model_kind'];model_confidence=proposed['confidence']
                # Construct a 013-compatible proposal with exact input fingerprint;
                # NEVER allow the model to supply a forged fingerprint.
                if type(proposed['model_kind']) is not str or len(proposed['model_kind'])>80 or (
                    proposed['confidence'] is not None and (
                        type(proposed['confidence']) not in (float,int) or
                        not 0 <= proposed['confidence'] <= 1)):
                    raise ModelError('model provenance/confidence malformed')
                if proposed['manifestation_ids']!=list(selected_pair or []):
                    raise ModelError('model may not change selected identities')
                if proposed['speech_act']!='UNKNOWN':
                    packed={'schema':PROPOSAL_SCHEMA,'input_digest':hashlib.sha256(text.encode()).hexdigest(),
                            'speech_act':proposed['speech_act'],
                            'manifestation_ids':proposed['manifestation_ids'],
                            'rationale':proposed['rationale']}
                    validate_language_proposal(packed,text,self.engine)
                    candidate=interpret(text,engine=self.engine,selected_pair=selected_pair,
                                        language_proposal=packed)
                    if candidate['status']!='TYPED_ONLY':
                        candidate=None
            except (InquiryError,ModelError,ValueError,TypeError,KeyError) as e:
                model_error=type(e).__name__
        chosen=candidate or baseline
        utterance={'speaker':'HUMAN','text':text,'speech_act':chosen['speech_act'],
                   'instrument':'PENCIL','source_digest':self.source_digest,
                   'selected_manifestations':chosen['selected_manifestations'],
                   'status':chosen['status'], 'source_class':chosen['interpreter_origin'],
                   'model_consulted':model is not None and baseline['speech_act']=='UNKNOWN',
                   'model_accepted_as_hypothesis':candidate is not None,
                   'epistemic_status':('UNVERIFIED_MODEL_GUESS' if candidate is not None
                     else 'DETERMINISTIC_LANGUAGE_RULE' if chosen['status']=='TYPED_ONLY'
                     else 'UNRESOLVED_OR_HELD'),
                   'alternative_interpretations':([baseline['speech_act']] if candidate is not None else []),
                   'model_kind_if_consulted':model_kind,
                   'model_reported_probability_unverified':model_confidence,
                   'model_error':model_error,
                   'pen_state':'UNCHANGED','external_authority':'NONE'}
        utterance['utterance_id']='u:'+digest(utterance)[:24]
        self.turns.append(utterance)
        return utterance

    def challenge(self,utterance_id,reason):
        if not isinstance(reason,str) or not 1<=len(reason.strip())<=240:
            raise InquiryError('bounded challenge required')
        target=next((t for t in self.turns if t['utterance_id']==utterance_id),None)
        if not target:raise InquiryError('unknown utterance')
        turn={'speaker':'MOTIF','speech_act':'CHALLENGE','instrument':'PENCIL',
              'target_utterance_id':utterance_id,'text':reason,
              'source_digest':self.source_digest,'status':'QUESTION_ONLY',
              'pen_state':'UNCHANGED','external_authority':'NONE'}
        turn['utterance_id']='u:'+digest(turn)[:24];self.turns.append(turn)
        return turn

    def snapshot(self):
        return {'schema':'motif.thought014.language-space.v1',
                'source_digest':self.source_digest,'turns':list(self.turns),
                'semantic_relations_modified':False,'pen_state':'UNCHANGED',
                'external_authority':'NONE','receipt_digest':digest(self.turns)}
