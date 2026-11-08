"""THOUGHT-031: model-invented, parameterized pidgin of typed portal operations.

Unlike 030's one-time alias, a word may be re-used with different typed
arguments. Defining it does not execute it; speaking it invokes exactly one
existing read-only portal operation. No arbitrary bytecode, programs, hidden
semantic channels or privilege amplification. Optional and session-local.
"""
from __future__ import annotations
import re,copy,json
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
p=str(HERE.parent/'thought-030')
if p not in sys.path:sys.path.insert(0,p)
from pidgin import PidginLexicon, PidginError, CANONICAL_TOOLS, PARAMS
from artifact_portal import compact

SYMBOL=re.compile(r'[A-Za-z][A-Za-z0-9_-]{1,15}\Z')
SLOTS={'artifact_id':'artifact','term':'term','graph_id':'graph','node_id':'node'}
RESERVED={'define','speak','search','read','catalog','graphs','neighbors','final','shell','exec','eval','python','delete','write'}

class PidginProtocolError(PidginError):pass

class ParameterizedPidgin:
    def __init__(self,portal,*,enabled=True,max_words=6):
        self.delegate=PidginLexicon(portal,enabled=enabled,max_words=max_words)
        self.portal=portal;self.enabled=enabled;self.definitions={};self.uses=[];self.refusals=0
    def define(self,symbol,template,gloss):
        if not self.enabled:raise PidginProtocolError('pidgin disabled')
        if type(symbol) is not str or not SYMBOL.fullmatch(symbol) or symbol.lower() in RESERVED:
            raise PidginProtocolError('unrecognized or reserved symbol')
        if symbol in self.definitions or len(self.definitions)>=self.delegate.max_words:
            raise PidginProtocolError('collision or lexicon full')
        if type(gloss) is not str or not 5<=len(gloss)<=100 or any(ord(c)<32 for c in gloss):
            raise PidginProtocolError('invalid public gloss')
        if type(template) is not dict or template.get('tool') not in CANONICAL_TOOLS:
            raise PidginProtocolError('unknown tool template')
        tool=template['tool']
        if set(template)-{'tool'}-PARAMS[tool]:raise PidginProtocolError('unknown tool parameters')
        if len(compact(template))>1200:raise PidginProtocolError('oversized definition')
        slots={}
        for field,value in template.items():
            if field=='tool':continue
            if type(value) is str and value.startswith('$'):
                expected=SLOTS.get(field)
                if value!='$'+str(expected) or expected in slots:
                    raise PidginProtocolError('only typed documented placeholder allowed')
                slots[expected]=field
        if not slots:raise PidginProtocolError('reusable pidgin requires a typed slot')
        if len(slots)>2:raise PidginProtocolError('overly complex template')
        # Check all constant parameters through the same source-owned validator.
        example={'artifact':next(iter(self.portal._items),''),'term':'proof',
                 'graph':next(iter(self.portal._graphs),''),'node':'dummy'}
        test={k:(example[v[1:]] if type(v) is str and v.startswith('$') else v)
              for k,v in template.items()}
        try:self.delegate._typed_request(test)
        except PidginError as exc:raise PidginProtocolError('template fails canonical tool validation') from exc
        entry={'symbol':symbol,'gloss':gloss,'template':copy.deepcopy(template),
               'slot_types':sorted(slots),'status':'MODEL_PROPOSED_UNVERIFIED_CONVENTION',
               'uses':0}
        self.definitions[symbol]=entry
        return copy.deepcopy(entry)
    def speak(self,symbol,values):
        if not self.enabled:raise PidginProtocolError('pidgin disabled')
        if type(symbol) is not str or symbol not in self.definitions:raise PidginProtocolError('undefined word')
        entry=self.definitions[symbol]
        if type(values) is not dict or set(values)!=set(entry['slot_types']):
            raise PidginProtocolError('arguments must satisfy exactly the declared slots')
        for key,value in values.items():
            if type(value) is not str or not 1<=len(value)<=180 or any(ord(c)<32 for c in value):
                raise PidginProtocolError('invalid typed slot value')
        expanded={k:(values[v[1:]] if type(v) is str and v.startswith('$') else v)
                  for k,v in entry['template'].items()}
        try:checked=self.delegate._typed_request(expanded)
        except PidginError as exc:raise PidginProtocolError('expanded read-only command invalid') from exc
        entry['uses']+=1
        self.uses.append({'symbol':symbol,'values':copy.deepcopy(values),'backtranslated_request':checked})
        return checked
    def view(self):
        return {'optional':self.enabled,'terms':copy.deepcopy(self.definitions),
                'tokens_coined':len(self.definitions),'token_uses':len(self.uses),
                'spoken':copy.deepcopy(self.uses),'refusals':self.refusals,
                'all_means_typed_read_only_operations':True}
    def cost_report(self):
        definitions=sum(len(compact({'action':'define',**{k:v for k,v in r.items()
                        if k in ('symbol','gloss','template')}})) for r in self.definitions.values())
        pidgin_calls=sum(len(compact({'action':'speak','symbol':u['symbol'],
                         'values':u['values']})) for u in self.uses)
        canonical_calls=sum(len(compact({'action':u['backtranslated_request']['tool'],
                                  **{k:v for k,v in u['backtranslated_request'].items()
                                     if k!='tool'}})) for u in self.uses)
        return {'definition_bytes':definitions,'spoken_bytes':pidgin_calls,
                'equivalent_plain_request_bytes':canonical_calls,
                'net_bytes_saved_including_definitions':canonical_calls-(definitions+pidgin_calls),
                'token_costs_not_equivalent_to_bytes':True,
                'success_is_not_short_message_length_alone':True}
