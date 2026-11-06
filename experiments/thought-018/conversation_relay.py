"""Conversations-as-model-transport: execute actual GPT-6-proposed *data* in MOTIF-018.

The conversation operator relays the two previously generated typed JSON model
proposals via a local file. In this run GPT-6 itself composed those proposals
in ChatGPT. MOTIF invokes this relay adapter and its own research director,
independent oracle, and existing fixed-template code evaluator.

CAUTION: The local process does NOT make an LLM API call. It does not prove
MOTIF autonomously ran Ollama, nor independently authenticate a model signer.
"""
from __future__ import annotations
import argparse
from copy import deepcopy
import json
from pathlib import Path
from director import ResearchDirector
from program import digest

BRIEF = ('Investigate transitions when arriving at a node can turn a switch off '
         'as well as on. Propose a mechanism and a discriminating test. '
         'Do not grant authority or change source code.')

class GPT6ConversationRelay:
    kind = 'GPT6_CONVERSATION_RELAY_NOT_LOCAL_API'

    def __init__(self, messages):
        if type(messages) is not list or not 1 <= len(messages) <= 6:
            raise ValueError('1..6 model reply messages required')
        self._messages = deepcopy(messages)
        self.calls = []

    def propose(self, brief, feedback=()):
        index = len(self.calls)
        if index >= len(self._messages): return None
        message = deepcopy(self._messages[index])
        self.calls.append({
            'round': index+1, 'brief': brief,
            'development_feedback_visible': deepcopy(feedback),
            'reply_digest': digest(message),
            'transport': 'GPT6_CONVERSATION_FILE_RELAY',
            'model_issued_network_request': False,
            'model_identity_cryptographically_verified': False,
            'frozen_audit_disclosed_before_proposal': False,
        })
        return message


def run(messages, *, max_rounds=3):
    model = GPT6ConversationRelay(messages)
    result, candidate = ResearchDirector(BRIEF, model=model,
                                         max_rounds=max_rounds).run()
    return {'schema':'motif.thought018.conversation-llm-run.v1',
            'report':result,'model_relay_calls':model.calls,
            'candidate':candidate,
            'proposer_claim':'GPT-6 in current ChatGPT conversation',
            'model_transport':'MANUAL_CONVERSATION_FILE_RELAY',
            'motif_autonomously_called_llm':False,
            'actual_local_ollama_inference':False,
            'external_model_identity_verified':False,
            'untrusted_proposal_input':True,
            'source_code_written_by_model_and_executed':False,
            'limitations':'The researcher is a conversation-provided GPT-6 response, not a model process invoked autonomously by MOTIF. Prior conversation discussed FLIP; heldout author-designed. This is an engineering integration demonstration, not blind discovery.'}


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--proposals',type=Path,default=Path(__file__).with_name('conversation-gpt6-proposals.json'))
    p.add_argument('--output',type=Path,default=Path(__file__).with_name('conversation-gpt6-results.json'))
    p.add_argument('--rounds',type=int,default=3)
    args=p.parse_args()
    packet=json.loads(args.proposals.read_text(encoding='utf-8'))
    result=run(packet,max_rounds=args.rounds)
    args.output.write_text(json.dumps(result,ensure_ascii=True,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':result['report']['status'],
       'model_kind':result['report']['model_kind'],
       'model_calls':result['report']['model_calls'],
       'dev_probe_count':result['report']['dev_probe_count'],
       'selected_mechanism':result['report']['selected_mechanism'],
       'development_graph':result['report']['development_graph'],
       'safety_graph':result['report']['safety_graph'],
       'frozen_graph_audit':result['report']['frozen_graph_audit'],
       'stress_graph_audit':result['report']['stress_graph_audit'],
       'motif_autonomously_called_llm':False},sort_keys=True,indent=2))

if __name__ == '__main__':main()
