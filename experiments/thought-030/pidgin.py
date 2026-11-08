"""Optional, model-invented pidgin tokens with deterministic, typed backtranslation.

The model chooses if/when to coin a symbol, its name and a tool meaning.
MOTIF never 'learns' arbitrary code, adopts semantic claims or decodes opaque
unbounded messages. A token has one inspectable read-only meaning and an
explicit plain-language gloss; unused symbols are faithfully recorded as unused.
"""
from __future__ import annotations
import re, copy
from artifact_portal import PortalError,compact

CANONICAL_TOOLS=('catalog','search','graphs','read','neighbors')
PARAMS={'catalog':{'kind','cursor','limit'},'search':{'term','kind','cursor','limit'},
        'graphs':{'cursor','limit'},'read':{'artifact_id','pointer','cursor','limit'},
        'neighbors':{'graph_id','node_id','cursor','limit'}}
SYMBOL=re.compile(r'[A-Za-z][A-Za-z0-9_-]{1,17}\Z')
class PidginError(ValueError):pass

class PidginLexicon:
    def __init__(self,portal,*,enabled=True,max_words=8):
        self.portal=portal;self.enabled=enabled;self.max_words=max_words
        self.definitions={};self.used=[];self.rejected=[]

    def _typed_request(self,obj):
        if type(obj) is not dict or obj.get('tool') not in CANONICAL_TOOLS:
            raise PidginError('symbol meaning must be one known read-only tool')
        tool=obj['tool']
        if set(obj)-{'tool'}-PARAMS[tool]:raise PidginError('unknown tool arguments')
        if tool=='read' and obj.get('artifact_id') not in self.portal._items:
            raise PidginError('artifact ID must be already indexed')
        if tool=='neighbors' and obj.get('graph_id') not in self.portal._graphs:
            raise PidginError('graph ID must be already indexed')
        if tool=='search' and (type(obj.get('term')) is not str or not 2<=len(obj['term'])<=100):
            raise PidginError('bounded search term required')
        # Source-owner portal checks the remaining shape and constraints.
        # A model never obtains an arbitrary URL, Python call, shell action or new path.
        try:
            self.portal.query(obj)
        except PortalError as exc:
            raise PidginError('unusable symbol meaning: '+str(exc)[:90]) from exc
        return copy.deepcopy(obj)

    def define(self,symbol,meaning,gloss):
        if not self.enabled:raise PidginError('experimental pidgin disabled')
        if type(symbol) is not str or SYMBOL.fullmatch(symbol) is None or symbol.lower() in {
            'final','search','read','catalog','graphs','neighbors','speak','define','python','shell','eval'}:
            raise PidginError('invalid or reserved invented symbol')
        if type(gloss) is not str or not 4<=len(gloss)<=100 or any(ord(c)<32 for c in gloss):
            raise PidginError('plain-language gloss required for auditability')
        if symbol in self.definitions or len(self.definitions)>=self.max_words:
            raise PidginError('symbol collision or glossary exhausted')
        request=self._typed_request(meaning)
        self.definitions[symbol]={'meaning':request,'gloss':gloss,'status':'MODEL_PROPOSED_UNVERIFIED_CONVENTION',
                                  'uses':0}
        return {'symbol':symbol,'gloss':gloss,'canonical_meaning':request,
                'machine_understood':True,'semantics_are_only_a_validated_tool_alias':True}

    def translate(self,symbol):
        if not self.enabled:raise PidginError('pidgin disabled')
        if type(symbol) is not str or symbol not in self.definitions:
            raise PidginError('undefined pidgin token')
        item=self.definitions[symbol]
        self.used.append(symbol)
        item['uses']+=1
        return copy.deepcopy(item['meaning'])

    def view(self):
        return {'optional':self.enabled,
                'terms':copy.deepcopy(self.definitions),
                'tokens_coined':len(self.definitions),
                'token_uses':len(self.used),
                'no_private_or_model_executable_syntax':True,
                'all_meanings_backtranslated_to_read_only_tool_calls':True}
